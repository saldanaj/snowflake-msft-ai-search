# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a clinical notes data pipeline that extracts data from Snowflake, generates embeddings using Azure OpenAI, and indexes the data in Azure AI Search for conversational AI/RAG applications. The pipeline supports incremental processing using watermark-based extraction.

## Essential Commands

### Environment Setup
```bash
# Windows
.\scripts\install_requirements.ps1

# Linux/Mac
chmod +x scripts/install_requirements.sh
./scripts/install_requirements.sh

# Manual installation (after activating venv)
pip install -r requirements.txt
```

### Running the Pipeline
```bash
# First run - create index and load all data
python scripts/run_pipeline.py --full --recreate-index

# Incremental run - only new/updated records
python scripts/run_pipeline.py --incremental

# Full refresh without recreating index
python scripts/run_pipeline.py --full
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_extractor.py

# Run specific test
pytest tests/test_extractor.py::test_extract_data_success
```

### Data Generation
```bash
# Generate synthetic clinical notes (outputs JSON and SQL)
python scripts/generate_synthetic_notes.py
```

### Infrastructure Deployment
```bash
# Deploy Azure resources using Bicep
az deployment group create \
  --resource-group <rg-name> \
  --template-file infrastructure/bicep/main.bicep \
  --parameters baseName=<your-base-name> environment=dev
```

## Architecture

### Component Structure

The codebase follows a **modular ETL pipeline pattern** with clear separation of concerns:

```
Snowflake → Extractor → Embedder → Indexer → Azure AI Search
              ↑           ↑          ↑
              └───── Pipeline Orchestrator ─────┘
                    (Checkpoint Management)
```

**Core Components:**
- **Extractors** (`src/extractors/`): Pull data from Snowflake with watermark-based incremental support
- **Embedders** (`src/embeddings/`): Generate vector embeddings using Azure OpenAI with batching and retry logic
- **Indexers** (`src/indexers/`): Create and populate Azure AI Search indexes with vector search capabilities
- **Pipeline** (`src/orchestration/`): Orchestrates the end-to-end flow, manages checkpoints, handles errors
- **Config** (`src/utils/`): Two-tier configuration (YAML for structure, .env for secrets)

### Data Flow

1. **Extract**: Query Snowflake with optional watermark filter (`WHERE updated_at > last_checkpoint`)
2. **Transform**: Generate embeddings for the `full_clinical_note` field (1536-dimensional vectors)
3. **Load**: Batch upload to Azure AI Search as documents with vector embeddings
4. **Checkpoint**: Save last processed watermark to `.checkpoint.json` for incremental runs

### Configuration Strategy

**Two-tier configuration pattern:**
- **`.env`**: Secrets (passwords, API keys, endpoints)
- **`config.yaml`**: Business logic (table names, column mappings, batch sizes)

Access pattern: `config.get("pipeline.source.table_name")` for YAML, `config.snowflake_password` for env vars.

### Incremental Processing

Uses **watermark-based incremental processing**:
- Checkpoint file (`.checkpoint.json`) tracks `last_watermark` timestamp
- Each run queries only records with `updated_at > last_watermark`
- New watermark saved after successful processing
- Full refresh available via `--full` flag

### Index Schema

Azure AI Search index structure:
- **id**: Document key (maps to `note_id` from Snowflake)
- **content**: Full clinical note text (searchable)
- **embedding**: 1536-dimensional vector for semantic search (HNSW algorithm)
- **metadata**: JSON string containing all other table columns (patient info, vitals, etc.)
- **last_updated**: Timestamp for tracking freshness

Only the `full_clinical_note` field is embedded; all other columns are stored as filterable metadata.

## Key Design Patterns

### Context Manager Pattern
All extractors use context managers for automatic resource cleanup:
```python
with SnowflakeExtractor(config) as extractor:
    df = extractor.extract_data(watermark_value=last_checkpoint)
# Connection automatically closed
```

