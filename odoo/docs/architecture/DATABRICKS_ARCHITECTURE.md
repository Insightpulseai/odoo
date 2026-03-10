# Databricks Architecture -- InsightPulse AI

> Last updated: 2026-03-05
>
> This document separates **verified current state** from **planned target state**.
> Every resource name references an SSOT file. Do not hardcode names here --
> trace them back to the canonical YAML.

---

## Current State (VERIFIED)

Everything in this section has been confirmed via Bicep IaC output, live workspace
queries, or active runtime inspection.

### Workspace

| Property | Value | SSOT Reference |
|----------|-------|----------------|
| URL | `adb-7405610347978231.11.azuredatabricks.net` | `ssot/databricks/workspace.yaml` -> `workspace.url` |
| Resource Name | `dbw-ipai-dev` | `ssot/databricks/workspace.yaml` -> `workspace.resource_name` |
| Region | `southeastasia` | `ssot/databricks/workspace.yaml` -> `workspace.region` |
| SKU | Premium (Unity Catalog enabled) | `ssot/databricks/workspace.yaml` -> `workspace.sku` |
| IaC Source | `infra/azure/databricks/main.bicep` | `ssot/databricks/workspace.yaml` -> `workspace.iac_source` |

### Network

| Property | Value | SSOT Reference |
|----------|-------|----------------|
| VNet | `vnet-ipai-databricks` | `ssot/azure/resources.yaml` -> `network[0].name` |
| Address Space | `10.10.0.0/16` | `ssot/databricks/workspace.yaml` -> `network.vnet.address_space` |
| Public Subnet | `snet-dbw-public` (`10.10.1.0/24`) | `ssot/databricks/workspace.yaml` -> `network.vnet.subnets.public` |
| Private Subnet | `snet-dbw-private` (`10.10.2.0/24`) | `ssot/databricks/workspace.yaml` -> `network.vnet.subnets.private` |
| NSG | `nsg-dbw-ipai-dev` | `ssot/azure/resources.yaml` -> `network[1].name` |
| Secure Cluster Connectivity | Enabled (no public IP on nodes) | `ssot/databricks/workspace.yaml` -> `network.secure_cluster_connectivity` |

Both subnets are delegated to `Microsoft.Databricks/workspaces` and share the NSG.

### Identity and Secrets

| Property | Value | SSOT Reference |
|----------|-------|----------------|
| Managed Identity | `id-ipai-databricks-dev` (user-assigned) | `ssot/azure/resources.yaml` -> `security[1].name` |
| Key Vault | `kv-ipai-dev` | `ssot/azure/resources.yaml` -> `security[0].name` |
| Key Vault RG | `rg-ipai-shared-dev` (cross-RG) | `ssot/databricks/workspace.yaml` -> `identity.key_vault.resource_group` |
| Secret Scope | `kv-ipai-dev` (Key Vault-backed) | `work/databricks/databricks.yml` -> `variables.secret_scope` |

Role assignments on the managed identity:

- **Storage Blob Data Contributor** on `stipaidevlake` (Bicep-defined)
- **Key Vault Secrets User** on `kv-ipai-dev` (post-deployment az CLI, cross-RG)

### Storage (ADLS Gen2)

| Property | Value | SSOT Reference |
|----------|-------|----------------|
| Account | `stipaidevlake` | `ssot/azure/resources.yaml` -> `storage[0].name` |
| Kind | StorageV2, HNS enabled (ADLS Gen2) | `ssot/azure/resources.yaml` -> `storage[0].hns_enabled` |
| SKU | Standard_LRS | `ssot/azure/resources.yaml` -> `storage[0].sku` |
| Containers | `bronze`, `silver`, `gold`, `platinum`, `checkpoints` | `ssot/azure/resources.yaml` -> `storage[0].containers` |
| Lifecycle | Archive bronze after 90d, delete after 730d | `ssot/azure/resources.yaml` -> `storage[0].lifecycle_rules` |

