param managedIdentityName string

resource mi 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: managedIdentityName
}

output identityId string = mi.id
output principalId string = mi.properties.principalId
output clientId string = mi.properties.clientId
