// ---------------------------------------------------------------------------
// Canonical Azure tag module
// ---------------------------------------------------------------------------
// Authority:  infra/azure/tags/main.bicep (this file)
// Contract:   ssot/azure/tagging-standard.yaml
// Behavior:   Produces the canonical tag object for subscription/RG/resource
//             deployments. Consumers pass the output `tags` to every resource.
//
// Usage:
//   module tagsModule 'infra/azure/tags/main.bicep' = {
//     name: 'tags'
//     params: {
//       environment: 'dev'
//       plane: 'transaction'
//       system: 'odoo'
//       owner: 'jake'
//       costCenter: 'ipai'
//       criticality: 'medium'
//       dataClassification: 'internal'
//       lifecycle: 'active'
//     }
//   }
//   resource whatever 'Microsoft.Whatever/x@2024-01-01' = {
//     tags: union(tagsModule.outputs.tags, { product: 'insightpulseai' })
//     ...
//   }
// ---------------------------------------------------------------------------

targetScope = 'resourceGroup'

// ---------------------------------------------------------------------------
// Required parameters (match ssot/azure/tagging-standard.yaml required_tags)
// ---------------------------------------------------------------------------

@description('Environment lane')
@allowed([
  'dev'
  'staging'
  'prod'
])
param environment string

@description('Platform plane per four-plane doctrine')
@allowed([
  'transaction'
  'agent'
  'data-intelligence'
  'platform'
  'observability'
  'network'
  'shared'
])
param plane string

@description('Logical system the resource belongs to')
@allowed([
  'odoo'
  'pulser'
  'fabric'
  'databricks'
  'shared'
  'foundry'
  'web'
])
param system string

@description('Single accountable owner')
param owner string = 'jake'

@description('FinOps allocation anchor')
param costCenter string = 'ipai'

@description('Incident priority')
@allowed([
  'low'
  'medium'
  'high'
])
param criticality string = 'medium'

@description('Data sensitivity')
@allowed([
  'internal'
  'restricted'
  'confidential'
  'public'
])
param dataClassification string = 'internal'

@description('Lifecycle stage')
@allowed([
  'experimental'
  'active'
  'legacy'
])
param lifecycle string = 'active'

// ---------------------------------------------------------------------------
// Optional surface-specific parameters
// ---------------------------------------------------------------------------

@description('Product identifier (insightpulseai, w9studio, prismalab)')
param product string = ''

@description('Public domain binding (e.g. erp.insightpulseai.com)')
param domain string = ''

@description('Workload descriptor (e.g. erp-runtime, marketing-site)')
param workload string = ''

@description('ISO deployment date (defaults to today)')
param deployed string = utcNow('yyyy-MM-dd')

@description('Compliance scope (bir-ph, gdpr, pci, none)')
param complianceScope string = 'none'

// ---------------------------------------------------------------------------
// Canonical tag object (always emitted)
// ---------------------------------------------------------------------------

var requiredTags = {
  environment: environment
  plane: plane
  system: system
  owner: owner
  cost_center: costCenter
  managed_by: 'bicep'
  criticality: criticality
  data_classification: dataClassification
  lifecycle: lifecycle
}

var optionalTags = union(
  empty(product) ? {} : { product: product },
  empty(domain) ? {} : { domain: domain },
  empty(workload) ? {} : { workload: workload },
  empty(deployed) ? {} : { deployed: deployed },
  complianceScope == 'none' ? {} : { compliance_scope: complianceScope }
)

// ---------------------------------------------------------------------------
// Outputs
// ---------------------------------------------------------------------------

@description('Canonical tag object to apply to every resource')
output tags object = union(requiredTags, optionalTags)

@description('Required tag subset only (for policy validation)')
output requiredOnly object = requiredTags
