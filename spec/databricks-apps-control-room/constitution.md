# Databricks Apps Control Room — Constitution

> Architectural boundaries for Databricks Apps within InsightPulse AI.

## Scope: Data-Plane Applications Only

Databricks Apps is bounded to applications that:
- Live close to data (Unity Catalog governed)
- Read from bronze/silver/gold medallion layers
- Serve data engineers, analysts, and platform team
- Are deployed via Databricks Asset Bundles (DABs)

## What Deploys on Databricks Apps

| Category | Examples | Why Here |
|----------|---------|----------|
| Connector monitoring | Sync status, failure alerts, replay triggers | Reads connector state tables directly |
| Data quality | DQ score dashboards, validation reports | Reads DQ check results from gold layer |
| Analyst tools | Ad-hoc query interfaces, data exploration | Direct Spark SQL access |
| Pipeline monitoring | DLT pipeline status, lineage views | Databricks-native observability |

## What Does NOT Deploy on Databricks Apps

| Category | Where Instead | Why |
|----------|--------------|-----|
| Customer-facing web | Vercel | Edge performance, Next.js |
| ERP workflows | Odoo (DigitalOcean) | System of truth, business logic |
| Agent runtime | Azure Container Apps | Scalable compute, event-driven |
| Business BI | Superset | Non-technical users, broader access |
| Webhooks/APIs | Azure Container Apps / DO | HTTP-first workloads |

## Deployment Rules

1. **DABs only**: All Databricks Apps deployed via `infra/databricks/` bundle
2. **Unity Catalog governed**: All data access through UC permissions
3. **No direct writes to Odoo**: Read from bronze/silver replicas, never write back
4. **SSO auth**: Databricks workspace SSO, no separate auth layer
5. **Streamlit/Gradio**: Preferred UI frameworks for data apps
6. **Version controlled**: App code lives in `infra/databricks/src/apps/`

## Data Access Pattern

```
Databricks App → Unity Catalog → Bronze/Silver/Gold tables
                                 ↑
                    Connectors sync from source systems
                    (Odoo PG, Notion, GitHub, Azure RG)
```

Apps NEVER access source systems directly. Always read from medallion layers.
