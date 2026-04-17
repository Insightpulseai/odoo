// infra/azure/marketplace/deploy-sponsorship-rbac.bicep
//
// Assigns 'Billing Reader' role to the Pulser Agent Managed Identity
// at the Subscription scope to enable Azure Sponsorship monitoring.
//
// Scope:   subscription
// Deploy:  az deployment sub create \
//            --location southcentralus \
//            --template-file infra/azure/marketplace/deploy-sponsorship-rbac.bicep \
//            --parameters principalId=<PULSER_AGENT_PRINCIPAL_ID>

targetScope = 'subscription'

@description('Principal ID of the Managed Identity (e.g., id-ipai-agent-pulser-dev)')
param principalId string

@description('Built-in Role ID for "Billing Reader"')
var billingReaderRoleId = '759216c3-b27b-4c31-a3d0-0030ebb149a4'

resource roleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(subscription().id, principalId, billingReaderRoleId)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', billingReaderRoleId)
    principalId: principalId
    principalType: 'ServicePrincipal'
  }
}

output roleAssignmentId string = roleAssignment.id
