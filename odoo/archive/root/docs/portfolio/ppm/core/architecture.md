# Notion x Finance PPM Architecture

## Overview

The Notion x Finance PPM system provides portfolio and project management (PPM) capabilities by synchronizing data from Notion databases through a Databricks lakehouse to a custom Control Room dashboard.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              NOTION WORKSPACE                               │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐ ┌───────┐ ┌─────────┐            │
│  │ Programs │ │ Projects │ │BudgetLines │ │ Risks │ │ Actions │            │
│  └────┬─────┘ └────┬─────┘ └─────┬──────┘ └───┬───┘ └────┬────┘            │
└───────┼────────────┼─────────────┼────────────┼──────────┼─────────────────┘
        │            │             │            │          │
        └────────────┴──────┬──────┴────────────┴──────────┘
                            │ Notion API
                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         NOTION SYNC SERVICE                                 │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────────┐         │
│  │  NotionClient   │→ │  PageTransformer │→ │  DatabricksWriter  │         │
│  │ (Incremental)   │  │  (Pydantic)      │  │  (Delta MERGE)     │         │
│  └─────────────────┘  └──────────────────┘  └────────────────────┘         │
└─────────────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATABRICKS LAKEHOUSE                                │
│                                                                             │
│  ┌─────────────────────────── BRONZE ───────────────────────────┐          │
│  │ notion_programs │ notion_projects │ notion_budget_lines │... │          │
│  │     (raw)       │     (raw)       │       (raw)          │   │          │
│  └───────────────────────────┬───────────────────────────────────┘          │
│                              ▼                                              │
│  ┌─────────────────────────── SILVER ───────────────────────────┐          │
│  │   programs   │   projects   │   budget_lines   │   risks     │          │
│  │  (cleaned)   │  (cleaned)   │    (cleaned)     │ (cleaned)   │          │
│  └───────────────────────────┬───────────────────────────────────┘          │
│                              ▼                                              │
│  ┌─────────────────────────── GOLD ─────────────────────────────┐          │
│  │ budget_vs_actual │ forecast │ risk_summary │ projects_summary │          │
│  │ dq_issues        │ job_status │ control_room_metrics         │          │
│  └───────────────────────────────────────────────────────────────┘          │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────┐        │
│  │                    DATABRICKS JOBS                              │        │
│  │  notion_sync (15m) │ transform (1h) │ marts (1h) │ dq (1h)     │        │
│  └────────────────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────────────────┘
                            │
                            │ Databricks SQL
                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CONTROL ROOM (Next.js)                             │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────┐       │
│  │                        API Routes                                │       │
│  │  /api/kpis │ /api/jobs │ /api/dq/issues │ /api/projects │ ...   │       │
│  └──────────────────────────────┬──────────────────────────────────┘       │
│                                 │                                           │
│  ┌──────────────────────────────┴──────────────────────────────────┐       │
│  │                        UI Pages                                  │       │
│  │  Overview │ Pipelines │ Data Quality │ Advisor │ Projects       │       │
│  └─────────────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Notion Workspace (Source of Truth)

Five interconnected Notion databases:

| Database | Purpose | Key Properties |
|----------|---------|----------------|
| Programs | Top-level initiatives | Name, Status, Owner, Start/End |
| Projects | Deliverables under programs | Name, Status, Program (relation) |
| BudgetLines | Financial allocations | Amount, Category, Project (relation) |
| Risks | Risk register | Severity, Likelihood, Impact, Mitigation |
| Actions | Action items from risks | Assignee, Due Date, Status |

### 2. Notion Sync Service

Python service that:
- Polls Notion API for changes (watermark-based incremental sync)
- Validates data with Pydantic models
- Writes to Delta tables using MERGE for upserts
- Adds metadata columns: `_extracted_at`, `_source`, `_raw_json`

Key classes:
- `NotionClient`: API wrapper with retry logic
- `PageTransformer`: Converts Notion pages to Pydantic models
- `DatabricksWriter`: Delta table writer with schema evolution

### 3. Databricks Lakehouse

Three-tier medallion architecture:

**Bronze Layer**
- Raw data from source systems
- Minimal transformations (metadata only)
- Schema evolution enabled

**Silver Layer**
- Cleaned, typed, deduplicated data
- Null handling and type casting
- Business key validation

**Gold Layer**
- Aggregated business metrics
- Pre-computed KPIs
- Data quality scores

### 4. Control Room Dashboard

Next.js 14 application with:
- React Server Components for data fetching
- Tailwind CSS with Azure-inspired dark theme
- Zod schema validation for API responses
- Recharts for data visualization

Pages:
- **Overview**: KPI cards, health summary, activity feed
- **Pipelines**: Job status, run history, logs
- **Data Quality**: Issue tracking, freshness metrics
- **Advisor**: Azure Advisor recommendations (reference)
- **Projects**: Portfolio view with search/filter

## Data Flow

### Sync Schedule

| Job | Schedule | Duration | Description |
|-----|----------|----------|-------------|
| notion_sync_bronze | Every 15m | ~2m | Incremental Notion sync |
| azure_rg_ingest | Every 6h | ~5m | Azure Resource Graph sync |
| notion_transform_silver | Every hour | ~3m | Bronze to silver ETL |
| ppm_marts_gold | Every hour | ~5m | Silver to gold aggregations |
| dq_checks | Every hour | ~2m | Data quality validation |
| control_room_refresh | Every 15m | ~1m | Dashboard cache refresh |

### Incremental Sync Strategy

```python
# Watermark-based sync
watermark = get_last_watermark(database_id)
pages = notion.query(
    database_id,
    filter={"last_edited_time": {"after": watermark}}
)
for page in pages:
    upsert_to_bronze(page)
save_watermark(database_id, max(pages.last_edited_time))
```

## Security

### Authentication
- Notion: Integration token with scoped permissions
- Databricks: Personal access token or service principal
- Control Room: Environment variables (no secrets in code)

### Data Protection
- HTTPS only for all endpoints
- No PII in bronze layer (masked in silver)
- Blob storage with private access only
- Key Vault for secret management (Azure reference)

## Deployment

### Environments

| Environment | Purpose | Databricks | Control Room |
|-------------|---------|------------|--------------|
| dev | Development | Premium (dev catalog) | localhost:3000 |
| staging | Pre-production | Premium (staging catalog) | staging.ppm.internal |
| prod | Production | Premium (prod catalog) | ppm.internal |

### Deployment Workflow

1. **Databricks DAB**: `databricks bundle deploy -t {env}`
2. **Control Room**: Docker container via CI/CD
3. **Notion Sync**: Deployed as Databricks job

## Monitoring

### Metrics

| Metric | Source | Threshold |
|--------|--------|-----------|
| Sync latency | Job duration | < 5 min |
| Data freshness | `_extracted_at` | < 30 min |
| DQ score | `dq_checks` table | > 95% |
| API response time | Control Room | < 500ms |

### Alerting

- Job failures: Email notification
- DQ threshold breach: Slack webhook
- API errors: Application Insights (reference)

## Related Documentation

- [Runbook](./runbook.md) - Operational procedures
- [Data Dictionary](./data-dictionary.md) - Schema reference
- [Spec Bundle](../spec/notion-finance-ppm-control-room/) - Requirements
