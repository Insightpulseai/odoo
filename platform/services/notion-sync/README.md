# Notion Sync Service

Syncs Notion databases to Databricks Delta Lake for Finance PPM analytics.

## Overview

This service provides:
- Incremental sync from Notion to Databricks (bronze layer)
- Column mapping and transformation (silver layer)
- Watermark-based change tracking
- Retry logic for API resilience
- CLI for manual and scheduled execution

## Architecture

```
Notion Databases                    Databricks
┌─────────────────┐                ┌──────────────────────────────┐
│ Programs        │────────┐       │ Bronze                       │
│ Projects        │────────┤       │ ├─ notion_raw_pages          │
│ Budget Lines    │────────┼──────▶│ └─ sync_watermarks           │
│ Risks           │────────┤       │                              │
│ Actions         │────────┘       │ Silver                       │
└─────────────────┘                │ ├─ notion_programs           │
                                   │ ├─ notion_projects           │
                                   │ ├─ notion_budget_lines       │
                                   │ └─ notion_risks              │
                                   │                              │
                                   │ Gold (computed separately)   │
                                   │ ├─ ppm_budget_vs_actual      │
                                   │ └─ ppm_forecast              │
                                   └──────────────────────────────┘
```

## Installation

```bash
# Install with pip
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

## Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required environment variables:

| Variable | Description |
|----------|-------------|
| `NOTION_TOKEN` | Notion integration token |
| `NOTION_PROGRAMS_DB_ID` | Programs database ID |
| `NOTION_PROJECTS_DB_ID` | Projects database ID |
| `NOTION_BUDGET_LINES_DB_ID` | Budget Lines database ID |
| `NOTION_RISKS_DB_ID` | Risks database ID |
| `DATABRICKS_HOST` | Databricks workspace URL |
| `DATABRICKS_TOKEN` | Databricks access token |
| `DATABRICKS_WAREHOUSE_ID` | SQL warehouse ID |

## Usage

### CLI Commands

```bash
# Sync all databases (incremental)
notion-sync sync

# Force full sync
notion-sync sync --full-sync

# Dry run (no writes to Databricks)
notion-sync sync --dry-run

# Sync a specific database
notion-sync sync-database projects

# Health check
notion-sync health
```

### Programmatic Usage

```python
from notion_sync.config import Config
from notion_sync.sync import SyncEngine

config = Config.from_env()
engine = SyncEngine(config)

# Run sync
summary = engine.sync_all(full_sync=False)

print(f"Synced {summary.total_pages_synced} pages")
```

## Notion Database Schema

### Programs

| Property | Type | Description |
|----------|------|-------------|
| Name | title | Program name |
| Owner | person | Program owner |
| Start Date | date | Start date |
| End Date | date | End date |
| Status | select | Active/On Hold/Completed |
| Description | rich_text | Description |

### Projects

| Property | Type | Description |
|----------|------|-------------|
| Name | title | Project name |
| Program | relation | Parent program |
| Budget Total | number | Total budget |
| Currency | select | USD/EUR/PHP |
| Status | select | Planning/In Progress/Completed |
| Priority | select | High/Medium/Low |
| Owner | person | Project owner |

### Budget Lines

| Property | Type | Description |
|----------|------|-------------|
| Project | relation | Parent project |
| Category | select | CapEx/OpEx |
| Vendor | text | Vendor name |
| Amount | number | Budgeted amount |
| Actual Amount | number | Actual spend |
| Committed Date | date | Commitment date |

### Risks

| Property | Type | Description |
|----------|------|-------------|
| Project | relation | Parent project |
| Title | title | Risk title |
| Severity | select | Critical/High/Medium/Low |
| Probability | select | High/Medium/Low |
| Status | select | Open/Mitigating/Closed |

## Sync Logic

1. **Read Watermark**: Get last sync timestamp per database
2. **Query Notion**: Fetch pages modified since watermark
3. **Write Bronze**: Store raw JSON payloads
4. **Transform Silver**: Map columns to normalized schema
5. **Update Watermark**: Record new sync timestamp

### Incremental Sync

By default, the service only syncs pages modified since the last run:

```sql
-- Watermark query
SELECT last_edited_time
FROM bronze.sync_watermarks
WHERE database_id = '<db_id>'
```

### Full Sync

Use `--full-sync` to ignore watermarks and sync all pages.

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black notion_sync tests
ruff check --fix notion_sync tests

# Type check
mypy notion_sync
```

## Deployment

### As a Databricks Job

```yaml
# databricks.yml
resources:
  jobs:
    notion_sync_bronze:
      name: "Notion Sync Bronze"
      tasks:
        - task_key: sync
          python_wheel_task:
            package_name: notion_sync
            entry_point: sync
      schedule:
        quartz_cron_expression: "0 */15 * * * ?"
```

### As a Container

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install .

CMD ["notion-sync", "sync"]
```

## License

AGPL-3.0-only
