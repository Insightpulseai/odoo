// Plane-scoped storage accounts (data, logs, backup)
targetScope = 'resourceGroup'
param location string = 'southeastasia'
param tags object = {
  org: 'ipai'
  env: 'dev'
  platform: 'pulser-odoo'
  plane: 'data'
  managed_by: 'bicep'
}

var storageConfigs = [
  { name: 'stipaidevagent', access: 'Private', sku: 'Standard_LRS' }
  { name: 'stipaidevlogs',  access: 'Private', sku: 'Standard_LRS' }
  { name: 'stipaidevbkp',   access: 'Private', sku: 'Standard_ZRS' }
]

module storage 'br/public:avm/res/storage/storage-account:0.14.3' = [for s in storageConfigs: {
  name: 'st-${s.name}'
  params: {
    name: s.name
    location: location
    tags: tags
    skuName: s.sku
    kind: 'StorageV2'
    publicNetworkAccess: s.access == 'Private' ? 'Disabled' : 'Enabled'
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
}]

output storageIds array = [for i in range(0, length(storageConfigs)): storage[i].outputs.resourceId]
