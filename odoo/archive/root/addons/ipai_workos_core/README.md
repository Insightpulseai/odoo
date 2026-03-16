# IPAI Work OS Core

## Overview

Notion-style Work OS - Core module with workspaces, spaces, and pages

- **Technical Name:** `ipai_workos_core`
- **Version:** 18.0.1.0.0
- **Category:** Productivity
- **License:** AGPL-3
- **Author:** InsightPulse AI
- **Application:** Yes
- **Installable:** Yes

## Business Use Case

Work OS Core provides the foundation for a Notion-like experience:
        - Workspaces as top-level containers
        - Spaces for organizing content within workspaces
        - Pages with nested page support (tree structure)
        - Sidebar navigation with page tree
        - Integration with blocks, databases, and other Work OS modules

## Functional Scope

### Data Models

- **ipai.workos.page** (Model)
  - Work OS Page
  - Fields: 15 defined
- **ipai.workos.workspace** (Model)
  - Work OS Workspace
  - Fields: 9 defined
- **ipai.workos.space** (Model)
  - Work OS Space
  - Fields: 10 defined

### Views

- : 3
- Kanban: 3
- Form: 3
- Search: 1

### Menus

- `menu_workos_root`: Work OS
- `menu_workos_workspaces`: Workspaces
- `menu_workos_spaces`: Spaces
- `menu_workos_pages`: Pages
- `menu_workos_config`: Configuration

## Installation & Dependencies

### Dependencies

- `base` (CE Core)
- `web` (CE Core)
- `mail` (CE Core)
- `ipai_platform_permissions` (IPAI)
- `ipai_platform_audit` (IPAI)

### Installation

```bash
# Install module
odoo-bin -d <database> -i ipai_workos_core --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_workos_core --stop-after-init
```

## Configuration

*No specific configuration required.*

## Security

### Access Rules

*6 access rules defined in ir.model.access.csv*

## Integrations

- Odoo Mail (Email notifications)

## Upgrade Notes

- Current Version: 18.0.1.0.0
- No breaking changes documented

## Verification Steps

```bash
# 1. Verify module is installed
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai_workos_core'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai_workos_core")]).state)'
```

## Data Files

- `security/ir.model.access.csv`
- `views/workspace_views.xml`
- `views/space_views.xml`
- `views/page_views.xml`
- `views/menu_views.xml`

## Static Validation Status

- Passed: 5
- Warnings: 0
- Failed: 0
