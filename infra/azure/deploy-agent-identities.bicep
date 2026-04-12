// infra/azure/deploy-agent-identities.bicep
//
// Creates one user-assigned managed identity per IPAI agent, for Agent 365
// Entra Agent ID registration (GA 2026-05-01). Also grants each MI
// `get`/`list` on kv-ipai-dev secrets.
//
// Scope:   resourceGroup (target: rg-ipai-dev-platform)
// Deploy:  az deployment group create \
//            --resource-group rg-ipai-dev-platform \
//            --template-file infra/azure/deploy-agent-identities.bicep \
//            --parameters env=dev
//
// Idempotent — re-running is safe. Creates 6 MIs matching the 6 agent
// surfaces under agents/*-surface/.

targetScope = 'resourceGroup'

@description('Environment suffix — dev | staging | prod')
@allowed([ 'dev', 'staging', 'prod' ])
param env string = 'dev'

@description('Azure region for the MIs. Matches rg-ipai-<env>-platform region.')
param location string = resourceGroup().location

@description('Key Vault name to grant secret read access to each agent MI')
param keyVaultName string = 'kv-ipai-${env}'

@description('Key Vault resource group (kv-ipai-dev is in rg-ipai-dev-platform, not runtime)')
param keyVaultResourceGroup string = 'rg-ipai-${env}-platform'

@description('Agent names — create one MI per entry. Must match agents/<name>-surface/ dirs.')
param agents array = [
  'pulser'
  'tax-guru'
  'doc-intel'
  'bank-recon'
  'ap-invoice'
  'finance-close'
]

@description('Common resource tags')
param tags object = {
  project: 'ipai'
  env: env
  layer: 'agents'
  spec: 'pulser-entra-agent-id'
}

// ─── Create one MI per agent ─────────────────────────────────────────────────
resource agentMis 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = [
  for agent in agents: {
    name: 'id-ipai-agent-${agent}-${env}'
    location: location
    tags: union(tags, {
      agent: agent
    })
  }
]

// ─── Reference kv-ipai-<env> (must pre-exist; do NOT create here) ────────────
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
  scope: resourceGroup(keyVaultResourceGroup)
}

// ─── Grant each MI get+list on secrets via access policy ─────────────────────
// Using access-policy mode (not RBAC). Change if kv-ipai-dev later migrates
// to RBAC authorization — that requires a separate roleAssignment module.
module kvAccessPolicies 'modules/keyvault-access-policy-batch.bicep' = {
  name: 'kv-access-policies-agents-${env}'
  scope: resourceGroup(keyVaultResourceGroup)
  params: {
    keyVaultName: keyVaultName
    principalIds: [ for i in range(0, length(agents)): agentMis[i].properties.principalId ]
    secretPermissions: [ 'get', 'list' ]
    certificatePermissions: []
    keyPermissions: []
  }
}

// ─── Outputs ─────────────────────────────────────────────────────────────────
output agentIdentities array = [
  for i in range(0, length(agents)): {
    agent: agents[i]
    name: agentMis[i].name
    clientId: agentMis[i].properties.clientId
    principalId: agentMis[i].properties.principalId
    resourceId: agentMis[i].id
  }
]
