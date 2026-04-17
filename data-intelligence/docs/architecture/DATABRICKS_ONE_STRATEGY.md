# DATABRICKS_ONE_STRATEGY

## Role

Databricks One is the **primary business user consumption surface** for operating intelligence. It replaces ad-hoc notebook sharing, raw SQL access, and standalone BI tool sprawl.

Databricks One hosts:
- Vertical domain dashboards (Delivery, Finance, Tax, ERP)
- Genie Spaces (natural language Q&A over gold marts)
- Vertical analytics apps (if needed — Databricks Apps layer)

## Target Users

| User type | Primary surface | Access pattern |
|---|---|---|
| Executives | Dashboards | Read-only, scheduled refresh |
| Finance managers | Genie Spaces + dashboards | Question-first, natural language |
| Analysts | Genie Spaces + SQL editor | Curated + exploratory |
| Consumer access stakeholders | Dashboards | Embedded or link-based read-only |

## Non-Goals

Databricks One is **not**:
- A transactional workspace (Odoo owns transactions)
- A replacement ERP UI
- A data engineering workspace (that is notebooks/jobs)
- A platform control surface (that is `platform` repo)

## Rollout — 3 Phases

### Phase 1: ADO Delivery Intelligence (now)
- Bronze ingest from Azure DevOps REST API
- Silver transformation (state normalization, iteration mapping)
- Gold mart: `gold_ado_work_item_flow`, `gold_ado_iteration_health`
- Genie Space: IPAI Platform Tracker (pilot)
- Dashboard: Delivery Intelligence v1

### Phase 2: Finance Operations Intelligence
- Bronze ingest from month-end close task schedules (CSV/SharePoint)
- Silver: task normalization, owner mapping, workload scoring
- Gold marts: `gold_finance_close_workload`, `gold_finance_approval_latency`, `gold_finance_recurring_task_load`
- Genie Space: Finance Operations
- Dashboard: Finance Operations v1

### Phase 3: Tax and Compliance Intelligence
- Bronze ingest from BIR deadline calendars, internal approval calendars
- Silver: deadline normalization, risk scoring, form-period mapping
- Gold marts: `gold_tax_deadline_control`, `gold_tax_filing_readiness`, `gold_tax_approval_latency`
- Genie Space: Compliance & Tax
- Dashboard: Compliance & Tax v1

## Data Source Doctrine

- **Bronze-backed pilots** are acceptable temporarily during initial domain build-out.
- **Canonical production serving** uses gold marts or curated serving views only.
- Bronze tables must never be exposed directly in Genie Spaces or dashboards in steady state.
- All gold mart schemas are governed by contracts in `data-intelligence/contracts/`.
