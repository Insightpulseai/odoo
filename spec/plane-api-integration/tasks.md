# Tasks — Plane API Integration

> Task breakdown for implementing the unified Plane connector.
> Generated from: plan.md | Date: 2026-03-01

---

## Legend

- **ID**: `T-<phase>.<seq>` (e.g., T-1.1)
- **P**: Parallelizable with other tasks in same phase? (Y/N)
- **US#**: User Story reference from PRD
- **Dep**: Dependency on other task(s)

---

## Phase 1: Foundation — Generic Connector Module

| ID | Task | P | US# | Dep | Status |
|----|------|---|-----|-----|--------|
| T-1.1 | Scaffold `addons/ipai/ipai_plane_connector/` module structure (manifest, `__init__`, security, data) | N | — | — | ☐ |
| T-1.2 | Implement `utils/plane_client.py` — `PlaneClient` class with: auth header selection (PAT `X-API-Key` / OAuth `Bearer`), configurable base URL, request method with error handling | Y | US-1 | T-1.1 | ☐ |
| T-1.3 | Add rate-limit handling to `PlaneClient`: read `X-RateLimit-Remaining` / `X-RateLimit-Reset` from response headers, exponential backoff + jitter on 429, preemptive slowdown when remaining < 5 | Y | US-1 | T-1.2 | ☐ |
| T-1.4 | Add cursor pagination to `PlaneClient`: `paginate()` generator method, cursor format `value:offset:is_prev`, `per_page` capped at 100, `fields` and `expand` query param pass-through | Y | US-1 | T-1.2 | ☐ |
| T-1.5 | Implement `utils/plane_webhook.py` — `verify_plane_signature(secret, payload_bytes, signature_header) → bool` using HMAC-SHA256 | Y | US-2 | T-1.1 | ☐ |
| T-1.6 | Implement `models/plane_webhook_delivery.py` — `plane.webhook.delivery` model (fields: `delivery_id` Char unique, `event_type` Char, `received_at` Datetime, `processed` Boolean) | Y | US-2 | T-1.1 | ☐ |
| T-1.7 | Implement `models/plane_connector.py` — `ipai.plane.connector` AbstractModel with methods: `_plane_client()` (returns configured `PlaneClient`), `_plane_verify_webhook(headers, body)`, `_plane_is_duplicate_delivery(delivery_id)`, `_plane_enabled()` config check | N | US-1,2 | T-1.2,T-1.5,T-1.6 | ☐ |
| T-1.8 | Add `data/ir_config_parameter.xml` with defaults: `plane.base_url` = `https://api.plane.so`, `plane.workspace_slug` = `insightpulseai` | Y | US-3 | T-1.1 | ☐ |
| T-1.9 | Add `ir.cron` scheduled action to clean `plane.webhook.delivery` records older than 7 days | Y | US-2 | T-1.6 | ☐ |

---

## Phase 2: Tests

| ID | Task | P | US# | Dep | Status |
|----|------|---|-----|-----|--------|
| T-2.1 | Unit tests for `PlaneClient`: auth header selection (PAT vs OAuth), base URL construction, error code mapping (400/401/404/429/500) | Y | US-1 | T-1.2 | ☐ |
| T-2.2 | Unit tests for rate-limit handling: parse `X-RateLimit-*` headers, 429 retry with backoff, preemptive slowdown | Y | US-1 | T-1.3 | ☐ |
| T-2.3 | Unit tests for cursor pagination: single page, multi-page iteration, empty results, `fields`/`expand` pass-through | Y | US-1 | T-1.4 | ☐ |
| T-2.4 | Unit tests for webhook verification: valid signature, invalid signature, missing signature, empty payload | Y | US-2 | T-1.5 | ☐ |
| T-2.5 | Unit tests for webhook deduplication: new delivery processed, duplicate delivery skipped, cleanup of old records | Y | US-2 | T-1.6 | ☐ |

---

## Phase 3: Refactor — BIR Module Migration

| ID | Task | P | US# | Dep | Status |
|----|------|---|-----|-----|--------|
| T-3.1 | Add `ipai_plane_connector` to `ipai_bir_plane_sync` manifest `depends` list | N | US-4 | T-1.7 | ☐ |
| T-3.2 | Refactor `bir_filing_deadline.py`: remove `import requests`, replace `_call_plane_sync_api()` with `self._plane_client().request()` | N | US-4 | T-3.1 | ☐ |
| T-3.3 | Update `handle_plane_webhook()` to use `_plane_verify_webhook()` and `_plane_is_duplicate_delivery()` from connector mixin | N | US-4 | T-3.2 | ☐ |
| T-3.4 | Verify BIR module still syncs correctly after refactor (manual test or existing test suite) | N | US-4 | T-3.3 | ☐ |

