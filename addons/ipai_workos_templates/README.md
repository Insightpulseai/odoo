# IPAI Work OS Templates

## 1. Overview
Page and database templates

**Technical Name**: `ipai_workos_templates`
**Category**: Productivity
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## 2. Functional Scope

        Template module for reusable page/database structures:
        - Page templates with pre-defined blocks
        - Database templates with schema
        - Apply templates to create new pages/databases
        - Template gallery
    

## 3. Installation & Dependencies
Dependencies (CE/OCA):
- `base`
- `web`
- `ipai_workos_core`
- `ipai_workos_blocks`
- `ipai_workos_db`

## 4. Configuration
Key system parameters or settings groups:
- (Audit Pending)

## 5. Data Model
Defined Models:
- `ipai.workos.template.tag`
- `ipai.workos.template`

## 6. User Interface
- **Views**: 2 files
- **Menus**: (Audit Pending)

## 7. Security
- **Access Rules**: `ir.model.access.csv` found
- **Groups**: `security.xml` not found

## 8. Integrations
- (Audit Pending)

## 9. Verification Steps
```bash
# Install
odoo-bin -d <db> -i ipai_workos_templates --stop-after-init

# Upgrade
odoo-bin -d <db> -u ipai_workos_templates --stop-after-init
```