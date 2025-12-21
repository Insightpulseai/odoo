# OCA Module Installation Guide for Finance PPM

**Target Database**: `odoo_accounting`
**Odoo Version**: 18.0
**Droplet**: `159.223.75.148` (odoo-erp-prod)

---

## Current Status

**Verified**: All 8 OCA modules are **NOT INSTALLED** on production

| Module | Status | Purpose |
|--------|--------|---------|
| `account_financial_report` | ❌ NOT FOUND | Trial balance, aging reports |
| `account_asset_management` | ❌ NOT FOUND | Fixed assets & depreciation |
| `account_cutoff_accrual_order_base` | ❌ NOT FOUND | Accrual entries |
| `account_move_reversal` | ❌ NOT FOUND | JE reversals |
| `hr_expense_advance_clearing` | ❌ NOT FOUND | CA liquidations |
| `account_multicurrency_revaluation` | ❌ NOT FOUND | FX revaluation |
| `account_intercompany` | ❌ NOT FOUND | IC transactions |
| `project_wip` | ❌ NOT FOUND | WIP tracking |

---

## Installation Steps

### Step 1: Download OCA Modules from GitHub

```bash
# SSH to production droplet
ssh root@159.223.75.148

# Create OCA modules directory
mkdir -p /root/oca-modules && cd /root/oca-modules

# Clone OCA repositories (18.0 branch)
git clone -b 18.0 --depth=1 https://github.com/OCA/account-financial-reporting.git
git clone -b 18.0 --depth=1 https://github.com/OCA/account-financial-tools.git
git clone -b 18.0 --depth=1 https://github.com/OCA/account-closing.git
git clone -b 18.0 --depth=1 https://github.com/OCA/hr-expense.git
git clone -b 18.0 --depth=1 https://github.com/OCA/project.git
```

**OCA Repository Mapping**:

| Module | Repository | Branch |
|--------|------------|--------|
| `account_financial_report` | `account-financial-reporting` | 18.0 |
| `account_asset_management` | `account-financial-tools` | 18.0 |
| `account_cutoff_accrual_order_base` | `account-closing` | 18.0 |
| `account_move_reversal` | `account-financial-tools` | 18.0 |
| `hr_expense_advance_clearing` | `hr-expense` | 18.0 |
| `account_multicurrency_revaluation` | `account-closing` | 18.0 |
| `account_intercompany` | `account-financial-tools` | 18.0 |
| `project_wip` | `project` | 18.0 |

---

### Step 2: Copy Modules to Odoo Addons Path

```bash
# Find current addons path
docker exec -i odoo-accounting grep -E "^addons_path" /etc/odoo/odoo.conf

# Expected output: addons_path = /mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons

# Copy modules to extra-addons
cp -r /root/oca-modules/account-financial-reporting/account_financial_report /mnt/extra-addons/
cp -r /root/oca-modules/account-financial-tools/account_asset_management /mnt/extra-addons/
cp -r /root/oca-modules/account-closing/account_cutoff_accrual_order_base /mnt/extra-addons/
cp -r /root/oca-modules/account-financial-tools/account_move_reversal /mnt/extra-addons/
cp -r /root/oca-modules/hr-expense/hr_expense_advance_clearing /mnt/extra-addons/
cp -r /root/oca-modules/account-closing/account_multicurrency_revaluation /mnt/extra-addons/
cp -r /root/oca-modules/account-financial-tools/account_intercompany /mnt/extra-addons/
cp -r /root/oca-modules/project/project_wip /mnt/extra-addons/

# Verify files copied
ls -la /mnt/extra-addons/ | grep -E "account_|hr_expense|project_wip"
```

---

### Step 3: Update Odoo Module List

```bash
# Restart Odoo to detect new modules
docker restart odoo-accounting

# Wait 30 seconds for startup
sleep 30

# Update module list via Odoo CLI
docker exec -i odoo-accounting odoo -d odoo_accounting --update=base --stop-after-init

# Or via web UI:
# 1. Navigate to: http://159.223.75.148:8071/web
# 2. Login as admin
# 3. Go to: Apps → Update Apps List
# 4. Refresh browser
```

