# IPAI Work OS Database

## 1. Overview
Notion-style databases with typed properties

**Technical Name**: `ipai_workos_db`
**Category**: Productivity
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## 2. Functional Scope

        Database module providing Notion-like structured data:
        - Databases with typed properties (columns)
        - Property types: text, number, select, multi-select, date, checkbox, person
        - Rows as records with inline editing
        - Relations between databases
    

## 3. Installation & Dependencies
Dependencies (CE/OCA):
- `base`
- `web`
- `ipai_workos_core`

## 4. Configuration
Key system parameters or settings groups:
- (Audit Pending)

## 5. Data Model
Defined Models:
- `ipai.workos.row`
- `ipai.workos.database`
- `ipai.workos.property`

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
odoo-bin -d <db> -i ipai_workos_db --stop-after-init

# Upgrade
odoo-bin -d <db> -u ipai_workos_db --stop-after-init
```