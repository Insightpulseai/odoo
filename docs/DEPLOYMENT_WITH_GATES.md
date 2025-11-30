# Odoo Module Deployment with Quality Gates

## Overview

This document describes the enhanced Odoo module deployment system with comprehensive quality gates, database backup, and rollback capability.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Deployment Pipeline                        │
├─────────────────────────────────────────────────────────────┤
│ Phase 1: Prerequisites   → SSH check, module validation     │
│ Phase 2: Linting         → flake8, pylint                   │
│ Phase 3: Unit Tests      → scripts/ci/run_odoo_tests.sh     │
│ Phase 4: Database Backup → pg_dump via Docker               │
│ Phase 5: Deploy Files    → rsync to production              │
│ Phase 6: Upgrade Module  → odoo -u module_name              │
│ Phase 7: Restart Odoo    → docker restart                   │
│ Phase 8: Smoke Tests     → Health check + visual parity     │
│                                                              │
│ On Failure → Automatic Rollback                             │
└─────────────────────────────────────────────────────────────┘
```

## Scripts

### 1. `deploy-odoo-modules-with-gates.sh`

Enhanced deployment script with quality gates and rollback capability.

**Features**:
- ✅ Pre-deployment validation (prerequisites, manifest check)
- ✅ Code quality gates (flake8, pylint)
- ✅ Unit test execution (via `scripts/ci/run_odoo_tests.sh`)
- ✅ Automatic database backup before upgrade
- ✅ Graceful rollback on failure
- ✅ Health check validation
- ✅ Optional visual parity testing

**Usage**:
```bash
# Standard deployment with all quality gates
./scripts/deploy-odoo-modules-with-gates.sh ipai_finance_ppm

# Skip unit tests (faster, but riskier)
./scripts/deploy-odoo-modules-with-gates.sh ipai_finance_ppm --skip-tests

# Skip linting (if you've already run locally)
./scripts/deploy-odoo-modules-with-gates.sh ipai_finance_ppm --skip-lint

# Skip database backup (NOT RECOMMENDED for production)
./scripts/deploy-odoo-modules-with-gates.sh ipai_finance_ppm --skip-backup

# Combine multiple flags
./scripts/deploy-odoo-modules-with-gates.sh ipai_finance_ppm --skip-tests --skip-lint
```

**Available Modules**:
- `ipai_ce_cleaner` - OCA compliance cleaner
- `ipai_expense` - Expense management
- `ipai_equipment` - Equipment tracking
- `ipai_ocr_expense` - OCR-powered expense automation
- `ipai_finance_monthly_closing` - Month-end closing
- `ipai_finance_ppm` - Finance PPM with ECharts dashboards

### 2. `rollback-module.sh`

Emergency rollback script for failed deployments.

**Features**:
- ✅ Database restore from backup
- ✅ Safety backup before rollback (in case of user error)
- ✅ Automatic Odoo restart
- ✅ Health check verification
- ✅ Interactive confirmation (prevents accidental rollbacks)

**Usage**:
```bash
# List available backups
ssh root@erp.insightpulseai.net "ls -lh /tmp/odoo_backup_*.sql"

# Rollback to specific backup
./scripts/rollback-module.sh /tmp/odoo_backup_ipai_finance_ppm_20251127_120000.sql
```

**Rollback Process**:
1. Validates backup file exists and is not empty
2. Creates safety backup of current state
3. Stops Odoo container
4. Drops and recreates database
5. Restores from backup
6. Starts Odoo container
7. Verifies health check passes

## Quality Gates

### 1. Prerequisites Check

**What it validates**:
- Module directory exists in `addons/`
- `__manifest__.py` is present
- SSH connectivity to production server
- Required Python packages (flake8, pylint)

**Failure behavior**: Exits immediately

### 2. Linting (flake8 + pylint)

**flake8 configuration**:
- Max line length: 120 characters
- Excludes: `__pycache__`, `*.pyc`

**pylint configuration**:
- Errors only (no refactoring/convention warnings)
- Disables: C (convention), R (refactoring)

**Failure behavior**: Exits immediately (blocking)

**Skip with**: `--skip-lint`

### 3. Unit Tests

**Test runner**: `scripts/ci/run_odoo_tests.sh`

**What it does**:
- Creates temporary test database
- Installs module
- Runs all tests in `tests/` directory
- Cleans up test database

**Requirements**:
- Module must have `tests/` directory
- Odoo test suite must pass

**Failure behavior**: Exits immediately (blocking)

**Skip with**: `--skip-tests`

### 4. Database Backup

**Backup location**: `/tmp/odoo_backup_<module>_<timestamp>.sql`

**Format**: PostgreSQL SQL dump

**What it includes**:
- Complete database schema
- All data
- Sequences and indexes

**Failure behavior**: Exits immediately (cannot deploy without backup)

**Skip with**: `--skip-backup` (NOT RECOMMENDED)

### 5. Deployment (rsync)

**Source**: `addons/<module>/`
**Target**: `root@erp.insightpulseai.net:/opt/odoo/custom-addons/<module>/`

**rsync flags**:
- `-a` Archive mode (preserves permissions, timestamps)
- `-v` Verbose output
- `-z` Compress during transfer
- `--delete` Remove files in target that don't exist in source

**Permissions**: `chown -R odoo:odoo` after rsync

**Failure behavior**: Automatic rollback

### 6. Module Upgrade

**Command**: `docker exec odoo-odoo-1 odoo -d odoo -u <module> --stop-after-init --log-level=warn`

**What it does**:
- Updates module in database
- Runs upgrade scripts (if any)
- Updates views, models, security rules
- Stops after initialization (safe mode)

**Failure behavior**: Automatic rollback

### 7. Container Restart

**Command**: `docker restart odoo-odoo-1`

**Wait time**: 10 seconds for Odoo to start

**Failure behavior**: Automatic rollback

### 8. Smoke Tests

**Health check**: `https://erp.insightpulseai.net/web/health`

