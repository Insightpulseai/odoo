# EE Parity Installation Pack

**Purpose**: Repeatable installation of OCA + IPAI modules for Odoo Enterprise Edition feature parity
**Status**: PRODUCTION-READY
**Last Updated**: 2026-01-28

---

## 1. Overview

This pack provides environment-driven installation of modules that replicate Odoo Enterprise Edition features using:
- **OCA modules**: Community-vetted accounting, UX, and sales extensions
- **IPAI modules**: Custom InsightPulse AI modules (e.g., Mailgun bridge, BIR compliance)

**Philosophy**: Environment variables define the module sets; scripts install them repeatably across dev/staging/production.

---

## 2. Environment Configuration

### A. Module Sets (in `.env`)

The `.env.example` file defines three OCA module categories:

#### Accounting / Finance
OCA "must-have" modules recommended for serious accounting installs:
```bash
ODOO_EE_PARITY_OCA_MODULES_ACCOUNTING="\
account_usability,\
account_asset_management,\
account_chart_update,\
account_financial_report,\
account_reconcile_oca,\
account_reconcile_model_oca,\
account_statement_base,\
currency_rate_update,\
mis_builder,\
mis_builder_budget,\
partner_statement\
"
```

**Purpose**:
- `account_usability`: Enhanced accounting UX
- `account_asset_management`: Fixed asset tracking (replaces EE Asset module)
- `account_financial_report`: Financial statements (replaces EE Financial Reports)
- `account_reconcile_oca`: Bank reconciliation (replaces EE Reconciliation)
- `mis_builder`: Management Information System reports (replaces EE Dashboards)

#### Base / UX / Safety
Standard OCA picks for multi-environment setup and CE enhancement:
```bash
ODOO_EE_PARITY_OCA_MODULES_BASE="\
base_technical_features,\
disable_odoo_online,\
remove_odoo_enterprise,\
web_environment_ribbon,\
web_m2x_options,\
web_responsive\
"
```

**Purpose**:
- `base_technical_features`: Show technical fields to admins
- `disable_odoo_online`: Remove odoo.com integrations
- `remove_odoo_enterprise`: Hide EE upsell messages
- `web_environment_ribbon`: Visual indicator for dev/staging/production
- `web_responsive`: Mobile-friendly backend UI

#### Sales (Optional)
```bash
ODOO_EE_PARITY_OCA_MODULES_SALES="\
portal_sale_order_search,\
sale_delivery_state,\
sale_fixed_discount,\
sale_order_archive\
"
```

#### IPAI Custom Modules
```bash
ODOO_EE_PARITY_IPAI_MODULES="\
ipai_mailgun_bridge\
"
```

**Extend this list** as you add more ipai_* modules (e.g., `ipai_finance_ppm`, `ipai_bir_compliance`).

### B. Container Configuration
```bash
ODOO_CONTAINER=odoo-dev          # Docker service name
ODOO_DB_NAME=odoo_dev            # Database name
POSTGRES_USER=odoo               # PostgreSQL user
```

---

## 3. Installation Scripts

### A. Install/Upgrade Modules

**Script**: `scripts/dev/install-ee-parity-modules.sh`

**Usage**:
```bash
./scripts/dev/install-ee-parity-modules.sh
```

**What it does**:
1. Validates `.env` file exists and required variables are set
2. Normalizes module list (strips spaces, collapses commas)
3. Displays installation plan and prompts for confirmation
4. Verifies Odoo container is running
5. Executes `odoo -d $DB -u $MODULES --stop-after-init`
6. Reports success/failure

**Requirements**:
- `.env` file must exist (copy from `.env.example`)
- Odoo container must be running (`docker compose up -d odoo-dev`)
- OCA addons must be available in `oca-addons/` directory

### B. List Module Status

**Script**: `scripts/dev/list-ee-parity-modules.sh`

**Usage**:
```bash
./scripts/dev/list-ee-parity-modules.sh
```

