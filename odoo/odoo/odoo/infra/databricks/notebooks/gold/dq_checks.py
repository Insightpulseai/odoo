# Databricks notebook source
# MAGIC %md
# MAGIC # Data Quality Checks
# MAGIC
# MAGIC Run data quality checks across all layers and write issues to gold table.

# COMMAND ----------

import json
from datetime import datetime
from pyspark.sql.functions import col, count, when, isnan, isnull, current_timestamp, lit
from pyspark.sql.types import StructType, StructField, StringType, BooleanType, TimestampType
import uuid

# COMMAND ----------

CATALOG = spark.conf.get("spark.databricks.catalog", "ppm")
SILVER_SCHEMA = "silver"
GOLD_SCHEMA = "gold"

# COMMAND ----------

# DQ issue schema
issue_schema = StructType([
    StructField("id", StringType(), False),
    StructField("table_name", StringType(), False),
    StructField("column_name", StringType(), True),
    StructField("issue_type", StringType(), False),
    StructField("severity", StringType(), False),
    StructField("description", StringType(), False),
    StructField("current_value", StringType(), True),
    StructField("expected_value", StringType(), True),
    StructField("detected_at", TimestampType(), False),
    StructField("resolved", BooleanType(), False),
    StructField("resolved_at", TimestampType(), True),
])

issues = []

# COMMAND ----------

def add_issue(table: str, column: str, issue_type: str, severity: str,
              description: str, current_value: str = None, expected_value: str = None):
    """Add a DQ issue to the list."""
    issues.append({
        "id": str(uuid.uuid4()),
        "table_name": table,
        "column_name": column,
        "issue_type": issue_type,
        "severity": severity,
        "description": description,
        "current_value": current_value,
        "expected_value": expected_value,
        "detected_at": datetime.utcnow(),
        "resolved": False,
        "resolved_at": None
    })

# COMMAND ----------

# Check 1: Null rate checks on key columns
def check_null_rate(table: str, column: str, threshold: float = 0.05):
    """Check if null rate exceeds threshold."""
    df = spark.read.table(f"{CATALOG}.{SILVER_SCHEMA}.{table}")
    total = df.count()
    if total == 0:
        return

    null_count = df.filter(col(column).isNull() | (col(column) == "")).count()
    null_rate = null_count / total

    if null_rate > threshold:
        add_issue(
            table=table,
            column=column,
            issue_type="null_rate",
            severity="warning" if null_rate < 0.2 else "critical",
            description=f"Null rate {null_rate:.1%} exceeds threshold {threshold:.1%}",
            current_value=f"{null_rate:.2%}",
            expected_value=f"<{threshold:.1%}"
        )
        print(f"  FAIL: {table}.{column} null rate = {null_rate:.2%}")
    else:
        print(f"  OK: {table}.{column} null rate = {null_rate:.2%}")

# COMMAND ----------

# Check 2: Row count drop detection
EXPECTED_MIN_ROWS = {
    "notion_projects": 10,
    "notion_programs": 2,
    "notion_budget_lines": 5,
    "notion_risks": 0,
}

def check_row_count(table: str, min_rows: int):
    """Check if table has minimum expected rows."""
    df = spark.read.table(f"{CATALOG}.{SILVER_SCHEMA}.{table}")
    row_count = df.count()

    if row_count < min_rows:
        add_issue(
            table=table,
            column=None,
            issue_type="row_count_drop",
            severity="critical" if row_count == 0 else "warning",
            description=f"Row count {row_count} below minimum {min_rows}",
            current_value=str(row_count),
            expected_value=f">={min_rows}"
        )
        print(f"  FAIL: {table} has {row_count} rows (expected >= {min_rows})")
    else:
        print(f"  OK: {table} has {row_count} rows")

# COMMAND ----------

