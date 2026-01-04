# IPAI Work OS Search

## 1. Overview
Global and scoped search for pages and databases

**Technical Name**: `ipai_workos_search`
**Category**: Productivity
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## 2. Functional Scope

        Search module providing Notion-like search:
        - Global search across pages, databases, and blocks
        - Scoped search within spaces or databases
        - Full-text search on block content
        - Quick search results with previews
    

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
- `ipai.workos.search`
- `ipai.workos.search.history`

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
odoo-bin -d <db> -i ipai_workos_search --stop-after-init

# Upgrade
odoo-bin -d <db> -u ipai_workos_search --stop-after-init
```