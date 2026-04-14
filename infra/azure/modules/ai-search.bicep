// =====================================================
// Azure AI Search — RAG backbone for Plane B agents
// AVM: avm/res/search/search-service@0.9.2
// Deploys to: rg-ipai-dev-ai-sea
// =====================================================
targetScope = 'resourceGroup'

param prefix string = 'ipai'
param env string = 'dev'
param location string = 'southeastasia'
param tags object = {
  org: 'ipai'
  env: 'dev'
  platform: 'pulser-odoo'
  plane: 'data'
  workload: 'agent-rag'
}

@description('SKU: basic (dev) or standard (prod).')
param sku string = 'basic'
param replicaCount int = 1
param partitionCount int = 1

@description('Log Analytics workspace resource ID for diagnostics. Optional.')
param logAnalyticsWorkspaceId string = ''

var searchName = 'srch-${prefix}-${env}-sea'
var diagnosticSettings = empty(logAnalyticsWorkspaceId) ? [] : [
  {
    workspaceResourceId: logAnalyticsWorkspaceId
    logCategoriesAndGroups: [{ categoryGroup: 'allLogs' }]
    metricCategories: [{ category: 'AllMetrics' }]
  }
]

module aiSearch 'br/public:avm/res/search/search-service:0.9.2' = {
  name: 'avm-search-${searchName}'
  params: {
    name: searchName
    location: location
    tags: tags
    sku: sku
    replicaCount: replicaCount
    partitionCount: partitionCount
    publicNetworkAccess: 'Enabled' // Hardened to 'Disabled' at R3 W6 with PE
    managedIdentities: { systemAssigned: true }
    diagnosticSettings: diagnosticSettings
  }
}

output searchServiceId string = aiSearch.outputs.resourceId
output searchServiceName string = aiSearch.outputs.name
