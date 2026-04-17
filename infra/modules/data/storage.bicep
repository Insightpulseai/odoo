// modules/data/storage.bicep
// Creates: stipaiprd (general blob) + stlkipaiprd (ADLS Gen2 lakehouse)
// Naming: no hyphens (24-char limit), Storage naming constraint
// stlkipaiprd: Bronze/Silver/Gold medallion architecture (stipaidevlake pattern)
targetScope = 'resourceGroup'

param prefix        string
param env           string
param location      string
param tags          object
param miPrincipalId string

// Storage names: no hyphens, max 24 chars, lowercase
// Pattern reversed to avoid collisions: st<env><prefix> / stlk<env><prefix>
var stName   = 'st${env}ipai'    // e.g. stdevipai / stprdipai
var stlkName = 'stlk${env}ipai' // e.g. stlkdevipai / stlkprdipai (ADLS Gen2)

// ── General Blob Storage ──────────────────────────────────────
resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name:     stName
  location: location
  tags:     tags
  kind:     'StorageV2'
  sku:      { name: env == 'prd' ? 'Standard_GRS' : 'Standard_LRS' }
  properties: {
    accessTier:                     'Hot'
    allowBlobPublicAccess:           false
    allowSharedKeyAccess:            false    // MI-only access
    minimumTlsVersion:              'TLS1_2'
    supportsHttpsTrafficOnly:        true
    publicNetworkAccess:            'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
      bypass:        'AzureServices'
    }
  }
}

resource storageContainerBirInbox 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  name: '${storage.name}/default/bir-inbox'
  properties: {
    publicAccess: 'None'
    metadata: { purpose: 'BIR document upload inbox for ADE processing' }
  }
}
resource storageContainerOdooAttachments 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  name: '${storage.name}/default/odoo-attachments'
  properties: {
    publicAccess: 'None'
    metadata: { purpose: 'Odoo ir.attachment blob storage' }
  }
}

// ── ADLS Gen2 Lakehouse (Medallion architecture) ──────────────
resource adls 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name:     stlkName
  location: location
  tags:     union(tags, { purpose: 'lakehouse-medallion' })
  kind:     'StorageV2'
  sku:      { name: env == 'prd' ? 'Standard_GRS' : 'Standard_LRS' }
  properties: {
    accessTier:              'Hot'
    allowBlobPublicAccess:   false
    allowSharedKeyAccess:    false
    minimumTlsVersion:       'TLS1_2'
    supportsHttpsTrafficOnly: true
    isHnsEnabled:            true     // Hierarchical namespace = ADLS Gen2
    publicNetworkAccess:     'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
      bypass:        'AzureServices'
    }
  }
}

// Medallion layers
resource adlsBronze 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  name: '${adls.name}/default/bronze'
  properties: {
    publicAccess: 'None'
    metadata: { layer: 'bronze', description: 'Raw Odoo CDC + agent telemetry events' }
  }
}
resource adlsSilver 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  name: '${adls.name}/default/silver'
  properties: {
    publicAccess: 'None'
    metadata: { layer: 'silver', description: 'Validated, deduplicated, typed Parquet' }
  }
}
resource adlsGold 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  name: '${adls.name}/default/gold'
  properties: {
    publicAccess: 'None'
    metadata: { layer: 'gold', description: 'Business-ready aggregates for Power BI' }
  }
}

// ── Role: Storage Blob Data Contributor → MI ─────────────────
var blobContribRoleId = 'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
resource miStorageBlobContrib 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name:  guid(storage.id, miPrincipalId, blobContribRoleId)
  scope: storage
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', blobContribRoleId)
    principalId:      miPrincipalId
    principalType:    'ServicePrincipal'
  }
}
resource miAdlsBlobContrib 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name:  guid(adls.id, miPrincipalId, blobContribRoleId)
  scope: adls
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', blobContribRoleId)
    principalId:      miPrincipalId
    principalType:    'ServicePrincipal'
  }
}

// ── Resource locks ────────────────────────────────────────────
resource storageLock 'Microsoft.Authorization/locks@2020-05-01' = {
  name:  'lock-${stName}'
  scope: storage
  properties: {
    level: 'CanNotDelete'
    notes: 'Protects IPAI production blob storage'
  }
}
resource adlsLock 'Microsoft.Authorization/locks@2020-05-01' = {
  name:  'lock-${stlkName}'
  scope: adls
  properties: {
    level: 'CanNotDelete'
    notes: 'Protects IPAI lakehouse (Bronze/Silver/Gold)'
  }
}

// ── Outputs ────────────────────────────────────────────────────
output storageAccountName  string = storage.name
output storagePrimaryEndpoint string = storage.properties.primaryEndpoints.blob
output adlsAccountName     string = adls.name
output adlsPrimaryEndpoint string = adls.properties.primaryEndpoints.dfs
output adlsResourceId      string = adls.id
