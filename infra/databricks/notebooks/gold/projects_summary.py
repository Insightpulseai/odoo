# Databricks notebook source
# MAGIC %md
# MAGIC # Projects Summary Gold Table
# MAGIC
# MAGIC Enriched projects table combining budget, risks, and forecast data.

# COMMAND ----------

import json
from datetime import datetime
from pyspark.sql.functions import col, coalesce, lit, current_timestamp

# COMMAND ----------

CATALOG = spark.conf.get("spark.databricks.catalog", "ppm")
SILVER_SCHEMA = "silver"
GOLD_SCHEMA = "gold"

# COMMAND ----------

# Load source data
projects_df = spark.read.table(f"{CATALOG}.{SILVER_SCHEMA}.notion_projects") \
    .filter(col("is_archived") == False)

programs_df = spark.read.table(f"{CATALOG}.{SILVER_SCHEMA}.notion_programs") \
    .filter(col("is_archived") == False)

# Load gold tables for enrichment
budget_df = spark.read.table(f"{CATALOG}.{GOLD_SCHEMA}.ppm_budget_vs_actual")
forecast_df = spark.read.table(f"{CATALOG}.{GOLD_SCHEMA}.ppm_forecast")
project_risks_df = spark.read.table(f"{CATALOG}.{GOLD_SCHEMA}.ppm_project_risks")

# COMMAND ----------

# Aggregate budget by project
budget_agg = budget_df.groupBy("project_id").agg(
    {"budget_amount": "sum", "actual_amount": "sum", "variance_amount": "sum"}
).select(
    col("project_id"),
    col("sum(budget_amount)").alias("budget_total"),
    col("sum(actual_amount)").alias("actual_total"),
    col("sum(variance_amount)").alias("variance_amount")
)

# COMMAND ----------

# Build enriched projects
projects_enriched = projects_df.alias("p").join(
    programs_df.alias("pr"),
    col("p.program_id") == col("pr.id"),
    "left"
).join(
    budget_agg.alias("b"),
    col("p.id") == col("b.project_id"),
    "left"
).join(
    forecast_df.alias("f").select(
        "project_id",
        "forecast_at_completion",
        "variance_at_completion",
        "burn_rate_pct",
        "is_at_risk"
    ),
    col("p.id") == col("f.project_id"),
    "left"
).join(
    project_risks_df.alias("r").select(
        "project_id",
        col("total_risks").alias("risk_count"),
        col("open_risks"),
        col("critical_risks")
    ),
    col("p.id") == col("r.project_id"),
    "left"
).select(
    col("p.id"),
    col("p.page_id"),
    col("p.name"),
    col("p.program_id"),
    col("pr.name").alias("program_name"),
    coalesce(col("b.budget_total"), col("p.budget_total"), lit(0)).alias("budget_total"),
    coalesce(col("b.actual_total"), lit(0)).alias("actual_total"),
    coalesce(col("b.variance_amount"), lit(0)).alias("variance_amount"),
    coalesce(col("f.forecast_at_completion"), lit(0)).alias("forecast_at_completion"),
    coalesce(col("f.burn_rate_pct"), lit(0)).alias("burn_rate_pct"),
    coalesce(col("f.is_at_risk"), lit(False)).alias("is_at_risk"),
    col("p.currency"),
    col("p.start_date"),
    col("p.end_date"),
    col("p.status"),
    col("p.priority"),
    col("p.owner"),
    coalesce(col("r.risk_count"), lit(0)).alias("risk_count"),
    coalesce(col("r.open_risks"), lit(0)).alias("open_risks"),
    coalesce(col("r.critical_risks"), lit(0)).alias("critical_risks"),
    col("p.is_archived")
)

# Calculate variance percentage
projects_enriched = projects_enriched.withColumn(
    "variance_pct",
    coalesce(
        (col("variance_amount") / col("budget_total") * 100).cast("decimal(10,2)"),
        lit(0)
    )
).withColumn(
    "at_risk_budget_lines",
    # This would need budget line level data - simplified here
    lit(0)
).withColumn(
    "updated_at",
    current_timestamp()
)

# COMMAND ----------

projects_enriched.show(10, truncate=False)

# COMMAND ----------

# Write to gold
gold_table = f"{CATALOG}.{GOLD_SCHEMA}.ppm_projects"

projects_enriched.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(gold_table)

print(f"Written to {gold_table}: {projects_enriched.count()} rows")

# COMMAND ----------

# Summary
total = projects_enriched.count()
at_risk = projects_enriched.filter(col("is_at_risk") == True).count()
active = projects_enriched.filter(col("status").isin("Planning", "In Progress")).count()

print(f"\nProjects Summary:")
print(f"  Total: {total}")
print(f"  Active: {active}")
print(f"  At Risk: {at_risk}")

# COMMAND ----------

dbutils.notebook.exit(json.dumps({
    "status": "success",
    "total_projects": total,
    "active_projects": active,
    "at_risk_projects": at_risk,
    "timestamp": datetime.utcnow().isoformat()
}))
