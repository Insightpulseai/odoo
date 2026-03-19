# Databricks notebook source
# MAGIC %md
# MAGIC # Notion Bronze Ingestion
# MAGIC
# MAGIC Syncs Notion databases to bronze layer Delta tables.

# COMMAND ----------

import os
import json
from datetime import datetime
from notion_client import Client
from pyspark.sql.functions import lit, current_timestamp

# COMMAND ----------

# Configuration
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
CATALOG = os.environ.get("DATABRICKS_CATALOG", "ppm")
SCHEMA = "bronze"

# Database IDs from secrets
PROGRAMS_DB_ID = dbutils.secrets.get("notion-ppm", "programs_db_id")
PROJECTS_DB_ID = dbutils.secrets.get("notion-ppm", "projects_db_id")
BUDGET_LINES_DB_ID = dbutils.secrets.get("notion-ppm", "budget_lines_db_id")
RISKS_DB_ID = dbutils.secrets.get("notion-ppm", "risks_db_id")

# COMMAND ----------

# Initialize Notion client
notion = Client(auth=NOTION_TOKEN)

# COMMAND ----------

def get_watermark(database_id: str) -> datetime:
    """Get last sync watermark for a database."""
    try:
        result = spark.sql(f"""
            SELECT MAX(last_edited_time) as watermark
            FROM {CATALOG}.{SCHEMA}.sync_watermarks
            WHERE database_id = '{database_id}'
        """).collect()
        if result and result[0]["watermark"]:
            return result[0]["watermark"]
    except Exception as e:
        print(f"No watermark found for {database_id}: {e}")
    return datetime.min

def update_watermark(database_id: str, database_name: str, last_edited: datetime, count: int):
    """Update sync watermark."""
    spark.sql(f"""
        MERGE INTO {CATALOG}.{SCHEMA}.sync_watermarks AS target
        USING (
            SELECT
                '{database_id}' as database_id,
                '{database_name}' as database_name,
                TIMESTAMP('{datetime.utcnow().isoformat()}') as last_synced_at,
                TIMESTAMP('{last_edited.isoformat()}') as last_edited_time,
                {count} as record_count
        ) AS source
        ON target.database_id = source.database_id
        WHEN MATCHED THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
    """)

# COMMAND ----------

def query_notion_database(database_id: str, since: datetime = None):
    """Query all pages from a Notion database."""
    pages = []
    has_more = True
    start_cursor = None

    filter_params = None
    if since and since != datetime.min:
        filter_params = {
            "timestamp": "last_edited_time",
            "last_edited_time": {"after": since.isoformat()}
        }

    while has_more:
        query_params = {
            "database_id": database_id,
            "page_size": 100,
            "sorts": [{"timestamp": "last_edited_time", "direction": "ascending"}]
        }
        if filter_params:
            query_params["filter"] = filter_params
        if start_cursor:
            query_params["start_cursor"] = start_cursor

        response = notion.databases.query(**query_params)
        pages.extend(response.get("results", []))
        has_more = response.get("has_more", False)
        start_cursor = response.get("next_cursor")

    return pages

# COMMAND ----------

def sync_database(database_id: str, database_name: str):
    """Sync a single Notion database to bronze."""
    print(f"Syncing {database_name}...")

    # Get watermark
    watermark = get_watermark(database_id)
    print(f"  Watermark: {watermark}")

    # Query Notion
    pages = query_notion_database(database_id, watermark)
    print(f"  Found {len(pages)} pages")

    if not pages:
        return 0

    # Convert to records
    records = []
    for page in pages:
        records.append({
            "page_id": page["id"],
            "database_id": database_id,
            "database_name": database_name,
            "payload": json.dumps(page),
            "last_edited_time": page["last_edited_time"],
            "is_archived": page.get("archived", False)
        })

    # Create DataFrame
    df = spark.createDataFrame(records)
    df = df.withColumn("synced_at", current_timestamp())

    # Merge to bronze table
    df.createOrReplaceTempView("source_pages")

    spark.sql(f"""
        MERGE INTO {CATALOG}.{SCHEMA}.notion_raw_pages AS target
        USING source_pages AS source
        ON target.page_id = source.page_id AND target.database_id = source.database_id
        WHEN MATCHED THEN UPDATE SET
            payload = source.payload,
            last_edited_time = source.last_edited_time,
            synced_at = source.synced_at,
            is_archived = source.is_archived
        WHEN NOT MATCHED THEN INSERT *
    """)

    # Update watermark
    last_edited = max(datetime.fromisoformat(p["last_edited_time"].replace("Z", "+00:00"))
                      for p in pages)
    update_watermark(database_id, database_name, last_edited, len(pages))

    print(f"  Synced {len(pages)} pages")
    return len(pages)

# COMMAND ----------

# Ensure tables exist
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {CATALOG}.{SCHEMA}.notion_raw_pages (
        page_id STRING,
        database_id STRING,
        database_name STRING,
        payload STRING,
        last_edited_time TIMESTAMP,
        synced_at TIMESTAMP,
        is_archived BOOLEAN
    )
    USING DELTA
    PARTITIONED BY (database_name)
""")

spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {CATALOG}.{SCHEMA}.sync_watermarks (
        database_id STRING,
        database_name STRING,
        last_synced_at TIMESTAMP,
        last_edited_time TIMESTAMP,
        record_count BIGINT
    )
    USING DELTA
""")

# COMMAND ----------

# Sync all databases
databases = [
    (PROGRAMS_DB_ID, "programs"),
    (PROJECTS_DB_ID, "projects"),
    (BUDGET_LINES_DB_ID, "budget_lines"),
    (RISKS_DB_ID, "risks"),
]

total_synced = 0
for db_id, db_name in databases:
    count = sync_database(db_id, db_name)
    total_synced += count

print(f"\nTotal pages synced: {total_synced}")

# COMMAND ----------

# Log completion
dbutils.notebook.exit(json.dumps({
    "status": "success",
    "total_pages_synced": total_synced,
    "timestamp": datetime.utcnow().isoformat()
}))
