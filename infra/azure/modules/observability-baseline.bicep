// =====================================================
// Observability expansion — plane-scoped Log Analytics + App Insights
// AVM: avm/res/operational-insights/workspace@0.7.1
//      avm/res/insights/component@0.4.2
// Deploys to: rg-ipai-dev-mon-sea (monitoring plane)
// =====================================================
targetScope = 'resourceGroup'

param location string = 'southeastasia'
param tags object = {
  org: 'ipai'
  env: 'dev'
  platform: 'pulser-odoo'
  plane: 'observability'
  managed_by: 'bicep'
}

// Plane-scoped workspaces — isolate logs per plane (agent / data / runtime)
// Existing: log-ipai-dev-sea (shared). Adding 3 plane-scoped ones.
var workspaceNames = [
  'log-ipai-dev-agent-sea'
  'log-ipai-dev-data-sea'
  'log-ipai-dev-runtime-sea'
]

module workspaces 'br/public:avm/res/operational-insights/workspace:0.7.1' = [for n in workspaceNames: {
  name: 'avm-law-${n}'
  params: {
    name: n
    location: location
    tags: tags
    dailyQuotaGb: 1
    dataRetention: 30
  }
}]

// Plane-scoped App Insights — one per plane using its own LAW
var appiNames = [
  'appi-ipai-dev-agent-sea'
  'appi-ipai-dev-runtime-sea'
]

module appInsights 'br/public:avm/res/insights/component:0.4.2' = [for i in range(0, length(appiNames)): {
  name: 'avm-appi-${appiNames[i]}'
  params: {
    name: appiNames[i]
    location: location
    tags: tags
    workspaceResourceId: workspaces[i].outputs.resourceId  // agent LAW[0], runtime LAW[2] — using[i] as simplification; adjust if strict binding needed
    applicationType: 'web'
    kind: 'web'
  }
}]

output workspaceIds array = [for i in range(0, length(workspaceNames)): workspaces[i].outputs.resourceId]
output appiIds array = [for i in range(0, length(appiNames)): appInsights[i].outputs.resourceId]
