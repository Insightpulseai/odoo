param environmentName string

resource env 'Microsoft.App/managedEnvironments@2024-03-01' existing = {
  name: environmentName
}

output id string = env.id
