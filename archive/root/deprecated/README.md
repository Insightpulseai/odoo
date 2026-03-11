# Archived Deprecated Modules

These modules have been deprecated and archived as part of the EE parity consolidation.

## Why Archived

- `ipai_theme_tbwa_backend`: Replaced by `ipai_theme_tbwa`

## Data Migration

No data migration needed - these modules had no production data.

## Restoration

If you need to restore a module:

```bash
git mv archive/deprecated/<module_name> addons/ipai/
```

Then update the manifest to set `installable: True`.

---

*Archived: 2026-01-28*
*Deprecation Plan: docs/DEPRECATION_PLAN.md*
