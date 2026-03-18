# API DNS and Ingress Contract

> **Contract ID**: C-API-DNS-01
> **Status**: Active
> **Created**: 2026-03-13
> **Scope**: Unified API Gateway -- DNS record, hostname classification, ingress flow

---

## 1. New DNS Record

The Unified API Gateway introduces a single new DNS record:

| Subdomain | Type | Target | Purpose |
|-----------|------|--------|---------|
| `api.insightpulseai.com` | CNAME | Azure Front Door endpoint (`ipai-fd-dev-ep-*.azurefd.net`) | Canonical API entrypoint |

**Provisioning workflow** (per SSOT platform rules):

1. Add record to `infra/dns/subdomain-registry.yaml`
2. Run `scripts/dns/generate-dns-artifacts.sh`
3. Commit all generated artifacts together
4. CI (`dns-ssot-apply.yml`) applies via Terraform on merge to main

No manual Cloudflare dashboard or API changes. YAML-first only.

---

## 2. Hostname Classification

| Hostname | Type | Target State | Notes |
|----------|------|-------------|-------|
| `api.insightpulseai.com` | API gateway | **NEW** -- canonical API entrypoint | All programmatic consumers use this |
| `erp.insightpulseai.com` | UI surface | Keep -- Odoo web UI only | Browser access to Odoo; not for API consumers |
| `auth.insightpulseai.com` | Identity | Keep -- Keycloak SSO | Not routed via API gateway; direct Front Door origin |
| `n8n.insightpulseai.com` | UI surface | Keep -- n8n editor UI | Webhooks route via `/api/v1/integrations/*` instead |
| `plane.insightpulseai.com` | UI surface | Keep -- Plane web UI | Read summaries available via `/api/v1/docs/*` |
| `superset.insightpulseai.com` | UI surface | Keep -- Superset BI dashboards | Dashboard access only; data via gateway |
| `ocr.insightpulseai.com` | Service | Keep -- OCR service | Evaluate gateway routing in future phase |
| `mcp.insightpulseai.com` | Runtime | Evaluate -- MCP protocol | MCP uses non-HTTP transport; may need separate handling |
| `crm.insightpulseai.com` | Alias | Evaluate -- potentially redundant | CRM is an Odoo module; may redirect to `erp` |
| `ops.insightpulseai.com` | Admin | Keep -- internal admin console | Restricted access; not exposed via API gateway |

---

## 3. Ingress Flow

```
Client
  |
  v
api.insightpulseai.com (DNS: Cloudflare CNAME)
  |
  v
Azure Front Door (ipai-fd-dev)
  - TLS termination (managed certificate)
  - WAF policy enforcement
  - Geo-routing (Southeast Asia primary)
  |
  v
Azure API Management (APIM)
  - JWT / API key validation
  - Route matching to backend pool
  - Rate limit enforcement
  - Request/response transformation
  - Audit logging
  |
  v
Backend Azure Container App (internal FQDN)
  - ipai-odoo-dev-web (ERP routes)
  - Supabase PostgREST (Control routes)
  - Azure AI Foundry (Agent routes)
  - Plane API (Docs routes)
  - n8n webhook (Integration routes)
```

**Key properties**:
- Front Door terminates TLS. Backend traffic is internal (ACA environment network).
- APIM is deployed within the ACA environment for low-latency backend access.
- Backend services are not publicly accessible -- only via Front Door + APIM.
- Health probes: Front Door probes APIM `/status` endpoint. APIM probes each backend `/health`.

---

## 4. Rules

1. **All new programmatic API consumers MUST use `api.insightpulseai.com`**.
   Direct service origin URLs (`*.thankfulbush-*.azurecontainerapps.io`) are for
   internal routing only and must not be shared with consumers.

2. **Direct service hostnames are for UI/browser access only**.
   `erp.insightpulseai.com`, `n8n.insightpulseai.com`, etc. serve web UIs.
   API integrations must not use these hostnames.

3. **No new CNAME records for API-only purposes**.
   New API surface areas are added as route groups under `api.insightpulseai.com`,
   not as new subdomains. This prevents hostname sprawl.

4. **DNS changes follow YAML-first workflow**.
   Per SSOT platform rules: edit `infra/dns/subdomain-registry.yaml`, run generator,
   commit artifacts, CI applies. No Cloudflare dashboard or direct API changes.

5. **TLS certificates are Front Door-managed**.
   No manual certificate provisioning. Front Door auto-provisions and renews certificates
   for all custom domains via ACME.

---

## 5. Migration Path

Existing integrations that call backend services directly (e.g., Odoo JSON-RPC on
`erp.insightpulseai.com:8069`) will be migrated to gateway routes in phases:

| Phase | Scope | Timeline |
|-------|-------|----------|
| P0 | New consumers use gateway only | Immediate |
| P1 | Agent and integration consumers migrated | 30 days |
| P2 | Legacy Odoo JSON-RPC consumers migrated | 60 days |
| P3 | Direct backend access restricted to internal only | 90 days |

---

*Governed by: `infra/dns/subdomain-registry.yaml`, `docs/contracts/DNS_EMAIL_CONTRACT.md`*
