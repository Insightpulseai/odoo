# Success Criteria - Production Hotfix

**Version**: 1.0
**Date**: 2025-01-05
**Deployment**: Production (erp.insightpulseai.com)

---

## 1. Expected End State (Artifacts)

This is what the system code and database state **MUST** look like after applying the fix.

### A. XML State (View Architecture)

**Target**: Odoo View Architecture in Database (`ir.ui.view`)

The specific view (likely inheriting `res.config.settings`) must **NOT** contain the field `pay_invoices_online`.

#### ❌ Current (Failing) State:

```xml
<div class="col-12 col-lg-6 o_setting_box" id="account_online_payment">
    <div class="o_setting_left_pane">
        <field name="pay_invoices_online"/>
    </div>
    <div class="o_setting_right_pane">
        <label for="pay_invoices_online"/>
        <div class="text-muted">
            Let your customers pay their invoices online
        </div>
    </div>
</div>
```

#### ✅ Expected End State:

```xml
<!-- Field completely removed - no trace in database -->
```

**Verification**:
```sql
-- Must return 0
SELECT COUNT(*) FROM ir_ui_view
WHERE arch_db ILIKE '%pay_invoices_online%';
```

---

### B. JSON/DB State (System Parameters)

**Target**: `ir.config_parameter` table in PostgreSQL

You can verify this by querying the database or checking `Settings > Technical > System Parameters`.

```json
{
  "web.base.url": "https://erp.insightpulseai.com",
  "web.base.url.freeze": "True",
  "report.url": "http://127.0.0.1:8069"
}
```

*Note: `report.url` is optional but recommended for wkhtmltopdf to work correctly behind Nginx.*

**Verification**:
```bash
docker exec odoo-erp-prod psql -U odoo -d prod -c "
  SELECT key, value FROM ir_config_parameter
  WHERE key IN ('web.base.url', 'web.base.url.freeze', 'report.url');
"
```

**Expected Output**:
```
            key            |              value
---------------------------+----------------------------------
 web.base.url              | https://erp.insightpulseai.com
 web.base.url.freeze       | True
 report.url                | http://127.0.0.1:8069
```

---

### C. Config State (Infrastructure)

**Target**: `odoo.conf` and Nginx Headers

#### `odoo.conf`:

```ini
[options]
proxy_mode = True
```

**Verification**:
```bash
docker exec odoo-erp-prod grep "proxy_mode" /etc/odoo/odoo.conf
# Expected: proxy_mode = True
```

#### Nginx Header Inspection (JSON representation):

When Odoo receives a request, the headers **MUST** look like this (verified via Odoo logs):

```json
{
  "Host": "erp.insightpulseai.com",
  "X-Forwarded-Host": "erp.insightpulseai.com",
  "X-Forwarded-Proto": "https",
  "X-Real-IP": "<Client_IP>"
}
```

**Verification**:
```bash
docker exec nginx nginx -T | grep "X-Forwarded-Proto"
# Expected: proxy_set_header X-Forwarded-Proto https;
```

---

## 2. Success Criteria

You have successfully fixed the system if **ALL** of the following conditions pass.

### Criterion 1: The "OwlError" Smoke Test (Frontend)

**Action**: Open Chrome Incognito, clear cache, navigate to `https://erp.insightpulseai.com/web/login`.

**Expected Result**:
- ✅ **PASS**: The login screen renders fully with Gmail SSO button visible
- ❌ **FAIL**: The screen is white/blank, or a popup appears saying `OwlError: An error occurred in the owl lifecycle`

**Verification Command**:
```bash
curl -s https://erp.insightpulseai.com/web/login | grep -q "Login" && echo "PASS" || echo "FAIL"
```

---

### Criterion 2: The "Console" Check (Developer Tools)

**Action**: Press `F12` to open Developer Tools → Console. Refresh the page.

**Expected Result**:
- ✅ **PASS**: No red errors related to `Uncaught Promise` or `Field pay_invoices_online does not exist`
- ❌ **FAIL**: `Error: Field pay_invoices_online does not exist in model res.config.settings`

**Verification Command**:
```bash
docker logs odoo-erp-prod --tail 100 | grep "pay_invoices_online"
# Expected: No output (0 matches)
```

**Browser Console Expected**:
```
[No errors]
```

**Browser Console Failure Example**:
```javascript
Uncaught (in promise) Error: Field pay_invoices_online does not exist
    at owl_component_2.js:1234
    at res_config_settings_view.js:567
```

---

### Criterion 3: The OAuth/HTTPS Loop Test

**Action**: Attempt to log in using Gmail SSO button.

**Expected Result**:
- ✅ **PASS**: The browser stays on `https://`. The URL **never** changes to `http://`
- ❌ **FAIL**: The browser redirects to `http://erp.insightpulseai.com` (dropping the 's') or enters an infinite redirect loop

**Verification Command**:
```bash
# Test OAuth redirect (should return 303 with https:// location)
curl -sI "https://erp.insightpulseai.com/auth_oauth/signin" | grep -i location
# Expected: Location: https://... (NOT http://)
```

**Browser Network Tab Expected**:
```
Request URL: https://erp.insightpulseai.com/auth_oauth/signin
Status Code: 303 See Other
Location: https://accounts.google.com/o/oauth2/auth?...
```

