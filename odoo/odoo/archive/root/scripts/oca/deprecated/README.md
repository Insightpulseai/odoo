# Deprecated OCA Install Scripts

These scripts have been **replaced** by `scripts/oca/oca_parity_install.py`.

## Why deprecated?

All three scripts reference `config/oca/module_allowlist.yml` which does not
exist in this repository. They would fail immediately on execution.

The new unified script reads from the canonical SSOT files:
- **Manifest**: `docs/oca/install_manifest.yaml`
- **Allowlist**: `odoo/ssot/oca_installed_allowlist.yaml`

## Migration

| Old command | New command |
|-------------|-------------|
| `./install_from_allowlist.sh` | `python3 scripts/oca/oca_parity_install.py --all` |
| `./install_from_allowlist_docker.sh` | `python3 scripts/oca/oca_parity_install.py --all` |
| `./install_from_allowlist_docker_v2.sh` | `python3 scripts/oca/oca_parity_install.py --all` |

## Selftest (CI-safe, no Odoo required)

```bash
python3 scripts/oca/oca_parity_install.py --selftest
```

## Dry-run preview

```bash
ODOO_DB=odoo_dev python3 scripts/oca/oca_parity_install.py --wave 1 --dry-run
```

## Do not delete these files

Retained for reference only. They are not executed by any CI workflow.
Committed: 2026-02-23
