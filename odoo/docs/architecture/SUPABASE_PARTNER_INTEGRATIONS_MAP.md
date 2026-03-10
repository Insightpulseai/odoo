# SUPABASE_PARTNER_INTEGRATIONS_MAP.md

This document maps the four Supabase "Works With" partner integrations used in the InsightPulse AI stack. Each integration has a per-file SSOT record under `ssot/integrations/`. This document provides a human-readable summary and cross-reference.

**Supabase "Works With" program**: https://supabase.com/partners/integrations

---

## Summary Table

| Integration | Category | SSOT Owner | Required Secrets | Allowed Egress | Write Boundaries |
|---|---|---|---|---|---|
| `cloudflare_workers` | edge_runtime | `ssot/integrations/cloudflare_workers.yaml` | `supabase_anon_key` (default); `supabase_service_role_key` (exception only) | `*.supabase.co` | Read-only via PostgREST unless explicitly privileged; no direct Postgres |
| `vercel_hosting` | hosting | `ssot/integrations/vercel_hosting.yaml` | `supabase_anon_key`, `supabase_service_role_key` | `*.supabase.co`, `*.vercel.app` | Server-only for service role key; `NEXT_PUBLIC_` prefix only for anon key |
| `supabase_wrappers_stripe` | postgres_fdw | `ssot/integrations/supabase_wrappers_stripe.yaml` | `stripe_secret_key` (via Vault UUID) | `api.stripe.com` | stripe.* schema is read-only by default; no DML on FDW tables |
| `n8n_automation` | automation_runner | `ssot/integrations/n8n.yaml` | `n8n_api_key`, `n8n_webhook_secret` | `*.n8n.io`, `n8n.insightpulseai.com` | n8n writes to ops.runs via Supabase PostgREST; no direct Odoo DB writes |

---

## Integration Details

### 1. Cloudflare Workers (Edge Runtime)

**Archetype**: Edge function calling Supabase over HTTP (PostgREST). No persistent DB connections. V8 isolates run at Cloudflare edge PoPs.

**Boundary Rules**:
- Workers use anon key by default — RLS is the primary access control layer.
- Service role requires a per-worker SSOT exception entry in `cloudflare_workers.yaml` under `service_role_exceptions`.
- No direct Postgres connection (Workers runtime lacks TCP) — all DB access via PostgREST HTTP.
- Secrets injected via Cloudflare env vars (wrangler.toml `[vars]` or dashboard); never hardcoded in source.

**Key Risks**:
- **Service role misuse** (medium): A Worker accidentally using service role bypasses all RLS. Mitigate by defaulting to anon key and requiring exception entries.
- **Env var drift** (low): Cloudflare dashboard env vars are not tracked in source. Mitigate by documenting expected names in SSOT and verifying wrangler.toml.

**Reference**: `ssot/integrations/cloudflare_workers.yaml`

---

### 2. Vercel Hosting (Next.js Apps)

**Archetype**: Deployment fabric for all `apps/*` Next.js applications. Each app has a dedicated Vercel project. Env vars propagate Supabase credentials to deployed functions and browser clients.

**Boundary Rules**:
- App source directories are `apps/*` — no monorepo root deployments.
- `SUPABASE_URL` and `SUPABASE_ANON_KEY` are always Vercel env vars; never hardcoded.
- `SUPABASE_SERVICE_ROLE_KEY` must be marked sensitive and server-only — never with `NEXT_PUBLIC_` prefix.
- `vercel.json` may reference env var names but never values.
- `KEY_MISSING` behavior (when env var absent) must be tested in CI before merge to production.

**Known Apps**:

| App Path | Vercel Project | Notes |
|---|---|---|
| `apps/workspace/` | `ops-console` | Ops console or workspace |
| `apps/ops-console/` | `odoo-ops-console` | Primary internal admin UI |
| `apps/slack-agent/` | `slack-agent` | Nitro app (vercel preset) |

**Key Risks**:
- **Env var drift** (medium): Vars added/removed in Vercel dashboard without updating SSOT cause silent KEY_MISSING failures at runtime.
- **Build secrets exposure** (low): `console.log(process.env...)` in build scripts can leak values to Vercel build logs.

