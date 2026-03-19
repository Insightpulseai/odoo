# Implementation Plan -- Unified API Gateway

> Spec: `spec/unified-api-gateway/`
> Status: Draft
> Owner: Platform Engineering
> Date: 2026-03-13

---

## Context

InsightPulseAI runs Odoo CE 19, Supabase, and Azure Foundry agents on Azure
Container Apps behind Azure Front Door (`ipai-fd-dev`). Each service currently
exposes its own origin FQDN directly. There is no unified API surface for
programmatic consumers, no centralized auth enforcement, and no cross-service
rate limiting or audit trail.

This plan introduces **Azure API Management (APIM)** as a single gateway that
sits behind the existing Front Door, consolidating all programmatic access
under `api.insightpulseai.com`.

---

## Gateway Choice

**Azure APIM -- Consumption tier** (initial), migrating to **Standard v2** when
sustained traffic exceeds Consumption limits (~1M calls/month threshold).

Rationale:
- Native integration with Azure Front Door, Container Apps, and Managed Identity
- Built-in OAuth2 validation, rate limiting, and request/response transformation
- Application Insights integration for end-to-end tracing
- Developer portal for API documentation and key management
- No additional networking infrastructure required -- APIM connects to ACA
  internal FQDNs via VNet integration

---

## Architecture

```
External Consumer
    |
    v
api.insightpulseai.com (DNS -- Cloudflare CNAME)
    |
    v
Azure Front Door (TLS termination, WAF, edge caching)
    |
    v
Azure APIM (auth, routing, rate limits, audit logging)
    |--- /api/v1/erp/*          -> ipai-odoo-dev-web.internal (ACA)
    |--- /api/v1/control/*      -> Supabase PostgREST / Edge Functions
    |--- /api/v1/agents/*       -> Foundry Agent Service endpoint
    |--- /api/v1/docs/*         -> Plane API / static repo content
    '--- /api/v1/integrations/* -> n8n webhook endpoints
```

UI domains (`erp.insightpulseai.com`, `plane.insightpulseai.com`, etc.) remain
unchanged and continue routing through Front Door directly to their ACA origins.
The gateway handles **programmatic/API traffic only**.

---

## Route Groups

| Route Group        | Backend Origin                        | Auth Model                  | Write Authority       |
|--------------------|---------------------------------------|-----------------------------|-----------------------|
| `/api/v1/erp`      | Odoo JSON-RPC / REST (ACA)           | OAuth2 bearer + session     | Odoo (exclusive)      |
| `/api/v1/control`  | Supabase PostgREST + Edge Functions  | Supabase JWT                | Supabase (exclusive)  |
| `/api/v1/agents`   | Foundry Agent Service                | Managed Identity + API key  | Foundry (exclusive)   |
| `/api/v1/docs`     | Plane API + static content           | API key                     | Plane (exclusive)     |
| `/api/v1/integrations` | n8n webhook endpoints            | HMAC signature              | n8n (exclusive)       |

**Cross-write rule**: No route group may write to another group's backing store.
Reads may cross boundaries via explicit APIM policies.

---

## Migration Phases

### Phase 1 -- Inventory (Week 1)

- Catalog all public endpoints across: erp, auth, crm, mcp, n8n, plane,
  supabase, ops
- Document current authentication pattern per service (session cookie, JWT,
  API key, unauthenticated)
- Map current DNS CNAME -> Front Door -> ACA origin relationships
- Identify endpoints that are programmatic-only vs browser-facing
- Produce endpoint inventory as `spec/unified-api-gateway/endpoint-inventory.yaml`

### Phase 2 -- Authority Classification (Week 1-2)

- Assign each cataloged endpoint to one of the five route groups
- Define owner, write authority, and read authority per route
- Identify forbidden cross-writes and document enforcement rules
- Flag endpoints that serve dual roles (browser + API) for special handling
- Produce authority map as `spec/unified-api-gateway/authority-map.yaml`

### Phase 3 -- Gateway Route Map (Week 2-3)

- Design APIM API definitions for each route group
- Define backend pool mappings (APIM backend entity -> ACA internal FQDN)
- Design inbound auth policies: OAuth2 validation, Supabase JWT validation,
  managed identity passthrough, API key validation, HMAC verification
