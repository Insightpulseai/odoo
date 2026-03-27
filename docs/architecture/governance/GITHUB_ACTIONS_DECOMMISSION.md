# GitHub Actions Decommission — 2026-03-18

## Decision

GitHub Actions is fully decommissioned for this repository.

## Reason

The repository will no longer rely on GitHub Actions for CI/CD, automation, or governance checks due to unresolved billing/operational issues and the decision to make Azure DevOps the sole CI/CD execution system.

## Effective policy

- No active workflow YAML files remain under `.github/workflows/`
- Azure DevOps is the canonical CI/CD and deployment system
- GitHub remains the source-control and pull-request system of record
- Any future automation must be implemented in Azure DevOps or another explicitly approved system, not GitHub Actions

## Removed workflows (20 total)

| Workflow | Category |
|----------|----------|
| `ci-odoo.yml` | CI validation |
| `codeql.yml` | Security scanning |
| `deploy-azure.yml` | Deployment |
| `devcontainer-drift-guard.yml` | Contract check |
| `enterprise-okrs-ssot-check.yml` | SSOT validation |
| `file-taxonomy-check.yml` | Contract check |
| `integrations-ssot-check.yml` | SSOT validation |
| `naming-drift-check.yml` | Contract check |
| `odoo-asset-contract.yml` | Contract check |
| `odoo-auto-upgrade.yml` | Deployment |
| `odoo-module-install.yml` | Deployment |
| `odoo-runtime-contract.yml` | Contract check |
| `planning-index-ssot-check.yml` | SSOT validation |
| `platform-strategy-ssot-check.yml` | SSOT validation |
| `pr-preview.yml` | Deployment |
| `prod-asset-health.yml` | Health check |
| `repo-boundary-check.yml` | Contract check |
| `spec-kit-enforce.yml` | Contract check |
| `ssot-ai-validate.yml` | SSOT validation |
| `supabase-self-host-migration.yml` | Migration |

## Implications

- Historical GitHub Actions runs may still appear in GitHub UI, but no new runs should be created
- All validation responsibilities are now owned by Azure DevOps pipelines
- Contract/SSOT checks that were GitHub-native must be re-implemented in Azure DevOps `ci-validation` pipeline

## Follow-up requirements

1. Ensure Azure DevOps `ci-validation` covers any still-required validation responsibilities
2. Update repo governance docs so they do not mention GitHub Actions as an active execution surface
3. Close or supersede any open PRs whose sole purpose was GitHub Actions cleanup or migration

## Related

- Issue #615: Azure DevOps CI fast-fail bootstrap regression
- Issue #567: Azure DevOps pipeline authorization (historical)
- PR #605: chore(ci): remove all GHA workflows (superseded by this decommission)
