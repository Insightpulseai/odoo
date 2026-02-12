# Multi-Company Seeding for Odoo CE

## Overview

Idempotent seeding script for creating organizational structure in Odoo CE with stable external IDs.

**Companies Created:**
1. **Dataverse IT Consultancy** (HO, BIR Branch 000, Pasig)
2. **W9 Studio** (Branch 001, Makati - La Fuerza)
3. **Project Meta - EvidenceLab Consulting** (Branch 002, Pasig)
4. **TBWA\SMP** (Separate entity)

**Users Created:**
1. **Jake Tolentino** (jgtolentino@yahoo.com) - System Admin, multi-company access
2. **Finance Ops** (finance@insightpulseai.com) - Accounting Manager, multi-company access (excluding TBWA\SMP)

## Files

- `scripts/seed_companies_users.py` - Main seeding script
- `scripts/rollback_seed_org.sql` - Rollback script
- `docs/operations/MULTI_COMPANY_SEEDING.md` - This file

## Execution

### Development Environment

```bash
cd /Users/tbwa/Documents/GitHub/Insightpulseai/odoo

# Via Docker Compose (recommended for dev sandbox)
docker compose exec -T odoo \
  odoo-bin shell -d odoo_dev --no-http < scripts/seed_companies_users.py

# Via local Odoo installation
odoo-bin shell -d odoo_dev -c odoo.conf --no-http < scripts/seed_companies_users.py
```

### Production Environment

**⚠️ WARNING:** Always test in dev/staging first.

```bash
# SSH to production server
ssh root@178.128.112.214

# Run via production container
docker exec -i odoo-erp-prod \
  odoo-bin shell -d odoo --no-http < /path/to/scripts/seed_companies_users.py
```

## Verification

### Check Companies and Users

```bash
# Via Docker
docker compose exec -T db psql -U odoo -d odoo_dev -c "
SELECT id, name, vat, city FROM res_company ORDER BY id;
"

# Check users
docker compose exec -T db psql -U odoo -d odoo_dev -c "
SELECT id, login, active, company_id FROM res_users ORDER BY id;
"

# Check multi-company assignments
docker compose exec -T db psql -U odoo -d odoo_dev -c "
SELECT u.login, array_agg(c.name ORDER BY c.name) as allowed_companies
FROM res_users u
JOIN res_company_users_rel r ON r.user_id = u.id
JOIN res_company c ON c.id = r.cid
WHERE u.login IN ('jgtolentino@yahoo.com', 'finance@insightpulseai.com')
GROUP BY u.login;
"
```

### Check External IDs

```bash
docker compose exec -T db psql -U odoo -d odoo_dev -c "
SELECT module, name, model, res_id
FROM ir_model_data
WHERE module = 'ipai_org'
ORDER BY model, name;
"
```

## Rollback

### Delete Seeded Records

```bash
# Via Docker
docker compose exec -T db psql -U odoo -d odoo_dev -f scripts/rollback_seed_org.sql

# Or via psql directly
psql "$DATABASE_URL" -f scripts/rollback_seed_org.sql
```

**Note:** This only removes the external ID bindings. To fully remove companies/users, you may need to delete them manually via Odoo UI or additional SQL.

## Idempotency

The script uses `ir.model.data` (external IDs) to ensure:
- Re-running the script updates existing records instead of creating duplicates
- Each company/user has a stable xmlid (e.g., `ipai_org.company_dataverse`)
- Safe to run multiple times without side effects

## BIR Branch Code Mapping

| Company | BIR Branch | Location | TIN/VAT |
|---------|------------|----------|---------|
| Dataverse IT Consultancy | 000 (HO) | Pasig | 215-308-716-000 |
| W9 Studio | 001 | Makati (La Fuerza) | Same as Dataverse (branch) |
| EvidenceLab Consulting | 002 | Pasig (virtual/tied to HO) | TBD (same TIN or separate) |
| TBWA\SMP | N/A | TBD | Separate (if applicable) |

**Note:** Odoo CE doesn't have native BIR branch code support. We use:
- `vat` field for TIN (HO only, or duplicated for branches)
- `report_footer` for BIR branch code comments
- Future: OCA module or custom field for proper branch code tracking

## Group Dependencies

The script references these Odoo security groups:
- `base.group_system` - Technical Settings (always exists)
- `account.group_account_manager` - Accounting Manager (requires `account` module)

If `account` module is not installed, you'll see an error. Fix:
1. Install accounting module first, OR
2. Change finance user group to `base.group_user` in script

## Security Considerations

1. **Passwords:** Script does not set passwords. Users must reset via Odoo UI or separate script.
2. **Multi-company access:** Jake has access to all 4 companies; Finance has access to 3 (excluding TBWA\SMP).
3. **Super admin:** Jake is `base.group_system` - full technical access.
4. **External IDs:** All records use `ipai_org.*` xmlids for traceability.

## Customization

Edit `scripts/seed_companies_users.py`:

**Add/modify companies:**
```python
COMPANIES = [
    {
        "xmlid": "ipai_org.company_new",
        "name": "New Company Name",
        "street": "Address Line 1",
        "city": "City",
        "vat": "TIN-NUMBER",
        # ... other fields
    },
]
```

**Add/modify users:**
```python
USERS = [
    {
        "xmlid": "ipai_org.user_new",
        "name": "User Name",
        "login": "email@domain.com",
        "groups": ["base.group_user"],
        "home_company_xmlid": "ipai_org.company_dataverse",
        "allowed_company_xmlids": ["ipai_org.company_dataverse"],
    },
]
```

## Troubleshooting

**Error: Missing group xmlid**
- Ensure required modules are installed (e.g., `account` for accounting groups)
- Or change group to `base.group_user`

**Error: Country code 'PH' not found**
- Load `base` module with country data
- Or remove `country_id` from company vals

**Duplicate companies created**
- Check that xmlids are unique
- Verify `ir.model.data` entries: `SELECT * FROM ir_model_data WHERE module='ipai_org';`

**Users not created**
- Check that home_company_xmlid exists
- Verify group xmlids are valid

## Next Steps

After seeding:
1. **Set user passwords** via Odoo UI (Settings → Users)
2. **Configure accounting** (chart of accounts, fiscal positions, taxes)
3. **Add BIR branch tracking** (custom field or OCA module)
4. **Setup company-specific settings** (email templates, report headers, etc.)
5. **Verify multi-company isolation** (test data access across companies)

## References

- [Odoo Multi-Company Documentation](https://www.odoo.com/documentation/19.0/applications/general/multi_companies.html)
- [External ID (ir.model.data)](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html#external-identifiers)
- [BIR Philippines Tax Compliance](https://www.bir.gov.ph/)
