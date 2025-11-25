# Quick Reference: SSO & Permissions Setup

**Target**: Odoo CE 18.0 @ https://erp.insightpulseai.net
**Module**: ipai_finance_ppm_tdi v1.0.0

---

## 🔴 Step 1: Validate Keycloak (5 minutes)

### Access Keycloak Admin Console
```
URL: [Your Keycloak admin console URL]
Login: [Your Keycloak admin credentials]
```

### Navigate to Odoo Client
1. **Clients** → Search for `odoo-sso` (or your Odoo client name)
2. Click on the client

### Check Valid Redirect URIs
**Current State** (what you might see):
```
http://159.223.75.148:8069/auth_oauth/signin
https://erp.insightpulseai.net/auth_oauth/signin
https://erp.insightpulseai.net/*
```

**Target State** (what you should have):
```
https://erp.insightpulseai.net/auth_oauth/signin
https://erp.insightpulseai.net/*
```

**Action**: Delete the `http://159.223.75.148...` line if present

### Check Web Origins
**Should be**:
```
https://erp.insightpulseai.net
```

### Save Changes
Click **Save** at the bottom

---

## 👤 Step 2: Assign Permissions to Jake (3 minutes)

### Login to Odoo
```
URL: https://erp.insightpulseai.net
Method: SSO (Keycloak button)
Credentials: jake.tolentino@insightpulseai.com
```

### Navigate to User Management
1. Click **Settings** (top menu)
2. **Users & Companies** → **Users**
3. Search for `Jake Tolentino`
4. Click to open user record

### Assign Finance PPM Role
1. Scroll down to find **Finance PPM** section
2. Select: `Finance PPM Administrator`
3. Click **Save**

### Expected Result
- New menu item **Finance PPM** appears in top menu
- Can access **Finance PPM** → **Data Ingestion** → **Import Data**

---

## ✅ Step 3: Test SSO Login (2 minutes)

### Test Full Flow
1. Log out from Odoo
2. Go to: https://erp.insightpulseai.net
3. Click **Log in with SSO** (or Keycloak button)
4. Enter: `jake.tolentino@insightpulseai.com` / [password]
5. **Expected**: Redirect to Odoo dashboard
6. **Finance PPM** menu visible in top menu

### Test Import Access
1. Click **Finance PPM** → **Data Ingestion** → **Import Data**
2. **Expected**: Import wizard opens with file upload form
3. Select **Import Type**: Finance Team Members
4. Click **Download Template**
5. **Expected**: CSV file downloads

### Test History Access
1. Click **Finance PPM** → **Data Ingestion** → **Import History**
2. **Expected**: Empty list with "No import history yet" message

---

## 🚨 Troubleshooting

### "Invalid redirect URI" error
- **Cause**: IP-based URI still in Keycloak
- **Fix**: Step 1 not completed - remove IP from Keycloak

### Finance PPM menu not visible
- **Cause**: User not assigned to any Finance PPM group
- **Fix**: Step 2 not completed - assign user to group

### "Access Denied" when opening Import Data
- **Cause**: User assigned to "User" group (view-only)
- **Fix**: Change to "Manager" or "Administrator"

---

## 📋 Validation Checklist

Copy this checklist and mark as you complete:

```
SSO Configuration:
[ ] Keycloak admin console accessed
[ ] Odoo client configuration opened
[ ] IP-based redirect URI removed (if present)
[ ] Domain-based URIs confirmed correct
[ ] Web origins set to domain only
[ ] Changes saved

User Permissions:
[ ] Logged in to Odoo as Admin
[ ] Opened Jake Tolentino user record
[ ] Finance PPM section found
[ ] Administrator role selected
[ ] User record saved

SSO Testing:
[ ] Logged out from Odoo
[ ] Logged in via SSO successfully
[ ] Finance PPM menu visible
[ ] Import Data wizard accessible
[ ] Import History accessible
[ ] Download Template works

Module Verification:
[ ] Module listed in Apps (after "Update Apps List")
[ ] Security groups created (check Settings → Users → Groups)
[ ] Models created (check database: finance_ppm_tdi_audit table exists)
```

---

## 🎯 Success Criteria

**All green** when:
1. SSO login works with domain-based URI only
2. Jake has Finance PPM Administrator role
3. Finance PPM menu visible and functional
4. Import wizard and history accessible
5. No errors in Odoo logs

**Ready for Phase 3** when all checkboxes above are marked ✓

---

## 📞 Need Help?

**Common Questions**:
- **Q**: What if I can't find the Finance PPM section in user settings?
  - **A**: Module not installed yet. Go to Apps → Update Apps List → Search "Finance PPM TDI" → Install

- **Q**: Import wizard shows "openpyxl not available"?
  - **A**: Should not happen (included in Docker image). If occurs, check container: `docker exec odoo-ce pip list | grep openpyxl`

- **Q**: Can I test with a different user?
  - **A**: Yes, create another SSO user, but manually assign Finance PPM role first

---

**Completion Time**: ~10 minutes total
**Difficulty**: Low (all UI-based, no coding)
**Prerequisites**: Keycloak admin access + Odoo admin access

**Document Updated**: 2025-11-25
