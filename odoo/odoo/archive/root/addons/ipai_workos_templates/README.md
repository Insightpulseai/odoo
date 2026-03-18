# IPAI Work OS Templates

## Overview

Page and database templates

- **Technical Name:** `ipai_workos_templates`
- **Version:** 18.0.1.0.0
- **Category:** Productivity
- **License:** AGPL-3
- **Author:** InsightPulse AI
- **Application:** No
- **Installable:** Yes

## Business Use Case

Template module for reusable page/database structures:
        - Page templates with pre-defined blocks
        - Database templates with schema
        - Apply templates to create new pages/databases
        - Template gallery

## Functional Scope

### Data Models

- **ipai.workos.template** (Model)
  - Work OS Template
  - Fields: 11 defined
- **ipai.workos.template.tag** (Model)
  - Work OS Template Tag
  - Fields: 2 defined

### Views

- : 1
- Form: 1
- Kanban: 1

### Menus

- `menu_workos_templates`: Templates

## Installation & Dependencies

### Dependencies

- `base` (CE Core)
- `web` (CE Core)
- `ipai_workos_core` (IPAI)
- `ipai_workos_blocks` (IPAI)
- `ipai_workos_db` (IPAI)

### Installation

```bash
# Install module
odoo-bin -d <database> -i ipai_workos_templates --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_workos_templates --stop-after-init
```

## Configuration

*No specific configuration required.*

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
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai_workos_templates'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai_workos_templates")]).state)'
```

## Data Files

- `security/ir.model.access.csv`
- `views/template_views.xml`
- `data/default_templates.xml`

## Static Validation Status

- Passed: 5
- Warnings: 0
- Failed: 0
