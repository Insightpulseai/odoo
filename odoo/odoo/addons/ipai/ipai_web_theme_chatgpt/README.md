# ipai_web_theme_chatgpt

Backend theme module for Odoo 18 CE with ChatGPT-inspired design language.

## Overview

This module applies a modern, SaaS-style design to the Odoo 18 backend web client. It uses Odoo 18's native manifest-based asset bundling for reliable loading across upgrades.

**Version:** 18.0.1.0.0
**License:** LGPL-3
**Depends:** `web`

## Features

### UI Surfaces Styled

| Component | Changes |
|-----------|---------|
| **Navbar** | Purple primary background (#6d28d9), white text |
| **Buttons** | 8px border radius, colored shadows on hover |
| **Inputs** | Focus ring with purple glow, rounded corners |
| **Cards** | 12px radius, subtle shadow, border |
| **Kanban** | Hover lift effect, consistent card styling |
| **Tags/Pills** | Full radius (pill shape), semantic colors |
| **Tables** | Uppercase headers, row hover states |
| **Modals** | 16px radius, larger shadow |
| **Dropdowns** | Rounded corners, item hover states |
| **Calendar** | Styled toolbar buttons and events |
| **Pivot/Graph** | Clean header styling |

### Design System

- **Primary color:** `#6d28d9` (purple)
- **Border radius:** 8px (sm), 12px (md), 16px (lg)
- **Shadows:** Subtle depth hierarchy
- **Typography:** System font stack with Inter fallback

## File Structure

```
ipai_web_theme_chatgpt/
├── __init__.py
├── __manifest__.py          # Odoo 18 native asset bundling
├── README.md
└── static/src/scss/
    ├── tokens.scss          # Design tokens + Odoo/Bootstrap mappings
    └── backend_overrides.scss  # Component styling (scoped to .o_web_client)
```

## Installation

### Install module

```bash
# From Odoo root directory
./odoo-bin -d <DB_NAME> -i ipai_web_theme_chatgpt --stop-after-init
```

### Update after changes

```bash
./odoo-bin -d <DB_NAME> -u ipai_web_theme_chatgpt --stop-after-init
```

## Verification

### 1. Force asset rebuild

Load any backend page with debug mode:

```
https://your-odoo.com/web?debug=assets
```

### 2. Check assets loaded

In browser DevTools → Network tab, search for `web.assets_backend`. The compiled bundle should include the theme styles.

### 3. Visual verification

- Navbar should be purple (#6d28d9)
- Buttons should have rounded corners
- Kanban cards should have subtle shadows
- Focus states should show purple glow

### 4. Hard cache bust

```
Cmd+Shift+R (Mac) / Ctrl+Shift+R (Windows/Linux)
```

## Customization

### Change brand colors

Edit `static/src/scss/tokens.scss`:

```scss
// Primary (Purple - main brand accent)
$ipai-primary: #6d28d9;        // Change this
$ipai-primary-800: #5b21b6;    // Darker shade for hover
$ipai-primary-900: #4c1d95;    // Darkest for active
```

### Change border radius

```scss
$ipai-radius-sm: 8px;   // Buttons, inputs
$ipai-radius-md: 12px;  // Cards, panels
$ipai-radius-lg: 16px;  // Modals
```

### Odoo/Bootstrap variable mappings

The theme maps IPAI tokens to Odoo/Bootstrap variables at the bottom of `tokens.scss`. This ensures system-wide inheritance:

```scss
$o-brand-primary: $ipai-primary !default;
$primary: $ipai-primary !default;
$border-radius: $ipai-radius-sm !default;
```

## Architecture

### Asset injection method

Uses Odoo 18 native `__manifest__.py["assets"]` bundling (preferred over template inheritance):

```python
"assets": {
    "web.assets_backend": [
        "ipai_web_theme_chatgpt/static/src/scss/tokens.scss",
        "ipai_web_theme_chatgpt/static/src/scss/backend_overrides.scss",
    ],
},
```

### Scoping strategy

- Bootstrap overrides (`.btn`, `.form-control`, `.dropdown-menu`, etc.) are scoped under `.o_web_client` to avoid affecting login/public pages
- Odoo-specific selectors (`.o_*`) are inherently scoped to the backend

## Troubleshooting

### Styles not appearing

1. Clear browser cache: `Cmd+Shift+R`
2. Restart Odoo with asset dev mode: `./odoo-bin -d <DB> --dev=assets`
3. Verify module is installed: Settings → Apps → search "IPAI Web Theme"

### Broken asset bundle (white screen)

1. Check Odoo logs for SCSS compilation errors
2. Validate SCSS syntax in both files
3. Remove module and reinstall: `-u ipai_web_theme_chatgpt`

### Styles conflict with other theme

This module should be the only backend theme installed. Disable other themes like `ipai_platform_theme` if conflicts occur.

## Limitations

- Only affects backend (web client), not website pages
- No dark mode support (tokens prepared but not implemented)
- Login page intentionally unstyled (scoped under `.o_web_client`)

## Related Modules

- `ipai_platform_theme` - Alternative TBWA-branded theme (disable if using this module)
- For website theming, create a separate `ipai_website_theme_chatgpt` module using `web.assets_frontend`
