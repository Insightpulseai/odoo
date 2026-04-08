# Data Platform Fix Plan -- Minimal Path to E2E Green

> Audit date: 2026-03-28
> Goal: Make the Odoo PG --> Bronze --> Silver --> Gold --> BI pipeline operational

---

## Phase 0: Unblock CLI Access (prerequisite for all phases)

| # | Action | Command / Detail | Effort |
|---|--------|-----------------|--------|
| 0.1 | Grant Storage Blob Data Reader on `stipaidevlake` to current user | `az role assignment create --assignee <user-oid> --role "Storage Blob Data Reader" --scope /subscriptions/536d8cf6-.../resourceGroups/rg-ipai-ai-dev/providers/Microsoft.Storage/storageAccounts/stipaidevlake` | 5 min |
| 0.2 | Verify Databricks CLI auth | `databricks auth login --host https://adb-7405610347978231.11.azuredatabricks.net` (AAD browser flow) | 5 min |
| 0.3 | Verify Unity Catalog metastore | `databricks unity-catalog metastore-summary` | 2 min |
| 0.4 | If no metastore: assign one | Requires account-level admin. Create metastore in `southeastasia` region, assign to workspace. | 30 min |

---

## Phase 1: Resolve Catalog Naming (blocks all subsequent phases)

| # | Action | Detail | Effort |
|---|--------|--------|--------|
| 1.1 | Decide canonical catalog name | Recommended: `ipai` (shortest, used in ingestion notebook). Update all code to use this single name. | Decision |
| 1.2 | Update `workspace.yaml` | Change `catalogs.dev.name` from `ipai_lakehouse_dev` to `ipai` | 5 min |
| 1.3 | Update test notebooks | Change `CATALOG = "dbw_ipai_dev"` to `CATALOG = "ipai"` in `seed_synthetic.py` and `test_medallion_pipeline.py` | 10 min |
| 1.4 | Update DAB bundle | Change `databricks.yml` variable `catalog` default from `ppm` to `ipai` | 5 min |
| 1.5 | Create catalog in UC | `CREATE CATALOG IF NOT EXISTS ipai MANAGED LOCATION 'abfss://unity-catalog@stipaidev.dfs.core.windows.net/ipai';` | 5 min |
| 1.6 | Create schemas | Run `schemas_odoo.sql` with `${catalog}` = `ipai` | 5 min |

---

## Phase 2: Databricks Lakehouse Federation (Lane 2 -- fastest path to E2E)

Lane 2 (Lakehouse Federation) is **faster to operationalize** than Lane 1 (Fabric Mirroring) because it requires no Fabric capacity. This is the recommended first path.

| # | Action | Detail | Effort |
|---|--------|--------|--------|
| 2.1 | Create Databricks secret scope | `databricks secrets create-scope ipai-odoo-pg` | 5 min |
| 2.2 | Store PG credentials | `databricks secrets put-secret ipai-odoo-pg host`, `user`, `password` (from Azure Key Vault `kv-ipai-dev`) | 10 min |
| 2.3 | Create Federation connection | Run SQL from `01_odoo_bronze_ingestion.py` Step 3 (CREATE CONNECTION) | 5 min |
| 2.4 | Create foreign catalog | Run SQL from Step 4 (CREATE FOREIGN CATALOG) | 5 min |
| 2.5 | Run bronze ingestion | Execute `01_odoo_bronze_ingestion.py` on a cluster or SQL warehouse | 15 min |
| 2.6 | Verify bronze tables | `SELECT count(*) FROM ipai.bronze.odoo_res_partner` | 2 min |

---

## Phase 3: Medallion Pipeline Test (synthetic data)

| # | Action | Detail | Effort |
|---|--------|--------|--------|
| 3.1 | Fix catalog references in test notebooks | Ensure all use `ipai` | 10 min |
| 3.2 | Run seed_synthetic notebook | Seeds `ipai.test_bronze.*` with synthetic data | 10 min |
| 3.3 | Run test_medallion_pipeline notebook | Transforms Bronze --> Silver --> Gold | 15 min |
| 3.4 | Run medallion_test_dlt pipeline | DLT pipeline with expectations | 20 min |
| 3.5 | Verify gold tables | Query `ipai.test_gold.revenue_summary`, `customer_kpis`, `payment_aging` | 5 min |

---

## Phase 4: Fabric Mirroring (Lane 1 -- requires budget approval)

**BLOCKED until Fabric capacity is provisioned.** Estimated cost: $5,000/month for F64, or free for 60-day trial.

| # | Action | Detail | Effort |
|---|--------|--------|--------|
| 4.1 | Activate Fabric trial or provision capacity | Azure portal or `az fabric capacity create` | 15 min |
| 4.2 | Create Fabric workspace | Portal or REST API | 10 min |
| 4.3 | Enable Fabric mirroring on PG server | `az postgres flexible-server update --name pg-ipai-odoo --resource-group rg-ipai-dev-odoo-data --fabric-mirroring Enabled` (triggers server restart) | 10 min |
| 4.4 | Select allowed database | Choose `odoo_staging` first (as per memory decision) | 5 min |
| 4.5 | Transfer table ownership to `azure_pg_admin` | `ALTER TABLE <table> OWNER TO azure_pg_admin;` for each mirrored table | 15 min |
| 4.6 | Create mirrored database in Fabric | Fabric portal: New > Mirrored database > Azure PostgreSQL | 10 min |
| 4.7 | Verify CDC replication | Check Fabric portal for replication status and row counts | 10 min |

---

## Phase 5: Power BI Consumption

**BLOCKED until either Fabric capacity or Power BI Pro/PPU licenses are provisioned.**

| # | Action | Detail | Effort |
|---|--------|--------|--------|
| 5.1 | Create Power BI workspace | Requires Pro or PPU license | 10 min |
| 5.2 | Connect to SQL Warehouse | Use Databricks SQL connector in Power BI Desktop | 15 min |
| 5.3 | Build semantic model from gold tables | Map `ipai.gold.*` tables to star schema | 2 hr |
| 5.4 | Publish and schedule refresh | Publish to Power BI Service, set refresh schedule | 30 min |

---

## Phase 6: Cleanup and Hardening

| # | Action | Detail | Effort |
|---|--------|--------|--------|
| 6.1 | Remove Notion references from DAB bundle | Delete `notion_sync_wheel` artifact, `notion_token` variable | 15 min |
| 6.2 | Remove Notion-specific SQL DDL | Remove `notion_raw_pages`, `notion_programs`, etc. from `bronze_odoo.sql` and `silver_odoo.sql` | 15 min |
| 6.3 | Update SSOT files | Set `unity_catalog.metastore.status` to `verified` once confirmed | 5 min |
| 6.4 | Apply UC grants | Run `grants_odoo.sql` with correct catalog name | 5 min |
| 6.5 | Set up Databricks token rotation | Configure AAD-based auth with service principal for CI/CD | 1 hr |

---

## Priority Order

```
Phase 0 (unblock CLI) --> Phase 1 (naming) --> Phase 2 (federation) --> Phase 3 (test pipeline)
                                                                        |
                                                           [E2E operational for Lane 2]
                                                                        |
                                               Phase 4 (Fabric, if budget approved) --> Phase 5 (Power BI)
                                                                        |
                                                               Phase 6 (cleanup)
```

**Minimum viable E2E: Phases 0-3** (estimated: 2-3 hours of focused work, assuming Databricks workspace is operational and has compute available).

**Full E2E with Fabric + Power BI: Phases 0-6** (estimated: 1-2 days, plus budget approval for Fabric capacity).

---

*Plan drafted 2026-03-28*