- Design rate limiting tiers: free (100 req/min), standard (1000 req/min),
  internal (10000 req/min)
- Design request/response transformation policies (header injection,
  correlation ID propagation, response envelope)
- Produce APIM policy XML templates in `infra/azure/apim/policies/`

### Phase 4 -- DNS + Ingress (Week 3)

- Add `api` subdomain entry to `infra/dns/subdomain-registry.yaml`
- Run `scripts/dns/generate-dns-artifacts.sh` to regenerate Terraform vars
- Configure Front Door routing rule: `api.insightpulseai.com/*` -> APIM origin
- TLS certificate: Front Door managed certificate for `api.insightpulseai.com`
- Deploy APIM instance via Bicep (`infra/azure/modules/apim.bicep`)
- Validate end-to-end connectivity: consumer -> Front Door -> APIM -> ACA

### Phase 5 -- Consumer Migration (Week 4-6)

- Identify all current direct consumers of service origin FQDNs
- Provide migration documentation with new unified endpoint patterns
- Implement backward-compatible HTTP 301 redirects where feasible
- Publish APIM subscription keys to authorized consumers
- Monitor adoption metrics via APIM built-in analytics
- Target: 80% of programmatic traffic routed through gateway by end of phase

### Phase 6 -- Deprecate Direct Access (Week 6-8)

- Add `Deprecation` and `Sunset` headers to direct service API responses
- Enforce gateway-only access for all programmatic consumers
- Keep UI domains (`erp.*`, `plane.*`, `superset.*`) unchanged
- Update all CI/CD pipelines and integration tests to use gateway URLs
- Update n8n workflow webhook URLs to gateway endpoints
- Remove direct API access from ACA ingress rules (internal-only)

### Phase 7 -- Policy + Observability (Week 8-10)

- Enable full request/response logging in APIM diagnostic settings
- Configure Application Insights integration with sampling policy
- Implement per-consumer rate limiting via APIM subscription tiers
- Enable WAF custom rules on Front Door for API-specific threat patterns
- Implement correlation ID propagation (`X-Request-ID`) across all backends
- Set up Log Analytics workspace queries for API traffic dashboards

### Phase 8 -- Operationalize (Week 10-12)

- Publish OpenAPI 3.x specs per route group in APIM developer portal
- Document API products, subscriptions, and onboarding flow
- Set up Azure Monitor alerts: error rate > 5%, P95 latency > 2s,
  rate limit breaches
- Conduct security review of APIM policies and auth flows
- Update platform contracts: `docs/contracts/API_GATEWAY_CONTRACT.md`
- Register contract in `docs/contracts/PLATFORM_CONTRACTS_INDEX.md`

---

## Dependencies

| Dependency                     | Status      | Blocker? |
|--------------------------------|-------------|----------|
| Azure Front Door (`ipai-fd-dev`) | Deployed  | No       |
| ACA internal FQDNs reachable   | Deployed    | No       |
| Cloudflare DNS delegation      | Active      | No       |
| Azure APIM resource provider   | Available   | No       |
| Supabase JWT validation keys   | Accessible  | No       |
| Foundry Agent Service endpoint | In progress | Phase 3  |

---

## Risk Register

| Risk                                         | Mitigation                                        |
|----------------------------------------------|---------------------------------------------------|
| Consumption tier cold-start latency (~1-2s)  | Accept for initial phase; upgrade to Standard v2  |
| Double-hop latency (Front Door -> APIM -> ACA) | Benchmark; bypass Front Door cache for API calls |
| Consumer migration resistance                | Backward-compatible redirects + deprecation window |
| APIM policy complexity drift                 | Store policies as code in `infra/azure/apim/`     |
| Supabase JWT validation in APIM              | Custom policy with JWKS endpoint caching          |

---

## Success Criteria

1. All programmatic API traffic routes through `api.insightpulseai.com`
2. No direct service origin access for API consumers (UI domains unaffected)
3. Centralized auth enforcement with zero unauthenticated API access
4. Sub-500ms P95 gateway overhead (APIM processing time)
5. Full request audit trail in Application Insights
6. Published OpenAPI specs for all five route groups
