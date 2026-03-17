# Enterprise Edition Parity Matrix

> Human-readable view of EE parity status.
> Source: `ssot/governance/platform-capabilities-unified.yaml` (Section A) +
> `infra/ssot/parity/ee_to_oca_proof_matrix.yaml`
>
> **Target**: >= 80% weighted parity via CE + OCA + `ipai_*`
> **Current**: 35-45% (audited 2026-03-08)

---

## Accounting

| Capability | EE Module | Replacement | Status | Parity | Priority |
|-----------|-----------|-------------|--------|--------|----------|
| Bank Reconciliation | `account_accountant` | `account_reconcile_oca` (OCA) | Planned | 0% | **P0** |
| Financial Reports | `account_reports` | `account_financial_report` (OCA) | Planned | 0% | **P0** |
| Asset Management | `account_asset` | `account_asset_management` (OCA) | Planned | 0% | P1 |
| Budget Management | `account_budget` | `ipai_finance_ppm` | **Active** | 40% | **P0** |
| Consolidation | `account_consolidation` | `ipai_finance_consolidation` (planned) | Planned | 0% | P2 |

## HR & Payroll

| Capability | EE Module | Replacement | Status | Parity | Priority |
|-----------|-----------|-------------|--------|--------|----------|
| Payroll | `hr_payroll` | `ipai_hr_payroll_ph` | **Active** | 70% | **P0** |
| Attendance | `hr_attendance` | `ipai_hr_attendance` (planned) | Planned | 0% | P1 |
| Leave Management | `hr_holidays` | `ipai_hr_leave` (planned) | Planned | 0% | P1 |
| Expense Management | `hr_expense` | `hr_expense` (OCA) | Planned | 0% | **P0** |
| Appraisals | `hr_appraisal` | `ipai_hr_appraisal` (planned) | Planned | 0% | P2 |

## Services

| Capability | EE Module | Replacement | Status | Parity | Priority |
|-----------|-----------|-------------|--------|--------|----------|
| Helpdesk | `helpdesk` | `ipai_helpdesk` | **Active** | 40% | P1 |
| Approvals | `approvals` | `ipai_approvals` (planned) | Planned | 0% | **P0** |
| Planning | `planning` | `ipai_planning` (planned) | Planned | 0% | P1 |
| Timesheet Grid | `timesheet_grid` | `ipai_timesheet` (planned) | Planned | 0% | P1 |

## Studio & Customization

| Capability | EE Module | Replacement | Status | Parity | Priority |
|-----------|-----------|-------------|--------|--------|----------|
| Studio | `studio` | `ipai_dev_studio_base` (planned) | Planned | 0% | P2 |
| Spreadsheet | `spreadsheet` | Apache Superset | Partial | 20% | P2 |

## Documents & Knowledge

| Capability | EE Module | Replacement | Status | Parity | Priority |
|-----------|-----------|-------------|--------|--------|----------|
| Documents | `documents` | `dms` (OCA) + `ipai_enterprise_bridge` | Partial | 30% | P2 |
| Knowledge | `knowledge` | `ipai_knowledge_base` (planned) | Planned | 0% | P2 |
| Sign | `sign` | `ipai_sign` | Partial | 20% | P2 |

---

## P0 Gap Summary

| # | Gap | Replacement Path | Blocker |
|---|-----|-----------------|---------|
| 1 | Bank Reconciliation | OCA `account_reconcile_oca` | OCA 19.0 branch hydration |
| 2 | Financial Reports | OCA `account_financial_report` | OCA 19.0 branch hydration |
| 3 | Budget Management | `ipai_finance_ppm` (40% → 80%) | Feature completion |
| 4 | Expense Management | OCA `hr_expense` | OCA 19.0 branch hydration |
| 5 | Approvals | `ipai_approvals` (new module) | Development |

## OCA Module Adoption

- **Target**: 56 must-have modules installed and green
- **Current**: Checklists defined, modules not hydrated
- **Base modules**: 27 (queue_job, auditlog, password_security, web_responsive, sentry, ...)
- **Accounting modules**: 18 (account_reconcile_oca, account_financial_report, mis_builder, ...)
- **Sales modules**: 11 (sale_order_type, sale_cancel_reason, sale_delivery_state, ...)
- **Manifest gaps**: 7 modules need ports or new repos for Odoo 19

## Critical Path

```
OCA 19.0 hydration → P0 module installation → ipai_* feature completion → parity gate (80%)
```

---

*Source: `ssot/governance/platform-capabilities-unified.yaml` (last updated 2026-03-18)*
