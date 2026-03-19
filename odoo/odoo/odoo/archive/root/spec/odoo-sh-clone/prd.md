# PRD — Odoo.sh Clone (Better-than-Odoo.sh)

## Problem
Odoo.sh provides a strong hosted workflow (branches, builds, staging from prod data, logs/shell, backups) but is tied to Odoo hosting and paid staging capacity.
We need the same developer and ops UX for Odoo CE+OCA+ipai under Insightpulseai governance, with deterministic automation and extensibility.

## Goals
1. **Parity with Odoo.sh primitives**
   - Branch stages: development, staging, production
   - Staging builds duplicate production DB and do not reuse databases between builds
   - Backups retention at least 7 daily / 4 weekly / 3 monthly
2. **Enterprise control plane**
   - central audit log, runs, artifacts, policies, approvals
3. **GitHub-native delivery**
   - GHCR images, reusable workflows, Codespaces devcontainers
4. **Zero-UI ops**
   - CLI/API for builds, restores, upgrades, access control

## Non-goals
- Rebuilding Odoo proprietary hosting UI pixel-for-pixel
- Replacing Odoo Online
- Supporting intermediate Odoo minor branches as first-class (only major versions initially; mirrors Odoo.sh constraints)

## Users
- Platform Admin (org owner): policies, secrets, environments
- Odoo Developer: feature branches, logs, shell, staging validation
- Release Manager: promote staging → prod with approvals
- Auditor: read-only access to evidence, history, events

## Product scope

### 1) Projects
- A "Project" = one Odoo runtime (code + config + DB + filestore).
- Projects are registered in control plane:
  - repo slug, odoo version, environment mapping, runtime targets.

### 2) Branch → Environment model
- `main` → production
- `release/*` → staging
- `feature/*` → development previews
Rules are configurable per project.

### 3) Builds (CI)
Build pipeline steps:
1. Resolve module dependencies (OCA/ipai)
2. Build/pin container images (GHCR)
3. Provision environment DB
4. Deploy runtime
5. Run smoke tests
6. Capture logs, artifacts, evidence

**Staging DB behavior**: each staging build uses a **fresh clone** of prod DB to avoid stale data drift.

### 4) Backups & restores
- Automated schedule meeting parity retention (7 daily / 4 weekly / 3 monthly)
- Backups include:
  - DB dump
  - filestore snapshot
  - build metadata + logs
- Restore supports staging and production (with approvals for prod).

### 5) Shell & logs
- "Shell": exec into running Odoo container via controlled endpoint (RBAC).
- Logs:
  - build logs
  - runtime logs
  - structured events in control plane

### 6) Upgrade advisor
- Preview upgrade: clone prod → upgrade candidate → run migrations/tests.
- Output a risk report + required steps.

### 7) Access control
- RBAC: project_member roles + environment-scoped permissions.
- RLS enforced in control plane DB.

## Success metrics
- <10 min: feature branch preview from push → running build
- Staging build uses prod-clone DB every time
- One-command rollback to prior artifact digest
- 0 secrets in Git; audit coverage for all deployments
- Backup restores validated monthly

## Risks / constraints
- Cloning prod DB frequently can be expensive; mitigate with:
  - logical dump/restore vs snapshot
  - pooled standby/read replica options later
- Running "shell" needs strict least privilege + audit
