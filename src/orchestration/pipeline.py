import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from ..extractors.snowflake_extractor import SnowflakeExtractor
from ..embeddings.azure_openai_embedder import AzureOpenAIEmbedder
from ..indexers.azure_search_indexer import AzureSearchIndexer
from ..utils.config import Config
from ..utils.logging_config import get_logger


class Pipeline:
    """Orchestrate the data pipeline from Snowflake to Azure AI Search."""

    def __init__(self, config: Config):
        """
        Initialize pipeline.

        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = get_logger(__name__)

        # Initialize components
        self.extractor = SnowflakeExtractor(config)
        self.embedder = AzureOpenAIEmbedder(config)
        self.indexer = AzureSearchIndexer(config)

        # Checkpoint management
        self.checkpoint_file = config.checkpoint_file

        self.logger.info("Pipeline initialized")

    def load_checkpoint(self) -> Dict[str, Any]:
        """
        Load checkpoint from file.

        Returns:
            Checkpoint data or empty dict if file doesn't exist
        """
        if not self.checkpoint_file.exists():
            self.logger.info("No checkpoint file found")
            return {}

        try:
            with open(self.checkpoint_file, 'r') as f:
                checkpoint = json.load(f)
            self.logger.info("Checkpoint loaded", checkpoint=checkpoint)
            return checkpoint
        except Exception as e:
            self.logger.error("Failed to load checkpoint", error=str(e))
            return {}

    def save_checkpoint(self, checkpoint: Dict[str, Any]) -> None:
        """
        Save checkpoint to file.

        Args:
            checkpoint: Checkpoint data to save
        """
        try:
            # Ensure directory exists
            self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.checkpoint_file, 'w') as f:
                json.dump(checkpoint, f, indent=2, default=str)

            self.logger.info("Checkpoint saved", checkpoint=checkpoint)
        except Exception as e:
            self.logger.error("Failed to save checkpoint", error=str(e))

    def run(
        self,
        incremental: Optional[bool] = None,
        recreate_index: bool = False
    ) -> Dict[str, Any]:
        """
        Run the pipeline.

        Args:
            incremental: If True, only process new/updated records
            recreate_index: If True, recreate the search index

        Returns:
            Dictionary with pipeline execution statistics
        """
        start_time = datetime.utcnow()
        self.logger.info("Pipeline execution started", start_time=start_time)

        stats = {
            "start_time": start_time.isoformat(),
            "rows_extracted": 0,
            "rows_embedded": 0,
            "rows_indexed": 0,
            "errors": []
        }

        try:
            # Determine if we're running incrementally
            if incremental is None:
                incremental = self.config.get("pipeline.execution.incremental", False)

            # Get pipeline configuration
            table_name = self.config.get("pipeline.source.table_name")
            columns = self.config.get("pipeline.source.columns")
            watermark_column = self.config.get("pipeline.source.watermark_column")
            text_field = self.config.get("pipeline.embedding.text_field", "content")
            batch_size = self.config.batch_size

            if not table_name:
                raise ValueError("table_name not configured in config.yaml")

            # Load checkpoint for incremental processing
            checkpoint = self.load_checkpoint() if incremental else {}
            last_watermark = checkpoint.get("last_watermark")

            # Step 1: Extract data from Snowflake
            self.logger.info("Step 1: Extracting data from Snowflake")

            with self.extractor as extractor:
                # Get initial stats
                total_rows = extractor.get_row_count(table_name)
                self.logger.info("Source table stats", table=table_name, total_rows=total_rows)

                # Extract data
                df = extractor.extract_data(
                    table_name=table_name,
                    columns=columns,
                    watermark_column=watermark_column if incremental else None,
                    watermark_value=last_watermark if incremental else None,
                    batch_size=None  # Get all matching rows
                )

            stats["rows_extracted"] = len(df)
            self.logger.info("Data extraction completed", rows=len(df))

            if df.empty:
                self.logger.info("No new data to process")
                stats["end_time"] = datetime.utcnow().isoformat()
                return stats

            # Step 2: Generate embeddings
            self.logger.info("Step 2: Generating embeddings")

            df = self.embedder.embed_dataframe(
                df=df,
                text_column=text_field,
                embedding_column="embedding",
                batch_size=batch_size
            )

            stats["rows_embedded"] = len(df)
            self.logger.info("Embedding generation completed", rows=len(df))

            # Step 3: Create/update search index
            self.logger.info("Step 3: Setting up Azure AI Search index")

            # Determine vector dimensions from first embedding
            vector_dimensions = len(df["embedding"].iloc[0]) if len(df) > 0 else 1536

            self.indexer.create_index(
                vector_dimensions=vector_dimensions,
                recreate=recreate_index
            )

            # Step 4: Index documents
            self.logger.info("Step 4: Indexing documents in Azure AI Search")

            # Prepare metadata columns (all columns except text and embedding)
            metadata_columns = [
                col for col in df.columns
                if col not in [text_field, "embedding", "id"]
            ]

            self.indexer.index_dataframe(
                df=df,
                id_column="id",
                content_column=text_field,
                embedding_column="embedding",
                metadata_columns=metadata_columns,
                timestamp_column=watermark_column,
                batch_size=batch_size
            )

            stats["rows_indexed"] = len(df)
            self.logger.info("Document indexing completed", rows=len(df))

            # Update checkpoint
            if incremental and watermark_column:
                new_watermark = df[watermark_column].max()
                checkpoint = {
                    "last_watermark": new_watermark,
                    "last_run": datetime.utcnow().isoformat(),
                    "rows_processed": len(df)
                }
                self.save_checkpoint(checkpoint)

            # Get final index stats
            total_indexed = self.indexer.get_document_count()
            self.logger.info("Index stats", total_documents=total_indexed)
            stats["total_documents_in_index"] = total_indexed

        except Exception as e:
            self.logger.error("Pipeline execution failed", error=str(e))
            stats["errors"].append(str(e))
            raise

        finally:
            end_time = datetime.utcnow()
            stats["end_time"] = end_time.isoformat()
            stats["duration_seconds"] = (end_time - start_time).total_seconds()

            self.logger.info(
                "Pipeline execution completed",
                duration_seconds=stats["duration_seconds"],
                stats=stats
            )

        return stats

    def reset_checkpoint(self) -> None:
        """Delete checkpoint file to force full reprocessing."""
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()
            self.logger.info("Checkpoint file deleted")
        else:
            self.logger.info("No checkpoint file to delete")
