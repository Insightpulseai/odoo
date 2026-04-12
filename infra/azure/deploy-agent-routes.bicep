// infra/azure/deploy-agent-routes.bicep
//
// Wraps bot-route.bicep once per agent to provision a distinct AFD route
// pattern per agent (e.g. /api/tax-guru/messages, /api/doc-intel/messages).
// Pulser remains on the canonical /api/messages pattern.
//
// Scope:   resourceGroup (target: the AFD profile's RG — verify before deploy)
// Deploy:  az deployment group create \
//            --resource-group <AFD_RG> \
//            --template-file infra/azure/deploy-agent-routes.bicep \
//            --parameters env=dev afdProfileName=afd-ipai-dev afdEndpointName=<endpoint-name>
//
// Idempotent — re-running is safe. Each agent gets its own origin group
// + origin + route in the same AFD profile.

targetScope = 'resourceGroup'

@description('Environment suffix — dev | staging | prod')
@allowed([ 'dev', 'staging', 'prod' ])
param env string = 'dev'

@description('Existing AFD profile name (afd-ipai-dev | afd-ipai-prod)')
param afdProfileName string = 'afd-ipai-${env}'

@description('Existing AFD endpoint name (under the profile)')
param afdEndpointName string

@description('Gateway FQDN — ipai-copilot-gateway ACA app')
param gatewayFqdn string = 'ipai-copilot-gateway.insightpulseai.com'

@description('Agent configs — name + route pattern prefix')
param agents array = [
  {
    name: 'pulser'
    // Pulser uses the canonical /api/messages (the Bot Framework default)
    patterns: [ '/api/messages', '/api/messages/*' ]
    customDomain: ''
  }
  {
    name: 'tax-guru'
    patterns: [ '/api/tax-guru/messages', '/api/tax-guru/messages/*' ]
    customDomain: ''
  }
  {
    name: 'doc-intel'
    patterns: [ '/api/doc-intel/messages', '/api/doc-intel/messages/*' ]
    customDomain: ''
  }
  {
    name: 'bank-recon'
    patterns: [ '/api/bank-recon/messages', '/api/bank-recon/messages/*' ]
    customDomain: ''
  }
  {
    name: 'ap-invoice'
    patterns: [ '/api/ap-invoice/messages', '/api/ap-invoice/messages/*' ]
    customDomain: ''
  }
  {
    name: 'finance-close'
    patterns: [ '/api/finance-close/messages', '/api/finance-close/messages/*' ]
    customDomain: ''
  }
]

// ─── One bot-route.bicep invocation per agent ────────────────────────────────
// bot-route.bicep creates origin group, origin, and route. Each agent gets
// distinct names derived from its agent key. No direct mutation of
// front-door.bicep; uses `existing` to attach new child resources.
module agentRoutes 'modules/bot-route.bicep' = [
  for agent in agents: {
    name: 'route-${agent.name}-${env}'
    params: {
      afdProfileName: afdProfileName
      afdEndpointName: afdEndpointName
      gatewayFqdn: gatewayFqdn
      routePatterns: agent.patterns
      customDomainName: agent.customDomain
    }
  }
]

output routeIds array = [
  for i in range(0, length(agents)): {
    agent: agents[i].name
    patterns: agents[i].patterns
    routeId: agentRoutes[i].outputs.routeId
  }
]
