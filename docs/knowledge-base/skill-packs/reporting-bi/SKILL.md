# Skill Pack: Reporting & Business Intelligence

## Scope

Operational reporting, management dashboards, semantic layer design, and self-service
BI across the Odoo 18 CE + OCA stack with Databricks lakehouse and Power BI for
advanced analytics. Targets parity with SAP BW/4HANA embedded analytics, SAP
Analytics Cloud, and Crystal Reports using open-source and Azure-native tools.

---

## Concepts

| Concept | SAP Equivalent | Odoo 18 CE / Platform Surface |
|---------|---------------|-------------------------------|
| Pivot View | ALV Grid / Query | `ir.ui.view` type=pivot |
| Graph View | SAP Analytics Cloud chart | `ir.ui.view` type=graph |
| Spreadsheet | BPC / Analysis for Office | Odoo Spreadsheet (CE) |
| SQL Report | SAP Query / QuickView | OCA `bi_sql_editor` |
| MIS Report | Management Cockpit | OCA `mis_builder` |
| Lakehouse | BW/4HANA | Databricks Unity Catalog |
| Semantic Model | HANA Calculation View | Power BI dataset / Databricks SQL |
| Dashboard | SAP Fiori Launchpad | Odoo Dashboard + Power BI |

---

## Must-Know Vocabulary

- **Pivot View**: Native Odoo view type rendering `account.move.line` or any model
  as a cross-tab with measures (sum, count, avg) and dimensions (group-by rows/cols).
- **MIS Builder**: OCA module for multi-period, multi-KPI management reports with
  Excel-like formulas over accounting data. Defines report templates as reusable objects.
- **bi_sql_editor**: OCA module allowing admins to write raw SQL, which Odoo wraps
  into a virtual model with pivot/graph/list views. No Python code needed.
- **Semantic Layer**: Abstraction between raw data and business users. Maps technical
  column names to business terms, defines default aggregations and relationships.
- **Medallion Architecture**: Bronze (raw) -> Silver (cleansed) -> Gold (business-ready)
  data layers in the Databricks lakehouse.
- **DLT (Delta Live Tables)**: Databricks framework for declarative ETL pipelines.
- **Materialized View**: Pre-computed query result stored as a table. Used in Databricks
  for performance on complex aggregations.

---

## Core Workflows

### 1. Operational Reporting (Inside Odoo)

**Pivot Views** -- available on any model with numeric fields:
```xml
<record id="view_move_line_pivot" model="ir.ui.view">
    <field name="name">Journal Items Pivot</field>
    <field name="model">account.move.line</field>
    <field name="arch" type="xml">
        <pivot string="Journal Items">
            <field name="account_id" type="row"/>
            <field name="date" interval="month" type="col"/>
            <field name="balance" type="measure"/>
        </pivot>
    </field>
</record>
```

Users can rearrange dimensions, add measures, and export to XLSX from the UI.

**Graph Views** -- bar, line, pie on the same data:
```xml
<graph string="Revenue by Month" type="bar">
    <field name="date" interval="month" type="row"/>
    <field name="balance" type="measure"/>
</graph>
```

### 2. Management Reporting with MIS Builder

MIS Builder (`mis_builder`) workflow:
1. Define a **Report Template** (`mis.report`): rows = KPIs with accounting expressions.
2. Define a **Report Instance** (`mis.report.instance`): binds template to date ranges
   and analytic filters.
3. Expressions use Odoo domain syntax: `balp[('account_id.code','=like','4%')]`
   returns the period balance of accounts starting with 4 (revenue).

Example KPIs:
```
Revenue     = -balp[('account_id.code','=like','4%')]
COGS        = balp[('account_id.code','=like','5%')]
Gross Margin = Revenue - COGS
GM %        = Gross_Margin / Revenue * 100
OPEX        = balp[('account_id.code','=like','6%')]
EBITDA      = Gross_Margin - OPEX
```

