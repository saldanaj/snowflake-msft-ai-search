import pytest
from unittest.mock import Mock, patch
import pandas as pd
from src.extractors.snowflake_extractor import SnowflakeExtractor
from src.utils.config import Config


@pytest.fixture
def mock_config():
    """Create a mock configuration object."""
    config = Mock(spec=Config)
    config.snowflake_account = "test_account"
    config.snowflake_user = "test_user"
    config.snowflake_password = "test_password"
    config.snowflake_database = "test_db"
    config.snowflake_schema = "test_schema"
    config.snowflake_warehouse = "test_warehouse"
    config.snowflake_role = "test_role"
    return config


@pytest.fixture
def extractor(mock_config):
    """Create a SnowflakeExtractor instance with mock config."""
    return SnowflakeExtractor(mock_config)


class TestSnowflakeExtractor:
    """Test cases for SnowflakeExtractor."""

    @patch('src.extractors.snowflake_extractor.snowflake.connector.connect')
    def test_connect_success(self, mock_connect, extractor, mock_config):
        """Test successful connection to Snowflake."""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection

        extractor.connect()

        assert extractor.connection == mock_connection
        mock_connect.assert_called_once_with(
            account=mock_config.snowflake_account,
            user=mock_config.snowflake_user,
            password=mock_config.snowflake_password,
            database=mock_config.snowflake_database,
            schema=mock_config.snowflake_schema,
            warehouse=mock_config.snowflake_warehouse,
            role=mock_config.snowflake_role
        )

    @patch('src.extractors.snowflake_extractor.snowflake.connector.connect')
    def test_extract_data(self, mock_connect, extractor):
        """Test data extraction from Snowflake."""
        # Setup mock connection and cursor
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        # Mock DataFrame response
        test_data = pd.DataFrame({
            'id': [1, 2, 3],
            'content': ['text1', 'text2', 'text3']
        })
        mock_cursor.fetch_pandas_all.return_value = test_data

        # Execute
        result = extractor.extract_data(
            table_name="test_table",
            columns=["id", "content"]
        )

        # Verify
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert list(result.columns) == ['id', 'content']
        mock_cursor.execute.assert_called_once()

    @patch('src.extractors.snowflake_extractor.snowflake.connector.connect')
    def test_get_row_count(self, mock_connect, extractor):
        """Test getting row count from table."""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (100,)

        extractor.connection = mock_connection
        count = extractor.get_row_count("test_table")

        assert count == 100
        mock_cursor.execute.assert_called_once()

    def test_context_manager(self, extractor):
        """Test using extractor as context manager."""
        with patch.object(extractor, 'connect') as mock_connect, \
             patch.object(extractor, 'disconnect') as mock_disconnect:

            with extractor:
                pass

            mock_connect.assert_called_once()
            mock_disconnect.assert_called_once()
