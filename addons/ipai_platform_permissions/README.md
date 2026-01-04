# IPAI Platform Permissions

## 1. Overview
Scope-based permission and role management for IPAI modules

**Technical Name**: `ipai_platform_permissions`
**Category**: Hidden/Tools
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## 2. Functional Scope

        Platform-level permission management providing:
        - Workspace/space/page/db permission scopes
        - Role definitions (admin/member/guest)
        - Record rules generation
        - Share token management
    

## 3. Installation & Dependencies
Dependencies (CE/OCA):
- `base`
- `mail`

## 4. Configuration
Key system parameters or settings groups:
- (Audit Pending)

## 5. Data Model
Defined Models:
- `ipai.share.token`
- `ipai.permission`

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
odoo-bin -d <db> -i ipai_platform_permissions --stop-after-init

# Upgrade
odoo-bin -d <db> -u ipai_platform_permissions --stop-after-init
```