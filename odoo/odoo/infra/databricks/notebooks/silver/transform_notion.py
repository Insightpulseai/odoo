# Databricks notebook source
# MAGIC %md
# MAGIC # Notion Silver Transformation
# MAGIC
# MAGIC Transform bronze Notion data to normalized silver tables.

# COMMAND ----------

import json
from datetime import datetime
from pyspark.sql.functions import (
    col, from_json, get_json_object, current_timestamp,
    when, lit, coalesce
)
from pyspark.sql.types import StringType, DoubleType, TimestampType, BooleanType

# COMMAND ----------

# Parameters
dbutils.widgets.text("table_name", "projects")
table_name = dbutils.widgets.get("table_name")

CATALOG = spark.conf.get("spark.databricks.catalog", "ppm")
BRONZE_SCHEMA = "bronze"
SILVER_SCHEMA = "silver"

print(f"Processing: {table_name}")

# COMMAND ----------

# Column extraction functions
def extract_title(payload_col, prop_name):
    """Extract title text from Notion title property."""
    return get_json_object(
        get_json_object(payload_col, f"$.properties.{prop_name}.title[0]"),
        "$.plain_text"
    )

def extract_rich_text(payload_col, prop_name):
    """Extract text from Notion rich_text property."""
    return get_json_object(
        get_json_object(payload_col, f"$.properties.{prop_name}.rich_text[0]"),
        "$.plain_text"
    )

def extract_select(payload_col, prop_name):
    """Extract value from Notion select property."""
    return get_json_object(
        get_json_object(payload_col, f"$.properties.{prop_name}.select"),
        "$.name"
    )

def extract_number(payload_col, prop_name):
    """Extract number from Notion number property."""
    return get_json_object(payload_col, f"$.properties.{prop_name}.number").cast(DoubleType())

def extract_date(payload_col, prop_name):
    """Extract date from Notion date property."""
    return get_json_object(
        get_json_object(payload_col, f"$.properties.{prop_name}.date"),
        "$.start"
    ).cast(TimestampType())

def extract_person(payload_col, prop_name):
    """Extract person name from Notion people property."""
    return get_json_object(
        get_json_object(payload_col, f"$.properties.{prop_name}.people[0]"),
        "$.name"
    )

def extract_relation(payload_col, prop_name):
    """Extract first relation ID from Notion relation property."""
    return get_json_object(
        get_json_object(payload_col, f"$.properties.{prop_name}.relation[0]"),
        "$.id"
    )

# COMMAND ----------

# Table-specific transformations
def transform_programs(df):
    """Transform programs bronze data to silver."""
    return df.select(
        col("page_id").alias("id"),
        col("page_id"),
        extract_title(col("payload"), "Name").alias("name"),
        extract_person(col("payload"), "Owner").alias("owner"),
        extract_date(col("payload"), "Start Date").alias("start_date"),
        extract_date(col("payload"), "End Date").alias("end_date"),
        extract_select(col("payload"), "Status").alias("status"),
        extract_rich_text(col("payload"), "Description").alias("description"),
        col("last_edited_time"),
        current_timestamp().alias("synced_at"),
        col("is_archived")
    )

def transform_projects(df):
    """Transform projects bronze data to silver."""
    return df.select(
        col("page_id").alias("id"),
        col("page_id"),
        extract_relation(col("payload"), "Program").alias("program_id"),
        extract_title(col("payload"), "Name").alias("name"),
        extract_number(col("payload"), "Budget Total").alias("budget_total"),
        coalesce(extract_select(col("payload"), "Currency"), lit("USD")).alias("currency"),
        extract_date(col("payload"), "Start Date").alias("start_date"),
        extract_date(col("payload"), "End Date").alias("end_date"),
        extract_select(col("payload"), "Status").alias("status"),
        extract_select(col("payload"), "Priority").alias("priority"),
        extract_person(col("payload"), "Owner").alias("owner"),
        col("last_edited_time"),
        current_timestamp().alias("synced_at"),
        col("is_archived")
    )

def transform_budget_lines(df):
    """Transform budget_lines bronze data to silver."""
    return df.select(
        col("page_id").alias("id"),
        col("page_id"),
        extract_relation(col("payload"), "Project").alias("project_id"),
        extract_select(col("payload"), "Category").alias("category"),
        extract_rich_text(col("payload"), "Vendor").alias("vendor"),
        extract_rich_text(col("payload"), "Description").alias("description"),
        extract_number(col("payload"), "Amount").alias("amount"),
        extract_date(col("payload"), "Committed Date").alias("committed_date"),
        extract_date(col("payload"), "Invoice Date").alias("invoice_date"),
        extract_date(col("payload"), "Paid Date").alias("paid_date"),
        extract_number(col("payload"), "Actual Amount").alias("actual_amount"),
        extract_rich_text(col("payload"), "Notes").alias("notes"),
        lit("USD").alias("currency"),
        col("last_edited_time"),
        current_timestamp().alias("synced_at"),
        col("is_archived")
    )

def transform_risks(df):
    """Transform risks bronze data to silver."""
    return df.select(
        col("page_id").alias("id"),
        col("page_id"),
        extract_relation(col("payload"), "Project").alias("project_id"),
        extract_title(col("payload"), "Title").alias("title"),
        extract_select(col("payload"), "Severity").alias("severity"),
        extract_select(col("payload"), "Probability").alias("probability"),
        extract_select(col("payload"), "Status").alias("status"),
        extract_rich_text(col("payload"), "Mitigation").alias("mitigation"),
        extract_person(col("payload"), "Owner").alias("owner"),
        col("last_edited_time"),
        current_timestamp().alias("synced_at"),
        col("is_archived")
    )

# COMMAND ----------

# Load bronze data for this table
bronze_df = spark.read.table(f"{CATALOG}.{BRONZE_SCHEMA}.notion_raw_pages") \
    .filter(col("database_name") == table_name)

print(f"Bronze records: {bronze_df.count()}")

# COMMAND ----------

# Apply transformation
transformers = {
    "programs": transform_programs,
    "projects": transform_projects,
    "budget_lines": transform_budget_lines,
    "risks": transform_risks,
}

if table_name not in transformers:
    raise ValueError(f"Unknown table: {table_name}")

silver_df = transformers[table_name](bronze_df)

print(f"Silver records: {silver_df.count()}")
silver_df.show(5, truncate=False)

# COMMAND ----------

# Write to silver table
silver_table = f"{CATALOG}.{SILVER_SCHEMA}.notion_{table_name}"

silver_df.createOrReplaceTempView("silver_source")

spark.sql(f"""
    MERGE INTO {silver_table} AS target
    USING silver_source AS source
    ON target.id = source.id
    WHEN MATCHED THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *
""")

print(f"Merged to {silver_table}")

# COMMAND ----------

dbutils.notebook.exit(json.dumps({
    "status": "success",
    "table": table_name,
    "records": silver_df.count(),
    "timestamp": datetime.utcnow().isoformat()
}))
