# Notion x Finance PPM Control Room — Product Requirements Document

> **Version**: 1.0.0
> **Status**: Active
> **Last Updated**: 2025-12-21

---

## 1. Executive Summary

The Notion x Finance PPM Control Room is a comprehensive system for **Project Portfolio Management (PPM)** that combines:

1. **Notion** as the planning interface for Programs, Projects, and Financial tracking
2. **Databricks** as the data platform with medallion architecture (bronze/silver/gold)
3. **Control Room** web app for governance, pipeline health, and KPI visibility
4. **Azure Advisor/Resource Graph** integration for cost and optimization signals

**Target Users**: Finance teams, Project managers, Platform engineers, Leadership

---

## 2. Problem Statement

### Current State
- PPM data scattered across spreadsheets and disconnected systems
- No unified view of budget vs actual across portfolios
- Manual data collection for financial reporting
- Azure costs not linked to project/program ownership
- Pipeline failures discovered reactively

### Desired State
- Single source of truth in Notion for project intake
- Automated sync to Databricks for analytics
- Real-time Control Room for governance
- Azure costs linked to programs/projects
- Proactive DQ and pipeline monitoring

---

## 3. User Personas

### 3.1 Finance Controller
- Reviews budget vs actual by program
- Tracks CapEx/OpEx allocation
- Needs monthly/quarterly reports

### 3.2 Project Manager
- Updates project status in Notion
- Tracks project-level spend
- Monitors risk register

### 3.3 Platform Engineer
- Monitors pipeline health
- Investigates DQ issues
- Manages sync configurations

### 3.4 Leadership
- Views portfolio-level KPIs
- Reviews Azure cost allocation
- Approves budget variances

---

## 4. Functional Requirements

### 4.1 Notion Data Model

| ID | Requirement | Priority |
|----|-------------|----------|
| N-001 | Programs database with name, owner, dates, status | P1 |
| N-002 | Projects database with program relation, budget, dates | P1 |
| N-003 | BudgetLines database with project relation, category, amounts | P1 |
| N-004 | Risks database with project relation, severity, mitigation | P1 |
| N-005 | Actions database for Control Room tasks | P2 |

### 4.2 Notion Sync Service

| ID | Requirement | Priority |
|----|-------------|----------|
| NS-001 | Incremental sync using last_edited_time watermark | P1 |
| NS-002 | Idempotent upserts keyed by page_id + database_id | P1 |
| NS-003 | Store raw payload in bronze layer | P1 |
| NS-004 | Track sync watermark per database | P1 |
| NS-005 | Support soft-delete via archived flag | P2 |
| NS-006 | Retry logic with exponential backoff | P2 |

### 4.3 Databricks Tables

#### Bronze Layer

| ID | Table | Description |
|----|-------|-------------|
| B-001 | bronze.notion_raw_pages | Raw Notion page payloads |
| B-002 | bronze.azure_rg_raw | Raw Azure Resource Graph results |
| B-003 | bronze.azure_advisor_raw | Raw Advisor recommendations |

#### Silver Layer

| ID | Table | Description |
|----|-------|-------------|
| S-001 | silver.notion_programs | Normalized programs |
| S-002 | silver.notion_projects | Normalized projects |
| S-003 | silver.notion_budget_lines | Normalized budget lines |
| S-004 | silver.notion_risks | Normalized risks |
| S-005 | silver.azure_advisor_recommendations | Normalized advisor recs |
| S-006 | silver.azure_cost_signals | Cost data by resource |

#### Gold Layer

| ID | Table | Description |
|----|-------|-------------|
| G-001 | gold.ppm_budget_vs_actual | Budget vs actual by period |
| G-002 | gold.ppm_forecast | Run-rate forecast |
| G-003 | gold.ppm_risk_summary | Risk rollups |
| G-004 | gold.azure_advisor_summary | Advisor recs by category |
| G-005 | gold.control_room_status | Pipeline health metrics |
| G-006 | gold.dq_issues | Data quality issues |

### 4.4 Databricks Jobs (DAB)

| ID | Job | Schedule | Description |
|----|-----|----------|-------------|
| J-001 | notion_sync_bronze | Every 15 min | Pull Notion → bronze |
| J-002 | notion_transform_silver | Hourly | Normalize → silver |
| J-003 | ppm_marts_gold | Hourly | Compute KPIs → gold |
| J-004 | azure_rg_ingest_bronze | Every 6 hours | Resource Graph → bronze |
| J-005 | azure_advisor_transform | Every 6 hours | Advisor → silver/gold |
| J-006 | control_room_status_refresh | Every 15 min | Job metadata → gold |
| J-007 | dq_checks | Hourly | Data quality checks |

### 4.5 Control Room API

