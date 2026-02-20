# OCA Module Porting Runbook: 18.0 → 19.0

> Canonical workflow for porting OCA modules to Odoo 19.0 following OCA maintainer-tools migration guide.
> Reference: https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-19.0

---

## Overview

This runbook documents the OCA canonical method for migrating modules from 18.0 to 19.0 using:
- `git format-patch` to extract module commits from 18.0 branch
- `git am` to apply patches to 19.0 branch
- `pre-commit` for automated framework updates
- Manual fixups for API changes not handled by automation

**Expected Effort**: 30min - 4 hours per module (simple → complex)

---

## Prerequisites

### Local Setup

```bash
# Install pre-commit (handles many Odoo 19 framework changes automatically)
pip install pre-commit

# Verify git configured
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# OCA commit access (if pushing upstream)
# Fork repo to your GitHub account if contributing
```

### Repository Context

- **Port Queue**: `config/oca/port_queue.yml` (SSOT for porting backlog)
- **Vendored Repos**: `addons/oca/<repo>/` (where ported modules land locally)
- **Scripts**: `scripts/oca/port_to_19.sh` (automated harness)
- **Inventory**: `docs/oca/ADDON_INVENTORY.json` (available modules per repo)

---

## Canonical Porting Workflow

### Step 1: Pick Module from Queue

```bash
# Read port queue
cat config/oca/port_queue.yml | yq '.queues.P0[] | .addon + " (" + .repo + ")"'

# Pick next unported module (prioritize P0 → P1 → P2)
# Example: server_environment from server-env repo
```

### Step 2: Clone OCA Repository

```bash
# Clone 19.0 branch
git clone -b 19.0 https://github.com/OCA/<repo-name>
cd <repo-name>

# Verify branch
git branch --show-current  # Should show: 19.0

# Check if module exists
ls <module-name>/  # Should not exist yet (we're porting it)
```

### Step 3: Create Migration Branch

```bash
# OCA naming convention: 19.0-mig-<module>
git checkout -b 19.0-mig-<module>

# Example:
git checkout -b 19.0-mig-server_environment
```

### Step 4: Extract Patches from 18.0

```bash
# Format patches from 18.0 branch limited to module directory
# --relative ensures paths are module-relative (critical for clean apply)
git format-patch --relative=<module> origin/18.0..origin/19.0 -- <module>/

# Example:
git format-patch --relative=server_environment origin/18.0..origin/19.0 -- server_environment/

# This creates numbered patch files: 0001-*.patch, 0002-*.patch, etc.
# If no patches: module doesn't exist in 18.0, cannot port this way
```

### Step 5: Apply Patches to 19.0

```bash
# Apply patches with 3-way merge and keep commit messages
git am -3 --keep *.patch

# Common issues:
# - Whitespace conflicts: Add --ignore-whitespace flag
# - Context mismatches: Resolve manually, then: git am --continue
# - No patches created: Module doesn't exist in 18.0, may need manual port

# If conflicts occur:
# 1. Edit conflicted files (git marks conflicts with <<<<<<< markers)
# 2. git add <fixed-files>
# 3. git am --continue

# To abort: git am --abort
```

### Step 6: Run Pre-Commit Auto-Fixes

Pre-commit handles many Odoo 19 framework changes automatically:

```bash
# Run all pre-commit hooks
pre-commit run -a

# Common auto-fixes:
# - groups_id → group_ids (field rename)
# - self._cr → self.env.cr (cursor access)
# - self._uid → self.env.uid (user ID access)
# - XML view updates
# - Python formatting (black, isort, flake8)
```

**If pre-commit makes changes**:

```bash
# Stage pre-commit fixes
git add .

# Commit with --no-verify (pre-commit already ran)
git commit -m "[IMP] <module>: pre-commit auto fixes" --no-verify
```

### Step 7: Manual Framework Updates

Pre-commit doesn't catch everything. Check for these Odoo 19 changes:

#### API Changes

| Old (18.0) | New (19.0) | Scope |
|------------|-----------|-------|
| `groups_id` | `group_ids` | Security groups (many2many field rename) |
| `self._cr` | `self.env.cr` | Database cursor access |
| `self._uid` | `self.env.uid` | User ID access |
| `self._context` | `self.env.context` | Context access |
| `@api.multi` | Remove decorator | All multi-record methods (decorator no longer needed) |
| `@api.returns('self')` | Remove decorator | Methods returning recordsets |

#### View Updates

```xml
<!-- Old: groups_id -->
<field name="groups_id" eval="[(4, ref('base.group_user'))]"/>

<!-- New: group_ids -->
<field name="group_ids" eval="[(4, ref('base.group_user'))]"/>
```

#### Python Framework Changes

```python
# Old: Direct cursor access
def _old_method(self):
    self._cr.execute("SELECT * FROM table")

# New: Environment cursor
def _new_method(self):
    self.env.cr.execute("SELECT * FROM table")

# Old: api.multi decorator
@api.multi
def compute_total(self):
    for record in self:
        # ...

# New: No decorator needed
def compute_total(self):
    for record in self:
        # ...
```

#### Test Updates

- Remove `odoo.tests.common.TransactionCase` → Use `odoo.tests.TransactionCase`
- Update form view usage if using `Form` helper
- Check for deprecated test decorators

### Step 8: Update Dependencies

Check `__manifest__.py`:

```python
{
    'name': 'Module Name',
    'version': '19.0.1.0.0',  # Update version to 19.0.x.y.z
    'depends': [
        # Verify all dependencies are available in 19.0
        # Check config/oca/port_queue.yml for ported status
    ],
    # ...
}
```

### Step 9: Test Installation

