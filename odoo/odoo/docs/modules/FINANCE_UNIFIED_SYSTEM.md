# Unified Finance System

> Canonical reference for the coordinated BIR tax compliance, month-end
> close, and finance PPM system. Spec bundle: `spec/finance-unified/`.

---

## 1. System Overview

The unified finance system serves TBWA\SMP Finance SSC (8 employees)
with three integrated capabilities running on a shared monthly cycle:

| Capability | Module | Purpose |
|------------|--------|---------|
| BIR Tax Compliance | `ipai_bir_tax_compliance` | 36 eBIRForms, filing deadlines, compliance dashboard |
| Month-End Close | `ipai_finance_close_seed` | 39 tasks across 5 phases, team assignments, milestones |
| Finance PPM | `ipai_finance_ppm` | Clarity PPM parity, OKR dashboard, analytic controls |
| BIR Alerts | `ipai_bir_notifications` | Deadline alerts via email digest (planned) |
| BIR ↔ Plane | `ipai_bir_plane_sync` | Bidirectional sync with Plane.so (planned) |

---

## 2. Process Model

```
                       Monthly Cycle
                            |
            +───────────────+───────────────+
            |                               |
       Month-End Close                BIR Tax Filing
       (39 tasks, 5 phases)          (50 tasks, 9+ forms)
            |                               |
      I.   Pre-Close               Monthly: 1601-C, 0619-E,
      II.  Transaction Close         SSS, PhilHealth, Pag-IBIG
      III. Reconciliation                   |
      IV.  Reporting               Quarterly: 2550Q, 1601-EQ
      V.   Post-Close                       |
            |                      Annual: 1604-CF, 2316,
            +───────────────+───────────────+    Alphalist
                            |
                      Finance PPM
                 (Portfolio oversight,
                  OKR tracking,
                  budget vs. actual)
```

### Kanban Workflow (6 stages)

`To Do` → `In Preparation` → `Under Review` → `Awaiting Approval` → `Done` → `Cancelled`

---

## 3. Module Graph

### Active (5 modules)

```
Foundation Layer:
  ipai_finance_ppm           v19.0.1.0.0  [project, account, analytic, mail, web]
  ipai_bir_tax_compliance    v18.0.1.0.0  [base, mail, account, project]
                                           ↑ version bump to 19.0 pending (T1.5)

Satellite Layer (depends on ipai_bir_tax_compliance):
  ipai_bir_notifications     v19.0.1.0.0  [base, mail]  installable: False (planned)
  ipai_bir_plane_sync        v19.0.1.0.0  [base]        installable: False (planned)

Data Layer:
  ipai_finance_close_seed    v19.0.1.0.0  [project, hr]  data-only module
```

### Deprecated (2 modules)

| Module | Version | Reason | Successor |
|--------|---------|--------|-----------|
| `ipai_finance_workflow` | 19.0.1.0.0 | Superseded | `ipai_finance_close_seed` |
| `ipai_finance_tax_return` | 19.0.1.0.0 | Migrated | `ipai_enterprise_bridge` |

Both are `installable: False` and must remain so.

---

## 4. Seed Ownership

| Artifact | Format | Authority | Location |
|----------|--------|-----------|----------|
| Stages (6) | XML | **Canonical** | `ipai_finance_close_seed/data/01_stages.xml` |
| Tags (33) | XML | **Canonical** | `ipai_finance_close_seed/data/02_tags.xml` |
| Team (9 members) | XML | **Canonical** | `ipai_finance_close_seed/data/03_partners_employees.xml` |
| Projects (2) | XML | **Canonical** | `ipai_finance_close_seed/data/04_projects.xml` |
| Milestones (11) | XML | **Canonical** | `ipai_finance_close_seed/data/05_milestones.xml` |
| Close tasks (39) | XML | **Canonical** | `ipai_finance_close_seed/data/06_tasks_month_end.xml` |
| BIR tasks (50) | XML | **Canonical** | `ipai_finance_close_seed/data/07_tasks_bir_tax.xml` |
| BIR tax rates | XML | **Canonical** | `ipai_bir_tax_compliance/data/bir_tax_rates.xml` |
| Filing deadlines | XML | **Canonical** | `ipai_bir_tax_compliance/data/bir_filing_deadlines.xml` |
| BIR form schedules | JSON | Derived | `ipai_finance_closing_seed.json` (repo root) |
| Expense categories | SQL | Deprecated | `supabase/seeds/002_finance_seed.sql` |

**Rule**: Changes to seed data start in the XML/CSV files. Derived formats
are regenerated, never hand-edited independently.

---

## 5. BIR Calendar Coverage

### Monthly (12 cycles per year)

