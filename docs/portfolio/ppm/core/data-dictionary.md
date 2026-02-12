# Notion x Finance PPM Data Dictionary

## Overview

This document describes the schema for all tables in the PPM data lakehouse.

## Bronze Layer

Raw data from source systems with minimal transformations.

### ppm_bronze.notion_programs

| Column | Type | Description |
|--------|------|-------------|
| id | STRING | Notion page ID (primary key) |
| properties | STRING | Raw JSON of page properties |
| created_time | TIMESTAMP | Page creation time |
| last_edited_time | TIMESTAMP | Last modification time |
| _extracted_at | TIMESTAMP | When record was extracted |
| _source | STRING | Source identifier ("notion") |
| _raw_json | STRING | Complete raw page JSON |

### ppm_bronze.notion_projects

| Column | Type | Description |
|--------|------|-------------|
| id | STRING | Notion page ID (primary key) |
| properties | STRING | Raw JSON of page properties |
| created_time | TIMESTAMP | Page creation time |
| last_edited_time | TIMESTAMP | Last modification time |
| _extracted_at | TIMESTAMP | When record was extracted |
| _source | STRING | Source identifier ("notion") |
| _raw_json | STRING | Complete raw page JSON |

### ppm_bronze.notion_budget_lines

| Column | Type | Description |
|--------|------|-------------|
| id | STRING | Notion page ID (primary key) |
| properties | STRING | Raw JSON of page properties |
| created_time | TIMESTAMP | Page creation time |
| last_edited_time | TIMESTAMP | Last modification time |
| _extracted_at | TIMESTAMP | When record was extracted |
| _source | STRING | Source identifier ("notion") |
| _raw_json | STRING | Complete raw page JSON |

### ppm_bronze.notion_risks

| Column | Type | Description |
|--------|------|-------------|
| id | STRING | Notion page ID (primary key) |
| properties | STRING | Raw JSON of page properties |
| created_time | TIMESTAMP | Page creation time |
| last_edited_time | TIMESTAMP | Last modification time |
| _extracted_at | TIMESTAMP | When record was extracted |
| _source | STRING | Source identifier ("notion") |
| _raw_json | STRING | Complete raw page JSON |

### ppm_bronze.notion_actions

| Column | Type | Description |
|--------|------|-------------|
| id | STRING | Notion page ID (primary key) |
| properties | STRING | Raw JSON of page properties |
| created_time | TIMESTAMP | Page creation time |
| last_edited_time | TIMESTAMP | Last modification time |
| _extracted_at | TIMESTAMP | When record was extracted |
| _source | STRING | Source identifier ("notion") |
| _raw_json | STRING | Complete raw page JSON |

### ppm_bronze.azure_rg_resources

| Column | Type | Description |
|--------|------|-------------|
| id | STRING | Azure resource ID |
| name | STRING | Resource name |
| type | STRING | Resource type |
| location | STRING | Azure region |
| tags | STRING | Resource tags (JSON) |
| properties | STRING | Resource properties (JSON) |
| _extracted_at | TIMESTAMP | When record was extracted |
| _source | STRING | Source identifier ("azure_rg") |

## Silver Layer

Cleaned, typed, and deduplicated data.

### ppm_silver.programs

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | STRING | No | Unique program ID (from Notion) |
| name | STRING | No | Program name |
| status | STRING | No | Status: Planning, Active, On Hold, Completed |
| owner | STRING | Yes | Program owner name |
| start_date | DATE | Yes | Planned start date |
| end_date | DATE | Yes | Planned end date |
| description | STRING | Yes | Program description |
| created_at | TIMESTAMP | No | Record creation time |
| updated_at | TIMESTAMP | No | Last update time |

**Indexes**: Primary key on `id`

### ppm_silver.projects

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | STRING | No | Unique project ID |
| program_id | STRING | Yes | Parent program ID (FK) |
| name | STRING | No | Project name |
| status | STRING | No | Status: Not Started, In Progress, Completed |
| priority | STRING | Yes | Priority: Low, Medium, High |
| owner | STRING | Yes | Project owner name |
| start_date | DATE | Yes | Planned start date |
| end_date | DATE | Yes | Planned end date |
| progress_pct | DOUBLE | Yes | Completion percentage (0-100) |
| created_at | TIMESTAMP | No | Record creation time |
| updated_at | TIMESTAMP | No | Last update time |

**Indexes**: Primary key on `id`, foreign key on `program_id`

### ppm_silver.budget_lines

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | STRING | No | Unique budget line ID |
| project_id | STRING | Yes | Parent project ID (FK) |
| category | STRING | No | Budget category |
| amount | DOUBLE | No | Budgeted amount |
| currency | STRING | No | Currency code (default: USD) |
| fiscal_year | INT | Yes | Fiscal year |
| fiscal_quarter | STRING | Yes | Fiscal quarter (Q1-Q4) |
| actual_amount | DOUBLE | Yes | Actual spent amount |
| created_at | TIMESTAMP | No | Record creation time |
| updated_at | TIMESTAMP | No | Last update time |

**Indexes**: Primary key on `id`, foreign key on `project_id`

