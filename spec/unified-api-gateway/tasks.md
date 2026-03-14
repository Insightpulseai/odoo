# Tasks -- Unified API Gateway

> Spec: `spec/unified-api-gateway/`
> Tracks: `plan.md` phases 1-8
> Date: 2026-03-13

---

## Phase 1: Inventory

- [ ] Catalog `erp.insightpulseai.com` public endpoints (JSON-RPC, REST, web controllers)
- [ ] Catalog `auth.insightpulseai.com` public endpoints (Keycloak OIDC, admin)
- [ ] Catalog `crm.insightpulseai.com` public endpoints
- [ ] Catalog `mcp.insightpulseai.com` public endpoints (MCP coordination API)
- [ ] Catalog `n8n.insightpulseai.com` webhook and API endpoints
- [ ] Catalog `plane.insightpulseai.com` API endpoints
- [ ] Catalog Supabase Edge Function endpoints (`spdtwktxdalcfigzeqrz`)
- [ ] Catalog `ops.insightpulseai.com` endpoints
- [ ] Document current auth pattern per service (session, JWT, API key, none)
- [ ] Map DNS CNAME -> Front Door -> ACA origin for each service
- [ ] Produce `spec/unified-api-gateway/endpoint-inventory.yaml`

## Phase 2: Authority Classification

- [ ] Assign each endpoint to a route group (`/erp`, `/control`, `/agents`, `/docs`, `/integrations`)
- [ ] Define owner and write authority per route group
- [ ] Define read authority and cross-read permissions
- [ ] Identify and document forbidden cross-write patterns
- [ ] Flag dual-role endpoints (browser + API) for split handling
- [ ] Produce `spec/unified-api-gateway/authority-map.yaml`

## Phase 3: Gateway Route Map

- [ ] Design APIM API definition for `/api/v1/erp` (Odoo JSON-RPC proxy)
- [ ] Design APIM API definition for `/api/v1/control` (Supabase PostgREST + Edge Functions)
- [ ] Design APIM API definition for `/api/v1/agents` (Foundry Agent Service) **[BLOCKED: Foundry endpoint TBD]**
- [ ] Design APIM API definition for `/api/v1/docs` (Plane API) **[BLOCKED: Plane API routing]**
- [ ] Design APIM API definition for `/api/v1/integrations` (n8n webhooks)
- [ ] Define backend pool mappings (APIM backend -> ACA internal FQDN)
- [ ] Design inbound auth policies (OAuth2, JWT, managed identity, API key, HMAC)
- [ ] Design rate limiting tiers (strict: 30/min, standard: 100/min, elevated: 200/min, relaxed: 300/min)
- [ ] Design correlation ID propagation policy (`X-Request-ID` header)
- [ ] Write APIM policy XML templates to `infra/azure/apim/policies/`

## Phase 4: DNS + Ingress

- [ ] Add `api` subdomain to `infra/dns/subdomain-registry.yaml`
- [ ] Run `scripts/dns/generate-dns-artifacts.sh` and commit generated files
- [ ] Write Bicep module `infra/azure/modules/apim.bicep` (Consumption tier)
- [ ] Configure Front Door routing rule: `api.insightpulseai.com/*` -> APIM origin
- [ ] Provision Front Door managed TLS certificate for `api.insightpulseai.com`
- [ ] Validate end-to-end connectivity: consumer -> Front Door -> APIM -> ACA backend

## Phase 5: Consumer Migration

- [ ] Inventory all direct consumers of service origin FQDNs (CI pipelines, n8n, external)
- [ ] Write consumer migration guide with old -> new endpoint mapping
- [ ] Implement HTTP 301 redirects on direct service origins for API paths
- [ ] Issue APIM subscription keys to authorized consumers
- [ ] Monitor gateway adoption percentage via APIM analytics dashboard

## Phase 6: Deprecate Direct Access

- [ ] Add `Deprecation` and `Sunset` HTTP headers to direct service API responses
- [ ] Update all CI/CD workflows to use `api.insightpulseai.com` endpoints
- [ ] Update n8n workflow webhook URLs to gateway endpoints
- [ ] Restrict ACA ingress to internal-only for API paths (UI paths unchanged)
- [ ] Verify UI domains (`erp.*`, `plane.*`, `superset.*`) remain unaffected

## Phase 7: Policy + Observability

- [ ] Enable APIM diagnostic logging to Log Analytics workspace
- [ ] Configure Application Insights integration with 10% sampling
- [ ] Implement per-consumer rate limiting via APIM subscription policies
- [ ] Enable Front Door WAF custom rules for API-specific patterns
- [ ] Build Log Analytics query dashboard for API traffic metrics
- [ ] Validate correlation ID propagation end-to-end across all backends

## Phase 8: Operationalize

- [ ] Publish OpenAPI 3.x spec for each route group in APIM developer portal
- [ ] Document API products, subscription tiers, and consumer onboarding flow
- [ ] Configure Azure Monitor alerts (error rate > 5%, P95 latency > 2s)
- [ ] Conduct security review of APIM policies and auth token flows
- [ ] Create `docs/contracts/API_GATEWAY_CONTRACT.md`
- [ ] Register contract in `docs/contracts/PLATFORM_CONTRACTS_INDEX.md`
