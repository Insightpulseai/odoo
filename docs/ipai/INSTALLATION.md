# IPAI Module Suite - Installation Guide

## Prerequisites

**Odoo Version**: 18.0 Community Edition
**Python**: 3.11+
**PostgreSQL**: 15+
**Docker**: 24.0+ (for containerized deployment)
**Operating System**: Ubuntu 22.04 LTS (production) or macOS (development)

**Required Odoo Core Modules**:
- `base` (always installed)
- `mail` (mail threading and activities)
- `project` (project management - for Finance PPM)
- `hr` (human resources - for asset management)
- `account` (accounting - for finance modules)
- `stock` (inventory - for asset checkout)
- `barcodes` (barcode scanning - for asset management)

**Optional OCA Modules** (recommended for full functionality):
- `account_financial_report` (OCA/account-financial-reporting/18.0)
- `account_asset_management` (OCA/account-financial-tools/18.0)
- `project_wip` (OCA/project/18.0)

## Installation Methods

### Method 1: Production Deployment (DigitalOcean + Docker Compose)

**Current Production Stack**:
- **Host**: 159.223.75.148 (odoo-erp-prod droplet)
- **Database**: PostgreSQL 15 (`odoo` database)
- **Containers**: `odoo-accounting`, `odoo-core`, `odoo-marketing`, `odoo-db-1`

**Installation Procedure**:

```bash
# 1. SSH to production server
ssh root@159.223.75.148

# 2. Navigate to deployment directory
cd /opt/odoo-ce

# 3. Pull latest code
git pull origin main

# 4. Restart Odoo containers to pickup new modules
docker-compose restart odoo-accounting odoo-core

# 5. Install modules via docker exec
docker exec -it odoo-accounting odoo-bin \
  -d odoo \
  -i ipai_module_name \
  --stop-after-init \
  --logfile=/var/log/odoo/install.log

# 6. Verify installation
docker exec -it odoo-db-1 psql -U odoo -d odoo -c \
  "SELECT name, state FROM ir_module_module WHERE name LIKE 'ipai_%' ORDER BY name;"
```

### Method 2: Development Installation (Local Odoo)

```bash
# 1. Clone repository
git clone https://github.com/jgtolentino/odoo-ce.git
cd odoo-ce

# 2. Install Odoo if not already installed
# (Assumes Odoo 18 installed via apt/pip/source)

# 3. Add IPAI modules to addons path
# Edit odoo.conf:
[options]
addons_path = /path/to/odoo/addons,/path/to/odoo-ce/addons/ipai

# 4. Restart Odoo and install via CLI
odoo -c /etc/odoo/odoo.conf -d <database> -i ipai_module_name --stop-after-init

# 5. Verify via web UI
# Login to http://localhost:8069 → Apps → Search "IPAI"
```

### Method 3: Docker Compose (Local Development)

```bash
# 1. Clone repository
git clone https://github.com/jgtolentino/odoo-ce.git
cd odoo-ce

# 2. Use development compose file
docker-compose -f deploy/docker-compose.dev.yml up -d

# 3. Install modules via docker exec
docker exec -it odoo odoo-bin \
  -d odoo \
  -i ipai_module_name \
  --stop-after-init

# 4. Access web UI
# http://localhost:8069
```

## Installation Order (Critical)

**IMPORTANT**: Install modules in dependency order to avoid circular dependency errors and ensure proper database schema creation.

### Phase 1: Platform Utilities (No Dependencies)

```bash
odoo -d production -i ipai_ce_cleaner,ipai_ce_branding --stop-after-init
```

**Modules**:
- `ipai_ce_cleaner` - Removes Enterprise/IAP dependencies
- `ipai_ce_branding` - InsightPulse AI branding

**Verification**:
```sql
SELECT name, state FROM ir_module_module
WHERE name IN ('ipai_ce_cleaner', 'ipai_ce_branding');
-- Both should show state='installed'
```

### Phase 2: Core Operations (Base Dependencies Only)

```bash
odoo -d production -i ipai_advisor,ipai_assets,ipai_equipment,ipai_expense --stop-after-init
```

