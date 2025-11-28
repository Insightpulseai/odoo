# IPAI OCA-First Module Strategy

> **Principle**: Extend OCA modules, minimize custom delta code.

---

## Protocol Summary

| Protocol | Purpose | Key OCA Modules |
|----------|---------|-----------------|
| **Tax Shield** | BIR compliance, EWT, DAT files | `account-invoicing`, `account-financial-tools` |
| **Financial Fortification** | Hard close, period locking | `account-closing`, `account-financial-reporting` |
| **Token Trap Bypass** | Replace Odoo IAP with direct APIs | `server-tools` (automation) |
| **Command Center** | Docker CLI operations | N/A (operational) |
| **Infrastructure Independence** | Replace Odoo.sh | GitHub Actions + Docker |

---

## Enterprise Parity Mapping

### Target Systems → OCA Replacements

| Enterprise System | OCA Repository | Key Modules | Coverage |
|-------------------|----------------|-------------|----------|
| **SAP Concur** | `hr-expense` | `hr_expense_tier_validation`, `hr_expense_invoice` | 60% |
| **SAP Ariba SRM** | `purchase-workflow` | `purchase_request`, `purchase_request_to_rfq` | 65% |
| **Cheqroom** | `maintenance` | `maintenance_request_*`, `resource_booking` | 70% |
| **Notion AI** | `dms` + Native Knowledge | `dms`, `dms_portal` | 75% |
| **Clarity PPM** | `project` + `calendar` | `resource_booking`, `project_milestone_status` | 55% |
| **MS Project** | `web` + `project` | `web_timeline`, `project_timeline` | 70% |
| **BIR/PH Tax** | `account-invoicing` | `account_invoice_tax_witholding` | 80% |

### Remaining Gaps (Delta Code Needed)

| Gap | Priority | Complexity | Notes |
|-----|----------|------------|-------|
| BIR Form 2307 QWeb template | High | Low | PDF layout for withholding certificate |
| Alphalist/RELIEF DAT generator | High | Medium | Python server action for BIR file format |
| Critical path (port 11.0→18.0) | Medium | Medium | OCA module exists, needs migration |
| Project baselines | Medium | Medium | Snapshot comparison for variance |
| Supplier scoring/rating | Low | Low | RFQ response evaluation |

### NOT Gaps (Use Native Odoo)

| Feature | Native Module | Status |
|---------|---------------|--------|
| Shipping (DHL, FedEx, UPS, USPS, etc.) | `delivery_*` | ✅ Native |
| Knowledge/Wiki | `knowledge` | ✅ Native Odoo 18 |
| Expenses | `hr_expense` | ✅ Installed |
| Invoicing | `account` | ✅ Installed |
| CRM | `crm` | ✅ Native |
| Employees | `hr` | ✅ Installed |
| Skills Management | `hr_skills` | ✅ Installed |
| Discuss/Chat | `mail` | ✅ Installed |

---

## Tax Shield Protocol (Philippines)

### The Compliance Matrix

| Tax Requirement | Enterprise Way | Smart Delta Way | OCA Module |
|-----------------|----------------|-----------------|------------|
| Chart of Accounts | Generic template | Custom CSV import | N/A |
| Withholding Tax (EWT) | Buggy checkbox | Proper GL postings | `account_invoice_tax_witholding` |
| BIR Form 2307 | Custom dev | QWeb template | Delta code |
| Tax Returns (2550Q) | Static grid | Dynamic drill-down | `account_tax_balance` |
| Alphalist/RELIEF | Manual Excel | Python DAT generator | Delta code |

### EWT Engine Setup

```python
# Workflow: Vendor Bill with 2% EWT
# Bill: ₱100,000 + ₱12,000 VAT
# Apply "EWT 2% - Services" (negative tax)
# Result: Net Payable = ₱110,000

# Journal Entry:
# Dr Expense      100,000
# Dr Input VAT     12,000
# Cr AP           110,000
# Cr EWT Payable    2,000  ← Critical for BIR
```

---

## Financial Fortification Protocol

### Hard Close vs Soft Close

| Feature | Odoo Soft Close | Smart Delta Hard Close |
|---------|-----------------|------------------------|
| Closing Entry | None (dynamic calc) | Actual JE zeroing P&L |
| Lock Dates | Manual setting | Process-driven auto-lock |
| Checklist | Static PDF | Living Project tasks |
| Audit Trail | Basic logs | Supabase snapshots |

