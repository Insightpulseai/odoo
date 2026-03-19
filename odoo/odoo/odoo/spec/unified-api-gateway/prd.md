# Unified API Gateway — Product Requirements Document

> PRD for the InsightPulseAI Unified API Gateway.
> Constitution: `spec/unified-api-gateway/constitution.md`

---

## 1. Problem

The InsightPulseAI platform exposes multiple unrelated integration surfaces:

- Odoo XML-RPC/JSON-RPC on `erp.insightpulseai.com`
- Supabase PostgREST and Edge Functions on their own endpoints
- n8n webhook URLs for automation triggers
- Foundry agent endpoints (emerging)

Each surface has its own auth model, versioning (or lack thereof), and audit posture.
External integrators must discover and authenticate against multiple origins.
Authority boundaries are implicit — nothing prevents a consumer from writing
ERP data through a Supabase function or triggering business mutations via n8n.
There is no unified rate limiting, no cross-service audit trail, and no
deprecation contract.

## 2. Solution

A single governed API surface at `api.insightpulseai.com` that:

- Routes requests to bounded domain APIs based on path prefix
- Enforces authentication, rate limiting, and audit logging at the edge
- Preserves authority boundaries — each route group maps to one owner system
- Provides versioned endpoints with a deprecation contract
- Runs on Azure APIM behind Azure Front Door

The gateway is a routing and policy layer. It does not merge backends,
transform payloads, or execute business logic.

## 3. Users

| Consumer | Auth Model | Use Case |
|----------|-----------|----------|
| External integrators | OAuth2/JWT (Entra ID) | ERP data reads, invoice submission, project queries |
| Internal cross-service | Managed identity | Service-to-service calls (e.g., Foundry reading ERP state) |
| AI agents (Foundry) | Managed identity + scoped tokens | Tool orchestration, ERP actions, control plane reads |
| CI/CD pipelines | API keys (subscription keys) | Deployment hooks, health checks, sync triggers |

## 4. Route Taxonomy

### `/api/v1/erp/*` — ERP Domain (Odoo)

- Invoices, projects, tasks, approvals, finance, contacts
- Proxied to Odoo JSON-RPC, translated to REST at gateway or adapter layer
- Write operations require ERP-scoped OAuth2 claims

### `/api/v1/control/*` — Control Plane (Supabase)

- Feature flags, agent registry, sync state, app configuration
- Proxied to Supabase PostgREST / Edge Functions
- Write operations require control-plane-scoped claims

### `/api/v1/agents/*` — Agent Runtime (Foundry)

- Conversations, sessions, tool orchestration, evaluations
- Proxied to Foundry agent endpoints
- Write operations require agent-scoped claims

### `/api/v1/docs/*` — Documentation (Plane / Repo-derived)

- Spec indexes, runbook metadata, plan summaries
- Read-only gateway — no write operations exposed
- Cached with moderate TTL (5-15 minutes)

### `/api/v1/integrations/*` — Orchestration (n8n triggers)

- Webhook intake, sync kickoff, callbacks
- Trigger-only — initiates workflows in owner systems
- Never performs authoritative writes directly
- Write-back happens in the owner system, not at this layer

## 5. Authority Matrix

| Route Group | Owner | Write Authority | Read Authority | Forbidden | Audit |
|-------------|-------|----------------|----------------|-----------|-------|
| `/api/v1/erp/*` | Odoo | Odoo only | Odoo, cached | Supabase/Foundry writes | Required |
| `/api/v1/control/*` | Supabase | Supabase only | Supabase | Odoo writes | Required |
| `/api/v1/agents/*` | Foundry | Foundry only | Foundry | Direct DB writes | Required |
| `/api/v1/docs/*` | Plane | Read-only gateway | Plane/repo | Gateway writes | Optional |
| `/api/v1/integrations/*` | Orchestration | Trigger only | Status only | Business writes | Required |

**Enforcement**: APIM policies validate that request method + route group + consumer
identity conform to the authority matrix. Forbidden operations return `403` with
a structured error body referencing the constitution rule violated.

## 6. Auth Model

### External Consumers (OAuth2/JWT)

- Token issuer: Entra ID (tenant: InsightPulseAI)
- Scopes: `erp.read`, `erp.write`, `control.read`, `agents.invoke`, etc.
- Token validation at APIM inbound policy
- Refresh token flow for long-lived integrations

### Service-to-Service (Managed Identity)

- Azure Managed Identity assigned to each Container App
- APIM validates identity claims against route-group ACL
- No shared secrets — identity-based auth only

### CI/CD (API Keys)

- APIM subscription keys, rotated via Key Vault
- Scoped to specific route groups (e.g., CI key can only hit `/integrations/*`)
- Rate-limited separately from human consumers

## 7. Non-Goals

- **Not replacing UI surfaces** — `erp.insightpulseai.com` remains the Odoo UI.
  The gateway serves programmatic integration, not browser traffic.
- **Not merging backends** — No cross-domain joins, no composite APIs,
  no data aggregation layer.
- **Not making n8n authoritative** — n8n triggers actions. Owner systems
  execute and persist. n8n never holds authoritative state.
- **Not building a custom gateway** — Azure APIM is the runtime.
  No bespoke proxy code.

## 8. Success Criteria

| Criterion | Measure |
|-----------|---------|
| Single entrypoint | All external API traffic routes through `api.insightpulseai.com` |
| Authority preserved | No cross-domain write violations in audit logs (30-day window) |
| Clear ownership | Every route group has declared owner in APIM configuration |
| Auth coverage | 100% of routes require authentication (no anonymous endpoints) |
| Audit coverage | All required-audit routes emit structured logs to Azure Monitor |
| Migration path | Existing integrations have documented migration to gateway routes |
| Versioning | All routes use `/v1/` prefix; deprecation headers functional |

## 9. Dependencies

| Dependency | Status | Required For |
|-----------|--------|-------------|
| Azure Front Door (`ipai-fd-dev`) | Exists | TLS termination, edge routing |
| Azure APIM | New — provision required | Policy enforcement, rate limiting, subscriptions |
| Azure Key Vault (`kv-ipai-dev`) | Exists | Secret references for backend credentials |
| Entra ID | Exists | OAuth2 token issuance and validation |
| Azure Monitor / Log Analytics | Exists | Audit logging, distributed tracing |
| DNS: `api.insightpulseai.com` | New — CNAME to Front Door | Public entrypoint |

## 10. Rollout Phases

| Phase | Scope | Gate |
|-------|-------|------|
| P0 | APIM provisioned, `api.*` DNS live, health probe responds | Infra validated |
| P1 | `/api/v1/erp/*` routes active (read-only), auth enforced | ERP reads verified |
| P2 | All route groups active, write operations enabled | Authority matrix enforced |
| P3 | External consumer onboarding, legacy direct-access sunset | Migration complete |

---

*Spec: `spec/unified-api-gateway/`*
*Constitution: `spec/unified-api-gateway/constitution.md`*
*Last updated: 2026-03-13*
