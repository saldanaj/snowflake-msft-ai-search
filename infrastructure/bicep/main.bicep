targetScope = 'resourceGroup'

@description('Base name for all resources')
param baseName string

@description('Location for all resources')
param location string = resourceGroup().location

@description('Environment name (e.g., dev, prod)')
@allowed([
  'dev'
  'test'
  'prod'
])
param environment string = 'dev'

@description('Deploy Event Hub (for future event-based triggering)')
param deployEventHub bool = false

@description('Tags to apply to all resources')
param tags object = {
  Environment: environment
  Project: 'Snowflake-Azure-AI-Search'
}

var searchServiceName = '${baseName}-search-${environment}'
var openAIServiceName = '${baseName}-openai-${environment}'
var storageAccountName = replace('${baseName}storage${environment}', '-', '')
var eventHubNamespaceName = '${baseName}-eventhub-${environment}'

// Deploy Azure AI Search
module searchService './modules/ai-search.bicep' = {
  name: 'searchServiceDeployment'
  params: {
    searchServiceName: searchServiceName
    location: location
    sku: 'basic'
    tags: tags
  }
}

// Deploy Azure OpenAI
module openAIService './modules/openai.bicep' = {
  name: 'openAIServiceDeployment'
  params: {
    openAIServiceName: openAIServiceName
    location: location
    embeddingDeploymentName: 'text-embedding-ada-002'
    embeddingModelName: 'text-embedding-ada-002'
    embeddingModelVersion: '2'
    embeddingCapacity: 120
    tags: tags
  }
}

// Deploy Storage Account
module storage './modules/storage.bicep' = {
  name: 'storageDeployment'
  params: {
    storageAccountName: storageAccountName
    location: location
    sku: 'Standard_LRS'
    tags: tags
  }
}

// Deploy Event Hub (optional, for future use)
module eventHub './modules/eventhub.bicep' = if (deployEventHub) {
  name: 'eventHubDeployment'
  params: {
    eventHubNamespaceName: eventHubNamespaceName
    eventHubName: 'snowflake-events'
    location: location
    sku: 'Standard'
    throughputUnits: 1
    tags: tags
  }
}

@description('Azure AI Search service endpoint')
output searchServiceEndpoint string = searchService.outputs.searchServiceEndpoint

@description('Azure AI Search service admin key')
@secure()
output searchServiceAdminKey string = searchService.outputs.searchServiceAdminKey

@description('Azure OpenAI service endpoint')
output openAIServiceEndpoint string = openAIService.outputs.openAIServiceEndpoint

@description('Azure OpenAI service key')
@secure()
output openAIServiceKey string = openAIService.outputs.openAIServiceKey

@description('Azure OpenAI embedding deployment name')
output embeddingDeploymentName string = openAIService.outputs.embeddingDeploymentName

@description('Storage account connection string')
@secure()
output storageConnectionString string = storage.outputs.connectionString

@description('Event Hub connection string (if deployed)')
@secure()
output eventHubConnectionString string = deployEventHub ? eventHub.outputs.eventHubConnectionString : ''