**Modules**:
- `ipai_advisor` - Ops advisor (recommendations engine)
- `ipai_assets` - Asset checkout (Cheqroom parity)
- `ipai_equipment` - Equipment management
- `ipai_expense` - Expense & Travel (PH tax rules)

**Verification**:
```sql
SELECT name, state FROM ir_module_module
WHERE name IN ('ipai_advisor', 'ipai_assets', 'ipai_equipment', 'ipai_expense');
-- All should show state='installed'
```

### Phase 3: Finance Base (Project + Account Dependencies)

```bash
odoo -d production -i ipai_finance_ppm,ipai_bir_compliance --stop-after-init
```

**Modules**:
- `ipai_finance_ppm` - Finance PPM core (logframe + BIR schedule + tasks)
- `ipai_bir_compliance` - Tax Shield (1601-C, 2550Q base)

**Verification**:
```sql
-- Check models created
SELECT tablename FROM pg_tables
WHERE tablename LIKE 'ipai_finance%' OR tablename LIKE 'ipai_bir%'
ORDER BY tablename;

-- Check menus created
SELECT id, name FROM ir_ui_menu
WHERE name ILIKE '%finance%' OR name ILIKE '%bir%';
```

### Phase 4: Finance PPM Stack (Depends on Phase 3)

```bash
odoo -d production -i ipai_ppm_a1,ipai_close_orchestration,ipai_finance_bir_compliance --stop-after-init
```

**Modules**:
- `ipai_ppm_a1` - A1 Control Center (logframe + task automation)
- `ipai_close_orchestration` - Close cycle orchestration engine
- `ipai_finance_bir_compliance` - BIR compliance (schedule + generator)

**Verification**:
```sql
-- Check BIR schedule records seeded
SELECT COUNT(*) FROM ipai_finance_bir_schedule;
-- Should return >0 (8+ BIR forms for current period)

-- Check logframe records seeded
SELECT COUNT(*) FROM ipai_finance_logframe;
-- Should return >0 (12+ logframe entries)
```

### Phase 5: Finance Advanced (Depends on Phase 4)

```bash
odoo -d production -i ipai_finance_month_end,ipai_finance_ppm_dashboard,ipai_finance_ppm_tdi --stop-after-init
```

**Modules**:
- `ipai_finance_month_end` - Month-end closing templates
- `ipai_finance_ppm_dashboard` - ECharts dashboards
- `ipai_finance_ppm_tdi` - Transaction data ingestion

**Verification**:
```bash
# Check dashboard accessible
curl -sf https://odoo.insightpulseai.com/ipai/finance/ppm | grep -q "TBWA Finance PPM Dashboard"
echo $?  # Should return 0 (success)
```

### Phase 6: WorkOS (Optional - Notion/AFFiNE Parity)

```bash
odoo -d production -i ipai_workspace_core --stop-after-init
```

**Modules**:
- `ipai_workspace_core` - Workspace core (blocks, pages, databases)

**Verification**:
```sql
SELECT tablename FROM pg_tables
WHERE tablename LIKE 'ipai_workos%' OR tablename LIKE 'ipai_workspace%'
ORDER BY tablename;
```

### Phase 7: Industry Modules (Optional)

```bash
odoo -d production -i ipai_industry_accounting_firm,ipai_industry_marketing_agency --stop-after-init
```

**Modules**:
- `ipai_industry_accounting_firm` - Accounting firm operations
- `ipai_industry_marketing_agency` - Marketing agency operations

## Upgrade Procedures

### Minor Version Upgrades (18.0.1.0.0 → 18.0.1.1.0)

```bash
# 1. Backup database first
docker exec odoo-db-1 pg_dump -U odoo odoo > backup_$(date +%Y%m%d).sql

# 2. Pull latest code
cd /opt/odoo-ce && git pull origin main

# 3. Upgrade modules
docker exec -it odoo-accounting odoo-bin \
  -d odoo \
  -u ipai_module_name \
  --stop-after-init

# 4. Verify upgrade
docker exec -it odoo-db-1 psql -U odoo -d odoo -c \
  "SELECT name, latest_version FROM ir_module_module WHERE name = 'ipai_module_name';"
```

