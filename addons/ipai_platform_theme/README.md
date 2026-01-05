# IPAI Platform Theme

## Overview

Single source of truth for IPAI design tokens and branding

- **Technical Name:** `ipai_platform_theme`
- **Version:** 18.0.1.1.0
- **Category:** Theme
- **License:** LGPL-3
- **Author:** InsightPulse AI
- **Application:** No
- **Installable:** Yes

## Business Use Case

IPAI Platform Theme - Design System Foundation
===============================================

This module provides the core design system tokens for all IPAI modules.
It is the **single source of truth** for colors, typography, spacing,
shadows, and component styling.

Key Principles:
- All brand colors are defined as CSS custom properties (variables)
- Skin modules (like ipai_theme_tbwa_backend) override values, not definitions
- No hex codes should be used directly in other IPAI modules

Tok...

## Functional Scope

## Installation & Dependencies

### Dependencies

- `web` (CE Core)

### Installation

```bash
# Install module
odoo-bin -d <database> -i ipai_platform_theme --stop-after-init

# Upgrade module
odoo-bin -d <database> -u ipai_platform_theme --stop-after-init
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
psql -d <database> -c "SELECT name, state FROM ir_module_module WHERE name = 'ipai_platform_theme'"

# 2. Check module info
odoo-bin shell -d <database> -c 'print(env["ir.module.module"].search([("name", "=", "ipai_platform_theme")]).state)'
```

## Static Validation Status

- Passed: 4
- Warnings: 0
- Failed: 0
