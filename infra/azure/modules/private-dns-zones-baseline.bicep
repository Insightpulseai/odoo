// =====================================================
// Private DNS Zones — R3 baseline set (Issue #626 prereq)
// AVM: avm/res/network/private-dns-zone@0.8.1
// Deploys to: rg-ipai-dev-net-sea (network plane)
// Doctrine: Azure Pipelines sole CI/CD; reuse AVM upstream
// =====================================================
targetScope = 'resourceGroup'

param tags object = {
  org: 'ipai'
  env: 'dev'
  platform: 'pulser-odoo'
  plane: 'security'
  workload: 'private-endpoint'
  managed_by: 'bicep'
}

@description('VNet resource IDs to link these zones to. Empty = no auto-link yet (zone exists, PE can bind later).')
param vnetResourceIds array = []

// 8 canonical zones covering every Plane A/B service that needs private DNS
var zoneNames = [
  'privatelink.vaultcore.azure.net'                // Key Vault
  'privatelink.blob.core.windows.net'              // Storage (blob)
  'privatelink.postgres.database.azure.com'        // PostgreSQL Flexible
  'privatelink.azurecr.io'                         // Container Registry
  'privatelink.search.windows.net'                 // AI Search
  'privatelink.applicationinsights.azure.com'      // App Insights
  'privatelink.servicebus.windows.net'             // Service Bus + Event Hub (Purview uses this)
  'privatelink.cognitiveservices.azure.com'        // Foundry / Azure AI Services
]

module zones 'br/public:avm/res/network/private-dns-zone:0.8.1' = [for zone in zoneNames: {
  name: 'dns-${replace(zone, '.', '-')}'
  params: {
    name: zone
    tags: tags
    virtualNetworkLinks: [for vnetId in vnetResourceIds: {
      registrationEnabled: false
      virtualNetworkResourceId: vnetId
    }]
  }
}]

output zoneNames array = zoneNames
output zoneIds array = [for i in range(0, length(zoneNames)): zones[i].outputs.resourceId]
