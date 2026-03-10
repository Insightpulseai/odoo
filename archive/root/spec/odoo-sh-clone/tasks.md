# TASKS — Odoo.sh Clone (Better-than-Odoo.sh)

## T0 — Spec-kit compliance
- [ ] Ensure `spec/odoo-sh-clone/{constitution,prd,plan,tasks}.md` exist
- [ ] Add CI check enforcing presence for platform specs

## T1 — Control plane schema (Supabase)
- [ ] Create migrations:
  - [ ] `ops.projects`
  - [ ] `ops.environments`
  - [ ] `ops.runs`
  - [ ] `ops.run_events`
  - [ ] `ops.artifacts`
  - [ ] `ops.backups`
  - [ ] `ops.restores`
  - [ ] `ops.approvals`
  - [ ] `ops.policies`
  - [ ] RBAC tables: `ops.project_members`, `ops.roles`
- [ ] Add RLS policies for all ops tables
- [ ] Add RPCs:
  - [ ] `ops.queue_run(project_id, env, git_sha, ref)`
  - [ ] `ops.claim_next_run(worker_id)`
  - [ ] `ops.append_event(run_id, level, message, payload)`
  - [ ] `ops.finish_run(run_id, status)`
  - [ ] `ops.create_backup(project_id, env)`
  - [ ] `ops.restore_backup(backup_id, target_env)`
- [ ] Add indexes, TTL policies for logs/events, retention config

## T2 — Runner (Edge Function)
- [ ] Implement `ops-runner` Edge Function:
  - claim run → execute phases → write events/artifacts
- [ ] Support deterministic phases:
  - build image (GHCR)
  - deploy runtime
  - smoke tests
- [ ] Emit artifacts:
  - build logs
  - deployment manifest
  - SBOM
  - evidence bundle pointer

## T3 — GHCR image standardization
- [ ] Add org reusable workflow (in `.github`)
- [ ] Add per-repo caller workflows for repos with Dockerfiles
- [ ] Enforce tags: `short_sha`, `date`, `latest` (optional)
- [ ] Add cosign signing (later)

## T4 — Codespaces standardization
- [ ] Roll out `.devcontainer/devcontainer.json` across repos
- [ ] Compose-based devcontainer where compose exists
- [ ] Base devcontainer otherwise
- [ ] Add minimal ports + postCreate checks

## T5 — Staging-from-prod cloning
- [ ] Implement clone method v1:
  - pg_dump from prod DB
  - restore to ephemeral staging DB
  - do not reuse DB between builds
- [ ] Add masking hooks for staging (optional)

## T6 — Backups parity
- [ ] Implement scheduled backups
- [ ] Enforce retention: 7 daily / 4 weekly / 3 monthly
- [ ] Include filestore snapshots + logs where possible

## T7 — Upgrade advisor
- [ ] Create upgrade preview run type
- [ ] Produce upgrade report artifact
- [ ] Add approval gate to promote upgrade to prod

## T8 — CLI tooling
- [ ] Implement `ops` CLI (Node or Python):
  - run create/status/logs
  - backups list/create/restore
  - promote staging→prod
- [ ] Add CI to publish CLI releases

## Acceptance criteria
- [ ] Push to `feature/*` produces a running preview
- [ ] Push to `release/*` produces staging using fresh prod-clone DB
- [ ] Backup/restore works and retention is enforced
- [ ] All actions are auditable and gated by policy
