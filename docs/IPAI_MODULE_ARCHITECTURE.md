# IPAI Module Architecture - Zero Drift Enforcement

**Status:** ✅ Achieved (2026-01-16)
**Enforcement:** CI gate prevents legacy modules from returning

---

## Canonical Architecture (The Trio)

Only these three `ipai_*` modules are allowed in the repository:

1. **`ipai_enterprise_bridge`** - Central integration hub
   - Purpose: Unified interface for all IPAI enterprise integrations
   - Status: Present (uninstalled in dev DB)

2. **`ipai_scout_bundle`** - Scout transaction processing (future)
   - Purpose: OCR expense automation, receipt processing
   - Status: To be created

3. **`ipai_ces_bundle`** - Client Engagement Suite (future)
   - Purpose: Client portal, agency management, vendor workflows
   - Status: To be created

---

## Zero Drift Achievement

### Database State

```sql
SELECT name, state FROM ir_module_module WHERE name ILIKE 'ipai_%';
```

**Result:**
```
          name          |    state    
------------------------+-------------
 ipai_enterprise_bridge | uninstalled
(1 row)
```

**✅ Zero legacy modules in database**

### Filesystem State

```bash
find addons -maxdepth 1 -type d -name "ipai_*"
```

**Result:**
```
addons/ipai_enterprise_bridge
```

**✅ Only canonical module present**

---

## Removed Legacy Modules

### 1. ipai_hello
- **Type:** Test module
- **Status:** Never installed (uninstalled in DB)
- **Action:** Deleted from filesystem + removed from `ir_module_module`
- **Risk:** Zero (no data loss, never used)

### 2. ipai_finance_ppm_umbrella
- **Type:** Legacy Finance PPM module
- **Status:** Never installed
- **Action:** Deleted from filesystem
- **Replacement:** Functionality absorbed into `ipai_enterprise_bridge`

---

## CI Enforcement

### Gate Script: `scripts/ci/deny_legacy_ipai_modules.sh`

**Purpose:** Block any `ipai_*` module not in the canonical trio

**Allowed modules:**
- `ipai_enterprise_bridge`
- `ipai_scout_bundle`
- `ipai_ces_bundle`

**Behavior:**
- Scans `addons/` directory for `ipai_*` modules
- Compares against allowed list
- Exits with error if legacy module detected
- Provides remediation instructions

**Local execution:**
```bash
cd ~/Documents/GitHub/odoo-ce
./scripts/ci/deny_legacy_ipai_modules.sh
```

**Expected output:**
```
=== IPAI Module Gate ===
Checking for legacy ipai_* modules...
Allowed: ipai_enterprise_bridge ipai_scout_bundle ipai_ces_bundle

✅ Allowed: ipai_enterprise_bridge

✅ OK: No legacy IPAI modules detected
All ipai_* modules comply with new architecture (enterprise_bridge, scout_bundle, ces_bundle)
```

### GitHub Actions Workflow: `.github/workflows/ipai-module-gate.yml`

**Triggers:**
- Pull requests touching `addons/ipai_*/**`
- Pushes to `main` or `feat/**` branches

**Job:**
1. Checkout code
2. Run `scripts/ci/deny_legacy_ipai_modules.sh`
3. Fail PR if legacy modules detected

**Benefits:**
- Prevents accidental legacy module commits
- Enforces architectural discipline
- Documents allowed modules in CI logs

---

## Migration History

### Phase 1: Classification (2026-01-16 13:53 UTC)

**Database query:**
```sql
SELECT name, state FROM ir_module_module WHERE name ILIKE 'ipai_%';
```

**Result:** 2 modules found
- `ipai_enterprise_bridge` (uninstalled)
- `ipai_hello` (uninstalled)

**Decision:** Safe to delete both from filesystem (neither installed)

### Phase 2: Filesystem Cleanup (2026-01-16 14:00 UTC)

**Actions:**
```bash
# Remove test module
rm -rf addons/ipai_hello

# Add canonical module to git
git add addons/ipai_enterprise_bridge/

# Remove legacy umbrella module (already deleted)
# git status showed ipai_finance_ppm_umbrella as deleted
```

**Result:** Only `ipai_enterprise_bridge` remains

