# TBWA Backend Theme

## Overview

TBWA branding skin - Black + Yellow + IBM Plex

- **Technical Name:** `ipai_theme_tbwa_backend`
- **Version:** 18.0.1.1.0
- **Category:** Themes/Backend
- **License:** AGPL-3
- **Author:** InsightPulse AI / TBWA Finance
- **Application:** No
- **Installable:** Yes

## Business Use Case

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
- Contains back...

## Functional Scope

## Installation & Dependencies

### Dependencies

- `web` (CE Core)
- `ipai_platform_theme` (IPAI)

### Installation

```bash
# Install module
odoo-bin -d <database> -i ipai_theme_tbwa_backend --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_theme_tbwa_backend --stop-after-init
```

## Configuration

*No specific configuration required.*

## Security

*No specific security configuration.*

## Integrations

*No external integrations.*

## Upgrade Notes

- Current Version: 18.0.1.1.0
- No breaking changes documented

## Verification Steps

```bash
# 1. Verify module is installed
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai_theme_tbwa_backend'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai_theme_tbwa_backend")]).state)'
```

## Static Validation Status

- Passed: 4
- Warnings: 0
- Failed: 0
