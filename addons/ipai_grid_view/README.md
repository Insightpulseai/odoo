# IPAI Grid/List View

## 1. Overview
Advanced grid and list view with sorting, filtering, and bulk actions

**Technical Name**: `ipai_grid_view`
**Category**: Productivity/Views
**Version**: 18.0.1.0.0
**Author**: IPAI Team

## 2. Functional Scope

IPAI Grid/List View
===================

A comprehensive grid/list view implementation for Odoo 18 featuring:

- **Grid Display**: Configurable column layouts with resize and reorder
- **Search & Filtering**: Real-time keyword search and advanced filter panel
- **Sorting**: Multi-column sort with visual indicators
- **Selection & Bulk Actions**: Row selection with bulk operation support
- **View Switching**: Seamless toggle between list and kanban views
- **Responsive Design**: Horizontal scroll and mobile adaptation
- **Activity Integration**: Activity buttons and status indicators

Technical Stack:
- OWL Components for reactive UI
- Server-side pagination and filtering
- JSON-based configuration storage
- SCSS styling with CSS variables
    

## 3. Installation & Dependencies
Dependencies (CE/OCA):
- `base`
- `web`
- `mail`

## 4. Configuration
Key system parameters or settings groups:
- (Audit Pending)

## 5. Data Model
Defined Models:
- `ipai.grid.view`
- `fieldfields.Char(`
- `record.displayrecord.label or record.field_name or _(Unnamed Column)`
- `modelfields.Char(`
- `ipai.grid.column`
- `ipai.grid.filter.condition`
- `displayfields.Char(compute=_compute_display_name, store=True)`
- `ipai.grid.filter`
- `is_primary: field_name == name,`

## 6. User Interface
- **Views**: 5 files
- **Menus**: (Audit Pending)

## 7. Security
- **Access Rules**: `ir.model.access.csv` found
- **Groups**: `security.xml` found

## 8. Integrations
- (Audit Pending)

## 9. Verification Steps
```bash
# Install
odoo-bin -d <db> -i ipai_grid_view --stop-after-init

# Upgrade
odoo-bin -d <db> -u ipai_grid_view --stop-after-init
```