### SQL Warehouse

| Property | Value | SSOT Reference |
|----------|-------|----------------|
| Name | Serverless Starter Warehouse | `ssot/databricks/warehouse.yaml` -> `warehouse.name` |
| Type | Serverless | `ssot/databricks/warehouse.yaml` -> `warehouse.type` |
| ID | `e7d89eabce4c330c` | `ssot/databricks/warehouse.yaml` -> `environments.dev.warehouse_id` |
| HTTP Path | `/sql/1.0/warehouses/e7d89eabce4c330c` | `ssot/databricks/warehouse.yaml` -> `environments.dev.http_path` |

A single serverless warehouse is shared across dev, staging, and prod environments.
The environment boundary is enforced at the **catalog** level, not the warehouse level.

Used by: dashboards, apps, Power BI, bridge API
(`ssot/databricks/warehouse.yaml` -> `default_for`).

### Unity Catalog

| Catalog | Environment | Status | SSOT Reference |
|---------|-------------|--------|----------------|
| `ipai_lakehouse_dev` | dev | Verified | `ssot/databricks/workspace.yaml` -> `unity_catalog.catalogs.dev` |
| `ipai_lakehouse_staging` | staging | Verified | `ssot/databricks/workspace.yaml` -> `unity_catalog.catalogs.staging` |
| `ipai_lakehouse` | prod | Verified | `ssot/databricks/workspace.yaml` -> `unity_catalog.catalogs.prod` |

Metastore assignment: **pending** -- not yet confirmed from live workspace.
(`ssot/databricks/workspace.yaml` -> `unity_catalog.metastore.status`)

### Medallion Architecture

```
Bronze -> Silver -> Gold -> Platinum
```

| Layer | Purpose | Default Schema |
|-------|---------|----------------|
| Bronze | Raw ingests from Odoo PG via n8n -> ADLS -> Auto Loader | `bronze` |
| Silver | Transformed, deduplicated, enriched | `silver` |
| Gold | Business metrics, KPIs | `gold` (default query schema) |
| Platinum | ML scores, embeddings, forecasts | `platinum` |

The default schema for SQL queries is `gold`
(`ssot/databricks/warehouse.yaml` -> `environments.*.default_schema`).

### Data Bridge (ACTIVE)

| Property | Value | SSOT Reference |
|----------|-------|----------------|
| Bridge ID | `odoo_pg_export_to_adls` | `ssot/bridges/registry.yaml` -> `bridges.odoo_pg_export_to_adls` |
| Status | Active | `ssot/bridges/registry.yaml` -> `bridges.odoo_pg_export_to_adls.status` |
| Source | Odoo PostgreSQL (`ipai-db:5432`, Docker-internal) | `ssot/bridges/registry.yaml` -> `source` |
| Transport | n8n (`0 1 * * *`, Asia/Manila) | `ssot/bridges/registry.yaml` -> `transport` |
| Target | `stipaidevlake` / `lakehouse/landing/odoo/` | `ssot/bridges/registry.yaml` -> `target` |
| Format | JSONL, partitioned by `ingest_date=YYYY-MM-DD` | `ssot/bridges/registry.yaml` -> `target.format` |
| Downstream | Databricks Auto Loader -> `bronze` schema | `ssot/bridges/registry.yaml` -> `downstream` |
| Watermark | Per-table `write_date` column, stored in ADLS | `ssot/bridges/registry.yaml` -> `watermark` |

**Bridge table priority:**

- P0: `hr_expense`, `account_move`, `account_move_line`, `project_task`, `ocr_expense_log`
- P1: `crm_lead`, `helpdesk_mgmt_ticket`, `maintenance_request`
- P2: `stock_move`, `mail_activity`

### AI Agent (DEV ONLY)

