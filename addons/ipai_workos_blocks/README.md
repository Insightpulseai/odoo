# IPAI Work OS Blocks

## 1. Overview
Notion-style block editor for pages

**Technical Name**: `ipai_workos_blocks`
**Category**: Productivity
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## 2. Functional Scope

        Block editor providing Notion-like content editing:
        - Block types: paragraph, heading, lists, todo, toggle, divider, quote, callout
        - Slash command menu for quick block insertion
        - Drag and drop block reordering
        - Block content stored as structured JSON
        - OWL-based editor surface
    

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
- `ipai.workos.block`

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
odoo-bin -d <db> -i ipai_workos_blocks --stop-after-init

# Upgrade
odoo-bin -d <db> -u ipai_workos_blocks --stop-after-init
```