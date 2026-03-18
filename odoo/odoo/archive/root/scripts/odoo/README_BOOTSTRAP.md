# Odoo Company Bootstrap Scripts

Three scripts for setting up InsightPulseAI + TBWA\SMP companies in Odoo CE 18.0.

---

## Quick Start (Recommended)

**Minimal setup** (name changes only, no side effects):

```bash
./scripts/odoo/bootstrap_companies_min.sh
```

**Full setup** (includes email, website, PH locale):

```bash
./scripts/odoo/bootstrap_companies.sh
```

**Remote setup** (no container access needed):

```bash
export ODOO_PASS='your-admin-password'
python3 scripts/odoo/company_bootstrap_xmlrpc.py
```

---

## Option 1: Minimal Bootstrap (Recommended)

**Script**: `company_bootstrap_min.py` + `bootstrap_companies_min.sh`

**What it does**:
- Renames "YourCompany" → "InsightPulseAI"
- Creates "TBWA\SMP" company
- Grants multi-company access to admin user
- Sets InsightPulseAI as default company

**What it DOESN'T do**:
- No email/website changes
- No currency/country changes
- No partner address updates

**When to use**: First-time setup, quick testing, minimal side effects

**Usage**:
```bash
# Default (odoo-erp-prod container)
./scripts/odoo/bootstrap_companies_min.sh

# Custom container name
./scripts/odoo/bootstrap_companies_min.sh my-odoo-container

# With environment variables
ODOO_OLD_COMPANY_NAME="MyOldCompany" \
ODOO_NEW_COMPANY_NAME="MyNewCompany" \
ODOO_TBWA_COMPANY_NAME="TBWA\SMP" \
ODOO_TARGET_USER_LOGIN="admin" \
./scripts/odoo/bootstrap_companies_min.sh
```

---

## Option 2: Full Bootstrap (Production-Ready)

**Script**: `company_bootstrap.py` + `bootstrap_companies.sh`

**What it does**:
- Everything from minimal bootstrap, PLUS:
- Sets company emails to `business@insightpulseai.com`
- Sets website to `https://insightpulseai.com`
- Sets currency to PHP (Philippine Peso)
- Sets country to PH (Philippines)
- Updates partner records to match

**When to use**: Production setup, complete company configuration

**Usage**:
```bash
# Default (odoo-erp-prod container)
./scripts/odoo/bootstrap_companies.sh

# Custom container name
./scripts/odoo/bootstrap_companies.sh my-odoo-container

# With custom values
ODOO_NEW_COMPANY_EMAIL="custom@example.com" \
ODOO_NEW_COMPANY_WEBSITE="https://example.com" \
ODOO_CURRENCY_CODE="USD" \
ODOO_COUNTRY_CODE="US" \
./scripts/odoo/bootstrap_companies.sh
```

**Environment Variables**:
```bash
ODOO_DB=odoo                          # Database name
ODOO_OLD_COMPANY_NAME=YourCompany     # Existing company to rename
ODOO_NEW_COMPANY_NAME=InsightPulseAI  # New company name
ODOO_NEW_COMPANY_EMAIL=business@insightpulseai.com
ODOO_NEW_COMPANY_WEBSITE=https://insightpulseai.com
ODOO_TBWA_COMPANY_NAME=TBWA\SMP       # Second company name
ODOO_TBWA_COMPANY_EMAIL=business@insightpulseai.com
ODOO_TBWA_COMPANY_WEBSITE=            # Leave empty for no website
ODOO_TARGET_USER_LOGIN=admin          # User to grant multi-company access
ODOO_COUNTRY_CODE=PH                  # Country code (ISO 3166-1 alpha-2)
ODOO_CURRENCY_CODE=PHP                # Currency code (ISO 4217)
```

---

## Option 3: XML-RPC Bootstrap (Remote Access)

**Script**: `company_bootstrap_xmlrpc.py`

**What it does**:
- Same as full bootstrap
- Works without container exec access
- Requires admin password

**When to use**:
- Remote Odoo instance
- No SSH/Docker access
- External automation scripts

**Usage**:
```bash
# Set credentials
export ODOO_URL="http://localhost:8069"  # or https://erp.insightpulseai.com
export ODOO_DB="odoo"
export ODOO_USER="admin"
export ODOO_PASS="your-admin-password"

# Run script
python3 scripts/odoo/company_bootstrap_xmlrpc.py
```

