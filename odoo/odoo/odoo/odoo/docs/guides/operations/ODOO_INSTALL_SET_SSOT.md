# Odoo Install Set SSOT (CI Verify)

This repo separates planning/governance from ERP runtime provisioning.

- GitHub Project templates: `ssot/github/projects/templates/*`
- Odoo runtime install sets: `ssot/odoo/install_sets/*`

## Finance PPM install set

Files:

- `ssot/odoo/oca_lock.yaml`
- `ssot/odoo/install_sets/finops_ppm.yaml`
- `addons/ipai_meta/ipai_meta_finops_ppm/__manifest__.py`
- `scripts/odoo/install_set.py`
- `.github/workflows/odoo-install-set-verify.yml`

## CI endpoint (safe mode)

Only dry-run validation is enabled.

```bash
python scripts/odoo/install_set.py \
  --dry-run \
  --set-file ssot/odoo/install_sets/finops_ppm.yaml \
  --oca-lock ssot/odoo/oca_lock.yaml \
  --report artifacts/odoo/install_sets/finops_ppm_report.json
```

`--apply` is intentionally blocked in Endpoint A.

## Report fields

`finops_ppm_report.json` includes:

- `selected_modules`
- `missing_modules`
- `missing_runtime_deps`
- `oca_lock_errors`
- `status` (`ok` or `failed`)

## Notes

- OCA repos are pinned by SHA in `oca_lock.yaml`.
- The meta module is dependency-only (no models/views/data).
- PR CI verifies module availability and static dependency coherence without touching databases.
