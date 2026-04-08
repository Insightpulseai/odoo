# Staging Environment Overlay

Staging environment configuration overlay. Mirrors production topology at reduced scale.

## Scope

- Database: `odoo_staging` on `pg-ipai-odoo`
- Key Vault: `kv-ipai-staging`

## Convention

- Staging mirrors prod ACA app topology
- Auto-scaling: min 1, max 2 for critical apps
- Secrets from `kv-ipai-staging`
- Deployment gate: staging must pass smoke tests before prod promotion

<!-- TODO: Add environment-specific parameter files -->