### Phase 3: Database Cleanup (2026-01-16 14:05 UTC)

**Action:**
```sql
DELETE FROM ir_module_module WHERE name = 'ipai_hello';
```

**Result:** Database matches filesystem (zero drift)

### Phase 4: CI Gate Installation (2026-01-16 14:10 UTC)

**Actions:**
1. Created `scripts/ci/deny_legacy_ipai_modules.sh`
2. Created `.github/workflows/ipai-module-gate.yml`
3. Tested locally (passed)
4. Committed and pushed

**Result:** Future protection against legacy module reintroduction

---

## Acceptance Criteria

✅ **Database contains only canonical modules**
- Query: `SELECT name FROM ir_module_module WHERE name ILIKE 'ipai_%'`
- Expected: `ipai_enterprise_bridge` only

✅ **Filesystem contains only canonical modules**
- Command: `find addons -maxdepth 1 -type d -name "ipai_*"`
- Expected: `addons/ipai_enterprise_bridge` only

✅ **CI gate blocks legacy modules**
- Script: `./scripts/ci/deny_legacy_ipai_modules.sh`
- Expected: Exit 0, message "No legacy IPAI modules detected"

✅ **GitHub Actions enforces gate**
- Workflow: `.github/workflows/ipai-module-gate.yml`
- Expected: PRs fail if legacy modules present

✅ **Zero drift achieved**
- No modules installed that shouldn't be
- No modules on filesystem that aren't allowed
- No modules in database that don't exist on filesystem

---

## Future Module Creation

### When creating `ipai_scout_bundle`:

```bash
cd ~/Documents/GitHub/odoo-ce

# Create module directory
mkdir -p addons/ipai_scout_bundle

# Generate module structure (use scaffold or manual)
# ...

# Verify CI gate passes
./scripts/ci/deny_legacy_ipai_modules.sh
# Should show: ✅ Allowed: ipai_scout_bundle

# Install module
docker compose exec odoo odoo -d odoo_dev -i ipai_scout_bundle --stop-after-init
```

### When creating `ipai_ces_bundle`:

Same procedure as `ipai_scout_bundle` above.

---

## Troubleshooting

### Issue: CI gate fails after adding new module

**Symptom:**
```
❌ BLOCKED legacy module: ipai_new_module
🚨 Legacy IPAI modules detected!
```

**Root cause:** Module name not in `ALLOWED` array in `scripts/ci/deny_legacy_ipai_modules.sh`

**Resolution:**
1. If module is part of new architecture:
   - Add to `ALLOWED` array in script
   - Update this documentation
   - Commit both changes together

2. If module is legacy/experimental:
   - Remove module: `rm -rf addons/ipai_new_module`
   - Or rename to non-ipai prefix: `mv addons/ipai_new_module addons/experiment_new_module`

### Issue: Module exists in database but not filesystem

**Symptom:**
```sql
SELECT name FROM ir_module_module WHERE name = 'ipai_missing_module';
-- Returns row, but addons/ipai_missing_module doesn't exist
```

**Resolution:**
```sql
-- If never installed (state='uninstalled'), safe to delete
DELETE FROM ir_module_module WHERE name = 'ipai_missing_module' AND state = 'uninstalled';

-- If installed, need uninstall workflow (data destructive)
-- Contact DevOps before proceeding
```

### Issue: Legacy module accidentally committed

**Symptom:** PR fails with CI gate error

**Resolution:**
```bash
# Remove from filesystem
rm -rf addons/ipai_legacy_module

# Remove from git history
git rm -r addons/ipai_legacy_module

# Amend commit or create new one
git commit --amend --no-edit

# Force push (only if on feature branch)
git push --force-with-lease origin feature-branch-name
```

---

## Related Documentation

- Enterprise Bridge module: `addons/ipai_enterprise_bridge/README.md`
- CI gate script: `scripts/ci/deny_legacy_ipai_modules.sh`
- GitHub workflow: `.github/workflows/ipai-module-gate.yml`
- Docker SSOT: `docs/DOCKER_SSOT_ARCHITECTURE.md`
- Infrastructure SSOT: `INFRASTRUCTURE_SSOT.yaml`
