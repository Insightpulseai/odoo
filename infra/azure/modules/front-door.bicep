// Azure Front Door Premium + WAF module
// Provides CDN, TLS termination, WAF, caching, and routing for Odoo services

@description('Name of the Front Door profile')
param profileName string

@description('Azure region (Front Door is always global)')
param location string = 'global'

@description('Resource tags')
param tags object

@description('Name of the WAF policy')
param wafPolicyName string

@description('Enable WAF policy association')
param enableWaf bool = true

@description('Origin groups with health probes and backend origins')
param originGroups array
// Each element: {
//   name: string
//   origins: [{ hostName: string, httpPort: int, httpsPort: int, priority: int, weight: int }]
//   healthProbePath: string
//   healthProbeProtocol: string         // 'Https' | 'Http'
//   healthProbeIntervalInSeconds: int
// }

@description('Custom domains with TLS configuration')
param customDomains array
// Each element: {
//   hostName: string
//   certificateType: string  // 'ManagedCertificate'
// }

@description('Routing rules mapping custom domains to origin groups')
param routes array
// Each element: {
//   name: string
//   customDomains: [ string ]           // hostnames to match
//   originGroupName: string
//   patternsToMatch: [ string ]
//   cacheEnabled: bool
//   cacheDuration: string               // ISO 8601 e.g. 'P30D'
//   forwardingProtocol: string          // 'HttpsOnly' | 'MatchRequest'
//   enabledState: string                // 'Enabled' | 'Disabled'
// }

// ---------------------------------------------------------------------------
// Front Door Premium profile
// ---------------------------------------------------------------------------

resource profile 'Microsoft.Cdn/profiles@2023-05-01' = {
  name: profileName
  location: location
  tags: tags
  sku: {
    name: 'Premium_AzureFrontDoor'
  }
}

// Default endpoint (the .azurefd.net hostname)
resource endpoint 'Microsoft.Cdn/profiles/afdEndpoints@2023-05-01' = {
  parent: profile
  name: '${profileName}-ep'
  location: location
  tags: tags
  properties: {
    enabledState: 'Enabled'
  }
}

// ---------------------------------------------------------------------------
// WAF policy
// ---------------------------------------------------------------------------

resource wafPolicy 'Microsoft.Network/FrontDoorWebApplicationFirewallPolicies@2022-05-01' = if (enableWaf) {
  name: wafPolicyName
  location: location
  tags: tags
  sku: {
    name: 'Premium_AzureFrontDoor'
  }
  properties: {
    policySettings: {
      enabledState: 'Enabled'
      mode: 'Prevention'
      requestBodyCheck: 'Enabled'
    }
    managedRules: {
      managedRuleSets: [
        {
          ruleSetType: 'Microsoft_DefaultRuleSet'
          ruleSetVersion: '2.1'
          ruleSetAction: 'Block'
          ruleGroupOverrides: []
          exclusions: []
        }
        {
          ruleSetType: 'Microsoft_BotManagerRuleSet'
          ruleSetVersion: '1.0'
          ruleSetAction: 'Block'
          ruleGroupOverrides: []
          exclusions: []
        }
      ]
    }
    customRules: {
      rules: [
        // Rate limit XML-RPC / JSON-RPC paths: 60 requests per minute per IP
        {
          name: 'RateLimitRpcEndpoints'
          priority: 100
          enabledState: 'Enabled'
          ruleType: 'RateLimitRule'
          rateLimitDurationInMinutes: 1
          rateLimitThreshold: 60
          action: 'Block'
          matchConditions: [
            {
              matchVariable: 'RequestUri'
              operator: 'Contains'
              matchValue: [
                '/xmlrpc/'
                '/jsonrpc'
              ]
              transforms: [
                'Lowercase'
              ]
              negateCondition: false
            }
          ]
        }
        // Block known AI crawlers by User-Agent
        {
          name: 'BlockAiCrawlers'
          priority: 200
          enabledState: 'Enabled'
          ruleType: 'MatchRule'
          action: 'Block'
          matchConditions: [
            {
              matchVariable: 'RequestHeader'
              selector: 'User-Agent'
              operator: 'Contains'
              matchValue: [
                'GPTBot'
                'CCBot'
                'Google-Extended'
                'anthropic-ai'
                'ClaudeBot'
                'Bytespider'
              ]
              transforms: []
              negateCondition: false
            }
          ]
        }
        // Allow health check paths unconditionally (bypass rate limits)
        {
          name: 'AllowHealthChecks'
          priority: 50
          enabledState: 'Enabled'
          ruleType: 'MatchRule'
          action: 'Allow'
          matchConditions: [
            {
              matchVariable: 'RequestUri'
              operator: 'Equal'
              matchValue: [
                '/health'
                '/healthz'
                '/web/health'
                '/api/health'
              ]
              transforms: [
                'Lowercase'
              ]
              negateCondition: false
            }
          ]
        }
      ]
    }
  }
}