### ppm_silver.risks

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | STRING | No | Unique risk ID |
| project_id | STRING | Yes | Associated project ID (FK) |
| title | STRING | No | Risk title |
| description | STRING | Yes | Risk description |
| severity | STRING | No | Severity: Low, Medium, High, Critical |
| likelihood | STRING | Yes | Likelihood: Rare, Unlikely, Possible, Likely |
| impact | STRING | Yes | Impact level |
| status | STRING | No | Status: Open, Mitigated, Closed |
| owner | STRING | Yes | Risk owner |
| mitigation_plan | STRING | Yes | Mitigation strategy |
| created_at | TIMESTAMP | No | Record creation time |
| updated_at | TIMESTAMP | No | Last update time |

**Indexes**: Primary key on `id`, foreign key on `project_id`

### ppm_silver.actions

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | STRING | No | Unique action ID |
| risk_id | STRING | Yes | Parent risk ID (FK) |
| title | STRING | No | Action title |
| assignee | STRING | Yes | Assigned person |
| due_date | DATE | Yes | Due date |
| status | STRING | No | Status: Open, In Progress, Completed |
| notes | STRING | Yes | Additional notes |
| created_at | TIMESTAMP | No | Record creation time |
| updated_at | TIMESTAMP | No | Last update time |

**Indexes**: Primary key on `id`, foreign key on `risk_id`

## Gold Layer

Business-ready aggregations and metrics.

### ppm_gold.budget_vs_actual

| Column | Type | Description |
|--------|------|-------------|
| project_id | STRING | Project ID |
| project_name | STRING | Project name |
| program_id | STRING | Parent program ID |
| program_name | STRING | Parent program name |
| total_budget | DOUBLE | Sum of budgeted amounts |
| total_actual | DOUBLE | Sum of actual amounts |
| variance | DOUBLE | Budget - Actual |
| variance_pct | DOUBLE | Variance as percentage |
| fiscal_year | INT | Fiscal year |
| updated_at | TIMESTAMP | Last calculation time |

### ppm_gold.forecast

| Column | Type | Description |
|--------|------|-------------|
| project_id | STRING | Project ID |
| project_name | STRING | Project name |
| current_spend | DOUBLE | Spend to date |
| run_rate_monthly | DOUBLE | Average monthly spend |
| projected_total | DOUBLE | Projected total at completion |
| months_remaining | INT | Months until project end |
| projected_variance | DOUBLE | Projected budget variance |
| forecast_date | DATE | Forecast calculation date |

### ppm_gold.risk_summary

| Column | Type | Description |
|--------|------|-------------|
| program_id | STRING | Program ID |
| program_name | STRING | Program name |
| total_risks | INT | Total risk count |
| critical_risks | INT | Critical severity risks |
| high_risks | INT | High severity risks |
| open_risks | INT | Open status risks |
| mitigated_risks | INT | Mitigated risks |
| risk_score | DOUBLE | Aggregate risk score |
| updated_at | TIMESTAMP | Last calculation time |

### ppm_gold.projects_summary

| Column | Type | Description |
|--------|------|-------------|
| id | STRING | Project ID |
| name | STRING | Project name |
| status | STRING | Project status |
| program_name | STRING | Parent program name |
| owner | STRING | Project owner |
| budget_total | DOUBLE | Total budget |
| actual_total | DOUBLE | Total actual spend |
| risk_count | INT | Associated risk count |
| health_score | DOUBLE | Calculated health score (0-100) |
| days_remaining | INT | Days until end date |
| updated_at | TIMESTAMP | Last calculation time |

### ppm_gold.dq_issues

| Column | Type | Description |
|--------|------|-------------|
| issue_id | STRING | Unique issue ID |
| table_name | STRING | Affected table |
| column_name | STRING | Affected column |
| rule_name | STRING | DQ rule that failed |
| severity | STRING | Issue severity |
| record_count | INT | Number of affected records |
| sample_ids | STRING | Sample record IDs (JSON array) |
| description | STRING | Issue description |
| detected_at | TIMESTAMP | When issue was detected |
| resolved_at | TIMESTAMP | When issue was resolved (null if open) |

### ppm_gold.control_room_status

| Column | Type | Description |
|--------|------|-------------|
| metric_name | STRING | Metric identifier |
| metric_value | DOUBLE | Metric value |
| metric_unit | STRING | Unit of measurement |
| category | STRING | Metric category |
| checked_at | TIMESTAMP | When metric was calculated |

## Relationships

```
programs (1) ─────< (N) projects
                         │
                         │
projects (1) ─────< (N) budget_lines
                         │
projects (1) ─────< (N) risks
                              │
                              │
risks (1) ─────< (N) actions
```

## Data Quality Rules

| Rule ID | Table | Rule | Severity |
|---------|-------|------|----------|
| DQ001 | programs | id NOT NULL | Critical |
| DQ002 | programs | name NOT NULL | Critical |
| DQ003 | projects | program_id EXISTS in programs | High |
| DQ004 | budget_lines | amount >= 0 | High |
| DQ005 | risks | severity IN valid_values | Medium |
| DQ006 | actions | due_date >= created_at | Medium |
| DQ007 | all | updated_at > 7 days ago | Low |

## Update Frequency

| Layer | Table Pattern | Update Frequency |
|-------|---------------|------------------|
| Bronze | ppm_bronze.* | Every 15 minutes |
| Silver | ppm_silver.* | Hourly |
| Gold | ppm_gold.* | Hourly |
