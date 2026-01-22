# Finance PPM Seed Data Assessment

**Date:** 2026-01-22
**Reviewed Against:** SAP Advanced Financial Closing + SAP Tax Compliance Best Practices
**Odoo Equivalent:** Odoo 18 CE + OCA Module Documentation

---

## Executive Summary

The Finance PPM seed data is **substantially complete** for task workflow orchestration. The data structure follows SAP AFC best practices with proper phase sequencing, RACI assignments, and deadline calculations. However, several supporting data structures require manual configuration in Odoo.

| Category | Status | Coverage |
|----------|--------|----------|
| Month-End Close Tasks | ✅ Complete | 36 tasks across 4 phases |
| BIR Tax Filing Tasks | ✅ Complete | 33 tasks for 2026 calendar |
| Task Staging Workflow | ✅ Complete | 5-stage lifecycle |
| RACI Assignments | ✅ Complete | Prep/Review/Approve per task |
| Fiscal Period Config | ⚠️ Manual | Not seeded |
| Chart of Accounts | ⚠️ Manual | Not seeded |
| Tax Configuration | ⚠️ Manual | Not seeded |

---

## SAP → Odoo Mapping Reference

### SAP Advanced Financial Closing (AFC) → Odoo CE18

| SAP AFC Concept | Odoo CE Equivalent | OCA Module | Documentation |
|-----------------|-------------------|------------|---------------|
| Closing Template | `finance.task.template` | - | [Project Management](https://www.odoo.com/documentation/18.0/applications/services/project/project_management.html) |
| Closing Task List | `project.task` + stages | - | [Project Tasks](https://www.odoo.com/documentation/18.0/applications/services/project.html) |
| Task Dependencies | `depend_on_ids` field | `project_task_dependency` | [OCA Project](https://github.com/OCA/project) |
| Period Lock | Lock Dates | `account_fiscal_year_closing` | [Year-End Closing](https://www.odoo.com/documentation/18.0/applications/finance/accounting/reporting/year_end.html) |
| Workflow Automation | SAP Build → n8n | - | [n8n Workflows](https://docs.n8n.io/) |
| Task Monitoring | Kanban + Dashboard | `project_dashboard` | [Project Views](https://www.odoo.com/documentation/18.0/applications/services/project.html) |

### SAP Tax Compliance → Odoo CE18 (Philippines)

| SAP STC Concept | Odoo CE Equivalent | OCA Module | Documentation |
|-----------------|-------------------|------------|---------------|
| Tax Forms | `project.task` (BIR Filing) | - | [BIR Online](https://www.bir.gov.ph/efps) |
| Compliance Calendar | Task deadlines | - | [BIR Tax Calendar 2026](https://www.bir.gov.ph/calendar) |
| WHT Alphalisting | `account.move` + `l10n_ph` | `l10n_ph_*` | [PH Localization](https://github.com/OCA/l10n-philippines) |
| VAT Summary List | `account.report` | `account_financial_report` | [OCA Reporting](https://github.com/OCA/account-financial-reporting) |
| Audit Trail | Chatter + `mail.tracking` | - | [Odoo Discuss](https://www.odoo.com/documentation/18.0/applications/productivity/discuss.html) |

---

## Current Seed Data Inventory

### 1. Month-End Close Tasks (36 Tasks)

**Source:** `data/finance_seed/03_project.task.month_end.csv`

| Phase | Tasks | Timeline | Categories |
|-------|-------|----------|------------|
| Phase I: Initial & Compliance | 6 | Days -6 to -3 | Payroll, Tax, Rent, Accruals |
| Phase II: Accruals & Amortization | 6 | Days -5 to -2 | Depreciation, Fees, Insurance, FX |
| Phase III: WIP | 12 | Days -3 to -1 | Billings, WIP/OOP, Intercompany |
| Phase IV: Final Adjustments | 12 | Days -2 to 0 | VAT, Reclassifications, Reporting |

**Alignment with SAP AFC:**
- ✅ 4-phase structure matches SAP AFC template best practice
- ✅ Due offset calculations align with AFC task scheduling
- ✅ RACI assignments (Prep → Review → Approve) match AFC workflow
- ✅ Evidence requirements flagged per task

### 2. BIR Tax Filing Tasks (33 Tasks)

**Source:** `data/finance_seed/04_project.task.bir_tax.csv`

| Form Type | Frequency | Tasks | 2026 Deadlines |
|-----------|-----------|-------|----------------|
| 1601-C (WHT Compensation) | Monthly | 12 | 10th of next month |
| 0619-E (VAT Declaration) | Monthly | 12 | 20th of next month |
| 2550Q (Quarterly VAT) | Quarterly | 4 | 25 days after Q end |
| 1601-EQ (Quarterly EWT) | Quarterly | 4 | Last day of next month |
| 1702-RT (Annual ITR) | Annual | 1 | April 15 |

**Alignment with BIR Regulations:**
- ✅ All statutory deadlines correctly calculated
- ✅ Weekend/holiday adjustments applied
- ✅ Prep → Report Approval → Payment Approval workflow
- ✅ Penalty references documented in YAML specs

### 3. AFC Task Specifications (33 Tasks)

**Source:** `seeds/workstreams/afc_financial_close/20_tasks.yaml`

Extended task metadata with SAP AFC reference codes:
- `AFC_I_PAYROLL`, `AFC_I_TAX_PROVISION`, etc.
- Category color coding for visualization
- Evidence requirements per task

### 4. PH Localization Overlay

**Source:** `seeds/workstreams/stc_tax_compliance/60_localization_ph.yaml`

- 8 BIR form definitions with deadline rules
- 14 ATC (Alphanumeric Tax Codes) for WHT
- TIN validation pattern: `XXX-XXX-XXX-XXX`
- Holiday adjustment rules

---

## Gap Analysis

### Critical Gaps (Required for Workflow Execution)

| Gap | Impact | Resolution | Odoo Documentation |
|-----|--------|------------|-------------------|
| **Fiscal Year 2026 not seeded** | Cannot lock periods | Manual: Accounting → Settings → Fiscal Year | [Fiscal Year](https://www.odoo.com/documentation/18.0/applications/finance/accounting/get_started.html) |
| **Chart of Accounts not seeded** | Journal entries fail | Use default COA or import CSV | [Chart of Accounts](https://www.odoo.com/documentation/18.0/applications/finance/accounting/get_started/chart_of_accounts.html) |
| **VAT 12% tax not configured** | Tax calculations fail | Accounting → Configuration → Taxes | [Tax Configuration](https://www.odoo.com/documentation/18.0/applications/finance/accounting/taxes.html) |
| **Users not fully seeded** | Task assignments fail | Run `update_tasks_after_import.py` | [User Management](https://www.odoo.com/documentation/18.0/applications/general/users.html) |

### Medium Priority Gaps

| Gap | Impact | OCA Module Needed |
|-----|--------|-------------------|
| Fixed Asset Depreciation | Phase II tasks incomplete | `account_asset_management` |
| Payroll Integration | Payroll entries not posted | `hr_payroll_account` |
| Cash Advance Clearing | CA liquidation not tracked | `hr_expense_advance_clearing` |
| FX Revaluation | IC revaluation not automated | `account_multicurrency_revaluation` |
| Bank Reconciliation | Manual reconciliation only | `account_reconcile_oca` |

### Low Priority Gaps

| Gap | Impact | Notes |
|-----|--------|-------|
| Multi-company setup | Single entity only | Add when needed |
| Cost center hierarchy | Department allocation N/A | OCA analytic modules |
| Document management | Evidence tracking manual | OCA document modules |

---

## OCA Module Requirements

The following OCA modules are required for full Finance PPM functionality:

```yaml
# oca.lock.json additions needed
oca_modules:
  # Required for Month-End Close
  - repo: account-closing
    modules:
      - account_fiscal_year_closing    # Period lock
      - account_cutoff_accrual_order_base  # Accruals

  - repo: account-financial-tools
    modules:
      - account_asset_management       # Depreciation

  - repo: account-financial-reporting
    modules:
      - account_financial_report       # TB, BS, PL reports

  - repo: account-reconcile
    modules:
      - account_reconcile_oca          # Bank reconciliation

  # Required for Tax Compliance
  - repo: l10n-philippines
    modules:
      - l10n_ph_base                   # PH localization
      - l10n_ph_tax                    # BIR tax codes

  # Optional Enhancements
  - repo: hr-expense
    modules:
      - hr_expense_advance_clearing    # CA liquidation

  - repo: hr
    modules:
      - hr_payroll_account             # Payroll GL posting
```

---

## Recommended Actions

### Immediate (Before Go-Live)

1. **Create Fiscal Year 2026**
   ```bash
   # Via Odoo UI: Accounting → Configuration → Fiscal Years
   # Or via XML-RPC using import script
   ```

2. **Configure VAT 12% Tax**
   ```bash
   # Accounting → Configuration → Taxes → Create
   # Name: VAT 12%, Amount: 12%, Type: Percent of Price
   ```

3. **Import Seed Data**
   ```bash
   cd /home/user/odoo-ce/data/finance_seed
   python import_all.py
   python update_tasks_after_import.py
   ```

### Short-Term (Sprint 1)

4. **Install OCA Modules**
   ```bash
   # Verify OCA repos in oca.lock.json
   # Install via Odoo Apps menu or CLI
   docker compose exec odoo odoo -d odoo_dev -i account_fiscal_year_closing --stop-after-init
   ```

5. **Configure Asset Depreciation**
   - Create asset categories for computer equipment, vehicles, furniture
   - Link to GL accounts

### Medium-Term (Sprint 2-3)

6. **Enable Payroll Integration** (if using HR Payroll)
7. **Configure Bank Reconciliation Rules**
8. **Set up Document Attachment Templates**

---

## Verification Checklist

After seed import, verify:

- [ ] 36 month-end tasks visible in Project → Month-End Close
- [ ] 33 BIR tasks visible in Project → BIR Tax Filing
- [ ] 5 task stages configured (Preparation → Review → Approval → Execute → Close)
- [ ] Tags visible: Phase I-IV + category tags
- [ ] Deadlines correctly calculated for 2026
- [ ] User assignments match team roster

---

## References

### SAP Documentation (Best Practices Source)
- [SAP Advanced Financial Closing](https://www.sap.com/products/financial-management/advanced-financial-closing.html)
- [SAP AFC - Manage Closing Task Lists](https://help.sap.com/docs/advanced-financial-closing/user/manage-closing-task-lists)
- [SAP AFC Workflows](https://community.sap.com/t5/financial-management-blog-posts-by-sap/sap-advanced-financial-closing-leveraging-workflows-to-extend-entity-closes/ba-p/13940497)

### Odoo Documentation (Implementation Target)
- [Odoo 18 Year-End Closing](https://www.odoo.com/documentation/18.0/applications/finance/accounting/reporting/year_end.html)
- [Odoo 18 Project Management](https://www.odoo.com/documentation/18.0/applications/services/project/project_management.html)
- [Odoo 18 Tax Configuration](https://www.odoo.com/documentation/18.0/applications/finance/accounting/taxes.html)
- [Odoo Financial Closing (Much Consulting)](https://muchconsulting.com/blog/odoo-2/odoo-financial-closing-102)

### BIR Philippines
- [BIR Tax Calendar 2026](https://www.bir.gov.ph/calendar)
- [BIR eFPS Portal](https://efps.bir.gov.ph/)
- [BIR Compliance Guide 2026](https://philippinehubpartners.com/bir-tax-compliance-philippines-2026-guide/)

### OCA Modules
- [OCA account-closing](https://github.com/OCA/account-closing)
- [OCA account-financial-reporting](https://github.com/OCA/account-financial-reporting)
- [OCA l10n-philippines](https://github.com/OCA/l10n-philippines)

---

*Generated by Claude Code - Session 01A3dz1AfXrdgu8fk6g6CowV*
