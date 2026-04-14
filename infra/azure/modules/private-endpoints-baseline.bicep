// =====================================================
// Private Endpoints — R3 T5 (Issue #626)
// AVM: avm/res/network/private-endpoint@0.9.1
// Binds existing services to pe-subnet + respective DNS zone
// Deploys to: rg-ipai-dev-net-sea (PEs live in network plane)
// =====================================================
targetScope = 'resourceGroup'

param location string = 'southeastasia'
param tags object = {
  org: 'ipai'
  env: 'dev'
  platform: 'pulser-odoo'
  plane: 'security'
  workload: 'private-endpoint'
  managed_by: 'bicep'
}

@description('Private-endpoint-dedicated subnet ID (from vnet-baseline).')
param peSubnetResourceId string

@description('Map of service → {targetResourceId, groupId, dnsZoneResourceId}.')
param targets array

module pes 'br/public:avm/res/network/private-endpoint:0.9.1' = [for t in targets: {
  name: 'pe-${t.name}'
  params: {
    name: 'pe-ipai-dev-${t.name}'
    location: location
    tags: tags
    subnetResourceId: peSubnetResourceId
    privateLinkServiceConnections: [
      {
        name: 'pe-${t.name}-conn'
        properties: {
          privateLinkServiceId: t.targetResourceId
          groupIds: [t.groupId]
        }
      }
    ]
    privateDnsZoneGroup: {
      privateDnsZoneGroupConfigs: [
        {
          name: 'config1'
          privateDnsZoneResourceId: t.dnsZoneResourceId
        }
      ]
    }
  }
}]

output peIds array = [for i in range(0, length(targets)): pes[i].outputs.resourceId]
