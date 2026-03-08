# Platform Contracts Index — InsightPulse AI

> A contract defines what crosses a boundary between two SSOT domains.
> Every contract has an owning SSOT, a consuming party, and a validation mechanism.
> Contracts marked **[pending]** have no committed document yet.
>
> Last updated: 2026-03-02 (C-23–C-24 added: Agent Workflows, Tool Permissions — MAF parity P0)

---

## Index

| #    | Contract                                               | Source SSOT domain                          | Consumer domain                           | Status     | Validator                                  |
| ---- | ------------------------------------------------------ | ------------------------------------------- | ----------------------------------------- | ---------- | ------------------------------------------ |
| C-01 | [DNS & Email](DNS_EMAIL_CONTRACT.md)                   | Cloudflare DNS (`infra/dns/`)               | Zoho Mail, Vercel, Odoo                   | ✅ Active  | `dns-ssot-apply.yml`                       |
| C-02 | ~~[Outbound Mail Bridge](MAIL_BRIDGE_CONTRACT.md)~~    | Odoo `mail.mail`                            | ~~Supabase Edge Function `zoho-mail-bridge`~~ | ❌ Deprecated | Superseded by C-26 |
| C-03 | [JWT Trust](JWT_TRUST_CONTRACT.md)                     | Supabase Auth                               | Odoo middleware, Vercel Edge              | 🔲 Pending | —                                          |
| C-04 | [Task Queue](TASK_QUEUE_CONTRACT.md)                   | n8n workflows                               | `ops.task_queue` (Supabase)               | 🔲 Pending | —                                          |
| C-05 | [Design Tokens](DESIGN_TOKENS_CONTRACT.md)             | Figma                                       | `packages/design-tokens/tokens.json`      | 🔲 Pending | —                                          |
| C-06 | [Vercel Environment Variables](VERCEL_ENV_CONTRACT.md) | Vercel dashboard                            | Next.js apps                              | 🔲 Pending | `vercel-env-leak-guard.yml`                |
| C-07 | [Supabase Vault Secrets](SUPABASE_VAULT_CONTRACT.md)   | Supabase Vault                              | Edge Functions, pg_cron                   | ✅ Active  | `20260221000001_vault_secret_registry.sql` |
| C-08 | [Platform Audit Events](AUDIT_EVENTS_CONTRACT.md)      | All services                                | `ops.platform_events` (Supabase)          | 🔲 Pending | —                                          |
| C-09 | [GitHub Actions Secrets](GH_SECRETS_CONTRACT.md)       | GitHub org secrets                          | CI workflows                              | 🔲 Pending | `platform-guardrails.yml`                  |
| C-10 | [Supabase Auth SMTP](SUPABASE_AUTH_SMTP_CONTRACT.md)   | Supabase Auth                               | Zoho SMTP (`smtppro.zoho.com`)            | ✅ Active  | `RB_SUPABASE_AUTH_SMTP_VERIFY.md`          |
| C-11 | [Edge Functions](SUPABASE_EDGE_FUNCTIONS_CONTRACT.md)  | `supabase/functions/`                       | All integration bridges                   | ✅ Active  | `ssot-surface-guard.yml`                   |
| C-12 | [Supabase Cron](SUPABASE_CRON_CONTRACT.md)             | `supabase/migrations/*_cron_*.sql`          | pg_cron jobs                              | ✅ Active  | `cron.job_run_details`                     |
| C-13 | [Nightly Repo Hygiene](SUPABASE_CRON_REPO_HYGIENE.md)  | `automations/repo_hygiene/jobs/nightly.yml` | `ops.repo_hygiene_*` (Supabase)           | ✅ Active  | `ops.repo_hygiene_runs`                    |
| C-14 | [Supabase ETL](SUPABASE_ETL_CONTRACT.md)               | Supabase Postgres (CDC/WAL)                 | Analytics Buckets (Iceberg) / BigQuery    | ✅ Active  | `pg_stat_replication`                      |
| C-15 | [Odoo Settings](ODOO_SETTINGS_CONTRACT.md)             | `config/odoo/settings.yaml`                 | Odoo `ir.config_parameter`                | ✅ Active  | `apply_settings.py --verify-only`          |
| C-16 | Odoo Auth Providers                                    | `config/odoo/auth_providers.yaml`           | Odoo `auth.oauth.provider`                | ✅ Active  | `apply_auth_providers.py --enforce`        |
| C-17 | [AI Copilot Bridge](AI_COPILOT_CONTRACT.md)            | `platform/ai/providers/gemini_tools.ts`     | `addons/ipai/ipai_ai_copilot/`            | 🔲 Planned | `check_parity_and_bridges_ssot.py`         |
| C-18 | [DigitalOcean API](C-DO-01-digitalocean-api.md)        | DigitalOcean v2 REST API                    | `ops.do_*` tables, ops-console UI         | ✅ Active  | `ssot/providers/digitalocean/provider.yaml` |
| C-19 | [Odoo.sh Parity](C-ODOOS-01-parity.md)                 | ops-console platform                        | All console modules                       | ✅ Active  | `spec/odooops-console/constitution.md`     |
| C-20 | [Mail Catcher](C-MAIL-01-mail-catcher.md)              | Mailgun relay + `ops.mail_events`           | ops-console Observability                 | 🔲 Planned | CI gate (task 33)                          |
| C-21 | [Plane Work Items Webhooks](C-PLANE-02-workitems-webhooks.md) | `ssot/sources/plane/work_items.yaml` | `ops.work_items`, ops-console Boards view | 🔲 Planned | `apps/ops-console/app/api/webhooks/plane/route.ts` |
| C-22 | [GitHub Issues Webhooks](C-GH-02-workitems-webhooks.md)       | `ssot/sources/github/work_items.yaml` | `ops.work_items`, ops-console Boards view | 🔲 Planned | `apps/ops-console/app/api/webhooks/github/route.ts` |
| C-23 | [Agent Workflows](C-AGENT-WORKFLOWS-01.md)                    | `ssot/agents/interface_schema.yaml`   | All IPAI agent skills, executor runtimes  | ✅ Active  | `scripts/ci/validate_skills_registry.py` |
| C-24 | [Tool Permissions](C-TOOLS-PERMISSIONS-01.md)                 | `ssot/tools/registry.yaml`            | All IPAI agent skills (`ssot/agents/skills.yaml`) | ✅ Active | `scripts/ci/validate_skills_registry.py` |
| C-25 | [Governed Tool Specs](../contracts/tools/)                    | `contracts/tools/*.md`                | `ipai_ai_copilot` tool dispatch                   | ✅ Active | `scripts/index_corpus_registry.py --check` |
| C-26 | [Mail Architecture](MAIL_ARCHITECTURE_CONTRACT.md)            | Mailgun SMTP (`mg.insightpulseai.com`) + Zoho (root) | Odoo `ir.mail_server`, business mailboxes | ✅ Active | `C-MAIL-01` CI gate |
| C-27 | [Addons Manifest](ADDONS_MANIFEST_CONTRACT.md)               | `config/addons.manifest.yaml`         | `docker/Dockerfile.unified`, `oca-aggregate.yml`  | ✅ Active | `addons-manifest-guard.yml`                |

