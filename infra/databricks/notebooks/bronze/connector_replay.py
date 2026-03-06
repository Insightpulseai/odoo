# Databricks notebook source
# MAGIC %md
# MAGIC # Connector Replay / Backfill
# MAGIC
# MAGIC Parameterized notebook for replaying connector syncs.
# MAGIC Supports modes: cursor, time_range, full, dry_run.

# COMMAND ----------

import os
import json

# COMMAND ----------

# Parameters
dbutils.widgets.text("connector_id", "", "Connector ID")
dbutils.widgets.dropdown("mode", "dry_run", ["cursor", "time_range", "full", "dry_run"], "Replay Mode")
dbutils.widgets.text("cursor_json", "{}", "Cursor JSON (for cursor mode)")
dbutils.widgets.text("start_time", "", "Start Time ISO8601 (for time_range mode)")
dbutils.widgets.text("end_time", "", "End Time ISO8601 (for time_range mode)")

connector_id = dbutils.widgets.get("connector_id")
mode = dbutils.widgets.get("mode")
cursor_json = dbutils.widgets.get("cursor_json")
start_time = dbutils.widgets.get("start_time")
end_time = dbutils.widgets.get("end_time")

if not connector_id:
    dbutils.notebook.exit(json.dumps({"status": "error", "message": "connector_id required"}))

CATALOG = os.environ.get("DATABRICKS_CATALOG", "ppm")

print(f"Connector: {connector_id}")
print(f"Catalog: {CATALOG}")
print(f"Mode: {mode}")

# COMMAND ----------

# Build connector config from Databricks secrets
def load_config(connector_id: str) -> dict:
    """Load connector-specific config from Databricks secrets."""
    scope = "notion-ppm"

    if connector_id == "notion":
        return {
            "token": dbutils.secrets.get(scope, "notion_token"),
            "databases": {
                "programs": dbutils.secrets.get(scope, "programs_db_id"),
                "projects": dbutils.secrets.get(scope, "projects_db_id"),
                "budget_lines": dbutils.secrets.get(scope, "budget_lines_db_id"),
                "risks": dbutils.secrets.get(scope, "risks_db_id"),
            },
        }
    elif connector_id == "azure":
        return {
            "subscription_id": dbutils.secrets.get(scope, "azure_subscription_id"),
            "client_id": dbutils.secrets.get(scope, "azure_client_id"),
            "client_secret": dbutils.secrets.get(scope, "azure_client_secret"),
            "tenant_id": dbutils.secrets.get(scope, "azure_tenant_id"),
        }
    elif connector_id == "odoo_pg":
        return {
            "pg_host": dbutils.secrets.get(scope, "odoo_pg_host"),
            "pg_port": int(dbutils.secrets.get(scope, "odoo_pg_port")),
            "pg_database": dbutils.secrets.get(scope, "odoo_pg_database"),
            "pg_user": dbutils.secrets.get(scope, "odoo_pg_user"),
            "pg_password": dbutils.secrets.get(scope, "odoo_pg_password"),
        }
    elif connector_id == "github":
        return {
            "github_token": dbutils.secrets.get(scope, "github_token"),
            "org": dbutils.secrets.get(scope, "github_org"),
        }
    else:
        raise ValueError(f"Unknown connector_id: {connector_id}")

# COMMAND ----------

from workbench.connectors import create_connector
from workbench.connectors.replay import ReplayEngine, ReplayMode, ReplayParams

# Import connectors to trigger registration
import workbench.connectors.notion  # noqa: F401
import workbench.connectors.azure  # noqa: F401
import workbench.connectors.odoo_pg  # noqa: F401
import workbench.connectors.github_api  # noqa: F401

# COMMAND ----------

# Load config and create connector
config = load_config(connector_id)
connector = create_connector(connector_id, config)

# Load Slack webhook
try:
    slack_url = dbutils.secrets.get("notion-ppm", "slack_webhook_url")
except Exception:
    slack_url = ""

# COMMAND ----------

# Build replay params
replay_mode = ReplayMode(mode)
params = ReplayParams(mode=replay_mode)

if replay_mode == ReplayMode.CURSOR:
    params.cursor = json.loads(cursor_json)
elif replay_mode == ReplayMode.TIME_RANGE:
    params.start_time = start_time
    if end_time:
        params.end_time = end_time

print(f"Replay params: mode={params.mode.value}")
if params.cursor:
    print(f"  cursor: {json.dumps(params.cursor)}")
if params.start_time:
    print(f"  start_time: {params.start_time}")
if params.end_time:
    print(f"  end_time: {params.end_time}")

# COMMAND ----------

# Execute replay
engine = ReplayEngine(
    spark=spark,
    catalog=CATALOG,
    schema="bronze",
    slack_webhook_url=slack_url,
)

result = engine.replay(connector, params)

# COMMAND ----------

# Print result
print(f"\nReplay result:")
print(f"  Mode: {result.mode.value}")
print(f"  Success: {result.success}")
if result.dry_run:
    print(f"  Ops collected: {result.ops_collected}")
    print(f"  Ops by type: {result.ops_by_type}")
elif result.sync_result:
    print(f"  Status: {result.sync_result.status.value}")
    print(f"  Duration: {result.sync_result.duration_seconds:.1f}s")
    print(f"  Tables synced: {result.sync_result.tables_synced}")
if result.error:
    print(f"  Error: {result.error}")

# COMMAND ----------

# Close connector
connector.close()

# COMMAND ----------

# Exit with result
exit_data = {
    "mode": result.mode.value,
    "connector_id": result.connector_id,
    "success": result.success,
    "dry_run": result.dry_run,
    "ops_collected": result.ops_collected,
    "ops_by_type": result.ops_by_type,
    "error": result.error,
}
if result.sync_result:
    exit_data["sync_status"] = result.sync_result.status.value
    exit_data["tables_synced"] = result.sync_result.tables_synced
    exit_data["duration_seconds"] = result.sync_result.duration_seconds

dbutils.notebook.exit(json.dumps(exit_data))
