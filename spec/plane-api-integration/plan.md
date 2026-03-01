# Implementation Plan — Plane API Integration

> Technical plan for building the unified Plane connector and refactoring existing integrations.
> Status: Draft | Date: 2026-03-01

---

## 1. Primary Requirements

From the PRD:

1. Generic `PlaneClient` class (auth, rate-limiting, cursor pagination, fields/expand)
2. Webhook verification + deduplication layer
3. MCP transport configuration (3 modes)
4. OAuth Plane App support (bot + user flows)
5. Refactor `ipai_bir_plane_sync` to use the generic connector
6. Platform contract C-18 + secrets registration

---

## 2. Technical Context

| Dimension | Value |
|-----------|-------|
| Language | Python 3.12+ |
| Framework | Odoo 19.0 CE |
| Database | PostgreSQL 16 (Odoo-local) |
| Testing | `unittest` via Odoo test runner |
| Existing pattern | `ipai_slack_connector` (AbstractModel + pure client) |
| Existing Plane module | `ipai_bir_plane_sync` (direct `requests` usage) |
| Webhook relay | Supabase Edge Function `plane-sync` (continues as-is) |

---

## 3. Architecture

### Module Structure

```
addons/ipai/ipai_plane_connector/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── plane_connector.py        # AbstractModel: ipai.plane.connector
│   └── plane_webhook_delivery.py # Model: plane.webhook.delivery (dedup)
├── utils/
│   ├── __init__.py
│   ├── plane_client.py           # Pure Python: PlaneClient class
│   └── plane_webhook.py          # Pure Python: HMAC verification
├── data/
│   └── ir_config_parameter.xml   # Default system parameters
├── security/
│   └── ir.model.access.csv
├── tests/
│   ├── __init__.py
│   ├── test_plane_client.py      # Client unit tests
│   └── test_plane_webhook.py     # Webhook verification tests
└── README.md
```

### Key Design Decisions

**D1: Follow the Slack connector pattern** — `ipai.plane.connector` is an `AbstractModel` that any domain module can `_inherit`. The `PlaneClient` lives in `utils/plane_client.py` as a pure Python class (no Odoo ORM dependency) for testability.

**D2: Webhook dedup via Odoo model** — `plane.webhook.delivery` stores processed `X-Plane-Delivery` UUIDs with a TTL. A scheduled action (`ir.cron`) cleans deliveries older than 7 days. This avoids needing Redis or external state.

**D3: Supabase Edge Function remains the relay** — Plane webhooks hit the existing `plane-sync` Edge Function, which forwards to Odoo. The Edge Function handles the first layer of signature verification. The Odoo connector adds a second verification layer for defense-in-depth.

**D4: Config via `ir.config_parameter`** — All Plane settings (`plane.base_url`, `plane.api_key`, `plane.workspace_slug`, `plane.webhook_secret`) use Odoo system parameters. Actual secret values live in Supabase Vault and are injected into Odoo container env at deploy time.

---

## 4. Connector Topology

```
┌─────────────────────────────────────────────────────┐
│ Odoo (ipai_plane_connector)                         │
│                                                     │
│  PlaneClient ──── REST API ────▶ Plane API          │
│  (auth, rate-limit, pagination)  (Cloud/Self-hosted)│
│                                                     │
│  PlaneWebhookMixin ◀──── Edge Function ◀── Plane WH│
│  (verify, dedup, dispatch)                          │
│                                                     │
│  Domain modules (BIR, future) ─── _inherit ──┘      │
└─────────────────────────────────────────────────────┘

MCP (agent layer — config only, no Odoo code):
┌─────────────────┐
│ Claude / Agents  │──── MCP ────▶ Plane MCP Server
│ (MCP client)     │              (3 transport modes)
└─────────────────┘
```

---

## 5. Eventing & Sync Topology

### Webhook Ingestion Flow

```
Plane Event → Plane Webhook → Supabase Edge Function (plane-sync)
    → Edge Function verifies X-Plane-Signature (HMAC-SHA256)
    → Edge Function forwards to Odoo JSON-RPC endpoint
    → Odoo ipai_plane_connector:
        1. Verify signature again (defense-in-depth)
        2. Check X-Plane-Delivery UUID against plane.webhook.delivery
        3. If duplicate → skip (return 200)
        4. If new → store delivery UUID → dispatch to domain handler
        5. Domain handler (e.g., BIR) processes the event
```

