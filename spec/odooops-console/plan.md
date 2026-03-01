# OdooOps Console — Plan
# Spec: spec/odooops-console/
# Slug: odooops-console
# Last updated: 2026-03-01

---

## Architecture

### UI Layer

Next.js 15 App Router (TypeScript, Tailwind CSS) deployed on Vercel.
Read-only surfaces backed by Supabase `ops.*` tables and Storage artifacts.

### Data Plane (Supabase `spdtwktxdalcfigzeqrz`)

`ops.*` tables as the operational SSOT mirror:

| Table | Purpose |
|-------|---------|
| `ops.builds` | GitHub Actions CI builds |
| `ops.deployments` | Vercel deployment events |
| `ops.backups` | Snapshot manifests |
| `ops.backup_jobs` | Backup job runs |
| `ops.platform_events` | Unified audit stream |
| `ops.advisor_runs` | Advisor scan runs |
| `ops.advisor_findings` | Advisor findings |
| `ops.secret_sync_runs` | Secret sync audit |
| `ops.integrations_catalog` | Integration catalog (PlanGuard) |
| `ops.integrations_installations` | Installed integrations |
| `ops.do_droplets` | DO Droplet inventory |
| `ops.do_databases` | DO managed DB clusters |
| `ops.do_firewalls` | DO Cloud Firewalls |
| `ops.do_actions` | DO action audit |
| `ops.do_ingest_runs` | DO ingest audit |
| `ops.mail_events` | Mail catcher events |

### Control Plane Jobs (Edge Functions)

Job executor writes:
- `ops.run_events` (audit trail for all jobs)
- Domain tables per job type
- Artifacts to Supabase Storage

---

## Provider Adapters (Shared Middleware)

All providers implement:

- Auth abstraction (token injection)
- Pagination helpers (offset or cursor as needed)
- Retry/backoff with bounded attempts (max 5)
- Typed error envelopes: `{ ok: false, error: string, code?: number }`

| Provider | Pagination | Auth | Worker |
|----------|-----------|------|--------|
| Supabase management | cursor | service role key | inline |
| Vercel | cursor | Bearer token | inline |
| DigitalOcean | offset (page/per_page) | Bearer token | `ops-do-ingest` |
| Mailgun | — (webhooks) | HMAC signed payload | `ops-mailgun-ingest` |
| Slack | cursor | Bot token | `ops-slack-notify` |

---

## Feature Maturity Map

| Page | Current | Target |
|------|---------|--------|
| Overview | beta | prod |
| Environments | beta | prod |
| Deployments | beta | prod |
| Builds | beta | prod |
| Policy Gates | beta | prod |
| Backups | beta | prod |
| Logs | beta | prod |
| Database | scaffold | beta |
| Control Plane | scaffold | beta |
| Modules | scaffold | beta |
| Integrations | prod | prod |
| Advisor | beta | prod |
| Observability | beta | prod |
| Metrics | beta | prod |
| Runbooks | scaffold | beta |
| Settings | beta | prod |
| DigitalOcean | beta | prod |

---

## Known Gaps to Close (Ordered)

1. ~~`/logs` route returns 404~~ → **Fixed** (committed `df209ea2c`).
2. Secret sync workflow returns empty/non-JSON → enforce JSON-only API envelope + safe parsing.
3. Control Plane cards: replace static "scaffold" labels with SSOT maturity + actual data sources.
4. Modules: implement SSOT waves + CI artifacts ingestion + diffs per env.

---

## Work items ingestion topology

### Plane

- **Default**: webhooks → ingest endpoint → delivery ledger → async processor → ops.work_items upsert.
- Fallback: scheduled poller (cursor pagination + rate-limit handling) for drift repair.

### GitHub Issues

- **Default**: GitHub webhooks for issues → delivery ledger → async processor → ops.work_items upsert.
- Fallback: scheduled poller for drift repair and missed deliveries.

### Idempotency

- Upserts keyed by `work_item_ref`.
- Webhook deliveries are persisted **before** any side effects; re-deliveries are no-ops.
- Processing is async by default (durable enqueue → immediate 200).

---

## Odoo.sh Parity Implementation Map

| Odoo.sh Feature | OdooOps Console Module | Backing System | Evidence Artifact |
|-----------------|----------------------|----------------|-------------------|
| GitHub integration | Builds + Deployments | GitHub Actions + Vercel | `ops.builds`, GitHub run links |
| Clear logs | Logs | `ops.platform_events` ingest | log queries + saved filters |
| Web shell | Runbooks / Env actions | Remote exec adapter | `ops.exec_sessions` ledger |
| Module dependencies | Modules + Policy Gates | SSOT allowlist + CI checks | `module_status_*.txt` + diffs |
| Runbot CI | Builds | CI pipeline | junit + summary artifacts |
| Mail catcher | Observability / Mail Events | Mailgun relay + `ops.mail_events` | mail event records |
| Backups | Backups | `ops.backups` + job executor | snapshot manifests + restore logs |
| Monitoring | Overview / Observability | DO + Supabase metrics | healthcheck runs + metric snapshots |

---

## Odoo.sh Restrictions Modeled as Policies

- **Jobs**: max duration per run, retry policy, auto-disable on repeated timeouts.
- **Staging/dev**: explicit concurrency limits in UI and job scheduler (single-worker semantics).
- **SMTP**: block port 25; staging/dev must route via mail catcher (Mailgun relay port 2525/587).
- **DB object-count gate**: CI fails if `tables + sequences > ~10,000` (Odoo.sh ceiling parity).
- **Addons paths**: support multiple addons folders + OCA submodules; CI validates no path drift.
- **Base images**: treat as immutable; all deps via `requirements.txt`, no ad-hoc `apt install`.

---

## Mail Catcher Architecture (Odoo.sh Parity)

### Outbound Policy

- **PROD**: transactional SMTP (Mailgun or equivalent), explicitly configured, full audit.
- **STAGE/DEV**: must route to catcher transport (`smtp.mailgun.org:2525` or `587`); never uses prod credentials.

Evidence anchor: captured message `subject: E2E-MAILGUN-ODOO-TEXT`,
`transport: smtp.mailgun.org:2525`, `from: no-reply@mg.insightpulseai.com`.

### Evidence Capture

Mailgun webhooks → `ops-mailgun-ingest` Edge Function (signed payload verification) → `ops.mail_events`.

### UI Surface

Read-only "Mail Catcher" panel under **Observability**:
- Last 50 captured events, filterable by env.
- Columns: stamp / subject / from / to / transport / env.

### CI Parity Gate

Gate fails when:
- STAGE/DEV `SMTP_HOST` ≠ `smtp.mailgun.org`
- STAGE/DEV `SMTP_PORT` = `25`
- STAGE/DEV references prod mail credentials

---

## Integration Catalog Policy (Baseline-Plan)

Decision order for new integrations:

1. Supabase primitive
2. Supabase partner integration
3. Vercel marketplace integration
4. Custom bridge (Edge Function + `ops.*` tables + Storage artifacts)

---

## Evidence Artifacts Standard

Every automated operation outputs:

- Run record in the relevant `ops.*` table
- Linkable artifact (text/json) in Supabase Storage when appropriate
- GitHub Actions run link for CI-derived signals
