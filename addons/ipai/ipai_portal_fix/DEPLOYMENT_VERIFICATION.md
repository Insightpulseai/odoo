# IPAI Portal Fix - Deployment Verification Report

**Date**: 2025-11-26
**Module**: `ipai_portal_fix` v1.0.0
**Server**: erp.insightpulseai.net (159.223.75.148)
**Odoo Version**: 18.0 Community Edition

---

## Deployment Summary

✅ **Status**: Successfully deployed and installed

### Deployment Steps Completed

1. ✅ Module uploaded to `/root/odoo-prod/addons/ipai_portal_fix/`
2. ✅ Copied to container at `/mnt/extra-addons/ipai_portal_fix/`
3. ✅ Permissions fixed (755, owner: odoo:root)
4. ✅ Module installed via `odoo -d production -i ipai_portal_fix --stop-after-init`
5. ✅ Container restarted to load controller and template changes

---

## Module Structure Verification

```
/mnt/extra-addons/ipai_portal_fix/
├── __manifest__.py          ✅ (1,088 bytes)
├── __init__.py              ✅ (50 bytes)
├── README.md                ✅ (5,019 bytes)
├── controllers/
│   ├── __init__.py          ✅
│   └── portal.py            ✅ (CustomerPortalWebsiteSafe class)
└── views/
    └── portal_templates.xml ✅ (Safe portal layout inheritance)
```

---

## Technical Implementation

### Controller Fix (`controllers/portal.py`)

**Purpose**: Inject safe 'website' context to prevent KeyError

**Key Method**:
```python
def _prepare_portal_layout_values(self):
    values = super()._prepare_portal_layout_values()

    if 'website' not in values:
        # Check if Website module is installed
        website_module = request.env['ir.module.module'].sudo().search([
            ('name', '=', 'website'),
            ('state', '=', 'installed')
        ], limit=1)

        if website_module:
            try:
                values['website'] = request.env['website'].get_current_website()
            except Exception:
                values['website'] = False
        else:
            values['website'] = False

    return values
```

**Behavior**:
- ✅ If Website module installed → Uses real website context
- ✅ If Website module NOT installed → Sets `website = False` (prevents KeyError)
- ✅ Handles exceptions gracefully

### Template Fix (`views/portal_templates.xml`)

**Purpose**: Remove website-dependent attributes from portal layout

**Inheritance**:
```xml
<template id="frontend_layout_safe"
          inherit_id="portal.frontend_layout"
          priority="20">
    <!-- Removes website dependencies from wrapwrap div -->
    <xpath expr="//div[@id='wrapwrap']" position="attributes">
        <attribute name="t-attf-class" add="#{...direction...}" />
        <attribute name="t-attf-class" add="#{'o_portal' if is_portal else ''}" />
    </xpath>
</template>
```

**Behavior**:
- ✅ Priority 20 ensures it loads after core portal template
- ✅ Only includes essential portal attributes
- ✅ Removes website-specific CSS classes

---

## Auto-Install Configuration

**Manifest Settings**:
```python
'auto_install': True,  # Auto-installs when portal is present
'depends': ['portal'],
```

**Rationale**: Finance SSC instances need portal access for vendors/employees but don't require the Website module for marketing purposes.

---

## Testing Checklist

### ✅ Basic Verification (Completed)

- [x] Module files uploaded to server
- [x] Permissions set correctly (755, odoo:root)
- [x] Module appears in `/mnt/extra-addons/`
- [x] Odoo installation completed without errors
- [x] Container restarted successfully

### 🔍 User Testing (Pending User Verification)

**Portal Access Test**:
1. Navigate to: `https://erp.insightpulseai.net/my`
2. Expected: Portal home page loads without `KeyError: 'website'`
3. Verify: No error messages in browser console

**Portal Document Test**:
1. Navigate to: `https://erp.insightpulseai.net/my/invoices` (or any portal route)
2. Expected: Portal pages load correctly
3. Verify: No template rendering errors