// Associate WAF policy with the Front Door security policy
resource securityPolicy 'Microsoft.Cdn/profiles/securityPolicies@2023-05-01' = if (enableWaf) {
  parent: profile
  name: '${profileName}-waf'
  properties: {
    parameters: {
      type: 'WebApplicationFirewall'
      wafPolicy: {
        id: wafPolicy.id
      }
      associations: [
        {
          domains: [
            {
              id: endpoint.id
            }
          ]
          patternsToMatch: [
            '/*'
          ]
        }
      ]
    }
  }
}

// ---------------------------------------------------------------------------
// Origin groups (one per service type)
// ---------------------------------------------------------------------------

resource afdOriginGroups 'Microsoft.Cdn/profiles/originGroups@2023-05-01' = [
  for og in originGroups: {
    parent: profile
    name: og.name
    properties: {
      loadBalancingSettings: {
        sampleSize: 4
        successfulSamplesRequired: 3
        additionalLatencyInMilliseconds: 50
      }
      healthProbeSettings: {
        probePath: og.healthProbePath
        probeRequestType: 'HEAD'
        probeProtocol: og.healthProbeProtocol
        probeIntervalInSeconds: og.healthProbeIntervalInSeconds
      }
      sessionAffinityState: 'Disabled'
    }
  }
]

// Origins within each origin group
resource afdOrigins 'Microsoft.Cdn/profiles/originGroups/origins@2023-05-01' = [
  for (og, ogIndex) in originGroups: {
    parent: afdOriginGroups[ogIndex]
    name: '${og.name}-origin-0'
    properties: {
      hostName: og.origins[0].hostName
      httpPort: og.origins[0].httpPort
      httpsPort: og.origins[0].httpsPort
      priority: og.origins[0].priority
      weight: og.origins[0].weight
      originHostHeader: og.origins[0].hostName
      enabledState: 'Enabled'
      enforceCertificateNameCheck: true
    }
  }
]

// ---------------------------------------------------------------------------
// Custom domains (Azure-managed TLS)
// ---------------------------------------------------------------------------

resource afdCustomDomains 'Microsoft.Cdn/profiles/customDomains@2023-05-01' = [
  for cd in customDomains: {
    parent: profile
    name: replace(replace(cd.hostName, '.', '-'), '*', 'wildcard')
    properties: {
      hostName: cd.hostName
      tlsSettings: {
        certificateType: cd.certificateType
        minimumTlsVersion: 'TLS12'
      }
    }
  }
]

// ---------------------------------------------------------------------------
// Rules Engine — Security headers
// ---------------------------------------------------------------------------

resource securityHeadersRuleSet 'Microsoft.Cdn/profiles/ruleSets@2023-05-01' = {
  parent: profile
  name: 'SecurityHeaders'
}

resource ruleXFrameOptions 'Microsoft.Cdn/profiles/ruleSets/rules@2023-05-01' = {
  parent: securityHeadersRuleSet
  name: 'AddXFrameOptions'
  properties: {
    order: 1
    conditions: []
    actions: [
      {
        name: 'ModifyResponseHeader'
        parameters: {
          typeName: 'DeliveryRuleHeaderActionParameters'
          headerAction: 'Overwrite'
          headerName: 'X-Frame-Options'
          value: 'SAMEORIGIN'
        }
      }
    ]
    matchProcessingBehavior: 'Continue'
  }
}

resource ruleXContentType 'Microsoft.Cdn/profiles/ruleSets/rules@2023-05-01' = {
  parent: securityHeadersRuleSet
  name: 'AddXContentTypeOptions'
  properties: {
    order: 2
    conditions: []
    actions: [
      {
        name: 'ModifyResponseHeader'
        parameters: {
          typeName: 'DeliveryRuleHeaderActionParameters'
          headerAction: 'Overwrite'
          headerName: 'X-Content-Type-Options'
          value: 'nosniff'
        }
      }
    ]
    matchProcessingBehavior: 'Continue'
  }
}

