// =====================================================
// Microsoft Purview — governance, lineage, DSPM
// AVM: avm/res/purview/account@0.9.2
// Deploys to: rg-ipai-dev-security-sea
// =====================================================
targetScope = 'resourceGroup'

param prefix string = 'ipai'
param env string = 'dev'
param location string = 'southeastasia'
param tags object = {
  org: 'ipai'
  env: 'dev'
  platform: 'pulser-odoo'
  plane: 'governance'
  workload: 'purview'
}

@description('Public network access. Hardened to Disabled at R3 W6 with PE.')
param publicNetworkAccess string = 'Enabled'

@description('Admin user/group object IDs for Purview Data Curator role.')
param collectionAdmins array = []

var purviewName = 'pv-${prefix}-${env}-sea'

module purview 'br/public:avm/res/purview/account:0.9.2' = {
  name: 'avm-purview-${purviewName}'
  params: {
    name: purviewName
    location: location
    tags: tags
    publicNetworkAccess: publicNetworkAccess
    // Purview always uses a system-assigned identity; not a user-configurable param.
    roleAssignments: [for admin in collectionAdmins: {
      principalId: admin
      roleDefinitionIdOrName: 'Purview Data Curator'
    }]
  }
}

output purviewAccountId string = purview.outputs.resourceId
output purviewAccountName string = purview.outputs.name
