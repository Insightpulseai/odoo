# Deprecated Addons Policy

**Effective**: 2026-02-14
**Authority**: `spec/repo-chores/constitution.md`

---

## Purpose

Deprecated Odoo addons are quarantined in `addons/_deprecated/` rather than deleted.
This preserves git history while preventing accidental installation or reference.

## Rules

1. **Move, don't delete.** When deprecating a module, `git mv` it to `addons/_deprecated/<module_name>/`.
2. **CI blocks references.** The `validate_no_deprecated_installed.sh` script (run in CI) fails if any deprecated module appears in:
   - Install set scripts (`scripts/odoo_install_modules.sh`, etc.)
   - CI workflow install commands
   - Docker compose environment variables (`ODOO_INSTALL_MODULES`, etc.)
   - `__manifest__.py` dependencies of active modules
3. **No resurrection without PR.** Moving a module back out of `_deprecated/` requires a PR with rationale.
4. **Manifest must be neutered.** Deprecated modules should have `"installable": False` in their `__manifest__.py`.

## Currently Deprecated Modules

| Module | Deprecated Date | Reason | Replacement |
|--------|----------------|--------|-------------|
| *(none yet)* | | | |

## How to Deprecate a Module

```bash
# 1. Move to quarantine
git mv addons/<module_name> addons/_deprecated/<module_name>

# 2. Set installable to False in manifest
# Edit addons/_deprecated/<module_name>/__manifest__.py
# Change "installable": True -> "installable": False

# 3. Update this table above

# 4. Commit
git add -A && git commit -m "chore(repo): deprecate <module_name>"
```

## Validation

```bash
# Run locally
./scripts/validate_no_deprecated_installed.sh

# CI runs this automatically on PRs
```