---

## Phase 4: SSOT & Governance

| ID | Task | P | US# | Dep | Status |
|----|------|---|-----|-----|--------|
| T-4.1 | Create `docs/contracts/PLANE_ODOO_SYNC_CONTRACT.md` (C-18): source SSOT = `addons/ipai/ipai_plane_connector/`, consumer = Plane API, protocol = REST + Webhooks, invariants, validator | Y | — | — | ☐ |
| T-4.2 | Add C-18 row to `docs/contracts/PLATFORM_CONTRACTS_INDEX.md` | Y | — | T-4.1 | ☐ |
| T-4.3 | Register secrets in `ssot/secrets/registry.yaml`: `plane_api_key` (purpose: Plane REST API PAT, stores: supabase_vault + os_keychain, consumers: Odoo + Edge Function, rotation: annually), `plane_webhook_secret` (purpose: Webhook HMAC verification, stores: supabase_vault + os_keychain, consumers: Edge Function + Odoo, rotation: annually) | Y | — | — | ☐ |
| T-4.4 | Update `docs/architecture/PLATFORM_REPO_TREE.md` SSOT Assignment Table: add `addons/ipai/ipai_plane_connector/` path | Y | — | — | ☐ |

---

## Phase 5: MCP & Integration Docs

| ID | Task | P | US# | Dep | Status |
|----|------|---|-----|-----|--------|
| T-5.1 | Create MCP transport config templates for Plane: `agents/mcp/configs/plane-mcp.yaml` with 3 modes (remote OAuth, remote API-key, local stdio) | Y | US-5 | — | ☐ |
| T-5.2 | Write integration selection policy doc: `docs/integration/PLANE_INTEGRATION_POLICY.md` documenting when to use built-in connectors (GitHub/Slack/GitLab/Sentry) vs. custom bridges | Y | US-7 | — | ☐ |
| T-5.3 | Add connector README: `addons/ipai/ipai_plane_connector/README.md` with usage examples, config params, and API reference | N | — | T-1.7 | ☐ |

---

## Phase 6 (P2): OAuth Plane App

| ID | Task | P | US# | Dep | Status |
|----|------|---|-----|-----|--------|
| T-6.1 | Add OAuth bot-token flow (client credentials) to `PlaneClient`: token exchange, storage, auto-refresh | N | US-6 | T-1.2 | ☐ |
| T-6.2 | Add OAuth user-token flow (authorization code) behind config flag | N | US-8 | T-6.1 | ☐ |
| T-6.3 | Unit tests for OAuth flows: token exchange, refresh, expiry handling | N | US-6,8 | T-6.1 | ☐ |

---

## Task Dependencies (ASCII)

```
Phase 1 (Foundation)
  T-1.1 ──┬── T-1.2 ──┬── T-1.3
           │           ├── T-1.4
           │           └── T-1.7 (also needs T-1.5, T-1.6)
           ├── T-1.5
           ├── T-1.6 ── T-1.9
           └── T-1.8

Phase 2 (Tests) — all parallel, each depends on its Phase 1 counterpart

Phase 3 (Refactor) — sequential chain
  T-3.1 → T-3.2 → T-3.3 → T-3.4

Phase 4 (SSOT) — mostly parallel, independent of code phases
  T-4.1 → T-4.2 (index update depends on contract doc)
  T-4.3, T-4.4 — independent

Phase 5 (MCP & Docs) — parallel, independent
  T-5.1, T-5.2, T-5.3 (README depends on T-1.7)

Phase 6 (OAuth) — sequential, depends on Phase 1 client
  T-6.1 → T-6.2 → T-6.3
```

---

## Implementation Strategy

**MVP-first**: Phases 1–4 form the MVP. Ship the generic connector, tests, BIR refactor, and governance docs together.

**Phase 5** (MCP + docs) can ship independently or alongside MVP.

**Phase 6** (OAuth) is P2 and should only be built when a concrete use case requires it (e.g., a Plane App that acts on behalf of specific users).

---

## Progress Tracking

| Phase | Tasks | Done | % |
|-------|-------|------|---|
| 1. Foundation | 9 | 0 | 0% |
| 2. Tests | 5 | 0 | 0% |
| 3. Refactor | 4 | 0 | 0% |
| 4. SSOT | 4 | 0 | 0% |
| 5. MCP & Docs | 3 | 0 | 0% |
| 6. OAuth (P2) | 3 | 0 | 0% |
| **Total** | **28** | **0** | **0%** |
