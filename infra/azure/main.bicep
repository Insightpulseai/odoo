// InsightPulse AI — Azure ERP SaaS Platform Infrastructure
// Main deployment template

targetScope = 'resourceGroup'

@description('Environment name')
@allowed(['dev', 'staging', 'prod'])
param environment string = 'dev'

@description('Azure region for resources')
param location string = resourceGroup().location

@description('Base name for resources')
param baseName string = 'ipai'

@description('Databricks workspace pricing tier')
@allowed(['standard', 'premium'])
param databricksTier string = 'premium'

@description('PostgreSQL admin password')
@secure()
param postgresAdminPassword string

@description('Deploy Databricks (optional data/AI plane)')
param deployDatabricks bool = false

@description('Custom domain for Front Door')
param customDomain string = 'erp.insightpulseai.com'

// Variables
var resourcePrefix = '${baseName}-${environment}'
var tags = {
  Environment: environment
  Project: 'InsightPulse AI ERP SaaS'
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

// Data/AI plane — optional, not in delivery path
module databricks 'modules/databricks.bicep' = if (deployDatabricks) {
  name: 'databricksDeployment'
  params: {
    workspaceName: '${resourcePrefix}-dbw'
    location: location
    pricingTier: databricksTier
    tags: tags
  }
}

// Azure Container Registry
module containerRegistry 'modules/acr.bicep' = {
  name: 'acrDeployment'
  params: {
    acrName: replace('${resourcePrefix}acr', '-', '')
    location: location
    tags: tags
  }
}

// PostgreSQL Flexible Server
module postgresql 'modules/postgresql.bicep' = {
  name: 'postgresqlDeployment'
  params: {
    serverName: '${resourcePrefix}-pg'
    location: location
    tags: tags
    administratorPassword: postgresAdminPassword
    keyVaultName: keyVault.outputs.keyVaultName
  }
}

// Container Apps Environment + Odoo runtime
module containerApp 'modules/containerapp.bicep' = {
  name: 'containerAppDeployment'
  params: {
    environmentName: '${resourcePrefix}-cae'
    appName: '${resourcePrefix}-odoo'
    location: location
    tags: tags
    acrLoginServer: containerRegistry.outputs.acrLoginServer
    keyVaultName: keyVault.outputs.keyVaultName
    postgresHost: postgresql.outputs.serverFqdn
  }
}

// Front Door + WAF
module frontDoor 'modules/frontdoor.bicep' = {
  name: 'frontDoorDeployment'
  params: {
    frontDoorName: '${resourcePrefix}-fd'
    location: 'global'
    tags: tags
    backendAddress: containerApp.outputs.appFqdn
    customDomain: customDomain
  }
}

// Outputs
output keyVaultName string = keyVault.outputs.keyVaultName
output keyVaultUri string = keyVault.outputs.keyVaultUri
output storageAccountName string = storage.outputs.storageAccountName
output databricksWorkspaceUrl string = deployDatabricks ? databricks.outputs.workspaceUrl : 'not-deployed'
output databricksWorkspaceId string = deployDatabricks ? databricks.outputs.workspaceId : 'not-deployed'
output acrLoginServer string = containerRegistry.outputs.acrLoginServer
output acrName string = containerRegistry.outputs.acrName
output postgresServerFqdn string = postgresql.outputs.serverFqdn
output postgresDatabaseName string = postgresql.outputs.databaseName
output containerAppFqdn string = containerApp.outputs.appFqdn
output containerAppId string = containerApp.outputs.appId
output containerEnvironmentId string = containerApp.outputs.environmentId
output frontDoorFqdn string = frontDoor.outputs.frontDoorFqdn
output frontDoorId string = frontDoor.outputs.frontDoorId
output wafPolicyId string = frontDoor.outputs.wafPolicyId
