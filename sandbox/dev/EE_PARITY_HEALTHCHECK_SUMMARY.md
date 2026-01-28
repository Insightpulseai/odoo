# EE Parity Healthcheck + CI Gate - Implementation Summary

**Date**: 2026-01-28
**Status**: COMPLETE - Ready for testing
**Purpose**: Enforce EE-parity as an invariant via automated healthcheck + CI gate

---

## What Was Implemented

### 1. Healthcheck Script (`scripts/dev/ee-parity-healthcheck.sh`)

**Purpose**: Validate that all EE-parity modules (OCA + IPAI) are installed and up-to-date

**Features**:
- ✅ Environment validation (.env file required)
- ✅ Module list normalization
- ✅ SQL query against `ir_module_module` table
- ✅ Color-coded status output (✅ installed, ⬆️ to upgrade, ❌ uninstalled)
- ✅ Summary statistics by module state
- ✅ Exit codes for automation:
  - `0` = All modules installed and up-to-date
  - `10` = Missing modules (uninstalled)
  - `11` = Modules need upgrade (to upgrade state)
  - `12` = Environment validation failed

**Permissions**: Made executable (`chmod +x`)

**Usage**:
```bash
./scripts/dev/ee-parity-healthcheck.sh

# Exit code handling example:
./scripts/dev/ee-parity-healthcheck.sh
case $? in
  0)  echo "All good" ;;
  10) echo "Missing modules - run installer" ;;
  11) echo "Modules need upgrade - run installer" ;;
  12) echo "Environment validation failed" ;;
esac
```

### 2. Self-Validation Integration

**Modified**: `scripts/dev/install-ee-parity-modules.sh`

**Added**: Post-install healthcheck validation at end of installation

**Behavior**:
- After module installation completes, automatically runs healthcheck
- If healthcheck passes (exit 0): Display success message
- If healthcheck fails (exit 10/11): Display diagnostic message and exit with code 12
- Provides user guidance on how to investigate failures

**Code Added** (lines 107-131):
```bash
# ═══════════════════════════════════════════════════════════════════════════════
# 7. POST-INSTALL HEALTHCHECK
# ═══════════════════════════════════════════════════════════════════════════════

echo
echo "Running post-install healthcheck..."
echo

if ./scripts/dev/ee-parity-healthcheck.sh; then
  echo
  echo "✅ EE parity modules installation/upgrade completed successfully"
  echo "✅ All modules verified as installed and up-to-date"
else
  HEALTHCHECK_EXIT=$?
  echo
  echo "⚠️  Installation completed but healthcheck failed (exit code: $HEALTHCHECK_EXIT)"
  # ... diagnostic messages ...
  exit 12
fi
```

### 3. CI Gate (`.github/workflows/ee-parity-check.yml`)

**Purpose**: Enforce EE-parity as invariant on main/release branches

**Trigger Events**:
- Push to `main` branch
- Push to `release/**` branches
- Pull requests targeting `main` or `release/**`

**Workflow Steps**:
1. **Checkout repository**
2. **Set up Python 3.11**
3. **Cache OCA modules** (speeds up CI runs)
4. **Install OCA dependencies** (clone required OCA repos if not cached)
5. **Install Odoo dependencies** (PostgreSQL libs, Python packages)
6. **Create .env for CI** (with all EE-parity module definitions)
7. **Start Odoo in CI mode** (minimal config for testing)
8. **Install EE-parity modules** (via install script)
9. **Run EE-parity healthcheck** (exit code determines CI pass/fail)
10. **Upload healthcheck results** (on failure, for debugging)
11. **Comment on PR** (on failure, notify developer)

**PostgreSQL Service**:
- Uses `postgres:16` container
- Health checks enabled
- Exposed on port 5432

**Caching Strategy**:
- OCA modules cached by `oca.lock.json` hash
- Significantly reduces CI run time on repeated runs

**Failure Handling**:
- Uploads logs as artifacts (retained 7 days)
- Automatically comments on PR with failure details and link to logs
- Provides local reproduction command: `./scripts/dev/ee-parity-healthcheck.sh`

---

## Testing Checklist

### Prerequisites
```bash
# 1. Ensure .env exists with EE-parity module definitions
[ -f .env ] || cp .env.example .env

# 2. Ensure OCA addons are available
ls oca-addons/  # Should show OCA module directories

# 3. Start Odoo container
docker compose up -d odoo-dev
```

### Local Testing Sequence

