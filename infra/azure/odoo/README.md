# Odoo-only Azure footprint

## Purpose

This stack codifies only the Azure footprint required to run Odoo CE 18.

It does not own:
- Databricks / Unity Catalog
- Non-Odoo container apps
- Broader platform/shared services outside the Odoo runtime contract
- AI Foundry / Cognitive Services
- Networking / VNet / Private Endpoints

## Design rules

1. Adopt existing canonical resource names where they already exist.
2. Do not rename or replace existing shared/data/platform resources.
3. Apply one tag contract to every managed resource.
4. Keep the stack small and environment-scoped.
5. Cross-subscription resources (PG, ACR on sponsored sub) are referenced by FQDN, not managed.

## Current scope

| Module | Type | Purpose |
|---|---|---|
| `aca-env.bicep` | Reference | Existing ACA managed environment |
| `aca-odoo-apps.bicep` | **Managed** | Odoo web + worker + cron container apps |
| `postgres-ref.bicep` | Reference | Existing PostgreSQL flexible server |
| `keyvault-ref.bicep` | Reference | Existing Key Vault |
| `monitoring-ref.bicep` | Reference | Existing Log Analytics workspace |
| `managed-identity-ref.bicep` | Reference | Existing user-assigned managed identity |

## Canonical resource names

| Resource | Name | RG | Sub |
|---|---|---|---|
| ACA Environment | `ipai-odoo-dev-env-v2` | `rg-ipai-dev-odoo-runtime` | Sub 1 |
| Odoo Web | `ipai-odoo-dev-web` | `rg-ipai-dev-odoo-runtime` | Sub 1 |
| Odoo Worker | `ipai-odoo-dev-worker` | `rg-ipai-dev-odoo-runtime` | Sub 1 |
| Odoo Cron | `ipai-odoo-dev-cron` | `rg-ipai-dev-odoo-runtime` | Sub 1 |
| PostgreSQL | `pg-ipai-odoo` | `rg-ipai-data-sea` | Sponsored |
| ACR | `acripaiodoo` | `rg-ipai-shared` | Sponsored |
| Key Vault | `kv-ipai-dev` | `rg-ipai-dev-platform` | Sub 1 |
| Managed Identity | `id-ipai-dev` | `rg-ipai-dev-odoo-runtime` | Sub 1 |
| Log Analytics | `la-ipai-odoo-dev` | `rg-ipai-dev-odoo-runtime` | Sub 1 |

## Tag contract

All managed resources inherit the same tag object from the parameters file.
SSOT: `ssot/azure/odoo-footprint.yaml`.

## Deployment

```bash
az deployment group create \
  --resource-group rg-ipai-dev-odoo-runtime \
  --template-file infra/azure/odoo/main.bicep \
  --parameters infra/azure/odoo/main.dev.bicepparam
```
