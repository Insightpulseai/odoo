param keyVaultName string

resource kv 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
}

output id string = kv.id
output vaultUri string = kv.properties.vaultUri
