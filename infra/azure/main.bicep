// InsightPulse AI — Azure Infrastructure
// Main deployment template
//
// Modules: Key Vault, Storage, Databricks, App Service, Front Door, APIM

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

@description('App Service plan SKU')
param appServiceSku string = 'B1'

@description('Enable Azure Front Door deployment')
param enableFrontDoor bool = false

@description('Front Door origin groups configuration')
param frontDoorOriginGroups array = []

@description('Front Door custom domains')
param frontDoorCustomDomains array = []

@description('Front Door routing rules')
param frontDoorRoutes array = []

@description('Enable Azure API Management deployment')
param enableApim bool = false

@description('APIM publisher email')
param apimPublisherEmail string = ''

@description('Container Apps Environment FQDN for APIM backends')
param containerAppsEnvironmentFqdn string = ''

// Variables
var resourcePrefix = '${baseName}-${environment}'
var tags = {
  Environment: environment
  Project: 'InsightPulse AI'
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

// Azure Front Door Premium (edge layer, WAF, caching)
module frontDoor 'modules/front-door.bicep' = if (enableFrontDoor) {
  name: 'frontDoorDeployment'
  params: {
    profileName: '${resourcePrefix}-fd'
    wafPolicyName: '${replace(resourcePrefix, '-', '')}WafPolicy'
    tags: tags
    originGroups: frontDoorOriginGroups
    customDomains: frontDoorCustomDomains
    routes: frontDoorRoutes
    enableWaf: true
  }
}

// Azure API Management (Foundry-facing API gateway)
module apim 'modules/apim.bicep' = if (enableApim) {
  name: 'apimDeployment'
  params: {
    apimName: '${resourcePrefix}-apim'
    location: location
    tags: tags
    publisherEmail: apimPublisherEmail
    publisherName: 'InsightPulse AI'
    containerAppsEnvironmentFqdn: containerAppsEnvironmentFqdn
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
output frontDoorEndpoint string = enableFrontDoor ? frontDoor.outputs.endpointHostName : 'not-deployed'
output apimGatewayUrl string = enableApim ? apim.outputs.apimGatewayUrl : 'not-deployed'
