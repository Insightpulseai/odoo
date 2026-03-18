// Azure Databricks Workspace module

@description('Name of the Databricks workspace')
param workspaceName string

@description('Azure region for the workspace')
param location string

@description('Pricing tier for Databricks')
@allowed(['standard', 'premium'])
param pricingTier string

@description('Resource tags')
param tags object

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
    publicNetworkAccess: 'Enabled'
    requiredNsgRules: 'AllRules'
  }
}

output workspaceUrl string = 'https://${workspace.properties.workspaceUrl}'
output workspaceId string = workspace.id
