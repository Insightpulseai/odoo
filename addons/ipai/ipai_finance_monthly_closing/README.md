# IPAI Finance Monthly Closing

## Overview

Structured month-end closing and BIR filing on top of Projects (CE/OCA-only).

- **Technical Name:** `ipai_finance_monthly_closing`
- **Version:** 18.0.1.0.0
- **Category:** Accounting/Finance
- **License:** AGPL-3
- **Author:** InsightPulseAI
- **Application:** No
- **Installable:** Yes

## Business Use Case

*No business use case documented.*

## Functional Scope

### Data Models

- **project.task** (Model)
  - Fields: 18 defined

## Installation & Dependencies

### Dependencies

- `project` (CE Core)

### Installation

```bash
# Install module
odoo-bin -d <database> -i ipai_finance_monthly_closing --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_finance_monthly_closing --stop-after-init
```

## Configuration

*No specific configuration required.*

## Security

*No specific security configuration.*

## Integrations

*No external integrations.*

## Upgrade Notes

- Current Version: 18.0.1.0.0
- No breaking changes documented

## Verification Steps

```bash
# 1. Verify module is installed
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai_finance_monthly_closing'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai_finance_monthly_closing")]).state)'
```

## Data Files

- `security/ir.model.access.csv`
- `views/project_task_views.xml`
- `data/project_templates.xml`

## Static Validation Status

- Passed: 4
- Warnings: 1
- Failed: 0