#### Test 1: Healthcheck on Clean Database (Expected: Exit 10)
```bash
# Reset database to clean state
./scripts/dev/reset-db.sh

# Run healthcheck (should fail - no modules installed)
./scripts/dev/ee-parity-healthcheck.sh
echo "Exit code: $?"  # Should be 10 (missing modules)
```

#### Test 2: Installation with Auto-Healthcheck
```bash
# Run installer (includes post-install healthcheck)
./scripts/dev/install-ee-parity-modules.sh

# Should complete with:
# ✅ EE parity modules installation/upgrade completed successfully
# ✅ All modules verified as installed and up-to-date
```

#### Test 3: Healthcheck on Fully Installed System (Expected: Exit 0)
```bash
# Run healthcheck independently
./scripts/dev/ee-parity-healthcheck.sh
echo "Exit code: $?"  # Should be 0 (all modules installed)
```

#### Test 4: Simulate Drift (Uninstall Module)
```bash
# Manually uninstall a module to simulate drift
docker compose exec odoo-dev odoo -d odoo_dev \
  -i base -u account_usability --uninstall --stop-after-init

# Run healthcheck (should fail)
./scripts/dev/ee-parity-healthcheck.sh
echo "Exit code: $?"  # Should be 10 (missing modules)

# Fix drift by re-running installer
./scripts/dev/install-ee-parity-modules.sh
```

### CI Testing Sequence

#### Test 1: Verify Workflow Syntax
```bash
# Validate GitHub Actions workflow syntax
cat .github/workflows/ee-parity-check.yml | yq eval '.' -
# Should parse without errors
```

#### Test 2: Push to Feature Branch (Optional)
```bash
git checkout -b test/ee-parity-gate
git add .github/workflows/ee-parity-check.yml
git commit -m "test(ci): add EE-parity gate"
git push origin test/ee-parity-gate

# Create PR on GitHub, observe CI run
# Expected: CI should run and pass if all modules install correctly
```

#### Test 3: Protected Branch Enforcement
```bash
# On GitHub:
# 1. Go to Settings → Branches → main
# 2. Add "EE Parity Check" to required status checks
# 3. Test by creating PR with intentionally broken .env (missing modules)
# Expected: PR cannot be merged until CI passes
```

---

## Deployment Workflow

### Development Environment

**Already Active**: Healthcheck available immediately after implementing files above

```bash
# Run healthcheck anytime
./scripts/dev/ee-parity-healthcheck.sh

# Installation now includes auto-validation
./scripts/dev/install-ee-parity-modules.sh
```

### Staging Environment

**Pre-Deployment** (validate on staging before production):
```bash
# SSH to staging server
ssh root@178.128.112.214  # Or staging server IP

# Copy healthcheck script
scp scripts/dev/ee-parity-healthcheck.sh root@staging:/opt/odoo-ce/repo/scripts/dev/

# Copy updated install script
scp scripts/dev/install-ee-parity-modules.sh root@staging:/opt/odoo-ce/repo/scripts/dev/

# Run healthcheck on staging
cd /opt/odoo-ce/repo
./scripts/dev/ee-parity-healthcheck.sh
```

### Production Environment

**Production Rollout** (after successful staging validation):
```bash
# SSH to production
ssh root@178.128.112.214

# Navigate to repo
cd /opt/odoo-ce/repo

# Pull latest changes (includes healthcheck + updated installer)
git pull origin main

# Backup database before any changes
docker compose exec postgres pg_dump -U odoo -d odoo_prod > /backups/odoo_prod_pre_healthcheck_$(date +%Y%m%d_%H%M%S).sql

# Run healthcheck to validate current state
./scripts/dev/ee-parity-healthcheck.sh

# If healthcheck fails, run installer
./scripts/dev/install-ee-parity-modules.sh

# Verify post-install state
./scripts/dev/ee-parity-healthcheck.sh
echo "Exit code: $?"  # Should be 0
```

### CI/CD Integration

**GitHub Branch Protection**:
```bash
# Via GitHub UI or gh CLI:
gh api repos/jgtolentino/odoo-ce/branches/main/protection \
  -X PUT \
  -F required_status_checks[strict]=true \
  -F required_status_checks[contexts][]=EE Parity Check

# Alternative: Use GitHub UI
# Settings → Branches → main → Edit → Require status checks
# ☑ EE Parity Check
```

**Scheduled Healthcheck** (optional - prevent silent drift):
```yaml
# Add to .github/workflows/ee-parity-check.yml
on:
  schedule:
    - cron: '0 8 * * 1'  # Every Monday at 8 AM UTC

  workflow_dispatch:  # Allow manual runs
```

---

## Rollback Strategy

