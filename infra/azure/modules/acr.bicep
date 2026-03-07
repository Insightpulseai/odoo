// Azure Container Registry module for Odoo runtime images

@description('Name of the container registry (must be globally unique)')
param acrName string

@description('Azure region')
param location string

@description('Resource tags')
param tags object

@description('SKU for the container registry')
@allowed(['Basic', 'Standard', 'Premium'])
param sku string = 'Basic'

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
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
        days: 30
        status: sku == 'Premium' ? 'enabled' : 'disabled'
      }
    }
  }
}

output acrName string = acr.name
output acrLoginServer string = acr.properties.loginServer
output acrId string = acr.id
