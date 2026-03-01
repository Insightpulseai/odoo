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
| `ops.convergence_findings` | Deployment convergence drift findings |
| `ops.maintenance_runs` | Maintenance chore execution |
| `ops.maintenance_run_events` | Maintenance run audit trail |
| `ops.ai_models` | AI provider model inventory |

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
| Convergence | — (internal) | service role | `ops-convergence-scan` |
| FixBot | — (internal) | service role | `ops-fixbot-dispatch` |

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

## Vercel for GitHub Semantics (Contract)

### Deploy-on-push + Deploy-on-PR

- Vercel deploys every push by default, including PR branches.
- If multiple commits push while a build is running on the same branch, Vercel
  finishes the current build then deploys only the latest commit, canceling
  queued intermediates (latest commit wins per branch).
- SSOT implication: treat "canceled superseded builds" as expected, not failures.

### Preview URLs + PR Association

- Each PR gets a unique preview deployment URL; Vercel can post it as a PR comment.
- Vercel uses GitHub's Deployments API: deployments appear in GitHub UI.
- `ops.deployments` stores: `deployment_url`, `environment` (preview|production),
  `pr_number` (nullable), `git_sha`, `github_deployment_id` (nullable).

### Production Branch + Instant Rollback

- Merges/pushes to the production branch update custom domains with the latest
  production deployment.
- Reverting a deployed commit effectively rolls back to the previous production
  deployment on the domain.
- Console "Rollback" modeled as: promote previous production deployment or
  revert commit (Git-first rollback).

### Fork PR Authorization

- PRs from forks require authorization before Vercel deploys (prevents env var /
  OIDC leakage).
- Console must show "Awaiting authorization" state distinctly from "failed".

### Optional GitHub Actions Deployment Mode

- For GHES or "don't expose source to Vercel" scenarios:
  `vercel pull` → `vercel build` → `vercel deploy --prebuilt`.
- Modeled as a toggle in integrations policy.

### Normalized Build Statuses

Map Vercel build states into:
- `success`
- `failed`
- `canceled_superseded` (expected — intermediate build replaced by later commit)
- `awaiting_authorization` (fork PR protection)

---

## FixBot Execution Surfaces

### Purpose

When an error occurs (failed build, gate failure, webhook signature error,
migration failure), the system detects → creates an agent run → invokes
@claude / coding agent → requires verification → opens PR → posts evidence.

### Agent Run Model

Uses existing `ops.agent_runs` + `ops.agent_events` + `ops.agent_artifacts`
tables (renamed in migration `20260213`).

New columns on `ops.agent_runs`:
- `kind` (fix_build | fix_gate | fix_migration | fix_webhook)
- `trigger_source` (vercel | github | supabase | manual)
- `trigger_ref` (deployment_id, run_id, gate_id, etc.)
- `prompt` (Agent Relay Template payload)
- `pr_url` (nullable — set when PR is opened)

### Governance Policy

Defined in `ssot/agents/fixbot_policy.yaml`:
- PR-only (never push to main)
- Require tests + gates to pass
- Max files/lines changed limits
- Forbidden paths (secrets, CI workflows)
- Escalation on repeat failures → create work item

### Trigger Mechanism

1. Gate failure or build failure detected in `ops.*` tables.
2. Dispatcher creates `ops.agent_runs` row with pre-filled prompt.
3. Agent invoked (Slack action or backend trigger).
4. Agent opens PR with fix + evidence.

---

## Deployment Convergence

### Purpose

Periodic maintenance job that detects drift between Git reality and runtime
reality, then drives environments to completion (or raises actionable tickets).

### Signals Checked

| Signal | Description |
|--------|-------------|
| Merged but not deployed | `main` advanced but prod/stage deployed SHA didn't move |
| Deployment failed | Latest build/deploy status is `failed` |
| Deployment incomplete | Deploy succeeded but follow-ups pending (migrations, functions, secrets, DNS) |
| Checklist not verified | Release checklist exists but has unverified items |

### Completion Definition

Per-environment requirements defined in `ssot/maintenance/convergence.yaml`:
- Required migrations (range)
- Required edge functions deployed
- Required env vars present
- Required vault keys present
- Required DNS entries active
- Required gates green

### Runner Behavior

- Level 1 (default): detect + report findings to `ops.convergence_findings`.
- Level 2 (optional): auto-complete safe actions (re-trigger deploy, re-run gate).
- Level 3: escalate persistent items to Slack + work items.

