#!/bin/bash

# Deploy Azure infrastructure using Bicep
# This script deploys Azure AI Search, Azure OpenAI, and supporting resources

set -e

echo "=========================================="
echo "Azure Infrastructure Deployment"
echo "=========================================="
echo ""

# Configuration
RESOURCE_GROUP_NAME="rg-snowflake-ai-demo"
LOCATION="eastus"
ENVIRONMENT="dev"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --resource-group)
            RESOURCE_GROUP_NAME="$2"
            shift 2
            ;;
        --location)
            LOCATION="$2"
            shift 2
            ;;
        --environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --resource-group NAME   Resource group name (default: rg-snowflake-ai-demo)"
            echo "  --location LOCATION     Azure region (default: eastus)"
            echo "  --environment ENV       Environment (dev|test|prod, default: dev)"
            echo "  --help                  Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo "Configuration:"
echo "  Resource Group: $RESOURCE_GROUP_NAME"
echo "  Location: $LOCATION"
echo "  Environment: $ENVIRONMENT"
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "Error: Azure CLI is not installed."
    echo "Please install it from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in
echo "Checking Azure CLI login status..."
if ! az account show &> /dev/null; then
    echo "Not logged in to Azure. Please log in..."
    az login
fi

SUBSCRIPTION_ID=$(az account show --query id -o tsv)
SUBSCRIPTION_NAME=$(az account show --query name -o tsv)
echo "Using subscription: $SUBSCRIPTION_NAME ($SUBSCRIPTION_ID)"
echo ""

# Create resource group
echo "Creating resource group..."
az group create \
    --name $RESOURCE_GROUP_NAME \
    --location $LOCATION \
    --output table

echo ""

# Deploy infrastructure
echo "Deploying infrastructure using Bicep..."
DEPLOYMENT_NAME="snowflake-ai-deployment-$(date +%Y%m%d-%H%M%S)"

az deployment group create \
    --name $DEPLOYMENT_NAME \
    --resource-group $RESOURCE_GROUP_NAME \
    --template-file infrastructure/bicep/main.bicep \
    --parameters infrastructure/bicep/parameters/${ENVIRONMENT}.bicepparam \
    --output table

echo ""

# Get deployment outputs
echo "Retrieving deployment outputs..."
SEARCH_ENDPOINT=$(az deployment group show \
    --name $DEPLOYMENT_NAME \
    --resource-group $RESOURCE_GROUP_NAME \
    --query properties.outputs.searchServiceEndpoint.value -o tsv)

OPENAI_ENDPOINT=$(az deployment group show \
    --name $DEPLOYMENT_NAME \
    --resource-group $RESOURCE_GROUP_NAME \
    --query properties.outputs.openAIServiceEndpoint.value -o tsv)

EMBEDDING_DEPLOYMENT=$(az deployment group show \
    --name $DEPLOYMENT_NAME \
    --resource-group $RESOURCE_GROUP_NAME \
    --query properties.outputs.embeddingDeploymentName.value -o tsv)

echo ""
echo "=========================================="
echo "Deployment completed successfully!"
echo "=========================================="
echo ""
echo "Deployed resources:"
echo "  Azure AI Search Endpoint: $SEARCH_ENDPOINT"
echo "  Azure OpenAI Endpoint: $OPENAI_ENDPOINT"
echo "  Embedding Deployment: $EMBEDDING_DEPLOYMENT"
echo ""
echo "Next steps:"
echo "1. Retrieve the API keys from Azure Portal or using Azure CLI"
echo "2. Update config/.env with the endpoints and keys"
echo "3. Run the pipeline: python scripts/run_pipeline.py"
echo ""
echo "To retrieve API keys:"
echo "  Search API Key:"
echo "    az search admin-key show --resource-group $RESOURCE_GROUP_NAME --service-name [search-service-name] --query primaryKey -o tsv"
echo ""
echo "  OpenAI API Key:"
echo "    az cognitiveservices account keys list --resource-group $RESOURCE_GROUP_NAME --name [openai-service-name] --query key1 -o tsv"
echo ""
