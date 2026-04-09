# Plan — Governance Drift Closure

## Implementation model

This target is implemented through:
- platform for drift model, inventory, exception registry, workload-center truth
- infra for IaC reconciliation and rebuild/recovery patterns
- docs for cross-repo architecture narrative and program visibility
- odoo where runtime-specific recovery assumptions affect the workload

## Repo ownership map

| Workstream | Canonical repo |
|---|---|
| Drift model and exceptions | platform |
| Rebuildability and recovery | infra |
| Evidence closure | platform + docs |
| Runtime/IaC reconciliation | infra + platform |

## Area Path model

- ipai-platform\platform
- ipai-platform\infra
- ipai-platform\docs
- ipai-platform\odoo

## Iteration model

- ipai-platform\Docs\Hardening

## Validation model

Every workstream must produce:
- authored guidance
- evidence records
- classification of current-state truth
- mapping to intended-state truth

## Risks

- unmanaged resources remain unknown
- exception registry becomes incomplete or stale
- docs lag behind live estate or IaC changes
- recovery expectations remain unproven

## Exit criteria

This target is complete only when:
- all known production-significant drift is classified
- approved exceptions are documented
- rebuildability and recovery guidance is published
- platform analysis and workload-center docs reflect the reconciled model
