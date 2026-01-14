# Production Login Fix - Canonical Runbook

**Issue**: Login form not clickable at https://erp.insightpulseai.net/web/login

**Root Cause**: Stale asset attachments in `ir_attachment` table after filestore wipe causing JavaScript assets to return HTTP 500, preventing OWL component `web.user_switch` from removing `d-none` class.

**Terminology Correction**: This is **stale asset attachments**, NOT database corruption. Evidence: assets regenerated immediately after purge with HTTP 200 responses in logs.

---

## Diagnosis (No UI Required)

### HTTP-Based Health Check
```bash
./scripts/healthcheck_odoo_login.sh
```

**Pass Criteria**:
- ✅ Login page returns HTTP 200
- ✅ Frontend assets return HTTP 200 (not 500)
- ✅ Asset content is valid JavaScript

### Headless JS Verification (Optional)
```bash
# Requires Node.js + Playwright
npm install -g playwright
npx playwright install chromium
node scripts/verify_login_headless.js
```

**Pass Criteria**:
- ✅ `login_form_visible: true`
- ✅ `odoo_global_detected: true`
- ✅ No console errors (or non-fatal only)

---

## Fix Procedure (Idempotent + Safe)

### Option 1: Automated Fix Script
```bash
# On production droplet (178.128.112.214)
cd /opt/odoo-ce/repo

# Set environment (adjust for your setup)
export DB_HOST="your-db-host"
export DB_PORT="6543"
export DB_NAME="odoo"
export DB_USER="your-db-user"
export DB_PASSWORD="your-db-password"
export ODOO_CONTAINER="odoo-prod"

./scripts/fix_odoo_assets_after_filestore_wipe.sh
```

### Option 2: Manual Steps
```bash
# Step 1: Purge stale asset attachments
psql "$POSTGRES_URL" <<'SQL'
DELETE FROM ir_attachment
WHERE (url LIKE '/web/assets/%')
   OR (name LIKE 'web.assets%')
   OR (name LIKE 'web_editor.assets%')
   OR (name LIKE 'web._assets_%')
   OR (name LIKE 'web.assets_frontend%')
   OR (name LIKE 'web.assets_backend%')
   OR (res_model = 'ir.ui.view' AND name LIKE '%assets%');

-- Also clear orphaned attachments
DELETE FROM ir_attachment
WHERE res_model = 'ir.ui.view'
  AND res_id NOT IN (SELECT id FROM ir_ui_view);
SQL

# Step 2: Restart Odoo to regenerate assets
docker restart odoo-prod

# Step 3: Wait and verify
sleep 10
./scripts/healthcheck_odoo_login.sh
```

---

## Prevention (CI/CD Health Gates)

### GitHub Actions (Automated)
```yaml
# .github/workflows/production-health-check.yml
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
```

Automatically runs `healthcheck_odoo_login.sh` and alerts on failure.

### n8n Monitoring (Optional)
```javascript
// n8n workflow: Production Login Health Monitor
// Schedule: Every 30 minutes

HTTP Request: GET https://erp.insightpulseai.net/web/assets/1/f72ec00/web.assets_frontend_minimal.min.js
IF status_code != 200:
  Mattermost: "🚨 Production login assets failing - HTTP {status_code}"
  Run: ssh root@178.128.112.214 "cd /opt/odoo-ce/repo && ./scripts/fix_odoo_assets_after_filestore_wipe.sh"
```

### Cron (Manual Setup)
```bash
# On production droplet
crontab -e

# Add:
0 */6 * * * cd /opt/odoo-ce/repo && ./scripts/healthcheck_odoo_login.sh || curl -X POST "$MATTERMOST_WEBHOOK_URL" -d '{"text":"🚨 Production login health check failed"}'
```

---

## Technical Details

### Why This Happens

**Scenario**: Filestore wipe WITHOUT database cleanup
```
1. Filestore wiped: rm -rf /var/lib/odoo/filestore/odoo/
2. ir_attachment still has records pointing to deleted files
3. ir.binary._record_to_stream() tries to read missing files
4. Returns HTTP 500 instead of regenerating
5. web.user_switch OWL component never loads
6. d-none class never removed → form stays hidden
```

**Correct Fix**: Purge attachments THEN wipe filestore (or just purge, Odoo will regenerate)

### Asset System Components

**Database Tables**:
- `ir_attachment`: Stores compiled asset bundles
- `ir_ui_view`: Contains QWeb templates

**Filestore Paths**:
- `/var/lib/odoo/filestore/{db}/web_editor/` - Asset blobs
- `/var/lib/odoo/sessions/` - Session data

**Critical Assets**:
- `/web/assets/1/*/web.assets_frontend_minimal.min.js` - Login JS
- `/web/assets/1/*/web.assets_frontend_minimal.min.css` - Login CSS

### OWL Component Flow

```javascript
// Odoo 18 login page flow:
1. HTML renders with <form class="oe_login_form d-none">
2. JavaScript loads: web.assets_frontend_minimal.min.js
3. OWL component mounts: <owl-component name="web.user_switch">
4. Component removes d-none class dynamically
5. Form becomes visible
```

**If JavaScript fails (HTTP 500)**: Steps 3-5 never execute → form stays hidden

---

## Acceptance Gates

### Minimum (HTTP-based)
```bash
./scripts/healthcheck_odoo_login.sh
```
- Exit code 0 = PASS
- Exit code 2 = Login page HTTP error
- Exit code 3 = Asset system HTTP error

### Comprehensive (Headless)
```bash
node scripts/verify_login_headless.js
```
- Exit code 0 = PASS (form visible + JS executed)
- Exit code 2 = FAIL (form still hidden after JS load)

### Visual Parity (Optional)
```bash
# Playwright screenshot comparison
node scripts/snap.js --routes="/web/login"
node scripts/ssim.js --routes="/web/login" --threshold-mobile=0.97
```

---

## Rollback Strategy

If fix fails or causes issues:

```bash
# 1. Check Odoo logs
docker logs odoo-prod --tail 100

# 2. Restart container (often fixes transient issues)
docker restart odoo-prod

# 3. Verify database connectivity
psql "$POSTGRES_URL" -c "SELECT COUNT(*) FROM ir_attachment WHERE name LIKE 'web.assets%';"

# 4. Restore from backup (if needed)
# See BACKUP_RESTORE.md for full procedure
```

---

## Related Documentation

- `SANDBOX.md` - Local development workflow
- `sandbox/dev/README_CANONICAL.md` - Local dev guide (safe operations)
- `scripts/fix_production_assets.sh` - Quick fix script (uses SSH)
- `scripts/healthcheck_odoo_login.sh` - Health gate (no dependencies)
- `scripts/verify_login_headless.js` - Playwright verification (requires Node)

---

## Changelog

**2026-01-14**: Initial canonical runbook
- Root cause: Stale asset attachments (not corruption)
- Fix: Purge ir_attachment records
- Health gates: HTTP-based (no UI) + optional Playwright
- Automation: GitHub Actions + n8n monitoring
