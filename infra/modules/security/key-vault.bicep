// modules/security/key-vault.bicep
// Creates: kv-ipai-prd-sea + RBAC role assignments + resource lock
// No access policies — RBAC-only mode enforced
// MI gets Secrets User; deploy principal gets Secrets Officer (bootstrap only)
targetScope = 'resourceGroup'

param prefix             string
param env                string
param location           string
param tags               object
param miPrincipalId      string
param deployPrincipalId  string = ''
@secure()
param adeApiKey          string = ''

var kvName = 'kv-${prefix}-${env}-sea'

// ── Key Vault ────────────────────────────────────────────────
resource kv 'Microsoft.KeyVault/vaults@2024-11-01' = {
  name:     kvName
  location: location
  tags:     tags
  properties: {
    sku: {
      family: 'A'
      name:   'standard'
    }
    tenantId:                       subscription().tenantId
    enableRbacAuthorization:        true    // RBAC-only — no legacy access policies
    enableSoftDelete:               true
    softDeleteRetentionInDays:      90
    enablePurgeProtection:          true    // Prevent accidental permanent deletion
    enabledForDeployment:           false
    enabledForTemplateDeployment:   true    // Allow Bicep to read KV params
    enabledForDiskEncryption:       false
    publicNetworkAccess:            'Enabled' // Restrict to VNet post-Marketplace
    networkAcls: {
      defaultAction: 'Allow'
      bypass:        'AzureServices'
    }
  }
}

// ── Resource lock (prevents accidental delete) ────────────────
resource kvLock 'Microsoft.Authorization/locks@2020-05-01' = {
  name:  'lock-${kvName}'
  scope: kv
  properties: {
    level: 'CanNotDelete'
    notes: 'Protects IPAI production Key Vault'
  }
}

// Role: Key Vault Secrets User → Managed Identity (all ACA containers)
var kvSecretsUserRoleId = '4633458b-17de-408a-b874-0445c86b69e6'
resource miSecretsUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name:  guid(kv.id, miPrincipalId, kvSecretsUserRoleId)
  scope: kv
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', kvSecretsUserRoleId)
    principalId:      miPrincipalId
    principalType:    'ServicePrincipal'
    description:      'IPAI MI → KV Secrets User (ACA containers)'
  }
}

// Role: Key Vault Administrator → deploying principal (bootstrap; remove post-deploy)
var kvAdminRoleId = '00482a5a-887f-4fb3-b363-3b7fe8e74483'
resource deployerKvAdmin 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(deployPrincipalId)) {
  name:  guid(kv.id, deployPrincipalId, kvAdminRoleId)
  scope: kv
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', kvAdminRoleId)
    principalId:      deployPrincipalId
    principalType:    'User'
    description:      'Bootstrap deployer — remove after initial secret population'
  }
}

// ── Seed secrets (only if provided at deploy time) ────────────
resource secretAdeApiKey 'Microsoft.KeyVault/vaults/secrets@2024-11-01' = if (!empty(adeApiKey)) {
  name:   'ade-vision-agent-api-key'
  parent: kv
  properties: {
    value: adeApiKey
    attributes: { enabled: true }
    contentType: 'LandingAI ADE API key — rotate at landing.ai'
  }
}

// Placeholder secrets — populate via post-deploy script
resource secretPgPassword 'Microsoft.KeyVault/vaults/secrets@2024-11-01' = {
  name:   'pg-odoo-admin-password'
  parent: kv
  properties: {
    value:       'REPLACE_AFTER_DEPLOY'
    attributes:  { enabled: true }
    contentType: 'PostgreSQL ipai-odoo-prd admin password — rotate after first deploy'
  }
}

// ── Outputs ────────────────────────────────────────────────────
output kvName          string = kv.name
output kvUri           string = kv.properties.vaultUri
output kvResourceId    string = kv.id
