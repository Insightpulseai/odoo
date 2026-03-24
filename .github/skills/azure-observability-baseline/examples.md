# azure-observability-baseline -- Worked Examples

## Example 1: Log Analytics + App Insights (Bicep)

```bicep
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'log-ipai-dev'
  location: location
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'appi-ipai-dev'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
  }
}

output appInsightsConnectionString string = appInsights.properties.ConnectionString
```

## Example 2: ACA Environment with App Insights

```bicep
resource acaEnv 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: 'ipai-odoo-dev-env'
  location: location
  properties: {
    appInsightsConfiguration: {
      connectionString: appInsightsConnectionString
    }
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
}
```

## Example 3: PG Diagnostic Settings

```bicep
resource pgDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'pg-ipai-odoo-diagnostics'
  scope: postgresServer
  properties: {
    workspaceId: logAnalytics.id
    logs: [
      { category: 'PostgreSQLLogs'; enabled: true; retentionPolicy: { days: 30; enabled: true } }
      { category: 'PostgreSQLFlexSessions'; enabled: true; retentionPolicy: { days: 7; enabled: true } }
      { category: 'PostgreSQLFlexQueryStoreRuntime'; enabled: true; retentionPolicy: { days: 7; enabled: true } }
    ]
    metrics: [
      { category: 'AllMetrics'; enabled: true; retentionPolicy: { days: 30; enabled: true } }
    ]
  }
}
```

## Example 4: Alert Rules

```bicep
resource alertAcaCpu 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: 'alert-aca-cpu-high'
  location: 'global'
  properties: {
    severity: 2
    enabled: true
    scopes: [acaEnv.id]
    evaluationFrequency: 'PT5M'
    windowSize: 'PT15M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: 'CpuHigh'
          metricName: 'UsageNanoCores'
          operator: 'GreaterThan'
          threshold: 800000000  // 80% of 1 core in nanocores
          timeAggregation: 'Average'
        }
      ]
    }
    actions: [{ actionGroupId: actionGroup.id }]
  }
}
```

## Example 5: MCP Query Sequence

```
Step 1: microsoft_docs_search("Azure Container Apps Application Insights monitoring")
Result: ACA environments support built-in App Insights via connectionString
        in environment config. System logs and app logs routed automatically.
        Custom metrics via OpenTelemetry SDK optional.

Step 2: microsoft_docs_search("Azure Monitor alert rules container apps CPU memory")
Result: Use metric alerts on ACA environment. Key metrics: UsageNanoCores,
        WorkingSetBytes, NetworkBytesReceived. Alert evaluation minimum 1 min.

Step 3: microsoft_docs_search("Azure Log Analytics diagnostic settings PostgreSQL Flexible")
Result: PG Flex supports diagnostic settings for PostgreSQLLogs,
        PostgreSQLFlexSessions, QueryStoreRuntime, QueryStoreWaitStatistics.
        Route to Log Analytics workspace. Retention configurable per category.
```

## Example 6: Stale References to Remove

Search for and remove patterns like:
- `prometheus.yml` or `prometheus.yml` references in docs
- `grafana` dashboard JSON or URLs in runbooks
- `cAdvisor` container references in compose files
- `node_exporter` references in monitoring docs
- Docker-specific log driver configurations presented as production monitoring
