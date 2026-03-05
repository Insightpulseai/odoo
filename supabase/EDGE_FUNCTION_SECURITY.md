# Edge Function Security Model

> Auth matrix for all Supabase Edge Functions in this repo.
> Source of truth: `supabase/config.toml` `[functions.*]` blocks.
> Last audited: 2026-03-05

## JWT Configuration Summary

| Status | Count | Description |
|--------|-------|-------------|
| `verify_jwt = true` | 7 | JWT required by Supabase gateway |
| `verify_jwt = false` | 6 | No gateway JWT — auth handled in-function or not required |
| No config | 68 | **Supabase default applies** (verify_jwt = true) |

**Supabase default**: Functions without explicit config inherit `verify_jwt = true` from the platform.
This means the 68 unconfigured functions DO require a valid JWT — but this is implicit, not documented.

---

## Functions with `verify_jwt = false` (Requires Justification)

| Function | Auth Method | Justification |
|----------|-------------|---------------|
| `copilot-chat` | None (dev tool) | Internal dev assistant, not exposed publicly |
| `github-slack-bridge` | GitHub webhook signature | Validates `X-Hub-Signature-256` header in-function |
| `ipai-copilot` | None (dev tool) | Internal dev assistant, not exposed publicly |
| `stripe-webhook` | Stripe signature | Validates `stripe-signature` header via Stripe SDK |
| `sync-odoo-modules` | Service role key | Checks `Authorization` header for service_role_key in-function |
| `workspace-ask-docs` | Hybrid (JWT or service_role) | Accepts both JWT and service_role_key, validated in-function |

---

## Functions with `verify_jwt = true` (Explicit Config)

| Function | Auth Method |
|----------|-------------|
| `cron-processor` | JWT (service_role_key via cron invocation) |
| `github-app-auth` | JWT |
| `infra-memory-ingest` | JWT |
| `schema-changed` | JWT |
| `tenant-invite` | JWT |
| `workspace-indexer` | JWT (service_role_key, scheduled worker) |

---

## Functions with No JWT Config (Inherits Platform Default)

These 68 functions have no `[functions.<name>]` block in `config.toml`.
They inherit Supabase's default `verify_jwt = true`.

| Function | Category |
|----------|----------|
| `auth-bootstrap` | Auth |
| `auth-otp-request` | Auth |
| `auth-otp-verify` | Auth |
| `bir-urgent-alert` | Finance |
| `bugbot-control-plane` | Ops |
| `catalog-sync` | Data |
| `config-publish` | Config |
| `consumer-heartbeat` | Ops |
| `context-resolve` | AI |
| `docs-ai-ask` | AI |
| `docs-ai-enhanced` | AI |
| `email-dispatcher` | Email |
| `email-events` | Email |
| `embed-chunk-worker` | AI |
| `executor` | Ops |
| `expense-policy-check` | Finance |
| `health` | Ops |
| `jobs-worker` | Ops |
| `lib-brain-sync` | AI |
| `llm-webhook-ingest` | AI |
| `m365-copilot-broker` | Integration |
| `marketplace-webhook` | Integration |
| `mcp-gateway` | MCP |
| `memory-ingest` | AI |
| `odoo-proxy` | Odoo |
| `odoo-template-export` | Odoo |
| `odoo-webhook` | Odoo |
| `ops-advisory-scan` | Ops |
| `ops-convergence-scan` | Ops |
| `ops-do-ingest` | Ops |
| `ops-fixbot-dispatch` | Ops |
| `ops-github-webhook-ingest` | Ops |
| `ops-health` | Ops |
| `ops-ingest` | Ops |
| `ops-job-worker` | Ops |
| `ops-mailgun-ingest` | Ops |
| `ops-memory-read` | Ops |
| `ops-memory-write` | Ops |
| `ops-metrics-ingest` | Ops |
| `ops-ppm-rollup` | Ops |
| `ops-runner` | Ops |
| `ops-search-query` | Ops |
| `ops-secrets-scan` | Ops |
| `ops-summary` | Ops |
| `ops-trigger-build` | Ops |
| `ops-workitems-processor` | Ops |
| `plane-github-sync` | Integration |
| `plane-sync` | Integration |
| `platformkit-introspect` | Ops |
| `pulser-intent-runner` | Ops |
| `pulser-slack-handler` | Integration |
| `realtime-sync` | Data |
| `repo-hygiene-runner` | Ops |
| `run-executor` | Ops |
| `secret-smoke` | Security |
| `seed-odoo-finance` | Finance |
| `semantic-export-osi` | AI |
| `semantic-import-osi` | AI |
| `semantic-query` | AI |
| `sentry-plane-sync` | Integration |
| `serve-erd` | Docs |
| `shadow-odoo-finance` | Finance |
| `skill-eval` | AI |
| `sync-kb-to-schema` | Data |
| `three-way-match` | Finance |
| `tick` | Ops |
| `vendor-score` | Finance |
| `webhook-ingest` | Data |
| `zoho-mail-bridge` | Email |

---

## Security Recommendations

1. **Add explicit config for webhook-receiving functions**: `ops-github-webhook-ingest`, `ops-mailgun-ingest`, `odoo-webhook`, `marketplace-webhook`, `webhook-ingest` likely need `verify_jwt = false` with in-function signature validation. Currently they inherit `verify_jwt = true` which may cause webhook delivery failures if the sender cannot provide a JWT.

2. **Audit `copilot-chat` and `ipai-copilot`**: Both have `verify_jwt = false` with no stated auth method. If these are accessible from the public internet, they should either enforce auth in-function or be restricted via network policy.

3. **Document in-function auth for all `verify_jwt = false` functions**: Each function that bypasses gateway JWT should have a code comment explaining its auth mechanism.

---

## How to Update This Document

1. Add/modify `[functions.<name>]` blocks in `supabase/config.toml`
2. Run: `grep -E "^\[functions\.|verify_jwt" supabase/config.toml` to verify
3. Update this matrix accordingly
4. Commit both files together
