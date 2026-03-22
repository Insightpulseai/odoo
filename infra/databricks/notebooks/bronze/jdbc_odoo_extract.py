# Databricks notebook source
# MAGIC %md
# MAGIC # JDBC Extract: Odoo PostgreSQL → ADLS Bronze
# MAGIC
# MAGIC Incremental extract from Odoo PG (Azure Database for PostgreSQL Flexible Server)
# MAGIC to Parquet files on ADLS Gen2 Bronze zone.
# MAGIC
# MAGIC **Replaces**: Supabase ETL CDC (Private Alpha, not available for self-hosted)
# MAGIC **Pattern**: JDBC incremental extract with write_id watermark
# MAGIC **Downstream**: DLT Auto Loader (`read_files`) picks up Parquet automatically
# MAGIC
# MAGIC Schedule: Every 15 minutes via Databricks Job
# MAGIC
# MAGIC Required secrets (Databricks secret scope `odoo-pg`):
# MAGIC   - `jdbc_url`: JDBC connection string to Odoo PG
# MAGIC   - `jdbc_user`: PostgreSQL user (read-only recommended)
# MAGIC   - `jdbc_password`: PostgreSQL password

# COMMAND ----------

import json
from datetime import datetime, timezone
from pyspark.sql import functions as F

# COMMAND ----------

# Configuration
BRONZE_PATH = spark.conf.get("bronze_storage_path", "abfss://bronze@stipaidevlake.dfs.core.windows.net")
WATERMARK_PATH = f"{BRONZE_PATH}/odoo_finance/_watermarks"
SECRET_SCOPE = "ipai-odoo-pg"

# Secrets: host, user, password stored in Databricks secret scope
PG_HOST = dbutils.secrets.get(scope=SECRET_SCOPE, key="host")
PG_USER = dbutils.secrets.get(scope=SECRET_SCOPE, key="user")
PG_PASSWORD = dbutils.secrets.get(scope=SECRET_SCOPE, key="password")

# Production database: 'odoo' on ipai-odoo-dev-pg (Azure PG Flexible Server)
JDBC_URL = f"jdbc:postgresql://{PG_HOST}:5432/odoo?sslmode=require"
JDBC_USER = PG_USER
JDBC_PASSWORD = PG_PASSWORD

JDBC_PROPERTIES = {
    "user": JDBC_USER,
    "password": JDBC_PASSWORD,
    "driver": "org.postgresql.Driver",
    "fetchsize": "10000",
}

# Tables to extract with their incremental column
TABLES = [
    {"source": "account_move",           "incremental_col": "write_date"},
    {"source": "account_move_line",      "incremental_col": "write_date"},
    {"source": "account_account",        "incremental_col": "write_date"},
    {"source": "account_tax",            "incremental_col": "write_date"},
    {"source": "res_partner",            "incremental_col": "write_date"},
    {"source": "hr_expense",             "incremental_col": "write_date"},
    {"source": "project_project",        "incremental_col": "write_date"},
    {"source": "sale_order_line",        "incremental_col": "write_date"},
    {"source": "account_analytic_line",  "incremental_col": "write_date"},
    {"source": "hr_employee",            "incremental_col": "write_date"},
]

# COMMAND ----------

def get_watermark(table_name: str) -> str:
    """Read last extracted watermark for a table. Returns ISO timestamp or epoch."""
    try:
        path = f"{WATERMARK_PATH}/{table_name}.json"
        content = dbutils.fs.head(path, 256)
        data = json.loads(content)
        return data.get("last_watermark", "1970-01-01T00:00:00")
    except Exception:
        return "1970-01-01T00:00:00"


def set_watermark(table_name: str, watermark: str):
    """Persist watermark after successful extract."""
    path = f"{WATERMARK_PATH}/{table_name}.json"
    content = json.dumps({
        "table": table_name,
        "last_watermark": watermark,
        "extracted_at": datetime.now(timezone.utc).isoformat(),
    })
    dbutils.fs.put(path, content, overwrite=True)

# COMMAND ----------

def extract_table(table_config: dict):
    """Extract one table incrementally from Odoo PG and write as Parquet to ADLS."""
    table_name = table_config["source"]
    incremental_col = table_config["incremental_col"]
    last_watermark = get_watermark(table_name)

    print(f"Extracting {table_name} where {incremental_col} > '{last_watermark}'")

    # Build query with incremental predicate
    query = f"""
        (SELECT *, '{datetime.now(timezone.utc).isoformat()}' AS _extracted_at
         FROM {table_name}
         WHERE {incremental_col} > '{last_watermark}'::timestamp
         ORDER BY {incremental_col}) AS extract
    """

    df = (
        spark.read
        .jdbc(url=JDBC_URL, table=query, properties=JDBC_PROPERTIES)
    )

    row_count = df.count()

    if row_count == 0:
        print(f"  {table_name}: no new rows since {last_watermark}")
        return 0

    # Add extraction metadata
    df = df.withColumn("_dlt_ingest_timestamp", F.current_timestamp())

    # Write as Parquet to ADLS Bronze zone (append mode for Auto Loader)
    output_path = f"{BRONZE_PATH}/odoo_finance/{table_name}/"
    (
        df.write
        .mode("append")
        .option("mergeSchema", "true")
        .parquet(output_path)
    )

    # Update watermark to max value extracted
    new_watermark = (
        df.agg(F.max(incremental_col).alias("max_wm"))
        .collect()[0]["max_wm"]
    )
    if new_watermark:
        set_watermark(table_name, str(new_watermark))

    print(f"  {table_name}: extracted {row_count} rows, watermark → {new_watermark}")
    return row_count

# COMMAND ----------

# MAGIC %md
# MAGIC ## Run extraction for all tables

# COMMAND ----------

total_rows = 0
results = []

for table_config in TABLES:
    try:
        count = extract_table(table_config)
        results.append({"table": table_config["source"], "rows": count, "status": "OK"})
        total_rows += count
    except Exception as e:
        results.append({"table": table_config["source"], "rows": 0, "status": f"ERROR: {e}"})
        print(f"  ERROR extracting {table_config['source']}: {e}")

# COMMAND ----------

# Summary
print(f"\n{'='*60}")
print(f"JDBC Extract Complete: {total_rows} total rows across {len(TABLES)} tables")
print(f"{'='*60}")
for r in results:
    status_icon = "OK" if r["status"] == "OK" else "FAIL"
    print(f"  [{status_icon}] {r['table']}: {r['rows']} rows")
