# IPAI Platform Theme

## 1. Overview
Single source of truth for IPAI design tokens and branding

**Technical Name**: `ipai_platform_theme`
**Category**: Theme
**Version**: 18.0.1.1.0
**Author**: InsightPulse AI

## 2. Functional Scope

IPAI Platform Theme - Design System Foundation
===============================================

This module provides the core design system tokens for all IPAI modules.
It is the **single source of truth** for colors, typography, spacing,
shadows, and component styling.

Key Principles:
- All brand colors are defined as CSS custom properties (variables)
- Skin modules (like ipai_theme_tbwa_backend) override values, not definitions
- No hex codes should be used directly in other IPAI modules

Token Categories:
- Brand colors (primary, ink, surface, border)
- Semantic colors (success, warning, error, info)
- Typography (font family, sizes, weights)
- Spacing scale
- Border radii and shadows
- Transitions and z-index layers

Usage in Other Modules:
- Add 'ipai_platform_theme' to depends
- Use var(--ipai-brand-primary) instead of hex colors
- Use var(--ipai-radius) instead of hardcoded border-radius

Odoo Integration:
- Maps IPAI tokens to --o-brand-primary and other Odoo variables
- Normalizes common Odoo components for consistent styling
    

## 3. Installation & Dependencies
Dependencies (CE/OCA):
- `web`

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
odoo-bin -d <db> -i ipai_platform_theme --stop-after-init

# Upgrade
odoo-bin -d <db> -u ipai_platform_theme --stop-after-init
```