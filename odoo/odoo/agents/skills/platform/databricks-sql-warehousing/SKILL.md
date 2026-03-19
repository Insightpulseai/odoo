# Skill: Databricks SQL & Data Warehousing

## Metadata

| Field | Value |
|-------|-------|
| **id** | `databricks-sql-warehousing` |
| **domain** | `lakehouse` |
| **source** | https://learn.microsoft.com/en-us/azure/databricks/sql/ |
| **extracted** | 2026-03-15 |
| **applies_to** | lakehouse, agents |
| **tags** | databricks, sql, warehousing, dashboards, metrics, alerts, delta-lake |

---

## What It Is

Data warehousing on Azure Databricks combines cloud DW capabilities with lakehouse architecture. Runs on SQL warehouses, supports ANSI SQL with Delta Lake extensions. Queries run directly on the data lake — no data copies.

## Interfaces

| Interface | Description | IPAI Use |
|-----------|-------------|----------|
| **Query Editor** | SQL with AI Assistant, code comments, version history | Ad-hoc analysis, debugging |
| **Notebooks** | SQL alongside Python/Scala/R | ETL development |
| **Jobs** | Scheduled SQL for automated processing | Gold mart refresh |
| **AI/BI Dashboards** | Interactive dashboards with AI-assisted authoring | Executive reporting |
| **Metric Views** | Semantic layer for consistent business metric definitions | KPI standardization |
| **Alerts** | Scheduled queries → condition evaluation → notifications | BIR deadline alerts, budget variance |
| **Query Performance** | History, bottleneck identification, optimization | Performance tuning |
| **REST API** | Programmatic automation | CI/CD integration |

## Key Concepts

| Concept | Description |
|---------|-------------|
| **SQL Warehouse** | Compute resource for running SQL (serverless or classic) |
| **Medallion layers** | Bronze → Silver → Gold architecture on Delta Lake |
| **Unity Catalog** | Governance: access control, lineage, data discovery |
| **Metric views** | Reusable business metric definitions (semantic layer) |
| **Delta Lake** | ACID transactions, time travel, schema evolution on Parquet |

## IPAI Mapping

| Databricks SQL | IPAI Current | Gap |
|---------------|-------------|-----|
| SQL Warehouse | No Databricks workspace yet | **Deploy**: provision `dbw-ipai-dev` |
| AI/BI Dashboards | Superset (`superset.insightpulseai.com`) | Superset covers this — evaluate migration later |
| Metric views | None | **Adopt**: standardize KPI definitions |
| Alerts | n8n cron + Slack | Databricks alerts add SQL-native monitoring |
| Query editor | None | Useful for analyst self-service |
| Unity Catalog | No data governance | **Adopt**: critical for data access control |

### When to Use Databricks SQL vs Superset

| Use Case | Tool |
|----------|------|
| Self-service SQL for analysts | Databricks SQL |
| Executive dashboards (embedded) | Superset (already deployed) |
| Metric definitions (semantic layer) | Databricks Metric Views |
| Ad-hoc data exploration | Databricks SQL |
| Operational dashboards | Superset |

### Gold Mart Queries (Sample)

```sql
-- Monthly revenue by journal
SELECT
  DATE_TRUNC('month', move_date) AS month,
  j.name AS journal_name,
  SUM(amount_total) AS total_revenue,
  COUNT(*) AS invoice_count
FROM gold.fct_invoices f
JOIN gold.dim_journals j ON f.journal_id = j.id
GROUP BY 1, 2
ORDER BY 1 DESC

-- Expense by category (for Concur parity dashboard)
SELECT
  DATE_TRUNC('month', date) AS month,
  p.name AS category,
  SUM(total_amount) AS total_expenses,
  COUNT(*) AS expense_count
FROM gold.fct_expenses e
JOIN gold.dim_expense_categories p ON e.product_id = p.id
GROUP BY 1, 2
ORDER BY 1 DESC, 3 DESC
```
