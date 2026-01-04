# IPAI Month-End Closing & BIR Tax Filing

## Overview

SAP AFC-style month-end closing with BIR tax compliance for TBWA Finance

- **Technical Name:** `ipai_month_end_closing`
- **Version:** 18.0.1.0.0
- **Category:** Accounting/Accounting
- **License:** AGPL-3
- **Author:** InsightPulse AI
- **Application:** No
- **Installable:** Yes

## Business Use Case

IPAI Month-End Closing & BIR Tax Filing
=======================================

Complete month-end financial closing workflow based on SAP Advanced Financial
Closing (AFC) best practices, tailored for TBWA Finance operations.

Features
--------
* 36 pre-configured closing tasks organized by functional area
* Employee assignments mapped to TBWA Finance team (RIM, BOM, JPAL, LAS, JLI, RMQB, JAP, JRMO)
* Three-tier approval workflow: Preparation → Review → Approval
* Task dependencies matching SAP...

## Functional Scope

## Installation & Dependencies

### Dependencies

- `project` (CE Core)
- `hr` (CE Core)

### Installation

```bash
# Install module
odoo-bin -d <database> -i ipai_month_end_closing --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_month_end_closing --stop-after-init
```

## Configuration

*No specific configuration required.*

## Security

### Access Rules

*2 access rules defined in ir.model.access.csv*

## Integrations

*No external integrations.*

## Upgrade Notes

- Current Version: 18.0.1.0.0
- No breaking changes documented

## Verification Steps

```bash
# 1. Verify module is installed
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai_month_end_closing'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai_month_end_closing")]).state)'
```

## Data Files

- `security/ir.model.access.csv`
- `data/ipai_users.xml`
- `data/project_config.xml`
- `data/ipai_closing_tasks.xml`
- `data/ipai_bir_tasks.xml`

## Static Validation Status

- Passed: 4
- Warnings: 0
- Failed: 0
