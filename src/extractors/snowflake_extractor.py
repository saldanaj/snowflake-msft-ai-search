import snowflake.connector
import pandas as pd
from typing import Optional, List, Dict, Any
from datetime import datetime
from ..utils.config import Config
from ..utils.logging_config import get_logger


class SnowflakeExtractor:
    """Extract data from Snowflake database."""

    def __init__(self, config: Config):
        """
        Initialize Snowflake extractor.

        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = get_logger(__name__)
        self.connection = None

    def connect(self) -> None:
        """Establish connection to Snowflake."""
        try:
            self.connection = snowflake.connector.connect(
                account=self.config.snowflake_account,
                user=self.config.snowflake_user,
                password=self.config.snowflake_password,
                database=self.config.snowflake_database,
                schema=self.config.snowflake_schema,
                warehouse=self.config.snowflake_warehouse,
                role=self.config.snowflake_role
            )
            self.logger.info(
                "Connected to Snowflake",
                account=self.config.snowflake_account,
                database=self.config.snowflake_database
            )
        except Exception as e:
            self.logger.error("Failed to connect to Snowflake", error=str(e))
            raise

    def disconnect(self) -> None:
        """Close connection to Snowflake."""
        if self.connection:
            self.connection.close()
            self.logger.info("Disconnected from Snowflake")

    def extract_data(
        self,
        table_name: str,
        columns: Optional[List[str]] = None,
        watermark_column: Optional[str] = None,
        watermark_value: Optional[Any] = None,
        batch_size: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Extract data from Snowflake table.

        Args:
            table_name: Name of the table to extract from
            columns: List of columns to extract (None = all columns)
            watermark_column: Column to use for incremental extraction
            watermark_value: Last watermark value for incremental extraction
            batch_size: Number of rows to fetch

        Returns:
            DataFrame containing extracted data
        """
        if not self.connection:
            self.connect()

        # Build query
        column_list = ", ".join(columns) if columns else "*"
        query = f"SELECT {column_list} FROM {table_name}"

        # Add incremental filter if watermark is provided
        if watermark_column and watermark_value:
            query += f" WHERE {watermark_column} > '{watermark_value}'"

        # Add ordering for consistent results
        if watermark_column:
            query += f" ORDER BY {watermark_column}"

        # Add limit if batch size is specified
        if batch_size:
            query += f" LIMIT {batch_size}"

        self.logger.info("Executing query", query=query)

        try:
            # Execute query and fetch results
            cursor = self.connection.cursor()
            cursor.execute(query)

            # Fetch results into DataFrame
            df = cursor.fetch_pandas_all()

            self.logger.info(
                "Data extracted successfully",
                rows=len(df),
                columns=list(df.columns)
            )

            cursor.close()
            return df

        except Exception as e:
            self.logger.error("Failed to extract data", error=str(e), query=query)
            raise

    def get_latest_watermark(
        self,
        table_name: str,
        watermark_column: str
    ) -> Optional[Any]:
        """
        Get the latest watermark value from a table.

        Args:
            table_name: Name of the table
            watermark_column: Column to get max value from

        Returns:
            Latest watermark value
        """
        if not self.connection:
            self.connect()

        query = f"SELECT MAX({watermark_column}) as max_value FROM {table_name}"

        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()

            if result and result[0]:
                self.logger.info(
                    "Retrieved latest watermark",
                    table=table_name,
                    column=watermark_column,
                    value=result[0]
                )
                return result[0]

            return None

        except Exception as e:
            self.logger.error(
                "Failed to get latest watermark",
                error=str(e),
                table=table_name,
                column=watermark_column
            )
            raise

    def get_row_count(self, table_name: str) -> int:
        """
        Get total row count for a table.

        Args:
            table_name: Name of the table

        Returns:
            Number of rows in the table
        """
        if not self.connection:
            self.connect()

        query = f"SELECT COUNT(*) as row_count FROM {table_name}"

        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()

            count = result[0] if result else 0
            self.logger.info("Retrieved row count", table=table_name, count=count)
            return count

        except Exception as e:
            self.logger.error("Failed to get row count", error=str(e), table=table_name)
            raise

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
