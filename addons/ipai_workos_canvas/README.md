# IPAI WorkOS - Canvas (Edgeless)

## 1. Overview
Edgeless canvas surface for WorkOS (AFFiNE-style)

**Technical Name**: `ipai_workos_canvas`
**Category**: Productivity
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## 2. Functional Scope

        Canvas module providing an edgeless infinite surface:
        - Pan and zoom navigation
        - Node-based content placement
        - Integration with blocks and pages
        - Collaborative canvas editing
    

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
- `ipai.workos.canvas`

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
odoo-bin -d <db> -i ipai_workos_canvas --stop-after-init

# Upgrade
odoo-bin -d <db> -u ipai_workos_canvas --stop-after-init
```