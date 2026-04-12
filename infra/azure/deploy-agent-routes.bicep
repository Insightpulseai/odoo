// infra/azure/deploy-agent-routes.bicep
//
// Adds per-agent AFD routes for the 6 IPAI bot surfaces. Each route
// sends its path pattern to the shared `og-copilot-gateway` origin
// group (pointing at ipai-bot-proxy-<env>, the external ingress that
// fronts the internal ipai-copilot-gateway).
//
// Pulser uses the canonical `/api/messages` Bot Framework default;
// other agents are namespaced to `/api/<name>/messages` so a single
// bot-proxy can host all six.
//
// Scope:   resourceGroup (where the AFD profile lives)
// Deploy:  az deployment group create \
//            --resource-group rg-ipai-dev-odoo-runtime \
//            --template-file infra/azure/deploy-agent-routes.bicep \
//            --parameters env=dev afdEndpointName=afd-ipai-dev-ep \
//                         gatewayFqdn="<bot-proxy FQDN from aca-bot-proxy.bicep>"
//
// This file is idempotent and inlines OG + origin + 6 routes to avoid
// the duplicate-origin-group race that happens when the same OG is
// created in parallel submodule invocations.

targetScope = 'resourceGroup'

@description('Environment suffix — dev | staging | prod')
@allowed([ 'dev', 'staging', 'prod' ])
param env string = 'dev'

@description('Existing AFD profile name (afd-ipai-dev | afd-ipai-prod)')
param afdProfileName string = 'afd-ipai-${env}'

@description('Existing AFD endpoint name (under the profile)')
param afdEndpointName string

@description('Gateway FQDN — external ACA ingress for bot-proxy (aca-bot-proxy.bicep output.fqdn)')
param gatewayFqdn string

@description('HTTPS port on the origin')
param originHttpsPort int = 443

@description('Origin Host header (usually same as gatewayFqdn)')
param originHostHeader string = gatewayFqdn

@description('Probe path for AFD health check on the bot-proxy')
param probePath string = '/healthz'

@description('Origin group name — shared by all 6 agent routes')
param originGroupName string = 'og-copilot-gateway'

@description('Agent route configs — one AFD route per entry')
param agents array = [
  { name: 'pulser',        patterns: [ '/api/messages',              '/api/messages/*' ] }
  { name: 'tax-guru',      patterns: [ '/api/tax-guru/messages',     '/api/tax-guru/messages/*' ] }
  { name: 'doc-intel',     patterns: [ '/api/doc-intel/messages',    '/api/doc-intel/messages/*' ] }
  { name: 'bank-recon',    patterns: [ '/api/bank-recon/messages',   '/api/bank-recon/messages/*' ] }
  { name: 'ap-invoice',    patterns: [ '/api/ap-invoice/messages',   '/api/ap-invoice/messages/*' ] }
  { name: 'finance-close', patterns: [ '/api/finance-close/messages','/api/finance-close/messages/*' ] }
]

// ─── Reference existing AFD profile + endpoint ──────────────────────────────
resource afdProfile 'Microsoft.Cdn/profiles@2023-05-01' existing = {
  name: afdProfileName
}

resource afdEndpoint 'Microsoft.Cdn/profiles/afdEndpoints@2023-05-01' existing = {
  parent: afdProfile
  name: afdEndpointName
}

// ─── Shared origin group (create once, safe to re-run — ARM is idempotent
//     on identical properties). Cascades to the origin below.
resource botOriginGroup 'Microsoft.Cdn/profiles/originGroups@2023-05-01' = {
  parent: afdProfile
  name: originGroupName
  properties: {
    loadBalancingSettings: {
      sampleSize: 4
      successfulSamplesRequired: 3
      additionalLatencyInMilliseconds: 50
    }
    healthProbeSettings: {
      probePath: probePath
      probeRequestType: 'GET'
      probeProtocol: 'Https'
      probeIntervalInSeconds: 60
    }
    sessionAffinityState: 'Disabled'
  }
}

resource botOrigin 'Microsoft.Cdn/profiles/originGroups/origins@2023-05-01' = {
  parent: botOriginGroup
  name: 'copilot-gateway-origin'
  properties: {
    hostName: gatewayFqdn
    httpPort: 80
    httpsPort: originHttpsPort
    originHostHeader: originHostHeader
    priority: 1
    weight: 1000
    enabledState: 'Enabled'
    enforceCertificateNameCheck: true
  }
}

// ─── One AFD route per agent — all point at the shared OG ───────────────────
// pulser uses `pulser-bot-route` (matches existing name for backward
// compatibility); others are `route-<agent>-<env>`.
resource agentRoutes 'Microsoft.Cdn/profiles/afdEndpoints/routes@2023-05-01' = [
  for agent in agents: {
    parent: afdEndpoint
    name: agent.name == 'pulser' ? 'pulser-bot-route' : 'route-${agent.name}-${env}'
    dependsOn: [
      botOrigin
    ]
    properties: {
      customDomains: []
      originGroup: {
        id: botOriginGroup.id
      }
      supportedProtocols: [ 'Https' ]
      patternsToMatch: agent.patterns
      forwardingProtocol: 'HttpsOnly'
      linkToDefaultDomain: 'Enabled'
      httpsRedirect: 'Enabled'
      enabledState: 'Enabled'
      cacheConfiguration: null
    }
  }
]

// ─── Outputs ────────────────────────────────────────────────────────────────
output routes array = [
  for i in range(0, length(agents)): {
    agent: agents[i].name
    routeName: agentRoutes[i].name
    patterns: agents[i].patterns
  }
]
output originGroupId string = botOriginGroup.id
output originHost string = botOrigin.properties.hostName
