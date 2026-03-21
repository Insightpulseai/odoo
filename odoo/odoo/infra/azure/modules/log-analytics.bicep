// Log Analytics workspace for centralized logging
// All ACA, Key Vault, Front Door, and PostgreSQL diagnostics flow here

@description('Log Analytics workspace name')
param workspaceName string

@description('Azure region')
param location string

@description('Resource tags')
param tags object

@description('Data retention in days (30 = free tier)')
param retentionInDays int = 30

@description('Pricing tier for the workspace')
param skuName string = 'PerGB2018'

resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: workspaceName
  location: location
  tags: tags
  properties: {
    sku: {
      name: skuName
    }
    retentionInDays: retentionInDays
  }
}

output workspaceId string = workspace.id
output workspaceName string = workspace.name
output customerId string = workspace.properties.customerId
