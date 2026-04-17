// modules/ai/databricks.bicep
// Creates: dbw-ipai-prd (Premium tier)
// Use: agent telemetry, MLflow eval, Vector Search, Unity Catalog
// Separate from Fabric — Databricks handles ML/AI, Fabric handles BI/OKR
targetScope = 'resourceGroup'

param prefix   string
param env      string
param location string
param tags     object

var dbwName      = 'dbw-${prefix}-${env}'
var dbwMrgName   = 'rg-${prefix}-${env}-dbw-managed'   // Databricks managed RG

resource databricks 'Microsoft.Databricks/workspaces@2024-05-01' = {
  name:     dbwName
  location: location
  tags:     tags
  sku: { name: 'premium' }      // Premium required for Unity Catalog
  properties: {
    managedResourceGroupId: subscriptionResourceId('Microsoft.Resources/resourceGroups', dbwMrgName)
    parameters: {
      enableNoPublicIp: { value: false }   // Set true when VNet injection is added
    }
    publicNetworkAccess: 'Enabled'
    requiredNsgRules:    'AllRules'
  }
}

// ── Outputs ────────────────────────────────────────────────────
output workspaceUrl string = databricks.properties.workspaceUrl
output workspaceId  string = databricks.id
output dbwName      string = databricks.name
