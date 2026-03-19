# Asset Bundle Contract

> Rules for Odoo frontend asset declarations, bundle ownership, and CI enforcement.

## Placement Rules

1. All custom frontend assets must live under `static/src/` within the declaring module
2. Only declare assets from files committed in the same repo
3. No hidden dependency on local/untracked files
4. No absolute paths or paths outside the module's own directory

## Bundle Rules

1. Use standard Odoo bundle keys: `web.assets_backend`, `web.assets_frontend`, `web.assets_common`, `website.assets_frontend`, etc.
2. Do not mix deprecated and current bundle names
3. Use bundle inheritance intentionally — document why if overriding a core bundle
4. Module-scoped bundles (e.g. `my_module.assets_backend`) are acceptable for isolated frontend features

## Declaration Rules

1. The `assets` key in `__manifest__.py` must be a dict of `string -> list[string]`
2. Every path in the list must resolve to an existing file on disk
3. Paths must follow format: `<module_name>/static/src/<subpath>`
4. No duplicate entries within the same bundle across `ipai_*` modules
5. Valid extensions: `.js`, `.css`, `.scss`, `.xml`, `.less`

## Ownership Boundaries

Each `ipai_*` module owns its own asset contributions. Cross-module asset dependencies must be declared via `depends` in the manifest, not via direct path references.

| Surface | Bundle Key | Typical Contributors |
|---------|-----------|---------------------|
| Backend (web client) | `web.assets_backend` | `ipai_odoo_copilot`, `ipai_finance_ppm` |
| Frontend (public) | `web.assets_frontend` | theme modules |
| Website editor | `website.assets_editor` | theme modules |
| POS | `point_of_sale.assets` | (none currently) |

## Testing Requirements

Every module declaring `assets` in its manifest must pass:

1. **Asset contract test** (`tests/test_odoo_asset_contract.py`) — validates paths, bundle keys, duplicates
2. **Web smoke test** (`tests/test_web_asset_smoke.py`) — validates runtime asset bundling against a live instance
3. **Module install test** — module installs cleanly on a disposable DB

## CI Enforcement

The `.github/workflows/odoo-asset-contract.yml` workflow runs on every PR that touches:
- `__manifest__.py`
- `static/src/**`
- `views/**`

It fails the PR if:
- Any asset path is missing
- Any bundle key is invalid
- Any duplicate asset entry exists
- Any installable module has missing data files

## Common Failure Causes

| Cause | Symptom | Fix |
|-------|---------|-----|
| File renamed, manifest not updated | `AssetError` at runtime | Update path in `__manifest__.py` |
| JS module syntax mismatch | `SyntaxError` in browser console | Match Odoo 19 OWL/ES module format |
| Duplicate registration | Asset loaded twice, UI glitch | Remove duplicate from one manifest |
| Wrong bundle key | Asset not loaded | Use correct Odoo bundle name |
| Missing `depends` | Asset loads before dependency | Add dependency module to `depends` |
| Stale browser cache | Works after hard refresh | Clear cache; not a code issue |