### Key Modules

- `account_fiscal_year_closing` - Creates closing journal entries
- `account_lock_date_update` - Advisor-level date locking
- `ipai_ppm_monthly_close` - Task-driven close workflow

---

## OCA Submodules (external-src/) - 14 Total

| Repository | Branch | Key Modules | Protocol |
|------------|--------|-------------|----------|
| `reporting-engine` | 18.0 | `bi_sql_editor` | BI/Dashboards |
| `account-closing` | 18.0 | `account_fiscal_year_closing` | Financial Fortification |
| `account-financial-reporting` | 18.0 | `account_tax_balance`, `general_ledger` | Tax Shield |
| `account-financial-tools` | 18.0 | `account_lock_date`, `account_asset` | Financial Fortification |
| `account-invoicing` | 18.0 | `account_invoice_tax_witholding` | Tax Shield (EWT) |
| `project` | 18.0 | `project_milestone_status`, `project_timeline` | Clarity PPM |
| `hr-expense` | 18.0 | `hr_expense_tier_validation` | SAP Concur |
| `purchase-workflow` | 18.0 | `purchase_request`, `purchase_request_to_rfq` | SAP Ariba |
| `maintenance` | 18.0 | `maintenance_request_*` | Cheqroom |
| `dms` | 18.0 | `dms`, `dms_portal` | Notion |
| `calendar` | 18.0 | `resource_booking` | Resource Planning |
| `web` | 18.0 | `web_timeline` | MS Project |
| `contract` | 18.0 | `contract`, `contract_sale` | Supplier Agreements |
| `server-tools` | 18.0 | `base_automation_*`, `onchange_helper` | Token Trap Bypass |

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
| `ipai_finance_ppm` | **REDUCE** | Keep BIR-specific only → `ipai_bir_compliance` |

### Phase 3: Keep (Legitimate Deltas)

| Module | Status | Reason |
|--------|--------|--------|
| `ipai_ce_cleaner` | **KEEP** | No OCA equivalent (hides Enterprise upsells) |
| `tbwa_spectra_integration` | **KEEP** | Company-specific Spectra export |
| `ipai_bir_compliance` | **NEW** | PH-specific DAT file generation |

---

## Updated odoo.conf

```ini
[options]
addons_path =
    /mnt/extra-addons,
    /mnt/external-src/reporting-engine,
    /mnt/external-src/account-closing,
    /mnt/external-src/account-financial-reporting,
    /mnt/external-src/account-financial-tools,
    /mnt/external-src/account-invoicing,
    /mnt/external-src/project,
    /mnt/external-src/hr-expense,
    /mnt/external-src/purchase-workflow,
    /mnt/external-src/maintenance,
    /mnt/external-src/dms,
    /mnt/external-src/calendar,
    /mnt/external-src/web,
    /mnt/external-src/contract,
    /mnt/external-src/server-tools
```

---

## Final Target State

```
addons/                        # Thin deltas only (3 modules)
├── ipai_ce_cleaner/           # KEEP - hides Enterprise upsells
├── ipai_bir_compliance/       # NEW - PH tax DAT file generation
└── tbwa_spectra_integration/  # KEEP - company-specific export

external-src/                  # OCA modules (14 repositories)
├── reporting-engine/          # BI dashboards
├── account-closing/           # Fiscal year closing
├── account-financial-reporting/  # Tax reports, GL, TB
├── account-financial-tools/   # Lock dates, assets
├── account-invoicing/         # Withholding tax (EWT)
├── project/                   # Project extensions
├── hr-expense/                # Expense management
├── purchase-workflow/         # Procurement, RFQ
├── maintenance/               # Asset tracking
├── dms/                       # Document management
├── calendar/                  # Resource booking
├── web/                       # Timeline/Gantt views
├── contract/                  # Supplier contracts
└── server-tools/              # Automation utilities
```

---

## Docker CLI Aliases

```bash
# Add to ~/.bash_aliases
alias oshell="docker exec -it odoo-ce odoo shell -d odoo"
alias ologs="docker compose logs -f odoo"
alias orestart="docker restart odoo-ce && docker logs -f odoo"

odoo-update() {
    docker exec -it odoo-ce odoo -d odoo -u "$1" --stop-after-init
}
alias oupdate=odoo-update
```

---

**Last Updated**: 2025-11-25
**OCA Repositories**: 14
**Custom Deltas**: 3 (target)
