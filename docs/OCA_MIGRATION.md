# IPAI OCA-First Module Strategy

> **Principle**: Extend OCA modules, minimize custom delta code.

## Enterprise Parity Mapping

### Target Systems → OCA Replacements

| Enterprise System | OCA Repository | Key Modules | Coverage |
|-------------------|----------------|-------------|----------|
| **SAP Concur** | `hr-expense` | `hr_expense_tier_validation`, `hr_expense_invoice`, `hr_expense_payment` | 60% |
| **SAP Ariba SRM** | `purchase-workflow` | `purchase_request`, `purchase_request_to_rfq` | 65% |
| **Cheqroom** | `maintenance` | `maintenance_request_*`, `resource_booking` | 70% |
| **Notion AI** | `dms` + Native Knowledge | `dms`, `dms_portal`, Knowledge app | 75% |
| **Clarity PPM** | `project` + `calendar` | `resource_booking`, `project_milestone_status` | 55% |
| **MS Project** | `web` + `project` | `web_timeline`, `project_timeline` | 70% |

### Gap Analysis (Delta Code Needed)

| Gap | Enterprise Reference | Priority | Complexity |
|-----|---------------------|----------|------------|
| Travel booking integration | SAP Concur | Medium | High |
| Supplier scoring/rating | SAP Ariba | High | Medium |
| Critical path (migrate 11.0→18.0) | MS Project | High | Medium |
| Project baselines | MS Project | High | Medium |
| Asset audit trails | Cheqroom | Medium | Low |
| Portfolio-level dashboards | Clarity PPM | High | Medium |

---

## OCA Submodules (external-src/)

| Repository | Branch | Key Modules | Replaces |
|------------|--------|-------------|----------|
| `reporting-engine` | 18.0 | `bi_sql_editor` | `ipai_finance_ppm_dashboard` |
| `account-closing` | 18.0 | `account_fiscal_year_closing` | `ipai_finance_monthly_closing` |
| `project` | 18.0 | `project_milestone_status`, `project_timeline` | Parts of `ipai_ppm_monthly_close` |
| `hr-expense` | 18.0 | `hr_expense_tier_validation` | Expense workflows |
| `purchase-workflow` | 18.0 | `purchase_request` | RFQ/procurement |
| `maintenance` | 18.0 | `maintenance_request_*` | Asset tracking |
| `dms` | 18.0 | `dms`, `dms_portal` | `ipai_docs` |
| `calendar` | 18.0 | `resource_booking` | Resource planning |
| `web` | 18.0 | `web_timeline` | Gantt views |

---

## ipai* Module Deprecation Schedule

### Phase 1: Immediate Removal

| Module | Status | Replacement |
|--------|--------|-------------|
| `ipai_finance_ppm_dashboard` | **DEPRECATED** | `bi_sql_editor` (OCA) |
| `ipai_docs` | **DEPRECATED** | Native Odoo 18 Knowledge |
| `ipai_docs_project` | **DEPRECATED** | Native Knowledge integration |

### Phase 2: Consolidate

| Module | Status | Action |
|--------|--------|--------|
| `ipai_ppm_monthly_close` | **CONSOLIDATE** | Extend `account_fiscal_year_closing` |
| `ipai_finance_monthly_closing` | **MERGE** | Into above |
| `ipai_finance_ppm` | **REDUCE** | Keep BIR-specific only |

### Phase 3: Keep (Legitimate Deltas)

| Module | Status | Reason |
|--------|--------|--------|
| `ipai_ce_cleaner` | **KEEP** | No OCA equivalent |
| `tbwa_spectra_integration` | **KEEP** | Company-specific export |

---

## Updated odoo.conf

```ini
[options]
addons_path =
    /mnt/extra-addons,
    /mnt/external-src/reporting-engine,
    /mnt/external-src/account-closing,
    /mnt/external-src/project,
    /mnt/external-src/hr-expense,
    /mnt/external-src/purchase-workflow,
    /mnt/external-src/maintenance,
    /mnt/external-src/dms,
    /mnt/external-src/calendar,
    /mnt/external-src/web
```

---

## Final Target State

```
addons/                        # Thin deltas only
├── ipai_ce_cleaner/           # KEEP - hides Enterprise upsells
├── ipai_bir_compliance/       # NEW - extends OCA account-closing
└── tbwa_spectra_integration/  # KEEP - company-specific export

external-src/                  # OCA modules (git submodules)
├── reporting-engine/          # BI dashboards
├── account-closing/           # Fiscal close
├── project/                   # Project extensions
├── hr-expense/                # Expense management (SAP Concur)
├── purchase-workflow/         # Procurement (SAP Ariba)
├── maintenance/               # Asset tracking (Cheqroom)
├── dms/                       # Document management (Notion)
├── calendar/                  # Resource booking (Clarity)
└── web/                       # Timeline/Gantt (MS Project)
```

---

**Last Updated**: 2025-11-25