| Property | Value | SSOT Reference |
|----------|-------|----------------|
| Name | `insightpulseai_copilot` | `ssot/databricks/agents.yaml` -> `agents.insightpulseai_copilot` |
| Type | DBSQL MCP | `ssot/databricks/agents.yaml` -> `type` |
| Allowed Schemas | `gold`, `platinum` | `ssot/databricks/agents.yaml` -> `allowed_schemas` |
| Denied Schemas | `bronze`, `silver`, `ops` | `ssot/databricks/agents.yaml` -> `denied_schemas` |
| Enforced Filter | `_tenant_id` (default: `demo`) | `ssot/databricks/agents.yaml` -> `enforced_filter` |
| Denied Operations | DDL, DML, DROP, TRUNCATE, INSERT, UPDATE, DELETE | `ssot/databricks/agents.yaml` -> `denied_operations` |
| Dev Status | Active | `ssot/databricks/agents.yaml` -> `deployment.dev` |
| Staging Status | Pending | `ssot/databricks/agents.yaml` -> `deployment.staging` |
| Prod Status | Pending | `ssot/databricks/agents.yaml` -> `deployment.prod` |

The agent is read-only and tenant-scoped. It cannot access raw or intermediate layers.

### AI Services (Confirmed)

| Resource | Name | Status | SSOT Reference |
|----------|------|--------|----------------|
| Azure OpenAI | `oai-ipai-dev` | Confirmed (portal) | `ssot/azure/resources.yaml` -> `ai[0].name` |
| Azure AI Search | `srch-ipai-dev` | Needs verification | `ssot/azure/resources.yaml` -> `ai[1].name` |

### Infrastructure as Code

All infrastructure is defined in `infra/azure/databricks/main.bicep`. The Bicep template
provisions:

- NSG with Databricks VNet injection rules
- VNet with delegated public/private subnets
- Databricks workspace (Premium SKU, Secure Cluster Connectivity)
- ADLS Gen2 storage account with medallion containers
- Lifecycle policy (archive bronze >90d, delete >730d)
- User-assigned managed identity
- RBAC role assignment (Storage Blob Data Contributor)

---

## Target State (PLANNED -- NOT YET DEPLOYED)

Everything in this section is defined in SSOT files but has **not** been deployed
to staging or production. Dev URLs may exist for prototyping.

### Databricks Apps (9 apps)

All 9 apps are defined in `ssot/apps/databricks_apps.yaml`. All have dev URLs.
Staging and prod URLs are `null` (not yet deployed).

| # | App Key | Display Name | Framework | Flagship | SSOT Reference |
|---|---------|-------------|-----------|----------|----------------|
| 1 | `finance-copilot` | Finance Copilot | Gradio | No | `ssot/apps/databricks_apps.yaml` -> `databricks_apps[0]` |
| 2 | `expense-intelligence` | Expense Intelligence | Streamlit | No | `ssot/apps/databricks_apps.yaml` -> `databricks_apps[1]` |
| 3 | `project-command-center` | Project Command Center | Next.js | No | `ssot/apps/databricks_apps.yaml` -> `databricks_apps[2]` |
| 4 | `bir-compliance-hub` | BIR Compliance Hub | Dash | No | `ssot/apps/databricks_apps.yaml` -> `databricks_apps[3]` |
| 5 | `marketing-intelligence` | Marketing Intelligence Hub | Next.js | Yes | `ssot/apps/databricks_apps.yaml` -> `databricks_apps[4]` |
| 6 | `tenant-admin` | Tenant Admin Console | Next.js | No | `ssot/apps/databricks_apps.yaml` -> `databricks_apps[5]` |
| 7 | `partner-360` | Partner 360 Explorer | Streamlit | No | `ssot/apps/databricks_apps.yaml` -> `databricks_apps[6]` |
| 8 | `ocr-analytics` | OCR Analytics | Dash | No | `ssot/apps/databricks_apps.yaml` -> `databricks_apps[7]` |
| 9 | `esg-reporter` | ESG Reporter | Streamlit | No | `ssot/apps/databricks_apps.yaml` -> `databricks_apps[8]` |

