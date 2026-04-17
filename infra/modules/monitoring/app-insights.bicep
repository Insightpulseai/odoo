// modules/monitoring/app-insights.bicep
// Creates: appi-ipai-prd — stores connection string in KV
// ACA containers read: kv-ipai-prd-sea/appi-connection-string
targetScope = 'resourceGroup'

param prefix                    string
param env                       string
param location                  string
param tags                      object
param logAnalyticsWorkspaceId   string
param keyVaultName              string
param keyVaultResourceGroupName string

var appiName = 'appi-${prefix}-${env}'

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name:     appiName
  location: location
  tags:     tags
  kind:     'web'
  properties: {
    Application_Type:               'web'
    WorkspaceResourceId:             logAnalyticsWorkspaceId
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery:     'Enabled'
    DisableIpMasking:                false
    RetentionInDays:                 90
  }
}

// ── Outputs ────────────────────────────────────────────────────
// NOTE: KV secret write removed (BCP165 — cross-scope existing ref not allowed in modules).
// Parent main.bicep or post-deploy.sh is responsible for writing appi-connection-string to KV.
output appInsightsId      string = appInsights.id
output instrumentationKey string = appInsights.properties.InstrumentationKey
output connectionString   string = appInsights.properties.ConnectionString
