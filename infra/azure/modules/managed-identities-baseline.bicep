// =====================================================
// Plane-scoped Managed Identities — runtime/build/data/agent separation
// AVM: avm/res/managed-identity/user-assigned-identity@0.5.0
// Deploys to: rg-ipai-dev-security-sea (identity plane)
// =====================================================
targetScope = 'resourceGroup'

param location string = 'southeastasia'
param tags object = {
  org: 'ipai'
  env: 'dev'
  platform: 'pulser-odoo'
  plane: 'identity'
  managed_by: 'bicep'
}

// Existing: id-ipai-dev (shared), id-ipai-stg.
// Adding plane-scoped identities so each plane has least-privilege SP.
var identityNames = [
  'id-ipai-dev-data'      // data plane (Databricks, PG, Storage)
  'id-ipai-dev-agent'     // agent plane (Foundry, Pulser)
  'id-ipai-dev-runtime'   // ACA runtime (Odoo, copilot-gateway, bot-proxy)
  'id-ipai-dev-pipeline'  // Azure Pipelines service connection
]

module ids 'br/public:avm/res/managed-identity/user-assigned-identity:0.5.0' = [for n in identityNames: {
  name: 'mi-${n}'
  params: {
    name: n
    location: location
    tags: tags
  }
}]

output identityNames array = identityNames
output identityIds array = [for i in range(0, length(identityNames)): ids[i].outputs.resourceId]
output identityPrincipalIds array = [for i in range(0, length(identityNames)): ids[i].outputs.principalId]
