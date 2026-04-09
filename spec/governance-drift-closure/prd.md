# PRD — Governance Drift Closure

## Objective

Close governance drift for the production baseline by reconciling live Azure estate, IaC, SSOT, and architecture documentation.

## Why this matters

The platform is conditionally ready based on live runtime controls, but the dominant remaining risk is governance drift rather than absence of infrastructure. This target formalizes the reconciliation effort needed to restore source-controlled, reviewable, reproducible control-plane integrity.

## Benchmark model

- workload-center / control-plane discipline from the Odoo-on-Azure operating model
- spec-first and evidence-first closure model

## In scope

- drift model and exception registry
- runtime/IaC reconciliation
- rebuildability and recovery docs
- evidence closure for production-significant resources

## Out of scope

- unrelated feature expansion
- speculative architecture changes not required for reconciliation
- replacing live evidence with aspirational docs

## Success metrics

- unmanaged production-significant resources are classified
- retained resources are in IaC or an approved exception registry
- rebuildability and recovery assumptions are documented
- governance risk is reduced from unknown drift to governed variance

## Affected repos

- platform
- infra
- docs
- odoo

## Owning teams

- ipai-platform-control
- ipai-infra
- ipai-docs
- ipai-odoo-runtime

## Workstream model

1. Drift Model and Exceptions
2. Rebuildability and Recovery Docs
3. Evidence Closure
4. Runtime/IaC Reconciliation

## Acceptance conditions

- all production-significant drift is classified
- approved exceptions are recorded
- rebuildability and recovery expectations are documented
- core platform docs reflect current-state truth and intended-state truth distinctly

## Azure Boards projection

Epic title:
`[TARGET] Governance Drift Closed for Production Baseline`
