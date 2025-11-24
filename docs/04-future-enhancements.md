# Future Enhancements

This document outlines potential enhancements and future directions for the Snowflake to Azure AI Search demo.

## Event-Based Processing

### Current State
The pipeline currently runs on-demand or on a schedule.

### Enhancement: Event-Driven Architecture

Implement real-time processing triggered by data changes in Snowflake.

#### Architecture

```
Snowflake Table Change → Event Hub → Azure Container App → Pipeline Execution
```

#### Implementation Steps

1. **Configure Snowflake Streams**

Create a stream to track table changes:

```sql
CREATE STREAM CUSTOMER_DATA_STREAM ON TABLE CUSTOMER_DATA;
```

2. **Set Up Change Data Capture**

Create a task to push changes to Event Hub:

```sql
CREATE OR REPLACE TASK PUSH_TO_EVENT_HUB
  WAREHOUSE = DEMO_WAREHOUSE
  SCHEDULE = '1 MINUTE'
WHEN
  SYSTEM$STREAM_HAS_DATA('CUSTOMER_DATA_STREAM')
AS
  -- Use Snowflake's external function to push to Event Hub
  CALL PUSH_STREAM_TO_EVENT_HUB('CUSTOMER_DATA_STREAM');
```

3. **Azure Container App with Event Hub Trigger**

Deploy the pipeline as a container app that responds to Event Hub messages:

```python
# event_handler.py
from azure.eventhub import EventHubConsumerClient

def on_event(partition_context, event):
    # Parse event data
    change_data = json.loads(event.body_as_str())

    # Run pipeline for changed records only
    pipeline.process_changes(change_data)

    partition_context.update_checkpoint(event)

consumer_client = EventHubConsumerClient.from_connection_string(
    conn_str=EVENT_HUB_CONNECTION_STRING,
    consumer_group="$Default",
    eventhub_name=EVENT_HUB_NAME
)

with consumer_client:
    consumer_client.receive(on_event=on_event)
```

4. **Deploy to Azure Container Apps**

```bash
az containerapp create \
  --name snowflake-pipeline \
  --resource-group rg-snowflake-ai-demo \
  --environment my-container-env \
  --image myregistry.azurecr.io/snowflake-pipeline:latest \
  --env-vars \
    EVENTHUB_CONNECTION_STRING=secretref:eventhub-conn \
  --scale-rule-name event-hub-rule \
  --scale-rule-type azure-eventhub \
  --scale-rule-metadata \
    connectionFromEnv=EVENTHUB_CONNECTION_STRING \
    consumerGroup=$Default \
    unprocessedEventThreshold=10
```

## Containerization

### Current State
The demo runs in a Python virtual environment.

### Enhancement: Docker Containerization

#### Dockerfile (Already Scaffolded)

The project includes a `Dockerfile` for containerization:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run pipeline
CMD ["python", "scripts/run_pipeline.py", "--incremental"]
```

#### Build and Run

```bash
# Build image
docker build -t snowflake-ai-pipeline .

# Run container
docker run --env-file config/.env snowflake-ai-pipeline
```

#### Azure Container Registry

Push to Azure Container Registry:

```bash
# Create ACR
az acr create \
  --resource-group rg-snowflake-ai-demo \
  --name snowflakeaidemo \
  --sku Basic

# Login
az acr login --name snowflakeaidemo

# Tag and push
docker tag snowflake-ai-pipeline snowflakeaidemo.azurecr.io/snowflake-pipeline:latest
docker push snowflakeaidemo.azurecr.io/snowflake-pipeline:latest
```

## Advanced Features

### 1. Incremental Schema Evolution

Automatically detect and handle schema changes in Snowflake tables.

```python
class SchemaManager:
    def detect_schema_changes(self, table_name):
        # Compare current schema with last known schema
        # Update index fields if needed
        pass

    def migrate_index(self, old_schema, new_schema):
        # Add new fields to index
        # Reindex affected documents
        pass
```

### 2. Multi-Table Support

Process multiple Snowflake tables into separate or unified indexes.

```yaml
# config/config.yaml
pipeline:
  sources:
    - table_name: "CUSTOMER_DATA"
      index_name: "customers"
      text_field: "description"
    - table_name: "PRODUCT_DATA"
      index_name: "products"
      text_field: "product_description"
```

### 3. Semantic Chunking

Implement intelligent text chunking based on semantic boundaries.

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

def semantic_chunk(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    return splitter.split_text(text)
```

### 4. Hybrid Search

Combine vector search with traditional keyword search.