---

## C-01 — DNS & Email Contract

**File**: `docs/contracts/DNS_EMAIL_CONTRACT.md`
**SSOT**: `infra/dns/subdomain-registry.yaml` + `infra/dns/zoho_mail_dns.yaml`
**Consumers**: Cloudflare (via Terraform), Zoho Mail SPF/DKIM, Vercel alias, Odoo `web.base.url`

**Invariants**:

- A subdomain must exist in `subdomain-registry.yaml` before any service uses it.
- SPF, DKIM, DMARC records live in `zoho_mail_dns.yaml` — never in the main registry.
- Terraform apply is the only valid way to push records to Cloudflare.

**Validator**: `dns-ssot-apply.yml` (path-triggered on `infra/dns/**`)

---

## C-02 — Outbound Mail Bridge Contract (DEPRECATED)

> **DEPRECATED**: Superseded by C-26 (Mail Architecture Contract). Odoo outbound mail now uses
> standard `ir.mail_server` → Mailgun SMTP directly. The `ipai_mail_bridge_zoho` module and
> `zoho-mail-bridge` Edge Function are no longer the canonical path.
> See `docs/contracts/MAIL_ARCHITECTURE_CONTRACT.md` for the current policy.

**File**: `docs/contracts/MAIL_BRIDGE_CONTRACT.md` _(deprecated — kept for historical reference)_
**SSOT**: ~~`addons/ipai/ipai_mail_bridge_zoho/`~~ + ~~`supabase/functions/zoho-mail-bridge/`~~
**Consumer**: ~~Any Odoo `mail.mail` record with `state=outgoing`~~

**Protocol**:

```
POST <ZOHO_MAIL_BRIDGE_URL>?action=send_email
Headers:
  x-bridge-secret: <ZOHO_MAIL_BRIDGE_SECRET>   ← 32+ char random shared secret
  Content-Type: application/json
Body:
  { from, to, subject, htmlBody?, textBody?, replyTo? }
Response (200 OK):
  { ok: true }
Response (error):
  { ok: false, code: ErrorCode, message: string }
  ErrorCodes: UNAUTHORIZED | BAD_REQUEST | METHOD_NOT_ALLOWED | NOT_FOUND | SERVICE_ERROR | NOT_CONFIGURED
```