| ID | Endpoint | Method | Description |
|----|----------|--------|-------------|
| A-001 | /api/health | GET | Health check |
| A-002 | /api/kpis | GET | KPI summary (budget, variance, etc.) |
| A-003 | /api/jobs | GET | Databricks jobs list |
| A-004 | /api/job-runs | GET | Job run history |
| A-005 | /api/dq/issues | GET | Data quality issues |
| A-006 | /api/advisor/recommendations | GET | Advisor recommendations |
| A-007 | /api/projects | GET | Projects with filters |
| A-008 | /api/notion/actions | POST | Create Notion action |

### 4.6 Control Room UI Pages

| ID | Page | Description |
|----|------|-------------|
| UI-001 | /overview | KPI cards, health summary, freshness |
| UI-002 | /pipelines | Jobs list, run status, duration |
| UI-003 | /data-quality | DQ issues, drift, null rates |
| UI-004 | /advisor | Advisor recs by category, savings |
| UI-005 | /projects | Project table with drilldown |

---

## 5. Non-Functional Requirements

### 5.1 Performance

| ID | Requirement | Target |
|----|-------------|--------|
| PF-001 | Notion sync latency | < 5 min per DB |
| PF-002 | API response time | < 500ms |
| PF-003 | UI initial load | < 3s |
| PF-004 | Gold table refresh | < 30 min |

### 5.2 Reliability

| ID | Requirement | Target |
|----|-------------|--------|
| RL-001 | Pipeline success rate | > 98% |
| RL-002 | Control Room uptime | > 99% |
| RL-003 | Data freshness SLA | < 1 hour |

### 5.3 Security

| ID | Requirement | Description |
|----|-------------|-------------|
| SC-001 | API authentication | API key required |
| SC-002 | Secrets management | Env vars, never hardcoded |
| SC-003 | Network isolation | VNet for Databricks |
| SC-004 | Audit logging | All API calls logged |

---

## 6. Data Model Details

### 6.1 Notion Database Schema

```yaml
Programs:
  - name: text
  - owner: person
  - start_date: date
  - end_date: date
  - status: select [Active, On Hold, Completed, Cancelled]
  - description: rich_text

Projects:
  - name: text
  - program: relation[Programs]
  - budget_total: number
  - currency: select [USD, EUR, PHP]
  - start_date: date
  - end_date: date
  - status: select [Planning, In Progress, Completed, On Hold]
  - priority: select [High, Medium, Low]
  - owner: person

BudgetLines:
  - project: relation[Projects]
  - category: select [CapEx, OpEx]
  - vendor: text
  - description: text
  - amount: number
  - committed_date: date
  - invoice_date: date
  - paid_date: date
  - actual_amount: number
  - notes: rich_text

Risks:
  - project: relation[Projects]
  - title: text
  - severity: select [Critical, High, Medium, Low]
  - probability: select [High, Medium, Low]
  - status: select [Open, Mitigating, Closed, Accepted]
  - mitigation: rich_text
  - owner: person

Actions:
  - project: relation[Projects]
  - title: text
  - assignee: person
  - due_date: date
  - status: select [Open, In Progress, Done]
  - source: select [Advisor, DataQuality, Manual]
  - source_ref: url
```

### 6.2 Delta Table Schema

```sql
-- Bronze: notion_raw_pages
CREATE TABLE bronze.notion_raw_pages (
  page_id STRING,
  database_id STRING,
  database_name STRING,
  payload STRING,  -- JSON
  last_edited_time TIMESTAMP,
  synced_at TIMESTAMP,
  is_archived BOOLEAN
)
USING DELTA
PARTITIONED BY (database_name);

-- Silver: notion_projects
CREATE TABLE silver.notion_projects (
  id STRING,
  page_id STRING,
  program_id STRING,
  name STRING,
  budget_total DECIMAL(18,2),
  currency STRING,
  start_date DATE,
  end_date DATE,
  status STRING,
  priority STRING,
  owner STRING,
  last_edited_time TIMESTAMP,
  synced_at TIMESTAMP,
  is_archived BOOLEAN
)
USING DELTA;

-- Gold: ppm_budget_vs_actual
CREATE TABLE gold.ppm_budget_vs_actual (
  period_month DATE,
  program_id STRING,
  program_name STRING,
  project_id STRING,
  project_name STRING,
  category STRING,
  budget_amount DECIMAL(18,2),
  actual_amount DECIMAL(18,2),
  variance_amount DECIMAL(18,2),
  variance_pct DECIMAL(5,2),
  currency STRING
)
USING DELTA
PARTITIONED BY (period_month);
```

---

## 7. Integration Contracts

### 7.1 Notion Sync Mapping (YAML)

