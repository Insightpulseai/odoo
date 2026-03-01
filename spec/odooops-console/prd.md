# OdooOps Console — PRD
# Spec: spec/odooops-console/
# Slug: odooops-console
# Last updated: 2026-03-01

---

## Product Overview

OdooOps Console is a real-time operational dashboard that manages an Odoo CE runtime
and its supporting infrastructure (Vercel + Supabase + DigitalOcean), providing deploy
visibility, policy enforcement, backups, integration status, and operational guidance.

**Vercel team**: `tbwa`
**Vercel project**: `odooops-console` (id: `prj_0pVE25oMd1EHDD1Ks3Xr7RTgqfsX`)
**Domain**: `https://odooops-console.vercel.app`
**Primary backend**: Supabase `spdtwktxdalcfigzeqrz`

---

## Users

1. **Maintainer (Ops)**: monitors health, runs preflight, rollback, restore/clone backups.
2. **Engineer**: inspects builds, policy gates, modules allowlist compliance, env drift.
3. **Security/Ops reviewer**: validates controls via evidence artifacts and advisory findings.

---

## Odoo.sh Parity Targets

This product aims to replicate the *operational outcomes* of Odoo.sh on our stack
(Vercel + Supabase + DigitalOcean), with explicit deltas documented.

### Parity Pillars (mapped to Odoo.sh)

1. **GitHub Integration**: commit/PR triggers CI + deploy; builds are linkable.
2. **Clear Logs**: real-time logs with filters; browser-viewable.
3. **Web Shell**: shell access to a prod container/build context (or equivalent remote exec).
4. **Module Dependencies**: OCA/submodule allowlist + dependency management; controlled updates.
5. **Continuous Integration**: dedicated runbot-like pipeline with test dashboard.
6. **SSH**: deterministic access mechanism (keys/roles) to runtime surfaces.
7. **Mail Catcher**: staging/dev email capture; no outbound mail leakage.
8. **Staging Branches**: ephemeral staged environments w/ production-like data where allowed.
9. **Backups & Recovery**: regular snapshots + restore/clone workflows.
10. **Monitoring & KPIs**: uptime/availability + health indicators.

### Odoo.sh Restrictions We Model as Constraints

- **No long-lived daemons in build containers**: treat workers as recyclable; jobs must be bounded.
- **Cron/scheduled actions time limits**: enforce job timeouts + auto-disable on repeated timeouts.
- **Staging/dev are resource-constrained**: represent as single-worker / limited concurrency.
- **Outbound SMTP constraints**: enforce "no port 25"; staging/dev mail is captured.
- **Addons folders & submodules**: multiple addons paths detected; OCA submodules supported.
- **No system packages on platform images**: treat base images as immutable; deps via requirements only.
- **Long-polling/websocket limits**: avoid overload; prefer queueing + polling for heavy tasks.
- **DB object count ceiling**: enforce a policy gate (approx. 10k tables+sequences parity guard).

### Explicit Non-Parity

- Odoo.sh "platform API" (create project/branches/rebuild) is not provided by Odoo.sh;
  our control plane *will* provide equivalents via Supabase/Vercel/DO APIs.

---

## Functional Requirements

### FR1 — Platform Overview (prod)
- Show global health, active nodes, audit pass rate, daily deploys.
- Show recent activity (deployments) by env.
- Active Nodes = `COUNT(ops.do_droplets WHERE status='active')` + DB clusters.
- Actions: Export Report, Manage Supabase, Trigger Preflight.

### FR2 — Environments (prod)
- List environments (PROD, STAGE) with host, database, current SHA, health.
- Host = DO Droplet name + ipv4; Database = DO managed PG endpoint.
- Actions: Healthcheck; Rollback (prod only).

### FR3 — Deployments (prod)
- Table of deployments by env with version/author/status/duration/time.
- Data from `ops.run_events` + Vercel deployments API.

### FR4 — Builds (prod)
- CI builds table populated from GitHub Actions → `ops.builds`.
- Links to GitHub Actions run page.

### FR5 — Policy Gates (prod)
- Gate cards: OCA Allowlist, Risk-tier Labels, Diagram Drift, Lint & Tests.
- Each card links to evidence artifacts + GitHub run.

