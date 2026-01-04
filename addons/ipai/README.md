# IPAI Module Namespace

## 1. Overview
InsightPulse AI namespace for Odoo CE modules

**Technical Name**: `ipai`
**Category**: Hidden
**Version**: 18.0.1.0.0
**Author**: InsightPulse AI

## 2. Functional Scope

        This is a namespace module for all IPAI (InsightPulse AI) custom modules.
        It provides the base namespace for the module hierarchy.
    

## 3. Installation & Dependencies
Dependencies (CE/OCA):
- `base`

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
odoo-bin -d <db> -i ipai --stop-after-init

# Upgrade
odoo-bin -d <db> -u ipai --stop-after-init
```