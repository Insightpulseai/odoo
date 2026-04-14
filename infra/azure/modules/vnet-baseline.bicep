// =====================================================
// IPAI VNet — R3 private-endpoint prereq (Issue #626)
// AVM: avm/res/network/virtual-network@0.7.0
// Deploys to: rg-ipai-dev-net-sea (network plane)
// Doctrine: enables T5 private endpoints per R3 roadmap
// =====================================================
targetScope = 'resourceGroup'

param location string = 'southeastasia'
param tags object = {
  org: 'ipai'
  env: 'dev'
  platform: 'pulser-odoo'
  plane: 'network'
  managed_by: 'bicep'
}

@description('VNet address space.')
param addressSpace array = ['10.40.0.0/16']

var vnetName = 'vnet-ipai-dev-sea'

module vnet 'br/public:avm/res/network/virtual-network:0.7.0' = {
  name: 'avm-vnet-${vnetName}'
  params: {
    name: vnetName
    location: location
    tags: tags
    addressPrefixes: addressSpace
    subnets: [
      {
        name: 'pe-subnet'             // dedicated for private endpoints
        addressPrefix: '10.40.1.0/24'
        privateEndpointNetworkPolicies: 'Disabled'
      }
      {
        name: 'aca-subnet'            // ACA workload profile (future internal mode)
        addressPrefix: '10.40.2.0/23'
        delegation: 'Microsoft.App/environments'
      }
      {
        name: 'data-subnet'           // PG flex private access (future)
        addressPrefix: '10.40.4.0/24'
        delegation: 'Microsoft.DBforPostgreSQL/flexibleServers'
      }
      {
        name: 'shared-subnet'         // misc (bastion, jumpboxes, agents)
        addressPrefix: '10.40.5.0/24'
      }
    ]
  }
}

output vnetId string = vnet.outputs.resourceId
output vnetName string = vnet.outputs.name
output peSubnetId string = vnet.outputs.subnetResourceIds[0]
output acaSubnetId string = vnet.outputs.subnetResourceIds[1]
output dataSubnetId string = vnet.outputs.subnetResourceIds[2]