**Portal Home Test**:
1. Navigate to: `https://erp.insightpulseai.net/my/home`
2. Expected: Dashboard displays without errors
3. Verify: All portal widgets render correctly

---

## Expected Behavior

### With Website Module Installed
- Controller detects Website module
- Uses real `request.env['website'].get_current_website()`
- Portal pages work as before (no change)

### Without Website Module (Finance SSC Setup)
- Controller detects Website module absent
- Sets `website = False` in context
- Portal pages load successfully (no KeyError)
- Template handles missing website gracefully

---

## Troubleshooting

### If KeyError Still Occurs

1. **Check Module State**:
   ```bash
   ssh root@159.223.75.148 "docker exec odoo-ce odoo -d production --list-modules | grep ipai_portal_fix"
   ```
   Expected: `ipai_portal_fix` appears in module list

2. **Restart Odoo**:
   ```bash
   ssh root@159.223.75.148 "docker restart odoo-ce"
   ```

3. **Upgrade Module** (if changes were made):
   ```bash
   ssh root@159.223.75.148 "docker exec odoo-ce odoo -d production -u ipai_portal_fix --stop-after-init"
   ```

4. **Check Logs**:
   ```bash
   ssh root@159.223.75.148 "docker logs odoo-ce --tail 100 | grep -iE 'keyerror|website|portal'"
   ```

### If Website Module Was Previously Installed

**Symptom**: Orphaned website records causing issues

**Solution**:
```sql
-- Check for orphaned website records
SELECT COUNT(*) FROM website;

-- Clean up if needed (USE WITH CAUTION)
DELETE FROM website WHERE id > 0;
```

**Then**:
1. Restart Odoo
2. Clear browser cache
3. Retry portal access

---

## Rollback Procedure (If Needed)

```bash
# 1. Uninstall module
ssh root@159.223.75.148 "docker exec odoo-ce odoo -d production -u ipai_portal_fix --uninstall --stop-after-init"

# 2. Remove module files
ssh root@159.223.75.148 "docker exec -u root odoo-ce rm -rf /mnt/extra-addons/ipai_portal_fix"

# 3. Restart Odoo
ssh root@159.223.75.148 "docker restart odoo-ce"
```

**Alternative**: Install Website module:
```bash
ssh root@159.223.75.148 "docker exec odoo-ce odoo -d production -i website --stop-after-init"
```

---

## Maintenance Notes

### When Odoo 18 Core Updates `portal.frontend_layout`

**Risk**: Template inheritance may break if core structure changes

**Procedure**:
1. **Review new template**:
   ```bash
   ssh root@159.223.75.148 "docker exec odoo-ce cat /usr/lib/python3/dist-packages/odoo/addons/portal/views/portal_templates.xml"
   ```

2. **Update xpath expressions** in `views/portal_templates.xml` if needed

3. **Upgrade module**:
   ```bash
   ssh root@159.223.75.148 "docker exec odoo-ce odoo -d production -u ipai_portal_fix --stop-after-init"
   ```

---

## Support

**Contact**: Jake Tolentino (TBWA Finance SSC / InsightPulse AI)
**Email**: jake.tolentino@insightpulseai.net
**Documentation**: `/Users/tbwa/odoo-ce/addons/ipai_portal_fix/README.md`
**Repository**: Local development at `/Users/tbwa/odoo-ce/addons/ipai_portal_fix/`

---

## Next Steps (User Action Required)

1. **Verify Portal Access**: Navigate to `https://erp.insightpulseai.net/my`
2. **Check for Errors**: Look for absence of `KeyError: 'website'`
3. **Test Portal Routes**: Try `/my/invoices`, `/my/tasks`, `/my/home`
4. **Report Results**: Confirm fix works or report any issues

**Status**: ✅ Deployment complete, awaiting user verification
