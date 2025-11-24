@description('Name of the Azure AI Search service')
param searchServiceName string

@description('Location for the Azure AI Search service')
param location string = resourceGroup().location

@description('SKU for the Azure AI Search service')
@allowed([
  'free'
  'basic'
  'standard'
  'standard2'
  'standard3'
  'storage_optimized_l1'
  'storage_optimized_l2'
])
param sku string = 'basic'

@description('Number of replicas')
@minValue(1)
@maxValue(12)
param replicaCount int = 1

@description('Number of partitions')
@allowed([
  1
  2
  3
  4
  6
  12
])
param partitionCount int = 1

@description('Tags to apply to the resource')
param tags object = {}

resource searchService 'Microsoft.Search/searchServices@2023-11-01' = {
  name: searchServiceName
  location: location
  tags: tags
  sku: {
    name: sku
  }
  properties: {
    replicaCount: replicaCount
    partitionCount: partitionCount
    hostingMode: 'default'
    publicNetworkAccess: 'enabled'
    networkRuleSet: {
      ipRules: []
    }
    disableLocalAuth: false
  }
}

@description('The resource ID of the Azure AI Search service')
output searchServiceId string = searchService.id

@description('The name of the Azure AI Search service')
output searchServiceName string = searchService.name

@description('The endpoint of the Azure AI Search service')
output searchServiceEndpoint string = 'https://${searchService.name}.search.windows.net'

@description('The primary admin key for the Azure AI Search service')
output searchServiceAdminKey string = searchService.listAdminKeys().primaryKey
