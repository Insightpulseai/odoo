// =============================================================================
// Azure Subscription-Level RBAC Governance
// =============================================================================
// Target: Production Subscription
// Strategy: Enforce the "Target Clean State" found in ssot/governance/azure-rbac-remediation.yaml
// =============================================================================

targetScope = 'subscription'

@description('Principal ID of the platform admin Entra group (ipai-platform-admins)')
param platformAdminGroupId string

@description('Principal ID of the break-glass emergency account')
param breakGlassObjectId string

@description('Principal ID of the DevOps Service Principal (Service Connection)')
param devOpsServiceId string

@description('Name of the production deployment resource group')
param deploymentResourceGroupName string = 'rg-ipai-deploy-prod'

// Role Definition IDs
var ownerRoleId = '8e3af657-a8ff-443c-a75c-2fe8c4bcb635'
var contributorRoleId = 'b24988ac-6180-42a0-ab88-20f7382dd24c'
var readerRoleId = 'acdd72a7-3385-48ef-bd42-f606fba81ae7'

// 1. Break-Glass Account -> Permanent Owner (Monitored)
// This is the ONLY active permanent human Owner allowed.
resource breakGlassOwnerAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(subscription().id, breakGlassObjectId, ownerRoleId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', ownerRoleId)
    principalId: breakGlassObjectId
    principalType: 'User'
    description: 'IPAI-GOV-01: Break-glass emergency Owner. Permanent active assignment. Monitored by security alert.'
  }
}

// 2. Admin Group -> Default Reader (Foundational)
// Note: Owner/Contributor elevation must be activated via PIM (az cli / PIM API)
resource platformAdminReaderAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(subscription().id, platformAdminGroupId, readerRoleId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', readerRoleId)
    principalId: platformAdminGroupId
    principalType: 'Group'
    description: 'IPAI-GOV-02: Foundational Reader for platform admins. Elevation via PIM only.'
  }
}

// 3. Service Principals -> Scoped Contributor (Not Subscription Owner)
// We assign Contributor at the specific deployment Resource Group scope.
resource devOpsContributorAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(subscription().id, devOpsServiceId, contributorRoleId, deploymentResourceGroupName)
  scope: resourceGroup(deploymentResourceGroupName)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', contributorRoleId)
    principalId: devOpsServiceId
    principalType: 'ServicePrincipal'
    description: 'IPAI-GOV-03: DevOps Service scaled down to Contributor at deployment RG scope.'
  }
}

// =============================================================================
// PIM Eligible Assignments (Manual/Script Activation)
// =============================================================================
// The following MUST be configured via az cli or Entra PIM API:
// 1. ipai-platform-admins group -> Eligible for Owner on Subscription (4h max)
// 2. ipai-platform-admins group -> Eligible for Contributor on Subscription (8h max)
// =============================================================================