resource ruleReferrerPolicy 'Microsoft.Cdn/profiles/ruleSets/rules@2023-05-01' = {
  parent: securityHeadersRuleSet
  name: 'AddReferrerPolicy'
  properties: {
    order: 3
    conditions: []
    actions: [
      {
        name: 'ModifyResponseHeader'
        parameters: {
          typeName: 'DeliveryRuleHeaderActionParameters'
          headerAction: 'Overwrite'
          headerName: 'Referrer-Policy'
          value: 'strict-origin-when-cross-origin'
        }
      }
    ]
    matchProcessingBehavior: 'Continue'
  }
}

// ---------------------------------------------------------------------------
// Rules Engine — Cache rules
// ---------------------------------------------------------------------------

resource cacheRuleSet 'Microsoft.Cdn/profiles/ruleSets@2023-05-01' = {
  parent: profile
  name: 'CacheRules'
}

// /web/static/* -> 30 day edge TTL, immutable
resource cacheStaticAssets 'Microsoft.Cdn/profiles/ruleSets/rules@2023-05-01' = {
  parent: cacheRuleSet
  name: 'CacheStaticAssets'
  properties: {
    order: 1
    conditions: [
      {
        name: 'UrlPath'
        parameters: {
          typeName: 'DeliveryRuleUrlPathMatchConditionParameters'
          operator: 'BeginsWith'
          matchValues: [
            '/web/static/'
          ]
          transforms: [
            'Lowercase'
          ]
          negateCondition: false
        }
      }
    ]
    actions: [
      {
        name: 'RouteConfigurationOverride'
        parameters: {
          typeName: 'DeliveryRuleRouteConfigurationOverrideActionParameters'
          cacheConfiguration: {
            isCompressionEnabled: 'Enabled'
            queryStringCachingBehavior: 'IgnoreQueryString'
            cacheBehavior: 'OverrideAlways'
            cacheDuration: '30.00:00:00'
          }
        }
      }
      {
        name: 'ModifyResponseHeader'
        parameters: {
          typeName: 'DeliveryRuleHeaderActionParameters'
          headerAction: 'Overwrite'
          headerName: 'Cache-Control'
          value: 'public, max-age=2592000, immutable'
        }
      }
    ]
    matchProcessingBehavior: 'Continue'
  }
}

// /web/image/*, /web/content/* -> 7 day edge TTL, vary on Cookie
resource cacheDynamicContent 'Microsoft.Cdn/profiles/ruleSets/rules@2023-05-01' = {
  parent: cacheRuleSet
  name: 'CacheDynamicContent'
  properties: {
    order: 2
    conditions: [
      {
        name: 'UrlPath'
        parameters: {
          typeName: 'DeliveryRuleUrlPathMatchConditionParameters'
          operator: 'BeginsWith'
          matchValues: [
            '/web/image/'
            '/web/content/'
          ]
          transforms: [
            'Lowercase'
          ]
          negateCondition: false
        }
      }
    ]
    actions: [
      {
        name: 'RouteConfigurationOverride'
        parameters: {
          typeName: 'DeliveryRuleRouteConfigurationOverrideActionParameters'
          cacheConfiguration: {
            isCompressionEnabled: 'Enabled'
            queryStringCachingBehavior: 'IgnoreQueryString'
            cacheBehavior: 'OverrideAlways'
            cacheDuration: '7.00:00:00'
          }
        }
      }
      {
        name: 'ModifyResponseHeader'
        parameters: {
          typeName: 'DeliveryRuleHeaderActionParameters'
          headerAction: 'Overwrite'
          headerName: 'Vary'
          value: 'Cookie'
        }
      }
    ]
    matchProcessingBehavior: 'Continue'
  }
}

// No-cache paths: login, session, RPC, longpolling, websocket
resource cacheBypassDynamic 'Microsoft.Cdn/profiles/ruleSets/rules@2023-05-01' = {
  parent: cacheRuleSet
  name: 'BypassCacheDynamic'
  properties: {
    order: 3
    conditions: [
      {
        name: 'UrlPath'
        parameters: {
          typeName: 'DeliveryRuleUrlPathMatchConditionParameters'
          operator: 'BeginsWith'
          matchValues: [
            '/web/login'
            '/web/session'
            '/xmlrpc/'
            '/jsonrpc'
            '/longpolling/'
            '/websocket'
          ]
          transforms: [
            'Lowercase'
          ]
          negateCondition: false
        }
      }
    ]
    actions: [
      {
        name: 'RouteConfigurationOverride'
        parameters: {
          typeName: 'DeliveryRuleRouteConfigurationOverrideActionParameters'
          cacheConfiguration: {
            cacheBehavior: 'HonorOrigin'
            isCompressionEnabled: 'Disabled'
            queryStringCachingBehavior: 'UseQueryString'
          }
        }
      }
      {
        name: 'ModifyResponseHeader'
        parameters: {
          typeName: 'DeliveryRuleHeaderActionParameters'
          headerAction: 'Overwrite'
          headerName: 'Cache-Control'
          value: 'no-store, no-cache, must-revalidate'
        }
      }
    ]
    matchProcessingBehavior: 'Continue'
  }
}

