# Odoo ERP SaaS Alone — Minimum Bill of Materials

## Purpose

Define the minimum Azure platform footprint required to run Odoo ERP SaaS alone, without Databricks, Foundry, Fabric, or other adjacent platform services.

## Minimum required components

1. Azure Container Registry
2. Azure Container Apps environment
3. Odoo web container app
4. Odoo worker container app
5. Odoo cron container app
6. Azure Database for PostgreSQL Flexible Server
7. Azure Key Vault
8. Canonical ERP DNS + HTTPS

## Minimum runtime topology

- `web`
- `worker`
- `cron`

A deployment is not considered complete if only the web app exists.

## Canonical public entrypoint

- `erp.insightpulseai.com`

## Explicit exclusions

This minimum BOM does not include:

- Databricks
- Fabric / Power BI
- Foundry
- Prismalab
- non-ERP browser apps
- public marketing surfaces

## Notes

This is the minimum production-capable Odoo SaaS footprint, not the full InsightPulseAI platform.
