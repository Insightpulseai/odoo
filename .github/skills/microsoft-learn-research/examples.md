# microsoft-learn-research -- Worked Examples

## Example 1: Query Construction Progression (Good vs Bad)

Bad queries (too vague -- returns generic architecture overview):
```
microsoft_docs_search("azure networking")
microsoft_docs_search("postgresql security")
microsoft_docs_search("foundry agents")
```

Good queries (specific service + feature + action):
```
microsoft_docs_search("Azure PostgreSQL Flexible Server disable public network access VNet")
microsoft_docs_search("Azure AI Foundry Agent Service Python SDK v2 create agent thread run")
microsoft_docs_search("Azure Container Apps liveness readiness startup probe Bicep configuration")
```

Better queries (add context to narrow results):
```
microsoft_docs_search("Azure PostgreSQL Flexible Server VNet integration delegated subnet private DNS zone Bicep")
microsoft_docs_search("Azure AI Foundry SDK v2 AIProjectClient DefaultAzureCredential migration from_connection_string")
microsoft_docs_search("Azure Container Apps minReplicas zero cold start Odoo production scaling")
```

## Example 2: Full Research Session -- ACA Startup Probe

```
Goal: Determine correct startup probe settings for Odoo 18 on ACA.

Query 1: microsoft_docs_search("Azure Container Apps health probes startup liveness readiness configuration")
Result:
  - Three probe types: Startup, Liveness, Readiness.
  - Startup probe: gates liveness/readiness until passes. Recommended for slow-init apps.
  - failureThreshold * periodSeconds = total startup window.
  - Default timeout: 1s. Recommended for Odoo: 5s (some endpoints are slow).
  - Probe path must return HTTP 200.

Query 2: microsoft_docs_search("Odoo health check endpoint web")
Result: Odoo 18 exposes /web/health endpoint returning HTTP 200 JSON.
  Use /web/health for all three probe types.

Query 3: microsoft_code_sample_search("bicep container app startup probe http", language="bicep")
Result:
  probes: [
    {
      type: 'Startup'
      httpGet: { path: '/health', port: 8080, scheme: 'HTTP' }
      initialDelaySeconds: 10
      periodSeconds: 10
      timeoutSeconds: 5
      failureThreshold: 30    // 300s total budget
    }
  ]

Conclusion: Set failureThreshold: 30, periodSeconds: 10 for 300s startup window.
Use /web/health on port 8069. Cite source in Bicep comment.
```

Applied in Bicep:
```bicep
// Source: microsoft_docs_search("Azure Container Apps health probes startup configuration")
// Odoo 18 /web/health returns 200. 300s startup window = 30 * 10s.
probes: [
  {
    type: 'Startup'
    httpGet: { path: '/web/health', port: 8069, scheme: 'HTTP' }
    initialDelaySeconds: 30
    periodSeconds: 10
    timeoutSeconds: 5
    failureThreshold: 30
  }
]
```

## Example 3: `microsoft_docs_fetch` for Complete Parameter Reference

When a search result mentions a page but doesn't include the full parameter table:

```
Step 1: microsoft_docs_search("Azure PostgreSQL Flexible Server minimalTlsVersion parameter values")
Result: References https://learn.microsoft.com/en-us/azure/templates/microsoft.dbforpostgresql/flexibleservers
        but doesn't show all enum values.

Step 2: microsoft_docs_fetch("https://learn.microsoft.com/en-us/azure/templates/microsoft.dbforpostgresql/flexibleservers")
Result: Full ARM/Bicep resource definition.
        minimalTlsVersion: 'TLS1_0' | 'TLS1_1' | 'TLS1_2' | 'TLSEnforcementDisabled'
        Recommendation: 'TLS1_2' (TLS 1.0 and 1.1 are deprecated per MSFT security baseline).

Applied: Set minimalTlsVersion: 'TLS1_2' in postgres-flexible.bicep.
Cite: # Source: microsoft_docs_fetch(arm-template-ref) -- TLS1_2 is minimum per MSFT security baseline.
```

## Example 4: Handling Insufficient MCP Results

```
Goal: Find the correct API for disabling Foundry content filters via Python SDK.

Query: microsoft_docs_search("Azure AI Foundry content filter disable Python SDK API")
Result: Returns general content safety documentation but no SDK API reference.

Query: microsoft_code_sample_search("azure ai foundry content filter python", language="python")
Result: Returns Azure AI Content Safety standalone SDK, not Foundry agent filter config.

Conclusion: MCP returned insufficient results for this query.

Evidence entry:
  BLOCKED: MCP returned insufficient results for
  "Azure AI Foundry content filter disable Python SDK API".
  Fallback: Check Azure AI Studio > Content Filters UI for current configuration.
  Document the current state manually in ssot/agent-platform/content_filters.yaml.
  Re-query after next Microsoft Learn docs update (check monthly).
```