### FR6 — Backups (beta → prod)
- List snapshots with env/type/size/created/retention.
- Actions: Restore, Clone.
- Data source: `ops.backups`, `ops.backup_jobs`, job executor.

### FR7 — Database / Platform Kit (beta)
- Show Supabase project status, link to manager.
- Provide "sync secrets" workflow that writes audit records to `ops.secret_sync_runs`.
- **Acceptance criteria**: API returns JSON envelope: `{ ok: true, pushed: [...], skipped: [...] }` or `{ ok: false, error }`. Never crashes on JSON parsing.

### FR8 — Control Plane (scaffold → beta)
- Surface Supabase management API capabilities: Projects, Branches, Logs, Security.
- Each capability shows maturity label and data-source annotation.

### FR9 — Modules (scaffold → beta)
- Wave tabs (Wave 1–4) sourced from SSOT.
- Installed vs allowlisted diff per environment.
- Evidence artifact links (`module_status_*.txt`, diff JSON).

### FR10 — Integrations (prod)
- Catalog-driven, not limited to currently installed.
- Default filter: `baseline_allowed = true`.
- Data: `ops.integrations_view` (LEFT JOIN catalog + installations).

### FR11 — Advisor (beta)
- Pillars: Security, Cost, Reliability, Ops Excellence, Performance.
- "Run Scan" triggers a job; findings persisted in `ops.advisor_findings`.

### FR12 — Observability + Metrics (beta)
- Observability cards (DO + Supabase metrics) with external links.
- Metrics page shows Prometheus scrape endpoint and config template.

### FR13 — Runbooks (scaffold → beta)
- Render `docs/ops/runbooks/*` as read-only documentation.

### FR14 — Settings (beta)
- Display platform config (Supabase project ref/url, Vercel project id).
- Show required secret presence for AI Gateway and integrations.

### FR15 — Logs (beta)
- Unified log stream: CI, runtime, DB, audit.
- Filters: Env, Service, Level, Correlation ID, Time Range.
- Data source: `ops.platform_events`, `ops.jobs`.

### FR16 — DigitalOcean (beta)
- Cards: Droplets, Databases, Networking, Monitoring.
- Data: `ops.do_droplets`, `ops.do_databases`, `ops.do_firewalls`.
- Powered by `ops-do-ingest` hourly worker.

---

## Non-Functional Requirements

- **No dead routes** (constitution constraint 3)
- **JSON-only internal APIs** (constitution constraint 4)
- **Idempotency** for jobs/event handlers (constitution constraint 6)
- **Baseline-plan bias** (constitution constraint 2)
- **Evidence-first** operations and audit logging (constitution constraint 5)
- **Parity gates** in CI (constitution constraint 12)

---

## Page Maturity Status

| Route | Page | Maturity | Data Source |
|-------|------|----------|-------------|
| `/` | Overview | `beta` | ops.platform_events, ops.do_droplets |
| `/environments` | Environments | `beta` | ops.do_droplets, ops.do_databases |
| `/deployments` | Deployments | `beta` | ops.run_events |
| `/builds` | Builds | `beta` | ops.builds |
| `/policy-gates` | Policy Gates | `beta` | ops.policy_gate_runs |
| `/backups` | Backups | `beta` | ops.backups |
| `/logs` | Logs | `beta` | ops.platform_events, ops.jobs |
| `/database` | Database | `scaffold` | ops.secret_sync_runs (planned) |
| `/control-plane` | Control Plane | `scaffold` | ops.capabilities (planned) |
| `/modules` | Modules | `scaffold` | ops.platform_events (Wave 1) |
| `/integrations` | Integrations | `prod` | ops.integrations_view |
| `/advisor` | Advisor | `beta` | ops.advisor_runs, ops.advisor_findings |
| `/platform/digitalocean` | DigitalOcean | `beta` | ops.do_droplets, ops.do_databases |
| `/observability` | Observability | `beta` | Supabase + DO metrics links |
| `/metrics` | Metrics | `beta` | Prometheus config + SSOT |
| `/runbooks` | Runbooks | `scaffold` | docs/ops/runbooks/* |
| `/settings` | Settings | `beta` | env vars presence |
