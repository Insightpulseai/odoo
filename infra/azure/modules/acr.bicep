// Azure Container Registry

@description('Name of the Container Registry')
param acrName string

@description('Azure region')
param location string

@description('Resource tags')
param tags object

@description('ACR SKU tier')
@allowed(['Basic', 'Standard', 'Premium'])
param sku string = 'Basic'

// Container Registry
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: acrName
  location: location
  tags: tags
  sku: {
    name: sku
  }
  properties: {
    adminUserEnabled: false
    publicNetworkAccess: 'Enabled'
    policies: {
      retentionPolicy: {
        status: 'enabled'
        days: 30
      }
    }
  }
}

output acrLoginServer string = containerRegistry.properties.loginServer
output acrId string = containerRegistry.id
output acrName string = containerRegistry.name
