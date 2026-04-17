# REPO_ROLE_DATA_INTELLIGENCE

## Purpose

`data-intelligence` is the analytics and operating intelligence layer for the IPAI platform. It owns all medallion pipeline code (bronze → silver → gold), Unity Catalog schema definitions, Databricks One dashboards, Genie Space configurations, and vertical control tower definitions.

## Owns / Does Not Own

### Owns
- Medallion pipeline code (bronze → silver → gold) in Databricks
- Unity Catalog schema and table definitions
- Databricks One dashboard definitions
- Genie Space configurations and curated example questions
- Vertical domain SSOT files (`ssot/domains/`)
- Data contracts (`contracts/`)
- Serving surface contracts (`ssot/serving/`)
- Vertical metrics and control tower definitions (`ssot/metrics/`)

### Does Not Own
- Odoo ERP source data — that is owned by the `odoo` repo
- Agent personas and tool definitions — owned by the `agents` repo
- Platform control metadata — owned by the `platform` repo
- User-facing product surfaces — owned by the `web` repo
- Infrastructure provisioning — owned by `infra/`

## Source System Relationship

`data-intelligence` consumes from source systems. It does not write back to them.

| Source system | Ingest pattern | Bronze landing |
|---|---|---|
| Azure DevOps (ADO) | REST API → Delta | `bronze_ado_*` |
| Finance workload sheets | CSV / SharePoint export → Delta | `bronze_finance_*` |
| BIR deadline calendars | Structured seed data → Delta | `bronze_bir_*` |
| Odoo ERP (PostgreSQL) | Foreign Catalog (Unity Catalog) or JDBC | `bronze_odoo_*` |

## Strategic Role

`data-intelligence` answers: **what is happening in the business?**

- `odoo` (ERP): **do the work** — transactions, approvals, records
- `data-intelligence`: **understand the work** — flow, bottlenecks, risk, patterns
- `agents`: **act on the understanding** — Pulser surfaces intelligence as copilot behavior
- `platform`: **control the metadata** — governance, RBAC, release gates

## Initial Telemetry Domains (4)

### 1. Delivery Intelligence (ADO)
Work item flow, iteration health, bottleneck detection across Azure DevOps epics, issues, and tasks. Primary question: **what is blocked and why?**

### 2. Finance Operations Intelligence
Month-end close workload analysis, task recurrence patterns, approval latency across the finance team. Primary question: **who is overloaded and where is the close delayed?**

### 3. Tax and Compliance Intelligence
BIR deadline control tower, filing readiness by form and period, approval bottleneck analysis for PH tax obligations. Primary question: **which filings are at risk?**

### 4. ERP Operations Intelligence (Odoo)
Odoo transaction health, vendor/customer flow, invoice aging, payment reconciliation status. Consumed via Unity Catalog Foreign Catalog from `pg-ipai-odoo`. Primary question: **what is the current state of the books?**

## Serving Doctrine

All data intelligence output is served through **Databricks One** (dashboards and Genie Spaces). No direct database access by end users. No standalone BI tool outside Databricks One and Power BI (Power BI consumes gold marts via Databricks SQL Warehouse connector).

Databricks is the **understand the business** layer.