### Batch Processing Pattern
Both embedder and indexer process data in batches to prevent memory issues and handle API rate limits:
```python
for i in range(0, len(items), batch_size):
    batch = items[i:i + batch_size]
    process_batch(batch)
```

### Retry Pattern
Embedder implements retry logic with exponential backoff for API failures (max 3 retries, 5s delay).

### Structured Logging
Uses `structlog` for JSON-formatted logs:
```python
logger.info("Data extracted", rows=75, table="PATIENT_CLINICAL_NOTES")
# Output: {"event": "Data extracted", "rows": 75, "table": "PATIENT_CLINICAL_NOTES"}
```

## Configuration Files

### Required Setup
```bash
# Copy example configs
cp config/.env.example config/.env
cp config/config.yaml.example config/config.yaml

# Edit .env with your credentials
# Edit config.yaml if table schema changes
```

### Key Configuration Points

**Snowflake Connection** (`.env`):
- `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`
- `SNOWFLAKE_DATABASE`, `SNOWFLAKE_SCHEMA`, `SNOWFLAKE_WAREHOUSE`

**Azure Services** (`.env`):
- `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT`
- `AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_API_KEY`, `AZURE_SEARCH_INDEX_NAME`

**Table Schema** (`config.yaml`):
- `pipeline.source.table_name`: Snowflake table name
- `pipeline.source.columns`: List of columns to extract
- `pipeline.source.watermark_column`: Column for incremental processing (must be timestamp)
- `pipeline.embedding.text_field`: Column to embed (should be your main text content)

## Testing Patterns

Tests use **mock-based unit testing** with `pytest` and `pytest-mock`:
- External dependencies (Snowflake, OpenAI, Azure Search) are mocked
- Each component tested in isolation
- Fixtures provide reusable test objects
- Focus on business logic, not external API behavior

**Test structure:**
```python
@pytest.fixture
def mock_config():
    config = Mock(spec=Config)
    config.snowflake_account = "test"
    return config

def test_component(mock_config):
    with patch('external.api') as mock_api:
        component = MyComponent(mock_config)
        result = component.do_something()
        assert result == expected
```

## Infrastructure (Bicep)

### Modular Bicep Architecture
- **`main.bicep`**: Orchestrator that composes modules
- **`modules/ai-search.bicep`**: Azure AI Search service
- **`modules/openai.bicep`**: Azure OpenAI + embedding deployment
- **`modules/storage.bicep`**: Storage for logs/checkpoints
- **`modules/eventhub.bicep`**: Event Hub (optional, for future event-driven processing)

### Naming Convention
Pattern: `${baseName}-${resource}-${environment}`
Example: `clinical-notes-search-dev`

### Deployment Outputs
All modules output secrets (endpoints, keys) that can be used to populate `.env`:
```bicep
output searchServiceEndpoint string = 'https://${searchService.name}.search.windows.net'
output searchServiceAdminKey string = searchService.listAdminKeys().primaryKey
```

## Important Constraints

### Snowflake Schema Requirements
- Table must have a **timestamp column** for incremental processing (e.g., `updated_at`)
- Table must have an **ID column** (first column in `config.yaml` columns list is used as ID)
- The **text field** to be embedded must be a TEXT or VARCHAR column

### Azure OpenAI Embeddings
- Model: `text-embedding-ada-002` (1536 dimensions)
- Default batch size: 100 texts per API call
- Rate limits depend on deployment capacity (TPM - tokens per minute)
- Long texts are automatically chunked (default: 2000 chars with 200 char overlap)

### Azure AI Search
- Index uses **HNSW algorithm** for vector search (efficient for semantic similarity)
- Vector field configured as `Collection(Edm.Single)` with 1536 dimensions
- Semantic configuration enabled for hybrid search capabilities
- Default batch size: 100 documents per upload

### Checkpoint Management
- Checkpoint file (`.checkpoint.json`) is **file-based** and local
- Not suitable for distributed/parallel processing (single-node limitation)
- Contains: `last_watermark`, `last_run`, `rows_processed`
- Manually delete checkpoint file to force full refresh

## Common Modifications

