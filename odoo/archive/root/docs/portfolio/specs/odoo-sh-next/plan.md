# Plan: Odoo.sh Next

## 1) Milestones

### M0 — Repo + Spec Freeze (Week 1)

- Spec Kit bundle committed
- Initial API surface defined (OpenAPI stub)
- Threat model skeleton

### M1 — Control Plane + Auth (Weeks 2–3)

- REST API v1: env lifecycle, builds, deploys
- RBAC scopes: org/project/env
- Audit log pipeline (append-only)

### M2 — Build System (Weeks 3–6)

- Odoo buildpack v1:
  - base image selection
  - addons layering
  - dependency pinning
- Artifact outputs:
  - OCI image
  - SBOM + provenance

### M3 — Environments + Routing (Weeks 5–8)

- Provision preview/staging/prod
- URL routing + TLS automation
- Exec/SSH policy wrapper + session audit

### M4 — Data Ops (Weeks 6–9)

- Snapshot scheduler for prod
- Restore workflow to staging/preview
- Masking pipeline (rules + tests)

### M5 — Observability (Weeks 7–10)

- Logs aggregation
- Metrics collection + release markers
- Health gates for promotion

### M6 — CLI v1 + GitHub App (Weeks 8–12)

- CLI implements all MVP workflows
- GitHub PR status integration
- Preview URLs + teardown on close/merge

## 2) Reference Architecture (High-level)

- **Control Plane API**: orchestrates lifecycle; emits events
- **Runner(s)**: build + test + publish artifacts
- **Runtime**: Odoo web + workers; Postgres; object storage for filestore/backups
- **Edge Router**: TLS + routes + release switching (blue/green)
- **Observability Stack**: logs + metrics + traces + alert hooks

## 3) Interfaces

- OpenAPI: `spec/odoo-sh-next/openapi.yaml` (to be added in M1)
- CLI: `odoo-sh-next` (binary) with `--json` everywhere
- Webhooks:
  - build.started / build.finished
  - deploy.started / deploy.finished
  - snapshot.created / restore.finished

## 4) Rollout Strategy

- Private alpha on 1–2 projects
- Beta: expand to 5–10 projects + self-host pilot
- GA: publish Helm chart + compose bundle + managed SaaS
