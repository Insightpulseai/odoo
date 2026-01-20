# Deploy Enterprise Bridge Fix - POS Self-Ordering Fields

**Date**: 2026-01-20
**Commit**: d11f923f
**Fix**: Add POS Enterprise field stubs to prevent Settings page crash

---

## Problem

**Error**: `"res.config.settings"."pos_self_ordering_mode" field is undefined`
**Location**: erp.insightpulseai.net (production Odoo instance)
**Cause**: Enterprise POS self-ordering fields don't exist in CE 18.0
**Impact**: Settings page crashes with OwlError

---

## Solution

Added 4 Enterprise field stubs to `ipai_enterprise_bridge`:
- `pos_self_ordering_mode` (Selection: nothing/mobile/kiosk)
- `pos_self_ordering_service_mode` (Selection: counter/table)
- `pos_self_ordering_pay_after` (Selection: each/meal)
- `pos_self_ordering_image_home_ids` (Many2many: ir.attachment)

All fields are non-functional stubs that prevent inheritance errors while maintaining CE compatibility.

---

## Deployment Steps

### 1. Push to Repository

```bash
cd ~/Documents/GitHub/odoo-ce
git push origin main
```

### 2. Deploy to Production Server

**SSH to server**:
```bash
ssh root@159.223.75.148
```

**Pull latest code**:
```bash
cd /opt/odoo-ce/repo
git pull origin main
```

**Expected output**:
```
Updating 28d81730..d11f923f
Fast-forward
 addons/ipai/ipai_enterprise_bridge/models/res_config_settings.py | 49 +++++++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 49 insertions(+)
```

### 3. Update Module in Odoo

**Upgrade ipai_enterprise_bridge module**:
```bash
docker exec odoo-erp-prod odoo \
  -d production \
  -u ipai_enterprise_bridge \
  --stop-after-init
```

**Expected output**:
```
INFO production odoo.modules.loading: loading 1 modules...
INFO production odoo.modules.loading: 1 modules loaded in 0.01s, 0 queries
INFO production odoo.modules.registry: module ipai_enterprise_bridge: creating or updating database tables
INFO production odoo.modules.loading: Modules loaded.
```

### 4. Restart Odoo

```bash
docker restart odoo-erp-prod
```

**Wait 10-15 seconds for restart**:
```bash
docker logs odoo-erp-prod --tail 20
```

**Expected**: No errors, server listening on port 8069

### 5. Verify Fix

**Test Settings page**:
```bash
curl -sf https://erp.insightpulseai.net/web/login
```

**Expected**: HTTP 200, no OwlError

**Test in browser**:
1. Navigate to https://erp.insightpulseai.net
2. Login as admin
3. Go to Settings → Point of Sale
4. Page should load without errors
5. Self-ordering fields should appear as "Disabled" (stub values)

---

## Verification Checklist

- [ ] Git push successful
- [ ] Code pulled on production server
- [ ] `ipai_enterprise_bridge` upgraded successfully
- [ ] Odoo restarted without errors
- [ ] Settings page loads without OwlError
- [ ] No JavaScript console errors
- [ ] POS self-ordering fields visible (disabled)

---

## Rollback (If Needed)

If deployment causes issues:

```bash
# On server
cd /opt/odoo-ce/repo
git checkout 28d81730  # Previous commit before fix

# Restart Odoo
docker restart odoo-erp-prod
```

---

## Architecture Context

This fix aligns with the canonical Odoo CE architecture:

**Config → OCA → Delta (ipai_*)**

- **Config**: Base Odoo CE 18.0 ✅
- **OCA**: Community modules for Enterprise features ✅
- **Delta**: `ipai_enterprise_bridge` provides CE → 19/EE parity ✅

The Enterprise Bridge is the **thin glue layer** that:
1. Stubs Enterprise-only fields
2. Provides OCA module integration
3. Maintains CE+OCA parity with Enterprise features

---

## Future Enhancements

If actual POS self-ordering functionality is needed:

**Option 1: OCA Module** (Recommended)
```bash
# Install OCA pos_order_mgmt or similar
# Check OCA/pos repository for CE alternatives
```

**Option 2: IPAI Scout Vertical**
```bash
# Enable Scout retail intelligence
# Settings → IPAI Bridge → Enable Scout (Retail)
```

**Option 3: Custom Implementation**
```bash
# Build custom POS self-ordering in ipai_scout module
# Use Enterprise Bridge stubs as foundation
```

---

## Related Documentation

- **Architecture**: `CLAUDE.md` (OCA-style workflow, Enterprise parity)
- **Enterprise Bridge Manifest**: `addons/ipai/ipai_enterprise_bridge/__manifest__.py`
- **Config Settings Model**: `addons/ipai/ipai_enterprise_bridge/models/res_config_settings.py`
- **OCA Guidelines**: `docs/OCA_CHORE_SCOPE.md`

---

**Status**: Ready for deployment
**Risk Level**: Low (non-functional field stubs only)
**Estimated Downtime**: <2 minutes (Odoo restart)
**Tested**: Local development, ready for production