# Check 3: Referential integrity
def check_referential_integrity(child_table: str, child_col: str,
                                 parent_table: str, parent_col: str):
    """Check foreign key integrity."""
    child_df = spark.read.table(f"{CATALOG}.{SILVER_SCHEMA}.{child_table}")
    parent_df = spark.read.table(f"{CATALOG}.{SILVER_SCHEMA}.{parent_table}")

    # Find orphaned records
    orphans = child_df.alias("c").join(
        parent_df.alias("p"),
        col(f"c.{child_col}") == col(f"p.{parent_col}"),
        "left_anti"
    ).filter(col(f"c.{child_col}").isNotNull())

    orphan_count = orphans.count()

    if orphan_count > 0:
        add_issue(
            table=child_table,
            column=child_col,
            issue_type="referential",
            severity="warning",
            description=f"{orphan_count} orphaned records (no matching {parent_table})",
            current_value=str(orphan_count),
            expected_value="0"
        )
        print(f"  FAIL: {child_table}.{child_col} has {orphan_count} orphans")
    else:
        print(f"  OK: {child_table}.{child_col} referential integrity")

# COMMAND ----------

# Check 4: Data freshness
def check_freshness(table: str, timestamp_col: str, max_hours: int = 24):
    """Check if data is stale."""
    df = spark.read.table(f"{CATALOG}.{SILVER_SCHEMA}.{table}")

    latest = df.agg({timestamp_col: "max"}).collect()[0][0]

    if latest:
        hours_old = (datetime.utcnow() - latest).total_seconds() / 3600

        if hours_old > max_hours:
            add_issue(
                table=table,
                column=timestamp_col,
                issue_type="freshness",
                severity="warning" if hours_old < max_hours * 2 else "critical",
                description=f"Data is {hours_old:.1f} hours old (max {max_hours}h)",
                current_value=f"{hours_old:.1f}h",
                expected_value=f"<{max_hours}h"
            )
            print(f"  FAIL: {table} is {hours_old:.1f} hours old")
        else:
            print(f"  OK: {table} is {hours_old:.1f} hours old")

# COMMAND ----------

# Run all checks
print("=== Null Rate Checks ===")
check_null_rate("notion_projects", "name")
check_null_rate("notion_projects", "budget_total")
check_null_rate("notion_budget_lines", "amount")
check_null_rate("notion_budget_lines", "project_id")

print("\n=== Row Count Checks ===")
for table, min_rows in EXPECTED_MIN_ROWS.items():
    check_row_count(table, min_rows)

print("\n=== Referential Integrity Checks ===")
check_referential_integrity("notion_projects", "program_id", "notion_programs", "id")
check_referential_integrity("notion_budget_lines", "project_id", "notion_projects", "id")
check_referential_integrity("notion_risks", "project_id", "notion_projects", "id")

print("\n=== Freshness Checks ===")
check_freshness("notion_projects", "synced_at", 24)
check_freshness("notion_budget_lines", "synced_at", 24)

# COMMAND ----------

# Write issues to gold table
print(f"\n=== Summary: {len(issues)} issues found ===")

if issues:
    issues_df = spark.createDataFrame(issues, issue_schema)
    issues_df.show(truncate=False)

    # Merge with existing issues
    gold_table = f"{CATALOG}.{GOLD_SCHEMA}.dq_issues"

    issues_df.createOrReplaceTempView("new_issues")

    spark.sql(f"""
        MERGE INTO {gold_table} AS target
        USING new_issues AS source
        ON target.table_name = source.table_name
           AND target.column_name <=> source.column_name
           AND target.issue_type = source.issue_type
           AND target.resolved = false
        WHEN MATCHED THEN UPDATE SET
            current_value = source.current_value,
            detected_at = source.detected_at
        WHEN NOT MATCHED THEN INSERT *
    """)

    print(f"Merged {len(issues)} issues to {gold_table}")

# COMMAND ----------

dbutils.notebook.exit(json.dumps({
    "status": "success",
    "issues_found": len(issues),
    "critical": len([i for i in issues if i["severity"] == "critical"]),
    "warning": len([i for i in issues if i["severity"] == "warning"]),
    "timestamp": datetime.utcnow().isoformat()
}))
