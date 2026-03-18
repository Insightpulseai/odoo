# Skill: Databricks Lakeflow — Data Engineering

## Metadata

| Field | Value |
|-------|-------|
| **id** | `databricks-lakeflow` |
| **domain** | `lakehouse` |
| **source** | https://learn.microsoft.com/en-us/azure/databricks/data-engineering/ |
| **extracted** | 2026-03-15 |
| **applies_to** | lakehouse, automations |
| **tags** | databricks, lakeflow, dlt, sdp, streaming, etl, connect, jobs, spark |

---

## What It Is

Lakeflow is Databricks' end-to-end data engineering solution. Three components:

1. **Lakeflow Connect** — Managed connectors for ingestion
2. **Lakeflow Spark Declarative Pipelines (SDP)** — Declarative ETL framework (formerly DLT)
3. **Lakeflow Jobs** — Orchestration and production monitoring

## Lakeflow Connect (Ingestion)

| Connector Type | Description | IPAI Use |
|---------------|-------------|----------|
| **Managed connectors** | UI-based, config-driven, minimal ops | Odoo DB → Bronze (if DB replica available) |
| **Standard connectors** | Wider range, used within pipelines | ADLS, PostgreSQL, REST API |

### Relevant Managed Connectors

| Source | Connector | Status |
|--------|-----------|--------|
| PostgreSQL (Odoo DB) | `postgresql` | Available — use for Odoo → Bronze |
| Azure Blob / ADLS | `azure_storage` | Available — use for file ingestion |
| Kafka / Event Hubs | `kafka` | Available — for streaming events |
| REST API | Custom via standard | Build for Odoo Extract API |

## Lakeflow SDP (Transformation)

Formerly Delta Live Tables (DLT). Declarative framework for batch + streaming pipelines.

| Concept | Description | IPAI Equivalent |
|---------|-------------|-----------------|
| **Flows** | Process data using Spark DataFrame API | n8n workflows (simpler) |
| **Streaming tables** | Delta tables with incremental processing | `ops.platform_events` (append-only) |
| **Materialized views** | Cached views with auto-refresh | Superset cached queries |
| **Sinks** | Output to Kafka, Event Hubs, external tables | Supabase REST API writes |
| **Pipelines** | Container that orchestrates flows, tables, views | n8n workflow sequences |

### SDP Pipeline Example (Python)

```python
import dlt
from pyspark.sql.functions import col, sum as spark_sum

# Bronze: ingest raw Odoo journal entries
@dlt.table(comment="Raw Odoo journal entries from Extract API")
def bronze_account_move():
    return (
        spark.read.format("parquet")
        .load("abfss://bronze@ipailakehouse.dfs.core.windows.net/odoo/account_move/")
    )

# Silver: clean and type
@dlt.table(comment="Cleaned journal entries")
@dlt.expect_or_drop("valid_state", "state IN ('posted', 'draft')")
def silver_account_move():
    return (
        dlt.read("bronze_account_move")
        .select(
            col("id"),
            col("name").alias("move_name"),
            col("date").cast("date").alias("move_date"),
            col("partner_id"),
            col("journal_id"),
            col("amount_total").cast("decimal(15,2)"),
            col("state"),
        )
    )

# Gold: monthly revenue mart
@dlt.table(comment="Monthly revenue aggregation")
def gold_monthly_revenue():
    return (
        dlt.read("silver_account_move")
        .filter(col("state") == "posted")
        .groupBy(
            spark_sum("amount_total").alias("total_revenue"),
        )
    )
```

### Data Quality with Expectations

```python
@dlt.expect("valid_amount", "amount_total > 0")           # Warn but keep
@dlt.expect_or_drop("has_date", "move_date IS NOT NULL")   # Drop invalid
@dlt.expect_or_fail("valid_state", "state IS NOT NULL")    # Fail pipeline
```

## Lakeflow Jobs (Orchestration)

| Feature | Description | IPAI Equivalent |
|---------|-------------|-----------------|
| **Jobs** | Primary orchestration resource, scheduled | n8n cron workflows |
| **Tasks** | Unit of work (notebook, pipeline, SQL, ML) | n8n nodes |
| **Control flow** | If/else branching, for-each loops | n8n IF/Switch nodes |

### Job Types

| Task Type | Use Case |
|-----------|----------|
| Notebook | Python/SQL ETL scripts |
| Pipeline | Lakeflow SDP pipeline execution |
| SQL | Databricks SQL query execution |
| dbt | dbt project execution |
| Python wheel | Packaged Python applications |
| ML training | Model training jobs |

## Databricks Runtime

| Feature | Description |
|---------|-------------|
| **Photon** | High-performance vectorized query engine |
| **Structured Streaming** | Near real-time processing |
| **Autoscaling** | Automatic cluster scaling |
| **Delta Lake** | ACID transactions on Parquet |

## IPAI Integration Architecture

```
Source Systems                    Databricks Lakeflow                  Consumption

Odoo PG ───── Lakeflow Connect ──► Bronze (Delta) ──►
                                    │
Supabase ──── REST API / CDC ────► Bronze (Delta) ──► SDP Pipeline ──► Silver ──► Gold
                                    │                  (expectations)         │
n8n events ── Webhook / Batch ───► Bronze (Delta) ──►                        │
                                                                              ▼
                                                                    ┌─────────────────┐
                                                                    │ Superset (BI)    │
                                                                    │ Databricks SQL   │
                                                                    │ ML Models        │
                                                                    │ Reverse ETL      │
                                                                    └─────────────────┘
```

## Decision: n8n vs Lakeflow for ETL

| Criteria | n8n | Lakeflow |
|----------|-----|----------|
| Simple webhook routing | Winner | Overkill |
| Data quality (expectations) | Manual | Built-in |
| Large volume transforms | Limited (memory) | Spark-native (distributed) |
| Streaming | Not supported | Structured Streaming |
| Schema evolution | Manual | Delta Lake native |
| Cost | Self-hosted (free) | Databricks DBUs ($$$) |
| Monitoring | Basic | Production-grade |

**Recommendation**:
- **n8n** for: event routing, webhook handling, Odoo CRUD, Slack notifications, simple ETL (<100K rows)
- **Lakeflow** for: Bronze → Silver → Gold transforms, data quality, streaming, ML features (>100K rows)

## Next Steps (from n8n-odoo-supabase-etl skill)

1. Provision Databricks workspace (`dbw-ipai-dev` in `rg-ipai-ai-dev`)
2. Create Unity Catalog for data governance
3. Set up Lakeflow Connect for Odoo PostgreSQL
4. Build first SDP pipeline: `bronze_account_move` → `silver_account_move` → `gold_monthly_revenue`
5. Connect Superset to Databricks SQL warehouse for Gold queries