**What it does**:
1. Queries `ir_module_module` table for all EE-parity modules
2. Displays module name, state, and status icon:
   - ✅ `installed` - Module is active
   - ⬆️ `to upgrade` - Module needs upgrade
   - 📦 `to install` - Module queued for installation
   - ❌ `uninstalled` - Module not installed
3. Shows summary statistics by state

**Sample Output**:
```
╔════════════════════════════════════════════╗
║   EE Parity Modules Status                 ║
╚════════════════════════════════════════════╝

Database: odoo_dev
Container: odoo-dev

        name         |   state    | status
---------------------+------------+--------
 account_usability   | installed  | ✅
 mis_builder         | installed  | ✅
 web_responsive      | installed  | ✅
 ipai_mailgun_bridge | installed  | ✅
 account_asset_mgmt  | uninstalled| ❌
 ...

Summary:
   state    | count
------------+-------
 installed  |   15
 uninstalled|    3
```

---

## 4. Typical Workflow

### First-Time Setup

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Customize .env (adjust ODOO_DB_NAME, POSTGRES_PASSWORD, etc.)
vim .env

# 3. Start Odoo container
./scripts/dev/up.sh

# 4. Check current module status (should show mostly uninstalled)
./scripts/dev/list-ee-parity-modules.sh

# 5. Install EE-parity modules
./scripts/dev/install-ee-parity-modules.sh

# 6. Verify installation (should show all as installed)
./scripts/dev/list-ee-parity-modules.sh
```

### Adding New Modules

To add more modules to the EE-parity pack:

1. **Update `.env`**:
   ```bash
   # Add to existing list
   ODOO_EE_PARITY_IPAI_MODULES="\
   ipai_mailgun_bridge,\
   ipai_finance_ppm,\
   ipai_bir_compliance\
   "
   ```

2. **Run installer**:
   ```bash
   ./scripts/dev/install-ee-parity-modules.sh
   ```

3. **Verify**:
   ```bash
   ./scripts/dev/list-ee-parity-modules.sh
   ```

---

## 5. Deployment to Staging/Production

### Staging Deployment

```bash
# 1. SSH to production droplet
ssh root@178.128.112.214

# 2. Navigate to repo
cd /opt/odoo-ce/repo

# 3. Update .env with staging values
cat >> .env.staging << 'EOF'
ODOO_CONTAINER=odoo-staging
ODOO_DB_NAME=odoo_staging
POSTGRES_USER=odoo
ODOO_EE_PARITY_OCA_MODULES="..."
ODOO_EE_PARITY_IPAI_MODULES="..."
EOF

# 4. Run installer with staging environment
env $(cat .env.staging | xargs) \
  ./scripts/dev/install-ee-parity-modules.sh
```

### Production Deployment

**⚠️ CRITICAL: Always backup database before production module installation**

```bash
# 1. Backup production database
docker exec odoo-db pg_dump -U odoo -d odoo_prod > /backups/odoo_prod_pre_ee_pack_$(date +%Y%m%d_%H%M%S).sql

# 2. Run installer with production environment
ODOO_CONTAINER=odoo-erp-prod \
ODOO_DB_NAME=odoo_prod \
./scripts/dev/install-ee-parity-modules.sh

# 3. Verify installation
ODOO_CONTAINER=odoo-erp-prod \
ODOO_DB_NAME=odoo_prod \
./scripts/dev/list-ee-parity-modules.sh

# 4. Test critical workflows
curl -f https://erp.insightpulseai.net/web/health
```

---

## 6. Rollback Strategy

### Option 1: Database Restore (Recommended)

If module installation causes critical issues, restore from backup:

```bash
# Stop Odoo to prevent DB writes
docker compose stop odoo-erp-prod

# Restore from backup
docker exec -i odoo-db psql -U odoo -d odoo_prod < /backups/odoo_prod_pre_ee_pack_20260128.sql

# Restart Odoo
docker compose start odoo-erp-prod
```

### Option 2: Module Uninstall (Risky)

Uninstalling modules can cause data loss. Only use for non-data-heavy modules:

```bash
docker compose exec odoo-erp-prod \
  odoo -d odoo_prod \
  -u account_usability \
  --uninstall \
  --stop-after-init
