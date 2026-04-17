// ADLS Gen2 canonical lake (stipaidevlake) for UC + CDM + FinOps FOCUS exports.
// Composes Microsoft.Storage/storageAccounts (HNS) + role assignments for
// the Databricks Unity Catalog access connector.
//
// Idempotent recapture of resource created 2026-04-15:
//   stipaidevlake  (HNS, TLS 1.2, no public blobs) in rg-ipai-dev-data-sea
//   containers: bronze | silver | gold | metastore | msexports
//   role: Storage Blob Data Contributor on unity-catalog-access-connector MI
//
// Deployment:
//   az deployment group create \
//     --resource-group rg-ipai-dev-data-sea \
//     --template-file infra/azure/modules/data-lake-canonical.bicep \
//     --parameters ucAccessConnectorPrincipalId=<principal-id>

targetScope = 'resourceGroup'

@description('Canonical lake storage account name (stipaidevlake).')
param storageAccountName string = 'stipaidevlake'

@description('Azure region.')
param location string = resourceGroup().location

@description('Principal ID of the Databricks Unity Catalog access connector managed identity.')
param ucAccessConnectorPrincipalId string

@description('Resource tags applied to the storage account.')
param tags object = {
  environment: 'dev'
  product: 'pulser'
  owner: 'platform'
  costCenter: 'ipai-platform'
  purpose: 'uc-canonical-lake'
}

var containerNames = [
  'bronze'
  'silver'
  'gold'
  'metastore'
  'msexports' // FinOps FOCUS cost exports land here
]

// Storage Blob Data Contributor role definition (Azure built-in)
var storageBlobDataContributorRoleId = 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountName
  location: location
  tags: tags
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    isHnsEnabled: true
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
    allowBlobPublicAccess: false
    allowSharedKeyAccess: true // Required for az cli container create; tighten to false after UC swap-over
    accessTier: 'Hot'
    networkAcls: {
      defaultAction: 'Allow'
      bypass: 'AzureServices'
    }
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: storage
  name: 'default'
}

resource containers 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = [
  for name in containerNames: {
    parent: blobService
    name: name
    properties: {
      publicAccess: 'None'
    }
  }
]

resource ucAccessConnectorRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: storage
  name: guid(storage.id, ucAccessConnectorPrincipalId, storageBlobDataContributorRoleId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageBlobDataContributorRoleId)
    principalId: ucAccessConnectorPrincipalId
    principalType: 'ServicePrincipal'
  }
}

output storageAccountName string = storage.name
output storageAccountId string = storage.id
output primaryDfsEndpoint string = storage.properties.primaryEndpoints.dfs
