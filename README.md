# Snowflake to Azure AI Search Demo

This demo showcases how to periodically extract data from Snowflake, generate embeddings using Azure OpenAI, and index the data in Azure AI Search for conversational AI applications.

## Architecture

```
Snowflake Database
       ↓
  Extractor (Python)
       ↓
  Embedder (Azure OpenAI)
       ↓
  Indexer
       ↓
Azure AI Search
```

## Prerequisites

- Python 3.10 or higher
- Azure subscription with:
  - Azure OpenAI service access
  - Azure AI Search service
- Snowflake trial account
- Azure CLI (for infrastructure deployment)

## Quick Start

### 1. Set Up Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example configuration files and fill in your values:

```bash
cp config/.env.example config/.env
cp config/config.yaml.example config/config.yaml
```

Edit `config/.env` with your credentials:
- Snowflake connection details
- Azure OpenAI endpoint and API key
- Azure AI Search endpoint and API key

### 3. Deploy Azure Infrastructure (Optional)

```bash
# Login to Azure
az login

# Deploy infrastructure using Bicep
./scripts/deploy_infrastructure.sh
```

### 4. Run the Pipeline

```bash
# Execute the pipeline manually
python scripts/run_pipeline.py
```

## Project Structure

```
snowflake-msft-ai-search/
├── src/                    # Source code
│   ├── extractors/         # Snowflake data extraction
│   ├── embeddings/         # Azure OpenAI embedding generation
│   ├── indexers/           # Azure AI Search indexing
│   ├── orchestration/      # Pipeline orchestration
│   └── utils/              # Utilities and configuration
├── infrastructure/         # Bicep IaC templates
├── config/                 # Configuration files
├── scripts/                # Deployment and execution scripts
├── tests/                  # Unit tests
└── docs/                   # Documentation
```

## Pipeline Components

### Extractor
Connects to Snowflake and extracts data based on configurable queries. Supports incremental extraction using watermark columns.

### Embedder
Generates embeddings using Azure OpenAI's text-embedding models. Handles batching and rate limiting.

### Indexer
Creates and populates Azure AI Search indexes with the embedded data. Supports both full and incremental indexing.

### Orchestration
Coordinates the pipeline execution, handles error recovery, and maintains state.

## Future Enhancements

- Event-based triggering using Azure Event Hubs
- Containerization with Azure Container Apps
- Monitoring and alerting
- Incremental indexing with change detection

## Documentation

- [Setup Guide](docs/01-setup.md)
- [Infrastructure Deployment](docs/02-infrastructure.md)
- [Running the Pipeline](docs/03-running-pipeline.md)
- [Future Enhancements](docs/04-future-enhancements.md)

## License

MIT
