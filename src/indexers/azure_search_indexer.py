import pandas as pd
from typing import List, Dict, Any, Optional
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch
)
from ..utils.config import Config
from ..utils.logging_config import get_logger


class AzureSearchIndexer:
    """Index documents in Azure AI Search."""

    def __init__(self, config: Config):
        """
        Initialize Azure AI Search indexer.

        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = get_logger(__name__)

        # Initialize credentials
        self.credential = AzureKeyCredential(self.config.azure_search_api_key)

        # Initialize index client
        self.index_client = SearchIndexClient(
            endpoint=self.config.azure_search_endpoint,
            credential=self.credential
        )

        self.index_name = self.config.azure_search_index_name

        self.logger.info(
            "Azure Search indexer initialized",
            endpoint=self.config.azure_search_endpoint,
            index_name=self.index_name
        )

    def create_index(
        self,
        vector_dimensions: int = 1536,
        recreate: bool = False
    ) -> None:
        """
        Create or update the search index.

        Args:
            vector_dimensions: Dimension of embedding vectors (1536 for text-embedding-ada-002)
            recreate: If True, delete existing index before creating
        """
        # Check if index exists
        try:
            existing_index = self.index_client.get_index(self.index_name)
            if recreate:
                self.logger.info("Deleting existing index", index_name=self.index_name)
                self.index_client.delete_index(self.index_name)
            else:
                self.logger.info("Index already exists", index_name=self.index_name)
                return
        except Exception:
            self.logger.info("Index does not exist, creating new", index_name=self.index_name)

        # Define index fields
        fields = [
            SimpleField(
                name="id",
                type=SearchFieldDataType.String,
                key=True,
                filterable=True,
                sortable=True
            ),
            SearchableField(
                name="content",
                type=SearchFieldDataType.String,
                searchable=True
            ),
            SearchField(
                name="embedding",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=vector_dimensions,
                vector_search_profile_name="vector-profile"
            ),
            SearchableField(
                name="metadata",
                type=SearchFieldDataType.String,
                searchable=True,
                filterable=True
            ),
            SimpleField(
                name="last_updated",
                type=SearchFieldDataType.DateTimeOffset,
                filterable=True,
                sortable=True
            )
        ]

        # Configure vector search
        vector_search = VectorSearch(
            algorithms=[
                HnswAlgorithmConfiguration(
                    name="hnsw-algorithm",
                    parameters={
                        "m": 4,
                        "efConstruction": 400,
                        "efSearch": 500,
                        "metric": "cosine"
                    }
                )
            ],
            profiles=[
                VectorSearchProfile(
                    name="vector-profile",
                    algorithm_configuration_name="hnsw-algorithm"
                )
            ]
        )

        # Configure semantic search
        semantic_config = SemanticConfiguration(
            name="semantic-config",
            prioritized_fields=SemanticPrioritizedFields(
                title_field=None,
                content_fields=[SemanticField(field_name="content")],
                keywords_fields=[SemanticField(field_name="metadata")]
            )
        )

        semantic_search = SemanticSearch(
            configurations=[semantic_config]
        )

        # Create index
        index = SearchIndex(
            name=self.index_name,
            fields=fields,
            vector_search=vector_search,
            semantic_search=semantic_search
        )

        try:
            self.index_client.create_index(index)
            self.logger.info(
                "Index created successfully",
                index_name=self.index_name,
                vector_dimensions=vector_dimensions
            )
        except Exception as e:
            self.logger.error("Failed to create index", error=str(e))
            raise

    def index_documents(
        self,
        documents: List[Dict[str, Any]],
        batch_size: Optional[int] = None
    ) -> None:
        """
        Index documents in Azure AI Search.

        Args:
            documents: List of documents to index
            batch_size: Number of documents to index per batch
        """
        if batch_size is None:
            batch_size = self.config.batch_size

        # Get search client for the index
        search_client = SearchClient(
            endpoint=self.config.azure_search_endpoint,
            index_name=self.index_name,
            credential=self.credential
        )

        total_docs = len(documents)
        self.logger.info(
            "Starting document indexing",
            total_documents=total_docs,
            batch_size=batch_size
        )

        indexed_count = 0
        failed_count = 0

        for i in range(0, total_docs, batch_size):
            batch = documents[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_docs + batch_size - 1) // batch_size

            self.logger.info(
                "Indexing batch",
                batch_num=batch_num,
                total_batches=total_batches,
                batch_size=len(batch)
            )

            try:
                result = search_client.upload_documents(documents=batch)

                # Count successes and failures
                for item in result:
                    if item.succeeded:
                        indexed_count += 1
                    else:
                        failed_count += 1
                        self.logger.warning(
                            "Document indexing failed",
                            document_id=item.key,
                            error=item.error_message
                        )

                self.logger.info(
                    "Batch indexed",
                    batch_num=batch_num,
                    indexed=indexed_count,
                    failed=failed_count
                )

            except Exception as e:
                self.logger.error(
                    "Failed to index batch",
                    batch_num=batch_num,
                    error=str(e)
                )
                failed_count += len(batch)

        self.logger.info(
            "Document indexing completed",
            total_documents=total_docs,
            indexed=indexed_count,
            failed=failed_count
        )

    def index_dataframe(
        self,
        df: pd.DataFrame,
        id_column: str = "id",
        content_column: str = "content",
        embedding_column: str = "embedding",
        metadata_columns: Optional[List[str]] = None,
        timestamp_column: Optional[str] = None,
        batch_size: Optional[int] = None
    ) -> None:
        """
        Index a DataFrame in Azure AI Search.

        Args:
            df: DataFrame to index
            id_column: Column to use as document ID
            content_column: Column containing text content
            embedding_column: Column containing embeddings
            metadata_columns: Columns to include as metadata
            timestamp_column: Column containing timestamp
            batch_size: Batch size for indexing
        """
        self.logger.info(
            "Converting DataFrame to documents",
            rows=len(df),
            id_column=id_column,
            content_column=content_column
        )

        documents = []

        for _, row in df.iterrows():
            doc = {
                "id": str(row[id_column]),
                "content": str(row[content_column]),
                "embedding": row[embedding_column]
            }

            # Add metadata
            if metadata_columns:
                metadata = {col: str(row[col]) for col in metadata_columns if col in df.columns}
                doc["metadata"] = str(metadata)
            else:
                doc["metadata"] = ""

            # Add timestamp
            if timestamp_column and timestamp_column in df.columns:
                doc["last_updated"] = row[timestamp_column]
            else:
                import datetime
                doc["last_updated"] = datetime.datetime.utcnow().isoformat() + "Z"

            documents.append(doc)

        self.logger.info("Documents prepared", count=len(documents))

        # Index documents
        self.index_documents(documents, batch_size=batch_size)

    def delete_documents(self, document_ids: List[str]) -> None:
        """
        Delete documents from the index.

        Args:
            document_ids: List of document IDs to delete
        """
        search_client = SearchClient(
            endpoint=self.config.azure_search_endpoint,
            index_name=self.index_name,
            credential=self.credential
        )

        documents_to_delete = [{"id": doc_id} for doc_id in document_ids]

        try:
            result = search_client.delete_documents(documents=documents_to_delete)
            self.logger.info(
                "Documents deleted",
                count=len(document_ids),
                succeeded=sum(1 for item in result if item.succeeded)
            )
        except Exception as e:
            self.logger.error("Failed to delete documents", error=str(e))
            raise

    def get_document_count(self) -> int:
        """
        Get the number of documents in the index.

        Returns:
            Number of documents
        """
        search_client = SearchClient(
            endpoint=self.config.azure_search_endpoint,
            index_name=self.index_name,
            credential=self.credential
        )

        try:
            results = search_client.search(search_text="*", include_total_count=True)
            count = results.get_count()
            self.logger.info("Retrieved document count", count=count)
            return count
        except Exception as e:
            self.logger.error("Failed to get document count", error=str(e))
            raise
