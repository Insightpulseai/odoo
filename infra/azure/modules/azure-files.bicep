// Azure Files module
// Storage Account + File Share for Odoo persistent filestore

@description('Name of the storage account')
param storageAccountName string

@description('Azure region')
param location string

@description('Resource tags')
param tags object

@description('File share name')
param fileShareName string = 'odoo-filestore'

@description('File share quota in GB')
param shareQuotaGb int = 50

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  tags: tags
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
    networkAcls: {
      defaultAction: 'Allow'
      bypass: 'AzureServices'
    }
  }
}

resource fileService 'Microsoft.Storage/storageAccounts/fileServices@2023-01-01' = {
  parent: storageAccount
  name: 'default'
}

resource fileShare 'Microsoft.Storage/storageAccounts/fileServices/fileShares@2023-01-01' = {
  parent: fileService
  name: fileShareName
  properties: {
    shareQuota: shareQuotaGb
    accessTier: 'TransactionOptimized'
  }
}

output storageAccountName string = storageAccount.name
output fileShareName string = fileShare.name
#disable-next-line outputs-should-not-contain-secrets
output storageAccountKey string = storageAccount.listKeys().keys[0].value