```python
# Azure AI Search supports hybrid search natively
results = search_client.search(
    search_text="customer satisfaction",  # Keyword search
    vector_queries=[VectorizedQuery(
        vector=query_embedding,            # Vector search
        k_nearest_neighbors=5,
        fields="embedding"
    )],
    query_type="semantic",
    semantic_configuration_name="semantic-config"
)
```

### 5. Data Quality Checks

Add validation and quality checks before indexing.

```python
class DataValidator:
    def validate_record(self, record):
        # Check for required fields
        # Validate data types
        # Check for PII/sensitive data
        # Validate text length
        pass

    def filter_invalid_records(self, df):
        # Remove or flag invalid records
        pass
```

### 6. Monitoring and Observability

Implement comprehensive monitoring.

```python
# Azure Application Insights integration
from opencensus.ext.azure import metrics_exporter
from opencensus.stats import aggregation as aggregation_module
from opencensus.stats import measure as measure_module
from opencensus.stats import stats as stats_module
from opencensus.stats import view as view_module

# Track metrics
metrics = {
    "rows_processed": measure_module.MeasureInt("rows_processed"),
    "embedding_latency": measure_module.MeasureFloat("embedding_latency"),
    "indexing_latency": measure_module.MeasureFloat("indexing_latency"),
    "error_count": measure_module.MeasureInt("error_count")
}
```

### 7. Cost Optimization

Implement strategies to reduce costs.

```python
# Batch embeddings more efficiently
# Use caching for repeated content
# Implement deduplication
# Use Snowflake's result caching

class EmbeddingCache:
    def __init__(self, cache_backend="redis"):
        self.cache = cache_backend

    def get_or_generate(self, text):
        # Check cache first
        cache_key = hashlib.md5(text.encode()).hexdigest()
        cached = self.cache.get(cache_key)

        if cached:
            return cached

        # Generate and cache
        embedding = self.embedder.generate_embedding(text)
        self.cache.set(cache_key, embedding)
        return embedding
```

## Integration with Conversational AI

### RAG Pattern Implementation

Use the indexed data for Retrieval Augmented Generation:

```python
from openai import AzureOpenAI
from azure.search.documents import SearchClient

class RAGAssistant:
    def __init__(self, search_client, openai_client):
        self.search = search_client
        self.openai = openai_client

    def answer_question(self, question):
        # 1. Generate question embedding
        question_embedding = self.embedder.generate_embedding(question)

        # 2. Search for relevant documents
        results = self.search.search(
            search_text=question,
            vector_queries=[VectorizedQuery(
                vector=question_embedding,
                k_nearest_neighbors=5,
                fields="embedding"
            )]
        )

        # 3. Build context from results
        context = "\n\n".join([r["content"] for r in results])

        # 4. Generate answer using GPT
        response = self.openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Answer based on the context."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
            ]
        )

        return response.choices[0].message.content
```

## Performance Enhancements

### 1. Parallel Processing

Process multiple batches in parallel:

```python
from concurrent.futures import ThreadPoolExecutor

def parallel_embed(texts, batch_size=100):
    with ThreadPoolExecutor(max_workers=5) as executor:
        batches = [texts[i:i+batch_size] for i in range(0, len(texts), batch_size)]
        results = executor.map(embedder.generate_embeddings_batch, batches)
        return [emb for batch in results for emb in batch]
```

### 2. Streaming Processing

Process large datasets without loading all into memory:

```python
def stream_process(table_name, chunk_size=1000):
    offset = 0
    while True:
        # Extract chunk
        df = extractor.extract_data(
            table_name=table_name,
            limit=chunk_size,
            offset=offset
        )

        if df.empty:
            break

        # Process chunk
        df = embedder.embed_dataframe(df)
        indexer.index_dataframe(df)

        offset += chunk_size
```

## Security Enhancements

### 1. Azure Managed Identity

Replace API keys with managed identities:

```python
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()

search_client = SearchClient(
    endpoint=search_endpoint,
    index_name=index_name,
    credential=credential  # Use managed identity
)
```

### 2. Key Vault Integration

Store secrets in Azure Key Vault:

```python
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://myvault.vault.azure.net/", credential=credential)

snowflake_password = client.get_secret("snowflake-password").value
```

## Next Steps

Choose enhancements based on your specific needs:

1. **Short-term**: Containerization for easier deployment
2. **Medium-term**: Event-based processing for real-time updates
3. **Long-term**: Full RAG implementation with conversational AI

For implementation assistance, refer to the respective documentation for each Azure service.
