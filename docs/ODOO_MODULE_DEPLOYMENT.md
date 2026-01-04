# Odoo Module Deployment Guide

**Purpose**: Comprehensive guide for deploying Odoo 18.0 CE modules with proper install vs upgrade detection

**Last Updated**: 2026-01-04

---

## Critical Concepts

### Install vs Upgrade

**Install (`-i`)**: Use when module is NOT in database or state is `uninstalled`
```bash
odoo -c /etc/odoo/odoo.conf -d production -i ipai_platform_theme --stop-after-init
```

**Upgrade (`-u`)**: Use when module state is `installed` or `to upgrade`
```bash
odoo -c /etc/odoo/odoo.conf -d production -u ipai_platform_theme --stop-after-init
```

**Common Error**: Clicking "Upgrade" on an uninstalled module
```
Error: Cannot upgrade module 'ipai_platform_theme' - module is not installed
```
**Fix**: Install first, then upgrade on subsequent deployments

### Display Name vs Technical Name

- **Display Name**: "IPAI Platform – Theme Tokens" (what you see in UI)
- **Technical Name**: `ipai_platform_theme` (folder name, used in CLI)

Always use technical name for CLI operations.

---

## Prerequisites

### Access Requirements
- SSH access to production droplet: `ssh root@159.223.75.148`
- Docker container running: `odoo-erp-prod`
- Database name: `odoo` (or `production` depending on environment)
- Odoo config: `/etc/odoo/odoo.conf`

### Required Scripts
- `scripts/check_module_status.sh` - Check module database state
- `scripts/deploy_odoo_smart.sh` - Smart deploy with auto-detection
- `scripts/deploy_odoo_upgrade.sh` - Legacy upgrade-only script

---

## Deployment Workflows

### Workflow 1: Check Module Status (Always Start Here)

```bash
# Check single module
ssh root@159.223.75.148
docker exec -i odoo-erp-prod bash -lc "
  psql -U odoo -d odoo -c \"
    SELECT name, state, latest_version
    FROM ir_module_module
    WHERE name = 'ipai_platform_theme';
  \"
"

# Check multiple modules using helper script
ODOO_MODULES=ipai_platform_theme,ipai_finance_ppm,ipai_finance_ppm_umbrella \
  ./scripts/check_module_status.sh
```

**Output Example**:
```
================================================================================
Module                                   State           Version
================================================================================
ipai_platform_theme                      📦 uninstalled  18.0.1.0.0
ipai_finance_ppm                         ✅ installed    18.0.1.0.0
ipai_finance_ppm_umbrella                ✅ installed    1.0.0
================================================================================
```

**Legend**:
- ✅ `installed` → Use `-u` (upgrade)
- 📦 `uninstalled` → Use `-i` (install)
- ⏳ `to install` → Already queued for install
- ⬆️ `to upgrade` → Already queued for upgrade
- ⚠️ Other states → Check manually

### Workflow 2: Smart Deploy (Recommended)

Auto-detects install vs upgrade:

```bash
# Deploy single module
ODOO_MODULES=ipai_platform_theme ./scripts/deploy_odoo_smart.sh

# Deploy multiple modules
ODOO_MODULES=ipai_finance_ppm,ipai_finance_ppm_umbrella ./scripts/deploy_odoo_smart.sh

# Dry-run (shows what would happen without executing)
ODOO_MODULES=ipai_platform_theme ./scripts/deploy_odoo_smart.sh --dry-run
```

**What it does**:
1. Queries `ir_module_module` for each module
2. Separates into INSTALL list and UPGRADE list
3. Runs `odoo -i <install-list>` for new modules
4. Runs `odoo -u <upgrade-list>` for existing modules
5. Restarts container
6. Shows logs

### Workflow 3: Manual Install (First-Time Deployment)

When deploying a module for the first time:

```bash
ssh root@159.223.75.148

# Single module install
docker exec -i odoo-erp-prod bash -lc "
  odoo -c /etc/odoo/odoo.conf -d odoo \
    -i ipai_platform_theme --stop-after-init
"

# Multiple modules install (comma-separated, no spaces)
docker exec -i odoo-erp-prod bash -lc "
  odoo -c /etc/odoo/odoo.conf -d odoo \
    -i ipai_finance_ppm,ipai_finance_ppm_umbrella --stop-after-init
"

# Restart container
docker restart odoo-erp-prod

# Check logs
docker logs --tail=200 odoo-erp-prod
```

