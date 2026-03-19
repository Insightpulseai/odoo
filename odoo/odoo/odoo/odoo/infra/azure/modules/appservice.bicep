// Azure App Service Plan + Web App module
// Linux, Node 18 runtime, Key Vault reference integration

@description('Base name for App Service resources')
param appName string

@description('Azure region')
param location string

@description('App Service Plan SKU')
param sku string

@description('Resource tags')
param tags object

@description('Key Vault name for managed identity access')
param keyVaultName string

resource appServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: '${appName}-plan'
  location: location
  tags: tags
  kind: 'linux'
  sku: {
    name: sku
  }
  properties: {
    reserved: true
  }
}

resource webApp 'Microsoft.Web/sites@2023-01-01' = {
  name: appName
  location: location
  tags: tags
  kind: 'app,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'NODE|18-lts'
      alwaysOn: sku != 'F1'
      minTlsVersion: '1.2'
      ftpsState: 'Disabled'
      appSettings: [
        {
          name: 'KEY_VAULT_NAME'
          value: keyVaultName
        }
      ]
    }
  }
}

output appUrl string = 'https://${webApp.properties.defaultHostName}'
output appName string = webApp.name
