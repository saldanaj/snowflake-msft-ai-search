@description('Name of the Azure OpenAI service')
param openAIServiceName string

@description('Location for the Azure OpenAI service')
param location string = resourceGroup().location

@description('SKU for the Azure OpenAI service')
@allowed([
  'S0'
])
param sku string = 'S0'

@description('Name of the embedding model deployment')
param embeddingDeploymentName string = 'text-embedding-ada-002'

@description('Embedding model name')
param embeddingModelName string = 'text-embedding-ada-002'

@description('Embedding model version')
param embeddingModelVersion string = '2'

@description('Embedding deployment capacity (in thousands of tokens per minute)')
param embeddingCapacity int = 120

@description('Tags to apply to the resource')
param tags object = {}

resource openAIService 'Microsoft.CognitiveServices/accounts@2023-10-01-preview' = {
  name: openAIServiceName
  location: location
  tags: tags
  kind: 'OpenAI'
  sku: {
    name: sku
  }
  properties: {
    customSubDomainName: openAIServiceName
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
    }
  }
}

resource embeddingDeployment 'Microsoft.CognitiveServices/accounts/deployments@2023-10-01-preview' = {
  parent: openAIService
  name: embeddingDeploymentName
  sku: {
    name: 'Standard'
    capacity: embeddingCapacity
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: embeddingModelName
      version: embeddingModelVersion
    }
  }
}

@description('The resource ID of the Azure OpenAI service')
output openAIServiceId string = openAIService.id

@description('The name of the Azure OpenAI service')
output openAIServiceName string = openAIService.name

@description('The endpoint of the Azure OpenAI service')
output openAIServiceEndpoint string = openAIService.properties.endpoint

@description('The primary API key for the Azure OpenAI service')
output openAIServiceKey string = openAIService.listKeys().key1

@description('The name of the embedding deployment')
output embeddingDeploymentName string = embeddingDeployment.name
