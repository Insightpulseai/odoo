# Dev Environment Overlay

Development environment configuration overlay. Applied on top of base infrastructure definitions.

## Scope

- Resource group: `rg-ipai-dev-odoo-runtime`
- ACA environment: `ipai-odoo-dev-env`
- Database: `odoo_dev` on `pg-ipai-odoo`
- Key Vault: `kv-ipai-dev`

## Convention

- Dev uses Burstable/Basic SKUs where available
- Auto-scaling: min 0, max 1 for non-critical apps
- Secrets from `kv-ipai-dev`

<!-- TODO: Add environment-specific parameter files -->
