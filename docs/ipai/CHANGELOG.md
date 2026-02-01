# IPAI Module Suite - Changelog

## Version History

This changelog tracks version history and breaking changes across the IPAI module suite for Odoo CE 18.0.

### Current Release: 18.0.1.1.0 (2025-12-26)

**Modules at v18.0.1.1.0**:
- `ipai_finance_monthly_closing` - Month-end closing workflows with enhanced automation

**Changes**:
- Enhanced month-end closing automation with improved workflow states
- Added multi-agency approval routing for month-end tasks
- Improved integration with BIR compliance schedules

### Current Release: 18.0.1.0.1 (2025-12-26)

**Modules at v18.0.1.0.1**:
- `ipai_finance_ppm` - Finance Project Portfolio Management (Logframe + BIR Schedule + ECharts)

**Changes**:
- Fixed ECharts dashboard rendering issues
- Enhanced BIR schedule auto-task creation logic
- Improved logframe hierarchy display in PPM dashboard

### Current Release: 18.0.1.0.0 (2025-12-26)

**Modules at v18.0.1.0.0** (26 modules):

**Finance Layer** (14 modules):
- `ipai_bir_compliance` - Tax Shield (Philippines BIR compliance)
- `ipai_clarity_ppm_parity` - Clarity PPM feature parity
- `ipai_close_orchestration` - Close cycle orchestration engine
- `ipai_finance_bir_compliance` - BIR compliance automation (1601-C, 2550Q, 1702-RT)
- `ipai_finance_month_end` - Month-end closing templates and generators
- `ipai_finance_ppm_closing` - PPM closing generator
- `ipai_finance_ppm_dashboard` - ECharts-based PPM dashboards
- `ipai_finance_ppm_tdi` - Transaction data ingestion for analytics
- `ipai_finance_project_hybrid` - Hybrid project/finance integration (IM1/IM2)
- `ipai_ppm` - Portfolio & Program Management
- `ipai_ppm_a1` - A1 Control Center (logframe + BIR schedule + task automation)
- `ipai_ppm_monthly_close` - Monthly close scheduler

**Other/Operations Layer** (11 modules):
- `ipai_advisor` - Azure Advisor-style recommendations engine
- `ipai_assets` - Equipment/asset checkout tracking (Cheqroom parity)
- `ipai_custom_routes` - Custom URL routing
- `ipai_default_home` - Default home page customization
- `ipai_dev_studio_base` - Dev studio base module
- `ipai_equipment` - Equipment management
- `ipai_expense` - Expense & Travel (PH tax rules)
- `ipai_master_control` - Work intake and master control
- `ipai_portal_fix` - Portal fixes for Odoo 18
- `ipai_project_program` - Program + IM projects
- `ipai_srm` - Supplier Relationship Management

**Platform/Utilities Layer** (2 modules):
- `ipai_ce_branding` - InsightPulse AI branding customization
- `ipai_ce_cleaner` - CE cleaner (removes Enterprise/IAP dependencies)

**Industry Layer** (2 modules):
- `ipai_industry_accounting_firm` - Accounting firm operations
- `ipai_industry_marketing_agency` - Marketing agency operations

**WorkOS Layer** (1 module):
- `ipai_workspace_core` - Workspace core (blocks, pages, databases)

**Changes**:
- Initial stable release for Odoo 18.0
- All modules tested and verified on production database
- OCA compliance validated for all modules
- PostgreSQL 15+ compatibility confirmed

### Legacy Versions

**v1.2.0** (1 module):
- `ipai_ocr_expense` - OCR expense automation (deprecated - superseded by ipai_expense)

**v1.0.0** (1 module):
- `ipai_ocr_webhook` - OCR webhook handler (deprecated - superseded by ipai_expense)

---

## Breaking Changes by Odoo Version

### Odoo 17 → Odoo 18 Migration

#### Critical Breaking Changes

**1. JSONB Name Fields**

**Issue**: `ir_ui_menu.name` and `ir_module_module.shortdesc` changed from `char` to `jsonb`

**Impact**: All menu definitions and module metadata must be migrated

