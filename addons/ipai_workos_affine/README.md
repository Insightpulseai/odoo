# IPAI WorkOS - AFFiNE Clone (Umbrella)

## Overview

Installs the full WorkOS AFFiNE-style suite

- **Technical Name:** `ipai_workos_affine`
- **Version:** 18.0.1.0.0
- **Category:** Productivity
- **License:** AGPL-3
- **Author:** InsightPulse AI
- **Application:** Yes
- **Installable:** Yes

## Business Use Case

Umbrella module that installs the complete Work OS suite providing
        AFFiNE/Notion-like functionality:
        - Pages with nested hierarchy
        - Block-based content editing
        - Databases with typed properties
        - Multiple view types (Table, Kanban, Calendar)
        - Edgeless canvas surface
        - Collaboration features
        - Global search
        - Templates

## Functional Scope

## Installation & Dependencies

### Dependencies

- `ipai_workos_core` (IPAI)
- `ipai_workos_blocks` (IPAI)
- `ipai_workos_db` (IPAI)
- `ipai_workos_views` (IPAI)
- `ipai_workos_collab` (IPAI)
- `ipai_workos_search` (IPAI)
- `ipai_workos_templates` (IPAI)
- `ipai_workos_canvas` (IPAI)
- `ipai_platform_permissions` (IPAI)
- `ipai_platform_audit` (IPAI)

### Installation

```bash
# Install module
odoo-bin -d <database> -i ipai_workos_affine --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_workos_affine --stop-after-init
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
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai_workos_affine'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai_workos_affine")]).state)'
```

## Static Validation Status

- Passed: 4
- Warnings: 0
- Failed: 0
