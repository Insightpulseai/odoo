# ADR-0001: Finance PPM Controls (Delta)

| Field | Value |
|-------|-------|
| **Capability** | Budget/forecast/variance tracking on projects |
| **Parity target** | Delta (`ipai_finance_ppm`) |
| **Date** | 2026-02-16 |
| **Status** | Accepted |

## Context

Finance PPM requires budget, forecast, and variance fields on `project.project`
to track month-end close and BIR tax filing financial metrics.

## CE Attempt

Odoo 19 CE `project.project` has no budget/forecast/variance fields natively.
Server actions and computed fields cannot express the full reporting model needed.

## OCA Search

No OCA module in the 19.0 series provides finance-specific PPM extensions
(budget tracking, variance computation, analytic linking for cost centers).

`project_budget` (OCA) exists but is oriented toward project billing, not
finance department close/compliance tracking.

## Decision

Created `ipai_finance_ppm` as a minimal delta module adding:
- PPM fields (budget, forecast, variance) on `project.project`
- Analytic account linking for cost centers
- Task-to-JE integration on `project.task`
- Bulk import wizard for CSV seeding

## Consequences

- Module must be maintained for Odoo 19 upgrades
- Budget/variance logic is Finance PPM-specific, not generalizable