---

### Step 4: Install OCA Modules (Sequential Order)

**Installation Order** (respect dependencies):

```bash
# 1. Core accounting modules (no dependencies)
docker exec -i odoo-accounting odoo -d odoo_accounting -i account_financial_report --stop-after-init
docker exec -i odoo-accounting odoo -d odoo_accounting -i account_asset_management --stop-after-init
docker exec -i odoo-accounting odoo -d odoo_accounting -i account_move_reversal --stop-after-init

# 2. Closing modules (depend on core)
docker exec -i odoo-accounting odoo -d odoo_accounting -i account_cutoff_accrual_order_base --stop-after-init
docker exec -i odoo-accounting odoo -d odoo_accounting -i account_multicurrency_revaluation --stop-after-init

# 3. HR expense modules
docker exec -i odoo-accounting odoo -d odoo_accounting -i hr_expense_advance_clearing --stop-after-init

# 4. Intercompany and project modules
docker exec -i odoo-accounting odoo -d odoo_accounting -i account_intercompany --stop-after-init
docker exec -i odoo-accounting odoo -d odoo_accounting -i project_wip --stop-after-init

# Restart to ensure all modules loaded
docker restart odoo-accounting
```

**Alternative**: Install all at once (riskier, harder to debug)

```bash
docker exec -i odoo-accounting odoo -d odoo_accounting \
  -i account_financial_report,account_asset_management,account_cutoff_accrual_order_base,account_move_reversal,hr_expense_advance_clearing,account_multicurrency_revaluation,account_intercompany,project_wip \
  --stop-after-init

docker restart odoo-accounting
```

---

### Step 5: Verify Installation

```bash
# Run verification script
python3 /tmp/check_finance_ppm_modules.py

# Expected output for odoo_accounting database:
# ✅ account_financial_report                 installed
# ✅ account_asset_management                 installed
# ✅ account_cutoff_accrual_order_base        installed
# ✅ account_move_reversal                    installed
# ✅ hr_expense_advance_clearing              installed
# ✅ account_multicurrency_revaluation        installed
# ✅ account_intercompany                     installed
# ✅ project_wip                              installed
#
# Summary: 8/8 installed, 0 missing
```

**Manual Verification via UI**:

1. Navigate to: `http://159.223.75.148:8071/web` (odoo_accounting)
2. Login as `admin`
3. Go to: **Apps** → Remove "Apps" filter → Show all modules
4. Search for each OCA module name
5. Verify state shows: **Installed** (green checkmark)

---

### Step 6: Install Finance PPM Module

**After OCA modules are installed**:

```bash
# Copy Finance PPM module to addons
cp -r /root/odoo-ce/addons/ipai_finance_ppm /mnt/extra-addons/

# Install module
docker exec -i odoo-accounting odoo -d odoo_accounting -i ipai_finance_ppm --stop-after-init

# Restart
docker restart odoo-accounting
```

**Verify Finance PPM Module**:

```bash
# Check module installation
docker exec -i odoo-accounting odoo -d odoo_accounting -c /etc/odoo/odoo.conf \
  --db-filter=odoo_accounting \
  --xmlrpc-port=8069 \
  -d odoo_accounting \
  -u ipai_finance_ppm
```

---

## Troubleshooting

### Issue: Module Not Found After Copy

**Symptom**: Module shows "NOT FOUND" even after copying to `/mnt/extra-addons/`

**Solutions**:
1. Verify addons_path includes `/mnt/extra-addons/`
   ```bash
   docker exec -i odoo-accounting grep addons_path /etc/odoo/odoo.conf
   ```

2. Update module list
   ```bash
   docker exec -i odoo-accounting odoo -d odoo_accounting --update=base --stop-after-init
   ```

3. Check file permissions
   ```bash
   ls -la /mnt/extra-addons/ | head -20
   # Should show odoo:odoo ownership
   ```

4. Restart container
   ```bash
   docker restart odoo-accounting
   ```

---

### Issue: Dependency Errors During Installation

**Symptom**: Error like "Module 'X' depends on unmet dependency 'Y'"

