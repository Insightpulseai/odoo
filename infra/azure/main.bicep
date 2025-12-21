// Notion x Finance PPM Control Room - Azure Infrastructure
// Main deployment template

targetScope = 'resourceGroup'

@description('Environment name')
@allowed(['dev', 'staging', 'prod'])
param environment string = 'dev'

@description('Azure region for resources')
param location string = resourceGroup().location

@description('Base name for resources')
param baseName string = 'notion-ppm'

@description('Databricks workspace pricing tier')
@allowed(['standard', 'premium'])
param databricksTier string = 'premium'

@description('App Service plan SKU')
param appServiceSku string = 'B1'

// Variables
var resourcePrefix = '${baseName}-${environment}'
var tags = {
  Environment: environment
  Project: 'Notion Finance PPM'
  ManagedBy: 'Bicep'
}

// Key Vault for secrets
module keyVault 'modules/keyvault.bicep' = {
  name: 'keyVaultDeployment'
  params: {
    keyVaultName: '${resourcePrefix}-kv'
    location: location
    tags: tags
  }
}

// Storage Account for data lake
module storage 'modules/storage.bicep' = {
  name: 'storageDeployment'
  params: {
    storageAccountName: replace('${resourcePrefix}data', '-', '')
    location: location
    tags: tags
  }
}

// Databricks Workspace
module databricks 'modules/databricks.bicep' = {
  name: 'databricksDeployment'
  params: {
    workspaceName: '${resourcePrefix}-dbw'
    location: location
    pricingTier: databricksTier
    tags: tags
  }
}

// App Service for Control Room
module appService 'modules/appservice.bicep' = {
  name: 'appServiceDeployment'
  params: {
    appName: '${resourcePrefix}-app'
    location: location
    sku: appServiceSku
    tags: tags
    keyVaultName: keyVault.outputs.keyVaultName
  }
}

// Outputs
output keyVaultName string = keyVault.outputs.keyVaultName
output keyVaultUri string = keyVault.outputs.keyVaultUri
output storageAccountName string = storage.outputs.storageAccountName
output databricksWorkspaceUrl string = databricks.outputs.workspaceUrl
output databricksWorkspaceId string = databricks.outputs.workspaceId
output appServiceUrl string = appService.outputs.appUrl
output appServiceName string = appService.outputs.appName
