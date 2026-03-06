# Runtime Prerequisites

## Environment Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABRICKS_HOST` | Databricks workspace URL | `adb-1234567890.1.azuredatabricks.net` |
| `DATABRICKS_TOKEN` | Personal access token or service principal token | `dapi...` |
| `DATABRICKS_CATALOG` | Unity Catalog name | `ppm` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `SLACK_WEBHOOK_URL` | Slack webhook for alerts | (none -- alerts disabled) |

## Secret Scopes (Databricks)

### Scope: `notion-ppm`

| Key | Connector | Description |
|-----|-----------|-------------|
| `notion_token` | notion | Notion API integration token |
| `programs_db_id` | notion | Programs database ID |
| `projects_db_id` | notion | Projects database ID |
| `budget_lines_db_id` | notion | Budget lines database ID |
| `risks_db_id` | notion | Risks database ID |
| `azure_subscription_id` | azure | Azure subscription ID |
| `azure_client_id` | azure | Azure service principal client ID |
| `azure_client_secret` | azure | Azure service principal secret |
| `azure_tenant_id` | azure | Azure AD tenant ID |
| `odoo_pg_host` | odoo_pg | PostgreSQL host |
| `odoo_pg_port` | odoo_pg | PostgreSQL port |
| `odoo_pg_database` | odoo_pg | Database name |
| `odoo_pg_user` | odoo_pg | Database user |
| `odoo_pg_password` | odoo_pg | Database password |
| `github_token` | github | GitHub personal access token |
| `github_org` | github | GitHub organization name |
| `slack_webhook_url` | (global) | Slack webhook URL for alerts |

## Unity Catalog

### Required Schemas

| Schema | Purpose |
|--------|---------|
| `{catalog}.bronze` | Raw connector output tables |
| `{catalog}.silver` | Cleaned/transformed tables |
| `{catalog}.gold` | Business-level aggregates |

### Required Tables (auto-created by SDK)

| Table | Created By | Purpose |
|-------|-----------|---------|
| `{catalog}.bronze.connector_state` | StateManager | Connector cursor persistence |
| `{catalog}.bronze.sync_runs` | SyncMonitor | Run metrics and history |

## Cluster Configuration

### Minimum Requirements

| Setting | Value |
|---------|-------|
| Spark Version | 14.3.x-scala2.12 or later |
| Node Type | Standard_DS3_v2 (or equivalent) |
| Workers | 1 (connectors are single-threaded) |
| Auto-termination | 30 minutes |

### Required Libraries

| Library | Connector | Version |
|---------|-----------|---------|
| `psycopg2-binary` | odoo_pg | >= 2.9.0 |

## Pre-flight Validation

Run before first deployment:

```bash
cd infra/databricks
PYTHONPATH=src:$PYTHONPATH python3 scripts/validate_runtime_env.py --check-local
```

Run with full Databricks connectivity:

```bash
PYTHONPATH=src:$PYTHONPATH python3 scripts/validate_runtime_env.py
```

Check specific connector:

```bash
PYTHONPATH=src:$PYTHONPATH python3 scripts/validate_runtime_env.py --connector notion
```
