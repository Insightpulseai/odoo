// =============================================================================
// Phase 0: Landing Zone — Resource Group Scaffold
// =============================================================================
//
// Scope:    subscription
// Purpose:  Create the 3 foundational resource groups for InsightPulseAI
// Task:     T0.1 from spec/azure-target-state/tasks.md
// SSOT:     ssot/azure/resources.yaml (target_resource_groups section)
//
// Usage:
//   az deployment sub create \
//     --location southeastasia \
//     --template-file infra/azure/platform/main.bicep \
//     --parameters environment=dev
//
// Follow-up tasks (not in this file):
//   T0.2: Key Vault           → infra/azure/platform/modules/keyvault.bicep
//   T0.3: Log Analytics + AI  → infra/azure/platform/modules/loganalytics.bicep
//   T0.4: Managed Identities  → infra/azure/platform/modules/identity.bicep
//   T0.5: VNet + NSGs         → infra/azure/platform/modules/network.bicep
// =============================================================================

targetScope = 'subscription'

// ── Parameters ──────────────────────────────────────────────────────────────

@description('Environment identifier (dev, staging, prod)')
@allowed([
  'dev'
  'staging'
  'prod'
])
param environment string = 'dev'

@description('Azure region for all resources')
param location string = 'southeastasia'

@description('Common tags applied to all resource groups')
param tags object = {
  project: 'insightpulseai'
  environment: environment
  managedBy: 'bicep'
  spec: 'spec/azure-target-state'
  phase: '0'
}

// ── Resource Groups ─────────────────────────────────────────────────────────

@description('Platform shared services: Key Vault, Log Analytics, App Insights, ACR')
resource rgPlatform 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: 'rg-ipai-platform-${environment}'
  location: location
  tags: tags
}

@description('Agent runtime: Container Apps Environment, Container Apps, Jobs')
resource rgAgents 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: 'rg-ipai-agents-${environment}'
  location: location
  tags: tags
}

@description('Integration workers: connector sync, webhook processors')
resource rgIntegration 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: 'rg-ipai-integration-${environment}'
  location: location
  tags: tags
}

// ── Outputs ─────────────────────────────────────────────────────────────────

output platformResourceGroupName string = rgPlatform.name
output platformResourceGroupId string = rgPlatform.id
output agentsResourceGroupName string = rgAgents.name
output agentsResourceGroupId string = rgAgents.id
output integrationResourceGroupName string = rgIntegration.name
output integrationResourceGroupId string = rgIntegration.id