// Default: no cache (order 4, catch-all)
resource cacheDefaultNoCache 'Microsoft.Cdn/profiles/ruleSets/rules@2023-05-01' = {
  parent: cacheRuleSet
  name: 'DefaultNoCache'
  properties: {
    order: 4
    conditions: []
    actions: [
      {
        name: 'RouteConfigurationOverride'
        parameters: {
          typeName: 'DeliveryRuleRouteConfigurationOverrideActionParameters'
          cacheConfiguration: {
            cacheBehavior: 'HonorOrigin'
            isCompressionEnabled: 'Enabled'
            queryStringCachingBehavior: 'UseQueryString'
          }
        }
      }
    ]
    matchProcessingBehavior: 'Continue'
  }
}

// ---------------------------------------------------------------------------
// Rules Engine — WebSocket support
// ---------------------------------------------------------------------------

resource websocketRuleSet 'Microsoft.Cdn/profiles/ruleSets@2023-05-01' = {
  parent: profile
  name: 'WebSocketSupport'
}

resource websocketRoute 'Microsoft.Cdn/profiles/ruleSets/rules@2023-05-01' = {
  parent: websocketRuleSet
  name: 'EnableWebSocket'
  properties: {
    order: 1
    conditions: [
      {
        name: 'UrlPath'
        parameters: {
          typeName: 'DeliveryRuleUrlPathMatchConditionParameters'
          operator: 'BeginsWith'
          matchValues: [
            '/websocket'
            '/longpolling/'
          ]
          transforms: [
            'Lowercase'
          ]
          negateCondition: false
        }
      }
    ]
    actions: [
      {
        name: 'RouteConfigurationOverride'
        parameters: {
          typeName: 'DeliveryRuleRouteConfigurationOverrideActionParameters'
          cacheConfiguration: {
            cacheBehavior: 'HonorOrigin'
            isCompressionEnabled: 'Disabled'
            queryStringCachingBehavior: 'UseQueryString'
          }
        }
      }
    ]
    matchProcessingBehavior: 'Stop'
  }
}

// ---------------------------------------------------------------------------
// Routes (derived from parameter)
// ---------------------------------------------------------------------------

resource afdRoutes 'Microsoft.Cdn/profiles/afdEndpoints/routes@2023-05-01' = [
  for route in routes: {
    parent: endpoint
    name: route.name
    properties: {
      customDomains: [
        for domainHost in route.customDomains: {
          id: resourceId('Microsoft.Cdn/profiles/customDomains', profileName, replace(replace(domainHost, '.', '-'), '*', 'wildcard'))
        }
      ]
      originGroup: {
        id: resourceId('Microsoft.Cdn/profiles/originGroups', profileName, route.originGroupName)
      }
      originPath: contains(route, 'originPath') ? route.originPath : null
      patternsToMatch: route.patternsToMatch
      forwardingProtocol: route.forwardingProtocol
      linkToDefaultDomain: 'Enabled'
      httpsRedirect: 'Enabled'
      enabledState: route.enabledState
      cacheConfiguration: route.cacheEnabled ? {
        cacheBehavior: 'OverrideAlways'
        cacheDuration: route.cacheDuration
        isCompressionEnabled: 'Enabled'
        queryStringCachingBehavior: 'IgnoreQueryString'
      } : null
      ruleSets: [
        {
          id: securityHeadersRuleSet.id
        }
        {
          id: cacheRuleSet.id
        }
        {
          id: websocketRuleSet.id
        }
      ]
    }
    dependsOn: [
      afdOriginGroups
      afdCustomDomains
    ]
  }
]

// ---------------------------------------------------------------------------
// Outputs
// ---------------------------------------------------------------------------

output profileName string = profile.name
output profileId string = profile.id
output endpointHostName string = endpoint.properties.hostName
output wafPolicyId string = enableWaf ? wafPolicy.id : ''
