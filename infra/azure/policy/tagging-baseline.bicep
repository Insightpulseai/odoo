// infra/azure/policy/tagging-baseline.bicep
//
// IPAI canonical tagging baseline — 5 built-in Azure Policy definitions
// assigned at subscription scope. Matches ssot/azure/tagging-standard.yaml.
//
// Assigns:
//   1. Deny resources missing `env`, `costcenter`, `owner`
//   2. Deny resource groups missing `owner`
//   3. Modify (inherit-if-missing) from RG for 6 tags
//   4. Modify (inherit-if-missing) from subscription for `businessunit`
// + role assignments for each `modify` policy's MI to run remediation tasks.
//
// Deploy:
//   az deployment sub create \
//     --location southeastasia \
//     --template-file infra/azure/policy/tagging-baseline.bicep \
//     --subscription 536d8cf6-89e1-4815-aef3-d5f2c5f4d070
//
// After deploy — trigger remediation on existing non-compliant resources:
//   for tag in env costcenter owner businessunit project data-classification; do
//     az policy remediation create \
//       --name "remediate-inherit-rg-${tag}-$(date +%Y%m%d)" \
//       --policy-assignment "ipai-inherit-rg-${tag}" \
//       --resource-discovery-mode ReEvaluateCompliance
//   done

targetScope = 'subscription'

@description('Required tag keys — deny if missing on resources')
param requiredTagKeys array = [ 'env', 'costcenter', 'owner' ]

@description('Tag keys to inherit from resource group if missing')
param inheritedFromRgKeys array = [
  'env'
  'costcenter'
  'owner'
  'businessunit'
  'project'
  'data-classification'
]

@description('Tag keys to inherit from subscription if missing')
param inheritedFromSubKeys array = [ 'businessunit' ]

@description('Location for policy MI (where remediation tasks run)')
param location string = 'southeastasia'

// ─── Built-in policy definition IDs ──────────────────────────────────────────
var policyRequireOnResources    = tenantResourceId('Microsoft.Authorization/policyDefinitions', '871b6d14-10aa-478d-b590-94f262ecfa99')
var policyRequireOnResourceGroups = tenantResourceId('Microsoft.Authorization/policyDefinitions', '96670d01-0a4d-4649-9c89-2d3abc0a5025')
var policyInheritFromRgIfMissing  = tenantResourceId('Microsoft.Authorization/policyDefinitions', 'ea3f2387-9b95-492a-a190-fcdc54f7b070')
var policyInheritFromSubIfMissing = tenantResourceId('Microsoft.Authorization/policyDefinitions', '40df99da-1232-49b1-a39a-6da8d878f469')

// Contributor role (built-in) — required for policy MIs to run remediation
var contributorRoleId = 'b24988ac-6180-42a0-ab88-20f7382dd24c'

// ─── 1. Deny: resources missing each required tag ───────────────────────────
resource denyRequired 'Microsoft.Authorization/policyAssignments@2023-04-01' = [
  for tagKey in requiredTagKeys: {
    name: 'ipai-require-${tagKey}'
    properties: {
      displayName: 'IPAI: Require ${tagKey} on resources'
      description: 'Denies creation of resources missing the ${tagKey} tag. Part of ipai canonical tagging baseline.'
      policyDefinitionId: policyRequireOnResources
      parameters: {
        tagName: { value: tagKey }
      }
      enforcementMode: 'Default'
    }
  }
]

// ─── 2. Deny: resource groups missing owner ─────────────────────────────────
resource denyRgOwner 'Microsoft.Authorization/policyAssignments@2023-04-01' = {
  name: 'ipai-rg-require-owner'
  properties: {
    displayName: 'IPAI: Require owner on resource groups'
    description: 'Denies RG creation without an owner tag.'
    policyDefinitionId: policyRequireOnResourceGroups
    parameters: {
      tagName: { value: 'owner' }
    }
  }
}

// ─── 3. Modify: inherit each key from RG if missing ─────────────────────────
resource inheritFromRg 'Microsoft.Authorization/policyAssignments@2023-04-01' = [
  for tagKey in inheritedFromRgKeys: {
    name: 'ipai-inherit-rg-${tagKey}'
    location: location
    identity: {
      type: 'SystemAssigned'
    }
    properties: {
      displayName: 'IPAI: Inherit ${tagKey} from RG if missing'
      description: 'Adds ${tagKey} from resource group tags when resource is missing it. Never overwrites.'
      policyDefinitionId: policyInheritFromRgIfMissing
      parameters: {
        tagName: { value: tagKey }
      }
    }
  }
]

// ─── 4. Modify: inherit businessunit from subscription if missing ───────────
resource inheritFromSub 'Microsoft.Authorization/policyAssignments@2023-04-01' = [
  for tagKey in inheritedFromSubKeys: {
    name: 'ipai-inherit-sub-${tagKey}'
    location: location
    identity: {
      type: 'SystemAssigned'
    }
    properties: {
      displayName: 'IPAI: Inherit ${tagKey} from subscription if missing'
      description: 'Adds ${tagKey} from subscription tags when resource is missing it.'
      policyDefinitionId: policyInheritFromSubIfMissing
      parameters: {
        tagName: { value: tagKey }
      }
    }
  }
]

// ─── 5. Grant Contributor to each modify-policy MI (for remediation) ───────
resource grantRg 'Microsoft.Authorization/roleAssignments@2022-04-01' = [
  for (tagKey, i) in inheritedFromRgKeys: {
    name: guid(subscription().id, 'ipai-inherit-rg', tagKey)
    properties: {
      roleDefinitionId: tenantResourceId('Microsoft.Authorization/roleDefinitions', contributorRoleId)
      principalId: inheritFromRg[i].identity.principalId
      principalType: 'ServicePrincipal'
    }
  }
]

resource grantSub 'Microsoft.Authorization/roleAssignments@2022-04-01' = [
  for (tagKey, i) in inheritedFromSubKeys: {
    name: guid(subscription().id, 'ipai-inherit-sub', tagKey)
    properties: {
      roleDefinitionId: tenantResourceId('Microsoft.Authorization/roleDefinitions', contributorRoleId)
      principalId: inheritFromSub[i].identity.principalId
      principalType: 'ServicePrincipal'
    }
  }
]

// ─── Outputs ────────────────────────────────────────────────────────────────
output requireAssignmentIds array = [ for i in range(0, length(requiredTagKeys)): denyRequired[i].id ]
output inheritRgAssignmentIds array = [ for i in range(0, length(inheritedFromRgKeys)): inheritFromRg[i].id ]
output rgOwnerAssignmentId string = denyRgOwner.id
