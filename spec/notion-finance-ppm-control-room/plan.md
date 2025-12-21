# Notion x Finance PPM Control Room — Implementation Plan

> **Version**: 1.0.0
> **Status**: Active
> **Last Updated**: 2025-12-21

---

## 1. Implementation Overview

This plan delivers a complete Notion x Finance PPM system with:
- Notion sync service (Python)
- Databricks lakehouse (DAB bundle)
- Control Room web app (Next.js)
- Azure infrastructure (Bicep)
- CI/CD pipelines (GitHub Actions)
- Verification scripts

---

## 2. Phase 1: Foundation

### 2.1 Repository Structure

Create the following directory structure:

```
/
├── apps/
│   └── control-room/              # Next.js Control Room app
│       ├── src/
│       │   ├── app/               # App Router pages
│       │   ├── components/        # React components
│       │   ├── lib/               # Utilities, API clients
│       │   └── types/             # TypeScript types
│       ├── package.json
│       ├── next.config.js
│       ├── tailwind.config.js
│       └── .env.example
│
├── services/
│   └── notion-sync/               # Python sync service
│       ├── notion_sync/
│       │   ├── __init__.py
│       │   ├── client.py          # Notion API client
│       │   ├── sync.py            # Sync logic
│       │   ├── transform.py       # Bronze → Silver
│       │   ├── models.py          # Pydantic models
│       │   └── config.py          # Configuration
│       ├── tests/
│       ├── pyproject.toml
│       ├── .env.example
│       └── README.md
│
├── infra/
│   ├── databricks/                # DAB bundle
│   │   ├── databricks.yml
│   │   ├── resources/
│   │   │   ├── jobs.yml
│   │   │   └── pipelines.yml
│   │   └── notebooks/
│   │       ├── bronze/
│   │       ├── silver/
│   │       └── gold/
│   │
│   └── azure/                     # Bicep templates
│       ├── main.bicep
│       ├── modules/
│       └── parameters/
│
├── .continue/
│   └── rules/                     # Continue rules
│       ├── architecture.md
│       ├── coding-standards.md
│       ├── data-contracts.md
│       └── security.md
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── deploy-control-room.yml
│       └── deploy-databricks.yml
│
├── scripts/
│   ├── dev_up.sh
│   ├── run_notion_sync.sh
│   ├── dab_deploy.sh
│   └── health_check.sh
│
└── docs/
    ├── architecture.md
    ├── runbooks.md
    └── data-dictionary.md
```

### 2.2 Core Dependencies

**Control Room (Next.js)**:
- next@14
- react@18
- tailwindcss@3
- zod (validation)
- @tanstack/react-query (data fetching)
- recharts (charts)

**Notion Sync (Python)**:
- notion-client
- databricks-sdk
- pydantic
- python-dotenv
- structlog

**Infrastructure**:
- Databricks CLI
- Azure CLI
- Bicep

---

## 3. Phase 2: Notion Sync Service

### 3.1 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    NOTION SYNC SERVICE                   │
│                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────┐ │
│  │ Notion API   │───→│ Sync Engine  │───→│ Databricks│ │
│  │ Client       │    │              │    │ Writer    │ │
│  └──────────────┘    └──────────────┘    └───────────┘ │
│         ▲                   │                   │       │
│         │                   ▼                   ▼       │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────┐ │
│  │ Watermark    │    │ Transform    │    │ Delta     │ │
│  │ Store        │    │ Mapper       │    │ Tables    │ │
│  └──────────────┘    └──────────────┘    └───────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Sync Flow

1. **Initialize**: Load config, connect to Notion + Databricks
2. **Get Watermark**: Read last sync time per database
3. **Query Notion**: Fetch pages modified since watermark
4. **Write Bronze**: Upsert raw payloads to bronze table
5. **Update Watermark**: Store new watermark
6. **Transform**: Extract columns to silver tables
7. **Log**: Record sync metrics

### 3.3 Mapping Configuration

```yaml
# config/notion_mapping.yaml
databases:
  programs:
    database_id: "${NOTION_PROGRAMS_DB_ID}"
    bronze_partition: "programs"
    silver_table: "silver.notion_programs"
    columns:
      - source: "Name"
        target: "name"
        type: "title"
      - source: "Owner"
        target: "owner"
        type: "person"
      - source: "Status"
        target: "status"
        type: "select"
```

