# Production Hotfix Summary

**Date**: 2025-01-05
**Status**: ✅ Ready for Deployment
**Estimated Downtime**: 2-3 minutes

---

## Critical Fixes Applied

### 1. OwlError Fix (Database-Level)
**File**: `scripts/hotfix_production.sh`
**Action**: Removes `pay_invoices_online` field references from `ir.ui.view` table

### 2. OAuth HTTPS Loop Fix (Nginx Configuration)
**File**: `deploy/nginx/erp.insightpulseai.com.conf`
**Change**: Line 31

```diff
- proxy_set_header   X-Forwarded-Proto  $scheme;
+ proxy_set_header   X-Forwarded-Proto  https;
```

---

## Quick Deployment (SSH Required)

```bash
# 1. SSH into production server
ssh root@159.223.75.148

# 2. Navigate to repo and pull changes
cd /root/odoo-ce && git pull origin main

# 3. Update nginx config
docker cp deploy/nginx/erp.insightpulseai.com.conf nginx:/etc/nginx/conf.d/erp.insightpulseai.com.conf
docker exec nginx nginx -t && docker exec nginx nginx -s reload

# 4. Run database hotfix
chmod +x scripts/hotfix_production.sh
./scripts/hotfix_production.sh prod

# 5. Verify
curl -I https://erp.insightpulseai.com
docker logs odoo-erp-prod --tail 20
```

---

## What Gets Fixed

✅ **UI Crash**: Settings page loads without JavaScript errors
✅ **OAuth Loop**: Login redirects work correctly with HTTPS
✅ **Database State**: Clean removal of Enterprise-only field references
✅ **Asset Cache**: Regenerated to clear stale JavaScript

---

## User Impact

- **During Deployment**: 2-3 minute service interruption
- **After Deployment**: All active sessions logged out (users must re-login)
- **Browser Action Required**: Clear cache (Ctrl+Shift+R / Cmd+Shift+R)

---

## Success Verification

After deployment, verify these conditions:

```bash
# 1. Nginx config correct
docker exec nginx nginx -T | grep "X-Forwarded-Proto https"

# 2. Database parameter set
docker exec postgres psql -U odoo -d prod -c \
  "SELECT value FROM ir_config_parameter WHERE key='web.base.url';"
# Expected: https://erp.insightpulseai.com

# 3. No view errors
docker logs odoo-erp-prod --tail 50 | grep -i "pay_invoices_online"
# Expected: No output

# 4. OAuth works
curl -Ls https://erp.insightpulseai.com/auth_oauth/signin | grep -q "oauth"
# Expected: Exit code 0
```

---

## Rollback (If Needed)

```bash
# Restore nginx config
docker cp deploy/nginx/erp.insightpulseai.com.conf.backup \
  nginx:/etc/nginx/conf.d/erp.insightpulseai.com.conf
docker exec nginx nginx -s reload

# Restore database from backup
docker exec -i postgres psql -U odoo -d postgres < /backups/prod_latest.sql
docker restart odoo-erp-prod
```

---

## Files Changed

1. `deploy/nginx/erp.insightpulseai.com.conf` - OAuth HTTPS fix
2. `scripts/hotfix_production.sh` - Database cleanup script (new)
3. `docs/PRODUCTION_HOTFIX.md` - Complete deployment guide (new)

---

**Next Steps**: Review deployment guide in `docs/PRODUCTION_HOTFIX.md` before executing.