**Expected response**: `{"status": "pass"}`

**Retry logic**:
- Max retries: 5
- Retry interval: 5 seconds
- Total timeout: 25 seconds

**Visual parity** (optional):
- Runs `scripts/snap.js --module=<module>` if available
- SSIM thresholds: ≥0.97 (mobile), ≥0.98 (desktop)
- Non-blocking (warnings only)

**Failure behavior**: Automatic rollback

## Rollback Behavior

### Automatic Rollback Triggers

1. **Deployment failure** (Phase 5)
2. **Module upgrade failure** (Phase 6)
3. **Container restart failure** (Phase 7)
4. **Health check failure** (Phase 8)

### Rollback Process

```bash
# 1. Detect failure
log_error "Deployment failed: <reason>"

# 2. Initiate rollback
log_warning "=== Initiating Rollback ==="

# 3. Restore database
docker exec -i odoo-odoo-1 psql -U odoo odoo < /tmp/odoo_backup_*.sql

# 4. Restart Odoo
docker restart odoo-odoo-1

# 5. Notify user
log_success "Rollback completed - system restored to pre-deployment state"
```

### Manual Rollback

If automatic rollback fails or you need to rollback after deployment:

```bash
# 1. List available backups
ssh root@erp.insightpulseai.net "ls -lh /tmp/odoo_backup_*.sql"

# 2. Run rollback script
./scripts/rollback-module.sh /tmp/odoo_backup_ipai_finance_ppm_20251127_120000.sql

# 3. Verify rollback success
curl -sf https://erp.insightpulseai.net/web/health | jq
```

## Comparison with Original Script

| Feature | Original `deploy-odoo-modules.sh` | Enhanced `deploy-odoo-modules-with-gates.sh` |
|---------|-----------------------------------|---------------------------------------------|
| Module validation | ✅ Basic | ✅ Comprehensive |
| Linting (flake8/pylint) | ❌ No | ✅ Yes |
| Unit tests | ❌ No | ✅ Yes |
| Database backup | ❌ No | ✅ Yes |
| Rollback capability | ❌ No | ✅ Automatic |
| Health check | ✅ Basic | ✅ Advanced (retries) |
| Visual parity | ❌ No | ✅ Optional |
| Deployment speed | Fast | Slower (safer) |
| Production readiness | Good | Excellent |

## Best Practices

### For Development

```bash
# Fast iteration (skip tests/lint if you've already run locally)
./scripts/deploy-odoo-modules-with-gates.sh ipai_finance_ppm --skip-tests --skip-lint
```

### For Staging

```bash
# Run all quality gates
./scripts/deploy-odoo-modules-with-gates.sh ipai_finance_ppm
```

### For Production

```bash
# Full quality gates + visual parity
./scripts/deploy-odoo-modules-with-gates.sh ipai_finance_ppm

# NEVER use --skip-backup in production
```

## Troubleshooting

### Problem: flake8 fails with "command not found"

**Solution**:
```bash
pip install flake8
```

Or skip linting:
```bash
./scripts/deploy-odoo-modules-with-gates.sh ipai_finance_ppm --skip-lint
```

### Problem: Unit tests fail

**Check test output**:
```bash
# Run tests locally first
ODOO_MODULES=ipai_finance_ppm \
DB_NAME=test_finance_ppm \
./scripts/ci/run_odoo_tests.sh
```

**Fix tests** before deploying, or skip (risky):
```bash
./scripts/deploy-odoo-modules-with-gates.sh ipai_finance_ppm --skip-tests
```

### Problem: Health check fails after deployment

**Check Odoo logs**:
```bash
ssh root@erp.insightpulseai.net 'docker logs odoo-odoo-1 --tail=50'
```

