# IPAI Work OS Views

## Overview

Table, Kanban, and Calendar views for databases

- **Technical Name:** `ipai_workos_views`
- **Version:** 18.0.1.0.0
- **Category:** Productivity
- **License:** AGPL-3
- **Author:** InsightPulse AI
- **Application:** No
- **Installable:** Yes

## Business Use Case

Database view module providing Notion-like view options:
        - Table (grid) view with sorting/filtering
        - Kanban view with group-by
        - Calendar view for date properties
        - Saved views (per user and shared)
        - View switcher UI

## Functional Scope

### Data Models

- **ipai.workos.view** (Model)
  - Work OS Database View
  - Fields: 13 defined

### Views

- : 1
- Form: 1

### Menus

- `menu_workos_views`: Saved Views

## Installation & Dependencies

### Dependencies

- `base` (CE Core)
- `web` (CE Core)
- `ipai_workos_core` (IPAI)
- `ipai_workos_db` (IPAI)

### Installation

```bash
# Install module
odoo-bin -d <database> -i ipai_workos_views --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_workos_views --stop-after-init
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
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai_workos_views'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai_workos_views")]).state)'
```

## Data Files

- `security/ir.model.access.csv`
- `views/view_views.xml`

## Static Validation Status

- Passed: 5
- Warnings: 0
- Failed: 0