Supports multi-company consolidation, budget vs. actual comparison, and analytic
filtering (by project, department, cost center).

### 3. SQL-Based Ad Hoc Reports (bi_sql_editor)

For reports not served by standard views or MIS Builder:
1. Admin writes SQL query in `bi.sql.view` model.
2. Odoo creates a virtual model (`x_bi_sql_view_<name>`).
3. Users access it via list, pivot, or graph views with standard Odoo security.

Example: Aged receivable by salesperson:
```sql
SELECT
    rp.name AS customer,
    ru.login AS salesperson,
    am.date AS invoice_date,
    am.amount_residual AS open_amount,
    CURRENT_DATE - am.invoice_date_due AS days_overdue
FROM account_move am
JOIN res_partner rp ON am.partner_id = rp.id
JOIN res_users ru ON am.invoice_user_id = ru.id
WHERE am.move_type = 'out_invoice'
  AND am.payment_state != 'paid'
  AND am.state = 'posted'
```

### 4. Lakehouse Analytics (Databricks)

Data flow: Odoo PostgreSQL -> Databricks (JDBC extract) -> Bronze -> Silver -> Gold.

**Bronze**: Raw table mirrors (`account_move`, `account_move_line`, `sale_order`,
`project_task`, `hr_timesheet`). Incremental load via `write_date` watermark.

**Silver**: Cleansed, typed, deduplicated. Join `account_move_line` with
`account_account`, `res_partner`, `analytic_account`. Currency normalization to PHP.

**Gold**: Business-ready aggregates:
- `gold.monthly_pnl` -- P&L by month, department, project
- `gold.aged_receivables` -- AR aging buckets (current, 30, 60, 90, 120+)
- `gold.project_ev` -- Earned value metrics per project
- `gold.tax_summary` -- VAT/EWT totals by period for BIR reconciliation

### 5. Power BI Dashboards

Connect Power BI to Databricks SQL Warehouse via Partner Connect or JDBC/ODBC.

Recommended dashboards:
- **Executive Scorecard**: Revenue, EBITDA, cash position, AR/AP aging.
- **Project Portfolio Health**: CPI/SPI heatmap, resource utilization, burn rate.
- **Tax Compliance**: VAT payable trend, EWT by ATC, filing deadline tracker.
- **Sales Pipeline**: Funnel from lead to invoice, win rate, average deal size.

Row-level security (RLS) in Power BI maps to Odoo `res.groups` membership
exported as a dimension table.

---

## Edge Cases

1. **Multi-currency reporting**: Odoo stores journal items in both transaction
   currency and company currency. Always aggregate on `balance` (company currency)
   for consolidated reports. Use `amount_currency` only for transaction-level detail.
2. **Analytic distribution**: Odoo 18 uses percentage-based analytic distribution
   on journal items. MIS Builder expressions must account for the `analytic_distribution`
   JSON field, not a single `analytic_account_id` FK.
3. **Unposted entries in reports**: MIS Builder defaults to posted entries only.
   Verify `target_move` parameter on report instances. Draft entries pollute reports.
4. **bi_sql_editor security**: SQL views bypass Odoo record rules. Always add
   `WHERE company_id = %s` with parameter binding or restrict access via `ir.model.access`.
5. **Databricks sync lag**: Bronze layer is T-1 at best (nightly JDBC). Real-time
   dashboards must query Odoo directly or use CDC (Debezium) for streaming.

---

## Controls & Compliance

| Control | Implementation |
|---------|---------------|
| Report access control | `ir.model.access` on `bi.sql.view` virtual models |
| Audit trail on report definitions | `mail.thread` on `mis.report` and `bi.sql.view` |
| Data freshness SLA | Databricks DLT pipeline monitoring + alerting on stale loads |
| PII masking | Silver layer masks `res_partner.name` for non-privileged datasets |
| Reconciliation gate | Gold aggregates must reconcile to Odoo GL totals within 0.01 PHP |