**Migration Script**:
```sql
-- Odoo 18 JSONB migration for ir_ui_menu.name
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

**IPAI Modules Affected**: All modules with menu definitions (30/30 modules)

**Verification**:
```sql
-- Verify JSONB structure
SELECT id, name FROM ir_ui_menu WHERE name::text ILIKE '%ipai%' LIMIT 5;
-- Expected: {"en_US": "Menu Name"}
```

---

**2. View XML Tag Changes**

**Issue**: Deprecated `<field name="arch" type="xml">` → use `<field name="arch">`

**Impact**: All view definitions must remove `type="xml"` attribute

**Example Fix**:
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

**IPAI Modules Affected**: All modules with view definitions (30/30 modules)

**Verification**:
```bash
# Check for deprecated syntax
grep -r 'type="xml"' addons/ipai/*/views/*.xml
# Should return no results after migration
```

---

**3. Cron Job Field Removal**

**Issue**: `ir.cron.numbercall` field removed in Odoo 18

**Impact**: All cron job definitions setting `numbercall` will fail

**Example Fix**:
```xml
<!-- REMOVE THIS LINE: -->
<field name="numbercall">-1</field>
```

**IPAI Modules Affected**:
- `ipai_tbwa_finance` - **CRITICAL**: Must fix `data/ir_cron.xml` before installation
- `ipai_finance_bir_compliance` - BIR deadline sync cron
- `ipai_advisor` - Recommendation refresh cron
- All modules with scheduled actions

**Migration Procedure**:
```bash
# 1. Find all cron definitions with numbercall
grep -r "numbercall" addons/ipai/*/data/ir_cron*.xml

# 2. Edit each file and remove numbercall field
# Example: addons/ipai_tbwa_finance/data/ir_cron.xml
$EDITOR addons/ipai_tbwa_finance/data/ir_cron.xml

# 3. Commit fix
git add addons/ipai_tbwa_finance/data/ir_cron.xml
git commit -m "fix(tbwa_finance): drop ir.cron numbercall for Odoo 18"
```

**Verification**:
```sql
-- Verify cron jobs installed correctly
SELECT id, name, active, nextcall, numbercall
FROM ir_cron
WHERE model LIKE 'ipai%';
-- Should return ERROR if numbercall field still referenced
```

---

**4. Python Version Requirement**

**Issue**: Odoo 18 drops Python 3.10 support, requires Python 3.11+

**Impact**: Production servers must upgrade Python version

**Migration Steps**:
```bash
# 1. Check current Python version
python3 --version

# 2. Install Python 3.11 (Ubuntu 22.04)
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev

# 3. Update system default (optional)
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# 4. Reinstall Odoo dependencies
pip3 install -r requirements.txt
```

**IPAI Modules Affected**: All modules (runtime environment)

**Verification**:
```bash
# Verify Odoo runs on Python 3.11+
odoo-bin --version
# Should show Odoo 18.0 with Python 3.11+
```

---

**5. Widget and Field Attribute Changes**

**Issue**: Various widget and field attributes deprecated or renamed

**Common Changes**:
- `widget="monetary"` → requires `currency_field` attribute
- `widget="many2many_tags"` → `widget="many2many_checkboxes"` (for forms)
- `attrs` attribute → replaced by `invisible`, `readonly`, `required` attributes

**Example Migration**:
```xml
<!-- OLD (Odoo 17) -->
<field name="amount" widget="monetary" attrs="{'invisible': [('state', '=', 'draft')]}"/>

