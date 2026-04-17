// modules/ai/ai-search.bicep
// Creates: srch-ipai-prd — BIR knowledge base + Pulser RAG index
// disableLocalAuth: true — MI-only access via DefaultAzureCredential
targetScope = 'resourceGroup'

param prefix        string
param env           string
param location      string
param tags          object
param miPrincipalId string

var searchName = 'srch-${env}-${prefix}'

resource search 'Microsoft.Search/searchServices@2024-06-01-preview' = {
  name:     searchName
  location: location
  tags:     tags
  sku: { name: env == 'prd' ? 'standard' : 'basic' }
  properties: {
    replicaCount:      env == 'prd' ? 2 : 1
    partitionCount:    1
    hostingMode:       'default'
    publicNetworkAccess: 'enabled'
    disableLocalAuth:  true          // MI + Entra-only, no API keys (T-WAF-SEC-03)
    semanticSearch:    'free'        // Semantic re-ranking for BIR document queries
    // authOptions must be omitted when disableLocalAuth is true
  }
}

// ── Resource lock ─────────────────────────────────────────────
resource searchLock 'Microsoft.Authorization/locks@2020-05-01' = {
  name:  'lock-${searchName}'
  scope: search
  properties: {
    level: 'CanNotDelete'
    notes: 'Protects IPAI production AI Search index'
  }
}

// Role: Search Index Data Contributor → MI
var searchIndexContribRoleId = '8ebe5a00-799e-43f5-93ac-243d3dce84a7'
resource miSearchContrib 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name:  guid(search.id, miPrincipalId, searchIndexContribRoleId)
  scope: search
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', searchIndexContribRoleId)
    principalId:      miPrincipalId
    principalType:    'ServicePrincipal'
    description:      'IPAI MI → AI Search Index Data Contributor'
  }
}
// Role: Search Service Contributor → MI
var searchSvcContribRoleId = '7ca78c08-252a-4471-8644-bb5ff32d4ba0'
resource miSearchSvcContrib 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name:  guid(search.id, miPrincipalId, searchSvcContribRoleId)
  scope: search
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', searchSvcContribRoleId)
    principalId:      miPrincipalId
    principalType:    'ServicePrincipal'
  }
}

// ── Outputs ────────────────────────────────────────────────────
output searchName  string = search.name
output endpoint    string = 'https://${search.name}.search.windows.net'
output resourceId  string = search.id
