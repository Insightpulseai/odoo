# VERTICAL_OPERATING_INTELLIGENCE

## Thesis

IPAI's data platform strategy is **Databricks + Unity Catalog as the vertical operating intelligence layer**. This is not a general-purpose data warehouse. It is a purpose-built intelligence substrate for the vertical domains IPAI serves: delivery operations, finance operations, tax compliance, and ERP health.

## Core Split

| System | Role | Question it answers |
|---|---|---|
| **Odoo ERP** | Do the work | Is the invoice posted? Is the close task complete? Is the tax payment approved? |
| **Databricks (data-intelligence)** | Understand the work | Where is the bottleneck? Who is overloaded? Which filing is at risk? What pattern repeats? |
| **Pulser agents** | Act on the understanding | Surface intelligence as Genie answers, copilot suggestions, proactive alerts |
| **Power BI** | Report to stakeholders | Board-level KPIs, external-facing financial summaries |

Odoo is never the analytics surface. Databricks is never the transaction surface.

## Four Vertical Domains

### Domain 1: Delivery Intelligence
- **Source**: Azure DevOps (work items, iterations, sprints)
- **Gold marts**: `gold_ado_work_item_flow`, `gold_ado_iteration_health`
- **Control tower questions**: What is blocked? Where are bottlenecks? Which iterations are at risk?
- **Genie Space**: IPAI Platform Tracker

### Domain 2: Finance Operations Intelligence
- **Source**: Month-end close task schedules, finance workload sheets
- **Gold marts**: `gold_finance_close_workload`, `gold_finance_approval_latency`, `gold_finance_recurring_task_load`
- **Control tower questions**: Who is overloaded? What tasks repeat most? Where are close delays?
- **Genie Space**: Finance Operations

### Domain 3: Tax and Compliance Intelligence
- **Source**: BIR deadline calendars, internal approval calendars
- **Gold marts**: `gold_tax_deadline_control`, `gold_tax_filing_readiness`, `gold_tax_approval_latency`
- **Control tower questions**: What filings are at risk? Which approvals are bottlenecked? What deadlines need escalation?
- **Genie Space**: Compliance & Tax

### Domain 4: ERP Operations Intelligence
- **Source**: Odoo PostgreSQL via Unity Catalog Foreign Catalog (`odoo_erp`)
- **Gold marts**: `gold_odoo_invoice_aging`, `gold_odoo_payment_recon`, `gold_odoo_vendor_flow`
- **Control tower questions**: What is the current AR/AP position? Which invoices are overdue? Where is reconciliation pending?
- **Genie Space**: ERP Health (planned)

## Product Implications

1. **Genie Spaces are the primary analyst surface** — curated, question-first, not raw SQL.
2. **Dashboards are the executive surface** — Databricks One dashboards backed by gold marts.
3. **Power BI is the external/board reporting surface** — consumes gold via SQL Warehouse.
4. **Agents consume gold marts directly** — Pulser finance and tax agents are grounded on gold data, not raw Odoo queries.

## Live Data First Doctrine

Genie Spaces and dashboards **must use live data from Unity Catalog gold tables**. Synthetic data or static sample data is not acceptable for production or pilot spaces. Synthetic data may be used for isolated UI prototyping only.
