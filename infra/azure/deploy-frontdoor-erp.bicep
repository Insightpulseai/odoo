// Deploy Azure Front Door for erp.insightpulseai.com
// Phase 1: Single subdomain (erp) → ipai-odoo-dev-web ACA origin
// Includes: WAF (DefaultRuleSet 2.1 + BotManager), security headers, Odoo cache rules
//
// Usage:
//   az deployment group create \
//     --resource-group rg-ipai-dev-odoo-runtime \
//     --template-file infra/azure/deploy-frontdoor-erp.bicep

targetScope = 'resourceGroup'

module frontDoor 'modules/front-door.bicep' = {
  name: 'frontdoor-erp-deploy'
  params: {
    profileName: 'afd-ipai-dev'
    wafPolicyName: 'wafipaidev'
    enableWaf: true
    tags: {
      environment: 'dev'
      project: 'insightpulseai'
      managedBy: 'bicep'
      phase: '1'
    }
    originGroups: [
      {
        name: 'og-odoo-erp'
        healthProbePath: '/web/health'
        healthProbeProtocol: 'Https'
        healthProbeIntervalInSeconds: 30
        origins: [
          {
            hostName: 'ipai-odoo-dev-web.salmontree-b7d27e19.southeastasia.azurecontainerapps.io'
            httpPort: 80
            httpsPort: 443
            priority: 1
            weight: 1000
          }
        ]
      }
    ]
    customDomains: [
      {
        hostName: 'erp.insightpulseai.com'
        certificateType: 'ManagedCertificate'
      }
    ]
    routes: [
      {
        name: 'route-erp'
        customDomains: [
          'erp.insightpulseai.com'
        ]
        originGroupName: 'og-odoo-erp'
        patternsToMatch: [
          '/*'
        ]
        forwardingProtocol: 'HttpsOnly'
        enabledState: 'Enabled'
        cacheEnabled: false
        cacheDuration: 'P0D'
      }
    ]
  }
}

output endpointHostName string = frontDoor.outputs.endpointHostName
output profileName string = frontDoor.outputs.profileName
output wafPolicyId string = frontDoor.outputs.wafPolicyId