### Rate-Limit Handling

```
PlaneClient.request():
    1. Send request
    2. Read X-RateLimit-Remaining from response headers
    3. If remaining < 5: preemptive backoff (sleep until X-RateLimit-Reset)
    4. If 429 received: exponential backoff with jitter (1s, 2s, 4s; max 3 retries)
    5. Log rate-limit state for observability
```

### Cursor Pagination

```
PlaneClient.paginate(endpoint, **params):
    cursor = None
    while True:
        response = self.request(endpoint, cursor=cursor, per_page=100, **params)
        yield from response["results"]
        if not response.get("next_page_results"):
            break
        cursor = response["next_cursor"]
```

---

## 6. System of Record Matrix

| Domain | SSOT Owner | Role |
|--------|-----------|------|
| Work items, projects, cycles, modules, comments | **Plane** | Authoritative for PM artifacts; Odoo reads/mirrors. |
| Finance, ops workflows (BIR, docflow, approvals) | **Odoo** | Authoritative for ERP records; Plane receives a view. |
| Connector mappings (entity ↔ issue) | **Supabase** (`ops.plane_sync_mappings`) | Bridge state; neither Plane nor Odoo owns the mapping. |
| Secrets & credentials | **Supabase Vault** | Never in Odoo DB or Plane. |

### Failure-Mode Semantics

| Scenario | Behavior |
|----------|----------|
| Webhook processing succeeds | Return `200`. Side effects committed. |
| Webhook processing fails after durable enqueue | Return `200`. Odoo retries internally via queue. Plane does NOT redeliver. |
| Webhook processing fails before durable enqueue | Return `500`. Plane redelivers with exponential backoff (10 min → 30 min). Safe because dedupe hasn't recorded this delivery yet. |
| REST call gets 429 | Retry with exponential backoff + jitter (1s, 2s, 4s; max 3 retries). Parse `X-RateLimit-Reset` header. |
| REST call gets 5xx | Retry once after 2s. If still failing, raise typed exception. |
| Missing secret at runtime | Return `503 KEY_MISSING` with `ssot_ref` pointing to registry entry. |

### Provider Selection Policy

- **MCP**: Primary for agentic operations (Claude/agent workflows). Use remote API-key transport for automation, OAuth transport for user-consent flows.
- **REST**: Primary for deterministic batch sync (BIR deadlines, bulk operations). Use `PlaneClient` with rate-limit and pagination.
- **OAuth Plane App**: Only when user-context is required (actions attributable to a specific user, not a bot).
- **Built-in connector**: Always prefer Plane's native integration (GitHub/Slack/GitLab/Sentry) before building a custom bridge.

---

## 7. Built-in Integration Selection Policy

| Need | First choice | Fallback |
|------|-------------|----------|
| GitHub issue sync | Plane built-in GitHub integration | REST API via connector |
| Slack notifications | Plane built-in Slack integration | `ipai_slack_connector` |
| GitLab MR tracking | Plane built-in GitLab integration | REST API via connector |
| Sentry error sync | Plane built-in Sentry integration (Pro-gated) | REST API via connector |
| Custom domain sync (BIR, etc.) | `ipai_plane_connector` + domain module | — |

**Rule**: Always prefer Plane's built-in connector when available. Only build custom bridges for domain-specific sync (BIR deadlines, sales orders, etc.).

---

## 8. Self-Hosted Deployment Topology

### Current State

- Plane CE is deployed (evidence in `docs/evidence/20260130-2014/PLANE_PRODUCTION_DEPLOYMENT.md`)
- Using self-hosted Plane at `plane.insightpulseai.com` (per bootstrap config)

### Config Surface

| Parameter | Source | Default |
|-----------|--------|---------|
| `plane.base_url` | `ir.config_parameter` | `https://api.plane.so` |
| `plane.api_key` | Supabase Vault → container env → `ir.config_parameter` | — |
| `plane.workspace_slug` | `ir.config_parameter` | `insightpulseai` |
| `plane.webhook_secret` | Supabase Vault → container env → `ir.config_parameter` | — |

---

## 9. MCP Configuration

