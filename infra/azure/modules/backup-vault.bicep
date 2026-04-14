// Azure Backup Vault — T9 R3 backup prereq
targetScope = 'resourceGroup'
param location string = 'southeastasia'
param tags object = {
  org: 'ipai'
  env: 'dev'
  platform: 'pulser-odoo'
  plane: 'observability'
  workload: 'backup'
  managed_by: 'bicep'
}

resource bkpVault 'Microsoft.DataProtection/backupVaults@2024-04-01' = {
  name: 'bvault-ipai-dev-sea'
  location: location
  tags: tags
  identity: { type: 'SystemAssigned' }
  properties: {
    storageSettings: [{ type: 'LocallyRedundant', datastoreType: 'VaultStore' }]
    securitySettings: {
      immutabilitySettings: { state: 'Disabled' }
      softDeleteSettings: { state: 'On', retentionDurationInDays: 14 }
    }
  }
}

output bkpVaultId string = bkpVault.id
