# Unified API Gateway -- Target State

> **SUPERSEDED** by [`API_LAYER_DOCTRINE.md`](API_LAYER_DOCTRINE.md) (2026-04-10).
> This document references Supabase, n8n, APIM Consumption tier, and Odoo CE 19 — all deprecated or changed.
> Retained for historical context only. Do not implement from this document.
>
> SSOT: `ssot/api/unified-api-gateway.yaml`
> Status: ~~Planning~~ **Superseded**
> Last updated: 2026-03-13

---

## 1. Overview

The InsightPulseAI platform comprises multiple bounded systems -- Odoo CE 19 (ERP),
Supabase (control plane), Azure Foundry (agent runtime), Plane (work management),
and n8n (orchestration) -- each currently exposed on separate subdomains behind
Azure Front Door.

This document defines the target state: a **single governed API surface** at
`api.insightpulseai.com`, fronted by Azure API Management (APIM) behind
Azure Front Door. The gateway routes to bounded domain APIs, enforces consistent
authentication, rate limiting, versioning, and audit logging -- while preserving
each system's authority over its own domain.

UI surfaces (erp, plane, superset, auth) remain on their existing subdomains.
Only programmatic API access consolidates behind the gateway.

---

## 2. Architecture Diagram

```
+------------------------------------------------------+
|                  External Consumers                   |
|    (integrators, agents, CI/CD, mobile apps)          |
+---------------------+--------------------------------+
                      | HTTPS
                      v
            api.insightpulseai.com
                      |
+---------------------+--------------------------------+
|            Azure Front Door (ipai-fd-dev)              |
|   TLS termination . WAF . geo-routing . caching       |
+---------------------+--------------------------------+
                      |
+---------------------+--------------------------------+
|         Azure API Management (Consumption)            |
|   OAuth2/JWT . API keys . rate limits . audit logs    |
|   correlation IDs . versioning . policy enforcement   |
+----------+----------+----------+----------+----------+
| /erp/*   |/control/*|/agents/* | /docs/*  |/integr/* |
| Odoo     |Supabase  |Foundry   |Plane/repo|n8n       |
+----------+----------+----------+----------+----------+
      |          |          |          |          |
      v          v          v          v          v
  ACA:odoo   Supabase   Foundry   ACA:plane   n8n
  (JSON-RPC) (PostgREST) (Agent)  (REST)     (webhook)
```

---

## 3. Route Taxonomy

| Route Group    | Prefix               | Backing System | Purpose                          | Examples                                      | Auth            | Methods                    |
|----------------|-----------------------|----------------|----------------------------------|-----------------------------------------------|-----------------|----------------------------|
| ERP            | `/api/v1/erp`        | Odoo CE 19     | Business data CRUD               | `/erp/invoices`, `/erp/projects`, `/erp/tasks` | OAuth2 / JWT    | GET, POST, PUT, PATCH, DELETE |
| Control Plane  | `/api/v1/control`    | Supabase       | Platform config, agent registry  | `/control/config`, `/control/agent-registry`   | OAuth2 / JWT    | GET, POST, PATCH           |
| Agents         | `/api/v1/agents`     | Azure Foundry  | Agent conversations, sessions    | `/agents/conversations`, `/agents/evaluations` | OAuth2 / JWT    | GET, POST                  |
| Docs           | `/api/v1/docs`       | Plane          | Specs, runbooks (read-only)      | `/docs/specs`, `/docs/runbooks`                | API Key / JWT   | GET                        |
| Integrations   | `/api/v1/integrations`| n8n           | Webhooks, sync triggers          | `/integrations/webhooks`, `/integrations/sync` | API Key / JWT   | POST                       |

---

## 4. Authority Matrix

