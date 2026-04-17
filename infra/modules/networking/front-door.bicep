// modules/networking/front-door.bicep
// Creates: afd-ipai-prd (Azure Front Door Standard)
//          WAF policy: DefaultRuleSet 2.1 + BotManager 1.0
// erp.insightpulseai.com → AFD → ACA odoo-web origin
// HTTPS-only; HTTP → HTTPS redirect
targetScope = 'resourceGroup'

param prefix     string
param env        string
param location   string   // 'global' — AFD is a global resource
param tags       object
param odoeFqdn   string   // ACA odoo-web FQDN from container-apps module

var afdName        = 'afd-${prefix}-${env}'
var wafPolicyName  = 'waf${prefix}${env}'
var originGroupName = 'og-odoo'
var originName      = 'or-odoo-aca'
var routeName       = 'rt-odoo'
var endpointName    = 'ep-${prefix}-odoo-${env}'

// ── WAF Policy ────────────────────────────────────────────────
// Prevention mode; DefaultRuleSet 2.1 + BotManager 1.0
resource wafPolicy 'Microsoft.Network/frontDoorWebApplicationFirewallPolicies@2024-02-01' = {
  name:     wafPolicyName
  location: 'global'
  tags:     tags
  sku: { name: 'Standard_AzureFrontDoor' }
  properties: {
    policySettings: {
      enabledState:     'Enabled'
      mode:             'Prevention'     // Not Detection — enforce blocks
      redirectUrl:      null
      customBlockResponseStatusCode: 403
      customBlockResponseBody:       null
      requestBodyCheck: 'Enabled'
    }
    managedRules: {
      managedRuleSets: [
        {
          ruleSetType:    'DefaultRuleSet'
          ruleSetVersion: '2.1'
          ruleSetAction:  'Block'
          exclusions: [
            // Odoo chat message body exclusion (WAF tuning — T-006)
            {
              matchVariable:         'RequestBodyPostArgNames'
              selectorMatchOperator: 'Equals'
              selector:              'message'
            }
            {
              matchVariable:         'RequestBodyPostArgNames'
              selectorMatchOperator: 'Equals'
              selector:              'arch'
            }
          ]
          ruleGroupOverrides: []
        }
        {
          ruleSetType:    'Microsoft_BotManagerRuleSet'
          ruleSetVersion: '1.0'
          ruleSetAction:  'Block'
          exclusions:     []
          ruleGroupOverrides: []
        }
      ]
    }
    customRules: {
      rules: [
        // Rate limit: max 100 req/min per IP (protect Odoo login endpoint)
        {
          name:         'RateLimitOdooLogin'
          priority:     100
          enabledState: 'Enabled'
          ruleType:     'RateLimitRule'
          rateLimitDurationInMinutes: 1
          rateLimitThreshold: 100
          matchConditions: [{
            matchVariable:   'RequestUri'
            operator:        'Contains'
            negateCondition: false
            matchValue:      ['/web/login', '/web/session/authenticate']
          }]
          action: 'Block'
        }
      ]
    }
  }
}

// ── Azure Front Door Profile ───────────────────────────────────
resource afd 'Microsoft.Cdn/profiles@2024-09-01' = {
  name:     afdName
  location: 'global'
  tags:     tags
  sku: { name: 'Standard_AzureFrontDoor' }
  properties: {}
}

// ── Endpoint ──────────────────────────────────────────────────
resource endpoint 'Microsoft.Cdn/profiles/afdEndpoints@2024-09-01' = {
  name:   endpointName
  parent: afd
  location: 'global'
  properties: {
    enabledState: 'Enabled'
  }
}

// ── Origin Group ──────────────────────────────────────────────
resource originGroup 'Microsoft.Cdn/profiles/originGroups@2024-09-01' = {
  name:   originGroupName
  parent: afd
  properties: {
    loadBalancingSettings: {
      sampleSize:                 4
      successfulSamplesRequired:  3
      additionalLatencyInMilliseconds: 50
    }
    healthProbeSettings: {
      probePath:          '/web/health'
      probeRequestType:   'HEAD'
      probeProtocol:      'Https'
      probeIntervalInSeconds: 30
    }
    sessionAffinityState:       'Enabled'   // Odoo requires sticky sessions
    trafficRestorationTimeInMinutes: 2
  }
}

// ── Origin (ACA odoo-web) ────────────────────────────────────
resource origin 'Microsoft.Cdn/profiles/originGroups/origins@2024-09-01' = {
  name:   originName
  parent: originGroup
  properties: {
    hostName:              odoeFqdn
    httpPort:              80
    httpsPort:             443
    originHostHeader:      odoeFqdn
    priority:              1
    weight:                1000
    enabledState:          'Enabled'
    enforceCertificateNameCheck: true
  }
}

// ── Security Policy (WAF association) ────────────────────────
resource securityPolicy 'Microsoft.Cdn/profiles/securityPolicies@2024-09-01' = {
  name:   'sp-waf-${prefix}-${env}'
  parent: afd
  properties: {
    parameters: {
      type: 'WebApplicationFirewall'
      wafPolicy: {
        id: wafPolicy.id
      }
      associations: [{
        domains: [{ id: endpoint.id }]
        patternsToMatch: ['/*']
      }]
    }
  }
}

// ── Route: HTTPS + HTTP→HTTPS redirect ───────────────────────
resource route 'Microsoft.Cdn/profiles/afdEndpoints/routes@2024-09-01' = {
  name:   routeName
  parent: endpoint
  properties: {
    originGroup:         { id: originGroup.id }
    originPath:          null
    ruleSets:            []
    supportedProtocols:  ['Http', 'Https']
    patternsToMatch:     ['/*']
    forwardingProtocol:  'HttpsOnly'
    linkToDefaultDomain: 'Enabled'
    httpsRedirect:       'Enabled'
    enabledState:        'Enabled'
    cacheConfiguration: null     // Odoo is dynamic — no CDN caching
  }
  dependsOn: [origin, securityPolicy]
}

// ── Custom domain: erp.insightpulseai.com ────────────────────
// After deploy: create CNAME erp.insightpulseai.com → AFD endpoint FQDN
// in Azure DNS zone insightpulseai.com
resource customDomain 'Microsoft.Cdn/profiles/customDomains@2024-09-01' = {
  name:   'erp-insightpulseai-com'
  parent: afd
  properties: {
    hostName:       'erp.insightpulseai.com'
    tlsSettings: {
      certificateType:    'ManagedCertificate'   // AFD-managed TLS — auto-renewal
      minimumTlsVersion:  'TLS12'
    }
    azureDnsZone: null  // Set if Azure DNS zone is in scope; else manual CNAME
  }
}

resource routeCustomDomain 'Microsoft.Cdn/profiles/afdEndpoints/routes@2024-09-01' = {
  name:   '${routeName}-custom'
  parent: endpoint
  properties: {
    originGroup:        { id: originGroup.id }
    customDomains:      [{ id: customDomain.id }]
    ruleSets:           []
    supportedProtocols: ['Https']
    patternsToMatch:    ['/*']
    forwardingProtocol: 'HttpsOnly'
    httpsRedirect:      'Enabled'
    enabledState:       'Enabled'
    cacheConfiguration: null
  }
  dependsOn: [route, customDomain]
}

// ── Outputs ────────────────────────────────────────────────────
output afdEndpointFqdn  string = endpoint.properties.hostName
output afdProfileName   string = afd.name
output afdResourceId    string = afd.id
output wafPolicyId      string = wafPolicy.id
output customDomainValidation string = customDomain.properties.validationProperties.validationToken
