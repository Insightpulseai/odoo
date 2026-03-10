# IPAI BIR Tax Compliance

## Overview

Philippine BIR tax compliance - 36 eBIRForms support

- **Technical Name:** `ipai_bir_tax_compliance`
- **Version:** 18.0.1.0.0
- **Category:** Accounting/Localizations
- **License:** AGPL-3
- **Author:** IPAI
- **Application:** Yes
- **Installable:** Yes

## Business Use Case

Complete Philippine Bureau of Internal Revenue (BIR) tax compliance module.

        Supported Tax Types:
        - VAT (Forms 2550M, 2550Q)
        - Withholding Tax (Forms 1600, 1601-C, 1601-E, 1601-F, 1604-CF)
        - Income Tax (Forms 1700, 1701, 1702)
        - Excise Tax (Forms 2200A, 2200P, 2200T, 2200M, 2200AN)
        - Percentage Tax (Forms 2551M, 2551Q)
        - Capital Gains Tax (Forms 1706, 1707)
        - Documentary Stamp Tax (Forms 2000, 2000-OT)

        Features:
        - A...

## Functional Scope

### Data Models

- **bir.filing.deadline** (Model)
  - BIR Filing Deadline
  - Fields: 9 defined
- **bir.withholding.return** (Model)
  - BIR Withholding Tax Return
  - Fields: 3 defined
- **bir.withholding.line** (Model)
  - BIR Withholding Tax Line
  - Fields: 8 defined
- **bir.alphalist** (Model)
  - BIR Annual Alphalist
  - Fields: 7 defined
- **bir.alphalist.line** (Model)
  - BIR Alphalist Line
  - Fields: 5 defined
- **res.partner** (Model)
  - Fields: 5 defined
- **bir.tax.return** (Model)
  - BIR Tax Return
  - Fields: 19 defined
- **bir.tax.return.line** (Model)
  - BIR Tax Return Line
  - Fields: 8 defined
- **bir.vat.return** (Model)
  - BIR VAT Return
- **bir.vat.line** (Model)
  - BIR VAT Line
  - Fields: 8 defined

### Views

- : 7
- Form: 5
- Search: 2
- Calendar: 1

### Menus

- `menu_bir_root`: BIR Compliance
- `menu_bir_dashboard`: Dashboard
- `menu_bir_returns`: Tax Returns
- `menu_bir_vat`: VAT Returns (2550M/Q)
- `menu_bir_withholding`: Withholding Tax (1601)
- ... and 6 more

## Installation & Dependencies

### Dependencies

- `base` (CE Core)
- `mail` (CE Core)
- `account` (CE Core)

### Installation

```bash
# Install module
odoo-bin -d <database> -i ipai_bir_tax_compliance --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_bir_tax_compliance --stop-after-init
```

## Configuration

*No specific configuration required.*

### Scheduled Actions

- **BIR: Generate Filing Deadlines** (Active)
- **BIR: Send Deadline Alerts** (Active)

## Security

### Access Rules

*18 access rules defined in ir.model.access.csv*

## Integrations

- Odoo Mail (Email notifications)

## Upgrade Notes

- Current Version: 18.0.1.0.0
- No breaking changes documented

## Verification Steps

```bash
# 1. Verify module is installed
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai_bir_tax_compliance'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai_bir_tax_compliance")]).state)'
```

## Data Files

- `security/ir.model.access.csv`
- `data/bir_tax_rates.xml`
- `data/bir_filing_deadlines.xml`
- `data/ir_cron.xml`
- `views/bir_tax_return_views.xml`
- `views/bir_vat_views.xml`
- `views/bir_withholding_views.xml`
- `views/bir_dashboard_views.xml`
- `views/res_partner_views.xml`
- `views/menu.xml`

## Static Validation Status

- Passed: 5
- Warnings: 0
- Failed: 0