| Form | Description | Deadline Pattern |
|------|-------------|------------------|
| 1601-C | Withholding Tax on Compensation | 10th of following month |
| 0619-E | Expanded Withholding Tax | 10th of following month |
| SSS | Social Security contribution | Varies by employer ID |
| PhilHealth | Health insurance contribution | ~15th of following month |
| Pag-IBIG | Housing fund contribution | ~10th of following month |

### Quarterly (4 cycles per year)

| Form | Description |
|------|-------------|
| 2550Q | Quarterly VAT Return |
| 1601-EQ | Quarterly Expanded Withholding Tax |

### Annual

| Form | Description |
|------|-------------|
| 1604-CF | Annual Information Return (Compensation/Final) |
| 2316 | Certificate of Compensation Payment |
| Alphalist | Annual Employee Alphalist |

### Full eBIRForms catalog (36 forms)

VAT: 2550M, 2550Q | Withholding: 1600, 1601-C, 1601-E, 1601-F, 1604-CF |
Income: 1700, 1701, 1702 | Excise: 2200A, 2200P, 2200T, 2200M, 2200AN |
Percentage: 2551M, 2551Q | Capital Gains: 1706, 1707 |
Documentary Stamp: 2000, 2000-OT | Others per `ipai_bir_tax_compliance` data files.

---

## 6. Month-End Close Flow

### Phase I: Pre-Close (days 1–3)

Cut-off notices, sub-ledger freeze, preliminary trial balance

### Phase II: Transaction Close (days 3–8)

Revenue recognition, expense accruals, payroll posting, intercompany entries

### Phase III: Reconciliation (days 8–12)

Bank reconciliation, AP/AR aging, fixed asset register, inventory valuation

### Phase IV: Reporting (days 12–15)

Financial statements, management reports, variance analysis, BIR form prep

### Phase V: Post-Close (days 15–20)

Audit adjustments, period lock, archive, next-period setup

39 tasks are distributed across these 5 phases with milestone checkpoints.

---

## 7. Clarity PPM Mapping

| Clarity PPM Concept | Odoo Implementation |
|---------------------|---------------------|
| Portfolio | `project.project` (top-level portfolio project) |
| Program | `project.project` (grouped by analytic account) |
| Project | `project.project` with PPM extensions |
| WBS (5 levels) | Goal → Outcome → Objective → Workstream → Task |
| Resource Plan | Team members via `res.partner` + `hr.employee` |
| Financial Plan | `account.analytic.account` with budget/forecast fields |
| OKR Dashboard | Custom JavaScript dashboard action |
| Import Wizard | `ppm.import.wizard` for bulk data loading |

---

## 8. Team Roles

| Code | Name | Role | Function |
|------|------|------|----------|
| CKVC | — | Finance Director | Approval, compliance sign-off, portfolio |
| RIM | — | Senior Finance Manager | Close orchestration, BIR review, PPM |
| BOM | — | Finance Supervisor | Task assignment, deadline tracking |
| JPAL | — | Accountant | Execution |
| LAS | — | Accountant | Execution |
| RMQB | — | Accountant | Execution |
| JPL | — | Accountant | Execution |
| JI | — | Accountant | Execution |
| JO | — | Accountant | Execution |

Functions: payroll, tax, treasury, reporting, AP, AR, closing.

---

## 9. Test Gaps

| Module | Tests | Gap |
|--------|-------|-----|
| `ipai_bir_tax_compliance` | None | No BIR schedule validation, no form coverage test |
| `ipai_finance_ppm` | None | No install smoke test, no field extension check |
| `ipai_finance_close_seed` | None | No seed integrity test (counts, references) |
| `ipai_bir_notifications` | None | Not installable — tests deferred until activation |
| `ipai_bir_plane_sync` | None | Not installable — tests deferred until activation |

### Planned Validators (from `spec/finance-unified/plan.md`)

1. **Seed integrity**: stage/tag/team/project/milestone/task counts and reference validity
2. **BIR schedule validation**: monthly/quarterly/annual form coverage
3. **PPM smoke tests**: module install, field extensions, wizard, dashboard
4. **Contract tests**: deprecated modules stay `installable: False`, version alignment, doc existence

---

## 10. Related Documentation

| Document | Scope | Relation to this doc |
|----------|-------|----------------------|
| `finance_ppm_technical_guide.md` | Technical deep-dive on all 6 modules | Subordinate — detailed implementation reference |
| `FINANCE_PPM_IMPLEMENTATION.md` | Architecture spec for PPM models | Subordinate — PPM-specific architecture |
| `PRD_ipai_ppm_portfolio.md` | Product requirements for PPM | Subordinate — PPM-specific requirements |
| `ipai_clarity_ppm_parity.md` | Clarity PPM feature mapping | Subordinate — parity checklist |
| Module doc stubs (20+) | Per-module status reports | Subordinate — individual module health |

This document (`FINANCE_UNIFIED_SYSTEM.md`) is the **canonical system-level
reference**. Subordinate docs provide detail but must not contradict this file.
