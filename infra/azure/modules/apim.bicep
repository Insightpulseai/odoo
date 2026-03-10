// Azure API Management — Consumption tier module
// Routes traffic to Container Apps backends (Foundry, Odoo, n8n)

@description('Name of the APIM instance')
param apimName string

@description('Azure region')
param location string

@description('Resource tags')
param tags object

@description('Publisher contact email (required by APIM)')
param publisherEmail string

@description('Publisher organization name')
param publisherName string = 'InsightPulse AI'

@description('Base FQDN of the Container Apps environment (e.g. myenv.region.azurecontainerapps.io)')
param containerAppsEnvironmentFqdn string

@description('Key Vault name for named value references')
param keyVaultName string

@description('Enable Application Insights diagnostics')
param enableApplicationInsights bool = true

@description('Application Insights resource ID (required when enableApplicationInsights is true)')
param applicationInsightsId string = ''

// ---------------------------------------------------------------------------
// APIM Instance — Consumption SKU (pay-per-call, no idle cost)
// ---------------------------------------------------------------------------

resource apim 'Microsoft.ApiManagement/service@2023-03-01-preview' = {
  name: apimName
  location: location
  tags: tags
  sku: {
    name: 'Consumption'
    capacity: 0
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    publisherEmail: publisherEmail
    publisherName: publisherName
  }
}

// ---------------------------------------------------------------------------
// Named Values
// ---------------------------------------------------------------------------

resource namedValueBackendBaseUrl 'Microsoft.ApiManagement/service/namedValues@2023-03-01-preview' = {
  parent: apim
  name: 'backend-base-url'
  properties: {
    displayName: 'backend-base-url'
    value: 'https://${containerAppsEnvironmentFqdn}'
    secret: false
  }
}

// ---------------------------------------------------------------------------
// Global Policy — CORS, rate-limit, JWT validation placeholder
// ---------------------------------------------------------------------------

resource globalPolicy 'Microsoft.ApiManagement/service/policies@2023-03-01-preview' = {
  parent: apim
  name: 'policy'
  properties: {
    format: 'rawxml'
    value: '''<policies>
  <inbound>
    <!-- CORS — allow the SPA and internal callers -->
    <cors allow-credentials="true">
      <allowed-origins>
        <origin>https://erp.insightpulseai.com</origin>
        <origin>https://ops.insightpulseai.com</origin>
        <origin>http://localhost:3000</origin>
      </allowed-origins>
      <allowed-methods preflight-result-max-age="300">
        <method>GET</method>
        <method>POST</method>
        <method>PUT</method>
        <method>PATCH</method>
        <method>DELETE</method>
        <method>OPTIONS</method>
      </allowed-methods>
      <allowed-headers>
        <header>Authorization</header>
        <header>Content-Type</header>
        <header>X-Requested-With</header>
      </allowed-headers>
    </cors>

    <!-- Rate limit: 100 calls / 60 seconds per subscription key -->
    <rate-limit calls="100" renewal-period="60" />

    <!-- JWT validation placeholder — uncomment and configure when IdP is ready
    <validate-jwt header-name="Authorization" require-scheme="Bearer"
                  failed-validation-httpcode="401"
                  failed-validation-error-message="Unauthorized">
      <openid-config url="https://login.microsoftonline.com/{tenant-id}/v2.0/.well-known/openid-configuration" />
      <audiences>
        <audience>api://{client-id}</audience>
      </audiences>
      <issuers>
        <issuer>https://login.microsoftonline.com/{tenant-id}/v2.0</issuer>
      </issuers>
    </validate-jwt>
    -->
  </inbound>
  <backend>
    <forward-request />
  </backend>
  <outbound />
  <on-error>
    <base />
  </on-error>
</policies>'''
  }
}

// ---------------------------------------------------------------------------
// Backends — Container Apps services
// ---------------------------------------------------------------------------

resource backendFoundry 'Microsoft.ApiManagement/service/backends@2023-03-01-preview' = {
  parent: apim
  name: 'foundry-mcp-adapter'
  properties: {
    description: 'Foundry MCP Adapter on Container Apps'
    url: 'https://foundry-mcp-adapter.${containerAppsEnvironmentFqdn}'
    protocol: 'http'
    tls: {
      validateCertificateChain: true
      validateCertificateName: true
    }
  }
}

resource backendOdoo 'Microsoft.ApiManagement/service/backends@2023-03-01-preview' = {
  parent: apim
  name: 'odoo-business-api'
  properties: {
    description: 'Odoo CE 19 Business API on Container Apps'
    url: 'https://odoo.${containerAppsEnvironmentFqdn}'
    protocol: 'http'
    tls: {
      validateCertificateChain: true
      validateCertificateName: true
    }
  }
}

resource backendN8n 'Microsoft.ApiManagement/service/backends@2023-03-01-preview' = {
  parent: apim
  name: 'n8n-gateway'
  properties: {
    description: 'n8n Workflow Automation on Container Apps'
    url: 'https://n8n.${containerAppsEnvironmentFqdn}'
    protocol: 'http'
    tls: {
      validateCertificateChain: true
      validateCertificateName: true
    }
  }
}

// ---------------------------------------------------------------------------
// API Definitions
// ---------------------------------------------------------------------------

