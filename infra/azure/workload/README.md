# Azure Workload Definitions

Workload-specific Azure Container Apps, ACR, and PostgreSQL definitions.

## Container Apps

Runtime environment: `ipai-odoo-dev-env` in `rg-ipai-dev-odoo-runtime`
Domain: `salmontree-b7d27e19.southeastasia.azurecontainerapps.io`

## Container Registry

Primary: `acripaiodoo` (formerly `ipaiodoodevacr`)

## PostgreSQL

Primary: `pg-ipai-odoo` (General Purpose, Fabric mirroring enabled)
Database: `odoo` (production), `odoo_staging`, `odoo_dev`

## Convention

- ACA definitions as Bicep modules in `infra/azure/modules/`
- Image tags: `latest` for dev, semver for staging/prod
- Health probes required on all ACA apps

<!-- TODO: Consolidate existing Bicep modules under this directory -->