**Solutions**:
1. Install dependencies first (see installation order above)
2. Check `__manifest__.py` in module for exact dependency list
3. Search OCA repos for missing dependency modules
4. Install missing dependency before retrying

---

### Issue: Database Migration Errors

**Symptom**: Installation fails with SQL errors or constraint violations

**Solutions**:
1. Backup database before installation:
   ```bash
   docker exec -i odoo-postgres pg_dump -U odoo odoo_accounting > /root/backup_odoo_accounting_$(date +%Y%m%d_%H%M%S).sql
   ```

2. Check Odoo logs for specific error:
   ```bash
   docker logs odoo-accounting --tail=100
   ```

3. If critical error, restore backup and retry:
   ```bash
   docker exec -i odoo-postgres psql -U odoo -d odoo_accounting < /root/backup_odoo_accounting_YYYYMMDD_HHMMSS.sql
   ```

---

### Issue: Container Won't Start After Module Installation

**Symptom**: `docker ps` doesn't show `odoo-accounting` container running

**Solutions**:
1. Check container logs:
   ```bash
   docker logs odoo-accounting --tail=200
   ```

2. Start container manually with debugging:
   ```bash
   docker start odoo-accounting
   docker logs -f odoo-accounting
   ```

3. If persistent failure, remove problematic module from addons_path temporarily

---

## Post-Installation Tasks

### 1. Create Month-End Closing Test Period

```bash
# Navigate to Odoo UI
# Accounting → Month-End → Closing Periods
# Click: Create
# Set Period: December 2025
# Click: Generate Tasks
# Verify: 36 tasks created (Seq 1-36, Phases I-IV)
```

### 2. Configure Philippine Holidays

```bash
# Navigate to: Accounting → Configuration → Philippine Holidays
# Import holidays from: docs/finance-ppm/month_end_schedule_2025_12.csv
# OR manually create for 2025-2026:
# - 2025-12-25 (Christmas Day)
# - 2025-12-30 (Rizal Day)
# - 2025-12-31 (Last Day of Year)
# - 2026-01-01 (New Year's Day)
```

### 3. Assign Employees to Tasks

```bash
# Create res.users for:
# - CKVC (Finance Director)
# - RIM (Finance Supervisor)
# - BOM (Senior Finance Manager)
# - JPAL, JLI, LAS, RMQB, JAP, JOL, JRMO (Finance Analysts)
#
# Assign to month-end tasks via RACI fields:
# - Prep By
# - Review By
# - Approve By
```

### 4. Test Task Workflow

```bash
# Test complete RACI workflow for one task:
# 1. Mark "Prep Done" → state changes to "In Progress"
# 2. Mark "Review Done" → state changes to "Review"
# 3. Mark "Approve Done" → state changes to "Done"
# 4. Verify completion % updates in closing period
```

---

## Acceptance Gates

✅ **All 8 OCA modules installed** in `odoo_accounting` database
✅ **Finance PPM module (`ipai_finance_ppm`) installed** successfully
✅ **36 task templates** seeded in database
✅ **Philippine holidays** loaded for 2025-2026
✅ **Test closing period** generated with all 36 tasks
✅ **RACI workflow** tested end-to-end for at least 1 task
✅ **Dashboard accessible** at: Accounting → Month-End → Closing Periods

---

## Quick Reference Commands

```bash
# SSH to droplet
ssh root@159.223.75.148

# Check Odoo containers
docker ps | grep odoo

# View accounting container logs
docker logs odoo-accounting --tail=100 -f

# Restart accounting container
docker restart odoo-accounting

# Access database directly
docker exec -i odoo-postgres psql -U odoo -d odoo_accounting

# Update module list
docker exec -i odoo-accounting odoo -d odoo_accounting --update=base --stop-after-init

# Install single module
docker exec -i odoo-accounting odoo -d odoo_accounting -i <module_name> --stop-after-init

# Check module installation status
python3 /tmp/check_finance_ppm_modules.py
```

---

**Version**: 1.0.0
**Last Updated**: 2025-12-21
**Target Odoo**: 18.0
**Target Database**: odoo_accounting