### Workflow 4: Manual Upgrade (Existing Modules)

When updating code for already-installed modules:

```bash
ssh root@159.223.75.148

# Single module upgrade
docker exec -i odoo-erp-prod bash -lc "
  odoo -c /etc/odoo/odoo.conf -d odoo \
    -u ipai_platform_theme --stop-after-init
"

# Multiple modules upgrade
docker exec -i odoo-erp-prod bash -lc "
  odoo -c /etc/odoo/odoo.conf -d odoo \
    -u ipai_finance_ppm,ipai_finance_ppm_umbrella --stop-after-init
"

# Restart container
docker restart odoo-erp-prod

# Check logs
docker logs --tail=200 odoo-erp-prod
```

---

## Verification Steps

### Step 1: Check Installation Status

```bash
# Via CLI
docker exec -i odoo-erp-prod bash -lc "
  psql -U odoo -d odoo -c \"
    SELECT name, state, latest_version
    FROM ir_module_module
    WHERE name IN ('ipai_platform_theme', 'ipai_finance_ppm');
  \"
"

# Expected output for successful install:
#        name         |   state   | latest_version
# --------------------+-----------+----------------
# ipai_platform_theme | installed | 18.0.1.0.0
# ipai_finance_ppm    | installed | 18.0.1.0.0
```

### Step 2: Check Odoo Logs

```bash
# Last 200 lines
docker logs --tail=200 odoo-erp-prod

# Follow live logs
docker logs -f odoo-erp-prod

# Search for errors
docker logs odoo-erp-prod 2>&1 | grep -i "error\|warning\|traceback"
```

**Success indicators**:
```
INFO odoo odoo.modules.loading: Modules loaded.
INFO odoo odoo.modules.registry: Registry loaded in X.XXs
```

**Failure indicators**:
```
ERROR odoo odoo.modules.loading: Module ipai_platform_theme: loading failed
Traceback (most recent call last):
```

### Step 3: Check UI (Optional)

1. Login to Odoo: `https://erp.insightpulseai.net`
2. Go to Apps menu
3. Search for module by technical name (e.g., `ipai_platform_theme`)
4. Should show green checkmark with "Installed" status

### Step 4: Verify Dependencies

Check that all dependency modules are also installed:

```bash
# Example: ipai_finance_ppm_umbrella depends on ipai_finance_ppm
docker exec -i odoo-erp-prod bash -lc "
  psql -U odoo -d odoo -c \"
    SELECT
      m1.name as module,
      m1.state,
      d.name as depends_on,
      m2.state as dependency_state
    FROM ir_module_module m1
    JOIN ir_module_module_dependency d ON d.module_id = m1.id
    LEFT JOIN ir_module_module m2 ON m2.name = d.name
    WHERE m1.name = 'ipai_finance_ppm_umbrella';
  \"
"
```

**Expected**: All dependencies should have `state = 'installed'`

---

## Common Issues & Fixes

### Issue 1: "Module not found in module list"

**Symptom**:
```
⚠️  ipai_platform_theme: not found in module list (will attempt install)
```

**Cause**: Module folder not in `addons_path` or Odoo hasn't scanned it

**Fix**:
```bash
# Check if module folder exists
ls -la /opt/odoo-ce/addons/ipai_platform_theme/

# Check addons_path in config
docker exec -i odoo-erp-prod cat /etc/odoo/odoo.conf | grep addons_path

# Update Apps List in Odoo UI
# Settings → Apps → Update Apps List

# Or via CLI
docker exec -i odoo-erp-prod bash -lc "
  odoo -c /etc/odoo/odoo.conf -d odoo --update=all --stop-after-init
"
```

### Issue 2: "Cannot upgrade module - not installed"

**Symptom**:
```
ERROR odoo odoo.modules.loading: Cannot upgrade module 'ipai_platform_theme' - module is not installed
```

**Cause**: Clicked "Upgrade" button on uninstalled module