| Domain       | Authoritative System | Writable via Gateway | Read-only via Gateway | Forbidden Operations                        | Audit Level |
|--------------|----------------------|----------------------|-----------------------|---------------------------------------------|-------------|
| ERP          | Odoo                 | Yes                  | No                    | Supabase writes, Foundry writes, direct DB  | Full        |
| Control      | Supabase             | Yes                  | No                    | Odoo writes, direct DB access               | Full        |
| Agents       | Foundry              | Yes                  | No                    | Direct DB writes, Odoo writes               | Full        |
| Docs         | Plane                | No                   | Yes                   | Any writes via gateway                      | Metadata    |
| Integrations | n8n                  | No (trigger only)    | No                    | Business state writes, direct data mutations | Full        |

**Key principle**: Each system is authoritative for its domain. The gateway never
becomes the source of truth -- it is a routing, policy, and observability layer.

---

## 5. Security and Identity

### External consumers

- **Primary**: OAuth2 (Microsoft Entra ID) with JWT bearer tokens
- **Secondary**: API keys for CI/CD pipelines and machine consumers
- **Token validation**: APIM validates JWT signature, audience, and expiry
- **Scopes**: Per route group (`erp.read`, `erp.write`, `agents.invoke`, etc.)

### Service-to-service

- **Managed identity**: Azure Container Apps use managed identity for APIM backend calls
- **No shared secrets**: Services authenticate to each other via managed identity or Entra ID tokens
- **Supabase service role**: Used only by APIM backend policy, never exposed to consumers

### Secrets management

- All secrets in Azure Key Vault (`kv-ipai-dev`)
- No secrets in Odoo database
- No secrets in repository
- APIM Named Values reference Key Vault entries

### Role mapping

| Route Group    | Required Role / Scope      |
|----------------|----------------------------|
| `/erp/*`       | `erp.read`, `erp.write`    |
| `/control/*`   | `control.read`, `control.write` |
| `/agents/*`    | `agents.invoke`            |
| `/docs/*`      | `docs.read`                |
| `/integrations/*` | `integrations.trigger`  |

---

## 6. Versioning Model

- **Format**: URL-based -- `/api/v1/...`, `/api/v2/...`
- **Current**: v1 (initial)
- **Compatibility**: Additive changes only within a version (new fields, new endpoints)
- **Breaking changes**: Require a new version number
- **Deprecation**: 90-day notice period with `Sunset` header on deprecated version
- **Discovery**: `GET /api/versions` returns supported versions and sunset dates
- **Header-based versioning**: Not used (URL-based is the only mechanism)

---

## 7. Observability

### Telemetry

- **Application Insights**: APIM diagnostic settings emit to a shared App Insights instance
- **Correlation IDs**: Every request receives an `X-Correlation-ID` header (propagated to backends)
- **Request/response logging**: Enabled with secret redaction (Authorization headers, API keys stripped)

### Rate limiting

- **Standard tier**: 100 req/min per consumer (ERP, Control, Docs)
- **Elevated tier**: 200 req/min per consumer (Agents -- higher due to streaming)
- **Strict tier**: 30 req/min per consumer (Integrations -- webhook triggers)
- **Relaxed tier**: 300 req/min per consumer (Docs read-only)
- Metrics exported per consumer identity

### Health endpoints

| Endpoint                        | Purpose                     |
|---------------------------------|-----------------------------|
| `/api/health`                   | Gateway-level health        |
| `/api/v1/erp/health`            | Odoo backend health         |
| `/api/v1/control/health`        | Supabase backend health     |
| `/api/v1/agents/health`         | Foundry backend health      |
| `/api/v1/docs/health`           | Plane backend health        |
| `/api/v1/integrations/health`   | n8n backend health          |

---

## 8. Current Surface Migration Map

