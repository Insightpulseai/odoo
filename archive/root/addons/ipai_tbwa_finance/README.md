# IPAI TBWA Finance

## Overview

Unified month-end closing + BIR tax compliance for TBWA Philippines

- **Technical Name:** `ipai_tbwa_finance`
- **Version:** 18.0.1.0.0
- **Category:** Accounting
- **License:** AGPL-3
- **Author:** IPAI / TBWA
- **Application:** Yes
- **Installable:** Yes

## Business Use Case

Complete finance operations module for TBWA Philippines combining:

        1. MONTH-END CLOSING (SAP AFC Replacement)
           - Template-driven 36-task checklist across 4 phases
           - RACI workflow (Prep → Review → Approve)
           - Holiday-aware workday scheduling
           - Progress tracking dashboards

        2. BIR TAX COMPLIANCE (Philippine Statutory)
           - 36 eBIRForms support (VAT, WHT, Income, Excise)
           - Filing deadline calendar with alerts
           -...

## Functional Scope

### Data Models

- **bir.return** (Model)
  - BIR Tax Return
  - Fields: 15 defined
- **bir.return.line** (Model)
  - BIR Return Line
  - Fields: 7 defined
- **compliance.check** (Model)
  - Compliance Check
  - Fields: 12 defined
- **res.partner** (Model)
  - Fields: 5 defined
- **ph.holiday** (Model)
  - Philippine Holiday
  - Fields: 5 defined
- **finance.task.template** (Model)
  - Finance Task Template
  - Fields: 19 defined
- **closing.period** (Model)
  - Closing Period
  - Fields: 15 defined
- **finance.task** (Model)
  - Finance Task
  - Fields: 31 defined

### Views

- : 8
- Form: 5
- Search: 2
- Kanban: 2
- Calendar: 1

### Menus

- `menu_tbwa_finance_root`: TBWA Finance
- `menu_closing_periods`: Closing Periods
- `menu_finance_tasks`: All Tasks
- `menu_bir`: BIR Compliance
- `menu_bir_returns`: BIR Returns
- ... and 4 more

## Installation & Dependencies

### Dependencies

- `base` (CE Core)
- `mail` (CE Core)
- `account` (CE Core)

### Installation

```bash
# Install module
odoo-bin -d <database> -i ipai_tbwa_finance --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_tbwa_finance --stop-after-init
```

## Configuration

*No specific configuration required.*

### Scheduled Actions

- **TBWA Finance: Send Overdue Notifications** (Active)

## Security

### Access Rules

*14 access rules defined in ir.model.access.csv*

## Integrations

- Odoo Mail (Email notifications)

## Upgrade Notes

- Current Version: 18.0.1.0.0
- No breaking changes documented

## Verification Steps

```bash
# 1. Verify module is installed
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai_tbwa_finance'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai_tbwa_finance")]).state)'
```

## Data Files

- `security/ir.model.access.csv`
- `data/ph_holidays.xml`
- `data/month_end_templates.xml`
- `data/bir_form_types.xml`
- `data/compliance_checks.xml`
- `data/ir_cron.xml`
- `views/ph_holiday_views.xml`
- `views/finance_task_views.xml`
- `views/closing_period_views.xml`
- `views/bir_return_views.xml`
- `views/dashboard_views.xml`
- `views/res_partner_views.xml`
- `views/menu.xml`

## Static Validation Status

- Passed: 5
- Warnings: 0
- Failed: 0
