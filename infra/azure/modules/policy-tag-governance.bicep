// =============================================================================
// Azure Policy — Tag Governance and Enforcement
// =============================================================================
// Implements SAP benchmark #647: Azure Policy for tag enforcement and governance.
//
// Strategy:
//   Phase 1 (this module): Audit mode — detect non-compliant resources using
//     Azure built-in policy definitions (no custom definitions needed at RG scope).
//   Phase 2 (future): Switch to deny mode after baseline compliance achieved.
//
// Uses built-in policies:
//   - "Require a tag on resources" (built-in ID: 871b6d14-10aa-478d-b466-208cb8a14081)
//
// Scope: Resource group level (deployed per-RG)
// =============================================================================

targetScope = 'resourceGroup'

@description('Environment name')
@allowed(['dev', 'staging', 'prod'])
param environment string = 'dev'

@description('Enforcement mode: Default (deny) or DoNotEnforce (audit only)')
@allowed(['Default', 'DoNotEnforce'])
param enforcementMode string = 'DoNotEnforce'

// Built-in policy: "Require a tag on resources"
// This policy audits/denies resources missing a specific tag.
// Azure built-in ID: 871b6d14-10aa-478d-b466-208cb8a14081
var requireTagPolicyId = subscriptionResourceId('Microsoft.Authorization/policyDefinitions', '871b6d14-10aa-478d-b466-208cb8a14081')

// --- Assignment: Require Environment Tag -----------------------------------
resource requireEnvironmentTagAssignment 'Microsoft.Authorization/policyAssignments@2022-06-01' = {
  name: 'ipai-req-env-tag-${environment}'
  location: resourceGroup().location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    displayName: 'IPAI: Require Environment tag (${environment})'
    description: 'SAP benchmark #647: All resources must have an Environment tag.'
    policyDefinitionId: requireTagPolicyId
    enforcementMode: enforcementMode
    parameters: {
      tagName: {
        value: 'Environment'
      }
    }
    metadata: {
      benchmark: 'SAP-on-Azure #647'
      assignedBy: 'IaC — infra/azure/modules/policy-tag-governance.bicep'
    }
    nonComplianceMessages: [
      {
        message: 'Missing required tag: Environment. Allowed values: dev, staging, prod. See: docs/architecture/SAP_ON_AZURE_BENCHMARK_REPORT.md'
      }
    ]
  }
}

// --- Assignment: Require Project Tag ---------------------------------------
resource requireProjectTagAssignment 'Microsoft.Authorization/policyAssignments@2022-06-01' = {
  name: 'ipai-req-proj-tag-${environment}'
  location: resourceGroup().location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    displayName: 'IPAI: Require Project tag (${environment})'
    description: 'SAP benchmark #647: All resources must have a Project tag.'
    policyDefinitionId: requireTagPolicyId
    enforcementMode: enforcementMode
    parameters: {
      tagName: {
        value: 'Project'
      }
    }
    metadata: {
      benchmark: 'SAP-on-Azure #647'
      assignedBy: 'IaC — infra/azure/modules/policy-tag-governance.bicep'
    }
    nonComplianceMessages: [
      {
        message: 'Missing required tag: Project. See: docs/architecture/SAP_ON_AZURE_BENCHMARK_REPORT.md'
      }
    ]
  }
}

// --- Assignment: Require ManagedBy Tag -------------------------------------
resource requireManagedByTagAssignment 'Microsoft.Authorization/policyAssignments@2022-06-01' = {
  name: 'ipai-req-mgby-tag-${environment}'
  location: resourceGroup().location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    displayName: 'IPAI: Require ManagedBy tag (${environment})'
    description: 'SAP benchmark #647: All resources must declare management method.'
    policyDefinitionId: requireTagPolicyId
    enforcementMode: enforcementMode
    parameters: {
      tagName: {
        value: 'ManagedBy'
      }
    }
    metadata: {
      benchmark: 'SAP-on-Azure #647'
      assignedBy: 'IaC — infra/azure/modules/policy-tag-governance.bicep'
    }
    nonComplianceMessages: [
      {
        message: 'Missing required tag: ManagedBy. Allowed values: Bicep, Manual, Terraform, AzDO, GitHub. See: docs/architecture/SAP_ON_AZURE_BENCHMARK_REPORT.md'
      }
    ]
  }
}

// Outputs
output environmentTagAssignment string = requireEnvironmentTagAssignment.name
output projectTagAssignment string = requireProjectTagAssignment.name
output managedByTagAssignment string = requireManagedByTagAssignment.name
output enforcementMode string = enforcementMode
