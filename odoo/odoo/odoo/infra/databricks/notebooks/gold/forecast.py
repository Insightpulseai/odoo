# Databricks notebook source
# MAGIC %md
# MAGIC # Forecast Gold Table
# MAGIC
# MAGIC Computes run-rate forecasts based on current actuals and burn rate.

# COMMAND ----------

import json
from datetime import datetime
from pyspark.sql.functions import (
    col, sum as spark_sum, round as spark_round, when, lit,
    datediff, current_date, current_timestamp, months_between
)

# COMMAND ----------

CATALOG = spark.conf.get("spark.databricks.catalog", "ppm")
SILVER_SCHEMA = "silver"
GOLD_SCHEMA = "gold"

# COMMAND ----------

# Load data
projects_df = spark.read.table(f"{CATALOG}.{SILVER_SCHEMA}.notion_projects") \
    .filter(col("is_archived") == False) \
    .filter(col("status").isin("Planning", "In Progress"))

budget_lines_df = spark.read.table(f"{CATALOG}.{SILVER_SCHEMA}.notion_budget_lines") \
    .filter(col("is_archived") == False)

programs_df = spark.read.table(f"{CATALOG}.{SILVER_SCHEMA}.notion_programs") \
    .filter(col("is_archived") == False)

# COMMAND ----------

# Aggregate actuals per project
actuals = budget_lines_df.groupBy("project_id").agg(
    spark_sum("amount").alias("total_budget"),
    spark_sum(when(col("actual_amount").isNotNull(), col("actual_amount")).otherwise(lit(0))).alias("total_actual")
)

# COMMAND ----------

# Join with projects
projects_with_actuals = projects_df.alias("p").join(
    actuals.alias("a"),
    col("p.id") == col("a.project_id"),
    "left"
).join(
    programs_df.alias("pr"),
    col("p.program_id") == col("pr.id"),
    "left"
).select(
    col("p.id").alias("project_id"),
    col("p.name").alias("project_name"),
    col("p.program_id"),
    col("pr.name").alias("program_name"),
    col("p.budget_total").alias("planned_budget"),
    col("a.total_budget").alias("committed_budget"),
    col("a.total_actual").alias("actual_spend"),
    col("p.start_date"),
    col("p.end_date"),
    col("p.currency"),
    col("p.status")
)

# COMMAND ----------

# Calculate forecast metrics
forecast_df = projects_with_actuals.withColumn(
    "days_elapsed",
    when(col("start_date").isNotNull(),
         datediff(current_date(), col("start_date"))
    ).otherwise(lit(0))
).withColumn(
    "total_days",
    when((col("start_date").isNotNull()) & (col("end_date").isNotNull()),
         datediff(col("end_date"), col("start_date"))
    ).otherwise(lit(365))
).withColumn(
    "days_remaining",
    when(col("end_date").isNotNull(),
         datediff(col("end_date"), current_date())
    ).otherwise(lit(180))
).withColumn(
    # Daily burn rate
    "daily_burn_rate",
    when(col("days_elapsed") > 0,
         col("actual_spend") / col("days_elapsed")
    ).otherwise(lit(0))
).withColumn(
    # Forecast at completion (EAC) = actual + (daily rate * remaining days)
    "forecast_at_completion",
    spark_round(
        col("actual_spend") + (col("daily_burn_rate") * col("days_remaining")),
        2
    )
).withColumn(
    # Variance at completion
    "variance_at_completion",
    col("planned_budget") - col("forecast_at_completion")
).withColumn(
    # Variance percentage
    "variance_pct",
    when(col("planned_budget") > 0,
         spark_round((col("variance_at_completion") / col("planned_budget")) * 100, 2)
    ).otherwise(lit(0))
).withColumn(
    # Burn rate percentage
    "burn_rate_pct",
    when(col("planned_budget") > 0,
         spark_round((col("actual_spend") / col("planned_budget")) * 100, 2)
    ).otherwise(lit(0))
).withColumn(
    # Progress percentage (time-based)
    "progress_pct",
    when(col("total_days") > 0,
         spark_round((col("days_elapsed") / col("total_days")) * 100, 2)
    ).otherwise(lit(0))
).withColumn(
    # At risk flag
    "is_at_risk",
    when(col("variance_at_completion") < 0, lit(True)).otherwise(lit(False))
).withColumn(
    "forecast_date",
    current_date()
).withColumn(
    "updated_at",
    current_timestamp()
)

# COMMAND ----------

forecast_df.show(10, truncate=False)

# COMMAND ----------

# Write to gold
gold_table = f"{CATALOG}.{GOLD_SCHEMA}.ppm_forecast"

forecast_df.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(gold_table)

print(f"Written to {gold_table}: {forecast_df.count()} rows")

# COMMAND ----------

# Summary stats
at_risk = forecast_df.filter(col("is_at_risk") == True).count()
total = forecast_df.count()

print(f"\nForecast Summary:")
print(f"  Total projects: {total}")
print(f"  At risk: {at_risk} ({at_risk/total*100:.1f}%)" if total > 0 else "  At risk: 0")

# COMMAND ----------

dbutils.notebook.exit(json.dumps({
    "status": "success",
    "projects": total,
    "at_risk": at_risk,
    "timestamp": datetime.utcnow().isoformat()
}))
