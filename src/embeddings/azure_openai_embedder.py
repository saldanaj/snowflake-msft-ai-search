import time
import pandas as pd
from typing import List, Dict, Any, Optional
from openai import AzureOpenAI
from ..utils.config import Config
from ..utils.logging_config import get_logger


class AzureOpenAIEmbedder:
    """Generate embeddings using Azure OpenAI."""

    def __init__(self, config: Config):
        """
        Initialize Azure OpenAI embedder.

        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = get_logger(__name__)

        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            api_key=self.config.azure_openai_api_key,
            api_version=self.config.azure_openai_api_version,
            azure_endpoint=self.config.azure_openai_endpoint
        )

        self.deployment = self.config.azure_openai_embedding_deployment
        self.logger.info(
            "Azure OpenAI embedder initialized",
            deployment=self.deployment,
            endpoint=self.config.azure_openai_endpoint
        )

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector
        """
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.deployment
            )
            return response.data[0].embedding

        except Exception as e:
            self.logger.error("Failed to generate embedding", error=str(e))
            raise

    def generate_embeddings_batch(
        self,
        texts: List[str],
        batch_size: Optional[int] = None,
        max_retries: int = 3,
        retry_delay: int = 5
    ) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts.

        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process in each API call
            max_retries: Maximum number of retries on failure
            retry_delay: Delay in seconds between retries

        Returns:
            List of embedding vectors
        """
        if batch_size is None:
            batch_size = self.config.batch_size

        embeddings = []
        total_texts = len(texts)

        self.logger.info(
            "Starting batch embedding generation",
            total_texts=total_texts,
            batch_size=batch_size
        )

        for i in range(0, total_texts, batch_size):
            batch = texts[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_texts + batch_size - 1) // batch_size

            self.logger.info(
                "Processing batch",
                batch_num=batch_num,
                total_batches=total_batches,
                batch_size=len(batch)
            )

            retry_count = 0
            while retry_count <= max_retries:
                try:
                    response = self.client.embeddings.create(
                        input=batch,
                        model=self.deployment
                    )

                    # Extract embeddings in the correct order
                    batch_embeddings = [item.embedding for item in response.data]
                    embeddings.extend(batch_embeddings)

                    self.logger.info(
                        "Batch processed successfully",
                        batch_num=batch_num,
                        embeddings_generated=len(batch_embeddings)
                    )
                    break

                except Exception as e:
                    retry_count += 1
                    if retry_count > max_retries:
                        self.logger.error(
                            "Failed to process batch after retries",
                            batch_num=batch_num,
                            error=str(e),
                            retries=max_retries
                        )
                        raise

                    self.logger.warning(
                        "Batch processing failed, retrying",
                        batch_num=batch_num,
                        error=str(e),
                        retry_count=retry_count,
                        max_retries=max_retries
                    )
                    time.sleep(retry_delay)

        self.logger.info(
            "Batch embedding generation completed",
            total_embeddings=len(embeddings)
        )

        return embeddings

    def embed_dataframe(
        self,
        df: pd.DataFrame,
        text_column: str,
        embedding_column: str = "embedding",
        batch_size: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Add embeddings to a DataFrame.

        Args:
            df: DataFrame containing text to embed
            text_column: Name of column containing text
            embedding_column: Name of column to store embeddings
            batch_size: Batch size for API calls

        Returns:
            DataFrame with embeddings added
        """
        self.logger.info(
            "Embedding DataFrame",
            rows=len(df),
            text_column=text_column,
            embedding_column=embedding_column
        )

        # Extract texts
        texts = df[text_column].astype(str).tolist()

        # Generate embeddings
        embeddings = self.generate_embeddings_batch(texts, batch_size=batch_size)

        # Add embeddings to DataFrame
        df[embedding_column] = embeddings

        self.logger.info(
            "DataFrame embedding completed",
            rows=len(df),
            embedding_dimension=len(embeddings[0]) if embeddings else 0
        )

        return df

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 2000,
        overlap: int = 200
    ) -> List[str]:
        """
        Split long text into chunks for embedding.

        Args:
            text: Text to chunk
            chunk_size: Maximum characters per chunk
            overlap: Number of characters to overlap between chunks

        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)

            # Move start position, accounting for overlap
            start = end - overlap

        self.logger.info(
            "Text chunked",
            original_length=len(text),
            chunks=len(chunks),
            chunk_size=chunk_size,
            overlap=overlap
        )

        return chunks