### Major Version Upgrades (Odoo 17 → 18 Migration)

**Critical Changes in Odoo 18**:
1. **JSONB name fields**: `ir_ui_menu.name` changed from `char` to `jsonb`
2. **View tag changes**: Deprecated `<field name="arch" type="xml">` → use `<field name="arch">`
3. **Python 3.11+ required**: Odoo 18 drops Python 3.10 support

**Migration Procedure**:

```bash
# 1. CRITICAL: Backup production database
pg_dump -h <host> -U odoo -d odoo > odoo17_backup_$(date +%Y%m%d).sql

# 2. Create Odoo 18 environment (DO NOT UPGRADE IN-PLACE)
# Use separate database for testing

# 3. Install Odoo 18 base
# (Follow official Odoo 18 installation guide)

# 4. Restore database to new Odoo 18 instance
psql -U odoo -d odoo18_test < odoo17_backup_$(date +%Y%m%d).sql

# 5. Run Odoo 18 migration scripts
odoo -c /etc/odoo/odoo.conf -d odoo18_test --update=all --stop-after-init

# 6. Install IPAI modules (fresh install - DO NOT upgrade old versions)
odoo -c /etc/odoo/odoo.conf -d odoo18_test -i ipai_ce_cleaner --stop-after-init
# Then follow Phase 1-7 above

# 7. Verify data integrity
psql -U odoo -d odoo18_test -c "SELECT COUNT(*) FROM account_move;"
# Compare with production

# 8. Test critical workflows
# - Create expense
# - Create project task
# - Run BIR compliance check
# - Generate month-end report

# 9. Switch production to Odoo 18 (only after full testing)
```

## Troubleshooting

### Issue 1: Module Installation Fails - Missing Dependencies

**Error**:
```
Error: Module 'ipai_finance_ppm' depends on module 'project' which is not installed
```

**Fix**:
```bash
# Install missing core module first
odoo -d production -i project --stop-after-init

# Then retry IPAI module
odoo -d production -i ipai_finance_ppm --stop-after-init
```

### Issue 2: Database Schema Mismatch After Upgrade

**Error**:
```
psycopg2.errors.UndefinedColumn: column "name" is of type jsonb but expression is of type character varying
```

**Fix**:
```sql
-- Odoo 18 JSONB migration for ir_ui_menu.name
-- Run this BEFORE upgrading to Odoo 18:

BEGIN;

-- Backup old name column
ALTER TABLE ir_ui_menu RENAME COLUMN name TO name_old;

-- Create new JSONB column
ALTER TABLE ir_ui_menu ADD COLUMN name jsonb;

-- Migrate data: char → jsonb with 'en_US' key
UPDATE ir_ui_menu SET name = jsonb_build_object('en_US', name_old);

-- Drop old column
ALTER TABLE ir_ui_menu DROP COLUMN name_old;

COMMIT;
```

### Issue 3: View Validation Error (Odoo 18)

**Error**:
```
ValueError: Element 'field[@name='arch']': This element is not expected. Expected is one of ( field[@name='priority'], field[@name='mode'] ).
```

**Fix**:
Edit view XML file and remove `type="xml"` attribute:

```xml
<!-- OLD (Odoo 17) -->
<field name="arch" type="xml">
    <tree>...</tree>
</field>

<!-- NEW (Odoo 18) -->
<field name="arch">
    <tree>...</tree>
</field>
```

### Issue 4: Cron Job Not Running

**Error**: BIR deadline alerts not triggering daily at 8 AM

**Verification**:
```sql
-- Check cron job exists
SELECT id, name, active, nextcall, numbercall
FROM ir_cron
WHERE model = 'ipai.finance.bir_schedule'
  AND name ILIKE '%sync%';

-- Check cron is active
SELECT active FROM ir_cron WHERE model = 'ipai.finance.bir_schedule';
-- Should return 't' (true)
```

**Fix**:
```sql
-- Activate cron job
UPDATE ir_cron SET active = true
WHERE model = 'ipai.finance.bir_schedule'
  AND name ILIKE '%sync%';

-- Manually trigger cron (for testing)
-- Via Odoo shell:
odoo-bin shell -d odoo -c /etc/odoo/odoo.conf
>>> env['ir.cron'].search([('model', '=', 'ipai.finance.bir_schedule')]).method_direct_trigger()
```

