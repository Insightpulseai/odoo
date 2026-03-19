# Addons Manifest System

## Current SSOT

**`config/addons.manifest.yaml`** is the canonical curated addons manifest.

- **Contract**: `docs/contracts/ADDONS_MANIFEST_CONTRACT.md` (C-27)
- **Validator**: `scripts/odoo/validate_addons_manifest.py`
- **CI gate**: `.github/workflows/addons-manifest-guard.yml`
- **OCA hydration**: `gitaggregate -c oca-aggregate.yml`

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/verify_oca_ipai_layout.sh` | Check OCA repo dirs + must-have modules against manifest |
| `scripts/ocadev/parse_manifest.sh` | Extract must-have modules as comma-separated list |
| `scripts/clone_missing_oca_repos.sh` | Clone missing OCA repos (prefer `gitaggregate` for production) |
| `scripts/odoo/validate_addons_manifest.py` | Full manifest validation (CI) |

## Update flow

1. Edit `config/addons.manifest.yaml`
2. Update `oca-aggregate.yml` if adding/removing repos
3. Run: `gitaggregate -c oca-aggregate.yml`
4. Run: `python scripts/odoo/validate_addons_manifest.py --check-hydrated -v`
5. Commit all changed files together

## Deprecated

- `config/addons_manifest.oca_ipai.json` — removed (targeted Odoo 18, superseded by YAML manifest)
- `addons.manifest.json` (root) — devcontainer mount declarations, separate scope
