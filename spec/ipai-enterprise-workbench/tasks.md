# Tasks — IPAI Enterprise Workbench

## M1 — Workspace (Odoo + Superset + optional n8n)
- [ ] Add deterministic compose file for workbench dev stack (Odoo+Postgres+Superset [+n8n])
- [ ] Ensure bind-mounted addons for fast iteration (Odoo reload pattern documented)
- [ ] Add `scripts/doctor_workbench.sh` (checks ports, DB reachability, container health)
- [ ] Add CI job to smoke-test `docker compose config` + service boot (headless)

## M2 — Finance PPM Canonicalization (Workbook → Seeds)
- [ ] Review uploaded workbook and reconcile all sheets into canonical seed model
- [ ] Ensure seed generator outputs:
  - [ ] task_code alignment
  - [ ] canonical 6-stage mapping
  - [ ] CSV exports
  - [ ] `--validate` mode
- [ ] Ensure stage import artifacts exist:
  - [ ] XML data import for stages
  - [ ] CSV templates for stages/tasks
- [ ] Add/confirm seed drift gate workflow (regen then `git diff --exit-code`)
- [ ] Confirm OCA aggregation includes required repos (project/queue/reporting-engine) and lock is updated

## M3 — Superset BI
- [ ] Create read-only role and SQL grants script for analytics access
- [ ] Define stable analytics views for Finance PPM (stage/state, deadlines, ownership, overdue)
- [ ] Add Superset bootstrap config (admin bootstrap via env; no UI dependency)
- [ ] Add importable dashboards JSON:
  - [ ] Finance PPM progress
  - [ ] Deadline calendar / SLA
  - [ ] Exceptions/overdue
- [ ] Add verification script for Superset dataset queries

## M4 — Supabase + n8n + MCP
- [ ] Add Supabase ops schema migrations (runs, run_events, artifacts)
- [ ] Add n8n workflows:
  - [ ] monthly close reminders
  - [ ] escalation ladder
  - [ ] approval request/response capture
  - [ ] artifact publishing (CSV/validation outputs)
- [ ] Expose MCP tools:
  - [ ] seed regen + validate
  - [ ] oca aggregation verify
  - [ ] repo drift gates runner
  - [ ] deployment readiness check
- [ ] Add runbook docs under GitHub Pages base

## M5 — IPAI Design System Modules
- [ ] Create SSOT `design/tokens/tokens.json`
- [ ] Implement `ipai_design_system` (and optional split modules) as adapters:
  - [ ] Odoo OWL theme adapter
  - [ ] web adapter (Workbench UI)
  - [ ] future Mattermost adapter hooks
- [ ] Add visual regression checks where feasible (token snapshots)

## M6 — Odoo 19 Readiness + "EE Replacement" mapping refresh
- [ ] Create Odoo 19 compatibility matrix (CE + OCA + IPAI)
- [ ] Add upgrade preflight script and gating tests
- [ ] Refresh EE/IAP replacement mapping docs
- [ ] Add CI branch workflow for Odoo 19 install validation

## Global Documentation & Canonical URLs
- [ ] Replace docs base references to `https://docs.insightpulseai.net/erp` with `https://jgtolentino.github.io/odoo-ce/`
- [ ] Ensure README and docs index pages point to GitHub Pages canonical base
- [ ] Add `DEPLOYMENT_STATE_CURRENT.md` update step into release process

