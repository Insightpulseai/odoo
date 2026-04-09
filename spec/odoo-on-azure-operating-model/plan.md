# Plan — Odoo on Azure Operating Model

## Implementation model

This target is implemented as a cross-repo program with Azure Boards as the execution spine and GitHub as the implementation spine.

Chain:
1. Spec bundle defines the target.
2. Azure Boards Epic represents the org-wide target.
3. Azure Boards Features represent workstreams.
4. User Stories represent repo/team deliverables.
5. Tasks represent execution steps.
6. GitHub branches / PRs / merge commits provide implementation traceability.
7. CI/CD and evidence tasks validate completion.

## Repo ownership map

| Workstream | Canonical repo |
|---|---|
| Overview / planning / reference | docs |
| Workload center / monitoring / AI control plane intersections | platform |
| Deployment automation / networking / environment bootstrap | infra |
| Runtime topology / Odoo-specific operational docs | odoo |
| Agent/runtime boundary docs | agents |
| Analytics intersections | data-intelligence |

## Area Path model

- ipai-platform
- ipai-platform\docs
- ipai-platform\platform
- ipai-platform\infra
- ipai-platform\odoo
- ipai-platform\agents
- ipai-platform\data-intelligence

## Iteration model

- ipai-platform\Docs\Foundation
- ipai-platform\Docs\Wave-1
- ipai-platform\Docs\Wave-2
- ipai-platform\Docs\Hardening

## Dependency model

Track dependencies at Feature level.

Recommended dependency tags:
- depends-docs
- depends-platform
- depends-infra
- depends-odoo
- depends-agents
- depends-data

## Validation model

Every workstream must include:
- authored output
- evidence output
- repo ownership confirmation
- cross-link/navigation confirmation
- acceptance review

## Risks

- repo authority ambiguity
- live-vs-IaC drift
- incomplete traceability between work item and PR
- documentation without runtime evidence
- scope inflation without feature decomposition

## UAT Operating Model

### Scenario Authority

Formal UAT execution must use the scenario definitions and templates in:
- `spec/odoo-on-azure-operating-model/uat-scenarios.md`

## Exit criteria

This target is complete only when:
- all planned Features are complete or intentionally descoped
- all critical Stories have evidence-backed closure
- source-of-truth repo placement is correct
- traceability from Boards to PR/build evidence exists
- target success metrics are reviewable