---

## 4. Phase 3: Databricks Lakehouse

### 4.1 DAB Bundle Structure

```yaml
# databricks.yml
bundle:
  name: notion-finance-ppm

variables:
  catalog: ${var.catalog}
  schema_bronze: bronze
  schema_silver: silver
  schema_gold: gold

include:
  - resources/*.yml

targets:
  dev:
    mode: development
    default: true
    variables:
      catalog: dev_ppm
  prod:
    mode: production
    variables:
      catalog: ppm
```

### 4.2 Job Definitions

```yaml
# resources/jobs.yml
resources:
  jobs:
    notion_sync_bronze:
      name: "Notion Sync Bronze"
      tasks:
        - task_key: sync
          python_wheel_task:
            package_name: notion_sync
            entry_point: sync_bronze
          libraries:
            - pypi:
                package: notion-client
      schedule:
        quartz_cron_expression: "0 */15 * * * ?"
        timezone_id: "UTC"

    notion_transform_silver:
      name: "Notion Transform Silver"
      tasks:
        - task_key: transform
          notebook_task:
            notebook_path: ../notebooks/silver/transform_notion.py
      schedule:
        quartz_cron_expression: "0 0 * * * ?"
        timezone_id: "UTC"

    ppm_marts_gold:
      name: "PPM Marts Gold"
      tasks:
        - task_key: budget_vs_actual
          notebook_task:
            notebook_path: ../notebooks/gold/budget_vs_actual.py
        - task_key: forecast
          notebook_task:
            notebook_path: ../notebooks/gold/forecast.py
          depends_on:
            - task_key: budget_vs_actual
      schedule:
        quartz_cron_expression: "0 30 * * * ?"
        timezone_id: "UTC"
```

### 4.3 Notebook Templates

**Bronze Ingestion** (`notebooks/bronze/ingest_notion.py`):
- Query Notion API with pagination
- Handle rate limits with backoff
- Write to bronze table with merge

**Silver Transform** (`notebooks/silver/transform_notion.py`):
- Read bronze, extract columns
- Apply type conversions
- Merge to silver tables

**Gold Marts** (`notebooks/gold/budget_vs_actual.py`):
- Join projects + budget lines
- Aggregate by period
- Calculate variance metrics

---

## 5. Phase 4: Control Room Application

### 5.1 Page Structure

```
/                          → Redirect to /overview
/overview                  → KPI cards + health summary
/pipelines                 → Jobs list + run history
/pipelines/[jobId]         → Job detail + runs
/data-quality              → DQ issues + metrics
/advisor                   → Azure Advisor summary
/projects                  → Projects table
/projects/[projectId]      → Project detail + budget lines
```

### 5.2 API Routes

```
/api/health               → GET health check
/api/kpis                 → GET KPIs (budget, variance, etc.)
/api/jobs                 → GET Databricks jobs
/api/job-runs             → GET job run history
/api/dq/issues            → GET data quality issues
/api/advisor/recommendations → GET Advisor recs
/api/projects             → GET projects with filters
/api/projects/[id]        → GET project detail
/api/notion/actions       → POST create Notion action
```

### 5.3 Component Library

```
components/
├── layout/
│   ├── Sidebar.tsx
│   ├── Header.tsx
│   └── PageContainer.tsx
├── dashboard/
│   ├── KPICard.tsx
│   ├── HealthBadge.tsx
│   └── ActivityFeed.tsx
├── tables/
│   ├── DataTable.tsx
│   ├── JobsTable.tsx
│   └── ProjectsTable.tsx
├── charts/
│   ├── BudgetChart.tsx
│   ├── TrendLine.tsx
│   └── PieChart.tsx
└── common/
    ├── Button.tsx
    ├── Badge.tsx
    └── Card.tsx
```

---

## 6. Phase 5: Azure Infrastructure

### 6.1 Bicep Modules

```
infra/azure/
├── main.bicep              # Main deployment
├── modules/
│   ├── databricks.bicep    # Databricks workspace
│   ├── keyvault.bicep      # Key Vault for secrets
│   ├── storage.bicep       # Storage account
│   └── appservice.bicep    # Control Room hosting
└── parameters/
    ├── dev.parameters.json
    └── prod.parameters.json
```