All apps are tenant-scoped (`_tenant_id` filter) and require `tenant-users` role
(except `tenant-admin` which requires `tenant-admins`).

There is also 1 native OWL widget set (`ipai_databricks_owl`) that runs inside
Odoo and is **not** a Databricks App.
(`ssot/apps/databricks_apps.yaml` -> `owl_widgets`)

### Scheduled Jobs

All jobs are defined in `work/databricks/databricks.yml`. The default (and only active)
target is `dev`. Schedules are in `Asia/Manila` timezone.

| Job | Schedule | Layer | SSOT Reference |
|-----|----------|-------|----------------|
| `odoo_bronze_ingest` | Daily 02:00 | bronze | `work/databricks/databricks.yml` -> `resources.jobs.odoo_bronze_ingest` |
| `silver_transform` | Daily 04:00 | silver | `work/databricks/databricks.yml` -> `resources.jobs.silver_transform` |
| `gold_build` | Daily 06:00 | gold | `work/databricks/databricks.yml` -> `resources.jobs.gold_build` |
| `data_quality` | Daily 08:00 | ops | `work/databricks/databricks.yml` -> `resources.jobs.data_quality` |
| `platinum_embeddings` | Weekly Sun 10:00 | platinum | `work/databricks/databricks.yml` -> `resources.jobs.platinum_embeddings` |
| `platinum_ml_training` | Weekly Sun 12:00 | platinum | `work/databricks/databricks.yml` -> `resources.jobs.platinum_ml_training` |
| `platinum_writeback` | Daily 14:00 | platinum | `work/databricks/databricks.yml` -> `resources.jobs.platinum_writeback` |
| `marketing_bronze_ingest` | Daily 02:30 | bronze | `work/databricks/databricks.yml` -> `resources.jobs.marketing_bronze_ingest` |
| `marketing_silver_transform` | Daily 04:30 | silver | `work/databricks/databricks.yml` -> `resources.jobs.marketing_silver_transform` |
| `marketing_gold_build` | Daily 06:30 | gold | `work/databricks/databricks.yml` -> `resources.jobs.marketing_gold_build` |
| `marketing_platinum_ml` | Weekly Sun 14:00 | platinum | `work/databricks/databricks.yml` -> `resources.jobs.marketing_platinum_ml` |
| `seed_demo` | On-demand | ops | `work/databricks/databricks.yml` -> `resources.jobs.seed_demo` |

The `seed_demo` job is hard-removed from the `prod` target
(`work/databricks/databricks.yml` -> `targets.prod.resources.jobs.seed_demo: null`).

All job clusters use `Standard_DS3_v2` single-node with spot instances
(`SPOT_WITH_FALLBACK_AZURE`) and 10-minute auto-termination, except
`marketing_platinum_ml` which uses `Standard_DS4_v2` with 15-minute auto-termination.

### DLT Pipeline

| Pipeline | Purpose | SSOT Reference |
|----------|---------|----------------|
| `marketing_dlt_pipeline` | Marketing Intelligence DLT (Photon-enabled) | `work/databricks/databricks.yml` -> `resources.pipelines.marketing_dlt_pipeline` |

### Lakeview Dashboards

Three dashboards defined in the DAB bundle:

| Dashboard | Display Name | SSOT Reference |
|-----------|-------------|----------------|
| `marketing_intelligence` | InsightPulseAI - Marketing Intelligence | `work/databricks/databricks.yml` -> `resources.dashboards.marketing_intelligence` |
| `finance_close_bir` | InsightPulseAI - Finance Close & BIR | `work/databricks/databricks.yml` -> `resources.dashboards.finance_close_bir` |
| `ocr_anomaly` | InsightPulseAI - OCR & Anomaly Detection | `work/databricks/databricks.yml` -> `resources.dashboards.ocr_anomaly` |