**Fix**:
```bash
# Option A: Install via UI
# Apps → Search "ipai_platform_theme" → Click "Install"

# Option B: Install via CLI
docker exec -i odoo-erp-prod bash -lc "
  odoo -c /etc/odoo/odoo.conf -d odoo -i ipai_platform_theme --stop-after-init
"
docker restart odoo-erp-prod
```

### Issue 3: Missing Dependency Error

**Symptom**:
```
ERROR odoo odoo.modules.loading: Module ipai_finance_ppm_umbrella: dependency ipai_finance_ppm is not installed
```

**Cause**: Trying to install module without its dependencies

**Fix**:
```bash
# Install dependency first
docker exec -i odoo-erp-prod bash -lc "
  odoo -c /etc/odoo/odoo.conf -d odoo -i ipai_finance_ppm --stop-after-init
"

# Then install dependent module
docker exec -i odoo-erp-prod bash -lc "
  odoo -c /etc/odoo/odoo.conf -d odoo -i ipai_finance_ppm_umbrella --stop-after-init
"

# Or install both together (Odoo handles order automatically)
docker exec -i odoo-erp-prod bash -lc "
  odoo -c /etc/odoo/odoo.conf -d odoo -i ipai_finance_ppm,ipai_finance_ppm_umbrella --stop-after-init
"
```

### Issue 4: Module Stuck in "to upgrade" State

**Symptom**:
```
ipai_platform_theme                      ⬆️  to upgrade  18.0.1.0.0
```

**Cause**: Upgrade was queued but not executed

**Fix**:
```bash
# Force upgrade
docker exec -i odoo-erp-prod bash -lc "
  odoo -c /etc/odoo/odoo.conf -d odoo -u ipai_platform_theme --stop-after-init
"
docker restart odoo-erp-prod

# Verify state changed to 'installed'
docker exec -i odoo-erp-prod bash -lc "
  psql -U odoo -d odoo -c \"
    SELECT name, state FROM ir_module_module WHERE name = 'ipai_platform_theme';
  \"
"
```

### Issue 5: Missing `__init__.py` Error

**Symptom**:
```
ERROR odoo odoo.modules.module: module ipai_finance_ppm_umbrella: __init__.py not found
```

**Cause**: Module folder missing `__init__.py` file

**Fix**:
```bash
# Check if __init__.py exists
ls -la /opt/odoo-ce/addons/ipai_finance_ppm_umbrella/__init__.py

# Create if missing (empty file is OK for umbrella modules)
touch /opt/odoo-ce/addons/ipai_finance_ppm_umbrella/__init__.py

# Or with minimal content
echo "# -*- coding: utf-8 -*-" > /opt/odoo-ce/addons/ipai_finance_ppm_umbrella/__init__.py

# Retry installation
docker exec -i odoo-erp-prod bash -lc "
  odoo -c /etc/odoo/odoo.conf -d odoo -i ipai_finance_ppm_umbrella --stop-after-init
"
```

---

## Rollback Procedures

### Rollback Option 1: Uninstall Module

```bash
# Uninstall via CLI
docker exec -i odoo-erp-prod bash -lc "
  odoo -c /etc/odoo/odoo.conf -d odoo \
    --uninstall=ipai_platform_theme --stop-after-init
"
docker restart odoo-erp-prod

# Or via UI
# Apps → Search module → Uninstall
```

**Warning**: Uninstalling removes module data (records, menus, etc.)

### Rollback Option 2: Restore Previous Code

```bash
# Git rollback on server
ssh root@159.223.75.148
cd /opt/odoo-ce
git log --oneline -5  # Find commit before deployment
git checkout <commit-hash>

# Restart container to reload modules
docker restart odoo-erp-prod

# Verify rollback
docker logs --tail=100 odoo-erp-prod
```

### Rollback Option 3: Database Backup Restore

```bash
# Only if module caused data corruption

# List backups
docker exec -i odoo-erp-prod ls -lh /var/lib/odoo/backups/

# Restore from backup
docker exec -i odoo-erp-prod bash -lc "
  dropdb -U odoo odoo
  createdb -U odoo odoo
  psql -U odoo -d odoo < /var/lib/odoo/backups/odoo_backup_<timestamp>.sql
"

docker restart odoo-erp-prod
```

