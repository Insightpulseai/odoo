# Finance PPM Umbrella Module

**Canonical Version:** `finance-ppm-v1.0.0` (Git tag)  
**Scope:** 8 employees, 12 logframe entries, 144 BIR schedules, 36 closing tasks  
**Canonical Project:** Month-End Closing and Tax Filing (ID 30)

## Architecture

```
Excel RACI File (Source of Truth)
   ↓
Python Generation Script
   ↓
XML Seed Files (noupdate="1")
   ↓
Odoo Database (Production)
```

## Data Pipeline

### Source of Truth

- **Excel File:** `config/finance/BIR_SCHEDULE_2026.xlsx`
- **Generator Script:** `scripts/generate_seed_from_excel.py`
- **Base Module:** `ipai_finance_ppm` (framework: models, views, security)
- **Umbrella Module:** `ipai_finance_ppm_umbrella` (seed data for 8-employee SSC)

### Generated Seed Files (all `noupdate="1"`)

1. `data/01_employees.xml` - 8 Finance SSC employees with codes
2. `data/02_logframe_complete.xml` - 12 logframe entries (Goal → Activities)
3. `data/03_bir_schedule.xml` - 144 BIR filing records (Q4 2025 + 2026)
4. `data/04_closing_tasks.xml` - 36 month-end closing tasks linked to logframe
5. `views/finance_ppm_menu.xml` - UI menus (Logframe, BIR, Closing Tasks)

## Canonical Data Counts

**Expected Health Check Results:**

| Metric | Count | Table | Filter |
|--------|-------|-------|--------|
| Employees | 8 | `res_users` | `x_employee_code IS NOT NULL` |
| Logframe | 12 | `ipai_finance_logframe` | All records |
| BIR Schedules | 144 | `ipai_finance_bir_schedule` | All records |
| Closing Tasks | 36 | `project_task` | `project_id = 30` |
| Logframe Links | 36 | `project_task` | `finance_logframe_id IS NOT NULL AND project_id = 30` |

**Summary:** `8 / 12 / 144 / 36 / 36`

## Regeneration Workflow

### 1. Update Source Data

Edit the canonical Excel file:

```bash
open config/finance/BIR_SCHEDULE_2026.xlsx
```

### 2. Regenerate XML Seed Files

```bash
python3 scripts/generate_seed_from_excel.py
```

This will update:
- `addons/ipai_finance_ppm_umbrella/data/*.xml`

### 3. Test on Test Database

```bash
# Upgrade modules on test DB
ssh root@159.223.75.148 "docker exec -e PGHOST=odoo-db-1 -e PGUSER=odoo -e PGPASSWORD=odoo \
  odoo-production odoo -d odoo_ppm_test -u ipai_finance_ppm,ipai_finance_ppm_umbrella --stop-after-init"

# Run health check
./scripts/finance_ppm_health_check.sh odoo_ppm_test
```

### 4. Verify Health Check

Expected output:

```
=== Finance PPM Health Check ===

6. Summary (expected: 8 / 12 / 144 / 36 / 36):
 employees | logframe | bir_records | tasks | logframe_links
-----------+----------+-------------+-------+----------------
         8 |       12 |         144 |    36 |             36
```

### 5. Deploy to Production

If health check passes:

```bash
# Upgrade modules on production
ssh root@159.223.75.148 "docker exec -e PGHOST=odoo-db-1 -e PGUSER=odoo -e PGPASSWORD=odoo \
  odoo-production odoo -d odoo -u ipai_finance_ppm,ipai_finance_ppm_umbrella --stop-after-init"

# Verify production health
./scripts/finance_ppm_health_check.sh odoo
```

### 6. Commit and Tag

```bash
git add addons/ipai_finance_ppm_umbrella/data/*.xml
git commit -m "feat(finance-ppm): Update seed data from BIR_SCHEDULE_2026.xlsx"
git tag -a finance-ppm-v1.2.0 -m "Updated seed data [date]"
git push origin main finance-ppm-v1.2.0
```

## Health Check

### Quick Check (Shell Script)

```bash
# Production database
./scripts/finance_ppm_health_check.sh

# Test database
./scripts/finance_ppm_health_check.sh odoo_ppm_test
```

### Manual SQL Check

```bash
ssh root@159.223.75.148 "docker exec -i odoo-db-1 psql -U odoo -d odoo" < scripts/finance_ppm_health_check.sql
```

## Legacy Data Management

**Canonical Project:** ID 30 (Month-End Closing and Tax Filing)  
**Legacy Projects (Deactivated):** IDs 19, 28, 29

To verify legacy projects are quarantined:

```sql
SELECT id, name::text, active FROM project_project WHERE id IN (19, 28, 29, 30);
```

Expected:
- Projects 19, 28, 29: `active = FALSE`
- Project 30: `active = TRUE`

## UI Access

After installation, access via:

**Finance PPM Menu** (ID 753)
- Logical Framework → View Logframe (ID 755)
- BIR Filing Schedule → View BIR Schedule (ID 757)
- Month-End Closing → View Closing Tasks (ID 759)

## Rollback Procedure

If deployment fails:

```bash
# 1. Restore from Git tag
git checkout finance-ppm-v1.0.0

# 2. Rollback Odoo modules
ssh root@159.223.75.148 "docker exec -e PGHOST=odoo-db-1 -e PGUSER=odoo -e PGPASSWORD=odoo \
  odoo-production odoo -d odoo -u ipai_finance_ppm,ipai_finance_ppm_umbrella --stop-after-init"

# 3. Verify health check
./scripts/finance_ppm_health_check.sh odoo
```

## Version History

- **v1.0.0** (2025-12-26): Initial canonical deployment
  - 8 employees (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)
  - 12 logframe entries
  - 144 BIR schedules (Q4 2025 + 2026)
  - 36 closing tasks
  - Project ID 30 as canonical

- **v1.1.0** (2025-12-26): UI menus and canonical seed warnings
  - Finance PPM root menu with 3 submenus
  - Canonical warning headers in XML files
  - Legacy projects quarantined (19, 28, 29)

## References

- **Base Module:** `/addons/ipai_finance_ppm/`
- **Umbrella Module:** `/addons/ipai_finance_ppm_umbrella/`
- **Generator Script:** `/scripts/generate_seed_from_excel.py`
- **Health Check SQL:** `/scripts/finance_ppm_health_check.sql`
- **Health Check Shell:** `/scripts/finance_ppm_health_check.sh`
- **Canonical Tag:** `git show finance-ppm-v1.0.0`

## License

LGPL-3 (same as Odoo CE 18.0)

## Authors

- InsightPulse AI
- Co-Authored-By: Claude Sonnet 4.5