```bash
# From repo root, run Odoo with test database
odoo-bin -i <module> --stop-after-init --database odoo_test

# Check for:
# - Module installs without errors
# - No deprecation warnings
# - Views render correctly
```

### Step 10: Run Module Tests

```bash
# Run module tests
odoo-bin -i <module> --test-enable --stop-after-init --database odoo_test

# Tests must pass before considering port complete
```

### Step 11: Update Port Queue

```bash
# Edit config/oca/port_queue.yml
# Change status from "missing" to "in_progress" or "complete"
# Add notes about issues encountered

# Example:
# - addon: server_environment
#   status: complete  # Changed from: missing
#   notes:
#     porting_notes: "Required manual fix for server_env_mixin API change"
#     porting_date: "2026-02-20"
```

---

## Definition of Done

A module port is considered **complete** when:

1. ✅ Module exists in `addons/oca/<repo>/<module>/`
2. ✅ Passes install: `odoo-bin -i <module> --stop-after-init`
3. ✅ All tests green: `odoo-bin --test-enable -i <module>`
4. ✅ No deprecation warnings in logs
5. ✅ Views render without errors
6. ✅ Port queue updated with status=complete
7. ✅ (Optional) PR submitted to upstream OCA repo

---

## Common Issues & Solutions

### Issue: No Patches Created

**Symptom**: `git format-patch` returns no files

**Cause**: Module doesn't exist in 18.0 branch

**Solution**: Cannot use patch method. Options:
1. Check if module exists in earlier version (17.0, 16.0) and port from there
2. Create module from scratch following OCA templates
3. Mark as "abandoned" in port queue if no upstream version exists

### Issue: Patch Apply Fails (Conflicts)

**Symptom**: `git am` fails with merge conflicts

**Cause**: 19.0 branch has diverged significantly from 18.0

**Solution**:
```bash
# Add --ignore-whitespace for whitespace-only conflicts
git am -3 --keep --ignore-whitespace *.patch

# For actual conflicts:
# 1. Edit files manually (look for <<<<<<< markers)
# 2. git add <fixed-files>
# 3. git am --continue
```

### Issue: Dependency Chain Unsatisfiable

**Symptom**: Module depends on unported modules

**Cause**: Dependencies not yet available in 19.0

**Solution**:
1. Check `config/oca/port_queue.yml` for dependency status
2. Port dependencies first (P0 modules often block others)
3. If dependency is "uninstallable", may need to wait for upstream fix

### Issue: Tests Fail After Port

**Symptom**: Module installs but tests fail

**Common Causes**:
- Test database state issues (try fresh DB)
- API changes not caught by pre-commit
- Test assertions need updates for new behavior
- Mock/patch targets changed in 19.0

**Solution**:
1. Read test failures carefully (often point to exact API change needed)
2. Check OCA maintainer-tools wiki for known test issues
3. Compare with similar modules already ported to 19.0

---

## Odoo 19.0 Framework Changes Reference

### Field Renames

- `groups_id` → `group_ids` (security groups, many2many)
- `category_id` → `categ_id` (in some models, check deprecation warnings)

### Environment Access

All env-related attributes now accessed via `self.env.*`:

```python
# Old                    # New
self._cr            →    self.env.cr
self._uid           →    self.env.uid
self._context       →    self.env.context
self.env.user.id    →    self.env.uid  (equivalent)
```

### Removed Decorators

- `@api.multi` - Removed (all methods are multi by default)
- `@api.returns('self')` - Removed for recordset returns
- `@api.one` - Removed (use multi-record pattern)

### ORM Changes

- `write()` now returns `True` instead of recordset (check code expecting return value)
- `create()` behavior unchanged (still returns recordset)
- Search domains: no changes for 19.0

### View Changes

- Group field: `groups_id` → `group_ids` in XML
- No major structural changes to views in 19.0

---

## Automated Porting Harness

Use the provided script for repetitive steps:

```bash
# Automated porting workflow
./scripts/oca/port_to_19.sh <repo> <module>

# Example:
./scripts/oca/port_to_19.sh server-env server_environment

# Script handles:
# - Clone repo
# - Create migration branch
# - Extract patches
# - Apply patches
# - Run pre-commit
# - Print next steps for manual review
```

---

## Contributing Ports Upstream

If porting for OCA contribution (not just local use):

1. **Fork OCA repo** to your GitHub account
2. **Push migration branch** to your fork
3. **Create PR** to OCA repo with title: `[MIG] <module>: migration to 19.0`
4. **PR description template**:
   ```
   Migration of <module> from 18.0 to 19.0

   Changes:
   - Applied patches via git format-patch / git am
   - Pre-commit auto-fixes for framework changes
   - Manual updates: [describe any manual changes]

   Testing:
   - [x] Module installs without errors
   - [x] All tests pass
   - [x] No deprecation warnings

   Related: OCA/<repo>#<issue-number> (if tracking issue exists)
   ```

5. **Wait for OCA maintainer review** (may take days/weeks)
6. **Address review feedback** if requested

---

## Next Steps After Porting

1. **Update allowlist**: Add module to `config/oca/module_allowlist.yml` if ready for CI
2. **Run install script**: `./scripts/oca/install_from_allowlist.sh` to verify in clean env
3. **Update documentation**: Note any breaking changes or migration gotchas
4. **Port dependent modules**: Check port queue for modules that depend on this one

---

## References

- [OCA Maintainer Tools Migration Guide](https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-19.0)
- [Odoo 19.0 Release Notes](https://www.odoo.com/odoo-19-release-notes)
- [OCA Module Template](https://github.com/OCA/maintainer-tools/tree/master/template)
- Port Queue SSOT: `config/oca/port_queue.yml`
- Porting Harness: `scripts/oca/port_to_19.sh`

---

*Last Updated: 2026-02-20*
