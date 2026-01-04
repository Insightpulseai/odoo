# IPAI Work OS Core

## 1. Overview
Notion-style Work OS - Core module with workspaces, spaces, and pages

**Technical Name**: `ipai_workos_core`
**Category**: Productivity
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## 2. Functional Scope

        Work OS Core provides the foundation for a Notion-like experience:
        - Workspaces as top-level containers
        - Spaces for organizing content within workspaces
        - Pages with nested page support (tree structure)
        - Sidebar navigation with page tree
        - Integration with blocks, databases, and other Work OS modules
    

## 3. Installation & Dependencies
Dependencies (CE/OCA):
- `base`
- `web`
- `mail`
- `ipai_platform_permissions`
- `ipai_platform_audit`

## 4. Configuration
Key system parameters or settings groups:
- (Audit Pending)

## 5. Data Model
Defined Models:
- `ipai.workos.space`
- `_parentparent_id`
- `ipai.workos.workspace`
- `ipai.workos.page`

## 6. User Interface
- **Views**: 4 files
- **Menus**: (Audit Pending)

## 7. Security
- **Access Rules**: `ir.model.access.csv` found
- **Groups**: `security.xml` not found

## 8. Integrations
- (Audit Pending)

## 9. Verification Steps
```bash
# Install
odoo-bin -d <db> -i ipai_workos_core --stop-after-init

# Upgrade
odoo-bin -d <db> -u ipai_workos_core --stop-after-init
```