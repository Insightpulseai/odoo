# Prod Environment Overlay

Production environment configuration overlay. Highest availability and security requirements.

## Scope

- Database: `odoo` on `pg-ipai-odoo`
- Key Vault: `kv-ipai-prod`

## Convention

- General Purpose SKUs for all data services
- Auto-scaling: min 1, max 3 for critical apps
- Secrets from `kv-ipai-prod`
- Deployment requires release gate approval
- Fabric mirroring enabled for analytics

<!-- TODO: Add environment-specific parameter files -->
