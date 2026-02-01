# InsightPulse AI - CE Branding Patch v1.2.0

## Overview

This patch bundle contains:
- **ipai_ce_branding** module: Custom login branding with SCSS-based styling
- **xmlid collision fix**: Patch for ipai_ce_cleaner module

## Quick Install

### 1. Copy Branding Module

```bash
# Copy the branding module to your Odoo addons directory
cp -r addons/ipai_ce_branding /path/to/odoo-ce/addons/
```

### 2. Apply xmlid Fix Patch

```bash
# Navigate to your Odoo CE root directory
cd /path/to/odoo-ce

# Apply the patch
git apply patches/ipai_ce_cleaner_xmlid_fix.diff
```

### 3. Install/Update Modules

```bash
# Install the branding module and update ipai_ce_cleaner
odoo -d your_database -i ipai_ce_branding -u ipai_ce_cleaner --stop-after-init
```

## Image Replacement Options

### Option A: Keep Filename (Zero Code Changes)

Simply replace the placeholder SVG with your custom image:

```bash
# Replace the placeholder (keep the filename)
cp your-custom-image.svg addons/ipai_ce_branding/static/src/img/login_bg.svg

# Restart Odoo
docker compose restart odoo
```

**Supported formats**: SVG, PNG, JPG, WEBP

### Option B: Use Different Filename/Format

1. Add your custom image:

```bash
# Add your custom image
cp your-custom-image.webp addons/ipai_ce_branding/static/src/img/login_bg.webp
```

2. Update the SCSS variable:

Edit `addons/ipai_ce_branding/static/src/scss/login.scss` (line 15):

```scss
// Change this line:
$ipai-login-bg-url: "/ipai_ce_branding/static/src/img/login_bg.svg" !default;

// To:
$ipai-login-bg-url: "/ipai_ce_branding/static/src/img/login_bg.webp" !default;
```

3. Restart Odoo:

```bash
docker compose restart odoo
```

## What's Fixed

| Issue | Resolution |
|-------|------------|
| `id="assets_backend"` collision | Changed to `id="ipai_ce_cleaner_assets_backend"` |
| Inline `style=""` attribute | Replaced with SCSS-based styling using `$ipai-login-bg-url` variable |
| Non-unique template xmlids | All template ids prefixed with `ipai_ce_branding_*` |

## Troubleshooting

### Branding Not Appearing

1. Clear Odoo assets cache:
```bash
# Clear assets
rm -rf ~/.local/share/Odoo/filestore/your_database/assets/*

# Restart Odoo
docker compose restart odoo
```

2. Update module with assets reload:
```bash
odoo -d your_database -u ipai_ce_branding --stop-after-init
```

### Patch Fails to Apply

If the patch doesn't apply cleanly, manually edit `addons/ipai_ce_cleaner/views/ipai_ce_cleaner_assets.xml`:

Change line 3 from:
```xml
<template id="assets_backend" inherit_id="web.assets_backend">
```

To:
```xml
<template id="ipai_ce_cleaner_assets_backend" inherit_id="web.assets_backend">
```

## Version Compatibility

- **Odoo Version**: 18.0 CE
- **Python**: 3.11+
- **PostgreSQL**: 15+

## License

AGPL-3.0

## Support

For issues or questions, contact: support@insightpulseai.com
