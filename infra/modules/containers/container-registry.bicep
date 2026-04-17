// modules/containers/container-registry.bicep
// Creates: acripaiprd (Premium tier — geo-replication for prd)
// Admin user DISABLED — MI pulls via AcrPull role
// No hyphens in name (ACR naming constraint)
targetScope = 'resourceGroup'

param prefix        string
param env           string
param location      string
param tags          object
param miPrincipalId string

var acrName = 'acr${prefix}${env}'    // e.g. acripaiprd

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name:     acrName
  location: location
  tags:     tags
  sku: { name: 'Standard' }
  properties: {
    adminUserEnabled:     false          // MI pulls only — no admin credentials
    anonymousPullEnabled: false
    dataEndpointEnabled:  false         // Premium-only feature — disabled with Standard SKU
    publicNetworkAccess: 'Enabled'
    networkRuleBypassOptions: 'AzureServices'
    policies: {
      quarantinePolicy: { status: 'disabled' }
      trustPolicy:      { type: 'Notary', status: 'disabled' }
      retentionPolicy: {
        status:   'enabled'
        days:     30               // Auto-purge untagged images after 30 days
      }
      softDeletePolicy: {
        status:        'enabled'
        retentionDays: 7
      }
    }
  }
}

// ── Geo-replication (Premium only) ────────────────────────────
// REMOVED: geo-replication requires Premium SKU. Disabled with Basic SKU.
// Re-enable by upgrading SKU to Premium and restoring this block.

// ── Resource lock ─────────────────────────────────────────────
resource acrLock 'Microsoft.Authorization/locks@2020-05-01' = {
  name:  'lock-${acrName}'
  scope: acr
  properties: {
    level: 'CanNotDelete'
    notes: 'Protects IPAI production container registry'
  }
}

// Role: AcrPull → MI (all ACA containers pull images)
var acrPullRoleId = '7f951dda-4ed3-4680-a7ca-43fe172d538d'
resource miAcrPull 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name:  guid(acr.id, miPrincipalId, acrPullRoleId)
  scope: acr
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', acrPullRoleId)
    principalId:      miPrincipalId
    principalType:    'ServicePrincipal'
    description:      'IPAI MI → ACR Pull (all ACA containers)'
  }
}

// Role: AcrPush → MI (build agent pushes images)
var acrPushRoleId = '8311e382-0749-4cb8-b61a-304f252e45ec'
resource miAcrPush 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name:  guid(acr.id, miPrincipalId, acrPushRoleId)
  scope: acr
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', acrPushRoleId)
    principalId:      miPrincipalId
    principalType:    'ServicePrincipal'
    description:      'IPAI MI → ACR Push (ipai-build-agent pushes Odoo images)'
  }
}

// ── Outputs ────────────────────────────────────────────────────
output acrName        string = acr.name
output acrLoginServer string = acr.properties.loginServer
output acrResourceId  string = acr.id
