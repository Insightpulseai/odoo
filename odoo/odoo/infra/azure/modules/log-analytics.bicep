// Azure Log Analytics Workspace module
// Central observability sink for all platform resources

@description('Name of the Log Analytics workspace')
param workspaceName string

@description('Azure region')
param location string

@description('Resource tags')
param tags object

@description('Retention period in days')
@minValue(30)
@maxValue(730)
param retentionInDays int = 90

@description('SKU name')
@allowed(['PerGB2018', 'Free', 'Standalone'])
param skuName string = 'PerGB2018'

resource workspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: workspaceName
  location: location
  tags: tags
  properties: {
    sku: {
      name: skuName
    }
    retentionInDays: retentionInDays
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

output workspaceId string = workspace.id
output workspaceName string = workspace.name
output customerId string = workspace.properties.customerId
