# PRD — Plane API Integration

> Product Requirements Document for the unified Plane ↔ Odoo integration.
> Status: Draft | Date: 2026-03-01

---

## 1. Feature Overview

### Problem

The repo has a single domain-specific Plane integration (`ipai_bir_plane_sync`) that embeds API-call logic directly in the BIR filing deadline model. There is no reusable Plane client, no spec bundle, no platform contract, and secrets are not registered in the SSOT registry. The ChatGPT conversation dump (5 Plane developer doc pages) reveals significant untapped integration surface: REST API with pagination/rate-limiting, Webhooks with HMAC verification, MCP Server with 3 transports, OAuth Plane Apps, self-hosting topology, and built-in connectors (GitHub/Slack/GitLab/Sentry).

### Solution

Build a **generic Plane connector module** (`ipai_plane_connector`) that encapsulates:

1. REST client (auth, rate-limiting, cursor pagination, `fields`/`expand`)
2. Webhook ingestion (HMAC verification, `X-Plane-Delivery` dedup)
3. MCP transport configuration (3 modes)
4. OAuth Plane App support (bot token + user token flows)

Then refactor `ipai_bir_plane_sync` to inherit from the connector base instead of embedding raw API logic.

### Alignment

- **Module Philosophy**: Config → OCA → Delta (`ipai_*`). No OCA module covers Plane integration, so a custom `ipai_plane_connector` is justified.
- **SSOT Boundaries**: Plane is an external work-management system. The connector crosses the Odoo ↔ Plane boundary, requiring a platform contract (C-18).

---

## 2. User Scenarios

### P1 — Must Have

| # | Scenario | Acceptance Criteria |
|---|---------|-------------------|
| US-1 | As a developer, I can call Plane REST API from any Odoo module via `ipai_plane_connector` without re-implementing auth or rate-limit logic. | Single `PlaneClient` class handles auth headers, 429 retry, cursor pagination. |
| US-2 | As a system, incoming Plane webhooks are verified (HMAC-SHA256) and deduplicated before processing. | Invalid signatures return 401. Duplicate `X-Plane-Delivery` UUIDs are silently dropped. |
| US-3 | As an ops engineer, I can configure the Plane base URL for self-hosted instances via Odoo system parameter. | `plane.base_url` defaults to `https://api.plane.so`; overridable for self-hosted. |
| US-4 | As a developer, `ipai_bir_plane_sync` uses the generic connector instead of direct `requests` calls. | BIR module no longer imports `requests`; delegates to connector. |

### P2 — Should Have

| # | Scenario | Acceptance Criteria |
|---|---------|-------------------|
| US-5 | As an agent system, I can interact with Plane via MCP Server (remote API-key mode). | MCP config template exists with endpoint, headers, and workspace slug. |
| US-6 | As a developer, I can register a Plane OAuth App (bot token flow) and the connector handles token exchange + refresh. | OAuth helpers for client-credentials flow; token stored in Vault. |
| US-7 | As an ops engineer, I can see which Plane built-in integrations (GitHub, Slack, GitLab, Sentry) are active in our workspace. | Documentation/runbook enumerates available connectors and selection policy. |

### P3 — Nice to Have

| # | Scenario | Acceptance Criteria |
|---|---------|-------------------|
| US-8 | As a developer, I can use Plane OAuth user-token flow for actions scoped to a specific user. | User-token OAuth (authorization code) is implemented behind a config flag. |
| US-9 | As an ops engineer, I have a self-hosted Plane deployment guide with Helm values and sizing. | Deploy templates (Compose + Helm) with placeholder values exist. |

---

## 3. Functional Requirements

| ID | Description | Priority | Story |
|----|------------|----------|-------|
| FR-1 | `PlaneClient` class with configurable base URL, auth (PAT via `X-API-Key` + OAuth `Bearer`), rate-limit handling (read `X-RateLimit-Remaining`/`Reset`, back off on 429), cursor pagination (cursor format `value:offset:is_prev`, `per_page` max 100), and `fields`/`expand` query params. | P1 | US-1 |
| FR-2 | Webhook verification function: `verify_plane_signature(secret, payload_bytes, signature_header) → bool` using HMAC-SHA256. | P1 | US-2 |
| FR-3 | Webhook deduplication: store `X-Plane-Delivery` UUIDs (TTL-based or DB table) and skip known deliveries. | P1 | US-2 |
| FR-4 | System parameter `plane.base_url` (default `https://api.plane.so`) used by all client calls. | P1 | US-3 |
| FR-5 | System parameter `plane.api_key` read from `ir.config_parameter` (stored in Vault, injected at runtime). | P1 | US-1 |
| FR-6 | Refactor `ipai_bir_plane_sync` to use `ipai_plane_connector` methods instead of raw `requests`. | P1 | US-4 |
| FR-7 | MCP transport configuration templates for 3 modes: remote OAuth (`/http/mcp`), remote API-key (`/http/api-key/mcp`), local stdio. | P2 | US-5 |
| FR-8 | OAuth bot-token flow (client credentials): exchange `client_id`+`client_secret` for access token, auto-refresh. | P2 | US-6 |
| FR-9 | Integration selection policy doc: prefer built-in connectors (GitHub/Slack/GitLab/Sentry) before custom bridges. | P2 | US-7 |
| FR-10 | OAuth user-token flow (authorization code): behind config flag, for user-scoped actions. | P3 | US-8 |
| FR-11 | Self-hosted Plane deployment templates (Docker Compose + Helm values) with placeholder secrets. | P3 | US-9 |