**Env vars (Odoo container)**:

- `ZOHO_MAIL_BRIDGE_URL` — Supabase Edge Function URL
- `ZOHO_MAIL_BRIDGE_SECRET` — 32+ char random secret (NOT the Supabase anon key)

**Env vars (Supabase Vault)**:

- `BRIDGE_SHARED_SECRET` — must match `ZOHO_MAIL_BRIDGE_SECRET`
- `ZOHO_CLIENT_ID`, `ZOHO_CLIENT_SECRET`, `ZOHO_REFRESH_TOKEN`, `ZOHO_ACCOUNT_ID`

**Fallback behavior**: If `ZOHO_MAIL_BRIDGE_URL` or `ZOHO_MAIL_BRIDGE_SECRET` is absent, Odoo falls back to standard SMTP (`smtppro.zoho.com:587`). Note: this port is blocked on DigitalOcean droplets.

**Audit trail**: Every `send_email` call is audited to `ops.platform_events` (actor: `zoho-mail-bridge`).

**[MANUAL_REQUIRED]** Zoho OAuth2 credentials must be set in Supabase Vault before `send_email` works:

```bash
supabase secrets set --project-ref spdtwktxdalcfigzeqrz \
  ZOHO_CLIENT_ID=<from Zoho API Console> \
  ZOHO_CLIENT_SECRET=<from Zoho API Console> \
  ZOHO_REFRESH_TOKEN=<from OAuth2 flow> \
  ZOHO_ACCOUNT_ID=<from /api/accounts>
```

---

## C-03 — JWT Trust Contract [pending]

**File**: `docs/contracts/JWT_TRUST_CONTRACT.md` _(not yet created)_

**Purpose**: Define how Odoo (Python/Werkzeug middleware) validates Supabase-issued JWTs.

**Key fields to specify**:

- JWKS endpoint URL
- Audience (`aud`) claim expected value
- Issuer (`iss`) claim
- Required scopes / roles
- Token expiry handling (`jwt_expiry = 3600` in `supabase/config.toml`)

**Consumers**: Odoo session middleware (`ipai_auth_oidc`), Vercel Edge middleware

---

## C-04 — Task Queue Contract [pending]

**File**: `docs/contracts/TASK_QUEUE_CONTRACT.md` _(not yet created)_

**Purpose**: Define the schema of `ops.task_queue` (Supabase) and the n8n → queue → consumer flow.

**Key fields**: `task_type`, `payload`, `status`, `created_at`, `processed_at`, `error`

---

## C-05 — Design Tokens Contract [pending]

**File**: `docs/contracts/DESIGN_TOKENS_CONTRACT.md` _(not yet created)_

**Purpose**: Define the schema of `packages/design-tokens/tokens.json` and the Figma → export → commit flow.

---

---

## C-14 — Supabase ETL Contract

**File**: `docs/contracts/SUPABASE_ETL_CONTRACT.md`
**SSOT**: Supabase Postgres (WAL logical replication)
**Consumers**: Analytics Buckets (Iceberg), BigQuery

**Purpose**: Route OLAP workloads off the OLTP database via CDC replication.

**Invariants**:

- ETL destinations are non-authoritative replicas — never write-back into SSOT
- Primary key required on every replicated table
- `vault.secrets`, `auth.users` (PII), and Supabase system tables must never be replicated
- Schema DDL changes must land in Supabase migration before ETL replicates them

**Monitoring**: `pg_stat_replication` slot lag; pg_cron alert if lag > 5 min

**[MANUAL_REQUIRED]**: ETL pipeline configuration is UI-only in Supabase dashboard (as of 2026-02).

---

## Contract Governance

### Adding a new contract

1. Create `docs/contracts/<NAME>_CONTRACT.md` with:
   - Source SSOT domain
   - Consumer domain
   - Protocol / schema
   - Invariants
   - Validator (CI workflow or script)
2. Add a row to the Index table above.
3. Add a path guard to `.github/workflows/ssot-surface-guard.yml`.

### Contract validation levels

| Level       | Meaning                                                 |
| ----------- | ------------------------------------------------------- |
| ✅ Active   | Contract doc exists + CI enforces it                    |
| ⚠️ Partial  | Contract doc exists but CI enforcement missing          |
| 🔲 Pending  | Contract conceptually defined here; no separate doc yet |
| ❌ Violated | Known violation — must be remediated                    |
