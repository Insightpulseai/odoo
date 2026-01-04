# TBWA Backend Theme

## 1. Overview
TBWA branding skin - Black + Yellow + IBM Plex

**Technical Name**: `ipai_theme_tbwa_backend`
**Category**: Themes/Backend
**Version**: 18.0.1.1.0
**Author**: InsightPulse AI / TBWA Finance

## 2. Functional Scope

TBWA Backend Theme - Brand Skin
===============================

Applies TBWA corporate identity to Odoo backend.

This is a **skin module** that overrides ipai_platform_theme token values:
- TBWA Yellow (#FFD800) as primary accent
- Black navbar/sidebar
- IBM Plex Sans typography

Architecture:
- Depends on ipai_platform_theme (token source of truth)
- Sets TBWA-specific color values via CSS custom property overrides
- Contains SCSS variables for Odoo's Bootstrap/variable system
- Contains backend.scss for component-level overrides

DO NOT define new tokens here - only override existing ones.
    

## 3. Installation & Dependencies
Dependencies (CE/OCA):
- `web`
- `ipai_platform_theme`

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
odoo-bin -d <db> -i ipai_theme_tbwa_backend --stop-after-init

# Upgrade
odoo-bin -d <db> -u ipai_theme_tbwa_backend --stop-after-init
```