---

## 4. Non-Functional Requirements

### Performance

- REST client must handle 60 req/min rate limit gracefully (no 429 cascades).
- Webhook processing latency target: < 2s from receipt to Odoo write.

### Security

- All secrets via Supabase Vault / OS keychain / GitHub Actions Secrets.
- HMAC-SHA256 webhook verification is mandatory — no bypass path.
- OAuth tokens encrypted at rest; auto-refresh before expiry.

### Reliability

- Webhook handler is idempotent (dedupe by `X-Plane-Delivery`).
- REST client retries on 429 with exponential backoff + jitter (max 3 retries).
- Webhook retries from Plane (10 min → 30 min → ...) are safe due to dedup.

---

## 5. Integration Points

### Plane API (REST)

- **Base URL**: `https://api.plane.so/api/v1/` (cloud) or `<self-host>/api/v1/`
- **Auth**: `X-API-Key: <PAT>` or `Authorization: Bearer <OAuth token>`
- **Rate limit**: 60/min per key; headers `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- **Pagination**: Cursor-based (`value:offset:is_prev`); `per_page` default/max 100
- **Payload shaping**: `fields` (comma-separated) and `expand` (related objects)
- **Status codes**: 200, 201, 400, 401, 403, 404, 429, 500

### Plane Webhooks

- **Signature**: `X-Plane-Signature` header = HMAC-SHA256(secret, raw JSON payload)
- **Delivery ID**: `X-Plane-Delivery` (UUID) for idempotency
- **Event header**: `X-Plane-Event` (e.g., `issue.created`, `issue.updated`)
- **Events**: Project, Issue, Cycle, Module, Issue Comment
- **Retries**: Exponential backoff (10 min, 30 min, ...) on non-200

### Plane MCP Server

- **Remote OAuth**: `https://mcp.plane.so/http/mcp`
- **Remote API-key**: `https://mcp.plane.so/http/api-key/mcp` + headers `Authorization: Bearer <API_KEY>`, `X-Workspace-slug: <slug>`
- **Local stdio**: `uvx ...` with env vars `PLANE_API_KEY`, `PLANE_WORKSPACE_SLUG`, optional `PLANE_BASE_URL`

### Plane OAuth Apps (Beta)

- **Bot Token Flow**: Client credentials → autonomous agent actions
- **User Token Flow**: Authorization code → user-scoped actions
- **App components**: OAuth app + Setup URL + Redirect URI + Webhook URL
- **SDKs**: `@makeplane/plane-node-sdk` (Node), `plane-sdk` (Python)

### Built-in Integrations

- GitHub, GitHub Enterprise, Slack, GitLab, Sentry
- Sentry marked "Pro" (plan-gated)
- Policy: prefer built-in connector before custom bridge

---

## 6. Success Criteria

| Metric | Target |
|--------|--------|
| All Plane REST calls use `ipai_plane_connector` | 100% (no raw `requests` in domain modules) |
| Webhook HMAC verification test coverage | Valid + invalid signatures tested |
| Rate-limit handling tested | 429 response triggers retry with backoff |
| Cursor pagination tested | Multi-page iteration verified |
| `ipai_bir_plane_sync` refactored | Zero direct `requests` imports |
| Platform contract C-18 exists | `docs/contracts/PLANE_ODOO_SYNC_CONTRACT.md` committed |
| Secrets registered | `plane_api_key`, `plane_webhook_secret` in `ssot/secrets/registry.yaml` |

---

## 7. Key Entities

| Entity | Description |
|--------|------------|
| `PlaneClient` | Generic REST client class in `ipai_plane_connector` |
| `PlaneWebhookMixin` | Mixin model providing webhook verification + dedup |
| `plane.webhook.delivery` | Odoo model tracking processed `X-Plane-Delivery` UUIDs |
| `ir.config_parameter` keys | `plane.base_url`, `plane.api_key`, `plane.workspace_slug`, `plane.webhook_secret` |

---

## 8. Out of Scope

- Plane Enterprise license procurement (commercial decision, not engineering).
- Full self-hosted Plane deployment (infra provisioning is ops, not this spec).
- Replacing Supabase Edge Function routing — existing `plane-sync` function continues as the webhook relay; this spec adds the Odoo-side client and verification layer.
