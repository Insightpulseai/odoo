# GitHub Cleanup Decision Log — 2026-03-18

## Summary

Full decommission of GitHub Actions. Azure DevOps is the sole CI/CD system.

## Workflows removed (20)

All workflow YAML files under `.github/workflows/` were deleted.

| Workflow | Category | Rationale |
|----------|----------|-----------|
| `ci-odoo.yml` | CI validation | Superseded by AzDO `ci-validation` pipeline |
| `codeql.yml` | Security | Will be replaced by AzDO security scanning or GHAS direct |
| `deploy-azure.yml` | Deploy | Superseded by AzDO `runtime-delivery` pipeline |
| `devcontainer-drift-guard.yml` | Contract | Superseded by AzDO `ci-validation` ConfigValidation stage |
| `enterprise-okrs-ssot-check.yml` | SSOT | Superseded by AzDO `ci-validation` SSOTValidation stage |
| `file-taxonomy-check.yml` | Contract | Superseded by AzDO `ci-validation` RepoSanity stage |
| `integrations-ssot-check.yml` | SSOT | Superseded by AzDO `ci-validation` SSOTValidation stage |
| `naming-drift-check.yml` | Contract | Superseded by AzDO `ci-validation` RepoSanity stage |
| `odoo-asset-contract.yml` | Contract | Superseded by AzDO `ci-validation` |
| `odoo-auto-upgrade.yml` | Deploy | Superseded by AzDO `runtime-delivery` pipeline |
| `odoo-module-install.yml` | Deploy | Superseded by AzDO `runtime-delivery` pipeline |
| `odoo-runtime-contract.yml` | Contract | Superseded by AzDO `ci-validation` |
| `planning-index-ssot-check.yml` | SSOT | Superseded by AzDO `ci-validation` SSOTValidation stage |
| `platform-strategy-ssot-check.yml` | SSOT | Superseded by AzDO `ci-validation` SSOTValidation stage |
| `pr-preview.yml` | Deploy | No longer needed — Azure-native previews |
| `prod-asset-health.yml` | Health | Superseded by AzDO `quality-governance` pipeline |
| `repo-boundary-check.yml` | Contract | Superseded by AzDO `ci-validation` RepoSanity stage |
| `spec-kit-enforce.yml` | Contract | Superseded by AzDO `ci-validation` |
| `ssot-ai-validate.yml` | SSOT | Superseded by AzDO `ci-validation` SSOTValidation stage |
| `supabase-self-host-migration.yml` | Migration | One-time migration; complete or re-implement in AzDO |

## Workflows kept

None. Zero workflow YAML files remain.

## PRs affected

| PR | Action | Reason |
|----|--------|--------|
| #605 | Close/supersede | Its intent (remove GHA workflows) is now fulfilled by this decommission |
| #609 | Keep open | Docs/governance normalization — not GHA-specific |
| #604 | Keep open | Architecture specs — not GHA-specific |
| #610-614 | Close | Dependabot GHA dependency bumps — no longer applicable |
| #607, #608 | Keep open | Module cleanup — not GHA-specific |

## Branches to clean

Stale branches backing closed PRs should be deleted after PR closure.

## Issues updated

| Issue | Action |
|-------|--------|
| #567 | Keep open — historical AzDO pipeline authorization |
| #615 | Keep open — current AzDO CI regression |
