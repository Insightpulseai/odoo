# IPAI Work OS Database

## Overview

Notion-style databases with typed properties

- **Technical Name:** `ipai_workos_db`
- **Version:** 18.0.1.0.0
- **Category:** Productivity
- **License:** AGPL-3
- **Author:** InsightPulse AI
- **Application:** No
- **Installable:** Yes

## Business Use Case

Database module providing Notion-like structured data:
        - Databases with typed properties (columns)
        - Property types: text, number, select, multi-select, date, checkbox, person
        - Rows as records with inline editing
        - Relations between databases

## Functional Scope

### Data Models

- **ipai.workos.row** (Model)
  - Work OS Database Row
  - Fields: 5 defined
- **ipai.workos.property** (Model)
  - Work OS Database Property
  - Fields: 9 defined
- **ipai.workos.database** (Model)
  - Work OS Database
  - Fields: 9 defined

### Views

- : 2
- Form: 2

### Menus

- `menu_workos_databases`: Databases

## Installation & Dependencies

### Dependencies

- `base` (CE Core)
- `web` (CE Core)
- `ipai_workos_core` (IPAI)

### Installation

```bash
# Install module
odoo-bin -d <database> -i ipai_workos_db --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_workos_db --stop-after-init
```

## Configuration

*No specific configuration required.*

## Security

### Access Rules

*6 access rules defined in ir.model.access.csv*

## Integrations

*No external integrations.*

## Upgrade Notes

- Current Version: 18.0.1.0.0
- No breaking changes documented

## Verification Steps

```bash
# 1. Verify module is installed
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai_workos_db'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai_workos_db")]).state)'
```

## Data Files

- `security/ir.model.access.csv`
- `views/database_views.xml`

## Static Validation Status

- Passed: 5
- Warnings: 0
- Failed: 0
