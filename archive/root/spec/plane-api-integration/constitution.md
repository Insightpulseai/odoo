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

## 3. Security

- OAuth tokens (bot and user flows) must be stored encrypted; refresh handled automatically.
- Webhook endpoints must reject requests with invalid or missing `X-Plane-Signature`.
- No Plane API token may appear in logs, CI output, or committed files.

## 4. Quality Gates

| Gate | Requirement |
|------|-------------|
| PR merge | All Plane client unit tests pass (auth, rate-limit, pagination, webhook verification). |
| PR merge | No secrets in diff (checked by `ssot-surface-guard.yml`). |
| Deploy | Plane connectivity health-check passes (`/api/v1/users/me/` returns 200). |

## 5. Governance

- Amendments require updating this file + PR review.
- Cross-boundary changes (Plane ↔ Supabase ↔ Odoo) require a contract doc per Rule 9.