---

## Odoo/OCA Implementation Surfaces

| Module | Source | Purpose |
|--------|--------|---------|
| `base` (pivot/graph views) | Core | Standard reporting views on any model |
| `spreadsheet` | Core | Collaborative spreadsheets with Odoo data sources |
| `mis_builder` | OCA | Management information system report builder |
| `mis_builder_budget` | OCA | Budget vs. actual comparison in MIS |
| `bi_sql_editor` | OCA | SQL-defined reports with auto-generated views |
| `account_financial_report` | OCA | Trial balance, P&L, balance sheet (OCA version) |
| `account_move_line_report_xls` | OCA | Excel export of journal items |
| `report_xlsx` | OCA | Base XLSX report engine for custom exports |
| `ipai_reporting_lakehouse` | Custom | Databricks JDBC sync configuration and scheduling |

---

## Azure/Platform Considerations

- **Databricks Unity Catalog**: Single governance layer for all Gold tables.
  Catalog: `ipai_prod`, schemas: `bronze`, `silver`, `gold`.
- **Azure Data Factory** (optional): Orchestrate JDBC extracts if Databricks
  DLT scheduling is insufficient. ADF Managed VNet for secure PG access.
- **Power BI Embedded**: Embed dashboards in Odoo via iframe widget in
  `ir.actions.client` for users who never leave the ERP.
- **Azure Monitor**: Alert on DLT pipeline failures, query performance
  degradation, and data freshness SLA breaches.
- **Cost management**: Databricks SQL Warehouse auto-scales. Set max cluster
  size to 2 for dev, 4 for prod. Monitor DBU consumption weekly.

---

## Exercises

### Exercise 1: MIS Builder P&L
Install `mis_builder`. Create a report template with rows: Revenue, COGS, Gross Margin,
OPEX, EBITDA. Use `balp[]` expressions filtered by account code ranges. Create an
instance for Q1 2026 with monthly columns. Verify totals match the trial balance.

### Exercise 2: SQL Ad Hoc Report
Install `bi_sql_editor`. Write a SQL query showing top 10 customers by outstanding
receivables. Create the view. Access via pivot. Add graph view (bar chart). Verify
access is restricted to Accounting Manager group only.

### Exercise 3: Odoo Spreadsheet Integration
Open the Odoo Spreadsheet app. Insert a pivot data source linked to `account.move.line`.
Build a P&L layout with account groups as rows and months as columns. Add a chart.
Share the spreadsheet with the CFO user. Verify they see the same data.

### Exercise 4: Lakehouse Gold Table
Write a Databricks SQL query that produces `gold.monthly_pnl` from silver-layer
`account_move_line` joined with `account_account`. Include columns: `month`, `account_type`,
`account_name`, `balance_php`. Verify the total net income matches Odoo's P&L report.

---

## Test Prompts for Agents

1. "Build a MIS Builder report showing Revenue, Direct Costs, Gross Margin, Operating
   Expenses, and Net Income. Configure it for FY 2026 with monthly columns and a
   YTD total. Apply analytic filter for the 'Consulting' department."

2. "Create a bi_sql_editor report showing sales by product category and month for
   the last 12 months. Include quantity sold, revenue, and average unit price.
   Make it accessible to Sales Manager group only."

3. "Our Power BI dashboard shows PHP 2.3M revenue for March but Odoo GL shows
   PHP 2.35M. Diagnose the discrepancy. Check for unposted entries, currency
   conversion differences, and sync lag."

4. "Design the Databricks Gold layer schema for a CFO dashboard. List the tables
   needed, their grain (granularity), refresh frequency, and which Odoo models
   they source from."

5. "Export the aged receivables report as XLSX with columns: customer, invoice number,
   invoice date, due date, days overdue, open amount, salesperson. Use OCA
   report_xlsx as the engine."