| Current Hostname               | Current Role              | Target State                              | Notes                                     |
|--------------------------------|---------------------------|-------------------------------------------|-------------------------------------------|
| `erp.insightpulseai.com`       | Odoo UI + JSON-RPC API    | UI surface only; API via gateway           | JSON-RPC passthrough or REST adapter TBD  |
| `auth.insightpulseai.com`      | Keycloak SSO              | Identity provider; not routed via gateway  | Tokens validated by APIM, not proxied     |
| `mcp.insightpulseai.com`       | MCP runtime               | Evaluate: gateway inclusion or separate    | MCP protocol may need dedicated transport |
| `n8n.insightpulseai.com`       | n8n UI + webhooks         | UI stays; webhooks via `/integrations/*`   | Internal orchestration preserved          |
| `plane.insightpulseai.com`     | Plane UI                  | UI surface only; docs API via gateway      | Read-only summaries through gateway       |
| Supabase (hosted)              | Control plane + Edge Fns  | Internal; control API via gateway          | PostgREST subset exposed, not full access |
| `ops.insightpulseai.com`       | Internal admin console    | Not exposed via API gateway                | Internal-only, no external consumers      |
| `crm.insightpulseai.com`       | CRM (alias for ERP)       | Evaluate deprecation                       | Redundant with `erp` subdomain            |
| `superset.insightpulseai.com`  | BI dashboards             | UI surface only; not exposed via gateway   | Embed tokens handled separately           |
| `ocr.insightpulseai.com`       | Document OCR service      | Evaluate: gateway inclusion for API calls  | May become `/api/v1/erp/documents/ocr`    |

---

## 9. DNS Model

### Add

| Record | Type  | Target            | Purpose                    |
|--------|-------|--------------------|----------------------------|
| `api`  | CNAME | Azure Front Door   | Canonical API entrypoint   |

### Keep as UI surfaces

- `erp.insightpulseai.com` -- Odoo web interface
- `auth.insightpulseai.com` -- Keycloak login pages
- `plane.insightpulseai.com` -- Plane project management UI
- `superset.insightpulseai.com` -- Apache Superset dashboards
- `ocr.insightpulseai.com` -- OCR service (evaluate gateway migration)

### Evaluate

- `mcp.insightpulseai.com` -- MCP uses a distinct protocol (stdio/SSE). Separate transport
  may be more appropriate than HTTP API gateway subpath.
- `crm.insightpulseai.com` -- Currently an alias for ERP. If no distinct CRM service exists,
  deprecate in favor of `erp.insightpulseai.com`.

### Deprecate for programmatic access

Direct service origins (`.azurecontainerapps.io` FQDNs) should not be used for
external programmatic access once the gateway is operational. Internal
service-to-service traffic may continue to use direct origins.

---

## 10. Open Decisions

| # | Decision                                        | Options                                             | Impact   |
|---|-------------------------------------------------|------------------------------------------------------|----------|
| 1 | Azure APIM tier                                 | Consumption (pay-per-call) vs Standard v2 (reserved) | Cost, SLA |
| 2 | MCP traffic routing                             | Subpath of unified API vs separate MCP endpoint      | Protocol compatibility |
| 3 | Plane docs exposure                             | Proxy live Plane API vs serve static summaries        | Freshness vs complexity |
| 4 | Odoo API transport                              | JSON-RPC passthrough vs thin REST adapter             | Developer experience |
| 5 | Foundry agent access                            | Direct proxy vs mediated control service              | Security boundary |
| 6 | Supabase PostgREST exposure                     | Expose curated subset vs wrap entirely in Edge Fns    | Attack surface |
| 7 | OCR service placement                           | Standalone route group vs ERP subpath                 | Authority clarity |
| 8 | Rate limit enforcement                          | APIM-only vs APIM + per-backend limits                | Defense in depth |

Each decision will be resolved as a numbered ADR in `docs/architecture/decisions/`
before implementation of the corresponding migration phase.

---

## References

- SSOT (machine-readable): `ssot/api/unified-api-gateway.yaml`
- Infrastructure: `infra/azure/modules/aca-odoo-services.bicep`
- DNS registry: `infra/dns/subdomain-registry.yaml`
- Front Door config: Azure resource `ipai-fd-dev`
- Platform SSOT rules: `.claude/rules/ssot-platform.md`
