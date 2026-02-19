# IPAI Platform Permissions

## Overview

Scope-based permission and role management for IPAI modules

- **Technical Name:** `ipai_platform_permissions`
- **Version:** 18.0.1.0.0
- **Category:** Hidden/Tools
- **License:** AGPL-3
- **Author:** InsightPulse AI
- **Application:** No
- **Installable:** Yes

## Business Use Case

Platform-level permission management providing:
        - Workspace/space/page/db permission scopes
        - Role definitions (admin/member/guest)
        - Record rules generation
        - Share token management

## Functional Scope

### Data Models

- **ipai.permission** (Model)
  - IPAI Permission Scope
  - Fields: 7 defined
- **ipai.share.token** (Model)
  - IPAI Share Token
  - Fields: 7 defined

### Views

- : 2
- Form: 1

## Installation & Dependencies

### Dependencies

- `base` (CE Core)
- `mail` (CE Core)

### Installation

```bash
# Install module
odoo-bin -d <database> -i ipai_platform_permissions --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_platform_permissions --stop-after-init
```

## Configuration

*No specific configuration required.*

## Security

### Access Rules

*4 access rules defined in ir.model.access.csv*

## Integrations

- Odoo Mail (Email notifications)

## Upgrade Notes

- Current Version: 18.0.1.0.0
- No breaking changes documented

## Verification Steps

```bash
# 1. Verify module is installed
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai_platform_permissions'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai_platform_permissions")]).state)'
```

## Data Files

- `security/ir.model.access.csv`
- `views/permission_views.xml`

## Static Validation Status

- Passed: 5
- Warnings: 0
- Failed: 0
