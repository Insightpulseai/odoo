// infra/azure/modules/bot-route.bicep
//
// Additive AFD module: route `/api/messages` (Bot Framework webhook)
// through Azure Front Door (afd-ipai-dev) to the ipai-copilot-gateway
// ACA app. This is the Teams/Copilot surface's ingress path for Pulser.
//
// Non-destructive: references the existing AFD profile + endpoint by
// name, adds a new origin group, origin, and route scoped to the
// `/api/messages` path pattern. Does NOT mutate front-door.bicep.
//
// Usage (from main.bicep):
//   module botRoute 'modules/bot-route.bicep' = if (deployBotRoute) {
//     name: 'bot-route-${environmentSuffix}'
//     params: {
//       afdProfileName:  'afd-ipai-${environmentSuffix}'
//       afdEndpointName: 'ipai-${environmentSuffix}-endpoint'
//       gatewayFqdn:     'ipai-copilot-gateway.internal.${acaEnvDomain}'
//       customDomainName: 'pulser-${environmentSuffix}.insightpulseai.com'
//     }
//   }

@description('Existing AFD profile name (afd-ipai-dev | afd-ipai-prod)')
param afdProfileName string

@description('Existing AFD endpoint name (under the profile)')
param afdEndpointName string

@description('FQDN of the ipai-copilot-gateway ACA app (internal or public)')
param gatewayFqdn string

@description('HTTPS port for the origin (usually 443)')
param originHttpsPort int = 443

@description('Origin host header — usually same as gatewayFqdn')
param originHostHeader string = gatewayFqdn

@description('Probe path for health check on the gateway')
param probePath string = '/healthz'

@description('Route pattern(s) to match. Bot Framework webhook is /api/messages')
param routePatterns array = [
  '/api/messages'
  '/api/messages/*'
]

@description('Optional custom domain name to bind (e.g. pulser-dev.insightpulseai.com). Leave empty to route only via the default *.azurefd.net endpoint.')
param customDomainName string = ''

// ─── Reference existing AFD profile + endpoint ──────────────────────────────
resource afdProfile 'Microsoft.Cdn/profiles@2023-05-01' existing = {
  name: afdProfileName
}

resource afdEndpoint 'Microsoft.Cdn/profiles/afdEndpoints@2023-05-01' existing = {
  parent: afdProfile
  name: afdEndpointName
}

resource customDomain 'Microsoft.Cdn/profiles/customDomains@2023-05-01' existing = if (!empty(customDomainName)) {
  parent: afdProfile
  name: replace(customDomainName, '.', '-')
}

// ─── Origin group: ipai-copilot-gateway ─────────────────────────────────────
resource botOriginGroup 'Microsoft.Cdn/profiles/originGroups@2023-05-01' = {
  parent: afdProfile
  name: 'og-copilot-gateway'
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

// ─── Route: /api/messages → ipai-copilot-gateway ────────────────────────────
// HTTPS-only, no caching (Bot Framework is interactive), forwards to HTTPS origin.
resource botRoute 'Microsoft.Cdn/profiles/afdEndpoints/routes@2023-05-01' = {
  parent: afdEndpoint
  name: 'pulser-bot-route'
  dependsOn: [
    botOrigin
  ]
  properties: {
    customDomains: empty(customDomainName) ? [] : [
      {
        id: customDomain.id
      }
    ]
    originGroup: {
      id: botOriginGroup.id
    }
    supportedProtocols: [
      'Https'
    ]
    patternsToMatch: routePatterns
    forwardingProtocol: 'HttpsOnly'
    linkToDefaultDomain: empty(customDomainName) ? 'Enabled' : 'Disabled'
    httpsRedirect: 'Enabled'
    enabledState: 'Enabled'
    cacheConfiguration: null
  }
}

// ─── Outputs ────────────────────────────────────────────────────────────────
output routeId string = botRoute.id
output originGroupId string = botOriginGroup.id
output routePatterns array = routePatterns