### Adding a New Table
1. Update Snowflake to create the new table
2. Update `config/config.yaml`:
   - Change `pipeline.source.table_name`
   - Update `pipeline.source.columns` list
   - Update `pipeline.embedding.text_field` to your main text column
3. Delete `.checkpoint.json` to start fresh
4. Run with `--full --recreate-index`

### Changing Embedding Model
1. Deploy new model in Azure OpenAI
2. Update `.env`: Change `AZURE_OPENAI_DEPLOYMENT` to new deployment name
3. If dimensions change (not 1536), update `src/indexers/azure_search_indexer.py` vector field configuration
4. Run with `--recreate-index` to rebuild index with new embedding dimensions

### Adjusting Batch Sizes
Edit `config/config.yaml`:
- `pipeline.embedding.batch_size`: Number of texts per OpenAI API call
- `pipeline.indexer.batch_size`: Number of documents per Azure Search upload
- Increase for better throughput, decrease if hitting rate limits or memory issues

## Troubleshooting

### Pipeline fails with "no checkpoint found"
Normal on first run. Run with `--full` flag to process all data.

### Embedding API rate limit errors
- Reduce `pipeline.embedding.batch_size` in config.yaml
- Increase deployment capacity (TPM) in Azure OpenAI
- Add delay between batches in embedder code

### Index already exists error
Use `--recreate-index` flag to delete and recreate the index (WARNING: deletes all data in index).

### Snowflake connection timeout
- Verify credentials in `.env`
- Check warehouse is running (auto-resume should start it)
- Verify network access (firewall, VPN)

## Documentation Structure

- **`QUICKSTART.md`**: 30-minute guided setup (start here)
- **`GETTING_STARTED.md`**: Overview and file locations
- **`docs/SNOWFLAKE_SETUP.md`**: Detailed Snowflake database setup
- **`docs/02-infrastructure.md`**: Azure infrastructure deployment
- **`docs/03-running-pipeline.md`**: Pipeline operations and troubleshooting
- **`docs/04-future-enhancements.md`**: Ideas for extending the demo
- **`DATA_PREPARATION_SUMMARY.md`**: Summary of data preparation work

## Critical Implementation Details

### Dynamic ID Column Resolution
Pipeline dynamically determines the ID column from the first column in the config:
```python
id_column = columns[0] if columns else df.columns[0]
```
Ensure your ID column is listed first in `config.yaml` columns list.

### Metadata Serialization
All columns except `id`, `content`, `embedding`, and timestamp are stringified into a single `metadata` JSON field:
```python
metadata_columns = [
    col for col in df.columns
    if col not in [text_field, "embedding", id_column]
]
metadata_json = json.dumps(row[metadata_columns].to_dict())
```

### Watermark Tracking
Max watermark is calculated from the entire batch, not per-record:
```python
new_watermark = df[watermark_column].max()
checkpoint["last_watermark"] = new_watermark.isoformat()
```

### Text Chunking for Long Documents
If a clinical note exceeds `chunk_size` (default 2000 chars), it's split with overlap:
```python
chunks = []
for i in range(0, len(text), chunk_size - chunk_overlap):
    chunk = text[i:i + chunk_size]
    chunks.append(chunk)
```
Each chunk is embedded separately, then averaged.

## Extension Points

### Future Enhancements Supported
- **Event-driven processing**: EventHub module scaffolded in Bicep
- **Multi-table support**: Can extend pipeline to handle multiple source tables
- **Parallel processing**: Architecture supports ThreadPoolExecutor for concurrent embedding generation
- **Custom embedders**: Embedder interface allows pluggable implementations (HuggingFace, Cohere, etc.)
- **Advanced checkpointing**: File-based checkpointing can be replaced with blob storage or database

### RAG Application Integration
This pipeline prepares data for RAG (Retrieval Augmented Generation):
1. User question → Generate embedding
2. Vector search in Azure AI Search → Retrieve similar clinical notes
3. Pass retrieved notes + question to LLM → Generate answer

The index is RAG-ready with semantic search capabilities and metadata for filtering.
