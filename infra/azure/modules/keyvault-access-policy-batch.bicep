// infra/azure/modules/keyvault-access-policy-batch.bicep
//
// Adds access policy entries to an existing Key Vault for a batch of
// principals. Non-destructive: uses `add` mode so existing policies are
// preserved.

@description('Existing Key Vault name (in the current RG scope of this module)')
param keyVaultName string

@description('Array of principalIds (user-assigned MI principalIds)')
param principalIds array

@description('Secret permissions to grant (e.g. [get, list])')
param secretPermissions array = []

@description('Certificate permissions to grant')
param certificatePermissions array = []

@description('Key permissions to grant')
param keyPermissions array = []

resource kv 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
}

resource policies 'Microsoft.KeyVault/vaults/accessPolicies@2023-07-01' = {
  parent: kv
  name: 'add'
  properties: {
    accessPolicies: [
      for pid in principalIds: {
        tenantId: subscription().tenantId
        objectId: pid
        permissions: {
          secrets: secretPermissions
          certificates: certificatePermissions
          keys: keyPermissions
        }
      }
    ]
  }
}