### Issue 5: Missing Seed Data After Install

**Error**: No BIR schedule records or logframe entries after installing `ipai_finance_ppm`

**Verification**:
```sql
SELECT COUNT(*) FROM ipai_finance_bir_schedule;
-- Should return 8+ (for current period)

SELECT COUNT(*) FROM ipai_finance_logframe;
-- Should return 12+ (goal/outcome/IM/outputs/activities)
```

**Fix**:
```bash
# Reinstall with --init flag to reload seed data
docker exec -it odoo-accounting odoo-bin \
  -d odoo \
  -i ipai_finance_ppm \
  --init=ipai_finance_ppm \
  --stop-after-init

# Or manually load seed data XML files
docker exec -it odoo-accounting odoo-bin \
  -d odoo \
  --load-language=en_US \
  --load=data/bir_schedule_seed.xml \
  --stop-after-init
```

## Post-Installation Verification

### Comprehensive Verification Script

```bash
#!/bin/bash
# verify_ipai_install.sh

DB="odoo"
PSQL="docker exec -it odoo-db-1 psql -U odoo -d $DB -tAc"

echo "=== IPAI Module Installation Verification ==="

# 1. Check installed modules
echo -e "\n1. Installed IPAI Modules:"
$PSQL "SELECT name, state, latest_version FROM ir_module_module WHERE name LIKE 'ipai_%' AND state = 'installed' ORDER BY name;"

# 2. Check database tables created
echo -e "\n2. IPAI Database Tables:"
$PSQL "SELECT tablename FROM pg_tables WHERE tablename LIKE 'ipai_%' ORDER BY tablename;" | wc -l
echo "tables created"

# 3. Check menus accessible
echo -e "\n3. IPAI Menus:"
$PSQL "SELECT COUNT(*) FROM ir_ui_menu WHERE name::text ILIKE '%ipai%' OR name::text ILIKE '%finance ppm%' OR name::text ILIKE '%bir%';"
echo "menus created"

# 4. Check seed data loaded
echo -e "\n4. Seed Data:"
echo -n "BIR Schedule Records: "
$PSQL "SELECT COUNT(*) FROM ipai_finance_bir_schedule;"
echo -n "Logframe Records: "
$PSQL "SELECT COUNT(*) FROM ipai_finance_logframe;"

# 5. Check cron jobs active
echo -e "\n5. Active Cron Jobs:"
$PSQL "SELECT name, active FROM ir_cron WHERE model LIKE 'ipai%' ORDER BY name;"

# 6. Check security groups created
echo -e "\n6. Security Groups:"
$PSQL "SELECT COUNT(*) FROM res_groups WHERE name ILIKE '%ipai%' OR name ILIKE '%finance%' OR name ILIKE '%bir%';"
echo "groups created"

# 7. Test dashboard accessibility (if on production)
echo -e "\n7. Dashboard Accessibility:"
curl -sf https://odoo.insightpulseai.com/ipai/finance/ppm | grep -q "TBWA Finance PPM Dashboard" && echo "✓ PPM Dashboard accessible" || echo "✗ PPM Dashboard not accessible"

echo -e "\n=== Verification Complete ==="
```

## Next Steps

After successful installation:

1. **Review Security Model**: See [SECURITY_MODEL.md](./SECURITY_MODEL.md) for access control configuration
2. **Configure Settings**: See module-specific READMEs in [modules/](./modules/) for configuration options
3. **Load Demo Data** (optional): For testing, load demo data from `data/*_demo.xml` files
4. **Review Operations**: See [OPERATIONS_RUNBOOK.md](./OPERATIONS_RUNBOOK.md) for daily operations procedures
5. **Monitor Logs**: Check `/var/log/odoo/` for installation warnings or errors

## Support

For installation issues:
1. Check [GitHub Issues](https://github.com/jgtolentino/odoo-ce/issues)
2. Review [CHANGELOG.md](./CHANGELOG.md) for known issues
3. Contact: Jake Tolentino (Finance SSC Manager / Odoo Developer)
