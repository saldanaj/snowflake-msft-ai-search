import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv


class Config:
    """Configuration manager for the pipeline."""

    def __init__(self, config_path: Optional[str] = None, env_path: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to YAML config file. Defaults to config/config.yaml
            env_path: Path to .env file. Defaults to config/.env
        """
        # Determine project root
        self.project_root = Path(__file__).parent.parent.parent

        # Load environment variables
        if env_path is None:
            env_path = self.project_root / "config" / ".env"
        load_dotenv(env_path)

        # Load YAML configuration
        if config_path is None:
            config_path = self.project_root / "config" / "config.yaml"

        self.config_data = self._load_yaml(config_path)

    def _load_yaml(self, config_path: Path) -> Dict[str, Any]:
        """Load YAML configuration file."""
        if not Path(config_path).exists():
            return {}

        with open(config_path, 'r') as f:
            return yaml.safe_load(f) or {}

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.

        Args:
            key: Configuration key in dot notation (e.g., 'pipeline.source.table_name')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config_data

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

        return value if value is not None else default

    # Snowflake configuration
    @property
    def snowflake_account(self) -> str:
        return os.getenv("SNOWFLAKE_ACCOUNT", "")

    @property
    def snowflake_user(self) -> str:
        return os.getenv("SNOWFLAKE_USER", "")

    @property
    def snowflake_password(self) -> str:
        return os.getenv("SNOWFLAKE_PASSWORD", "")

    @property
    def snowflake_database(self) -> str:
        return os.getenv("SNOWFLAKE_DATABASE", "")

    @property
    def snowflake_schema(self) -> str:
        return os.getenv("SNOWFLAKE_SCHEMA", "")

    @property
    def snowflake_warehouse(self) -> str:
        return os.getenv("SNOWFLAKE_WAREHOUSE", "")

    @property
    def snowflake_role(self) -> str:
        return os.getenv("SNOWFLAKE_ROLE", "")

    # Azure OpenAI configuration
    @property
    def azure_openai_endpoint(self) -> str:
        return os.getenv("AZURE_OPENAI_ENDPOINT", "")

    @property
    def azure_openai_api_key(self) -> str:
        return os.getenv("AZURE_OPENAI_API_KEY", "")

    @property
    def azure_openai_embedding_deployment(self) -> str:
        return os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")

    @property
    def azure_openai_api_version(self) -> str:
        return os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")

    # Azure AI Search configuration
    @property
    def azure_search_endpoint(self) -> str:
        return os.getenv("AZURE_SEARCH_ENDPOINT", "")

    @property
    def azure_search_api_key(self) -> str:
        return os.getenv("AZURE_SEARCH_API_KEY", "")

    @property
    def azure_search_index_name(self) -> str:
        return os.getenv("AZURE_SEARCH_INDEX_NAME", "snowflake-data-index")

    # Pipeline configuration
    @property
    def batch_size(self) -> int:
        return int(os.getenv("BATCH_SIZE", "100"))

    @property
    def log_level(self) -> str:
        return os.getenv("LOG_LEVEL", "INFO")

    @property
    def checkpoint_file(self) -> Path:
        """Get checkpoint file path."""
        checkpoint = self.get("pipeline.execution.checkpoint_file", ".checkpoint.json")
        return self.project_root / checkpoint
