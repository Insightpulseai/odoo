# Constitution — Plane API Integration

> Governing principles for the Plane ↔ Odoo integration layer.
> Ratified: 2026-03-01

---

## 1. Purpose

Define non-negotiable rules for how this repo integrates with Plane (project management) across REST API, Webhooks, MCP Server, and OAuth Plane Apps.

## 2. Constraints

| # | Constraint | Rationale |
|---|-----------|-----------|
| C1 | **Plane is NOT the SSOT for any Odoo domain object.** Plane is a work-management _view_; Odoo owns the data. | Prevents split-brain between ERP records and PM issues. |
| C2 | **All Plane API calls route through a single generic client module** (`ipai_plane_connector`), never direct `requests.post` in domain modules. | Centralizes auth, rate-limit handling, retry logic, and audit. |
| C3 | **Webhook signatures MUST be verified** using HMAC-SHA256 before any payload is processed. | Prevents spoofed webhook injection. |
| C4 | **Secrets (API keys, webhook secrets, OAuth client secrets) MUST live in approved stores only** — Supabase Vault, OS keychain, or GitHub Actions Secrets. Never in Git. | Aligns with repo secrets policy. |
| C5 | **Rate-limit budget: 60 req/min per API key** (Plane's documented limit). Client must read `X-RateLimit-Remaining` / `X-RateLimit-Reset` and back off. | Prevents 429 cascades. |
| C6 | **Cursor pagination only** — client must not assume offset-based pagination. Cursor format is `value:offset:is_prev`. | Matches Plane API contract. |
| C7 | **Self-hosted Plane base URL is configurable** via `ir.config_parameter` key `plane.base_url` (default: `https://api.plane.so`). | Supports both Plane Cloud and self-hosted deployments. |
| C8 | **Domain modules inherit, never fork** — domain-specific sync modules (e.g., `ipai_bir_plane_sync`) must `_inherit` from the connector base, not duplicate client logic. | DRY + consistent error handling. |
| C9 | **MCP transport config must support all three modes** — remote OAuth, remote API-key, and local stdio — selectable by environment. | Covers Plane Cloud, self-hosted, and local dev. |
| C10 | **Webhook deduplication by `X-Plane-Delivery` header** — every webhook handler must deduplicate on this UUID before processing. | Plane retries with exponential backoff; without dedupe, events process multiple times. |
| C11 | **Idempotency is mandatory for webhook handlers.** All webhook processing MUST be keyed by `X-Plane-Delivery` and event type, stored in durable storage _before_ side effects execute. | Guarantees exactly-once semantics even across process restarts. |
| C12 | **Throttle contract.** Client MUST parse `X-RateLimit-Remaining` and `X-RateLimit-Reset` and implement adaptive backoff; 429 MUST be retried with jitter and a bounded upper limit (max 3 retries). | Prevents cascading failures and respects Plane's 60 req/min budget. |
| C13 | **Cursor iteration contract.** Pagination MUST use `next_cursor`/`prev_cursor` from response; cursor format is opaque (do not parse except to store/forward). | Forward-compatible if Plane changes cursor internals. |
| C14 | **No duplicate side effects.** Re-delivered events MUST be no-ops (exactly-once effect) even across restarts. Dedupe persistence uses a unique constraint on `delivery_id`. | Prevents double-writes to Odoo records on webhook re-delivery. |
| C15 | **Base URL normalization.** All requests MUST be built from `PLANE_BASE_URL` + `/api/v1/` with safe join (no double slashes), and test coverage must assert correct URL joining for both trailing-slash and no-trailing-slash base URLs. | Self-hosted deployments commonly break on URL construction. |

## 3. Security

- OAuth tokens (bot and user flows) must be stored encrypted; refresh handled automatically.
- Webhook endpoints must reject requests with invalid or missing `X-Plane-Signature`.
- No Plane API token may appear in logs, CI output, or committed files.

## 4. Quality Gates

| Gate | Requirement |
|------|-------------|
| PR merge | All Plane client unit tests pass (auth, rate-limit, pagination, webhook verification). |
| PR merge | No secrets in diff (checked by `ssot-surface-guard.yml`). |
| PR merge | `plane_api_key` and `plane_webhook_secret` entries exist in `ssot/secrets/registry.yaml`. |
| PR merge | Dedupe persistence has unique constraint on `delivery_id` (schema gate). |
| Deploy | Plane connectivity health-check passes (`/api/v1/users/me/` returns 200). |

## 5. Governance

- Amendments require updating this file + PR review.
- Cross-boundary changes (Plane ↔ Supabase ↔ Odoo) require a contract doc per Rule 9.
