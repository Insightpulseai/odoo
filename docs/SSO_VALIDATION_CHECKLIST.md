# SSO Configuration Validation Checklist

**Date**: 2025-11-25
**Module**: ipai_finance_ppm_tdi v1.0.0
**Deployment**: Odoo CE v0.10.0 on VPS 159.223.75.148

---

## ✅ Phase 2 Complete - Code Validation

### Odoo Configuration Files
- ✅ `addons/ipai_finance_ppm_tdi/__manifest__.py` - OCA-compliant manifest
- ✅ `addons/ipai_finance_ppm_tdi/models/finance_ppm_tdi_audit.py` - Audit trail model
- ✅ `addons/ipai_finance_ppm_tdi/wizard/finance_ppm_import_wizard.py` - Import wizard
- ✅ `addons/ipai_finance_ppm_tdi/security/security_groups.xml` - 3 security groups
- ✅ `addons/ipai_finance_ppm_tdi/security/ir.model.access.csv` - Access control lists
- ✅ `addons/ipai_finance_ppm_tdi/views/*.xml` - Wizard UI, audit views, menus
- ✅ `addons/ipai_finance_ppm_tdi/README.md` - Complete documentation

### Security Groups Created
1. **Finance PPM User** - View access to import history
2. **Finance PPM Manager** - Can import data (includes User permissions)
3. **Finance PPM Administrator** - Full access including cleanup/rollback

---

## ⚠️ Manual SSO Validation Required

### 🔴 CRITICAL: Keycloak Redirect URI Configuration

**Action Required**: Log in to Keycloak Admin Console and verify:

1. **Navigate to**: Keycloak Admin Console → Clients → `odoo-sso` (or your Odoo client name)

2. **Valid Redirect URIs Section**: Check if this exists:
   ```
   http://159.223.75.148:8069/auth_oauth/signin
   ```

3. **Expected State**:
   - ❌ **REMOVE** this URI if present (IP-based authentication is insecure)
   - ✅ **KEEP** only domain-based URIs:
     ```
     https://erp.insightpulseai.com/auth_oauth/signin
     https://erp.insightpulseai.com/*
     ```

4. **Web Origins**: Should match redirect URIs domain:
   ```
   https://erp.insightpulseai.com
   ```

### Why This Matters
- **Security Risk**: IP-based URIs bypass SSL/TLS certificate validation
- **Login Failures**: Mixed IP/domain configuration causes OAuth state mismatches
- **Production Standard**: All production SSO should use domain names only

---

## 📋 User Permission Assignment (Manual Setup)

After module installation, SSO users will have **no Finance PPM permissions by default**.

### Initial User Setup (Jake Tolentino)

