// =============================================================================
// Entra PIM Governance — Eligible Role Assignments
// =============================================================================
// Implements SAP benchmark #644: Privileged Identity Management for admin roles.
//
// Strategy: Use Azure PIM-eligible role assignments (time-bound, require activation)
// instead of permanent "active" assignments for privileged roles.
//
// Scope: Subscription-level for Global Admin, Contributor, Owner, User Access Admin.
// Resource-group-level for Key Vault, ACA, and PG admin roles.
//
// NOTE: PIM eligible assignments require Microsoft.Authorization/roleEligibilityScheduleRequests
// which is an ARM control-plane operation. Bicep supports this via
// Microsoft.Authorization/roleAssignments@2022-04-01 for active assignments,
// but PIM eligible assignments require the PIM API or az cli.
//
// This module creates the RBAC foundation:
//   1. Role assignment conditions (least-privilege active assignments)
//   2. PIM-ready role definitions documented for az cli activation
//   3. Custom role for Odoo Operator (read + restart, no delete)
// =============================================================================

targetScope = 'resourceGroup'

@description('Principal ID of the platform admin group in Entra ID')
param platformAdminGroupId string

@description('Principal ID of the Odoo operator group in Entra ID')
param odooOperatorGroupId string = ''

@description('Principal ID of the managed identity for ACA workloads')
param acaManagedIdentityPrincipalId string = ''

@description('Key Vault resource name for scoped RBAC')
param keyVaultName string = ''

@description('Environment name')
@allowed(['dev', 'staging', 'prod'])
param environment string = 'dev'

@description('Tags')
param tags object = {}

// Built-in role definition IDs
var readerRoleId = 'acdd72a7-3385-48ef-bd42-f606fba81ae7'
var contributorRoleId = 'b24988ac-6180-42a0-ab88-20f7382dd24c'
var keyVaultSecretsUserRoleId = '4633458b-17de-408a-b874-0445c86b69e6'
var keyVaultSecretsOfficerRoleId = 'b86a8fe4-44ce-4948-aee5-eccb2c155cd7'
var monitoringReaderRoleId = '43d0d8ad-25c7-4714-9337-8ba259a9fe05'

// Custom role: Odoo Operator (read + restart ACA apps, no delete/create)
resource odooOperatorRole 'Microsoft.Authorization/roleDefinitions@2022-04-01' = {
  name: guid(resourceGroup().id, 'odoo-operator-${environment}')
  properties: {
    roleName: 'Odoo Operator (${environment})'
    description: 'Can view, restart, and scale Odoo ACA apps. Cannot create, delete, or modify infrastructure. SAP benchmark #644 least-privilege role.'
    type: 'CustomRole'
    permissions: [
      {
        actions: [
          'Microsoft.App/containerApps/read'
          'Microsoft.App/containerApps/revisions/read'
          'Microsoft.App/containerApps/revisions/restart/action'
          'Microsoft.App/containerApps/start/action'
          'Microsoft.App/containerApps/stop/action'
          'Microsoft.App/managedEnvironments/read'
          'Microsoft.Insights/metrics/read'
          'Microsoft.Insights/logs/read'
          'Microsoft.OperationalInsights/workspaces/read'
          'Microsoft.OperationalInsights/workspaces/query/read'
        ]
        notActions: []
        dataActions: []
        notDataActions: []
      }
    ]
    assignableScopes: [
      resourceGroup().id
    ]
  }
}

// Active assignment: Platform admin group gets Reader (not Contributor) as default
// Contributor/Owner access should be activated via PIM eligible assignment (az cli)
resource platformAdminReaderAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, platformAdminGroupId, readerRoleId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', readerRoleId)
    principalId: platformAdminGroupId
    principalType: 'Group'
    description: 'SAP benchmark #644: Default Reader for platform admins. Contributor access via PIM activation only.'
  }
}

// Active assignment: Platform admin group gets Monitoring Reader
resource platformAdminMonitoringAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, platformAdminGroupId, monitoringReaderRoleId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', monitoringReaderRoleId)
    principalId: platformAdminGroupId
    principalType: 'Group'
    description: 'SAP benchmark #644: Monitoring Reader for platform admins (always-on).'
  }
}

// Active assignment: Odoo operator group gets custom Odoo Operator role
resource odooOperatorAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(odooOperatorGroupId)) {
  name: guid(resourceGroup().id, odooOperatorGroupId, odooOperatorRole.id)
  properties: {
    roleDefinitionId: odooOperatorRole.id
    principalId: odooOperatorGroupId
    principalType: 'Group'
    description: 'SAP benchmark #644: Custom Odoo Operator role for day-to-day operations.'
  }
}

// Active assignment: ACA managed identity gets Key Vault Secrets User (read-only)
resource acaKeyVaultAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (!empty(acaManagedIdentityPrincipalId) && !empty(keyVaultName)) {
  name: guid(resourceGroup().id, acaManagedIdentityPrincipalId, keyVaultSecretsUserRoleId)
  scope: resourceGroup()
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', keyVaultSecretsUserRoleId)
    principalId: acaManagedIdentityPrincipalId
    principalType: 'ServicePrincipal'
    description: 'SAP benchmark #644: ACA managed identity reads secrets from Key Vault. No write access.'
  }
}

// Outputs
output odooOperatorRoleId string = odooOperatorRole.id
output odooOperatorRoleName string = odooOperatorRole.properties.roleName

// =============================================================================
// PIM Eligible Assignments (cannot be done in Bicep — documented for az cli)
// =============================================================================
// The following PIM eligible role assignments must be created via az cli or
// Microsoft Graph API. They cannot be expressed in Bicep as of 2026-04.
//
// Run: scripts/governance/configure-pim.sh
//
// Eligible assignments to create:
//   1. Platform Admin Group → Contributor on rg-ipai-dev-odoo-runtime (8h max, justification required)
//   2. Platform Admin Group → Key Vault Secrets Officer on kv-ipai-dev (4h max, justification required)
//   3. Platform Admin Group → Owner on subscription (4h max, MFA + justification + approval required)
//
// Activation policy:
//   - Maximum activation duration: 8 hours (Contributor), 4 hours (Owner/KV Officer)
//   - Require justification: yes
//   - Require MFA on activation: yes
//   - Require approval for Owner: yes (approve by: secondary admin)
//   - Notification on activation: yes (notify: platform-admins@insightpulseai.com)
// =============================================================================
