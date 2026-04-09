// InsightPulse AI — Azure Infrastructure
// Main deployment template
//
// Modules: Key Vault, Storage, Databricks, App Service, Front Door, APIM, Odoo ACA,
//          Log Analytics, Application Insights

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

@description('Enable Log Analytics workspace')
param enableLogAnalytics bool = true

@description('Enable PIM governance (RBAC foundation + custom roles)')
param enablePimGovernance bool = false

@description('Entra ID group object ID for platform admins')
param platformAdminGroupId string = ''

@description('Entra ID group object ID for Odoo operators')
param odooOperatorGroupId string = ''

@description('Enable Azure Policy tag governance')
param enableTagGovernance bool = false

@description('Policy enforcement mode: Default (deny) or DoNotEnforce (audit)')
@allowed(['Default', 'DoNotEnforce'])
param policyEnforcementMode string = 'DoNotEnforce'

@description('Log Analytics retention in days')
@minValue(30)
@maxValue(730)
param logAnalyticsRetentionDays int = 30

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

// Log Analytics Workspace (central observability)
module logAnalytics 'modules/log-analytics.bicep' = if (enableLogAnalytics) {
  name: 'logAnalyticsDeployment'
  params: {
    workspaceName: '${resourcePrefix}-law'
    location: location
    retentionInDays: logAnalyticsRetentionDays
    tags: tags
  }
}

// Application Insights (APM telemetry)
module appInsights 'modules/app-insights.bicep' = if (enableLogAnalytics) {
  name: 'appInsightsDeployment'
  params: {
    appInsightsName: '${resourcePrefix}-ai'
    location: location
    workspaceId: logAnalytics.outputs.workspaceId
    tags: tags
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

// PIM Governance (RBAC foundation + custom Odoo Operator role)
module pimGovernance 'modules/pim-governance.bicep' = if (enablePimGovernance && !empty(platformAdminGroupId)) {
  name: 'pimGovernanceDeployment'
  params: {
    platformAdminGroupId: platformAdminGroupId
    odooOperatorGroupId: odooOperatorGroupId
    keyVaultName: keyVault.outputs.keyVaultName
    environment: environment
    tags: tags
  }
}

// Azure Policy — Tag Governance (audit mode by default)
module tagGovernance 'modules/policy-tag-governance.bicep' = if (enableTagGovernance) {
  name: 'tagGovernanceDeployment'
  params: {
    environment: environment
    enforcementMode: policyEnforcementMode
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
output logAnalyticsWorkspaceId string = enableLogAnalytics ? logAnalytics.outputs.workspaceId : 'not-deployed'
output logAnalyticsCustomerId string = enableLogAnalytics ? logAnalytics.outputs.customerId : 'not-deployed'
output appInsightsConnectionString string = enableLogAnalytics ? appInsights.outputs.connectionString : 'not-deployed'
output appInsightsInstrumentationKey string = enableLogAnalytics ? appInsights.outputs.instrumentationKey : 'not-deployed'
output pimOdooOperatorRole string = enablePimGovernance && !empty(platformAdminGroupId) ? pimGovernance.outputs.odooOperatorRoleName : 'not-deployed'
output tagGovernanceEnvAssignment string = enableTagGovernance ? tagGovernance.outputs.environmentTagAssignment : 'not-deployed'
output tagGovernanceEnforcementMode string = enableTagGovernance ? tagGovernance.outputs.enforcementMode : 'not-deployed'