**Browser Network Tab Failure Example**:
```
Request URL: https://erp.insightpulseai.com/auth_oauth/signin
Status Code: 301 Moved Permanently
Location: http://erp.insightpulseai.com/auth_oauth/signin  ❌ (infinite loop)
```

---

### Criterion 4: Assets Generation

**Action**: Check the `<head>` of the source code (View Page Source).

**Expected Result**:
- ✅ **PASS**: `<link type="text/css" rel="stylesheet" href="/web/assets/....css"/>` loads with status `200 OK`
- ❌ **FAIL**: Asset files return `404 Not Found` (requires regeneration)

**Verification Command**:
```bash
# Check if web assets exist in database
docker exec odoo-erp-prod psql -U odoo -d prod -c "
  SELECT COUNT(*) FROM ir_attachment
  WHERE name LIKE 'web.assets_%';
"
# Expected: COUNT > 0
```

**Browser Source Code Expected**:
```html
<head>
  <link type="text/css" rel="stylesheet" href="/web/assets/web.assets_common.min.css" />
  <link type="text/css" rel="stylesheet" href="/web/assets/web.assets_backend.min.css" />
  <script type="text/javascript" src="/web/assets/web.assets_common.min.js"></script>
</head>
```

**Browser Network Tab Verification**:
```
GET /web/assets/web.assets_backend.min.css
Status: 200 OK
Content-Type: text/css
```

---

## 3. Automated Validation

Run the automated validation script to verify all criteria:

```bash
./scripts/validate_production.sh prod
```

**Expected Output**:
```
==================================================
VALIDATION RESULTS
==================================================
Total Tests:  7
Passed:       7
Failed:       0

✅ ALL SUCCESS CRITERIA MET

Expected End State Achieved:
  ✓ XML State: No 'pay_invoices_online' in database views
  ✓ JSON/DB State: web.base.url = https://erp.insightpulseai.com
  ✓ Config State: proxy_mode = True, X-Forwarded-Proto = https
  ✓ Assets State: Web assets generated and cached
```

---

## 4. Manual User Acceptance Testing

### Step-by-Step UAT Checklist

#### Test 1: Login Page Rendering

- [ ] Open Chrome Incognito window
- [ ] Navigate to `https://erp.insightpulseai.com`
- [ ] Verify login page renders (no white screen)
- [ ] Verify "Sign in with Gmail" button is visible
- [ ] Press F12 → Console tab
- [ ] Verify no red error messages

#### Test 2: OAuth Flow

- [ ] Click "Sign in with Gmail" button
- [ ] Verify redirect to `https://accounts.google.com/...`
- [ ] Complete Google authentication
- [ ] Verify redirect back to `https://erp.insightpulseai.com` (NOT `http://`)
- [ ] Verify successful login to Odoo dashboard

#### Test 3: Settings Page (OwlError Test)

- [ ] Navigate to Settings → General Settings
- [ ] Verify page loads without JavaScript errors
- [ ] Press F12 → Console tab
- [ ] Verify no `OwlError` or `Field pay_invoices_online` errors
- [ ] Scroll through settings tabs
- [ ] Verify no crashes or blank sections

#### Test 4: Assets Loading

- [ ] View page source (Ctrl+U / Cmd+Option+U)
- [ ] Find `<link rel="stylesheet" href="/web/assets/...css" />`
- [ ] Copy asset URL and paste in new tab
- [ ] Verify CSS file loads with `200 OK` status
- [ ] Repeat for JavaScript assets

#### Test 5: Multi-Browser Testing

- [ ] Repeat Test 1-4 in Firefox
- [ ] Repeat Test 1-4 in Safari (if on macOS)
- [ ] Verify consistent behavior across browsers

---

## 5. Rollback Criteria

Rollback deployment if **ANY** of these conditions occur:

- ❌ Login page shows white screen or OwlError popup
- ❌ Browser console shows `Field pay_invoices_online does not exist`
- ❌ OAuth redirect enters infinite loop (http:// ↔ https://)
- ❌ Asset files return 404 Not Found
- ❌ More than 5% of login attempts fail within first 30 minutes
- ❌ Automated validation script returns `FAILED`

**Rollback Command**:
```bash
# See docs/PRODUCTION_HOTFIX.md for complete rollback procedure
git checkout deploy/nginx/erp.insightpulseai.com.conf.backup
docker cp deploy/nginx/erp.insightpulseai.com.conf nginx:/etc/nginx/conf.d/
docker exec nginx nginx -s reload
docker exec postgres psql -U odoo -d postgres < /backups/prod_latest.sql
docker restart odoo-erp-prod
```

---

## 6. Sign-Off

**Deployment Sign-Off**:

- [ ] All automated validation tests passed (7/7)
- [ ] Manual UAT completed successfully (all checkboxes)
- [ ] OAuth login works with Gmail SSO
- [ ] No OwlError in browser console
- [ ] Assets load correctly (200 OK status)
- [ ] Production monitoring shows no errors (first 30 min)

**Approval**:
- **Deployed by**: _________________ Date: _________
- **Verified by**: _________________ Date: _________
- **Approved by**: _________________ Date: _________

---

**Last Updated**: 2025-01-05
**Document Owner**: DevOps Engineer (jgtolentino)
**Next Review**: After successful production deployment