### 6.2 Resource Graph Query

```kusto
// Azure Advisor recommendations
advisorresources
| where type == 'microsoft.advisor/recommendations'
| where properties.category in ('Cost', 'Security', 'Reliability', 'OperationalExcellence')
| project
    id,
    category = properties.category,
    impact = properties.impact,
    impactedField = properties.impactedField,
    impactedValue = properties.impactedValue,
    shortDescription = properties.shortDescription.problem,
    extendedProperties = properties.extendedProperties
```

---

## 7. Phase 6: CI/CD Pipelines

### 7.1 GitHub Actions

**ci.yml**:
- Lint (Python + TypeScript)
- Type check
- Unit tests
- Build verification

**deploy-control-room.yml**:
- Build Next.js app
- Deploy to Azure App Service
- Run smoke tests

**deploy-databricks.yml**:
- Validate DAB bundle
- Deploy to Databricks
- Run integration tests

### 7.2 Deployment Flow

```
push to main
    │
    ├──→ ci.yml (lint, test, build)
    │       │
    │       ├──→ pass ──→ deploy-control-room.yml
    │       │              └──→ Azure App Service
    │       │
    │       └──→ pass ──→ deploy-databricks.yml
    │                      └──→ Databricks workspace
    │
    └──→ fail ──→ notify
```

---

## 8. Phase 7: Continue Rules

### 8.1 Rule Files

**architecture.md**:
- Medallion architecture enforcement
- Service boundaries
- API contract requirements

**coding-standards.md**:
- Python style (Black, isort)
- TypeScript style (Prettier, ESLint)
- Naming conventions

**data-contracts.md**:
- Table naming: `{layer}.{source}_{entity}`
- Column types consistency
- Partition strategy

**security.md**:
- No secrets in code
- Environment variable usage
- Authentication requirements

---

## 9. Phase 8: Verification

### 9.1 Scripts

**dev_up.sh**:
```bash
# Start local development
cd apps/control-room && npm run dev &
cd services/notion-sync && python -m notion_sync.main --dry-run
```

**health_check.sh**:
```bash
# Verify system health
curl -f $CONTROL_ROOM_URL/api/health
databricks jobs list --output json | jq '.jobs[] | select(.state.life_cycle_state == "RUNNING")'
```

### 9.2 Test Strategy

| Layer | Tool | Coverage Target |
|-------|------|-----------------|
| Python unit | pytest | 80% |
| TypeScript unit | jest | 80% |
| API integration | pytest + httpx | Key endpoints |
| E2E | Playwright | Critical paths |
| Data quality | Great Expectations | 100% tables |

---

## 10. Deployment Runbook

### 10.1 Prerequisites

1. Azure subscription with Databricks workspace
2. Notion integration token
3. GitHub repository with secrets configured
4. Azure CLI + Databricks CLI installed

### 10.2 Steps

```bash
# 1. Clone and configure
git clone <repo>
cp .env.example .env
# Edit .env with real values

# 2. Deploy infrastructure
cd infra/azure
az deployment group create -g $RG -f main.bicep -p @parameters/prod.parameters.json

# 3. Deploy Databricks bundle
cd infra/databricks
databricks bundle deploy -t prod

# 4. Deploy Control Room
cd apps/control-room
npm run build
az webapp deploy --name $APP_NAME --src-path .next

# 5. Verify
./scripts/health_check.sh
```

---

## Appendix: Environment Variables

```bash
# Notion
NOTION_TOKEN=secret_xxx
NOTION_PROGRAMS_DB_ID=xxx
NOTION_PROJECTS_DB_ID=xxx
NOTION_BUDGET_LINES_DB_ID=xxx
NOTION_RISKS_DB_ID=xxx
NOTION_ACTIONS_DB_ID=xxx

# Databricks
DATABRICKS_HOST=https://xxx.azuredatabricks.net
DATABRICKS_TOKEN=dapi_xxx
DATABRICKS_CATALOG=ppm

# Azure
AZURE_SUBSCRIPTION_ID=xxx
AZURE_RESOURCE_GROUP=xxx

# Control Room
CONTROL_ROOM_API_KEY=xxx
CONTROL_ROOM_URL=https://xxx.azurewebsites.net
```
