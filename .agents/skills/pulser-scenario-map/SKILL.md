---
name: Pulser Scenario Map
description: Map Pulser for Odoo business scenarios — Project to Profit, Record to Report, Source to Pay — to canonical Odoo 18 MVP module sets.
---

# Pulser Scenario Map Skill

## When to use
When planning a new user story, feature, or tenant implementation to ensure the functional architecture aligns with the **SAP Concur/Dynamics 365** benchmarks.

## Canonical Scenarios

### 1. Project to Profit (Sales, Resourcing, Finance)
- **Odoo Modules**: `project`, `sale_project`, `hr_timesheet`, `analytic`, `account`.
- **Goal**: Track margin, budget, and actuals at the project level.

### 2. Record to Report (Close, Audit)
- **Odoo Modules**: `account`, `account_payment`, `mis_builder`.
- **Goal**: Financial close, TB reconciliation, and audit trailing.

### 3. Source to Pay (AP, Expense, Cash Advance)
- **Odoo Modules**: `hr_expense`, `account_payment`, `ipai_hr_expense_liquidation`.
- **Goal**: AP queue, expense liquidation (TBWA), and cash-advance settlement.

### 4. Order to Cash (Billing, Collections)
- **Odoo Modules**: `account`, `sale_timesheet`.
- **Goal**: Invoicing accuracy and collection monitoring.

## Validation Checks
1. Ensure the scenario has a defined **Scenario UAT P1** set of stories.
2. Verify that Odoo is the authoritative business-process owner.
3. Check for redundant external logic if Odoo native/OCA covers the use case.