### Unity Catalog -- Pending Items

- **Metastore name**: Not yet confirmed (`ssot/databricks/workspace.yaml` -> `unity_catalog.metastore.status: pending`)
- **External locations**: Not yet set up

### Azure PostgreSQL Flexible Server

| Property | Value | SSOT Reference |
|----------|-------|----------------|
| Name | `pg-ipai-dev` | `ssot/azure/resources.yaml` -> `database[0].name` |
| Status | Pending (not provisioned) | `ssot/azure/resources.yaml` -> `database[0].source: pending` |
| Purpose | Replace DO-hosted PostgreSQL for Odoo | `ssot/azure/resources.yaml` -> `database[0].notes` |

The DAB bundle references this server in its JDBC URL variable:
`jdbc:postgresql://pg-ipai-dev.postgres.database.azure.com:5432/odoo_prod`
(`work/databricks/databricks.yml` -> `variables.jdbc_url`).

The `ingest_mode` variable controls whether Bronze ingest reads from JDBC (Azure PG)
or ADLS (n8n landing zone). Current default: `jdbc` in the bundle, but the
active bridge still uses the n8n/ADLS path since Azure PG is not provisioned.

### Microsoft Integration Pack

Defined in `ssot/microsoft/integration_pack.yaml`.

**Three demo narratives:**

| Narrative | Databricks Apps | Power BI Dataset |
|-----------|----------------|-----------------|
| Marketing Intel / CDP | marketing-intelligence, partner-360 | InsightPulseAI - Marketing Demo |
| Finance Close + BIR | finance-copilot, bir-compliance-hub | InsightPulseAI - Finance Demo |
| OCR Expense + Anomaly | expense-intelligence, ocr-analytics | InsightPulseAI - OCR Demo |

**Power Platform bridge:**

- OpenAPI spec: `platform/bridges/power_platform/openapi.yaml`
  (`ssot/microsoft/integration_pack.yaml` -> `bridge.openapi_spec`)
- Runtime: Azure Container App or Function
- Auth: Azure AD / Entra ID (client credentials)
- Reads from: Databricks SQL Warehouse (Gold/Platinum)
- Writes to: Odoo JSON-RPC, ADLS outbox

### Demo Tenant

| Property | Value | SSOT Reference |
|----------|-------|----------------|
| Tenant ID | `demo` | `ssot/tenants/demo.yaml` -> `tenant.id` |
| Name | Demo Corp International | `ssot/tenants/demo.yaml` -> `tenant.name` |
| Allowed Targets | dev, staging | `ssot/tenants/demo.yaml` -> `tenant.allowed_targets` |
| Date Range | 2025-01-01 to 2026-03-01 (14 months) | `ssot/tenants/demo.yaml` -> `date_range` |
| Prod Blocked | Yes (hard block) | `ssot/tenants/demo.yaml` -> `guardrails.hard_block_prod` |

Tenant filter: `_tenant_id = 'demo'`
(`ssot/databricks/warehouse.yaml` -> `tenant_filter`).

---

## Resource Naming Convention

All Azure resources follow: `{type}-ipai-{environment}`

(`ssot/azure/resources.yaml` -> `naming_convention`)

The region (`southeastasia`) is **NOT** encoded in resource names. Names ending in
`-sea` do not exist.

(`ssot/azure/resources.yaml` -> errata section)