### Cadence

- Every 15 minutes: convergence scan.
- Daily: summarize outstanding findings + open tickets.
- Weekly: auto-close stale items / archive evidence.

---

## Periodic Maintenance Schedule

Defined in `ssot/maintenance/schedules.yaml`:

| Cadence | Chore | Runner |
|---------|-------|--------|
| Daily | CI gates + security scan | CI |
| Daily | Dependency vulnerability scan | Dependabot / CI |
| Daily | Backup freshness check | ops-convergence-scan |
| Daily | Provider inventory ingest (DO) | ops-do-ingest |
| Daily | Log/error rollup | ops-summary |
| Weekly | Dependency upgrade PR window | CI |
| Weekly | Diagram drift enforcement | CI |
| Weekly | RLS/policy drift audit | ops-convergence-scan |
| Weekly | Secrets registry audit | ops-convergence-scan |
| Monthly | Backup restore drill (staging) | manual + ops runner |
| Monthly | Access review (GitHub/Vercel/Supabase/DO) | ops-convergence-scan |
| Monthly | Cost & quota review | ops-convergence-scan |
| Quarterly | Key/token rotation window | manual + ops runner |
| Quarterly | Major version upgrade planning | manual |

---

## DigitalOcean Gradient ADK (Optional Provider)

Deploy agent services as managed endpoints on DigitalOcean Gradient AI Platform.
Console triggers runs and stores evidence.

- **Modules**: agents/ADK, serverless inference, knowledge bases, routing,
  guardrails, insights/logs, tracing, evaluation.
- **Auth**: `GRADIENT_MODEL_ACCESS_KEY` + `DIGITALOCEAN_API_TOKEN` (genai CRUD).
- **Local**: `gradient agent run` → `http://0.0.0.0:8080/run`.
- **Deployed**: `https://agents.do-ai.run/v1/.../<deployment>/run`.
- **Provider SSOT**: `ssot/providers/digitalocean/gradient_adk.yaml`.

---

## Evidence Artifacts Standard

Every automated operation outputs:

- Run record in the relevant `ops.*` table
- Linkable artifact (text/json) in Supabase Storage when appropriate
- GitHub Actions run link for CI-derived signals

---

## Navigation Taxonomy (Vercel-style IA)

Added 2026-03-01. Three top-level sections — **Use Cases**, **Tools**, **Users** — compose existing
pages under `/app/use-cases/`, `/app/tools/`, and `/app/users/` route groups.

### Use Cases

| Route | Title | Surfaces (ops tables / pages) |
|-------|-------|-------------------------------|
| `/use-cases/ai-apps` | AI Apps | `ops.runs` (agent runs), `ops.ai_models` (AI providers), `ops.advisor_findings` (artifacts) |
| `/use-cases/marketing-sites` | Marketing Sites | `ops.deployments` (Vercel deploys), `ops.do_droplets` (domains), `ops.convergence_findings` (edge/DNS drift) |
| `/use-cases/multi-tenant-platforms` | Multi-Tenant Platforms | `ops.do_databases` (Supabase environments), `ops.advisor_findings` (RLS audit), `ops.platform_events` (branch envs) |
| `/use-cases/web-apps` | Web Apps | `ops.integrations_catalog` (integrations), `ops.platform_events` (monitoring), `ops.do_droplets` (metrics) |

### Tools

| Route | Title | Surfaces |
|-------|-------|----------|
| `/tools/integrations` | Integrations | Redirect → `/integrations` (alias only) |
| `/tools/templates` | Templates | Spec kit bundles (`spec/`), runbook templates (`docs/ops/`), CI workflow templates |
| `/tools/partner-finder` | Partner Finder | DIY guides, vendor alternatives, integration decision framework |

### Users

| Route | Title | Surfaces (ops tables / pages) |
|-------|-------|-------------------------------|
| `/users/platform-engineers` | Platform Engineers | `/environments`, `/deployments`, `/backups`, `ops.convergence_findings`, `ops.maintenance_runs` |
| `/users/design-engineers` | Design Engineers | `ops.deployments` (preview URLs), `ops.builds` (build artifacts), `ops.runs` (FixBot fix-it loop) |

### Sidebar Section

A new **Explore** section was added to
`apps/ops-console/components/navigation/sidebar.tsx` containing links to all Use Cases, Tools
(excluding the redirect alias), and Users routes.