```yaml
sync_config:
  databases:
    programs:
      database_id: "${NOTION_PROGRAMS_DB_ID}"
      bronze_table: "bronze.notion_raw_pages"
      silver_table: "silver.notion_programs"
      column_mapping:
        name: "Name.title[0].plain_text"
        owner: "Owner.people[0].name"
        start_date: "Start Date.date.start"
        end_date: "End Date.date.end"
        status: "Status.select.name"

    projects:
      database_id: "${NOTION_PROJECTS_DB_ID}"
      bronze_table: "bronze.notion_raw_pages"
      silver_table: "silver.notion_projects"
      column_mapping:
        name: "Name.title[0].plain_text"
        program_id: "Program.relation[0].id"
        budget_total: "Budget Total.number"
        currency: "Currency.select.name"
        status: "Status.select.name"
        priority: "Priority.select.name"
```

### 7.2 API Response DTOs

```typescript
// GET /api/kpis
interface KPIsResponse {
  totalBudget: number;
  totalActual: number;
  varianceAmount: number;
  variancePct: number;
  burnRate: number;
  atRiskProjects: number;
  lastSyncTime: string;
  dataFreshnessMinutes: number;
}

// GET /api/jobs
interface Job {
  jobId: string;
  name: string;
  lastRunStatus: 'SUCCESS' | 'FAILED' | 'RUNNING' | 'PENDING';
  lastRunTime: string;
  lastRunDurationSeconds: number;
  nextRunTime: string;
}

// GET /api/dq/issues
interface DQIssue {
  id: string;
  table: string;
  column: string;
  issueType: 'null_rate' | 'schema_drift' | 'row_count_drop' | 'referential';
  severity: 'critical' | 'warning' | 'info';
  description: string;
  detectedAt: string;
  resolved: boolean;
}
```

---

## 8. UI Wireframes

### 8.1 Overview Page

```
┌─────────────────────────────────────────────────────────────────┐
│  NOTION x FINANCE PPM CONTROL ROOM                    [Refresh]│
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │ $1.2M    │ │ $890K    │ │ -$310K   │ │ 3        │           │
│  │ Budget   │ │ Actual   │ │ Variance │ │ At Risk  │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
│                                                                 │
│  ┌─ PIPELINE HEALTH ─────────────────────────────────────────┐ │
│  │ Last Sync: 5 min ago | Failing Jobs: 0 | DQ Issues: 2     │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─ RECENT ACTIVITY ──────────────────────────────────────────┐│
│  │ • notion_sync_bronze completed (2 min ago)                 ││
│  │ • ppm_marts_gold completed (15 min ago)                    ││
│  │ • DQ Warning: null rate > 5% on budget_lines.vendor        ││
│  └────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 Pipelines Page

```
┌─────────────────────────────────────────────────────────────────┐
│  PIPELINES                                          [Filter ▼] │
├─────────────────────────────────────────────────────────────────┤
│  Job Name              │ Status  │ Last Run   │ Duration │ Next│
│  ─────────────────────────────────────────────────────────────  │
│  notion_sync_bronze    │ ✓ OK    │ 5 min ago  │ 45s      │ 10m │
│  notion_transform_silver│ ✓ OK   │ 1 hr ago   │ 2m 15s   │ 1hr │
│  ppm_marts_gold        │ ✓ OK    │ 1 hr ago   │ 5m 30s   │ 1hr │
│  azure_rg_ingest       │ ✓ OK    │ 4 hr ago   │ 1m 45s   │ 2hr │
│  dq_checks             │ ⚠ WARN  │ 1 hr ago   │ 30s      │ 1hr │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. Acceptance Criteria

### 9.1 MVP (Phase 1)

- [x] Notion database schema defined
- [ ] Notion sync service pulling to bronze
- [ ] Silver transformation for projects/budgets
- [ ] Gold mart for budget vs actual
- [ ] Control Room overview page
- [ ] API endpoints for KPIs and jobs

### 9.2 V1.0 (Phase 2)

- [ ] All Notion databases syncing
- [ ] Azure Advisor integration
- [ ] Data quality checks
- [ ] Action push to Notion
- [ ] Full Control Room UI

---

## 10. Dependencies

| Dependency | Purpose | Status |
|------------|---------|--------|
| Notion API | Data source | Available |
| Databricks | Compute + storage | Required |
| Azure subscription | Advisor/RG | Required |
| Next.js | Control Room UI | Included |
| Python 3.11+ | Sync service | Required |

---

## 11. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Notion API rate limits | Slow sync | Batch requests, backoff |
| Databricks costs | Budget overrun | Delta optimization |
| Schema changes in Notion | Sync breaks | Schema versioning |
| Azure permissions | No data | Clear RBAC docs |

---

## Appendix: Related Documents

- `constitution.md` — Governing Principles
- `plan.md` — Implementation Plan
- `tasks.md` — Task Checklist
