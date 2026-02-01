# Production Hotfix - Quick Deployment Checklist

**Date**: 2025-01-05
**Issues**: OwlError + OAuth HTTPS Loop
**Server**: 159.223.75.148 (odoo-erp-prod)

---

## ⚡ Quick Deploy (5 Minutes)

### 1. SSH & Prepare (1 min)
```bash
ssh root@159.223.75.148
cd /root/odoo-ce
git pull origin main
```

### 2. Update Nginx (1 min)
```bash
# Backup current config
cp deploy/nginx/erp.insightpulseai.com.conf deploy/nginx/erp.insightpulseai.com.conf.backup

# Apply updated config
docker cp deploy/nginx/erp.insightpulseai.com.conf nginx:/etc/nginx/conf.d/erp.insightpulseai.com.conf

# Test and reload
docker exec nginx nginx -t && docker exec nginx nginx -s reload
```

**Expected**: `nginx: configuration file ... test is successful`

### 3. Run Hotfix Script (2 min)
```bash
chmod +x scripts/hotfix_production.sh
./scripts/hotfix_production.sh prod
```

**Expected**: `✅ ALL VALIDATIONS PASSED`

### 4. Verify Deployment (1 min)
```bash
./scripts/validate_production.sh prod
```

**Expected**: `Total Tests: 7 | Passed: 7 | Failed: 0`

---

## ✅ Quick Validation Checklist

After deployment, verify these in order:

- [ ] **Nginx header**: `docker exec nginx nginx -T | grep "X-Forwarded-Proto https"`
- [ ] **Database clean**: `docker exec odoo-erp-prod psql -U odoo -d prod -c "SELECT COUNT(*) FROM ir_ui_view WHERE arch_db ILIKE '%pay_invoices_online%';"` → Returns `0`
- [ ] **HTTPS base URL**: `docker exec odoo-erp-prod psql -U odoo -d prod -c "SELECT value FROM ir_config_parameter WHERE key='web.base.url';"` → Returns `https://erp.insightpulseai.com`
- [ ] **Odoo running**: `docker ps | grep odoo` → Shows running container
- [ ] **Login page loads**: `curl -I https://erp.insightpulseai.com` → Returns `200 OK`
- [ ] **No recent errors**: `docker logs odoo-erp-prod --tail 20` → No `OwlError` or `pay_invoices_online`

---

## 🧪 User Acceptance Testing

Share this with end users:

### Quick Test Steps:
1. **Clear browser cache**: Press `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
2. **Open incognito**: Chrome → New Incognito Window
3. **Visit**: `https://erp.insightpulseai.com`
4. **Verify login page loads** (no white screen)
5. **Press F12** → Console tab → **No red errors**
6. **Click "Sign in with Gmail"**
7. **Complete Google login**
8. **Verify URL stays `https://`** (no redirect to `http://`)
9. **Navigate to Settings** → General Settings
10. **Verify page loads** without crashes

**Expected Result**: All steps complete successfully with no errors.

---

## 🔄 Rollback (If Needed)

If validation fails:

```bash
# Restore nginx
docker cp deploy/nginx/erp.insightpulseai.com.conf.backup nginx:/etc/nginx/conf.d/erp.insightpulseai.com.conf
docker exec nginx nginx -s reload

# Restore database (if backup exists)
docker exec -i postgres psql -U odoo -d postgres -c "DROP DATABASE prod;"
docker exec -i postgres psql -U odoo -d postgres < /backups/prod_$(date +%Y%m%d).sql

# Restart Odoo
docker restart odoo-erp-prod
```

---

## 📊 Success Metrics (First 30 Min)

Monitor these metrics post-deployment:

```bash
# Login success rate (should be >95%)
docker exec postgres psql -U odoo -d prod -c "
  SELECT COUNT(*) AS successful_logins
  FROM res_users_log
  WHERE create_date > NOW() - INTERVAL '30 minutes';
"

# Error count (should be 0)
docker logs odoo-erp-prod --tail 100 | grep -c "ERROR"

# OAuth redirects (should show https://)
docker logs nginx --tail 50 | grep "auth_oauth" | grep "Location"
```

---

## 📞 Emergency Contacts

- **DevOps**: jgtolentino (Mattermost)
- **Admin**: admin@insightpulseai.com
- **Escalation**: Finance Director

---

## 📚 Detailed Documentation

For complete details, see:

- **Hotfix Script**: `scripts/hotfix_production.sh`
- **Validation Script**: `scripts/validate_production.sh`
- **Success Criteria**: `docs/SUCCESS_CRITERIA.md`
- **Full Deployment Guide**: `docs/PRODUCTION_HOTFIX.md`

---

**Deployment Time**: ~5 minutes
**Testing Time**: ~5 minutes
**Total Downtime**: 2-3 minutes (during Odoo restart)
