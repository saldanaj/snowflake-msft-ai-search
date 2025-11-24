# Infrastructure Deployment

This guide explains how to deploy the Azure infrastructure required for the demo.

## Overview

The demo requires the following Azure resources:
- **Azure OpenAI**: For generating text embeddings
- **Azure AI Search**: For storing and searching embedded data
- **Azure Storage Account**: For logs and checkpoints (optional)
- **Azure Event Hub**: For event-based triggering (optional, future use)

## Prerequisites

- Azure CLI installed and configured
- Azure subscription with:
  - Azure OpenAI service access (requires approval)
  - Contributor permissions on the subscription or resource group
- Completed [Setup Guide](01-setup.md)

## Deployment Options

### Option 1: Automated Deployment (Recommended)

Use the provided deployment scripts to automatically provision all resources.

#### Windows

```powershell
.\scripts\deploy_infrastructure.ps1 `
    -ResourceGroupName "rg-snowflake-ai-demo" `
    -Location "eastus" `
    -Environment "dev"
```

#### Linux/Mac

```bash
chmod +x scripts/deploy_infrastructure.sh
./scripts/deploy_infrastructure.sh \
    --resource-group "rg-snowflake-ai-demo" \
    --location "eastus" \
    --environment "dev"
```

### Option 2: Manual Deployment

1. Login to Azure CLI:

```bash
az login
```

2. Set your subscription:

```bash
az account set --subscription "your-subscription-id"
```

3. Create a resource group:

```bash
az group create \
    --name rg-snowflake-ai-demo \
    --location eastus
```

4. Deploy the Bicep template:

```bash
az deployment group create \
    --name snowflake-ai-deployment \
    --resource-group rg-snowflake-ai-demo \
    --template-file infrastructure/bicep/main.bicep \
    --parameters infrastructure/bicep/parameters/dev.bicepparam
```

## Retrieve Resource Credentials

After deployment, you need to retrieve the API keys and endpoints.

### Azure AI Search

Get the search service endpoint and admin key:

```bash
# Get endpoint
az search service show \
    --name <search-service-name> \
    --resource-group rg-snowflake-ai-demo \
    --query "hostName" -o tsv

# Get admin key
az search admin-key show \
    --service-name <search-service-name> \
    --resource-group rg-snowflake-ai-demo \
    --query "primaryKey" -o tsv
```

### Azure OpenAI

Get the OpenAI endpoint and API key:

```bash
# Get endpoint
az cognitiveservices account show \
    --name <openai-service-name> \
    --resource-group rg-snowflake-ai-demo \
    --query "properties.endpoint" -o tsv

# Get API key
az cognitiveservices account keys list \
    --name <openai-service-name> \
    --resource-group rg-snowflake-ai-demo \
    --query "key1" -o tsv
```

## Update Configuration

Update `config/.env` with the deployed resource information:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-openai-service.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_API_VERSION=2024-02-01

# Azure AI Search Configuration
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_API_KEY=your_search_api_key_here
AZURE_SEARCH_INDEX_NAME=snowflake-data-index
```

## Verify Deployment

### Test Azure OpenAI Connection

```python
# test_openai.py
from src.utils.config import Config
from src.embeddings.azure_openai_embedder import AzureOpenAIEmbedder

config = Config()
embedder = AzureOpenAIEmbedder(config)

# Generate a test embedding
embedding = embedder.generate_embedding("This is a test sentence.")
print(f"Successfully generated embedding with {len(embedding)} dimensions")
```

### Test Azure AI Search Connection

```python
# test_search.py
from src.utils.config import Config
from src.indexers.azure_search_indexer import AzureSearchIndexer

config = Config()
indexer = AzureSearchIndexer(config)

# Create the index
indexer.create_index()
print("Successfully created search index")
```

## Resource Costs

Estimated monthly costs for the demo (as of 2025):

| Resource | SKU | Estimated Cost |
|----------|-----|---------------|
| Azure AI Search | Basic | ~$75/month |
| Azure OpenAI | Standard (120K TPM) | Pay-per-use, ~$0.0001/1K tokens |
| Azure Storage | Standard LRS | ~$2/month |
| **Total** | | **~$77/month + usage** |

To minimize costs:
- Delete resources when not in use
- Use the `free` tier for AI Search during development (limited features)
- Monitor usage in Azure Cost Management

## Infrastructure Customization

### Modify SKUs

Edit `infrastructure/bicep/parameters/dev.bicepparam`:

```bicep
using '../main.bicep'

param baseName = 'snowflake-ai-demo'
param environment = 'dev'
param deployEventHub = false

// Add custom parameters
param searchServiceSku = 'free'  // Use free tier
param openAICapacity = 60        // Reduce capacity
```

### Deploy Event Hub for Event-Based Processing

Set `deployEventHub = true` in the parameters file to enable event-driven processing:

```bicep
param deployEventHub = true
```

## Cleanup

To delete all deployed resources:

```bash
az group delete \
    --name rg-snowflake-ai-demo \
    --yes \
    --no-wait
```

## Troubleshooting

### Azure OpenAI Access Denied

Azure OpenAI requires approval. Apply for access at:
https://aka.ms/oai/access

### Region Availability

Not all regions support Azure OpenAI. Recommended regions:
- East US
- West Europe
- South Central US

Check current availability:
https://azure.microsoft.com/en-us/explore/global-infrastructure/products-by-region/

### Deployment Failures

View deployment errors:

```bash
az deployment group show \
    --name snowflake-ai-deployment \
    --resource-group rg-snowflake-ai-demo \
    --query "properties.error"
```

## Next Steps

After deploying infrastructure, proceed to:
- [Running the Pipeline](03-running-pipeline.md)
