import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from src.embeddings.azure_openai_embedder import AzureOpenAIEmbedder
from src.utils.config import Config


@pytest.fixture
def mock_config():
    """Create a mock configuration object."""
    config = Mock(spec=Config)
    config.azure_openai_api_key = "test_api_key"
    config.azure_openai_api_version = "2024-02-01"
    config.azure_openai_endpoint = "https://test.openai.azure.com/"
    config.azure_openai_embedding_deployment = "text-embedding-ada-002"
    config.batch_size = 10
    return config


@pytest.fixture
def embedder(mock_config):
    """Create an AzureOpenAIEmbedder instance with mock config."""
    with patch('src.embeddings.azure_openai_embedder.AzureOpenAI'):
        return AzureOpenAIEmbedder(mock_config)


class TestAzureOpenAIEmbedder:
    """Test cases for AzureOpenAIEmbedder."""

    def test_initialization(self, embedder, mock_config):
        """Test embedder initialization."""
        assert embedder.config == mock_config
        assert embedder.deployment == mock_config.azure_openai_embedding_deployment

    def test_generate_embedding(self, embedder):
        """Test generating a single embedding."""
        # Mock response
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
        embedder.client.embeddings.create.return_value = mock_response

        # Execute
        embedding = embedder.generate_embedding("test text")

        # Verify
        assert embedding == [0.1, 0.2, 0.3]
        embedder.client.embeddings.create.assert_called_once()

    def test_generate_embeddings_batch(self, embedder):
        """Test generating embeddings for a batch of texts."""
        # Mock response
        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(embedding=[0.1, 0.2, 0.3]),
            MagicMock(embedding=[0.4, 0.5, 0.6])
        ]
        embedder.client.embeddings.create.return_value = mock_response

        # Execute
        texts = ["text1", "text2"]
        embeddings = embedder.generate_embeddings_batch(texts, batch_size=2)

        # Verify
        assert len(embeddings) == 2
        assert embeddings[0] == [0.1, 0.2, 0.3]
        assert embeddings[1] == [0.4, 0.5, 0.6]

    def test_embed_dataframe(self, embedder):
        """Test adding embeddings to a DataFrame."""
        # Setup test data
        df = pd.DataFrame({
            'id': [1, 2],
            'content': ['text1', 'text2']
        })

        # Mock response
        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(embedding=[0.1, 0.2, 0.3]),
            MagicMock(embedding=[0.4, 0.5, 0.6])
        ]
        embedder.client.embeddings.create.return_value = mock_response

        # Execute
        result_df = embedder.embed_dataframe(df, text_column='content')

        # Verify
        assert 'embedding' in result_df.columns
        assert len(result_df) == 2
        assert result_df['embedding'].iloc[0] == [0.1, 0.2, 0.3]

    def test_chunk_text_short_text(self, embedder):
        """Test chunking text that doesn't need splitting."""
        text = "Short text"
        chunks = embedder.chunk_text(text, chunk_size=100)

        assert len(chunks) == 1
        assert chunks[0] == text

    def test_chunk_text_long_text(self, embedder):
        """Test chunking long text."""
        text = "a" * 5000
        chunks = embedder.chunk_text(text, chunk_size=2000, overlap=200)

        assert len(chunks) > 1
        assert all(len(chunk) <= 2000 for chunk in chunks)

    def test_retry_on_failure(self, embedder):
        """Test retry logic on API failure."""
        # Mock to fail once then succeed
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]

        embedder.client.embeddings.create.side_effect = [
            Exception("API Error"),
            mock_response
        ]

        # Execute
        embeddings = embedder.generate_embeddings_batch(
            ["text1"],
            max_retries=3,
            retry_delay=0
        )

        # Verify it retried and succeeded
        assert len(embeddings) == 1
        assert embedder.client.embeddings.create.call_count == 2