```

**Note**: Some modules (like `account_asset_management`) create database tables and stored data. Uninstalling them will delete this data permanently.

### Option 3: Disable Functionality (Safest)

Keep modules installed but disable functionality via:
- Hide menus (via security groups)
- Disable scheduled actions
- Archive configuration records

---

## 7. Extending the Pack

### Adding New OCA Module Categories

To add HR modules:

```bash
# In .env
ODOO_EE_PARITY_OCA_MODULES_HR="\
hr_expense_sequence,\
hr_holidays_validity_date,\
hr_timesheet_sheet\
"

# Update rollup
ODOO_EE_PARITY_OCA_MODULES="\
${ODOO_EE_PARITY_OCA_MODULES_ACCOUNTING},\
${ODOO_EE_PARITY_OCA_MODULES_BASE},\
${ODOO_EE_PARITY_OCA_MODULES_SALES},\
${ODOO_EE_PARITY_OCA_MODULES_HR}\
"
```

### Adding IPAI Modules

As you create more ipai_* modules:

```bash
ODOO_EE_PARITY_IPAI_MODULES="\
ipai_mailgun_bridge,\
ipai_finance_ppm,\
ipai_bir_compliance,\
ipai_enterprise_bridge,\
ipai_approvals,\
ipai_helpdesk\
"
```

---

## 8. Maintenance

### Module Updates

When OCA releases module updates:

```bash
# 1. Update OCA submodules
cd oca-addons
git pull origin 18.0

# 2. Re-run installer (will upgrade modules)
./scripts/dev/install-ee-parity-modules.sh
```

### Deprecation Handling

If an OCA module is deprecated:

1. Remove from `.env` module list
2. Find replacement module
3. Install replacement before uninstalling deprecated module
4. Migrate data if necessary

---

## 9. Troubleshooting

### Module Not Found

**Symptom**: `Module 'account_usability' not found`

**Solution**:
1. Check OCA addons are present: `ls oca-addons/`
2. Verify `addons_path` in `config/odoo.conf` includes `oca-addons/`
3. Restart Odoo container: `docker compose restart odoo-dev`
4. Update module list: `docker compose exec odoo-dev odoo -d odoo_dev --update=all --stop-after-init`

### Dependency Conflicts

**Symptom**: `Module X depends on Y which is not installed`

**Solution**:
1. Add missing dependency to module list in `.env`
2. Re-run installer (dependencies will be installed automatically)

### Installation Hangs

**Symptom**: Installation script hangs for >10 minutes

**Solution**:
1. Check Odoo logs: `docker compose logs odoo-dev`
2. Check for database locks:
   ```sql
   SELECT * FROM pg_locks WHERE NOT granted;
   ```
3. If locked, restart Odoo: `docker compose restart odoo-dev`

---

## 10. Integration with Canonical Documentation

**Reference in `CANONICAL_ODOO_STACK_SNAPSHOT.md`**:

```markdown
## EE Parity Core Modules

**Installation Method**: Environment-driven via `.env` + scripts

**OCA Modules**: Defined in `ODOO_EE_PARITY_OCA_MODULES`
**IPAI Modules**: Defined in `ODOO_EE_PARITY_IPAI_MODULES`

**Install/Upgrade**: `./scripts/dev/install-ee-parity-modules.sh`
**Verify Status**: `./scripts/dev/list-ee-parity-modules.sh`

**Documentation**: `docs/EE_PARITY_INSTALL_PACK.md`
```

---

## 11. References

- **OCA Accounting Must-Haves**: https://odoo-community.org/list-of-must-have-oca-accounting-modules
- **OCA Guidelines**: https://github.com/OCA/odoo-community.org
- **Canonical Stack**: `docs/infra/CANONICAL_ODOO_STACK_SNAPSHOT.md`
- **Dev Sandbox Runbook**: `docs/runbooks/DEV_SANDBOX.md`

---

**Next Steps**: After running the installer, validate EE-parity coverage with:
```bash
./scripts/dev/list-ee-parity-modules.sh
```

All modules should show ✅ `installed` state.
