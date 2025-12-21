# Notion x Finance PPM Control Room — Constitution

> **Version**: 1.0.0
> **Status**: Active
> **Last Updated**: 2025-12-21

---

## 1. Purpose

The Notion x Finance PPM Control Room is a **unified governance and observability layer** that:
- Uses **Notion** as the source-of-truth for Programs, Projects, and Financial planning
- Leverages **Databricks** as the compute + lakehouse (bronze/silver/gold) for PPM metrics
- Provides a **Control Room web app** for pipeline health, KPIs, and governance checks
- Integrates **Azure Advisor + Azure Resource Graph** signals for cost/risk/optimization insights

---

## 2. Governing Principles

### 2.1 Notion as Planning UI

Notion serves as the human-facing intake for:
- Programs (portfolios of projects)
- Projects (deliverables with budgets and timelines)
- BudgetLines (CapEx/OpEx tracking)
- Risks (issues and mitigations)
- Actions (tasks generated from DQ issues or Advisor recommendations)

The system syncs Notion data to Databricks, **never** writes back to Notion except for Actions/Tasks.

### 2.2 Medallion Architecture (Bronze/Silver/Gold)

All data flows through three layers:

| Layer | Purpose | Update Frequency |
|-------|---------|------------------|
| Bronze | Raw payloads, unchanged | On sync |
| Silver | Normalized, typed tables | On transform |
| Gold | Business-ready marts | On refresh |

### 2.3 Idempotent Sync

All sync operations are idempotent:
- Keyed by `notion_page_id + database_id`
- Use `last_edited_time` watermark for incremental sync
- Support soft-delete (archived flag)
- No data loss on re-run

### 2.4 Control Room as Single Pane

The Control Room provides:
- Pipeline health (job runs, status, lag)
- Data quality checks (drift, nulls, referential)
- Azure Advisor summary (cost, reliability, security)
- Action queue with push-to-Notion capability

### 2.5 No Placeholders Policy

All code must be complete and runnable:
- No `TODO: implement later` stubs
- No placeholder API keys or credentials
- No mock implementations in production paths
- All scripts must be executable end-to-end

---

## 3. Architecture Boundaries

### 3.1 Notion Layer (External)

- Read-only sync of Programs, Projects, BudgetLines, Risks
- Write-only for Actions (push from Control Room)
- API: Notion Python SDK

### 3.2 Databricks Layer (Core Compute)

- Bronze tables: raw Notion pages, Azure RG queries
- Silver tables: normalized entities
- Gold tables: PPM metrics, Advisor rollups
- Jobs: DAB-managed, scheduled

### 3.3 Control Room Layer (Custom UI)

- Next.js + Tailwind app
- FastAPI-style API routes
- Reads gold tables + job metadata
- Writes actions to Notion

### 3.4 Azure Layer (External)

- Azure Resource Graph queries
- Azure Advisor recommendations
- Ingested via scheduled jobs

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CONTROL ROOM UI                              │
│  ┌──────────┐ ┌───────────┐ ┌─────────────┐ ┌──────────┐ ┌────────┐│
│  │ Overview │ │ Pipelines │ │ Data Quality│ │ Advisor  │ │Projects││
│  └──────────┘ └───────────┘ └─────────────┘ └──────────┘ └────────┘│
└───────────────────────────────────────────────────────────────────────┘
                                   │
                         ┌─────────┴─────────┐
                         │   Control Room    │
                         │      API          │
                         └─────────┬─────────┘
                                   │
           ┌───────────────────────┼───────────────────────┐
           │                       │                       │
           ▼                       ▼                       ▼
    ┌─────────────┐        ┌─────────────┐        ┌─────────────┐
    │  Databricks │        │   Notion    │        │    Azure    │
    │  (Lakehouse)│        │   (Intake)  │        │  (Advisor)  │
    └─────────────┘        └─────────────┘        └─────────────┘
```

---

## 4. Data Contracts

### 4.1 Notion → Bronze

Raw payloads stored with:
- `page_id`: Notion page UUID
- `database_id`: Notion database UUID
- `payload`: Full JSON from API
- `synced_at`: Timestamp of sync
- `last_edited_time`: Notion's edit timestamp

### 4.2 Silver Tables

Normalized columns with types:
- Programs: `id, name, owner, start_date, end_date, status`
- Projects: `id, program_id, name, budget_total, currency, status, priority`
- BudgetLines: `id, project_id, category, vendor, amount, committed_date, actual_amount`
- Risks: `id, project_id, severity, probability, status, mitigation, owner`

### 4.3 Gold Tables

Business metrics:
- `ppm_budget_vs_actual`: Monthly budget vs actual by program/project
- `ppm_forecast`: Run-rate forecast with remaining budget
- `ppm_risk_summary`: Risk counts by severity/status
- `azure_advisor_recs`: Advisor recommendations by category
- `control_room_status`: Job runs, DQ checks, freshness

---

## 5. Security & Compliance

### 5.1 Secret Management

- All credentials in environment variables
- Never hardcoded in code or configs
- Use `.env.example` for documentation
- Databricks secrets scope for production

### 5.2 Access Control

- Control Room: API key authentication
- Databricks: Service principal
- Notion: Integration token (scoped)
- Azure: Managed identity preferred

### 5.3 Data Classification

- **Internal**: Project names, budgets, timelines
- **Confidential**: Vendor details, actual spend
- **Restricted**: Never stored (secrets, PII)

---

## 6. Non-Goals

This system does NOT:
- Replace Odoo for financial operations
- Implement full BI/OLAP cube
- Store actual financial transactions (invoices, payments)
- Provide real-time streaming (batch is sufficient)

---

## 7. Success Metrics

| Metric | Target |
|--------|--------|
| Sync lag (Notion → Bronze) | < 15 minutes |
| Data freshness (Gold tables) | < 1 hour |
| DQ check pass rate | > 95% |
| Control Room availability | > 99% |
| Pipeline success rate | > 98% |

---

## Appendix A: Technology Choices

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Planning UI | Notion | User familiarity, collaboration |
| Compute | Databricks | Delta Lake, scalability |
| Storage | Delta Lake | ACID, time travel |
| Control Room | Next.js | Type safety, React ecosystem |
| Sync Service | Python | Notion SDK, Databricks SDK |
| Infra | Bicep | Azure-native IaC |
| CI/CD | GitHub Actions | Repo integration |

## Appendix B: Related Documents

- `prd.md` — Product Requirements
- `plan.md` — Implementation Plan
- `tasks.md` — Task Checklist
