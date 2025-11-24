# Running the Pipeline

This guide explains how to run the Snowflake to Azure AI Search data pipeline.

## Prerequisites

- Completed [Setup Guide](01-setup.md)
- Deployed [Azure Infrastructure](02-infrastructure.md)
- Configured `config/.env` and `config/config.yaml`
- Sample data loaded in Snowflake

## Pipeline Overview

The pipeline performs the following steps:

1. **Extract**: Pull data from Snowflake table
2. **Embed**: Generate embeddings using Azure OpenAI
3. **Index**: Upload documents to Azure AI Search

## Basic Usage

### Run Full Pipeline

Process all records in the source table:

```bash
python scripts/run_pipeline.py --full
```

### Run Incremental Pipeline

Process only new/updated records since last run:

```bash
python scripts/run_pipeline.py --incremental
```

### Recreate Search Index

Delete and recreate the search index before indexing:

```bash
python scripts/run_pipeline.py --full --recreate-index
```

## Command Line Options

```bash
python scripts/run_pipeline.py [OPTIONS]

Options:
  --config PATH          Path to config YAML file (default: config/config.yaml)
  --env PATH             Path to .env file (default: config/.env)
  --incremental          Run in incremental mode (only new/updated records)
  --full                 Run in full mode (all records)
  --recreate-index       Recreate the search index before indexing
  --reset-checkpoint     Reset checkpoint to force full reprocessing
  --log-level LEVEL      Logging level (DEBUG|INFO|WARNING|ERROR|CRITICAL)
  --json-logs            Output logs in JSON format
```

## Examples

### First Time Setup

When running for the first time:

```bash
# Create the index and process all data
python scripts/run_pipeline.py --full --recreate-index
```

### Regular Updates

For subsequent runs to process new data:

```bash
# Process only new/updated records
python scripts/run_pipeline.py --incremental
```

### Debugging

Enable debug logging to troubleshoot issues:

```bash
python scripts/run_pipeline.py --full --log-level DEBUG
```

### Force Full Reindex

Reset checkpoint and reprocess all data:

```bash
python scripts/run_pipeline.py --full --reset-checkpoint --recreate-index
```

## Monitoring Pipeline Execution

### Console Output

The pipeline provides real-time console output showing:

```
Pipeline execution started
Step 1: Extracting data from Snowflake
  Source table stats: 1000 total rows
  Data extraction completed: 1000 rows

Step 2: Generating embeddings
  Processing batch 1/10 (100 documents)
  ...
  Embedding generation completed: 1000 rows

Step 3: Setting up Azure AI Search index
  Index created successfully

Step 4: Indexing documents in Azure AI Search
  Indexing batch 1/10 (100 documents)
  ...
  Document indexing completed: 1000 rows

==================================================
Pipeline Execution Summary
==================================================
Rows extracted: 1000
Rows embedded: 1000
Rows indexed: 1000
Total documents in index: 1000
Duration: 45.23 seconds
==================================================
```

### Log Files

With JSON logging enabled, logs can be captured for analysis:

```bash
python scripts/run_pipeline.py --full --json-logs > pipeline.log
```

## Incremental Processing

The pipeline supports incremental processing using a watermark column.

### How It Works

1. Pipeline extracts the maximum value of `watermark_column` from the last run
2. Only rows with `watermark_column > last_watermark` are processed
3. New watermark is saved in `.checkpoint.json`

### Configuration

In `config/config.yaml`:

```yaml
pipeline:
  source:
    watermark_column: "updated_at"  # Column to track changes
  execution:
    incremental: true               # Enable incremental by default
    checkpoint_file: ".checkpoint.json"
```

### Checkpoint File

The checkpoint file (`.checkpoint.json`) stores the last processed watermark:

```json
{
  "last_watermark": "2025-01-15T10:30:00.000Z",
  "last_run": "2025-01-15T10:35:00.000Z",
  "rows_processed": 150
}
```

To force a full reprocess, delete or reset this file:

```bash
python scripts/run_pipeline.py --reset-checkpoint
```

## Error Handling

### Common Errors

#### Snowflake Connection Error

```
Failed to connect to Snowflake: 250001 (08001)
```

**Solution**: Verify Snowflake credentials in `config/.env`

#### Azure OpenAI Rate Limit

```
Error 429: Too Many Requests
```

**Solution**: The pipeline has built-in retry logic. For persistent issues:
- Reduce batch size in config
- Increase deployment capacity in Azure

#### Azure Search Indexing Failure

```
Failed to index batch: 400 Bad Request
```

**Solution**: Check that document structure matches index schema

### Retry Behavior

The pipeline automatically retries failed operations:

- Embedding generation: 3 retries with 5-second delay
- Configurable in `config/config.yaml`:

```yaml
pipeline:
  execution:
    max_retries: 3
    retry_delay_seconds: 5
```

## Performance Tuning

### Batch Size

Adjust batch size for embedding and indexing:

In `config/.env`:
```bash
BATCH_SIZE=100  # Increase for faster processing (may hit rate limits)
```

Or in `config/config.yaml`:
```yaml
pipeline:
  embedding:
    batch_size: 100
```

### Text Chunking

For long documents, configure chunking:

```yaml
pipeline:
  embedding:
    chunk_size: 2000      # Characters per chunk
    chunk_overlap: 200    # Overlap between chunks
```

## Verification

### Check Azure AI Search Index

After the pipeline runs, verify the index contains data:

```python
from src.utils.config import Config
from src.indexers.azure_search_indexer import AzureSearchIndexer

config = Config()
indexer = AzureSearchIndexer(config)

count = indexer.get_document_count()
print(f"Index contains {count} documents")
```

### Test Search Queries

Perform a sample search:

```python
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

client = SearchClient(
    endpoint="https://your-service.search.windows.net",
    index_name="snowflake-data-index",
    credential=AzureKeyCredential("your-api-key")
)

results = client.search(search_text="customer satisfaction", top=5)
for result in results:
    print(f"Score: {result['@search.score']}")
    print(f"Content: {result['content']}")
    print("---")
```

## Scheduling

### Manual Execution

Run the pipeline on-demand when needed.

### Scheduled Execution (Windows)

Use Task Scheduler:

1. Create a batch file `run_pipeline.bat`:
```batch
@echo off
cd C:\path\to\snowflake-msft-ai-search
call venv\Scripts\activate.bat
python scripts\run_pipeline.py --incremental
```

2. Schedule in Task Scheduler to run hourly/daily

### Scheduled Execution (Linux)

Use cron:

```bash
# Edit crontab
crontab -e

# Add entry to run hourly
0 * * * * cd /path/to/snowflake-msft-ai-search && ./venv/bin/python scripts/run_pipeline.py --incremental >> logs/pipeline.log 2>&1
```

## Next Steps

- [Future Enhancements](04-future-enhancements.md) - Event-based processing, containerization
- Integrate with conversational AI applications
- Set up monitoring and alerting
