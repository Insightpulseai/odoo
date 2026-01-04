# Production Hotfix Guide: OwlError & OAuth Loop

**Date**: 2025-01-05
**Status**: ✅ Ready for Deployment
**Severity**: Critical (Production Down)

---

## Issues Fixed

### 1. OwlError: `pay_invoices_online` Field Crash

**Symptom**:
```
OwlError: Field 'pay_invoices_online' does not exist
JavaScript crash in settings view
```

**Root Cause**:
- Field `pay_invoices_online` exists in Odoo Enterprise but NOT in Community Edition
- Database view references non-existent field from previous migration
- Odoo 18 CE has stricter validation causing UI crash

**Fix Applied**:
- Database-level removal of field references from `ir.ui.view` table
- Python script removes all variations: `<field name="pay_invoices_online"/>`, `<field name="pay_invoices_online" />`, etc.

---

### 2. OAuth HTTPS Redirect Loop

**Symptom**:
```
OAuth redirects infinitely between HTTP/HTTPS
Login fails with "redirect_uri_mismatch"
```

**Root Cause**:
- Nginx uses `proxy_set_header X-Forwarded-Proto $scheme`
- `$scheme` evaluates to client protocol (could be HTTP in some proxy scenarios)
- Odoo generates OAuth URLs with HTTP instead of HTTPS
- OAuth provider rejects HTTP redirect URIs

**Fix Applied**:
- **File**: `deploy/nginx/erp.insightpulseai.net.conf`
- **Change**: `X-Forwarded-Proto $scheme` → `X-Forwarded-Proto https`
- **Database**: Force `web.base.url = https://erp.insightpulseai.net` and freeze parameter

---

## Deployment Steps

### Prerequisites
```bash
# SSH into production server
ssh root@159.223.75.148

# Navigate to odoo-ce directory
cd /root/odoo-ce

# Pull latest changes
git pull origin main
```

### Step 1: Apply Nginx Configuration Fix

```bash
# Backup current nginx config
cp deploy/nginx/erp.insightpulseai.net.conf deploy/nginx/erp.insightpulseai.net.conf.backup

# Copy updated config to nginx container
docker cp deploy/nginx/erp.insightpulseai.net.conf nginx:/etc/nginx/conf.d/erp.insightpulseai.net.conf

# Test nginx configuration
docker exec nginx nginx -t

# Reload nginx (zero-downtime)
docker exec nginx nginx -s reload
```

**Expected Output**:
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### Step 2: Run Database Hotfix Script

```bash
# Make script executable (if not already)
chmod +x scripts/hotfix_production.sh

# Run hotfix script
./scripts/hotfix_production.sh prod
```

**Expected Output**:
```
==================================================
INSIGHTPULSE ODOO PRODUCTION HOTFIX
==================================================
Container: odoo-erp-prod
Database:  prod

>>> [1/4] Fixing OwlError (pay_invoices_online field)...
Found 1 view(s) to patch:
  - Settings View (ID: 1234, XML ID: base.res_config_settings_view_form)
  ✓ Patched: Settings View
✓ Database views patched successfully

>>> [2/4] Fixing OAuth HTTPS loop...
            key            |              value
---------------------------+----------------------------------
 web.base.url              | https://erp.insightpulseai.net
 web.base.url.freeze       | True
✓ HTTPS system parameters enforced

>>> [3/4] Regenerating assets (clearing JS cache)...
✓ Assets regenerated

>>> [4/4] Restarting Odoo service...
Waiting for Odoo to restart ✓

==================================================
✅ HOTFIX COMPLETED SUCCESSFULLY
==================================================
```

### Step 3: Verify Deployment

```bash
# 1. Check Odoo is running
docker ps | grep odoo

# 2. Test HTTPS endpoint
curl -I https://erp.insightpulseai.net

# Expected: HTTP/2 200 (or 303 for login redirect)

# 3. Check Odoo logs for errors
docker logs odoo-erp-prod --tail 50

# 4. Verify X-Forwarded-Proto header
docker exec nginx nginx -T | grep X-Forwarded-Proto
# Expected: proxy_set_header X-Forwarded-Proto https;
```

