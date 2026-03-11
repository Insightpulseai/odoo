# IPAI Work OS Search

## Overview

Global and scoped search for pages and databases

- **Technical Name:** `ipai_workos_search`
- **Version:** 18.0.1.0.0
- **Category:** Productivity
- **License:** AGPL-3
- **Author:** InsightPulse AI
- **Application:** No
- **Installable:** Yes

## Business Use Case

Search module providing Notion-like search:
        - Global search across pages, databases, and blocks
        - Scoped search within spaces or databases
        - Full-text search on block content
        - Quick search results with previews

## Functional Scope

### Data Models

- **ipai.workos.search** (TransientModel)
  - Work OS Search
  - Fields: 6 defined
- **ipai.workos.search.history** (Model)
  - Work OS Search History
  - Fields: 3 defined

### Views

- : 1

### Menus

- `menu_workos_search_history`: Search History

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
odoo-bin -d <database> -i ipai_workos_search --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_workos_search --stop-after-init
```

## Configuration

*No specific configuration required.*

## Security

### Access Rules

*3 access rules defined in ir.model.access.csv*

## Integrations

*No external integrations.*

## Upgrade Notes

- Current Version: 18.0.1.0.0
- No breaking changes documented

## Verification Steps

```bash
# 1. Verify module is installed
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai_workos_search'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai_workos_search")]).state)'
```

## Data Files

- `security/ir.model.access.csv`
- `views/search_views.xml`

## Static Validation Status

- Passed: 5
- Warnings: 0
- Failed: 0
