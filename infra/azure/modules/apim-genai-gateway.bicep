// ==========================================================================
// APIM GenAI Gateway — Pulser Supervisor Front Door
// ==========================================================================
//
// Purpose:
//   Azure API Management AI Gateway in front of pulser_supervisor (A2A server).
//   Provides: rate limiting, semantic caching, cost cap, policy enforcement,
//   Entra token validation, tenant routing.
//
// Authority:
//   - CLAUDE.md Cross-Repo Invariant #10a (three-protocol model)
//   - docs/architecture/three-protocol-model.md (APIM position in stack)
//   - ssot/governance/reference-samples-register.yaml (custom-engine-agent-apim-genai-gateway)
//
// Status: SKELETON — needs filling in during Phase 2 build. Schema + structure
//         are canonical; values are placeholders tagged with TODO(phase2).
//
// Reference sample:
//   https://github.com/OfficeDev/microsoft-365-agents-toolkit-samples/tree/main/
//     custom-engine-agent-apim-genai-gateway-ts
//
// Rev: 2026-04-15 — initial skeleton landing as part of codification pass
// ==========================================================================

@description('Environment (dev/staging/prod) — maps to ACA revision + Foundry backing')
param environment string = 'dev'

@description('Azure region (must match ipai-copilot-resource region for latency)')
param location string = 'eastus2'

@description('APIM instance SKU. Developer for dev/staging; Premium v2 for prod.')
@allowed([ 'Developer', 'Basic', 'Standard', 'StandardV2', 'Premium', 'PremiumV2' ])
param apimSku string = 'StandardV2'

@description('Backing supervisor ACA FQDN (pulser-supervisor agent)')
param supervisorBackendFqdn string

@description('Managed identity resource id granting APIM → Foundry access')
param managedIdentityId string

@description('Key Vault URI for secrets (zero hardcoded)')
param keyVaultUri string

@description('Application Insights connection string for observability')
param appInsightsConnectionString string

@description('Azure OpenAI / Foundry endpoint for Semantic Kernel cache + model routing')
param foundryEndpoint string

