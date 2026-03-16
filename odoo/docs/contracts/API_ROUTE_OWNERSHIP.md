# API Route Ownership Contract

> **Contract ID**: C-API-ROUTES-01
> **Status**: Active
> **Created**: 2026-03-13
> **Scope**: Unified API Gateway -- route prefix ownership, methods, auth, and rate limits

---

## 1. Purpose

Define explicit ownership for every route group exposed by the Unified API Gateway at
`api.insightpulseai.com`. Each route prefix maps to exactly one backing service with
declared methods, auth requirements, rate limits, and forbidden patterns.

---

## 2. Route Groups

### 2.1 `/api/v1/erp/*` -- Odoo ERP

| Property | Value |
|----------|-------|
| **Owner** | Odoo (ERP team) |
| **Backing service** | `ipai-odoo-dev-web` via ACA internal FQDN |
| **Allowed methods** | GET, POST, PUT, PATCH, DELETE |
| **Auth** | OAuth2 (Azure Entra ID) -- required |
| **Rate limit tier** | Standard (60 req/min, burst 100) |
| **Example resources** | `/api/v1/erp/invoices`, `/api/v1/erp/projects`, `/api/v1/erp/tasks`, `/api/v1/erp/purchase-orders`, `/api/v1/erp/approvals` |
| **Forbidden** | Direct SQL queries, bypassing Odoo ORM, bulk DELETE without scope restriction |

**Notes**: All requests are translated to Odoo JSON-RPC calls at the APIM policy layer.
Response format is normalized to REST-style JSON (not raw JSON-RPC envelopes).

---

### 2.2 `/api/v1/control/*` -- Supabase Control Plane

| Property | Value |
|----------|-------|
| **Owner** | Platform team (Supabase) |
| **Backing service** | Supabase PostgREST (`spdtwktxdalcfigzeqrz`) |
| **Allowed methods** | GET, POST, PATCH |
| **Auth** | OAuth2 or API key -- required |
| **Rate limit tier** | Standard (60 req/min, burst 100) |
| **Example resources** | `/api/v1/control/feature-flags`, `/api/v1/control/agent-registry`, `/api/v1/control/sync-state`, `/api/v1/control/app-config` |
| **Forbidden** | Schema mutations via gateway, direct PostgREST admin endpoints, DELETE operations (append-only policy) |

**Notes**: POST creates new records. PATCH updates existing records. No DELETE -- control
plane data is append-only per `SSOT_BOUNDARIES.md`.

---

### 2.3 `/api/v1/agents/*` -- Azure Foundry

| Property | Value |
|----------|-------|
| **Owner** | AI/Agent team (Foundry) |
| **Backing service** | Azure AI Foundry endpoint |
| **Allowed methods** | GET, POST |
| **Auth** | OAuth2 (Azure Entra ID) -- required |
| **Rate limit tier** | Elevated (30 req/min, burst 50) |
| **Example resources** | `/api/v1/agents/conversations`, `/api/v1/agents/sessions/{id}/messages`, `/api/v1/agents/evaluations`, `/api/v1/agents/tools` |
| **Forbidden** | Direct model access, unbounded streaming without timeout, PUT/PATCH/DELETE (conversations are immutable once created) |

**Notes**: Agent conversations can be long-running. APIM policy enforces a 120-second
gateway timeout with streaming support. Conversation state is owned by Foundry -- summaries
may be synced to Supabase via declared sync contract.

---

### 2.4 `/api/v1/docs/*` -- Plane / Repo (Read-Only)

| Property | Value |
|----------|-------|
| **Owner** | Platform team (Plane + repo-derived) |
| **Backing service** | Plane API + static repo content |
| **Allowed methods** | GET only |
| **Auth** | API key or OAuth2 |
| **Rate limit tier** | Relaxed (120 req/min, burst 200) |
| **Example resources** | `/api/v1/docs/specs`, `/api/v1/docs/runbooks`, `/api/v1/docs/plan-summaries` |
| **Forbidden** | POST, PUT, PATCH, DELETE -- this is a read-only surface |

**Notes**: Content is derived from Plane work items and repo markdown. Cached aggressively
(TTL 5 minutes). No write-back path exists through the gateway.

---

### 2.5 `/api/v1/integrations/*` -- n8n Webhooks

| Property | Value |
|----------|-------|
| **Owner** | Automation team (n8n) |
| **Backing service** | n8n webhook receiver |
| **Allowed methods** | POST only |
| **Auth** | API key + HMAC signature -- required |
| **Rate limit tier** | Strict (10 req/min, burst 20) |
| **Example resources** | `/api/v1/integrations/webhooks/github`, `/api/v1/integrations/webhooks/slack`, `/api/v1/integrations/sync/trigger`, `/api/v1/integrations/callbacks/{id}` |
| **Forbidden** | GET (no browsing webhook endpoints), business state writes (n8n triggers actions, not data) |

**Notes**: HMAC validation is enforced at the APIM policy layer before forwarding to n8n.
Payloads are logged (PII redacted) for audit. Callback endpoints are ephemeral and expire
after 24 hours.

---

## 3. Route Conflict Resolution

- No two route groups may share a prefix.
- New route groups require an amendment to this contract before APIM configuration.
- Versioning: All routes use `/api/v1/`. When v2 is introduced, v1 routes remain active
  with a 6-month deprecation window.

---

## 4. Monitoring

Each route group emits metrics to Azure Monitor:
- Request count by method and status code
- P50/P95/P99 latency
- Rate limit rejections
- Auth failures

Dashboards: Superset at `superset.insightpulseai.com` (API Gateway dashboard).

---

*Governed by: `docs/contracts/API_AUTHORITY_BOUNDARIES.md`*
