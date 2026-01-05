# IPAI Work OS Blocks

## Overview

Notion-style block editor for pages

- **Technical Name:** `ipai_workos_blocks`
- **Version:** 18.0.1.0.0
- **Category:** Productivity
- **License:** AGPL-3
- **Author:** InsightPulse AI
- **Application:** No
- **Installable:** Yes

## Business Use Case

Block editor providing Notion-like content editing:
        - Block types: paragraph, heading, lists, todo, toggle, divider, quote, callout
        - Slash command menu for quick block insertion
        - Drag and drop block reordering
        - Block content stored as structured JSON
        - OWL-based editor surface

## Functional Scope

### Data Models

- **ipai.workos.block** (Model)
  - Work OS Block
  - Fields: 14 defined

### Views

- : 1
- Form: 1

### Menus

- `menu_workos_blocks`: Blocks

## Installation & Dependencies

### Dependencies

- `base` (CE Core)
- `web` (CE Core)
- `ipai_workos_core` (IPAI)

### Installation

```bash
# Install module
odoo-bin -d <database> -i ipai_workos_blocks --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_workos_blocks --stop-after-init
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
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai_workos_blocks'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai_workos_blocks")]).state)'
```

## Data Files

- `security/ir.model.access.csv`
- `views/block_views.xml`

## Static Validation Status

- Passed: 5
- Warnings: 0
- Failed: 0
