# PRD — ADLS ETL + Reverse ETL

> Product requirements for the canonical data flow architecture between
> Supabase (SSOT), Odoo (SoR), and Azure Data Lake Storage (ADLS Gen2).

---

## 1. Problem Statement

The platform currently has:

- **Supabase** as SSOT for control-plane data (208 tables, 59 functions,
  pgvector, Auth, Realtime, Edge Functions)
- **Odoo** as SoR for ERP operations (accounting, projects, BIR compliance,
  HR, finance PPM)
- No canonical analytical/lake storage layer
- No structured ETL pipeline from either system to a shared analytical surface
- No governed reverse ETL path for writing analytical outputs back to
  operational systems

This creates fragmented analytics, duplicate exports, and ungoverned
data movement between systems.

## 2. Objective

Build a canonical ETL + reverse ETL architecture where:

1. Supabase and Odoo data lands in ADLS (bronze → silver → gold)
2. Analytical, ML, and BI workloads consume from ADLS gold layer
3. Approved analytical outputs flow back to operational systems via
   bounded, typed reverse ETL
4. System authority boundaries are preserved at every stage

## 3. Systems

| System | Role | Key Data |
|--------|------|----------|
| Supabase (`spdtwktxdalcfigzeqrz`) | SSOT — control plane | Users, platform events, workflow state, app metadata, vector embeddings, Edge Function state |
| Odoo CE 19 (`ipai-odoo-dev-web`) | SoR — ERP operations | Journal entries, invoices, projects, tasks, BIR tax filings, employees, vendors, analytic accounts |
| ADLS Gen2 | Analytical lake | Replicated bronze/silver/gold datasets, ML features, BI marts, reverse ETL staging |
| Azure AI Foundry | ML/AI compute | Model training, scoring, embedding generation |
| Tableau Cloud | BI presentation | Dashboards consuming ADLS gold layer |

## 4. Data Flow Topology

```
Supabase (SSOT)                    Odoo (SoR)
    │                                  │
    │ ETL (CDC or batch)               │ ETL (Extract API or DB replica)
    ▼                                  ▼
┌──────────────────────────────────────────────┐
│              ADLS Gen2                        │
│                                              │
│  raw/bronze    ← append-only landing         │
│  standardized/silver  ← normalized, typed    │
│  curated/gold  ← business-ready marts        │
│  reverse_etl_exports  ← approved writebacks  │
│  rejected/quarantine  ← failed records       │
│  audit/evidence  ← run logs, lineage         │
│                                              │
│         ┌──────────┐                         │
│         │ Compute  │ (Databricks optional)   │
│         │ Azure AI │ (scoring, embeddings)   │
│         └──────────┘                         │
└──────────────────────────────────────────────┘
    │                    │                │
    │ BI consumption     │ ML outputs     │ Reverse ETL
    ▼                    ▼                ▼
Tableau Cloud     Azure AI Foundry    Supabase / Odoo
                                      (bounded writebacks)
```

## 5. ETL Flows (Inbound to ADLS)

### 5.1 Supabase → ADLS Bronze

| Object Category | Examples | Extraction Method | Cadence |
|-----------------|----------|-------------------|---------|
| App events | `platform_events`, `task_queue` | Realtime CDC or batch export | Hourly or event-driven |
| User/identity | `auth.users`, profiles | Incremental batch | Daily |
| Platform metadata | Edge Function state, config | Full snapshot | Daily |
| Vector embeddings | pgvector tables | Incremental batch | Daily |
| Workflow state | n8n job records, sync state | Incremental batch | Hourly |

### 5.2 Odoo → ADLS Bronze

| Object Category | Examples | Extraction Method | Cadence |
|-----------------|----------|-------------------|---------|
| Journal entries | `account.move`, `account.move.line` | Extract API | Daily |
| Invoices | `account.move` (type=invoice) | Extract API | Daily |
| Projects/tasks | `project.project`, `project.task` | Extract API | Daily |
| BIR filings | `bir.tax.return`, schedules | Extract API | Weekly |
| Employees | `hr.employee`, `res.partner` | Extract API | Daily |
| Vendors | `res.partner` (supplier=True) | Extract API | Daily |
| Analytic accounts | `account.analytic.account` | Extract API | Daily |
| Expense documents | `hr.expense`, `hr.expense.sheet` | Extract API | Daily |

## 6. Reverse ETL Flows (Outbound from ADLS)

### 6.1 Approved Writeback Targets

| Flow | Type | Target | Data | Guard |
|------|------|--------|------|-------|
| Customer segmentation | `scoring_writeback` | Supabase | Segment flags on user profiles | Write to `_segment` column only |
| Anomaly alerts | `notification_trigger` | Slack / n8n | Alert payload | No data mutation |
| Budget forecast | `enrichment_writeback` | Odoo | Forecast fields on analytic accounts | Write to `x_forecast_*` fields only |
| ML risk scores | `scoring_writeback` | Supabase | Risk score on operational records | Write to `_risk_score` column only |
| Draft expense import | `draft_record_creation` | Odoo | Expense documents from Concur/ADLS | Draft state only, requires approval |
| Materialized summaries | `read_model_refresh` | Supabase | Pre-computed dashboard aggregates | Overwrite designated materialized tables |

### 6.2 Prohibited Writebacks

- Direct overwrite of Odoo posted journal entries
- Direct overwrite of Supabase SSOT control tables
- Mutation of Odoo `account.move` in posted state
- Mutation of Supabase `auth.users` core fields
- Any writeback without an entry in `REVERSE_ETL_GUARDRAILS.md`

## 7. Non-Goals

- Replacing Supabase as SSOT for platform data
- Replacing Odoo as SoR for ERP data
- Making ADLS an operational data store
- Uncontrolled bidirectional sync between any systems
- Mandating Databricks for all compute (ADLS-first, tool-agnostic)
- Real-time streaming for analytical workloads (batch is sufficient)

## 8. Success Criteria

1. Supabase and Odoo data lands in ADLS bronze within defined SLAs
2. Silver and gold layers produce clean, typed, deduplicated datasets
3. Reverse ETL flows are bounded, typed, and contract-governed
4. No authority boundary violations (Supabase=SSOT, Odoo=SoR, ADLS=lake)
5. Every flow has idempotency, failure handling, and evidence output
6. Machine-readable SSOT artifact tracks all flows
7. Phased migration from legacy export paths to ADLS-native
