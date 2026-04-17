@description('Storage account name for Odoo filestore (ir_attachment when location=file)')
param storageAccountName string

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' existing = {
  name: storageAccountName
}

output id string = storage.id
output primaryBlobEndpoint string = storage.properties.primaryEndpoints.blob
