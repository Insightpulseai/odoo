# Databricks notebook source
# MAGIC %md
# MAGIC # JDBC Extract: Odoo PBI Views → Gold OKR Dashboard
# MAGIC
# MAGIC Reads the `pbi.*` PostgreSQL views from Odoo and writes them as
# MAGIC Delta tables in the `gold` schema for the OKR Dashboard.
# MAGIC
# MAGIC **Source**: `pbi.*` views on `ipai-odoo-dev-pg`
# MAGIC **Target**: `${catalog}.gold.okr_*` Delta tables
# MAGIC **Schedule**: Hourly (or on-demand via Databricks Job)
# MAGIC
# MAGIC Required secrets (Databricks secret scope `ipai-odoo-pg`):
# MAGIC   - `host`, `user`, `password`

# COMMAND ----------

from datetime import datetime, timezone
from pyspark.sql import functions as F

# COMMAND ----------

# Configuration
SECRET_SCOPE = "ipai-odoo-pg"
CATALOG = spark.conf.get("catalog", "dbw_ipai_dev")
GOLD_SCHEMA = f"{CATALOG}.gold"

_PG_HOST = dbutils.secrets.get(scope=SECRET_SCOPE, key="host")
JDBC_URL = f"jdbc:postgresql://{_PG_HOST}:5432/odoo_dev?sslmode=require"
JDBC_USER = dbutils.secrets.get(scope=SECRET_SCOPE, key="user")
JDBC_PASSWORD = dbutils.secrets.get(scope=SECRET_SCOPE, key="password")

JDBC_PROPERTIES = {
    "user": JDBC_USER,
    "password": JDBC_PASSWORD,
    "driver": "org.postgresql.Driver",
    "fetchsize": "10000",
}

# PBI views → Gold table mapping
VIEWS = [
    {"source": "pbi.dim_team_member",        "target": "okr_dim_team_member"},
    {"source": "pbi.dim_project",            "target": "okr_dim_project"},
    {"source": "pbi.dim_stage",              "target": "okr_dim_stage"},
    {"source": "pbi.dim_tag",                "target": "okr_dim_tag"},
    {"source": "pbi.dim_milestone",          "target": "okr_dim_milestone"},
    {"source": "pbi.fact_task",              "target": "okr_fact_task"},
    {"source": "pbi.fact_task_assignment",   "target": "okr_fact_task_assignment"},
    {"source": "pbi.fact_task_tag",          "target": "okr_fact_task_tag"},
    {"source": "pbi.agg_team_performance",   "target": "okr_agg_team_performance"},
    {"source": "pbi.agg_stage_distribution", "target": "okr_agg_stage_distribution"},
    {"source": "pbi.agg_milestone_progress", "target": "okr_agg_milestone_progress"},
]

# COMMAND ----------

# MAGIC %md
# MAGIC ## Extract & Load

# COMMAND ----------

load_ts = datetime.now(timezone.utc).isoformat()
results = []

for view in VIEWS:
    source = view["source"]
    target = f"{GOLD_SCHEMA}.{view['target']}"

    print(f"Loading {source} → {target}...")
    try:
        df = (
            spark.read.jdbc(
                url=JDBC_URL,
                table=f"(SELECT * FROM {source}) AS t",
                properties=JDBC_PROPERTIES,
            )
            .withColumn("_etl_loaded_at", F.lit(load_ts))
        )

        row_count = df.count()

        (
            df.write
            .format("delta")
            .mode("overwrite")
            .option("overwriteSchema", "true")
            .saveAsTable(target)
        )

        results.append({"view": source, "table": target, "rows": row_count, "status": "OK"})
        print(f"  ✓ {row_count} rows")

    except Exception as e:
        results.append({"view": source, "table": target, "rows": 0, "status": str(e)[:100]})
        print(f"  ✗ {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary

# COMMAND ----------

summary_df = spark.createDataFrame(results)
display(summary_df)

total_rows = sum(r["rows"] for r in results)
ok_count = sum(1 for r in results if r["status"] == "OK")
print(f"\nLoaded {ok_count}/{len(VIEWS)} tables, {total_rows} total rows")
