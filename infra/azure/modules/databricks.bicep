// Azure Databricks Workspace module
// Hardened: VNet injection, diagnostics, parameterized network access

@description('Name of the Databricks workspace')
param workspaceName string

@description('Azure region for the workspace')
param location string

@description('Pricing tier for Databricks')
@allowed(['standard', 'premium'])
param pricingTier string

@description('Resource tags')
param tags object = {}

@description('Public network access (set to Disabled for prod)')
@allowed(['Enabled', 'Disabled'])
param publicNetworkAccess string = 'Enabled'

@description('Enable VNet injection for network isolation')
param enableVnetInjection bool = false

@description('Resource ID of the VNet (required when enableVnetInjection is true)')
param vnetId string = ''

@description('Name of the public (host) subnet within the VNet')
param publicSubnetName string = ''

@description('Name of the private (container) subnet within the VNet')
param privateSubnetName string = ''

@description('Enable diagnostic settings to Log Analytics')
param enableDiagnostics bool = false

@description('Log Analytics workspace resource ID (required when enableDiagnostics is true)')
param logAnalyticsWorkspaceId string = ''

resource workspace 'Microsoft.Databricks/workspaces@2024-05-01' = {
  name: workspaceName
  location: location
  tags: tags
  sku: {
    name: pricingTier
  }
  properties: {
    managedResourceGroupId: subscriptionResourceId(
      'Microsoft.Resources/resourceGroups',
      '${workspaceName}-managed-rg'
    )
    publicNetworkAccess: publicNetworkAccess
    requiredNsgRules: enableVnetInjection ? 'NoAzureDatabricksRules' : 'AllRules'
    parameters: enableVnetInjection ? {
      customVirtualNetworkId: {
        value: vnetId
      }
      customPublicSubnetName: {
        value: publicSubnetName
      }
      customPrivateSubnetName: {
        value: privateSubnetName
      }
      enableNoPublicIp: {
        value: publicNetworkAccess == 'Disabled'
      }
    } : {}
  }
}

resource diagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = if (enableDiagnostics) {
  name: '${workspaceName}-diag'
  scope: workspace
  properties: {
    workspaceId: logAnalyticsWorkspaceId
    logs: [
      {
        categoryGroup: 'allLogs'
        enabled: true
        retentionPolicy: {
          enabled: false
          days: 0
        }
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
        retentionPolicy: {
          enabled: false
          days: 0
        }
      }
    ]
  }
}

output workspaceUrl string = 'https://${workspace.properties.workspaceUrl}'
output workspaceId string = workspace.id
