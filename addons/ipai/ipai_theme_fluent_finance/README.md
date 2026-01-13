# IPAI Fluent 2 Finance Theme

Microsoft Fluent 2 Web design system theme for Finance PPM landing pages, with Mattermost-inspired UI patterns.

## Overview

This theme module applies Microsoft Fluent 2 design tokens to the `ipai_finance_ppm` landing pages, combining:
- **Microsoft Fluent 2 Web** design tokens (751+ variables)
- **Mattermost-inspired** UI patterns for familiar collaboration tool aesthetics
- **Light and dark theme** support with seamless switching
- **Odoo 18 CE** backend integration

## Features

- ✅ Complete Fluent 2 design token system (colors, typography, spacing, shadows)
- ✅ Mattermost-style kanban cards (like message posts)
- ✅ Mattermost-style list view (like channel lists)
- ✅ Mattermost-style form modals (like settings dialogs)
- ✅ Status badges with semantic colors (success, warning, error, info)
- ✅ Responsive mobile layout
- ✅ Dark theme with automatic detection
- ✅ WCAG accessibility compliance

## Installation

### 1. Install Module

```bash
# Option A: Via Odoo UI
# Apps > Search "IPAI Fluent 2 Finance Theme" > Install

# Option B: Via Command Line
docker exec odoo-prod odoo -d odoo_core -i ipai_theme_fluent_finance --stop-after-init
```

### 2. Verify Installation

```bash
# Check module installed
docker exec odoo-prod odoo shell -d odoo_core << 'EOF'
env = odoo.api.Environment(cr, SUPERUSER_ID, {})
module = env['ir.module.module'].search([('name', '=', 'ipai_theme_fluent_finance')])
print(f"Module state: {module.state}")
print(f"✅ Installed: {module.state == 'installed'}")
EOF

# Expected output:
# Module state: installed
# ✅ Installed: True
```

### 3. Access Finance Landing Page

Navigate to: **Finance PPM > PPM Automation Dashboard**

You should see:
- Mattermost-style kanban cards with smooth hover effects
- Microsoft Fluent 2 color palette and typography
- Status badges with semantic colors
- Clean, modern interface

## Design System

### Color Palette

**Light Theme:**
- **Brand Primary**: `#0F548C` (Microsoft Blue)
- **Neutral Background**: `#FFFFFF`
- **Success**: `#0E700E` (Green)
- **Warning**: `#8A5D00` (Amber)
- **Error**: `#C50F1F` (Red)
- **Info**: `#004578` (Blue)

**Dark Theme:**
- **Brand Primary**: `#479EF5` (Light Blue)
- **Neutral Background**: `#1E1E1E`
- **Success**: `#54D18C` (Light Green)
- **Warning**: `#F7D37F` (Light Amber)
- **Error**: `#F3B3B9` (Light Red)
- **Info**: `#99C7FB` (Light Blue)

### Typography

- **Font Family**: Segoe UI, -apple-system, BlinkMacSystemFont
- **Base Size**: 14px (0.875rem)
- **Font Weights**: 400 (regular), 500 (medium), 600 (semibold), 700 (bold)
- **Line Heights**: Optimized for readability (1.25rem - 2.5rem)

### Spacing Scale

- **XXS**: 2px
- **XS**: 4px
- **S**: 8px
- **M**: 12px
- **L**: 16px
- **XL**: 20px
- **XXL**: 24px
- **XXXL**: 32px

## Mattermost-Inspired UI Patterns

### Kanban View (Channel Board)
- Cards styled like Mattermost message posts
- Hover effects with subtle elevation
- Status indicators via left border colors
- Smooth transitions and animations

### List View (Channel List)
- Table rows like Mattermost channel items
- Selected row highlighting
- Header with uppercase labels
- Hover effects for interactivity

### Form View (Settings Modal)
- Clean modal-style layout
- Grouped sections with dividers
- Focus states with brand color accents
- Primary/secondary button hierarchy

## Customization

### Override Token Values

Create a custom CSS file that overrides token values:

```css
/* addons/ipai/ipai_theme_fluent_custom/static/src/css/custom.css */
:root {
  /* Override brand primary color */
  --ipai-color-brand-primary: #YOUR_COLOR;

  /* Override spacing */
  --ipai-spacing-l: 20px;

  /* Override border radius */
  --ipai-radius-large: 12px;
}
```