**Reference**: `ssot/integrations/vercel_hosting.yaml`

---

### 3. Supabase Wrappers — Stripe FDW

**Archetype**: Postgres Foreign Data Wrapper (FDW) via Supabase Wrappers extension. Stripe API is exposed as SQL foreign tables (e.g., `stripe.customers`, `stripe.subscriptions`). Credentials stored in Supabase Vault — not in the pg_foreign_server catalog as plaintext.

**Required Extensions**: `wrappers` + `pg_net` — both installed via committed migration.

**Boundary Rules**:
- `stripe.*` schema is read-only by default — no DML (INSERT/UPDATE/DELETE) against FDW foreign tables.
- Only `service_role` and explicitly granted DB roles may query `stripe.*` — never `anon` or `authenticated` directly.
- Vault secret must be referenced via `api_key_id` (UUID) in `CREATE SERVER OPTIONS` — never the raw key value.
- All FDW setup (`CREATE EXTENSION`, `CREATE SERVER`, `CREATE FOREIGN TABLE`) requires a committed migration.
- Schema grants must be explicit — never `GRANT TO public`.

**Key Risks**:
- **Vault bypass** (high): Placing the Stripe key as plaintext in `pg_foreign_server OPTIONS` stores it unencrypted in the system catalog. Always use `api_key_id` (Vault UUID).
- **Overly permissive grants** (medium): Granting `SELECT` on `stripe.*` to `authenticated` or `anon` exposes all Stripe payment data to any user reachable via Supabase REST API.

**Reference**: `ssot/integrations/supabase_wrappers_stripe.yaml`

---

### 4. n8n Automation (Automation Runner)

**Archetype**: Self-hosted n8n instance running automation workflows. Acts as an automation runner that enqueues tasks into `ops.runs` via Supabase PostgREST. Triggered by external systems (GitHub Actions, Slack agent, scheduled cron).

**Boundary Rules**:
- n8n writes to `ops.runs` via Supabase PostgREST — no direct Odoo DB writes.
- n8n workflows use credential references, not literal secret values in JSON exports.
- n8n is not a write surface to SoR (Odoo) — all Odoo operations route through the task worker.

**Key Risks**:
- Credential leakage in workflow JSON exports if literal values are used instead of credential references.
- Webhook endpoint exposure if `n8n_webhook_secret` is not rotated on team member offboarding.

**Reference**: `ssot/integrations/n8n.yaml`

---

## Secrets Cross-Reference

All secrets referenced by these integrations are registered in `ssot/secrets/registry.yaml`.

| Secret Key | Registry Entry | Primary Consumers |
|---|---|---|
| `supabase_anon_key` | `registry.yaml#supabase_anon_key` | Cloudflare Workers (edge), Vercel apps (`NEXT_PUBLIC_SUPABASE_ANON_KEY`) |
| `supabase_service_role_key` | `registry.yaml#supabase_service_role_key` | Vercel server-only, CI migrations (exception path for Workers) |
| `stripe_secret_key` | `registry.yaml#stripe_secret_key` | Supabase Vault → Stripe FDW `api_key_id` |
| `vercel_token` | `registry.yaml#vercel_token` | GitHub Actions CI (programmatic deploys only; omit if push-to-deploy) |
| `n8n_api_key` | `registry.yaml#n8n_api_key` | Supabase Vault, external workflow triggers |
| `n8n_webhook_secret` | `registry.yaml#n8n_webhook_secret` | Supabase Vault, n8n webhook node auth |

---

## Per-Integration SSOT Files

| Integration | File |
|---|---|
| Cloudflare Workers | `ssot/integrations/cloudflare_workers.yaml` |
| Vercel Hosting | `ssot/integrations/vercel_hosting.yaml` |
| Supabase Wrappers (Stripe) | `ssot/integrations/supabase_wrappers_stripe.yaml` |
| n8n Automation | `ssot/integrations/n8n.yaml` |
| Integration Index | `ssot/integrations/_index.yaml` |
| Secrets Registry | `ssot/secrets/registry.yaml` |

---

*Last updated: 2026-03-01*