### If Healthcheck Script Causes Issues

**Scenario**: Healthcheck script has bugs or blocks legitimate workflows

**Rollback**:
```bash
# Option 1: Remove post-install healthcheck from installer
cd /opt/odoo-ce/repo
git show HEAD~1:scripts/dev/install-ee-parity-modules.sh > scripts/dev/install-ee-parity-modules.sh

# Option 2: Disable healthcheck script temporarily
chmod -x scripts/dev/ee-parity-healthcheck.sh

# Option 3: Bypass healthcheck in CI (add to workflow)
# - name: Run EE-parity healthcheck
#   continue-on-error: true  # Add this line
```

### If CI Gate Blocks Valid PRs

**Scenario**: CI gate falsely fails due to environment issues (OCA module fetch failures, etc.)

**Emergency Bypass**:
```bash
# Via GitHub UI:
# Settings → Branches → main → Edit
# ☐ Uncheck "EE Parity Check" temporarily

# Via gh CLI:
gh api repos/jgtolentino/odoo-ce/branches/main/protection \
  -X DELETE
```

**Better Solution**: Fix root cause in workflow, then re-enable gate

---

## Key Benefits

### For Developers

- ✅ **Immediate Feedback**: Know instantly if module installation succeeded
- ✅ **Local Testing**: Run healthcheck before pushing to CI
- ✅ **Clear Diagnostics**: Exit codes and colored output show exactly what's wrong
- ✅ **Prevent Drift**: Can't accidentally uninstall critical modules without detection

### For Operations

- ✅ **Automated Enforcement**: CI gate prevents bad deployments
- ✅ **Drift Prevention**: Scheduled healthchecks catch configuration drift early
- ✅ **Audit Trail**: GitHub Actions logs provide evidence of compliance
- ✅ **Rollback Safety**: Clear exit codes enable automated recovery scripts

### For Documentation

- ✅ **Single Source of Truth**: .env defines expected state, healthcheck validates it
- ✅ **Self-Documenting**: Healthcheck output shows current vs expected state
- ✅ **Compliance Proof**: CI badge shows EE-parity status on every commit

---

## Next Steps

### Immediate Actions (After Testing)

1. **Run Local Tests**: Complete all 4 test scenarios in "Testing Checklist" above
2. **Validate CI Workflow**: Create test PR to verify workflow runs correctly
3. **Document Module Requirements**: Update `oca.lock.json` or equivalent with OCA module pins
4. **Enable Branch Protection**: Add "EE Parity Check" to required status checks

### Future Enhancements

1. **Add Scheduled Healthcheck**: Weekly cron job to catch silent drift
2. **Enhance CI Caching**: Cache Odoo dependencies, not just OCA modules
3. **Metrics Dashboard**: Track healthcheck pass/fail rates over time
4. **Slack/Email Notifications**: Alert on healthcheck failures in production
5. **Module Versioning**: Track installed versions, not just installed/uninstalled state

### Integration Opportunities

1. **Prometheus Metrics**: Export healthcheck results as metrics
2. **Grafana Dashboard**: Visualize EE-parity compliance over time
3. **Ansible Playbook**: Automate healthcheck execution across multiple environments
4. **Terraform State**: Treat .env module definitions as infrastructure-as-code

---

## Files Created

| File | Lines | Purpose |
|------|-------|------------|
| `scripts/dev/ee-parity-healthcheck.sh` | 138 | Healthcheck script with exit codes |
| `.github/workflows/ee-parity-check.yml` | 151 | CI gate enforcing EE-parity |
| `scripts/dev/install-ee-parity-modules.sh` (updated) | +25 | Added post-install self-validation |
| `EE_PARITY_HEALTHCHECK_SUMMARY.md` | 400 | This summary document |

**Total**: 714 lines of code + documentation

---

## Success Criteria

Healthcheck + CI gate is successful when:

- ✅ `./scripts/dev/ee-parity-healthcheck.sh` exits with code 0 on fully installed system
- ✅ Healthcheck correctly detects missing modules (exit 10)
- ✅ Healthcheck correctly detects modules needing upgrade (exit 11)
- ✅ Installation script auto-validates and exits 12 on failure
- ✅ CI workflow runs on push/PR to main/release branches
- ✅ CI workflow fails when EE-parity is not maintained
- ✅ PR comments automatically notify developers of failures
- ✅ All local tests pass (4 scenarios in testing checklist)

---

**Status**: READY FOR TESTING
**Blocker**: None (all dependencies documented)
**Risk**: Low (read-only healthcheck, optional CI gate)
