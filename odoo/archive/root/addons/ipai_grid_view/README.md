# IPAI Grid/List View

## Overview

Advanced grid and list view with sorting, filtering, and bulk actions

- **Technical Name:** `ipai_grid_view`
- **Version:** 18.0.1.0.0
- **Category:** Productivity/Views
- **License:** AGPL-3
- **Author:** IPAI Team
- **Application:** No
- **Installable:** Yes

## Business Use Case

IPAI Grid/List View
===================

A comprehensive grid/list view implementation for Odoo 18 featuring:

- **Grid Display**: Configurable column layouts with resize and reorder
- **Search & Filtering**: Real-time keyword search and advanced filter panel
- **Sorting**: Multi-column sort with visual indicators
- **Selection & Bulk Actions**: Row selection with bulk operation support
- **View Switching**: Seamless toggle between list and kanban views
- **Responsive Design**: Horizontal scroll...

## Functional Scope

### Data Models

- **ipai.grid.column** (Model)
  - Grid Column Configuration
  - Fields: 30 defined
- **ipai.grid.filter** (Model)
  - Grid View Filter
  - Fields: 12 defined
- **ipai.grid.filter.condition** (TransientModel)
  - Grid Filter Condition
  - Fields: 13 defined
- **ipai.grid.view** (Model)
  - Grid View Configuration
  - Fields: 22 defined

### Views

- : 3
- Form: 3
- Search: 3

### Menus

- `menu_ipai_grid_view_root`: Grid Views
- `menu_ipai_grid_view_config`: Configurations
- `menu_ipai_grid_column`: Columns
- `menu_ipai_grid_filter`: Saved Filters

## Installation & Dependencies

### Dependencies

- `base` (CE Core)
- `web` (CE Core)
- `mail` (CE Core)

### Installation

```bash
# Install module
odoo-bin -d <database> -i ipai_grid_view --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_grid_view --stop-after-init
```

## Configuration

*No specific configuration required.*

## Security

### Security Groups

- `group_grid_view_user`: User
- `group_grid_view_manager`: Manager

### Access Rules

*7 access rules defined in ir.model.access.csv*

### Record Rules

- `rule_grid_filter_user`: Grid Filter: Users see own or global filters
- `rule_grid_filter_manager`: Grid Filter: Managers see all
- `rule_grid_view_read`: Grid View: Users can read all
- `rule_grid_view_manager`: Grid View: Managers can modify

## Integrations

- Odoo Mail (Email notifications)

## Upgrade Notes

- Current Version: 18.0.1.0.0
- No breaking changes documented

## Verification Steps

```bash
# 1. Verify module is installed
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai_grid_view'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai_grid_view")]).state)'
```

## Data Files

- `security/security.xml`
- `security/ir.model.access.csv`
- `views/grid_view_views.xml`
- `views/grid_column_views.xml`
- `views/grid_filter_views.xml`
- `data/demo_data.xml`

## Static Validation Status

- Passed: 5
- Warnings: 0
- Failed: 0
