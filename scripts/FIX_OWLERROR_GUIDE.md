# Fix OwlError: pay_invoices_online Field Undefined

## Error Summary

**Error**: `res.config.settings.pay_invoices_online field is undefined`
**Location**: erp.insightpulseai.com
**Impact**: OWL lifecycle crash when accessing certain views
**Root Cause**: View references a field that doesn't exist (CE vs Enterprise mismatch)

## Quick Fix (Recommended)

### Option 1: Remove Orphaned Field References (Safest)

```bash
# 1. Set environment variables
export ODOO_URL="https://erp.insightpulseai.com"
export ODOO_DB="production"
export ODOO_USERNAME="admin"  # or your admin user
export ODOO_PASSWORD="your_password"

# 2. Run fix script in dry-run mode (preview changes)
python scripts/fix-pay-invoices-online-error.py --dry-run --remove-field

# 3. If dry-run looks good, apply changes
python scripts/fix-pay-invoices-online-error.py --remove-field

# 4. Restart Odoo to clear cache
ssh root@159.223.75.148
docker compose -f /opt/odoo/docker-compose.yml restart odoo-ce

# 5. Clear browser cache and test
# Visit: https://erp.insightpulseai.com
```

### Option 2: Direct SQL Cleanup (If script fails)

```bash
# SSH to production server
ssh root@159.223.75.148

# Connect to PostgreSQL
docker exec -it odoo-postgres psql -U odoo -d production

# Find affected views
SELECT id, name, model
FROM ir_ui_view
WHERE arch_db LIKE '%pay_invoices_online%';

# Remove field references (replace VIEW_ID with actual ID from above)
UPDATE ir_ui_view
SET arch_db = regexp_replace(
    arch_db,
    '<field[^>]*name="pay_invoices_online"[^>]*/>',
    '',
    'g'
)
WHERE arch_db LIKE '%pay_invoices_online%';

# Exit psql
\q

# Restart Odoo
docker compose -f /opt/odoo/docker-compose.yml restart odoo-ce
```

### Option 3: Module Update (If field should exist)

```bash
# If the field is from a module that needs updating
ssh root@159.223.75.148
docker exec -it odoo-ce odoo-bin \
  -d production \
  -u account,account_payment \
  --stop-after-init

# Restart
docker compose -f /opt/odoo/docker-compose.yml restart odoo-ce
```

## Verification Steps

After applying fix:

1. **Clear browser cache** (Cmd+Shift+R on Mac, Ctrl+Shift+R on Windows)

2. **Visit Settings page**:
   - Navigate to: https://erp.insightpulseai.com/web#action=base.action_res_config_settings
   - Should load without OWL errors

3. **Check browser console**:
   - Open DevTools (F12)
   - Look for any remaining errors
   - Should be clean

4. **Test affected workflows**:
   - Access Accounting → Configuration → Settings
   - Verify all tabs load correctly
   - No OwlError in console

## Root Cause Analysis

### Why This Happened

**Field Origin**: `pay_invoices_online` is from Odoo **Enterprise** module `account_payment`

**Your Setup**: Odoo CE 18.0 (Community Edition)

**Mismatch**:
- A view inherited from Enterprise was copied or imported
- View XML references Enterprise-only field
- Odoo CE doesn't have the field definition
- OWL renderer throws error when parsing view

### Common Triggers

1. Importing database from Enterprise to CE
2. Installing third-party module with Enterprise dependencies
3. Copy-pasting view XML from Enterprise documentation
4. Module upgrade left orphaned view references

## Prevention

### Add to Module Manifest

In any custom modules, ensure proper dependency checks:

```python
# addons/your_module/__manifest__.py
{
    'name': 'Your Module',
    'depends': ['account'],  # Don't depend on 'account_payment' if CE
    'external_dependencies': {
        'python': [],
    },
    # ...
}
```

### View Inheritance Best Practice

When inheriting Enterprise views in CE-compatible modules:

```xml
<!-- views/res_config_settings_views.xml -->
<odoo>
  <record id="res_config_settings_view_form" model="ir.ui.view">
    <field name="name">res.config.settings.view.form.inherit</field>
    <field name="model">res.config.settings</field>
    <field name="inherit_id" ref="account.res_config_settings_view_form"/>
    <field name="arch" type="xml">
      <xpath expr="//field[@name='pay_invoices_online']" position="attributes">
        <!-- Only if you're sure this field exists -->
        <attribute name="invisible">1</attribute>
      </xpath>
    </field>
  </record>
</odoo>
```

Better approach - check field exists first:

```python
# models/res_config_settings.py
from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Only add if not already defined (CE vs EE compatibility)
    if not hasattr(models.Model, 'pay_invoices_online'):
        pay_invoices_online = fields.Boolean(
            string="Online Invoice Payment",
            help="Allow customers to pay invoices online"
        )
```

## Monitoring

### Add to CI/CD Pipeline

```yaml
# .github/workflows/odoo-tests.yml
- name: Check for orphaned field references
  run: |
    # Scan for Enterprise-only fields in CE modules
    ENTERPRISE_FIELDS=(
      "pay_invoices_online"
      "l10n_latam_document_type_id"
      "social_*"
    )

    for field in "${ENTERPRISE_FIELDS[@]}"; do
      if grep -r "$field" addons/ipai_*/views/*.xml; then
        echo "❌ Enterprise field '$field' found in CE module"
        exit 1
      fi
    done
```

### Runtime Error Detection

Add to your monitoring setup:

```python
# Custom error handler in main Odoo config
def custom_error_handler(exc_type, exc_value, exc_traceback):
    """Log undefined field errors to Mattermost"""
    if 'field is undefined' in str(exc_value):
        # Extract field name
        field_match = re.search(r'"([^"]+)" field is undefined', str(exc_value))
        if field_match:
            field_name = field_match.group(1)
            # Notify via Mattermost
            notify_mattermost(
                f"⚠️ Undefined field detected: {field_name}\n"
                f"Check for CE/EE compatibility issues"
            )
```

## Support

If the automated fix doesn't work:

1. **Collect diagnostics**:
   ```bash
   python scripts/fix-pay-invoices-online-error.py --dry-run --remove-field > /tmp/diagnostics.txt
   ```

2. **Check Odoo logs**:
   ```bash
   ssh root@159.223.75.148
   docker logs odoo-ce --tail 100 | grep -i "pay_invoices_online"
   ```

3. **Create GitHub issue** with:
   - Diagnostics output
   - Odoo logs
   - Full error stack trace from browser console

## Related Issues

- **Similar errors**: `field is undefined` for other fields → Use same fix pattern
- **View inheritance**: Always check CE vs EE compatibility
- **Module upgrades**: Test in staging before production

---

**Script**: `scripts/fix-pay-invoices-online-error.py`
**Last Updated**: 2025-12-28
**Author**: Jake Tolentino (@jgtolentino)
