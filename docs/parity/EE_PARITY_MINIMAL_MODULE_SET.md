# EE Parity – Minimal Installable Module Set

> **Version**: 1.0.0
> **Last Updated**: 2026-01-28

This document defines the **minimum** module set that must always be
present in the codebase and visible in Apps as installable/upgradable.

---

## 1. Folder Layout (Canonical)

```
odoo-ce/
├── odoo/addons/              # Core Odoo addons (read-only)
├── addons/
│   ├── oca/                  # OCA addons (cloned repos)
│   │   ├── account-financial-tools/
│   │   ├── account-financial-reporting/
│   │   ├── account-reconcile/
│   │   ├── currency/
│   │   ├── sale-workflow/
│   │   ├── server-ux/
│   │   ├── server-tools/
│   │   └── ...
│   └── ipai/                 # IPAI custom addons
│       ├── ipai_mailgun_bridge/
│       ├── ipai_website_shell/
│       ├── ipai_enterprise_bridge/
│       └── ...
```

These paths are exported via `ODOO_EXTRA_ADDONS` and `ADDONS_PATH` and
are used by all dev/staging/prod compose files.

---

## 2. Required OCA Modules (Must Be Present & Installable)

### 2.1 Accounting (Global "Must Have" List)

From the [OCA "must-have Accounting modules" list](https://test.odoo-community.org/list-of-must-have-oca-accounting-modules):

| Module | Repository | Purpose |
|--------|------------|---------|
| `account_analytic_required` | account-analytic | Enforce analytic on GL entries |
| `partner_statement` | account-financial-reporting | Customer/vendor statements |
| `account_asset_management` | account-financial-tools | Depreciation & asset lifecycle |
| `account_chart_update` | account-financial-tools | Update CoA from template |
| `account_journal_lock_date` | account-financial-tools | Lock journals by date |
| `account_lock_date_update` | account-financial-tools | Bulk lock date updates |
| `account_move_line_tax_editable` | account-financial-tools | Edit tax on posted entries |
| `account_usability` | account-financial-tools | UX improvements |
| `account_reconcile_oca` | account-reconcile | Bank reconciliation UI |
| `account_reconcile_model_oca` | account-reconcile | Reconcile model enhancements |
| `account_statement_base` | account-reconcile | Statement base framework |
| `currency_rate_update` | currency | Auto-update exchange rates |
| `mis_builder` | mis-builder | Custom KPI/MIS reports |
| `account_financial_report` | account-financial-reporting | P&L, Balance Sheet, Trial Balance |
| `date_range` | server-ux | Reporting date ranges |
| `date_range_account` | account-financial-tools | Accounting date ranges |

### 2.2 Sales (Core "Must Have" List)

From the [OCA "must-have Sales modules" list](https://test.odoo-community.org/list-of-must-have-sales-modules):

| Module | Repository | Purpose |
|--------|------------|---------|
| `portal_sale_order_search` | sale-workflow | Portal order search |
| `sale_cancel_reason` | sale-workflow | Track cancellation reasons |
| `sale_order_line_input` | sale-workflow | Better line input UX |
| `sale_order_line_menu` | sale-workflow | Direct line access menu |
| `sale_order_line_price_history` | sale-workflow | Price change history |
| `sale_report_salesperson_from_partner` | sale-workflow | Salesperson attribution |

### 2.3 Base / UX / Technical

From the [OCA "must-have Base modules" list](https://odoo-community.org/list-of-must-have-oca-modules):

| Module | Repository | Purpose |
|--------|------------|---------|
| `web_environment_ribbon` | web | Environment indicator ribbon |
| `server_environment` | server-env | Environment-based config |
| `base_technical_features` | server-ux | Technical features toggle |
| `queue_job` | queue | Async job processing |
| `auditlog` | server-tools | Change tracking |

---

## 3. Required IPAI Modules

### 3.1 Minimum IPAI Layer (Must Be Present & Installable)

| Module | Purpose | Status |
|--------|---------|--------|
| `ipai_mailgun_bridge` | Mailgun webhook + email observability | Required |
| `ipai_website_shell` | Website shell/PWA framework | Required |

### 3.2 Next-Wave IPAI Modules (Recommended)

Keep in repo even if not yet installed:

| Module | Purpose | Status |
|--------|---------|--------|
| `ipai_prisma_consulting` | PRISMA services + CRM bridge | Recommended |
| `ipai_figma_bridge` | Figma→Odoo design sync | Recommended |
| `ipai_rag_bridge` | RAG query + analytics | Recommended |
| `ipai_enterprise_bridge` | EE-parity glue (accounting/PPM/AI mixins) | Recommended |

All IPAI modules live under: `./addons/ipai/<module_name>`

---

## 4. Installation Expectations

All modules listed above must:

1. **Appear in Apps** when filtering by `Module` and searching for `oca` or `ipai`
2. **Be installable from UI** AND via CLI using the EE-parity scripts
3. **Be upgradable** without manual intervention (no hard-coded version pins)

### Environment Variables

```bash
# Core accounting + sales + base/UX parity modules
ODOO_EE_PARITY_OCA_MODULES="account_analytic_required,partner_statement,..."

# IPAI custom modules that must be present & installable
ODOO_EE_PARITY_IPAI_MODULES="ipai_mailgun_bridge,ipai_website_shell"

# Roll-up convenience (used by install/list scripts)
ODOO_EE_PARITY_MODULES="$ODOO_EE_PARITY_OCA_MODULES,$ODOO_EE_PARITY_IPAI_MODULES"
```

---

## 5. Verification Commands

### List Parity Modules

```bash
./scripts/dev/list-ee-parity-modules.sh
```

### Install Parity Modules

```bash
./scripts/dev/install-ee-parity-modules.sh
```

### Check Module States in Odoo

```bash
docker compose exec -T odoo odoo shell -d odoo_core << 'PYEOF'
from odoo import api, SUPERUSER_ID
env = api.Environment(cr, SUPERUSER_ID, {})
modules = [
    'account_reconcile_oca',
    'account_financial_report',
    'mis_builder',
    'ipai_mailgun_bridge',
    'ipai_website_shell',
]
mods = env['ir.module.module'].search([('name', 'in', modules)])
for m in mods:
    print(f"{m.name}: {m.state}")
PYEOF
```

---

## 6. OCA Repository Mapping

| Repository | Branch | Modules Included |
|------------|--------|------------------|
| `OCA/account-financial-tools` | 19.0 | account_asset_management, account_chart_update, account_journal_lock_date, account_lock_date_update, account_move_line_tax_editable, account_usability, date_range_account |
| `OCA/account-financial-reporting` | 19.0 | partner_statement, account_financial_report |
| `OCA/account-reconcile` | 19.0 | account_reconcile_oca, account_reconcile_model_oca, account_statement_base |
| `OCA/account-analytic` | 19.0 | account_analytic_required |
| `OCA/currency` | 19.0 | currency_rate_update |
| `OCA/mis-builder` | 19.0 | mis_builder |
| `OCA/sale-workflow` | 19.0 | portal_sale_order_search, sale_cancel_reason, sale_order_line_input, sale_order_line_menu, sale_order_line_price_history, sale_report_salesperson_from_partner |
| `OCA/server-ux` | 19.0 | date_range, base_technical_features |
| `OCA/server-tools` | 19.0 | auditlog |
| `OCA/server-env` | 19.0 | server_environment |
| `OCA/web` | 19.0 | web_environment_ribbon |
| `OCA/queue` | 19.0 | queue_job |

---

## 7. Rollback Procedure

If any module breaks production:

```bash
# 1. Snapshot before install (always)
docker exec odoo-db pg_dump -U odoo -d odoo_prod > backup_$(date +%F)_pre_ee_minimal.sql

# 2. Rollback if needed
docker exec -i odoo-db psql -U odoo -d odoo_prod < backup_YYYY-MM-DD_pre_ee_minimal.sql
```

Or selectively uninstall problematic modules by removing them from `ODOO_EE_PARITY_MODULES`.

---

## References

- [OCA Must-Have Accounting Modules](https://test.odoo-community.org/list-of-must-have-oca-accounting-modules)
- [OCA Must-Have Sales Modules](https://test.odoo-community.org/list-of-must-have-sales-modules)
- [OCA Must-Have Base Modules](https://odoo-community.org/list-of-must-have-oca-modules)
- [EE Parity Layering Analysis](./EE_PARITY_LAYERING_ANALYSIS.md)
