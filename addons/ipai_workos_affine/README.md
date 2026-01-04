# IPAI WorkOS - AFFiNE Clone (Umbrella)

## 1. Overview
Installs the full WorkOS AFFiNE-style suite

**Technical Name**: `ipai_workos_affine`
**Category**: Productivity
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## 2. Functional Scope

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
    

## 3. Installation & Dependencies
Dependencies (CE/OCA):
- `ipai_workos_core`
- `ipai_workos_blocks`
- `ipai_workos_db`
- `ipai_workos_views`
- `ipai_workos_collab`
- `ipai_workos_search`
- `ipai_workos_templates`
- `ipai_workos_canvas`
- `ipai_platform_permissions`
- `ipai_platform_audit`

## 4. Configuration
Key system parameters or settings groups:
- (Audit Pending)

## 5. Data Model
Defined Models:
- No explicit new models detected (may inherit existing).

## 6. User Interface
- **Views**: 0 files
- **Menus**: (Audit Pending)

## 7. Security
- **Access Rules**: `ir.model.access.csv` not found
- **Groups**: `security.xml` not found

## 8. Integrations
- (Audit Pending)

## 9. Verification Steps
```bash
# Install
odoo-bin -d <db> -i ipai_workos_affine --stop-after-init

# Upgrade
odoo-bin -d <db> -u ipai_workos_affine --stop-after-init
```