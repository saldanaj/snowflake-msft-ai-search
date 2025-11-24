# Deploy Azure infrastructure using Bicep
# This script deploys Azure AI Search, Azure OpenAI, and supporting resources

param(
    [string]$ResourceGroupName = "rg-snowflake-ai-demo",
    [string]$Location = "eastus",
    [string]$Environment = "dev"
)

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Azure Infrastructure Deployment" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Resource Group: $ResourceGroupName"
Write-Host "  Location: $Location"
Write-Host "  Environment: $Environment"
Write-Host ""

# Check if Azure CLI is installed
try {
    $azVersion = az version 2>&1 | Out-Null
} catch {
    Write-Host "Error: Azure CLI is not installed." -ForegroundColor Red
    Write-Host "Please install it from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
}

# Check if logged in
Write-Host "Checking Azure CLI login status..." -ForegroundColor Yellow
try {
    $account = az account show 2>&1 | ConvertFrom-Json
    $subscriptionId = $account.id
    $subscriptionName = $account.name
    Write-Host "Using subscription: $subscriptionName ($subscriptionId)" -ForegroundColor Green
} catch {
    Write-Host "Not logged in to Azure. Please log in..." -ForegroundColor Yellow
    az login
    $account = az account show | ConvertFrom-Json
}

Write-Host ""

# Create resource group
Write-Host "Creating resource group..." -ForegroundColor Yellow
az group create `
    --name $ResourceGroupName `
    --location $Location `
    --output table

Write-Host ""

# Deploy infrastructure
Write-Host "Deploying infrastructure using Bicep..." -ForegroundColor Yellow
$deploymentName = "snowflake-ai-deployment-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

az deployment group create `
    --name $deploymentName `
    --resource-group $ResourceGroupName `
    --template-file infrastructure/bicep/main.bicep `
    --parameters "infrastructure/bicep/parameters/$Environment.bicepparam" `
    --output table

Write-Host ""

# Get deployment outputs
Write-Host "Retrieving deployment outputs..." -ForegroundColor Yellow
$searchEndpoint = az deployment group show `
    --name $deploymentName `
    --resource-group $ResourceGroupName `
    --query properties.outputs.searchServiceEndpoint.value -o tsv

$openaiEndpoint = az deployment group show `
    --name $deploymentName `
    --resource-group $ResourceGroupName `
    --query properties.outputs.openAIServiceEndpoint.value -o tsv

$embeddingDeployment = az deployment group show `
    --name $deploymentName `
    --resource-group $ResourceGroupName `
    --query properties.outputs.embeddingDeploymentName.value -o tsv

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Deployment completed successfully!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Deployed resources:" -ForegroundColor Yellow
Write-Host "  Azure AI Search Endpoint: $searchEndpoint"
Write-Host "  Azure OpenAI Endpoint: $openaiEndpoint"
Write-Host "  Embedding Deployment: $embeddingDeployment"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Retrieve the API keys from Azure Portal or using Azure CLI"
Write-Host "2. Update config\.env with the endpoints and keys"
Write-Host "3. Run the pipeline: python scripts\run_pipeline.py"
Write-Host ""
Write-Host "To retrieve API keys:" -ForegroundColor Yellow
Write-Host "  Search API Key:"
Write-Host "    az search admin-key show --resource-group $ResourceGroupName --service-name [search-service-name] --query primaryKey -o tsv"
Write-Host ""
Write-Host "  OpenAI API Key:"
Write-Host "    az cognitiveservices account keys list --resource-group $ResourceGroupName --name [openai-service-name] --query key1 -o tsv"
Write-Host ""
