# Skill: Databricks Data Intelligence Platform — IPAI Reference

source: databricks.com/product/*
extracted: 2026-03-15
applies-to: lakehouse, agents, ops-platform

## Core Architecture: Lakehouse = Lake + Warehouse + AI
- Delta Lake: ACID transactions, time travel, schema enforcement on object storage
- Unity Catalog: "define once, govern everywhere" for data, models, features, AI assets
- Photon: vectorized query engine (5x faster than legacy warehouses)
- Lakeflow (DLT): declarative ETL pipelines with medallion pattern (Bronze→Silver→Gold)
- MLflow 3.0: experiment tracking, agent eval, LLMOps, deployment jobs

## IPAI resource: `dbw-ipai-dev` (Azure, Southeast Asia)

| Capability | Status |
|---|---|
| Delta Lake + Spark | GA |
| Unity Catalog | Partial activation |
| Delta Live Tables (DLT) | Ready |
| AI/BI Dashboards | Evaluating vs. Superset |
| Lakebase (Postgres OLTP) | Azure preview — evaluate |
| Databricks Apps | Evaluate |
| MLflow 3.0 | Ready |
| Vector Search | Ready |

## Product Layer Map

```
stipaidevlake (ADLS)           ← raw storage (Bronze)
  ↓ Delta Live Tables
dbw-ipai-dev Unity Catalog     ← Silver + Gold tables (SSOT for analytics)
  ↓ AI/BI Dashboards / DBSQL
ops-console (web repo)         ← surfaces to users
  ↓ Supabase (ops-platform)    ← SSOT for orchestration + control plane
  ↓ Odoo (odoo repo)           ← SOR for ERP/accounting
```

## Medallion pattern

```
Bronze (stipaidevlake/bronze/*)
  Sources: Odoo webhooks → Supabase → export → ADLS
  Format: raw Parquet/JSON, partitioned by date

Silver (Unity Catalog: ipai_silver.*)
  Transformations: DLT with expectations (data quality rules)
  Schema: validated, typed, deduplicated

Gold (Unity Catalog: ipai_gold.*)
  Aggregations: business-metric rollups
  Consumers: AI/BI Dashboards, Databricks Apps, Delta Sharing

AI layer (Unity Catalog: ipai_ai.*)
  Vector indexes, embeddings, feature tables
  MLflow registered models
```

## Lakehouse Federation (priority integration)

```sql
-- Register Supabase as foreign catalog in Unity Catalog
CREATE CONNECTION supabase_prod
  TYPE POSTGRESQL
  OPTIONS (
    host 'db.spdtwktxdalcfigzeqrz.supabase.co',
    port '5432',
    user secret('supabase_ro_user'),
    password secret('supabase_ro_password')
  );

CREATE FOREIGN CATALOG supabase USING CONNECTION supabase_prod;

-- Query Supabase tables directly from Databricks
SELECT * FROM supabase.ops.runs WHERE status = 'failed';
```

## SSOT/SOR mapping
- Databricks IS NOT SSOT or SOR for any operational domain
- Databricks = analytics/intelligence layer ONLY
- Canonical path: Odoo SOR → Supabase SSOT → Databricks (read-only replica)
- Never write back from Databricks to Odoo or Supabase except via explicit Edge Function / queue workflow with audit trail

## Governance contract
- All tables registered in Unity Catalog
- Schema: `ipai_bronze` / `ipai_silver` / `ipai_gold` / `ipai_ai`
- External access: Delta Sharing only (no direct JDBC from external apps)
- Lineage: auto-captured by Unity Catalog — do not bypass