---

## Best Practices

### 1. Always Check Status First

```bash
# Before any deployment
ODOO_MODULES=ipai_platform_theme ./scripts/check_module_status.sh
```

### 2. Use Smart Deploy Script

```bash
# Let automation handle install vs upgrade detection
ODOO_MODULES=ipai_platform_theme ./scripts/deploy_odoo_smart.sh
```

### 3. Deploy to Staging First

```bash
# Test on staging environment
ssh root@staging.insightpulseai.net
docker exec -i odoo-staging bash -lc "
  odoo -c /etc/odoo/odoo.conf -d odoo -i ipai_platform_theme --stop-after-init
"

# If successful, deploy to production
ssh root@159.223.75.148
docker exec -i odoo-erp-prod bash -lc "
  odoo -c /etc/odoo/odoo.conf -d odoo -i ipai_platform_theme --stop-after-init
"
```

### 4. Monitor Logs During Deployment

```bash
# In one terminal: follow logs
ssh root@159.223.75.148
docker logs -f odoo-erp-prod

# In another terminal: deploy
ODOO_MODULES=ipai_platform_theme ./scripts/deploy_odoo_smart.sh
```

### 5. Document Module Dependencies

Create `docs/modules/<module-name>.md` with:
```markdown
# ipai_finance_ppm_umbrella

**Depends on**: ipai_finance_ppm, project

**Data files**:
- 01_employees.xml (8 employees)
- 02_logframe_complete.xml
- 03_bir_schedule_2026.xml (22 BIR forms)

**Install order**:
1. ipai_finance_ppm
2. ipai_finance_ppm_umbrella
```

---

## Quick Reference Commands

### Check module status
```bash
docker exec -i odoo-erp-prod psql -U odoo -d odoo -c \
  "SELECT name, state FROM ir_module_module WHERE name = 'ipai_platform_theme';"
```

### Install new module
```bash
docker exec -i odoo-erp-prod bash -lc \
  "odoo -c /etc/odoo/odoo.conf -d odoo -i ipai_platform_theme --stop-after-init"
docker restart odoo-erp-prod
```

### Upgrade existing module
```bash
docker exec -i odoo-erp-prod bash -lc \
  "odoo -c /etc/odoo/odoo.conf -d odoo -u ipai_platform_theme --stop-after-init"
docker restart odoo-erp-prod
```

### Check logs
```bash
docker logs --tail=200 odoo-erp-prod
```

### List all installed modules
```bash
docker exec -i odoo-erp-prod psql -U odoo -d odoo -c \
  "SELECT name, state, latest_version FROM ir_module_module WHERE state = 'installed' ORDER BY name;"
```

---

## Troubleshooting Decision Tree

```
Module deployment fails
  |
  ├─ "Module not found"
  │   └─ Check folder exists → Update Apps List → Retry
  |
  ├─ "Cannot upgrade - not installed"
  │   └─ Use -i instead of -u → Install first
  |
  ├─ "Dependency not installed"
  │   └─ Install dependency first → Then install module
  |
  ├─ "Missing __init__.py"
  │   └─ Create empty __init__.py → Retry
  |
  └─ Other error
      └─ Check logs → Search error message → Fix root cause
```

---

## Support

**Scripts**:
- `scripts/check_module_status.sh` - Status checker
- `scripts/deploy_odoo_smart.sh` - Smart deploy
- `scripts/deploy_odoo_upgrade.sh` - Legacy upgrade

**Documentation**:
- `docs/MODULE_STATUS_FINAL.md` - Complete module inventory
- `docs/ODOO_ADDONS_PATH_CONFIGURATION.md` - Addons path setup
- `docs/CE_OCA_EQUIVALENTS_AUDIT.md` - Enterprise to CE mapping

**Emergency Contact**:
- Jake Tolentino (jgtolentino_rn@yahoo.com)

**Server Access**:
- Production droplet: `ssh root@159.223.75.148`
- Container: `docker exec -i odoo-erp-prod bash`
- Database: `psql -U odoo -d odoo`

---

**Last Updated**: 2026-01-04
**Generated By**: Claude Code SuperClaude Framework
**Status**: ✅ PRODUCTION READY
