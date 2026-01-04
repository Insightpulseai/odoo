# IPAI Work OS Collaboration

## 1. Overview
Comments, mentions, and notifications

**Technical Name**: `ipai_workos_collab`
**Category**: Productivity
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## 2. Functional Scope

        Collaboration module providing Notion-like features:
        - Comments on pages and database rows
        - @mentions with notifications
        - Activity log for edits/moves/shares
        - Integration with mail module
    

## 3. Installation & Dependencies
Dependencies (CE/OCA):
- `base`
- `mail`
- `ipai_workos_core`

## 4. Configuration
Key system parameters or settings groups:
- (Audit Pending)

## 5. Data Model
Defined Models:
- `record.targettarget.display_name if target.exists() else Deleted`
- `record.targetUnknown`
- `targetfields.Char(string=Target Name, compute=_compute_target_name)`
- `ipai.workos.comment`

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
odoo-bin -d <db> -i ipai_workos_collab --stop-after-init

# Upgrade
odoo-bin -d <db> -u ipai_workos_collab --stop-after-init
```