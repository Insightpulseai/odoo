# PLAN — Odoo.sh Clone (Better-than-Odoo.sh)

## Phase 0 — Repo and workflow foundation (Week 0)
- Standard GHCR build workflow (reusable) across org repos
- Standard Codespaces devcontainer rollout across org repos
- Required checks + branch protections

## Phase 1 — Control plane (Supabase)
Deliver `ops_*` schema:
- projects, environments, runs, run_events, artifacts
- backups, restores, approvals, policies
- RBAC tables + RLS policies
Deliver Edge Function runner:
- claim queued runs
- write events/artifacts
- update status deterministically

## Phase 2 — Runtime deploy target (DigitalOcean + compose)
- Standard compose bundle for Odoo runtime:
  - odoo service
  - reverse proxy
  - filestore volume
- Deployment script:
  - pull pinned GHCR images
  - apply config
  - health checks

## Phase 3 — Staging-from-prod cloning
- Implement "fresh prod clone per staging build" rule:
  - clone strategy v1: pg_dump/pg_restore into new DB
  - ensure DB not reused between builds
- Add automatic data-scrubbing option for staging (PII masking)

## Phase 4 — Backups parity + restore
- Backup schedule + retention: 7 daily / 4 weekly / 3 monthly
- Backup contents:
  - DB dump, filestore tar, logs snapshot
- Restore flows:
  - staging restore self-serve
  - prod restore gated by approvals

## Phase 5 — Upgrade advisor
- Upgrade preview pipeline:
  - clone prod
  - run upgrade container/migrations
  - smoke tests + report artifacts
- Gate production upgrade promotion

## Phase 6 — UX surfaces (CLI + minimal UI)
- CLI commands:
  - `ops run create`, `ops run logs`, `ops backups list`, `ops restore`, `ops promote`
- Optional thin web console later (not required for v1)

## Cross-cutting
- Security: audit trails for shell/log access
- Observability: run events, metrics, alerts
- Evidence: produce `docs/evidence/<run_id>/` bundles for PRs
