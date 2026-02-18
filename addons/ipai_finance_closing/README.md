# SAP AFC-Style Month-End Closing Template

## Overview

Month-end financial closing task template based on SAP Advanced Financial Closing

- **Technical Name:** `ipai_finance_closing`
- **Version:** 18.0.1.0.0
- **Category:** Accounting/Accounting
- **License:** AGPL-3
- **Author:** InsightPulse AI
- **Application:** No
- **Installable:** Yes

## Business Use Case

SAP AFC-Style Month-End Closing Template
=========================================

This module provides a comprehensive month-end closing task template
based on SAP S/4HANA Cloud for Advanced Financial Closing (AFC) best practices.

Features:
---------
* Pre-configured project template for month-end close
* 25+ closing tasks organized by functional area
* Task dependencies matching SAP AFC workflow
* Tags for GL, AP, AR, Assets, Tax, Reporting
* Automated actions for recurring tasks
* BIR (Phil...

## Functional Scope

## Installation & Dependencies

### Dependencies

- `project` (CE Core)
- `account` (CE Core)

### Installation

```bash
# Install module
odoo-bin -d <database> -i ipai_finance_closing --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_finance_closing --stop-after-init
```

## Configuration

*No specific configuration required.*

### Scheduled Actions

- **Update Currency Rates (BSP)** (Inactive)
- **Auto-Reverse Prior Month Accruals** (Active)
- **Weekly Customer Follow-up** (Active)
- **Period Lock Reminder** (Active)

## Security

### Access Rules

*4 access rules defined in ir.model.access.csv*

## Integrations

*No external integrations.*

## Upgrade Notes

- Current Version: 18.0.1.0.0
- No breaking changes documented

## Verification Steps

```bash
# 1. Verify module is installed
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai_finance_closing'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai_finance_closing")]).state)'
```

## Data Files

- `data/closing_tasks.xml`

## Static Validation Status

- Passed: 4
- Warnings: 0
- Failed: 0
