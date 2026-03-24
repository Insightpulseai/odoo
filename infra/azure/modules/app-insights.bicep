// Application Insights — APM telemetry connected to Log Analytics workspace

@description('Application Insights resource name')
param appInsightsName string

@description('Azure region')
param location string

@description('Log Analytics workspace resource ID')
param workspaceId string

@description('Resource tags')
param tags object

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: workspaceId
    IngestionMode: 'LogAnalytics'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
    RetentionInDays: 90
  }
}

output connectionString string = appInsights.properties.ConnectionString
output instrumentationKey string = appInsights.properties.InstrumentationKey
output appInsightsId string = appInsights.id
output appInsightsName string = appInsights.name
