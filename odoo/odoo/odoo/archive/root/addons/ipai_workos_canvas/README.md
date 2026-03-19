# IPAI WorkOS - Canvas (Edgeless)

## Overview

Edgeless canvas surface for WorkOS (AFFiNE-style)

- **Technical Name:** `ipai_workos_canvas`
- **Version:** 18.0.1.0.0
- **Category:** Productivity
- **License:** AGPL-3
- **Author:** InsightPulse AI
- **Application:** No
- **Installable:** Yes

## Business Use Case

Canvas module providing an edgeless infinite surface:
        - Pan and zoom navigation
        - Node-based content placement
        - Integration with blocks and pages
        - Collaborative canvas editing

## Functional Scope

### Data Models

- **ipai.workos.canvas** (Model)
  - WorkOS Canvas
  - Fields: 5 defined

### Views

- : 1
- Form: 1

### Menus

- `menu_ipai_workos_canvas`: Canvas

## Installation & Dependencies

### Dependencies

- `base` (CE Core)
- `web` (CE Core)
- `mail` (CE Core)

### Installation

```bash
# Install module
odoo-bin -d <database> -i ipai_workos_canvas --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_workos_canvas --stop-after-init
```

## Configuration

*No specific configuration required.*

## Security

### Access Rules

*2 access rules defined in ir.model.access.csv*

## Integrations

- Odoo Mail (Email notifications)

## Upgrade Notes

- Current Version: 18.0.1.0.0
- No breaking changes documented

## Verification Steps

```bash
# 1. Verify module is installed
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai_workos_canvas'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai_workos_canvas")]).state)'
```

## Data Files

- `security/ir.model.access.csv`
- `views/canvas_views.xml`

## Static Validation Status

- Passed: 5
- Warnings: 0
- Failed: 0
