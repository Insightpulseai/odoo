# ADR-0004: Finance Workflow (Delta)

| Field | Value |
|-------|-------|
| **Capability** | Role-based finance workflow stages |
| **Parity target** | Delta (`ipai_finance_workflow`) |
| **Date** | 2026-02-16 |
| **Status** | Accepted |

## Context

Finance PPM requires a 4-tier approval workflow:
Analyst prepares → Manager reviews → Senior Manager validates → Director approves.
Stages must enforce role-based transitions, not just generic task movement.

## CE Attempt

Odoo 19 CE `project.task.type` stages are generic — any user can move any
task to any stage. CE provides no mechanism for role-based stage gate enforcement
without custom code.

## OCA Search

OCA provides:
- `project_stage_closed`: Distinguishes closed stages (useful but insufficient)
- No OCA module enforces role-based stage transitions for finance workflows

`purchase_requisition` (OCA) provides approval workflows but is
oriented toward procurement, not finance close/filing.

## Decision

Created `ipai_finance_workflow` providing:
- Finance team role definitions (Director, Senior Manager, Manager, Analyst)
- Stage seeds: Preparation → Review → Approval → Execute → Closed
- Project seeds: Month-End Close (IM1), BIR Returns (IM2)
- Team member assignment to finance roles

## Consequences

- Role definitions are Finance PPM-specific
- Stage names differ from the 6-stage Kanban in seed data
  (finance_workflow has 5 stages; seed scripts create 6 stages)
- Reconciliation needed: seed stages vs module stages
