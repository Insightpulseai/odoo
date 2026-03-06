# Databricks notebook source
# MAGIC %md
# MAGIC # Generic Connector Sync
# MAGIC
# MAGIC Parameterized notebook that runs any registered connector via SyncEngine.
# MAGIC Pass `connector_id` as a widget parameter. Secrets are loaded from
# MAGIC Databricks scope `notion-ppm`.

# COMMAND ----------

import os
import json

# COMMAND ----------

# Parameters
dbutils.widgets.text("connector_id", "", "Connector ID")
dbutils.widgets.text("history_mode", "false", "Enable SCD2 history mode")

connector_id = dbutils.widgets.get("connector_id")
history_mode = dbutils.widgets.get("history_mode").lower() == "true"

if not connector_id:
    dbutils.notebook.exit(json.dumps({"status": "error", "message": "connector_id required"}))

CATALOG = os.environ.get("DATABRICKS_CATALOG", "ppm")

print(f"Connector: {connector_id}")
print(f"Catalog: {CATALOG}")
print(f"History mode: {history_mode}")

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

# Import SDK (ensure wheel is installed on cluster)
from workbench.connectors import create_connector, SyncEngine

# Also import connector modules to trigger registration
import workbench.connectors.notion  # noqa: F401
import workbench.connectors.azure  # noqa: F401
import workbench.connectors.odoo_pg  # noqa: F401
import workbench.connectors.github_api  # noqa: F401

# COMMAND ----------

# Load config and create connector
config = load_config(connector_id)
connector = create_connector(connector_id, config)

# Optionally load Slack webhook for alerts
try:
    slack_url = dbutils.secrets.get("notion-ppm", "slack_webhook_url")
except Exception:
    slack_url = ""

# COMMAND ----------

# Run sync via SyncEngine
engine = SyncEngine(
    spark=spark,
    connector=connector,
    catalog=CATALOG,
    schema="bronze",
    slack_webhook_url=slack_url,
    history_mode=history_mode,
)

result = engine.run()

print(f"\nSync result: {result.status.value}")
print(f"Run ID: {result.run_id}")
print(f"Duration: {result.duration_seconds:.1f}s")
print(f"Tables synced: {result.tables_synced}")
if result.error_message:
    print(f"Error: {result.error_message}")

# COMMAND ----------

# Close connector resources
connector.close()

# COMMAND ----------

# Exit with result
dbutils.notebook.exit(json.dumps({
    "status": result.status.value,
    "run_id": result.run_id,
    "connector_id": connector_id,
    "tables_synced": result.tables_synced,
    "duration_seconds": result.duration_seconds,
    "error_message": result.error_message,
}))
