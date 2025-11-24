import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from src.indexers.azure_search_indexer import AzureSearchIndexer
from src.utils.config import Config


@pytest.fixture
def mock_config():
    """Create a mock configuration object."""
    config = Mock(spec=Config)
    config.azure_search_endpoint = "https://test.search.windows.net"
    config.azure_search_api_key = "test_api_key"
    config.azure_search_index_name = "test-index"
    config.batch_size = 10
    return config


@pytest.fixture
def indexer(mock_config):
    """Create an AzureSearchIndexer instance with mock config."""
    with patch('src.indexers.azure_search_indexer.SearchIndexClient'), \
         patch('src.indexers.azure_search_indexer.AzureKeyCredential'):
        return AzureSearchIndexer(mock_config)


class TestAzureSearchIndexer:
    """Test cases for AzureSearchIndexer."""

    def test_initialization(self, indexer, mock_config):
        """Test indexer initialization."""
        assert indexer.config == mock_config
        assert indexer.index_name == mock_config.azure_search_index_name

    @patch('src.indexers.azure_search_indexer.SearchClient')
    def test_create_index_new(self, mock_search_client, indexer):
        """Test creating a new index."""
        # Mock that index doesn't exist
        indexer.index_client.get_index.side_effect = Exception("Not found")

        # Execute
        indexer.create_index(vector_dimensions=1536, recreate=False)

        # Verify
        indexer.index_client.create_index.assert_called_once()

    @patch('src.indexers.azure_search_indexer.SearchClient')
    def test_create_index_recreate(self, mock_search_client, indexer):
        """Test recreating an existing index."""
        # Mock that index exists
        mock_index = Mock()
        indexer.index_client.get_index.return_value = mock_index

        # Execute
        indexer.create_index(vector_dimensions=1536, recreate=True)

        # Verify
        indexer.index_client.delete_index.assert_called_once()
        indexer.index_client.create_index.assert_called_once()

    @patch('src.indexers.azure_search_indexer.SearchClient')
    def test_index_documents(self, mock_search_client_class, indexer):
        """Test indexing documents."""
        # Setup mock search client
        mock_search_client = Mock()
        mock_search_client_class.return_value = mock_search_client

        # Mock successful upload
        mock_result = [Mock(succeeded=True, key="1")]
        mock_search_client.upload_documents.return_value = mock_result

        # Test documents
        documents = [
            {
                "id": "1",
                "content": "test content",
                "embedding": [0.1, 0.2, 0.3],
                "metadata": "test",
                "last_updated": "2025-01-01T00:00:00Z"
            }
        ]

        # Execute
        indexer.index_documents(documents, batch_size=10)

        # Verify
        mock_search_client.upload_documents.assert_called_once_with(documents=documents)

    @patch('src.indexers.azure_search_indexer.SearchClient')
    def test_index_dataframe(self, mock_search_client_class, indexer):
        """Test indexing a DataFrame."""
        # Setup mock
        mock_search_client = Mock()
        mock_search_client_class.return_value = mock_search_client
        mock_result = [Mock(succeeded=True, key="1"), Mock(succeeded=True, key="2")]
        mock_search_client.upload_documents.return_value = mock_result

        # Test DataFrame
        df = pd.DataFrame({
            'id': ['1', '2'],
            'content': ['text1', 'text2'],
            'embedding': [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
            'category': ['cat1', 'cat2']
        })

        # Execute
        indexer.index_dataframe(
            df,
            id_column='id',
            content_column='content',
            embedding_column='embedding',
            metadata_columns=['category']
        )

        # Verify
        mock_search_client.upload_documents.assert_called_once()
        call_args = mock_search_client.upload_documents.call_args
        documents = call_args.kwargs['documents']

        assert len(documents) == 2
        assert documents[0]['id'] == '1'
        assert documents[0]['content'] == 'text1'
        assert documents[0]['embedding'] == [0.1, 0.2, 0.3]

    @patch('src.indexers.azure_search_indexer.SearchClient')
    def test_delete_documents(self, mock_search_client_class, indexer):
        """Test deleting documents from index."""
        mock_search_client = Mock()
        mock_search_client_class.return_value = mock_search_client
        mock_result = [Mock(succeeded=True, key="1")]
        mock_search_client.delete_documents.return_value = mock_result

        # Execute
        indexer.delete_documents(["1", "2"])

        # Verify
        mock_search_client.delete_documents.assert_called_once()

    @patch('src.indexers.azure_search_indexer.SearchClient')
    def test_get_document_count(self, mock_search_client_class, indexer):
        """Test getting document count from index."""
        mock_search_client = Mock()
        mock_search_client_class.return_value = mock_search_client

        # Mock search results
        mock_results = Mock()
        mock_results.get_count.return_value = 100
        mock_search_client.search.return_value = mock_results

        # Execute
        count = indexer.get_document_count()

        # Verify
        assert count == 100
        mock_search_client.search.assert_called_once()

    @patch('src.indexers.azure_search_indexer.SearchClient')
    def test_batch_indexing(self, mock_search_client_class, indexer):
        """Test indexing documents in batches."""
        mock_search_client = Mock()
        mock_search_client_class.return_value = mock_search_client
        mock_result = [Mock(succeeded=True, key=str(i)) for i in range(10)]
        mock_search_client.upload_documents.return_value = mock_result

        # Create 25 documents with batch size of 10
        documents = [
            {
                "id": str(i),
                "content": f"content{i}",
                "embedding": [0.1, 0.2, 0.3],
                "metadata": "",
                "last_updated": "2025-01-01T00:00:00Z"
            }
            for i in range(25)
        ]

        # Execute
        indexer.index_documents(documents, batch_size=10)

        # Verify - should be called 3 times (10 + 10 + 5)
        assert mock_search_client.upload_documents.call_count == 3