### Step 4: User Verification

**Clear Browser Cache**:
- Chrome/Edge: `Ctrl + Shift + R` (Windows) / `Cmd + Shift + R` (Mac)
- Firefox: `Ctrl + F5` (Windows) / `Cmd + Shift + R` (Mac)
- Safari: `Cmd + Option + R`

**Test OAuth Login**:
1. Navigate to `https://erp.insightpulseai.net`
2. Click "Login with Google" (or other OAuth provider)
3. Verify redirect works without loops
4. Confirm successful login

**Test Settings Page**:
1. Navigate to Settings → General Settings
2. Verify no JavaScript errors in browser console (F12)
3. Confirm page loads without crashes

---

## Rollback Procedure

If issues occur, rollback using these commands:

```bash
# Rollback nginx config
docker cp deploy/nginx/erp.insightpulseai.net.conf.backup nginx:/etc/nginx/conf.d/erp.insightpulseai.net.conf
docker exec nginx nginx -s reload

# Restore database from backup (if available)
docker exec -i postgres psql -U odoo -d postgres -c "DROP DATABASE prod;"
docker exec -i postgres psql -U odoo -d postgres < /backups/prod_$(date +%Y%m%d).sql

# Restart Odoo
docker restart odoo-erp-prod
```

---

## Post-Deployment Monitoring

### Critical Metrics (First 30 Minutes)

```bash
# Monitor Odoo logs for errors
docker logs -f odoo-erp-prod | grep -i error

# Monitor nginx access logs
docker logs -f nginx | grep erp.insightpulseai.net

# Check OAuth success rate
docker exec postgres psql -U odoo -d prod -c "
  SELECT COUNT(*) FROM res_users_log
  WHERE create_date > NOW() - INTERVAL '30 minutes'
  AND login_type = 'oauth';
"
```

### Health Checks (Every 5 Minutes)

```bash
# Endpoint health
curl -sf https://erp.insightpulseai.net/web/health || echo "FAILED"

# Database connectivity
docker exec odoo-erp-prod odoo shell -d prod -c "
  env['res.users'].search_count([])
" || echo "DB ERROR"
```

---

## Known Issues & Limitations

### Issue: Asset Regeneration Slow
- **Impact**: First page load after hotfix may take 10-15 seconds
- **Mitigation**: Pre-warm cache by visiting common pages
- **Duration**: One-time, subsequent loads normal

### Issue: Session Invalidation
- **Impact**: All active users will be logged out after restart
- **Mitigation**: Schedule during low-traffic window (e.g., 2 AM SGT)
- **Notification**: Send advance notice to active users

---

## Success Criteria

Deployment considered successful when:

- ✅ No JavaScript errors in browser console
- ✅ Settings page loads without OwlError
- ✅ OAuth login completes without redirect loops
- ✅ `web.base.url` shows HTTPS in database
- ✅ nginx X-Forwarded-Proto header set to `https`
- ✅ Zero error logs in Odoo container (first 30 min)
- ✅ User login success rate >95%

---

## Related Documentation

- **OAuth Configuration**: `docs/OAUTH_SETUP.md`
- **Nginx Proxy Setup**: `docs/NGINX_PROXY.md`
- **Odoo 18 CE Migration**: `docs/MIGRATION_18.md`
- **Production Deployment**: `docs/PRODUCTION_DEPLOY.md`

---

## Emergency Contacts

- **DevOps Engineer**: jgtolentino (Mattermost)
- **System Admin**: admin@insightpulseai.net
- **Escalation**: Finance Director (for business impact)

---

**Last Updated**: 2025-01-05
**Next Review**: After successful deployment
**Approval Required**: ✅ Finance Director (for production changes)
