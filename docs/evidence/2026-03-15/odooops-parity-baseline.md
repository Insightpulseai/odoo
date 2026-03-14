# OdooOps Parity Baseline

> Date: 2026-03-15
> Evidence type: baseline parity snapshot

## Purpose

Capture the current baseline status of the Odoo runtime against the Azure Odoo.sh-equivalent target-state contract.

## Canonical Naming Alignment

| Type | Name | Status |
|------|------|--------|
| Dev DB | `odoo_dev` | Aligned |
| Demo DB | `odoo_dev_demo` | Aligned |
| Staging DB | `odoo_staging` | Aligned |
| Production DB | `odoo` | Aligned |
| Dev env label | `odoo-dev` | Aligned |
| Staging env label | `odoo-staging` | Aligned |
| Production env label | `odoo-production` | Aligned |

## Current Strengths

- Repo-owned Odoo runtime and addon structure exists
- Addon manifests are discoverable from source control
- Python dependency declaration pattern exists
- Submodule-based addon dependency model is compatible
- Local/dev runtime discipline exists (`config/dev/odoo.conf`)
- Production config exists (`config/prod/odoo.conf`)
- Staging config exists (`config/staging/odoo.conf`)
- Per-environment feature flags exist (`config/*/features.yaml`)
- Environment contracts documented (`config/*/env.contract.md`)
- Environment index documented (`config/ENVIRONMENTS.md`)

## Current Gaps

| Capability | Status | Notes |
|---|---|---|
| Addon discovery from repo | pass | Manifests under `addons/**` |
| Python dependencies declared in repo | pass | `requirements.txt` contract |
| Git submodule dependency model | pass | Compatible with addon strategy |
| Canonical database naming | pass | `odoo_dev` / `odoo_staging` / `odoo` |
| Dev runtime workflow | partial | Functional, not fully normalized |
| Staging refresh from neutralized prod | missing | Must be implemented and evidenced |
| Non-prod mail suppression | partial | Config exists, not yet operationally proven |
| Non-prod cron control | missing | Must be stage-aware and evidenced |
| Backup / restore rehearsal | missing | Must be executed and documented |
| Release evidence pack standardization | partial | Evidence exists, not normalized |
| Runtime contract CI enforcement | added | `odoo-runtime-contract.yml` |

## Evidence Produced

This patch contributes:

- `docs/architecture/AZURE_ODOOSH_EQUIVALENT_TARGET_STATE.md`
- `docs/architecture/RUNTIME_CONTRACT_AZURE_ODOO.md`
- `docs/operations/ODOOSH_CAPABILITY_PARITY_MATRIX.md`
- `docs/runbooks/BRANCH_PROMOTION_AND_STAGING_REFRESH.md`
- `ssot/governance/odooops-capabilities.yaml`
- `ssot/governance/azure-odoosh-equivalent.yaml` (updated)
- `config/staging/odoo.conf` + `features.yaml` + `env.contract.md`
- `config/prod/features.yaml` + `env.contract.md`
- `config/ENVIRONMENTS.md`
- `.github/workflows/odoo-runtime-contract.yml`

## Next Required Evidence

1. Staging refresh rehearsal
2. Neutralization checklist result
3. Mail suppression verification
4. Stage-aware cron verification
5. Restore rehearsal result
6. Production promotion evidence tied to release candidate

## Baseline Conclusion

The repo is ready to enforce a runtime contract and is aligned with core repo-first Odoo hosting principles. Main remaining work is operational parity: staged promotion, neutralized staging refresh, non-prod safety controls, and restore/rollback evidence.
