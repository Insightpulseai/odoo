# CI Configuration

## Core Modules Allowlist

`odoo_core_addons_allowlist.txt` contains the canonical list of Odoo CE 19.0 core modules used for manifest validation.

### Purpose

This file is used by `scripts/validate_manifest.py` when an Odoo instance is not running (e.g., in CI environments). It ensures that all legitimate core module dependencies are recognized during manifest validation, preventing false-positive failures.

### Usage

The validator script automatically loads this file when:
- Odoo is not running at `http://localhost:8069`
- Connection to Odoo fails for any reason
- Running in CI environment (GitHub Actions)

### Maintenance

**Update when:**
- Upgrading to new Odoo versions (new core modules may be added)
- Core module list changes in Odoo CE releases

**How to update:**
1. Check `scripts/ce_oca_audit.py` for current `CE_CORE_MODULES` set
2. Extract module names: `python3 -c "from scripts.ce_oca_audit import CE_CORE_MODULES; print('\n'.join(sorted(CE_CORE_MODULES)))"`
3. Update `odoo_core_addons_allowlist.txt` with new modules
4. Run validation test: `python scripts/validate_manifest.py`

**Source of truth:** `scripts/ce_oca_audit.py` `CE_CORE_MODULES` set

**Last verified:** 2026-02-13 (Odoo CE 19.0)

### Module Count

- Current: 68 core modules
- Includes: Standard Odoo CE modules (account, hr, sale, etc.)

### CI Integration

Used by `.github/workflows/ci.yml` in the "Preflight Checks" job:

```yaml
- name: Validate Manifest Icons
  # Uses ci/odoo_core_addons_allowlist.txt for core module recognition
  run: python scripts/validate_manifest.py
```

This eliminates the need to start an Odoo instance in CI just for manifest validation, improving:
- **Speed**: No 30-60s Odoo startup overhead
- **Reliability**: No database/service dependencies
- **Cost**: Reduced CI runner resource usage
