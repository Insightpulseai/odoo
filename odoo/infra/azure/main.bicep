// InsightPulse AI — Azure Infrastructure
// Main deployment template
//
// Modules: Key Vault, Storage, Databricks, App Service, Front Door, APIM, Odoo ACA

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

@description('Enable Odoo ACA services (web + worker + cron)')
param enableOdooServices bool = false

@description('Odoo ACA Environment name')
param odooAcaEnvironmentName string = ''

@description('Container registry server for Odoo images')
param odooContainerRegistryServer string = ''

@description('Managed identity resource ID for Odoo ACA')
param odooManagedIdentityResourceId string = ''

@description('Key Vault name for Odoo secrets')
param odooKeyVaultName string = ''

@description('PostgreSQL host for Odoo')
param odooPostgresHost string = ''

@description('PostgreSQL database for Odoo')
param odooPostgresDb string = 'odoo'

@description('Odoo container image tag')
param odooImageTag string = 'latest'

@description('CPU for odoo-web')
param odooCpuWeb string = '1.0'

@description('Memory for odoo-web')
param odooMemoryWeb string = '2Gi'

@description('Min replicas for odoo-web')
param odooMinReplicasWeb int = 1

@description('Max replicas for odoo-web')
param odooMaxReplicasWeb int = 3

@description('CPU for odoo-worker')
param odooCpuWorker string = '0.5'

@description('Memory for odoo-worker')
param odooMemoryWorker string = '1Gi'

@description('Min replicas for odoo-worker')
param odooMinReplicasWorker int = 1

@description('Max replicas for odoo-worker')
param odooMaxReplicasWorker int = 2

@description('CPU for odoo-cron')
param odooCpuCron string = '0.5'

@description('Memory for odoo-cron')
param odooMemoryCron string = '1Gi'

@description('Enable VNet deployment')
param enableVnet bool = false

@description('VNet address prefix')
param vnetAddressPrefix string = '10.0.0.0/16'

@description('Enable Log Analytics deployment')
param enableLogAnalytics bool = false

@description('Log Analytics retention in days')
param logAnalyticsRetentionDays int = 90

@description('Enable Azure Files for Odoo filestore')
param enableAzureFiles bool = false

@description('Azure Files share quota in GB')
param azureFilesQuotaGb int = 50

// Variables
var resourcePrefix = '${baseName}-${environment}'
var tags = {
  Environment: environment
  Project: 'InsightPulse AI'
  ManagedBy: 'Bicep'
}

// Virtual Network
module vnet 'modules/vnet.bicep' = if (enableVnet) {
  name: 'vnetDeployment'
  params: {
    vnetName: '${resourcePrefix}-vnet'
    location: location
    addressPrefix: vnetAddressPrefix
    tags: tags
  }
}

// Log Analytics Workspace
module logAnalytics 'modules/log-analytics.bicep' = if (enableLogAnalytics) {
  name: 'logAnalyticsDeployment'
  params: {
    workspaceName: '${resourcePrefix}-law'
    location: location
    retentionInDays: logAnalyticsRetentionDays
    tags: tags
  }
}

// Azure Files for Odoo filestore
module azureFiles 'modules/azure-files.bicep' = if (enableAzureFiles) {
  name: 'azureFilesDeployment'
  params: {
    storageAccountName: replace('${resourcePrefix}files', '-', '')
    location: location
    shareQuotaGb: azureFilesQuotaGb
    tags: tags
  }
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

// Odoo ACA Runtime (web + worker + cron)
module odooServices 'modules/aca-odoo-services.bicep' = if (enableOdooServices) {
  name: 'odooServicesDeployment'
  params: {
    environmentName: odooAcaEnvironmentName
    containerRegistryServer: odooContainerRegistryServer
    managedIdentityResourceId: odooManagedIdentityResourceId
    keyVaultName: !empty(odooKeyVaultName) ? odooKeyVaultName : keyVault.outputs.keyVaultName
    postgresHost: odooPostgresHost
    postgresDb: odooPostgresDb
    imageTag: odooImageTag
    cpuWeb: odooCpuWeb
    memoryWeb: odooMemoryWeb
    minReplicasWeb: odooMinReplicasWeb
    maxReplicasWeb: odooMaxReplicasWeb
    cpuWorker: odooCpuWorker
    memoryWorker: odooMemoryWorker
    minReplicasWorker: odooMinReplicasWorker
    maxReplicasWorker: odooMaxReplicasWorker
    cpuCron: odooCpuCron
    memoryCron: odooMemoryCron
    tags: tags
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
output odooWebFqdn string = enableOdooServices ? odooServices.outputs.odooWebFqdn : 'not-deployed'
output odooWebName string = enableOdooServices ? odooServices.outputs.odooWebName : 'not-deployed'
output odooWorkerName string = enableOdooServices ? odooServices.outputs.odooWorkerName : 'not-deployed'
output odooCronName string = enableOdooServices ? odooServices.outputs.odooCronName : 'not-deployed'
output vnetName string = enableVnet ? vnet.outputs.vnetName : 'not-deployed'
output logAnalyticsWorkspaceId string = enableLogAnalytics ? logAnalytics.outputs.workspaceId : 'not-deployed'
output azureFilesAccountName string = enableAzureFiles ? azureFiles.outputs.storageAccountName : 'not-deployed'
