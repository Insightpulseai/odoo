# IPAI Work OS Views

## 1. Overview
Table, Kanban, and Calendar views for databases

**Technical Name**: `ipai_workos_views`
**Category**: Productivity
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## 2. Functional Scope

        Database view module providing Notion-like view options:
        - Table (grid) view with sorting/filtering
        - Kanban view with group-by
        - Calendar view for date properties
        - Saved views (per user and shared)
        - View switcher UI
    

## 3. Installation & Dependencies
Dependencies (CE/OCA):
- `base`
- `web`
- `ipai_workos_core`
- `ipai_workos_db`

## 4. Configuration
Key system parameters or settings groups:
- (Audit Pending)

## 5. Data Model
Defined Models:
- `ipai.workos.view`

## 6. User Interface
- **Views**: 1 files
- **Menus**: (Audit Pending)

## 7. Security
- **Access Rules**: `ir.model.access.csv` found
- **Groups**: `security.xml` not found

## 8. Integrations
- (Audit Pending)

## 9. Verification Steps
```bash
# Install
odoo-bin -d <db> -i ipai_workos_views --stop-after-init

# Upgrade
odoo-bin -d <db> -u ipai_workos_views --stop-after-init
```