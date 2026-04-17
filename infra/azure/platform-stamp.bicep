// =============================================================================
// platform-stamp.bicep — Platform-wide deployment orchestrator (subscription scope)
// =============================================================================
// Deploys a complete IPAI platform stamp: 5 resource groups, 5 composition modules.
// Each resource gets `stampId` suffixed into its name for slot/multi-stamp safety.
//
// Deploy order (enforced by dependencies):
//   1. Monitoring  (Log Analytics, App Insights, Action Group)
//   2. Platform    (Key Vault, APIM)
//   3. Data        (PG Flex, ADLS Gen2, private endpoints)
//   4. Intelligence (Foundry ref, AI Search, Content Safety)
//   5. Runtime     (ACA env, all apps, CR, VNet, AFD)
//
// Run at subscription scope:
//   az deployment sub create \
//     --location southeastasia \
//     --template-file infra/azure/platform-stamp.bicep \
//     --parameters @infra/azure/parameters/dev.parameters.json
// =============================================================================

targetScope = 'subscription'

@description('Environment name (dev/staging/prod)')
@allowed(['dev', 'staging', 'prod'])
param environment string = 'dev'

@description('Stamp identifier (00 for the primary stamp; use 01/02 for additional isolated instances)')
param stampId string = '00'

@description('Primary Azure region')
param location string = 'southeastasia'

@description('Base name prefix for all resources')
param baseName string = 'ipai'

@description('Rollout group for this stamp')
@allowed(['canary', 'early-adopter', 'general-availability'])
param rolloutGroup string = 'general-availability'

@description('Foundry resource already deployed (reference-only)')
param foundryResourceName string = 'ipai-copilot-resource'

@description('Foundry resource group (separate from platform stamp)')
param foundryResourceGroup string = 'rg-data-intel-ph'

@description('Foundry project name')
param foundryProjectName string = 'ipai-copilot'

// -----------------------------------------------------------------------------
// Computed names — stampId embedded in every resource name
// -----------------------------------------------------------------------------

var rgPrefix    = 'rg-${baseName}-${environment}'
var rgMonitor   = '${rgPrefix}-monitoring'
var rgPlatform  = '${rgPrefix}-platform'
var rgData      = '${rgPrefix}-odoo-data'
var rgIntel     = '${rgPrefix}-intelligence'
var rgRuntime   = '${rgPrefix}-odoo-runtime'

var commonTags = {
  Environment:  environment
  StampId:      stampId
  RolloutGroup: rolloutGroup
  Platform:     'InsightPulseAI'
  ManagedBy:    'Bicep'
}

// -----------------------------------------------------------------------------
// 1. Resource groups
// -----------------------------------------------------------------------------

resource rgMonitoring 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: rgMonitor
  location: location
  tags: commonTags
}

resource rgPlat 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: rgPlatform
  location: location
  tags: commonTags
}

resource rgDataRG 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: rgData
  location: location
  tags: commonTags
}

resource rgIntelligence 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: rgIntel
  location: location
  tags: commonTags
}

resource rgRt 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: rgRuntime
  location: location
  tags: commonTags
}

// -----------------------------------------------------------------------------
// 2. Monitoring (deploys FIRST — all other modules reference its workspace id)
// -----------------------------------------------------------------------------

module monitoring 'modules/monitoring.bicep' = {
  scope: rgMonitoring
  name: 'monitoring-s${stampId}'
  params: {
    stampId: stampId
    environment: environment
    baseName: baseName
    location: location
    tags: commonTags
  }
}

// -----------------------------------------------------------------------------
// 3. Platform (Key Vault, APIM)
// -----------------------------------------------------------------------------

module platform 'modules/platform.bicep' = {
  scope: rgPlat
  name: 'platform-s${stampId}'
  params: {
    stampId: stampId
    environment: environment
    baseName: baseName
    location: location
    logAnalyticsWorkspaceId: monitoring.outputs.logAnalyticsWorkspaceId
    tags: commonTags
  }
  dependsOn: [monitoring]
}

// -----------------------------------------------------------------------------
// 4. Data (PG Flex, ADLS Gen2, private endpoints)
// -----------------------------------------------------------------------------

module data 'modules/data.bicep' = {
  scope: rgDataRG
  name: 'data-s${stampId}'
  params: {
    stampId: stampId
    environment: environment
    baseName: baseName
    location: location
    keyVaultId: platform.outputs.keyVaultId
    logAnalyticsWorkspaceId: monitoring.outputs.logAnalyticsWorkspaceId
    tags: commonTags
  }
  dependsOn: [platform]
}

// -----------------------------------------------------------------------------
// 5. Intelligence (Foundry ref + AI Search + Content Safety)
// -----------------------------------------------------------------------------

module intelligence 'modules/intelligence.bicep' = {
  scope: rgIntelligence
  name: 'intelligence-s${stampId}'
  params: {
    stampId: stampId
    environment: environment
    baseName: baseName
    location: location
    // Foundry is reference-only; the resource lives in rg-data-intel-ph (East US 2)
    foundryResourceName: foundryResourceName
    foundryResourceGroup: foundryResourceGroup
    foundryProjectName: foundryProjectName
    logAnalyticsWorkspaceId: monitoring.outputs.logAnalyticsWorkspaceId
    tags: commonTags
  }
  dependsOn: [monitoring]
}

// -----------------------------------------------------------------------------
// 6. Runtime (ACA env, apps, CR, VNet, AFD)
// -----------------------------------------------------------------------------

module runtime 'modules/runtime.bicep' = {
  scope: rgRt
  name: 'runtime-s${stampId}'
  params: {
    stampId: stampId
    environment: environment
    baseName: baseName
    location: location
    logAnalyticsWorkspaceId: monitoring.outputs.logAnalyticsWorkspaceId
    keyVaultId: platform.outputs.keyVaultId
    postgresFqdn: data.outputs.postgresFqdn
    aiSearchEndpoint: intelligence.outputs.aiSearchEndpoint
    contentSafetyEndpoint: intelligence.outputs.contentSafetyEndpoint
    tags: commonTags
  }
  dependsOn: [platform, data, intelligence]
}

// -----------------------------------------------------------------------------
// Outputs (consumed by CI for URL smoke tests and DNS registration)
// -----------------------------------------------------------------------------

output stampId string = stampId
output environment string = environment
output rolloutGroup string = rolloutGroup

output rgMonitoring string = rgMonitoring.name
output rgPlatform   string = rgPlat.name
output rgData       string = rgDataRG.name
output rgIntelligence string = rgIntelligence.name
output rgRuntime    string = rgRt.name

output logAnalyticsWorkspaceId string = monitoring.outputs.logAnalyticsWorkspaceId
output keyVaultName string = platform.outputs.keyVaultName
output postgresFqdn string = data.outputs.postgresFqdn
output aiSearchEndpoint string = intelligence.outputs.aiSearchEndpoint
output contentSafetyEndpoint string = intelligence.outputs.contentSafetyEndpoint
output acaEnvironmentName string = runtime.outputs.acaEnvironmentName
output containerRegistryLoginServer string = runtime.outputs.containerRegistryLoginServer
output frontDoorFqdn string = runtime.outputs.frontDoorFqdn