Three transport templates (config-only, no Odoo code needed):

### Remote OAuth (Plane Cloud users)

```json
{
  "transport": "remote-http",
  "endpoint": "https://mcp.plane.so/http/mcp",
  "auth": "oauth"
}
```

### Remote API-Key (automation/CI)

```json
{
  "transport": "remote-http",
  "endpoint": "https://mcp.plane.so/http/api-key/mcp",
  "headers": {
    "Authorization": "Bearer ${PLANE_API_KEY}",
    "X-Workspace-slug": "${PLANE_WORKSPACE_SLUG}"
  }
}
```

### Local stdio (self-hosted Plane)

```json
{
  "transport": "stdio",
  "command": "uvx",
  "args": ["plane-mcp-server", "stdio"],
  "env": {
    "PLANE_API_KEY": "${PLANE_API_KEY}",
    "PLANE_WORKSPACE_SLUG": "${PLANE_WORKSPACE_SLUG}",
    "PLANE_BASE_URL": "${PLANE_BASE_URL}"
  }
}
```

---

## 10. Constitutional Compliance

| Constraint | How addressed |
|-----------|---------------|
| C1 (Plane not SSOT) | Odoo owns data; Plane is a view. Connector never overwrites Odoo records without domain-module logic. |
| C2 (Single client) | All API calls go through `PlaneClient` in `utils/plane_client.py`. |
| C3 (Webhook verification) | HMAC-SHA256 verification in `utils/plane_webhook.py`. |
| C4 (Secrets in Vault) | Secrets registered in `ssot/secrets/registry.yaml`; values in Supabase Vault. |
| C5 (Rate limit) | Client reads `X-RateLimit-*` headers; backs off on 429. |
| C6 (Cursor pagination) | `paginate()` method uses cursor format `value:offset:is_prev`. |
| C7 (Configurable base URL) | `plane.base_url` system parameter. |
| C8 (Inherit, not fork) | `ipai_bir_plane_sync` will `_inherit` from `ipai.plane.connector`. |
| C9 (MCP 3 modes) | Config templates for all three transports. |
| C10 (Webhook dedup) | `plane.webhook.delivery` model with UUID lookup. |
| C11 (Idempotency) | Delivery ID persisted _before_ side effects; duplicate deliveries are no-ops. |
| C12 (Throttle contract) | Client parses `X-RateLimit-*` headers; adaptive backoff with jitter; bounded retries. |
| C13 (Cursor opaque) | `paginate()` stores/forwards cursor as-is; no parsing of cursor format. |
| C14 (No dup side effects) | Unique constraint on `delivery_id`; duplicate insert raises → skip. |
| C15 (URL normalization) | Base URL join tested for trailing-slash variants; `urljoin` with path safety. |

---

## 11. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Plane API rate limit changes | Low | Medium | Client reads dynamic headers, not hardcoded limits. |
| Plane MCP Server (Beta) breaks | Medium | Low | MCP is config-only; fallback is REST. |
| Webhook delivery loss | Low | Medium | Supabase Edge Function has its own retry; Odoo dedup handles re-delivery safely. |
| OAuth Plane Apps (Beta) API changes | Medium | Medium | Bot-token flow is isolated in its own method; easy to update. |
| `ipai_bir_plane_sync` refactor breaks existing sync | Medium | High | Tests before/after; feature flag to toggle new connector. |

---

## 12. Verification Commands

```bash
# Run connector unit tests
python -m pytest addons/ipai/ipai_plane_connector/tests/ -v

# Validate module installable
odoo-bin -c /etc/odoo/odoo.conf --test-enable -u ipai_plane_connector --stop-after-init

# Check secrets not committed
git diff --cached -- '*.py' '*.xml' '*.yaml' | grep -iE '(api.key|secret|token|password)' && echo "FAIL: possible secret" || echo "PASS"

# Validate contract exists
test -f docs/contracts/PLANE_ODOO_SYNC_CONTRACT.md && echo "PASS" || echo "FAIL"

# Validate secrets registered
grep 'plane_api_key' ssot/secrets/registry.yaml && echo "PASS" || echo "FAIL"
```

---

## 13. Handoff

After plan approval → generate tasks via `/speckit.tasks` → implement phase by phase.
