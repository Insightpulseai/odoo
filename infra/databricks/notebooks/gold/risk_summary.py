# Databricks notebook source
# MAGIC %md
# MAGIC # Risk Summary Gold Table
# MAGIC
# MAGIC Aggregates risk data for portfolio-level visibility.

# COMMAND ----------

import json
from datetime import datetime
from pyspark.sql.functions import (
    col, count, when, lit, current_timestamp
)

# COMMAND ----------

CATALOG = spark.conf.get("spark.databricks.catalog", "ppm")
SILVER_SCHEMA = "silver"
GOLD_SCHEMA = "gold"

# COMMAND ----------

# Load data
risks_df = spark.read.table(f"{CATALOG}.{SILVER_SCHEMA}.notion_risks") \
    .filter(col("is_archived") == False)

projects_df = spark.read.table(f"{CATALOG}.{SILVER_SCHEMA}.notion_projects") \
    .filter(col("is_archived") == False)

programs_df = spark.read.table(f"{CATALOG}.{SILVER_SCHEMA}.notion_programs") \
    .filter(col("is_archived") == False)

print(f"Risks: {risks_df.count()}")

# COMMAND ----------

# Enrich risks with project and program names
enriched_risks = risks_df.alias("r").join(
    projects_df.alias("p"),
    col("r.project_id") == col("p.id"),
    "left"
).join(
    programs_df.alias("pr"),
    col("p.program_id") == col("pr.id"),
    "left"
).select(
    col("r.id").alias("risk_id"),
    col("r.title"),
    col("r.project_id"),
    col("p.name").alias("project_name"),
    col("p.program_id"),
    col("pr.name").alias("program_name"),
    col("r.severity"),
    col("r.probability"),
    col("r.status"),
    col("r.mitigation"),
    col("r.owner")
)

# COMMAND ----------

# Calculate risk score
def risk_score(severity, probability):
    """Calculate numeric risk score from severity and probability."""
    severity_map = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
    probability_map = {"High": 3, "Medium": 2, "Low": 1}
    return severity_map.get(severity, 0) * probability_map.get(probability, 0)

# Add risk score
risk_summary = enriched_risks.withColumn(
    "risk_score",
    when(col("severity") == "Critical",
         when(col("probability") == "High", lit(12))
         .when(col("probability") == "Medium", lit(8))
         .otherwise(lit(4))
    ).when(col("severity") == "High",
         when(col("probability") == "High", lit(9))
         .when(col("probability") == "Medium", lit(6))
         .otherwise(lit(3))
    ).when(col("severity") == "Medium",
         when(col("probability") == "High", lit(6))
         .when(col("probability") == "Medium", lit(4))
         .otherwise(lit(2))
    ).otherwise(
         when(col("probability") == "High", lit(3))
         .when(col("probability") == "Medium", lit(2))
         .otherwise(lit(1))
    )
).withColumn(
    "is_open",
    col("status").isin("Open", "Mitigating")
).withColumn(
    "updated_at",
    current_timestamp()
)

# COMMAND ----------

risk_summary.show(10, truncate=False)

# COMMAND ----------

# Write detailed risk summary
gold_table = f"{CATALOG}.{GOLD_SCHEMA}.ppm_risk_summary"

risk_summary.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(gold_table)

print(f"Written to {gold_table}: {risk_summary.count()} rows")

# COMMAND ----------

# Aggregate by project
project_risk_agg = risk_summary.groupBy("project_id", "project_name", "program_id", "program_name").agg(
    count("*").alias("total_risks"),
    count(when(col("is_open"), True)).alias("open_risks"),
    count(when(col("severity") == "Critical", True)).alias("critical_risks"),
    count(when(col("severity") == "High", True)).alias("high_risks"),
    count(when(col("severity") == "Medium", True)).alias("medium_risks"),
    count(when(col("severity") == "Low", True)).alias("low_risks"),
).withColumn(
    "updated_at",
    current_timestamp()
)

project_risk_agg.show()

# Write project-level aggregation
project_risk_table = f"{CATALOG}.{GOLD_SCHEMA}.ppm_project_risks"
project_risk_agg.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable(project_risk_table)

# COMMAND ----------

# Summary stats
open_risks = risk_summary.filter(col("is_open") == True).count()
critical_open = risk_summary.filter((col("is_open") == True) & (col("severity") == "Critical")).count()

print(f"\nRisk Summary:")
print(f"  Total risks: {risk_summary.count()}")
print(f"  Open risks: {open_risks}")
print(f"  Critical open: {critical_open}")

# COMMAND ----------

dbutils.notebook.exit(json.dumps({
    "status": "success",
    "total_risks": risk_summary.count(),
    "open_risks": open_risks,
    "critical_open": critical_open,
    "timestamp": datetime.utcnow().isoformat()
}))
