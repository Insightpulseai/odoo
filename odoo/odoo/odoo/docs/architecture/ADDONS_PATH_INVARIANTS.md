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

## Parity Boundary Baseline

The check uses a baseline to avoid perma-warn noise:
- **Baseline file**: `scripts/ci/parity_boundaries.baseline.txt`
- **CI behavior**: Fails only on NEW warnings (not in baseline)
- **Update baseline**: When intentionally adding ipai_* modules without justification:
  ```bash
  bash scripts/ci/check_parity_boundaries.sh 2>&1 | \
    grep '^WARN:' | \
    sort > scripts/ci/parity_boundaries.baseline.txt
  git add scripts/ci/parity_boundaries.baseline.txt
  git commit -m "chore(ci): update parity boundary baseline"
  ```

## Reason Codes

Addons path invariant failures include reason codes for fast CI triage:
- **AP-01**: `working_dir` must be `/workspaces/odoo`
- **AP-02**: Devcontainer must not mount `/mnt/extra-addons`
- **AP-03**: Addons path must not reference host-only paths
