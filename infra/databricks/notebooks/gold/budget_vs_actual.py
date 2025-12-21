# Databricks notebook source
# MAGIC %md
# MAGIC # Budget vs Actual Gold Table
# MAGIC
# MAGIC Computes budget vs actual metrics by period, program, and project.

# COMMAND ----------

import json
from datetime import datetime
from pyspark.sql.functions import (
    col, sum as spark_sum, round as spark_round, coalesce, lit,
    date_trunc, when, current_timestamp
)

# COMMAND ----------

CATALOG = spark.conf.get("spark.databricks.catalog", "ppm")
SILVER_SCHEMA = "silver"
GOLD_SCHEMA = "gold"

# COMMAND ----------

# Load silver tables
projects_df = spark.read.table(f"{CATALOG}.{SILVER_SCHEMA}.notion_projects") \
    .filter(col("is_archived") == False)

budget_lines_df = spark.read.table(f"{CATALOG}.{SILVER_SCHEMA}.notion_budget_lines") \
    .filter(col("is_archived") == False)

programs_df = spark.read.table(f"{CATALOG}.{SILVER_SCHEMA}.notion_programs") \
    .filter(col("is_archived") == False)

print(f"Projects: {projects_df.count()}")
print(f"Budget Lines: {budget_lines_df.count()}")
print(f"Programs: {programs_df.count()}")

# COMMAND ----------

# Join projects with programs to get program names
projects_with_programs = projects_df.alias("p").join(
    programs_df.alias("pr"),
    col("p.program_id") == col("pr.id"),
    "left"
).select(
    col("p.id").alias("project_id"),
    col("p.page_id").alias("project_page_id"),
    col("p.name").alias("project_name"),
    col("p.program_id"),
    col("pr.name").alias("program_name"),
    col("p.budget_total"),
    col("p.currency"),
    col("p.status"),
    col("p.priority")
)

# COMMAND ----------

# Aggregate budget lines by project and category
budget_agg = budget_lines_df.groupBy("project_id", "category").agg(
    spark_sum("amount").alias("budget_amount"),
    spark_sum(coalesce(col("actual_amount"), lit(0))).alias("actual_amount")
)

# COMMAND ----------

# Join projects with aggregated budget lines
budget_vs_actual = projects_with_programs.join(
    budget_agg,
    projects_with_programs.project_id == budget_agg.project_id,
    "left"
).select(
    projects_with_programs.project_id,
    projects_with_programs.project_page_id,
    projects_with_programs.project_name,
    projects_with_programs.program_id,
    projects_with_programs.program_name,
    budget_agg.category,
    coalesce(budget_agg.budget_amount, lit(0)).alias("budget_amount"),
    coalesce(budget_agg.actual_amount, lit(0)).alias("actual_amount"),
    projects_with_programs.currency,
    projects_with_programs.status,
    projects_with_programs.priority
)

# Calculate variance
budget_vs_actual = budget_vs_actual.withColumn(
    "variance_amount",
    col("budget_amount") - col("actual_amount")
).withColumn(
    "variance_pct",
    when(col("budget_amount") > 0,
         spark_round((col("variance_amount") / col("budget_amount")) * 100, 2)
    ).otherwise(lit(0))
).withColumn(
    "period_month",
    date_trunc("month", current_timestamp())
).withColumn(
    "updated_at",
    current_timestamp()
)

# COMMAND ----------

# Show sample
budget_vs_actual.show(10, truncate=False)

# COMMAND ----------

# Write to gold table
gold_table = f"{CATALOG}.{GOLD_SCHEMA}.ppm_budget_vs_actual"

budget_vs_actual.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(gold_table)

print(f"Written to {gold_table}: {budget_vs_actual.count()} rows")

# COMMAND ----------

# Create summary view
summary = budget_vs_actual.groupBy("program_id", "program_name").agg(
    spark_sum("budget_amount").alias("total_budget"),
    spark_sum("actual_amount").alias("total_actual"),
    spark_sum("variance_amount").alias("total_variance")
).withColumn(
    "variance_pct",
    when(col("total_budget") > 0,
         spark_round((col("total_variance") / col("total_budget")) * 100, 2)
    ).otherwise(lit(0))
).withColumn(
    "burn_rate",
    when(col("total_budget") > 0,
         spark_round((col("total_actual") / col("total_budget")) * 100, 2)
    ).otherwise(lit(0))
)

summary.show()

# COMMAND ----------

dbutils.notebook.exit(json.dumps({
    "status": "success",
    "rows": budget_vs_actual.count(),
    "timestamp": datetime.utcnow().isoformat()
}))
