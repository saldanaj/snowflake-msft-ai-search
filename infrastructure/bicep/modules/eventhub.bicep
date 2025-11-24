@description('Name of the Event Hub namespace')
param eventHubNamespaceName string

@description('Name of the Event Hub')
param eventHubName string = 'snowflake-events'

@description('Location for the Event Hub')
param location string = resourceGroup().location

@description('SKU for the Event Hub namespace')
@allowed([
  'Basic'
  'Standard'
  'Premium'
])
param sku string = 'Standard'

@description('Throughput units (only for Standard and Premium SKUs)')
@minValue(1)
@maxValue(20)
param throughputUnits int = 1

@description('Tags to apply to the resource')
param tags object = {}

resource eventHubNamespace 'Microsoft.EventHub/namespaces@2023-01-01-preview' = {
  name: eventHubNamespaceName
  location: location
  tags: tags
  sku: {
    name: sku
    tier: sku
    capacity: throughputUnits
  }
  properties: {
    isAutoInflateEnabled: false
  }
}

resource eventHub 'Microsoft.EventHub/namespaces/eventhubs@2023-01-01-preview' = {
  parent: eventHubNamespace
  name: eventHubName
  properties: {
    messageRetentionInDays: 7
    partitionCount: 4
  }
}

resource consumerGroup 'Microsoft.EventHub/namespaces/eventhubs/consumergroups@2023-01-01-preview' = {
  parent: eventHub
  name: 'pipeline-consumer'
  properties: {}
}

resource authorizationRule 'Microsoft.EventHub/namespaces/authorizationRules@2023-01-01-preview' = {
  parent: eventHubNamespace
  name: 'RootManageSharedAccessKey'
  properties: {
    rights: [
      'Listen'
      'Manage'
      'Send'
    ]
  }
}

@description('The resource ID of the Event Hub namespace')
output eventHubNamespaceId string = eventHubNamespace.id

@description('The name of the Event Hub namespace')
output eventHubNamespaceName string = eventHubNamespace.name

@description('The name of the Event Hub')
output eventHubName string = eventHub.name

@description('The connection string for the Event Hub namespace')
output eventHubConnectionString string = listKeys(authorizationRule.id, authorizationRule.apiVersion).primaryConnectionString
