// modules/monitoring/log-analytics.bicep
// Creates: log-ipai-prd-sea (90-day retention)
targetScope = 'resourceGroup'

param prefix   string
param env      string
param location string
param tags     object

var workspaceName = 'log-${prefix}-${env}-sea'

resource workspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name:     workspaceName
  location: location
  tags:     tags
  properties: {
    sku:              { name: 'PerGB2018' }
    retentionInDays:  90
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
      searchVersion: 1
    }
    workspaceCapping: { dailyQuotaGb: -1 }
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery:     'Enabled'
  }
}

// ── Outputs ────────────────────────────────────────────────────
output workspaceId   string = workspace.id
output workspaceName string = workspace.name
output customerId    string = workspace.properties.customerId