**Steps**:
1. Log in to Odoo as **Admin** (https://erp.insightpulseai.com)
2. Navigate to: **Settings** → **Users & Companies** → **Users**
3. Search for: `Jake Tolentino` or `jake.tolentino@insightpulseai.com`
4. Click to open user record
5. Scroll to **Finance PPM** section (added by `ipai_finance_ppm_tdi` module)
6. Select role:
   - `Finance PPM Administrator` (for full access)
   - `Finance PPM Manager` (for import capabilities)
   - `Finance PPM User` (for view-only access)
7. Click **Save**

**Repeat** for other finance team members as they are added.

### Alternative: Automatic Role Mapping (Future Enhancement)

**Goal**: Map Keycloak roles to Odoo groups automatically via OIDC token claims.

**Implementation** (Phase 4 - Integration):
1. Configure Keycloak Role Mapper:
   ```
   Client: odoo-sso
   Mapper Type: User Realm Role
   Token Claim Name: groups
   Include in: ID Token, Access Token
   ```

2. Create Keycloak roles:
   - `finance-ppm-admin`
   - `finance-ppm-manager`
   - `finance-ppm-user`

3. Extend Odoo OAuth provider to parse `groups` claim:
   ```python
   # In auth_oauth module extension
   def _parse_oauth_groups(self, validation):
       groups = validation.get('groups', [])
       if 'finance-ppm-admin' in groups:
           # Add user to group_finance_ppm_admin
       # etc.
   ```

**Status**: Not implemented yet (manual assignment required for Phase 2)

---

## 🧪 SSO Login Test Procedure

After Keycloak configuration is validated:

### Test 1: Domain-Based Login
1. Navigate to: https://erp.insightpulseai.com
2. Click **Log in with SSO** (or Keycloak button)
3. Enter credentials: `jake.tolentino@insightpulseai.com` / [password]
4. **Expected**: Successful redirect to Odoo dashboard

### Test 2: Finance PPM Access
1. Navigate to: **Finance PPM** → **Data Ingestion** → **Import Data**
2. **Expected**:
   - If `Administrator`: Full wizard access
   - If `Manager`: Full wizard access
   - If `User`: Error (no permission to import)
   - If no group assigned: Menu not visible

### Test 3: Import History Access
1. Navigate to: **Finance PPM** → **Data Ingestion** → **Import History**
2. **Expected**:
   - If `User`, `Manager`, or `Administrator`: View audit logs
   - If no group assigned: Menu not visible

---

## 📊 Module Installation Verification

After deploying module to VPS:

### Pre-Installation Check
```bash
# SSH to VPS
ssh root@159.223.75.148

# Check if module is in addons path
docker exec odoo-ce ls -la /mnt/extra-addons/ | grep ipai_finance_ppm_tdi

# Expected: Directory exists with all files
```

### Installation Steps
1. Navigate to: https://erp.insightpulseai.com
2. **Settings** → **Apps** → **Update Apps List**
3. Remove "Apps" filter in search
4. Search: `Finance PPM TDI`
5. Click **Install**

### Post-Installation Verification
```sql
-- Connect to database
psql "postgresql://odoo:$DB_PASSWORD@159.223.75.148:5432/odoo"

-- Check if models are created
SELECT tablename FROM pg_tables WHERE tablename LIKE 'finance_ppm%';

-- Expected output:
-- finance_ppm_tdi_audit
-- finance_ppm_import_wizard

-- Check if security groups are created
SELECT name FROM res_groups WHERE name LIKE 'Finance PPM%';

-- Expected output:
-- Finance PPM User
-- Finance PPM Manager
-- Finance PPM Administrator
```

---

## 🚨 Troubleshooting

### Issue: SSO Login Fails with "Invalid redirect URI"
**Cause**: IP-based URI still present in Keycloak config
**Fix**: Remove `http://159.223.75.148:8069/auth_oauth/signin` from Valid Redirect URIs

### Issue: User has no Finance PPM menu access
**Cause**: User not assigned to any Finance PPM security group
**Fix**: Manually assign user to appropriate group (see User Permission Assignment above)

### Issue: Module not visible in Apps list
**Cause**: Module not in Odoo addons path or not detected
**Fix**:
1. Check docker-compose volume mount for custom addons
2. Update Apps List
3. Check Odoo logs for module loading errors

### Issue: Import wizard throws "openpyxl not available"
**Cause**: Missing Python dependency
**Fix**: Already included in Dockerfile.v0.10.0 (should not occur)

---

## ✅ Validation Sign-Off

### Phase 2 Code Validation
- [x] Module structure complete
- [x] Python models implemented
- [x] XML views and menus created
- [x] Security groups and access control defined
- [x] Documentation written

### SSO Configuration Validation (Manual)
- [ ] Keycloak redirect URI verified (IP removed)
- [ ] Domain-based URIs confirmed
- [ ] Web origins set correctly
- [ ] SSO login tested successfully

### User Permissions Validation (Manual)
- [ ] Jake Tolentino assigned to Finance PPM Administrator
- [ ] Test import wizard access
- [ ] Test import history access
- [ ] Confirm menu visibility

---

## 📅 Next Steps

**Ready for Phase 3**: Seed Data Generation

Once SSO and permissions are validated:
1. Create XML seed data for Finance Team (12 users)
2. Create XML seed data for Month-End Tasks (50+ tasks)
3. Create XML seed data for BIR Calendar (24+ forms)
4. Create XML seed data for LogFrame KPIs
5. Implement PH Holiday Calendar logic

**Deployment Timeline**:
- Phase 2 (Module Code): ✅ Complete (2025-11-25)
- Phase 3 (Seed Data): Pending
- Phase 4 (Integration): Pending
- Phase 5 (Verification): Pending

---

**Prepared by**: Claude Code (SuperClaude Framework)
**Reviewed by**: [Jake Tolentino - Pending]
**Approved for Production**: [Pending SSO Validation]
