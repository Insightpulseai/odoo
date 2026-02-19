# Addons Path Invariants

## Canonical Dev Root

The devcontainer workspace root is `/workspaces/odoo`.
All Odoo addons in the devcontainer MUST be loaded from `/workspaces/odoo/addons/*`.

## Invariants (CI-enforced)

1. No tracked file (except allowlisted base configs) may reference `/mnt/extra-addons` as a runtime path
2. `.devcontainer/docker-compose.devcontainer.yml` MUST NOT mount addons separately
3. `--addons-path` in devcontainer command MUST use `/workspaces/odoo/addons/*`
4. `working_dir: /workspaces/odoo` MUST be present in the devcontainer overlay

## Exceptions (not enforced)

- `docker-compose.yml` (base): uses `/mnt/extra-addons` for production/CI use ✅
- `config/dev/odoo.conf`: uses `/mnt/oca` — overridden by devcontainer `--addons-path` args ✅

## ipai_* Namespace Policy

`ipai_*` module namespace is **reserved for Integration Bridge connectors only**.
EE-parity modules MUST live under `addons/oca/*`.
See `spec/odoo-ee-parity-seed/constitution.md` for full policy.
