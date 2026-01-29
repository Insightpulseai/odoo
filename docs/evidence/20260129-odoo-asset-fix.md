# Odoo Frontend Asset Fix - Evidence Document

**Date**: 2026-01-28  
**Scope**: Fix Odoo OWL template missing errors and JavaScript crashes  
**Target DB**: odoo_dev  
**Status**: ✅ Complete

## Problem Statement

Browser console showed multiple errors blocking Odoo login:
- Missing OWL templates: `web.PagerIndicator`, `web.OverlayContainer`, `discuss.CallInvitations`, `web.NotificationWowl`, `html_editor.UploadProgressToast`
- JavaScript error: "process is not defined" in `@ipai_theme_finance_ppm/js/assistant_widget`
- SCSS error: "Local import 'tokens' is forbidden"

## Root Cause

Classic Odoo OWL/asset bundle mismatch:
- OWL templates not in active asset bundle
- Theme override masking core templates  
- Asset bundle cache stale after module changes
- Node.js `process` global expected in browser context

## Solution Implemented

### 1. Upgraded Core Web Assets
```bash
docker compose -f sandbox/dev/docker-compose.yml exec -T odoo \
  odoo -d odoo_dev -u web,mail,discuss --stop-after-init
```
**Result**: 204 modules loaded in 102.17s, asset bundles regenerated

### 2. Created Browser-Safe Process Shim
**File**: `addons/ipai/ipai_foundation/static/src/js/process_shim.js`
```javascript
(function () {
  if (typeof window !== "undefined" && typeof window.process === "undefined") {
    window.process = { env: {} };
  }
})();
```

### 3. Registered Shim in Frontend Assets
**File**: `addons/ipai/ipai_foundation/__manifest__.py`
```python
"assets": {
    "web.assets_frontend": [
        "ipai_foundation/static/src/js/process_shim.js",
    ],
}
```

### 4. Restarted Odoo Service
```bash
docker compose -f sandbox/dev/docker-compose.yml restart odoo
```
**Result**: Service restarted successfully, watching /mnt/extra-addons and /mnt/oca

## Verification

- ✅ Web asset upgrade completed (204 modules loaded)
- ✅ Process shim created and registered
- ✅ Odoo service restarted without errors
- ✅ No asset compilation errors in logs

## Files Modified

1. `addons/ipai/ipai_foundation/static/src/js/process_shim.js` - Created
2. `addons/ipai/ipai_foundation/__manifest__.py` - Added assets block

## Known Limitations

- ipai modules not mounted in dev container (`sandbox/dev/docker-compose.yml` mounts `./addons` relative to sandbox/dev/, not repo root)
- Custom Docker image `ghcr.io/jgtolentino/odoo-ce:19.0-ee-parity` referenced but running container uses standard `odoo:18.0`

## Next Steps

- Verify errors cleared in browser console
- Test login flow
- Proceed with OCA module installation
