# Databricks notebook source
# MAGIC %md
# MAGIC # Connector Monitoring Dashboard
# MAGIC
# MAGIC Gold-layer aggregations from `bronze.sync_runs` and `bronze.connector_state`.
# MAGIC Produces monitoring tables for Superset/dashboards.

# COMMAND ----------

import os
from datetime import datetime

# COMMAND ----------

CATALOG = os.environ.get("DATABRICKS_CATALOG", "ppm")
BRONZE = f"{CATALOG}.bronze"
GOLD = f"{CATALOG}.gold"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Connector Health Summary

# COMMAND ----------

# Current connector status
spark.sql(f"""
    CREATE OR REPLACE TABLE {GOLD}.connector_health AS
    SELECT
        cs.connector_id,
        cs.paused,
        cs.paused_reason,
        cs.consecutive_failures,
        cs.last_success,
        cs.last_failure,
        cs.updated_at,
        sr.last_run_status,
        sr.last_run_duration_seconds,
        sr.runs_24h,
        sr.success_rate_24h,
        sr.avg_duration_24h,
        sr.total_rows_24h
    FROM {BRONZE}.connector_state cs
    LEFT JOIN (
        SELECT
            connector_id,
            FIRST(status) AS last_run_status,
            FIRST(duration_seconds) AS last_run_duration_seconds,
            COUNT(*) AS runs_24h,
            ROUND(
                COUNT(CASE WHEN status = 'success' THEN 1 END) * 100.0 / COUNT(*),
                1
            ) AS success_rate_24h,
            ROUND(AVG(duration_seconds), 1) AS avg_duration_24h,
            SUM(
                AGGREGATE(
                    MAP_VALUES(COALESCE(tables_synced, MAP())),
                    CAST(0 AS LONG),
                    (acc, x) -> acc + x
                )
            ) AS total_rows_24h
        FROM {BRONZE}.sync_runs
        WHERE started_at >= CURRENT_TIMESTAMP() - INTERVAL 24 HOURS
        GROUP BY connector_id
    ) sr ON cs.connector_id = sr.connector_id
""")

print("connector_health table refreshed")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Sync Run History (last 7 days)

# COMMAND ----------

spark.sql(f"""
    CREATE OR REPLACE TABLE {GOLD}.sync_run_history AS
    SELECT
        run_id,
        connector_id,
        status,
        started_at,
        finished_at,
        duration_seconds,
        tables_synced,
        error_message,
        DATE(started_at) AS run_date,
        HOUR(started_at) AS run_hour
    FROM {BRONZE}.sync_runs
    WHERE started_at >= CURRENT_TIMESTAMP() - INTERVAL 7 DAYS
    ORDER BY started_at DESC
""")

print("sync_run_history table refreshed")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Daily Connector Metrics

# COMMAND ----------

spark.sql(f"""
    CREATE OR REPLACE TABLE {GOLD}.connector_daily_metrics AS
    SELECT
        connector_id,
        DATE(started_at) AS run_date,
        COUNT(*) AS total_runs,
        COUNT(CASE WHEN status = 'success' THEN 1 END) AS successful_runs,
        COUNT(CASE WHEN status = 'failure' THEN 1 END) AS failed_runs,
        ROUND(
            COUNT(CASE WHEN status = 'success' THEN 1 END) * 100.0 / COUNT(*),
            1
        ) AS success_rate_pct,
        ROUND(AVG(duration_seconds), 1) AS avg_duration_seconds,
        ROUND(MAX(duration_seconds), 1) AS max_duration_seconds,
        SUM(
            AGGREGATE(
                MAP_VALUES(COALESCE(tables_synced, MAP())),
                CAST(0 AS LONG),
                (acc, x) -> acc + x
            )
        ) AS total_rows_synced
    FROM {BRONZE}.sync_runs
    WHERE started_at >= CURRENT_TIMESTAMP() - INTERVAL 30 DAYS
    GROUP BY connector_id, DATE(started_at)
    ORDER BY run_date DESC, connector_id
""")

print("connector_daily_metrics table refreshed")

# COMMAND ----------

# Display current health
display(spark.table(f"{GOLD}.connector_health"))

# COMMAND ----------

import json

dbutils.notebook.exit(json.dumps({
    "status": "success",
    "tables_refreshed": [
        f"{GOLD}.connector_health",
        f"{GOLD}.sync_run_history",
        f"{GOLD}.connector_daily_metrics",
    ],
    "timestamp": datetime.utcnow().isoformat(),
}))