**Environment Variables**:
```bash
ODOO_URL=http://localhost:8069        # Odoo base URL
ODOO_DB=odoo                          # Database name
ODOO_USER=admin                       # Admin username
ODOO_PASS=                            # Admin password (REQUIRED)
ODOO_OLD_COMPANY_NAME=YourCompany
ODOO_NEW_COMPANY_NAME=InsightPulseAI
ODOO_NEW_COMPANY_EMAIL=business@insightpulseai.com
ODOO_NEW_COMPANY_WEBSITE=https://insightpulseai.com
ODOO_TBWA_COMPANY_NAME=TBWA\SMP
ODOO_TBWA_COMPANY_EMAIL=business@insightpulseai.com
ODOO_TARGET_USER_LOGIN=admin
```

---

## Verification

All scripts include automatic verification:

```
Companies:
  [1] InsightPulseAI
  [2] TBWA\SMP

admin default: InsightPulseAI
admin allowed: ['InsightPulseAI', 'TBWA\\SMP']
```

**Manual verification** (via Odoo UI):

1. Log in as admin
2. Go to Settings → Users & Companies → Companies
3. **Expected**: See "InsightPulseAI" and "TBWA\SMP"
4. Click user menu (top-right) → should show company switcher
5. **Expected**: Can switch between InsightPulseAI and TBWA\SMP

---

## Troubleshooting

### "No company found to rename"

**Symptom**: Script fails with `RuntimeError: No company found to rename.`

**Fix**: First company is always renamed. If "YourCompany" doesn't exist, it renames the first company by ID.

### "User not found"

**Symptom**: `RuntimeError: Target user not found: login=admin`

**Fix**: Set `ODOO_TARGET_USER_LOGIN` to correct username:
```bash
ODOO_TARGET_USER_LOGIN="your-username" ./scripts/odoo/bootstrap_companies_min.sh
```

### XML-RPC Authentication Failed

**Symptom**: `RuntimeError: Authentication failed`

**Fix**: Verify credentials:
```bash
# Test authentication
curl -X POST http://localhost:8069/xmlrpc/2/common \
  -d '<?xml version="1.0"?>
  <methodCall>
    <methodName>authenticate</methodName>
    <params>
      <param><string>odoo</string></param>
      <param><string>admin</string></param>
      <param><string>your-password</string></param>
      <param><struct></struct></param>
    </params>
  </methodCall>'
# Should return user ID (e.g., <int>2</int>)
```

### Multi-Company Group Not Found

**Symptom**: Warning about multi-company group not found (non-fatal)

**Fix**: Group is found by XML ID or name. If both fail, user won't have company switcher, but can be manually added in UI:
1. Settings → Users & Companies → Users → [User] → Edit
2. Groups → Check "Multi Companies"

---

## Production Checklist

Before running in production:

1. ✅ Backup database (`pg_dump` or DigitalOcean snapshot)
2. ✅ Test in sandbox/staging first
3. ✅ Verify container name (default: `odoo-erp-prod`)
4. ✅ Confirm admin user login (default: `admin`)
5. ✅ Run verification after script completes
6. ✅ Test company switcher in UI
7. ✅ Verify emails/websites if using full bootstrap

---

## Script Comparison

| Feature | Minimal | Full | XML-RPC |
|---------|---------|------|---------|
| Rename company | ✅ | ✅ | ✅ |
| Create TBWA\SMP | ✅ | ✅ | ✅ |
| Multi-company access | ✅ | ✅ | ✅ |
| Email/website | ❌ | ✅ | ✅ |
| Currency/country | ❌ | ✅ | ❌ |
| Partner updates | ❌ | ✅ | ❌ |
| Requires container exec | ✅ | ✅ | ❌ |
| Requires admin password | ❌ | ❌ | ✅ |

**Recommendation**:
- **First-time setup**: Use **minimal** (safest, no side effects)
- **Production config**: Use **full** (complete company setup)
- **Remote automation**: Use **XML-RPC** (no SSH needed)

---

**Last Updated**: 2026-01-14
**Tested On**: Odoo CE 18.0, PostgreSQL 16, Python 3.11
**Container**: `odoo-erp-prod` (default), customizable via `ODOO_CONTAINER` env var
