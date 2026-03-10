# Finance PPM Safety Mechanisms

**Status:** 🛡️ TRIPLE-LAYER PROTECTION ACTIVE
**Last Updated:** 2025-12-26

## Protection Layers

### Layer 1: CI/CD Health Check 🤖

**File:** `.github/workflows/finance-ppm-health.yml`

**Triggers:**
- Every push to main touching PPM files
- Manual workflow dispatch
- Changes to health check scripts

**Action:**
- SSH into production server
- Run health check: `8 / 12 / 144 / 36 / 36`
- Fail build if mismatch detected

**Purpose:** Prevent broken deployments from reaching production

**Test:**
```bash
# Trigger manually
gh workflow run finance-ppm-health.yml
```

### Layer 2: Git Pre-commit Hook 🔒

**File:** `.githooks/pre-commit`

**Protected Files:**
- `addons/ipai_finance_ppm_umbrella/data/01_employees.xml`
- `addons/ipai_finance_ppm_umbrella/data/02_logframe_complete.xml`
- `addons/ipai_finance_ppm_umbrella/data/03_bir_schedule.xml`
- `addons/ipai_finance_ppm_umbrella/data/04_closing_tasks.xml`

**Action:**
- Block commits with direct edits to seed files
- Require regeneration via `generate_seed_from_excel.py`
- Provide clear error messages with workflow

**Purpose:** Prevent manual drift from canonical Excel source

**Bypass (emergency only):**
```bash
git commit --no-verify  # NOT RECOMMENDED
```

**Setup:**
```bash
# Enable hooks (already configured)
git config core.hooksPath .githooks
```

**Test:**
```bash
# Try to edit protected file
echo "test" >> addons/ipai_finance_ppm_umbrella/data/01_employees.xml
git add addons/ipai_finance_ppm_umbrella/data/01_employees.xml
git commit -m "test"  # Should be BLOCKED
```

### Layer 3: Golden Database Snapshot 💾

**Location:** `/root/backups/odoo_finance_ppm_golden_*.sql`

**Current Snapshot:**
```
/root/backups/odoo_finance_ppm_golden_20251227_022029.sql (72MB)
```

**Purpose:** Nuclear rollback option if Git tags insufficient

**Create New Snapshot:**
```bash
ssh root@159.223.75.148 "docker exec -i odoo-db-1 pg_dump -U odoo odoo > \
  /root/backups/odoo_finance_ppm_golden_$(date +%Y%m%d_%H%M%S).sql"
```

**Restore from Snapshot:**
```bash
# Interactive restore script
./scripts/finance_ppm_restore_golden.sh /root/backups/odoo_finance_ppm_golden_20251227_022029.sql

# Manual restore
ssh root@159.223.75.148 "docker exec -i odoo-db-1 psql -U odoo -d postgres -c 'DROP DATABASE odoo;'"
ssh root@159.223.75.148 "docker exec -i odoo-db-1 psql -U odoo -d postgres -c 'CREATE DATABASE odoo;'"
ssh root@159.223.75.148 "cat /root/backups/odoo_finance_ppm_golden_20251227_022029.sql | \
  docker exec -i odoo-db-1 psql -U odoo -d odoo"
```

## Rollback Decision Matrix

| Scenario | Layer | Action |
|----------|-------|--------|
| Bad seed XML committed | Layer 2 | Pre-commit hook blocks it |
| Bad deploy pushed to main | Layer 1 | CI fails, rollback Git tag |
| Production DB corrupted | Layer 3 | Restore golden snapshot |
| Manual Odoo UI edits | None | Run health check, regenerate from Excel |

## Rollback Procedures

### Git Tag Rollback (Layer 1)

**When:** Code changes broke the deployment

```bash
# 1. Checkout canonical tag
git checkout finance-ppm-v1.0.0

# 2. Redeploy Odoo modules
ssh root@159.223.75.148 "docker exec -e PGHOST=odoo-db-1 odoo-production \
  odoo -d odoo -u ipai_finance_ppm,ipai_finance_ppm_umbrella --stop-after-init"

# 3. Verify
./scripts/finance_ppm_health_check.sh odoo
```

### Database Snapshot Rollback (Layer 3)

**When:** Database is corrupted beyond Git rollback

```bash
# 1. Use restore script (recommended)
./scripts/finance_ppm_restore_golden.sh /root/backups/odoo_finance_ppm_golden_20251227_022029.sql

# 2. Verify
./scripts/finance_ppm_health_check.sh odoo
```

### Manual UI Edits Recovery

**When:** Someone edited data directly in Odoo UI

```bash
# 1. Regenerate from Excel
python3 scripts/generate_seed_from_excel.py

# 2. Redeploy
ssh root@159.223.75.148 "docker exec -e PGHOST=odoo-db-1 odoo-production \
  odoo -d odoo -u ipai_finance_ppm,ipai_finance_ppm_umbrella --stop-after-init"

# 3. Verify
./scripts/finance_ppm_health_check.sh odoo
```

## Emergency Contacts

**If all layers fail:**
1. Check `/root/backups/` for golden snapshots
2. Restore most recent snapshot
3. Run health check to verify
4. Document what went wrong
5. Update safety mechanisms accordingly

## Testing Safety Mechanisms

### Test CI Health Check

```bash
# Make a safe change
touch test.txt
git add test.txt
git commit -m "test: trigger CI health check"
git push origin main

# Watch workflow
gh run watch
```

### Test Pre-commit Hook

```bash
# Should BLOCK
echo "test" >> addons/ipai_finance_ppm_umbrella/data/01_employees.xml
git add addons/ipai_finance_ppm_umbrella/data/01_employees.xml
git commit -m "test"

# Should PASS
python3 scripts/generate_seed_from_excel.py
git add addons/ipai_finance_ppm_umbrella/data/*.xml
git commit -m "feat: regenerate from Excel"
```

### Test Database Snapshot

```bash
# List snapshots
ssh root@159.223.75.148 "ls -lh /root/backups/odoo_finance_ppm_golden_*.sql"

# Restore (CAUTION: test DB only!)
./scripts/finance_ppm_restore_golden.sh /root/backups/odoo_finance_ppm_golden_20251227_022029.sql
```

## Maintenance Schedule

**Weekly:**
- Run health check manually: `./scripts/finance_ppm_health_check.sh odoo`

**Monthly:**
- Create new golden snapshot after verified changes
- Archive old snapshots (keep 3 most recent)

**Quarterly:**
- Test all rollback procedures on test database
- Update this document with any new scenarios

## Version History

- **2025-12-26**: Initial safety mechanisms deployed
  - CI health check workflow
  - Pre-commit hook for seed protection
  - Golden database snapshot (72MB)
  - Restore scripts and documentation

## References

- **CI Workflow:** `.github/workflows/finance-ppm-health.yml`
- **Pre-commit Hook:** `.githooks/pre-commit`
- **Health Check:** `scripts/finance_ppm_health_check.sh`
- **Restore Script:** `scripts/finance_ppm_restore_golden.sh`
- **Canonical State:** `FINANCE_PPM_CANONICAL.md`
- **Technical README:** `addons/ipai_finance_ppm_umbrella/README.md`
