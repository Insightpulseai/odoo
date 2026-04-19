# PRD — Odoo Cloud Platform (IPAI)

## Vision
Odoo.sh-equivalent experience on Azure for managing IPAI's Odoo CE 18 + OCA runtime: branches → environments, backup/restore, one-click promotions, observability, eval-gated releases.

## Mission
Give ERP operators a self-service platform to:
- Spin up/down branch environments
- Promote branches from dev → staging → prod with evidence
- Perform backup / restore / point-in-time recovery
- Monitor health + resource utilization
- Roll back safely

## Scope (in)
- Branch-to-environment orchestration
- Backup + restore policy and automation
- Release readiness gates (ties to `ssot/release/go-live-readiness.yaml`)
- Observability dashboard (Databricks PPM Control Tower feeds here)
- ACA + PostgreSQL + ACR + KV + monitor wiring (via `infra/`)
- Pulser-assisted operator actions (read/suggest, never auto-commit prod)

## Scope (out)
- Rebuilding Odoo core functionality
- Forking Odoo
- Any Odoo Enterprise source
- Replacing Azure Boards/Pipelines as SoR

## Actors / roles
- Platform operator (ops team; PIM-eligible admin during operations)
- Business user (uses ERP via `erp.insightpulseai.com`)
- External guest (TBWA\SMP approvers per `ssot/identity/guest-invite-registry.yaml`)
- Finance director (Khalil — final procurement + production approvals)

## Workflow (high level)
```
branch commit → CI (Azure Pipelines) → env provision (ACA) → smoke →
optional promotion to staging → eval gate → promotion to prod
(with FD approval + rollback drill evidence) → hypercare window
```

## Key deliverables
- 3-environment model: dev / staging / production
- One-click promote (via pipeline, not manual)
- Automated backup (pg-ipai-odoo) + tested restore
- Dashboards: deployment status, env health, release readiness
- Runbook: branch promotion + rollback + hypercare

## Success criteria
- MTTR < 30 min for runtime incidents in hypercare window
- Zero-data-loss promotion between envs
- 100% of prod promotions require FD approval + evidence pack
- All environment state traceable to a commit SHA + pipeline run ID

## Anchors
- Constitution: [constitution.md](constitution.md)
- Plan: [plan.md](plan.md)
- Tasks: [tasks.md](tasks.md)
- Branch/env contract: [../../platform/ssot/runtime/branch-environment-contract.yaml](../../platform/ssot/runtime/branch-environment-contract.yaml)
- Platform BOM: [../../platform/ssot/architecture/odoo-cloud-platform-bom.yaml](../../platform/ssot/architecture/odoo-cloud-platform-bom.yaml)
- Release gates: [../../platform/ssot/release/odoo-cloud-release-gates.yaml](../../platform/ssot/release/odoo-cloud-release-gates.yaml)