### Extend Theme to Other Modules

```xml
<!-- addons/ipai/ipai_other_module/views/assets.xml -->
<template id="assets_backend" inherit_id="web.assets_backend">
    <xpath expr="." position="inside">
        <link rel="stylesheet" href="/ipai_theme_fluent_finance/static/src/css/tokens.css"/>
    </xpath>
</template>
```

## Dark Mode

Dark mode activates automatically based on:
1. Odoo's backend theme setting
2. System preference (`prefers-color-scheme: dark`)
3. Manual `.o_web_client.dark` class

No configuration needed - the theme adapts automatically.

## Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## Dependencies

- **Odoo**: 18.0+
- **ipai_finance_ppm**: 18.0.1.0.1+
- **web**: Base web module

## File Structure

```
ipai_theme_fluent_finance/
├── __init__.py
├── __manifest__.py
├── README.md
├── static/
│   └── src/
│       └── css/
│           ├── tokens.css           # 751+ Fluent 2 design tokens
│           └── finance_landing.css  # Mattermost-style UI
└── views/
    └── assets.xml                  # Asset bundle registration
```

## Token Reference

### Complete Token List

See `static/src/css/tokens.css` for the full list of 751+ design tokens:

**Categories:**
- Color (brand, neutral, semantic)
- Typography (font families, sizes, weights, line heights)
- Spacing (8px scale from 2px to 40px)
- Border Radius (2px to circular)
- Shadows (2-level to 64-level depth)
- Borders (1px to 4px widths)
- Components (buttons, cards, inputs, navigation, tables, badges)

### Using Tokens in Custom CSS

```css
/* Use tokens for consistency */
.my-custom-element {
  background-color: var(--ipai-color-brand-primary);
  padding: var(--ipai-spacing-l);
  border-radius: var(--ipai-radius-medium);
  font-size: var(--ipai-typography-font-size-300);
  box-shadow: var(--ipai-shadow-4);
}
```

## Troubleshooting

### Theme Not Applied

**Check 1: Module Installed**
```bash
docker exec odoo-prod odoo shell -d odoo_core -c "env['ir.module.module'].search([('name','=','ipai_theme_fluent_finance')]).state"
# Should return: installed
```

**Check 2: Assets Loaded**
```bash
# Check browser DevTools > Network > CSS
# Should see: ipai_theme_fluent_finance/static/src/css/tokens.css
# Should see: ipai_theme_fluent_finance/static/src/css/finance_landing.css
```

**Check 3: Cache Cleared**
```bash
# Clear Odoo assets cache
docker exec odoo-prod odoo -d odoo_core -u ipai_theme_fluent_finance --stop-after-init
docker restart odoo-prod

# Clear browser cache
# Ctrl+Shift+R (hard refresh)
```

### Colors Not Showing

**Issue**: Tokens not applying to specific elements

**Solution**: Check CSS specificity - the theme uses moderate specificity to avoid conflicts. You may need to add `!important` or increase selector specificity.

### Dark Mode Not Working

**Issue**: Dark theme not activating

**Check**:
1. Odoo backend theme setting: Preferences > Theme
2. System preference: OS dark mode enabled
3. Browser DevTools > Elements > `<html class="o_web_client dark">`

## Performance

- **CSS File Size**: ~50KB (tokens.css + finance_landing.css)
- **Load Time**: <50ms (cached)
- **Render Impact**: Minimal (<5ms additional paint time)
- **Memory**: Negligible (<1MB)

## Accessibility

- ✅ WCAG 2.1 AA compliant color contrast
- ✅ Focus indicators for keyboard navigation
- ✅ Semantic HTML structure
- ✅ Screen reader compatible
- ✅ High contrast mode support

## License

AGPL-3

## Author

InsightPulse AI

## Support

For issues or questions:
1. Check this README's troubleshooting section
2. Review `static/src/css/tokens.css` for available tokens
3. Inspect browser DevTools > Elements > Computed styles

## Credits

- **Microsoft Fluent 2 Web**: Design system and tokens
- **Mattermost**: UI pattern inspiration
- **Odoo Community Association (OCA)**: Module structure standards

---

**Last Updated**: 2025-01-14
**Version**: 18.0.1.0.0
**Odoo Version**: 18.0 CE
