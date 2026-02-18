# IPAI Finance PPM – TBWA Complete Configuration

## Overview

Complete seed data for 8-employee Finance SSC with BIR compliance and month-end closing tasks

- **Technical Name:** `ipai_finance_ppm_umbrella`
- **Version:** 1.0.0
- **Category:** 
- **License:** LGPL-3
- **Author:** InsightPulse AI
- **Application:** No
- **Installable:** Yes

## Business Use Case

TBWA Finance PPM Umbrella Configuration
========================================

Complete seed data for Finance SSC operations:

**8 Employees:**
- RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB

**BIR Tax Forms (22 entries for 2026):**
- 1601-C / 0619-E (Monthly - 12 months)
- 2550Q (Quarterly VAT - 4 quarters)
- 1601-EQ (Quarterly EWT - 4 quarters)
- 1702-RT/EX (Annual Income Tax - 1 entry)
- 1702Q (Quarterly Income Tax - 1 entry)

**Month-End Closing Tasks (36 entries):**
- Payroll & Personnel
- ...

## Functional Scope

## Installation & Dependencies

### Dependencies

- `ipai_finance_ppm` (IPAI)
- `project` (CE Core)

### Installation

```bash
# Install module
odoo-bin -d <database> -i ipai_finance_ppm_umbrella --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_finance_ppm_umbrella --stop-after-init
```

## Configuration

*No specific configuration required.*

## Security

*No specific security configuration.*

## Integrations

*No external integrations.*

## Upgrade Notes

- Current Version: 1.0.0
- No breaking changes documented

## Verification Steps

```bash
# 1. Verify module is installed
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai_finance_ppm_umbrella'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai_finance_ppm_umbrella")]).state)'
```

## Data Files

- `security/ir.model.access.csv`
- `data/01_employees.xml`
- `data/02_logframe_complete.xml`
- `data/03_bir_schedule_2026.xml`
- `data/04_closing_tasks.xml`
- `data/05_raci_assignments.xml`

## Static Validation Status

- Passed: 4
- Warnings: 0
- Failed: 0