<!-- NEW (Odoo 18) -->
<field name="amount" widget="monetary" currency_field="currency_id" invisible="state == 'draft'"/>
```

**IPAI Modules Affected**: All modules with custom views (especially Finance modules)

**Verification**:
```bash
# Check for deprecated attrs usage
grep -r "attrs=" addons/ipai/*/views/*.xml | grep -v "<!-- OLD"
# Review and update remaining occurrences
```

---

#### Non-Breaking Changes

**1. Performance Improvements**

**Odoo 18 Performance Enhancements**:
- Improved ORM query optimization (30-40% faster bulk operations)
- Enhanced PostgreSQL connection pooling
- Better Redis session caching

**IPAI Modules Benefiting**:
- `ipai_finance_ppm` - Faster logframe and BIR schedule queries
- `ipai_finance_ppm_dashboard` - Improved ECharts data loading
- `ipai_expense` - Faster OCR expense batch processing

**No Code Changes Required**: Automatic performance gains

---

**2. Security Enhancements**

**Odoo 18 Security Features**:
- Stricter CSRF protection
- Enhanced RLS policy enforcement
- Improved password hashing (bcrypt → Argon2)

**IPAI Modules Affected**:
- All modules with security groups and record rules
- Enhanced protection with zero configuration changes

---

**3. UI/UX Improvements**

**Odoo 18 Frontend Updates**:
- Modernized form layouts
- Improved mobile responsiveness
- Enhanced kanban card designs

**IPAI Modules Benefiting**:
- `ipai_assets` - Better mobile asset checkout experience
- `ipai_expense` - Improved expense approval workflows
- `ipai_workspace_core` - Enhanced collaborative editing UI

**No Code Changes Required**: Automatic UI improvements

---

## Migration Notes

### Pre-Migration Checklist

**Critical Steps** (MUST complete before Odoo 18 upgrade):

1. **Backup Production Database**:
   ```bash
   pg_dump -h <host> -U odoo -d odoo > odoo17_backup_$(date +%Y%m%d).sql
   ```

2. **Fix Cron Job Definitions**:
   ```bash
   # Find all numbercall references
   grep -r "numbercall" addons/ipai/*/data/ir_cron*.xml

   # Remove numbercall field from all cron XML files
   ```

3. **Remove Deprecated View Attributes**:
   ```bash
   # Find deprecated type="xml"
   grep -r 'type="xml"' addons/ipai/*/views/*.xml

   # Remove type="xml" from all view definitions
   ```

4. **Test Modules in Staging**:
   ```bash
   # Install all IPAI modules in fresh Odoo 18 database
   odoo -d odoo18_test -i ipai_ce_cleaner --stop-after-init
   # Follow Phase 1-7 from INSTALLATION.md
   ```

5. **Verify JSONB Migration**:
   ```sql
   -- Check ir_ui_menu.name structure
   SELECT id, name FROM ir_ui_menu LIMIT 5;
   -- Should return JSONB: {"en_US": "Menu Name"}
   ```

---

### Post-Migration Verification

**Required Verification Steps** (After Odoo 18 upgrade):

1. **Module Installation Check**:
   ```sql
   SELECT name, state, latest_version
   FROM ir_module_module
   WHERE name LIKE 'ipai_%'
   AND state != 'installed'
   ORDER BY name;
   -- Should return 0 rows (all installed)
   ```

2. **Cron Jobs Active**:
   ```sql
   SELECT id, name, active, nextcall
   FROM ir_cron
   WHERE model LIKE 'ipai%'
   AND active = false;
   -- Should return 0 rows (all active)
   ```

3. **Menu Accessibility**:
   ```sql
   SELECT COUNT(*)
   FROM ir_ui_menu
   WHERE name::text ILIKE '%ipai%';
   -- Should match expected menu count
   ```

4. **View Validation**:
   ```bash
   # Check Odoo logs for view errors
   grep -i "error" /var/log/odoo/odoo.log | grep -i "view"
   # Should return no view-related errors
   ```

5. **Data Integrity**:
   ```sql
   -- Finance PPM: Verify logframe + BIR schedule
   SELECT COUNT(*) FROM ipai_finance_logframe;  -- Should return 12+
   SELECT COUNT(*) FROM ipai_finance_bir_schedule;  -- Should return 8+

   -- Expense: Verify expenses retained
   SELECT COUNT(*) FROM hr_expense WHERE create_date >= '2025-01-01';

   -- Projects: Verify tasks retained
   SELECT COUNT(*) FROM project_task WHERE create_date >= '2025-01-01';
   ```

---

### Rollback Procedure

**If Migration Fails**:

1. **Stop Odoo 18 Instance**:
   ```bash
   docker-compose down
   ```

2. **Restore Odoo 17 Database**:
   ```bash
   psql -U odoo -d odoo < odoo17_backup_$(date +%Y%m%d).sql
   ```

3. **Revert to Odoo 17 Docker Image**:
   ```bash
   # Edit docker-compose.yml
   # Change image: odoo:18.0 → odoo:17.0
   docker-compose up -d
   ```

4. **Verify Rollback**:
   ```bash
   curl -s http://localhost:8069/web/database/manager | grep "Odoo 17"
   ```

---

## Known Issues

### Issue 1: ipai_tbwa_finance - Cron Numbercall Field

**Status**: 🚨 CRITICAL - Requires fix before installation

**Affected Version**: All versions prior to fix

**Issue**: Module uses deprecated `ir.cron.numbercall` field, causing installation failure

**Error Message**:
```
odoo.exceptions.ValidationError: Invalid field `numbercall` on `ir.cron`
```

**Fix**:
```bash
# Edit addons/ipai_tbwa_finance/data/ir_cron.xml
# Remove: <field name="numbercall">-1</field>

git add addons/ipai_tbwa_finance/data/ir_cron.xml
git commit -m "fix(tbwa_finance): drop ir.cron numbercall for Odoo 18"
git push origin main
```

**Verification**:
```bash
# Reinstall module after fix
odoo -d production -i ipai_tbwa_finance --stop-after-init

# Check cron job installed
psql "$POSTGRES_URL" -c "SELECT name, active FROM ir_cron WHERE name ILIKE '%tbwa%';"
```

---

### Issue 2: Visual Parity SSIM Drops After Odoo 18 Upgrade

**Status**: ⚠️ Known - Monitor after upgrade

**Affected Modules**: All modules with custom views

**Issue**: UI layout changes in Odoo 18 may cause SSIM score drops >0.02

**Expected Impact**: Non-functional visual regression (layout shifts, font changes)

**Mitigation**:
```bash
# 1. Capture new baselines after Odoo 18 upgrade
node scripts/snap.js --routes="/expenses,/tasks,/finance/ppm" --base-url="https://odoo.insightpulseai.com"

# 2. Update baselines in Supabase
node scripts/update_baselines.js --odoo-version="18.0"

# 3. Re-run SSIM verification
node scripts/ssim.js --routes="/expenses,/tasks,/finance/ppm" --threshold-mobile=0.97 --threshold-desktop=0.98
```

---

### Issue 3: Multi-Agency Security - Employee ID Hardcoding

**Status**: ✅ RESOLVED - Use res.users context

**Affected Modules**: `ipai_expense`, `ipai_finance_ppm`, `ipai_bir_compliance`

**Issue**: Some modules hardcoded employee IDs (RIM, CKVC, BOM, etc.) instead of using `res.users` context

**Fix Applied** (v18.0.1.0.0):
- All employee references now use `self.env.user.employee_id`
- Record rules use `[('employee_id.user_id', '=', user.id)]`
- No hardcoded employee codes

**Verification**:
```bash
# Check for hardcoded employee IDs
grep -r "CKVC\|RIM\|BOM" addons/ipai/*/models/*.py
# Should return no matches in Python code
```

---

## Version Numbering Scheme

**Format**: `{ODOO_VERSION}.{MAJOR}.{MINOR}.{PATCH}`

**Example**: `18.0.1.0.0`
- `18.0` - Odoo major version
- `1` - IPAI major version (breaking changes)
- `0` - IPAI minor version (new features, backward compatible)
- `0` - IPAI patch version (bug fixes)

**Version Increment Rules**:
- **Patch** (`18.0.1.0.X`) - Bug fixes, no new features, backward compatible
- **Minor** (`18.0.1.X.0`) - New features, backward compatible, no breaking changes
- **Major** (`18.0.X.0.0`) - Breaking changes, deprecations, major refactoring
- **Odoo** (`X.0.1.0.0`) - Odoo version upgrade (17→18, etc.)

---

## Support and Documentation

**Primary Maintainer**: Jake Tolentino (Finance SSC Manager / Odoo Developer)
**Organization**: InsightPulse AI (TBWA)
**Repository**: https://github.com/jgtolentino/odoo-ce
**Documentation**: `docs/ipai/` (this directory)

**For Issues**:
1. Check [INSTALLATION.md](./INSTALLATION.md) for troubleshooting
2. Review [OPERATIONS_RUNBOOK.md](./OPERATIONS_RUNBOOK.md) for operational procedures
3. Open issue in GitHub repository with:
   - Module name and version
   - Odoo version
   - Error message and stack trace
   - Steps to reproduce

**For Migration Help**:
1. Review migration notes above
2. Test in staging environment first
3. Follow pre-migration checklist completely
4. Keep Odoo 17 backups until Odoo 18 verified stable

---

## Upcoming Releases

### Planned for v18.0.2.0.0

**New Features**:
- `ipai_finance_ppm_realtime` - Real-time BIR deadline notifications via WebSocket
- `ipai_workspace_collab_v2` - Enhanced collaborative editing with conflict resolution
- `ipai_finance_analytics` - Advanced analytics dashboards for finance operations

**Improvements**:
- Enhanced multi-agency support with 20+ employees
- Improved mobile responsiveness across all Finance modules
- Performance optimization for large dataset operations (>100K records)

**Breaking Changes**:
- None planned (backward compatible)

**Target Release**: Q1 2026

---

**Last Updated**: 2025-12-26
**Document Version**: 1.0.0
