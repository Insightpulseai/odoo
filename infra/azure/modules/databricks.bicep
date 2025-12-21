// Databricks Workspace module

@description('Name of the Databricks workspace')
param workspaceName string

@description('Azure region')
param location string

@description('Pricing tier')
@allowed(['standard', 'premium'])
param pricingTier string = 'premium'

@description('Resource tags')
param tags object

resource databricksWorkspace 'Microsoft.Databricks/workspaces@2023-02-01' = {
  name: workspaceName
  location: location
  tags: tags
  sku: {
    name: pricingTier
  }
  properties: {
    managedResourceGroupId: subscriptionResourceId('Microsoft.Resources/resourceGroups', '${workspaceName}-managed-rg')
    parameters: {
      enableNoPublicIp: {
        value: false
      }
    }
  }
}

output workspaceName string = databricksWorkspace.name
output workspaceId string = databricksWorkspace.id
output workspaceUrl string = 'https://${databricksWorkspace.properties.workspaceUrl}'
output managedResourceGroupId string = databricksWorkspace.properties.managedResourceGroupId