// --------------------------------------------------------------------------
// APIM resource
// --------------------------------------------------------------------------
resource apim 'Microsoft.ApiManagement/service@2024-05-01' = {
  name: 'apim-ipai-${environment}-genai'
  location: location
  sku: {
    name: apimSku
    capacity: 1
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
  properties: {
    publisherEmail: 'platform-engineering@insightpulseai.com'
    publisherName: 'InsightPulse AI'
    // TODO(phase2): configure virtual network integration, custom domains,
    // TLS certs from Key Vault
  }
}

// --------------------------------------------------------------------------
// Pulser Supervisor API — A2A entry point
// --------------------------------------------------------------------------
resource supervisorApi 'Microsoft.ApiManagement/service/apis@2024-05-01' = {
  parent: apim
  name: 'pulser-supervisor-a2a'
  properties: {
    displayName: 'Pulser Supervisor (A2A)'
    path: 'pulser/a2a'
    protocols: [ 'https' ]
    serviceUrl: 'https://${supervisorBackendFqdn}'
    subscriptionRequired: true
    // TODO(phase2): import OpenAPI spec for supervisor A2A endpoints
    // (message/send, message/stream, tasks/get, tasks/cancel, /.well-known/agent-card.json)
  }
}

// --------------------------------------------------------------------------
// GenAI Gateway policies (inbound)
//   1. Entra JWT validation (Agent365 tokens + MI tokens + client tokens)
//   2. Per-tenant rate limit (header x-tenant-id)
//   3. Cost cap (daily $ per tenant, computed from Foundry usage headers)
//   4. Semantic cache (cache completions by prompt hash)
//   5. Prompt-injection pre-filter (Content Safety)
//   6. Tenant → Foundry deployment routing
//   7. Retry + circuit breaker on backend
// --------------------------------------------------------------------------
resource supervisorApiPolicy 'Microsoft.ApiManagement/service/apis/policies@2024-05-01' = {
  parent: supervisorApi
  name: 'policy'
  properties: {
    format: 'xml'
    value: '''
<policies>
  <inbound>
    <base />
    <!-- 1. Entra JWT validation -->
    <validate-jwt header-name="Authorization" failed-validation-httpcode="401">
      <openid-config url="https://login.microsoftonline.com/{{tenant-id}}/v2.0/.well-known/openid-configuration" />
      <required-claims>
        <claim name="aud">
          <value>api://pulser-supervisor</value>
        </claim>
      </required-claims>
    </validate-jwt>

    <!-- 2. Per-tenant rate limit (200 rpm dev, 2000 rpm prod) -->
    <rate-limit-by-key calls="200" renewal-period="60"
                        counter-key="@(context.Request.Headers.GetValueOrDefault("x-tenant-id","anonymous"))" />

    <!-- 3. Cost cap placeholder — TODO(phase2): implement via custom-policy + App Insights query -->
    <!-- <cost-cap tenant-header="x-tenant-id" daily-usd-limit="200" /> -->

    <!-- 4. Semantic cache — TODO(phase2): azure-openai-semantic-cache-lookup -->
    <!-- <azure-openai-semantic-cache-lookup
            embeddings-backend-id="embedding-backend"
            embeddings-backend-auth="system-assigned"
            score-threshold="0.95" /> -->

    <!-- 5. Content Safety pre-filter — TODO(phase2): call azure-ai-content-safety -->

    <!-- 6. Tenant → Foundry deployment routing -->
    <set-backend-service base-url="https://{{supervisor-backend-fqdn}}" />

    <!-- 7. Propagate trace context -->
    <set-header name="traceparent" exists-action="append">
      <value>@(context.RequestId)</value>
    </set-header>
  </inbound>

  <backend>
    <retry condition="@(context.Response.StatusCode >= 500 && context.Response.StatusCode < 600)"
           count="2"
           interval="1"
           max-interval="10"
           delta="1">
      <forward-request />
    </retry>
  </backend>

  <outbound>
    <base />
    <!-- Semantic cache store — TODO(phase2): azure-openai-semantic-cache-store -->
    <!-- Cost telemetry emit to App Insights -->
    <log-to-eventhub logger-id="appinsights-logger">@{
      return new JObject(
        new JProperty("tenant", context.Request.Headers.GetValueOrDefault("x-tenant-id","anonymous")),
        new JProperty("workflow_id", context.Request.Headers.GetValueOrDefault("x-workflow-id","")),
        new JProperty("latency_ms", context.Elapsed.TotalMilliseconds),
        new JProperty("status", context.Response.StatusCode)
      ).ToString();
    }</log-to-eventhub>
  </outbound>

  <on-error>
    <base />
  </on-error>
</policies>
'''
  }
}

// --------------------------------------------------------------------------
// Named values (secrets pulled from Key Vault, never inline)
// --------------------------------------------------------------------------
resource namedValueTenantId 'Microsoft.ApiManagement/service/namedValues@2024-05-01' = {
  parent: apim
  name: 'tenant-id'
  properties: {
    displayName: 'tenant-id'
    keyVault: {
      secretIdentifier: '${keyVaultUri}secrets/entra-tenant-id'
      identityClientId: managedIdentityId
    }
    secret: true
  }
}

resource namedValueSupervisorFqdn 'Microsoft.ApiManagement/service/namedValues@2024-05-01' = {
  parent: apim
  name: 'supervisor-backend-fqdn'
  properties: {
    displayName: 'supervisor-backend-fqdn'
    value: supervisorBackendFqdn
  }
}

// --------------------------------------------------------------------------
// Outputs
// --------------------------------------------------------------------------
output apimResourceId string = apim.id
output apimGatewayUrl string = apim.properties.gatewayUrl
output supervisorApiPath string = '${apim.properties.gatewayUrl}/${supervisorApi.properties.path}'
output agentCardUrl string = '${apim.properties.gatewayUrl}/${supervisorApi.properties.path}/.well-known/agent-card.json'