resource apiFoundry 'Microsoft.ApiManagement/service/apis@2023-03-01-preview' = {
  parent: apim
  name: 'foundry-mcp-adapter'
  properties: {
    displayName: 'Foundry MCP Adapter'
    description: 'Palantir Foundry integration via MCP adapter'
    path: 'foundry'
    protocols: [ 'https' ]
    subscriptionRequired: true
    serviceUrl: 'https://foundry-mcp-adapter.${containerAppsEnvironmentFqdn}'
    apiType: 'http'
  }
}

resource apiFoundryPolicy 'Microsoft.ApiManagement/service/apis/policies@2023-03-01-preview' = {
  parent: apiFoundry
  name: 'policy'
  properties: {
    format: 'rawxml'
    value: '''<policies>
  <inbound>
    <base />
    <set-backend-service backend-id="foundry-mcp-adapter" />
  </inbound>
  <backend>
    <base />
  </backend>
  <outbound>
    <base />
  </outbound>
  <on-error>
    <base />
  </on-error>
</policies>'''
  }
  dependsOn: [ backendFoundry ]
}

resource apiOdoo 'Microsoft.ApiManagement/service/apis@2023-03-01-preview' = {
  parent: apim
  name: 'odoo-business-api'
  properties: {
    displayName: 'Odoo Business API'
    description: 'Odoo CE 19 ERP business endpoints'
    path: 'odoo'
    protocols: [ 'https' ]
    subscriptionRequired: true
    serviceUrl: 'https://odoo.${containerAppsEnvironmentFqdn}'
    apiType: 'http'
  }
}

resource apiOdooPolicy 'Microsoft.ApiManagement/service/apis/policies@2023-03-01-preview' = {
  parent: apiOdoo
  name: 'policy'
  properties: {
    format: 'rawxml'
    value: '''<policies>
  <inbound>
    <base />
    <set-backend-service backend-id="odoo-business-api" />
  </inbound>
  <backend>
    <base />
  </backend>
  <outbound>
    <base />
  </outbound>
  <on-error>
    <base />
  </on-error>
</policies>'''
  }
  dependsOn: [ backendOdoo ]
}

resource apiN8n 'Microsoft.ApiManagement/service/apis@2023-03-01-preview' = {
  parent: apim
  name: 'n8n-gateway'
  properties: {
    displayName: 'n8n Workflow Gateway'
    description: 'n8n automation webhook and API gateway'
    path: 'n8n'
    protocols: [ 'https' ]
    subscriptionRequired: true
    serviceUrl: 'https://n8n.${containerAppsEnvironmentFqdn}'
    apiType: 'http'
  }
}

resource apiN8nPolicy 'Microsoft.ApiManagement/service/apis/policies@2023-03-01-preview' = {
  parent: apiN8n
  name: 'policy'
  properties: {
    format: 'rawxml'
    value: '''<policies>
  <inbound>
    <base />
    <set-backend-service backend-id="n8n-gateway" />
  </inbound>
  <backend>
    <base />
  </backend>
  <outbound>
    <base />
  </outbound>
  <on-error>
    <base />
  </on-error>
</policies>'''
  }
  dependsOn: [ backendN8n ]
}

// ---------------------------------------------------------------------------
// Application Insights Logger (conditional)
// ---------------------------------------------------------------------------

resource appInsightsLogger 'Microsoft.ApiManagement/service/loggers@2023-03-01-preview' = if (enableApplicationInsights && applicationInsightsId != '') {
  parent: apim
  name: 'application-insights'
  properties: {
    loggerType: 'applicationInsights'
    resourceId: applicationInsightsId
    credentials: {
      instrumentationKey: '{{appinsights-instrumentation-key}}'
    }
  }
}

resource diagnosticSettings 'Microsoft.ApiManagement/service/diagnostics@2023-03-01-preview' = if (enableApplicationInsights && applicationInsightsId != '') {
  parent: apim
  name: 'applicationinsights'
  properties: {
    loggerId: appInsightsLogger.id
    alwaysLog: 'allErrors'
    sampling: {
      samplingType: 'fixed'
      percentage: 100
    }
    frontend: {
      request: {
        body: {
          bytes: 1024
        }
      }
      response: {
        body: {
          bytes: 1024
        }
      }
    }
    backend: {
      request: {
        body: {
          bytes: 1024
        }
      }
      response: {
        body: {
          bytes: 1024
        }
      }
    }
  }
}

// ---------------------------------------------------------------------------
// Key Vault access — allow APIM managed identity to read secrets
// ---------------------------------------------------------------------------

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
}

@description('RBAC: APIM managed identity gets Key Vault Secrets User role')
resource kvRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, apim.id, 'Key Vault Secrets User')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6') // Key Vault Secrets User
    principalId: apim.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// ---------------------------------------------------------------------------
// Outputs
// ---------------------------------------------------------------------------

@description('APIM instance name')
output apimName string = apim.name

@description('APIM gateway URL (e.g. https://<name>.azure-api.net)')
output apimGatewayUrl string = apim.properties.gatewayUrl

@description('APIM resource ID')
output apimId string = apim.id

@description('APIM system-assigned managed identity principal ID')
output apimPrincipalId string = apim.identity.principalId
