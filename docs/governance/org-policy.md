# Org-Level Policy

> Placeholder for organization-wide policy documentation.
> Canonical governance contracts live in `ssot/governance/`.

## Authority References

| Document | Path |
|----------|------|
| Platform authority split | `ssot/governance/platform-authority-split.yaml` |
| CI/CD authority matrix | `ssot/governance/ci-cd-authority-matrix.yaml` |
| Repo delivery disposition | `ssot/governance/repo-delivery-disposition.yaml` |
| Release gates | `ssot/release/release_gates.yaml` |
| Identity contract | `ssot/contracts/identity.yaml` |

## Principles

1. Azure-native only. No Cloudflare, no Supabase, no DigitalOcean.
2. GitHub Actions for CI + web deploys. Azure DevOps for Odoo/Databricks/infra deploys.
3. Secrets in Azure Key Vault, never in source.
4. OCA-first module adoption. Config before OCA before custom `ipai_*`.
5. All production releases pass release gates defined in `ssot/release/release_gates.yaml`.

<!-- TODO: Expand with ratified org policies once governance review is complete -->
