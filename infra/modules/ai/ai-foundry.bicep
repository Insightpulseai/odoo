// modules/ai/ai-foundry.bicep
// Creates: aif-ipai-prd (AI Services / Microsoft Foundry hub) in EUS2
//          proj-ipai-claude (Foundry project — Claude Sonnet 4.6 deployment)
// Naming: aif-ipai-prd (previously ipai-copilot-resource, rg-data-intel-ph pattern)
// disableLocalAuth: true — DefaultAzureCredential (no API keys)
// Deployed in EUS2 — required for Claude Sonnet model availability
targetScope = 'resourceGroup'

param prefix          string
param env             string
param location        string    // EUS2
param tags            object
param miPrincipalId   string
param miResourceId    string
param keyVaultName    string
param kvRgName        string

var foundryName   = 'aif-${prefix}-${env}'
var projectName   = 'proj-${prefix}-claude'

// ── Microsoft Foundry (AI Services hub) ──────────────────────
resource foundry 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name:     foundryName
  location: location
  tags:     tags
  kind:     'AIServices'
  sku:      { name: 'S0' }
  identity: {
    type: 'SystemAssigned'    // Foundry system MI for internal operations
  }
  properties: {
    customSubDomainName:       foundryName
    disableLocalAuth:          true         // Key-less — DefaultAzureCredential only
    publicNetworkAccess:      'Enabled'
    restrictOutboundNetworkAccess: false
    allowedFqdnList:          []
    apiProperties: {}
    allowProjectManagement:    true         // Required for Foundry project provisioning
  }
}

// ── Foundry Project ───────────────────────────────────────────
// Note: Foundry projects are provisioned as CognitiveServices/accounts child
// resource type. The proj-ipai-claude project groups the Claude deployments.
resource foundryProject 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' = {
  name:   projectName
  parent: foundry
  location: location
  identity: {
    type:                   'UserAssigned'
    userAssignedIdentities: { '${miResourceId}': {} }
  }
  properties: {}
}

// ── Claude Sonnet 4.6 deployment ─────────────────────────────
// COMMENTED OUT: claude-sonnet-4-6 not available in this subscription.
// Re-enable when Anthropic models are available via Azure Marketplace acceptance.
// resource claudeSonnet 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
//   name:   'claude-sonnet'
//   parent: foundry
//   sku: {
//     name:     'GlobalStandard'
//     capacity: 25              // 25K TPM — adjust per usage
//   }
//   properties: {
//     model: {
//       format:  'Anthropic'
//       name:    'claude-sonnet-4-6'
//       version: 'latest'
//     }
//     versionUpgradeOption: 'OnceNewDefaultVersionAvailable'
//     modelProviderData: {
//       industry:          'Technology'
//       organizationName:  'InsightPulseAI'
//       countryCode:       'PH'
//     }
//   }
// }

// Claude Haiku 4.5 — cheaper model for eval grading
// COMMENTED OUT: claude-haiku-4-5 not available in this subscription.
// Re-enable when Anthropic models are available via Azure Marketplace acceptance.
// resource claudeHaiku 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
//   name:   'claude-haiku'
//   parent: foundry
//   sku: {
//     name:     'GlobalStandard'
//     capacity: 50
//   }
//   properties: {
//     model: {
//       format:  'Anthropic'
//       name:    'claude-haiku-4-5'
//       version: 'latest'
//     }
//     versionUpgradeOption: 'OnceNewDefaultVersionAvailable'
//   }
//   dependsOn: [claudeSonnet]
// }

// ── Role: Cognitive Services User → MI ───────────────────────
var cogSvcUserRoleId = 'a97b65f3-24c7-4388-baec-2e87135dc908'
resource miCogSvcUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name:  guid(foundry.id, miPrincipalId, cogSvcUserRoleId)
  scope: foundry
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', cogSvcUserRoleId)
    principalId:      miPrincipalId
    principalType:    'ServicePrincipal'
    description:      'IPAI MI → Foundry Cognitive Services User (Claude inference)'
  }
}

// ── Outputs ────────────────────────────────────────────────────
// NOTE: KV secret write removed (BCP165 — cross-scope existing ref not allowed in modules).
// Parent main.bicep or post-deploy.sh is responsible for writing foundryProjectEndpoint to KV.
output foundryEndpoint        string = foundry.properties.endpoint
output foundryProjectEndpoint string = '${foundry.properties.endpoint}api/projects/${foundryProject.name}'
output projectId              string = foundryProject.name
output foundryName            string = foundry.name
output foundryResourceId      string = foundry.id