**Common causes**:
- Module syntax errors (check pylint output)
- Missing dependencies in `__manifest__.py`
- Database migration issues

**Solution**: Rollback and fix:
```bash
./scripts/rollback-module.sh /tmp/odoo_backup_*.sql
```

### Problem: Rollback fails

**Manual database restore**:
```bash
# 1. SSH to server
ssh root@erp.insightpulseai.net

# 2. Stop Odoo
docker stop odoo-odoo-1

# 3. Drop database
docker exec odoo-db-1 psql -U odoo -d postgres -c 'DROP DATABASE odoo;'

# 4. Create database
docker exec odoo-db-1 psql -U odoo -d postgres -c 'CREATE DATABASE odoo OWNER odoo;'

# 5. Restore from backup
docker exec -i odoo-db-1 psql -U odoo odoo < /tmp/odoo_backup_*.sql

# 6. Start Odoo
docker start odoo-odoo-1
```

## Example Deployment Session

```bash
$ ./scripts/deploy-odoo-modules-with-gates.sh ipai_finance_ppm

=========================================
Odoo Module Deployment with Quality Gates
=========================================
Module: ipai_finance_ppm
Target: root@erp.insightpulseai.net
Database: odoo
Skip tests: false
Skip lint: false
Skip backup: false
=========================================

ℹ === Phase 1: Prerequisites Check ===
✅ Prerequisites check passed

ℹ === Phase 2: Quality Gates - Linting ===
ℹ Running flake8...
✅ flake8 passed
ℹ Running pylint...
✅ pylint passed
✅ Linting phase passed

ℹ === Phase 3: Quality Gates - Unit Tests ===
ℹ Running unit tests for ipai_finance_ppm...
=========================================
Odoo Test Runner
=========================================
Modules: ipai_finance_ppm
Database: test_ipai_finance_ppm_1732704000
Log level: warn
Addons path: addons,oca
========================================
✅ Unit tests passed

ℹ === Phase 4: Database Backup ===
ℹ Creating database backup: /tmp/odoo_backup_ipai_finance_ppm_20251127_120000.sql
✅ Database backup created: /tmp/odoo_backup_ipai_finance_ppm_20251127_120000.sql

ℹ === Phase 5: Deploy Module Files ===
ℹ Deploying ipai_finance_ppm to erp.insightpulseai.net...
✅ Module files deployed

ℹ === Phase 6: Upgrade Module in Odoo ===
ℹ Upgrading module ipai_finance_ppm in database odoo...
✅ Module upgraded successfully

ℹ === Phase 7: Restart Odoo Container ===
ℹ Restarting odoo-odoo-1...
ℹ Waiting for Odoo to start...
✅ Odoo container restarted

ℹ === Phase 8: Smoke Tests & Health Check ===
ℹ Checking health endpoint: https://erp.insightpulseai.net/web/health
✅ Health check passed
✅ Smoke tests passed

=========================================
✅ Deployment Completed Successfully!
=========================================
Module: ipai_finance_ppm
Deployed to: https://erp.insightpulseai.net
Backup: /tmp/odoo_backup_ipai_finance_ppm_20251127_120000.sql
=========================================
```

## Integration with CI/CD

**GitHub Actions example**:

```yaml
name: Deploy Odoo Module

on:
  push:
    branches: [main]
    paths:
      - 'addons/ipai_finance_ppm/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install dependencies
        run: |
          pip install flake8 pylint

      - name: Deploy module
        env:
          SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}
        run: |
          # Setup SSH
          mkdir -p ~/.ssh
          echo "$SSH_PRIVATE_KEY" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh-keyscan erp.insightpulseai.net >> ~/.ssh/known_hosts

          # Deploy with quality gates
          ./scripts/deploy-odoo-modules-with-gates.sh ipai_finance_ppm
```

## Security Considerations

1. **Backup files contain sensitive data** - stored in `/tmp/` (temporary)
2. **SSH keys required** - ensure proper key management
3. **Database credentials** - never logged or exposed
4. **RLS policies** - validated in Phase 8 (optional)

## Performance Impact

| Phase | Typical Duration | Impact |
|-------|------------------|--------|
| Prerequisites | < 5 seconds | Minimal |
| Linting | 10-30 seconds | Moderate |
| Unit Tests | 1-5 minutes | High |
| Database Backup | 10-30 seconds | Moderate |
| Deploy Files | 5-15 seconds | Minimal |
| Upgrade Module | 10-60 seconds | Moderate |
| Restart Odoo | 10-20 seconds | Minimal |
| Smoke Tests | 5-25 seconds | Minimal |
| **Total** | **2-7 minutes** | **Varies** |

**Speed optimization**:
- Use `--skip-tests` for development iterations
- Use `--skip-lint` if linting locally
- Never skip backup in production

---

**Last Updated**: 2025-11-27
**Canonical Source**: This document describes the enhanced deployment system for odoo-ce repository
