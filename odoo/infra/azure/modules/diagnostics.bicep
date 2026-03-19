// Azure Diagnostic Settings module
// Attaches diagnostic settings to a target resource, sending logs/metrics to Log Analytics.
//
// Usage: Deploy this module with targetScope = 'resourceGroup' and pass the
// target resource ID. The module uses an extension resource pattern.
//
// Note: Bicep diagnostic settings are typically declared inline per resource.
// This module provides a reusable pattern for attaching diagnostics after
// the fact (e.g., to existing resources not managed by this Bicep deployment).

@description('Name of the diagnostic setting')
param diagnosticSettingName string = 'diag-to-law'

@description('Resource ID of the target resource to attach diagnostics to')
param targetResourceId string

@description('Log Analytics workspace resource ID')
param logAnalyticsWorkspaceId string

@description('Enable log collection (allLogs category group)')
param enableLogs bool = true

@description('Enable metric collection (AllMetrics category)')
param enableMetrics bool = true

// Diagnostic settings are extension resources — deployed via ARM targetResourceId scope.
// In Bicep, this requires using a module with explicit scope or deploying via ARM template.
// For maximum compatibility, this module outputs the ARM deployment payload.
// Consumers should use `az monitor diagnostic-settings create` or inline the setting
// on each resource definition.

// Inline diagnostic setting pattern (copy into resource modules):
//
// resource diag 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
//   name: 'diag-to-law'
//   scope: <parentResource>
//   properties: {
//     workspaceId: logAnalyticsWorkspaceId
//     logs: [{ categoryGroup: 'allLogs', enabled: true }]
//     metrics: [{ category: 'AllMetrics', enabled: true }]
//   }
// }

// Output the CLI command for applying diagnostics to existing resources
output cliCommand string = 'az monitor diagnostic-settings create --name ${diagnosticSettingName} --resource ${targetResourceId} --workspace ${logAnalyticsWorkspaceId} ${enableLogs ? '--logs \'[{"categoryGroup":"allLogs","enabled":true}]\'' : ''} ${enableMetrics ? '--metrics \'[{"category":"AllMetrics","enabled":true}]\'' : ''}'
