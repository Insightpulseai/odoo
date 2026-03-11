# IPAI Work OS Collaboration

## Overview

Comments, mentions, and notifications

- **Technical Name:** `ipai_workos_collab`
- **Version:** 18.0.1.0.0
- **Category:** Productivity
- **License:** AGPL-3
- **Author:** InsightPulse AI
- **Application:** No
- **Installable:** Yes

## Business Use Case

Collaboration module providing Notion-like features:
        - Comments on pages and database rows
        - @mentions with notifications
        - Activity log for edits/moves/shares
        - Integration with mail module

## Functional Scope

### Data Models

- **ipai.workos.comment** (Model)
  - Work OS Comment
  - Fields: 14 defined

### Views

- : 1
- Form: 1

### Menus

- `menu_workos_comments`: Comments

## Installation & Dependencies

### Dependencies

- `base` (CE Core)
- `mail` (CE Core)
- `ipai_workos_core` (IPAI)

### Installation

```bash
# Install module
odoo-bin -d <database> -i ipai_workos_collab --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_workos_collab --stop-after-init
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
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai_workos_collab'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai_workos_collab")]).state)'
```

## Data Files

- `security/ir.model.access.csv`
- `views/comment_views.xml`

## Static Validation Status

- Passed: 5
- Warnings: 0
- Failed: 0