| Type | Dev Name | Source | SSOT Reference |
|------|----------|--------|----------------|
| Databricks Workspace | `dbw-ipai-dev` | Bicep | `ssot/azure/resources.yaml` -> `compute[0].name` |
| ADLS Gen2 | `stipaidevlake` | Bicep | `ssot/azure/resources.yaml` -> `storage[0].name` |
| Key Vault | `kv-ipai-dev` | Bicep (cross-RG) | `ssot/azure/resources.yaml` -> `security[0].name` |
| VNet | `vnet-ipai-databricks` | Bicep (fixed name) | `ssot/azure/resources.yaml` -> `network[0].name` |
| NSG | `nsg-dbw-ipai-dev` | Bicep | `ssot/azure/resources.yaml` -> `network[1].name` |
| Managed Identity | `id-ipai-databricks-dev` | Bicep | `ssot/azure/resources.yaml` -> `security[1].name` |
| Managed RG | `rg-dbw-managed-ipai-dev` | Bicep | `ssot/databricks/workspace.yaml` -> `managed_resource_group.name` |
| Azure OpenAI | `oai-ipai-dev` | Confirmed | `ssot/azure/resources.yaml` -> `ai[0].name` |
| Azure AI Search | `srch-ipai-dev` | Needs verification | `ssot/azure/resources.yaml` -> `ai[1].name` |
| Azure PG | `pg-ipai-dev` | Pending | `ssot/azure/resources.yaml` -> `database[0].name` |

### Resource Groups

| Name | Purpose | SSOT Reference |
|------|---------|----------------|
| `rg-ipai-dev` | Primary RG for Databricks stack | `ssot/azure/resources.yaml` -> `resource_groups[0]` |
| `rg-ipai-shared-dev` | Shared services (Key Vault) | `ssot/azure/resources.yaml` -> `resource_groups[1]` |
| `rg-dbw-managed-ipai-dev` | Databricks-managed (auto-created) | `ssot/azure/resources.yaml` -> `resource_groups[2]` |

---

## SSOT File Map

| File | Purpose | State |
|------|---------|-------|
| `ssot/databricks/warehouse.yaml` | SQL warehouse config per environment | Verified |
| `ssot/databricks/workspace.yaml` | Workspace, VNet, security, Unity Catalog | Verified |
| `ssot/databricks/agents.yaml` | AI agent registry | Verified (dev only) |
| `ssot/apps/databricks_apps.yaml` | 9 Databricks Apps + 1 OWL widget set | Defined (dev URLs only) |
| `ssot/azure/resources.yaml` | Azure resource inventory (all types) | Verified |
| `ssot/bridges/registry.yaml` | Data bridge definitions | Active |
| `ssot/microsoft/integration_pack.yaml` | Power BI / Power Platform bridge | Planned |
| `ssot/tenants/demo.yaml` | Demo tenant config (volumes, distributions) | Defined |
| `infra/azure/databricks/main.bicep` | IaC -- source of truth for infrastructure | Bicep |
| `work/databricks/databricks.yml` | DAB bundle (jobs, pipelines, dashboards, apps) | Dev target only |

---

## Data Flow Diagram (Text)

```
Odoo PG (DO Droplet)
  |
  | n8n (daily 01:00 Asia/Manila)
  v
ADLS Gen2: stipaidevlake/lakehouse/landing/odoo/
  |
  | Databricks Auto Loader
  v
Bronze (raw ingests)
  |
  | silver_transform (daily 04:00)
  v
Silver (deduplicated, enriched)
  |
  | gold_build (daily 06:00)
  v
Gold (business metrics, KPIs)    <--- SQL Warehouse (e7d89eabce4c330c)
  |                                    |
  | platinum_* (weekly/daily)          |--- Dashboards
  v                                    |--- Apps
Platinum (ML scores, embeddings)       |--- Power BI
  |                                    |--- Copilot Agent
  | writeback_pipeline (daily 14:00)
  v
ADLS Outbox -> Odoo / Power Platform
```

---

## Errata

The following resource names have appeared in past documentation but **do not exist**:

- `oai-ipai-sea` -- correct name is `oai-ipai-dev`
- `kv-ipai-sea` -- correct name is `kv-ipai-dev`
- `vnet-ipai-sea` -- correct name is `vnet-ipai-databricks`
- `search-ipai-sea` -- expected canonical name is `srch-ipai-dev`

Source: `ssot/azure/resources.yaml` errata section.
