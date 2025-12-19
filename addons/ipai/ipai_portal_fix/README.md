# IPAI Portal Fix - Website-Free Support

## Overview

This module fixes the `KeyError: 'website'` error that occurs when accessing portal pages in Odoo 18 CE without the Website module installed.

**Problem**: The `portal.frontend_layout` template assumes a `website` context variable exists, which causes crashes on finance-only Odoo instances.

**Solution**: This module provides both controller-level and template-level defensive fixes to ensure portal pages work correctly with or without the Website module.

## Features

- ✅ **Controller Fix**: Injects `website` context (set to `False` if Website not installed)
- ✅ **Template Fix**: Defensive portal layout that handles missing `website` gracefully
- ✅ **Auto-Install**: Automatically installs when `portal` module is present
- ✅ **Zero Impact**: No effect when Website module is installed (uses real website context)
- ✅ **OCA Compliant**: Follows Odoo 18 CE standards and best practices

## Technical Details

### Controller Patch (`controllers/portal.py`)

Inherits `CustomerPortal` and overrides:
- `_prepare_portal_layout_values()` - Ensures `website` key exists in context
- `_prepare_home_portal_values()` - Ensures `website` key exists for portal home

**Logic**:
1. Check if `website` key is missing from context
2. If Website module is installed → Get current website
3. If Website module is NOT installed → Set `website = False`
4. Return enhanced context with safe `website` value

### Template Patch (`views/portal_templates.xml`)

Inherits `portal.frontend_layout` with priority `20` to override any website-dependent attributes.

**Safe Patterns**:
- Only includes essential portal attributes
- Removes website-specific CSS classes
- Defensive meta tag generation (optional)

## Installation

### Automatic (Recommended)
Module auto-installs when `portal` module is present due to `'auto_install': True` in manifest.

### Manual
```bash
# Upload module
scp -r addons/ipai_portal_fix root@<server>:/root/odoo-prod/addons/

# Install
ssh root@<server> "docker exec odoo-ce odoo -d production -i ipai_portal_fix --stop-after-init"
```

## Verification

Check module status:
```bash
ssh root@<server> "docker exec odoo-ce psql \"\$POSTGRES_URL\" -c \"SELECT name, state FROM ir_module_module WHERE name = 'ipai_portal_fix';\""
```

Expected output:
```
      name       | state
-----------------+-----------
 ipai_portal_fix | installed
```

## Testing

1. **Portal Access Test**:
   - Navigate to: `https://erp.insightpulseai.net/my`
   - Should load without `KeyError: 'website'`

2. **Portal Home Test**:
   - Navigate to: `https://erp.insightpulseai.net/my/home`
   - Should display portal dashboard

3. **Portal Document Test**:
   - Navigate to any portal document (e.g., `/my/tasks`)
   - Should render without errors

## Use Cases

### Finance-Only Odoo Instances
Perfect for TBWA Finance SSC stack where:
- Portal is needed for vendor access, employee self-service
- Website module is NOT needed (no marketing website)
- Finance PPM dashboards are accessed via portal routes

### Hybrid Instances
Safe to use even when Website module IS installed:
- Controller checks for Website module
- If installed: Uses real website context
- If not installed: Uses safe `False` value

## Troubleshooting

### Error Still Occurs After Installation

1. **Check Module Status**:
```bash
ssh root@<server> "docker exec odoo-ce odoo -d production -u ipai_portal_fix --stop-after-init"
```

2. **Restart Odoo**:
```bash
ssh root@<server> "docker restart odoo-ce"
```

3. **Check Logs**:
```bash
ssh root@<server> "docker logs odoo-ce --tail 100 | grep -i 'keyerror\|website'"
```

### Website Module Interference

If Website module was previously installed and then uninstalled:
1. Check for orphaned website records:
```sql
SELECT COUNT(*) FROM website;
```

2. Clean up if needed:
```sql
DELETE FROM website WHERE id > 0;
```

3. Restart Odoo and clear browser cache

## Maintenance

### Updating the Fix

If Odoo 18 core updates `portal.frontend_layout` template:

1. Review new template structure:
```bash
ssh root@<server> "docker exec odoo-ce cat /usr/lib/python3/dist-packages/odoo/addons/portal/views/portal_templates.xml"
```

2. Update `views/portal_templates.xml` xpath expressions if needed

3. Upgrade module:
```bash
ssh root@<server> "docker exec odoo-ce odoo -d production -u ipai_portal_fix --stop-after-init"
```

## Dependencies

- **Required**: `portal` (Odoo core module)
- **Optional**: `website` (works with or without)

## License

AGPL-3

## Author

Jake Tolentino (TBWA Finance SSC / InsightPulse AI)

## Support

- **Email**: jake.tolentino@insightpulseai.net
- **Documentation**: `/Users/tbwa/odoo-ce/docs/`
- **Repository**: Local development at `/Users/tbwa/odoo-ce/addons/ipai_portal_fix/`

## Changelog

### Version 1.0.0 (2025-11-26)
- Initial release
- Controller-level fix for `_prepare_portal_layout_values()`
- Template-level defensive portal layout
- Auto-install capability
- Comprehensive documentation
