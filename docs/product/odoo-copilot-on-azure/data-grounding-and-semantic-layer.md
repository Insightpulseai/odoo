# Data Grounding and Semantic Layer

> How Copilot (public brand: Pulser) gets its data, what it can see, and what it cannot do.
> Companion to: `docs/architecture/data-intelligence-architecture.md`

---

## Where Copilot Gets Grounded Data

Copilot operates in two grounding modes, each with distinct data sources, latency profiles, and authorization boundaries.

### Operational Grounding (Odoo ORM)

For real-time transactional context -- looking up a specific invoice, checking current stock levels, reading a partner record -- Copilot queries Odoo directly through the ORM API. This path provides immediate, authoritative answers for single-record or small-set lookups.

- **Source**: Odoo CE 19 via ORM/RPC
- **Latency**: Sub-second (database round-trip)
- **Freshness**: Real-time (current transaction state)
- **Scope**: Current user's Odoo access rights (ir.model.access + ir.rule)
- **Use cases**: "What is the status of SO-2024-00142?", "Show me the last 5 invoices for partner X", "What items are below reorder point?"

### Analytical Grounding (Databricks Gold Layer)

For trend analysis, cross-domain insights, aggregated metrics, and historical patterns, Copilot queries the governed gold layer in the Databricks lakehouse. This path provides curated, pre-computed answers that span time ranges and business domains.

- **Source**: Gold tables in Unity Catalog via Databricks SQL Warehouse `e7d89eabce4c330c`
- **Latency**: 1-10 seconds (SQL warehouse query)
- **Freshness**: Based on DLT pipeline schedule (see Freshness Contract below)
- **Scope**: Entra ID group membership mapped to Unity Catalog ACLs
- **Use cases**: "What is the revenue trend for Q1?", "Which product categories have the highest return rate?", "Compare sales performance across regions for the last 12 months"

---

## Operational vs Analytical Grounding

| Dimension | Operational (Odoo ORM) | Analytical (Gold Layer) |
|-----------|----------------------|------------------------|
| Data source | Odoo PostgreSQL (live) | Databricks gold tables (curated) |
| Freshness | Real-time | Pipeline-dependent (hourly/daily) |
| Scope | Single records, small sets | Aggregates, trends, cross-domain |
| Authorization | Odoo ACLs (ir.model.access, ir.rule) | Unity Catalog ACLs (Entra ID groups) |
| Latency | < 1 second | 1-10 seconds |
| Write capability | Read-only from Copilot | Read-only from Copilot |
| Conflict resolution | ORM is authoritative for current state | Gold layer is authoritative for historical/aggregate |

### When to Use Each

**Use operational grounding when:**

- The question refers to a specific record by ID, name, or reference number
- The answer requires the current transactional state (e.g., order status, payment status)
- The data scope is narrow (single partner, single order, current inventory level)
- Real-time accuracy is required

**Use analytical grounding when:**

- The question asks about trends, patterns, or comparisons over time
- The answer requires aggregation across many records (totals, averages, distributions)
- The question spans multiple business domains (sales + inventory + finance)
- Historical data is needed beyond the current transaction window

**Copilot routing logic:**

The Copilot gateway determines the grounding mode based on query classification. If a query matches both modes (e.g., "What is partner X's total spend this year?"), the gateway prefers analytical grounding for aggregated answers and falls back to operational grounding if the analytical source lacks the requested domain.

---

## Semantic Model Boundaries

A "semantic product" is the unit of governed data that Copilot and BI consumers can access. Each semantic product consists of:

| Component | Description |
|-----------|-------------|
| Gold table | The physical Delta table in Unity Catalog (`gold.<domain>.<product>`) |
| Metadata | Column descriptions, business glossary terms, data classification tags |
| Access policy | Unity Catalog ACL defining which Entra ID groups can query |
| Freshness SLA | Maximum acceptable staleness (e.g., 1 hour, 24 hours) |
| Owner | Named team or individual responsible for data quality and schema evolution |
| Version | Schema version tracked in Unity Catalog; consumers bind to a specific version |

A gold table that lacks any of these components is not a complete semantic product and must not be registered as a Copilot grounding source.

### Semantic Product Lifecycle

1. **Proposed**: DLT pipeline code written, gold table schema defined, not yet materialized
2. **Materialized**: Gold table populated, quality checks passing, metadata registered
3. **Published**: Access policy applied, freshness SLA declared, Purview sync active
4. **Grounding-ready**: Registered in Copilot grounding index, validated by grounding validation runbook
5. **Deprecated**: Superseded by a new version; consumers given a migration window

Only products in **Published** or **Grounding-ready** state are valid grounding sources.

---

## Gold/Business-Ready vs Raw/Exploratory

| Layer | Consumer Access | Copilot Access | Justification Required |
|-------|----------------|----------------|----------------------|
| Gold | All authorized consumers | Default grounding source | No |
| Silver | Data engineers, analysts | Not available | Yes -- explicit request with business justification |
| Bronze | Data engineers only | Never available | N/A -- raw data is not a grounding source |

**Default rule**: Gold is the only layer exposed to Copilot and BI consumers. Silver access requires a documented justification (e.g., debugging a data quality issue, building a new gold table). Bronze is never exposed outside the data engineering team.

If a consumer requests data that exists only in Silver or Bronze, the correct response is to build a gold table for that domain, not to grant Silver/Bronze access.

---

## Non-Goal: Copilot Does Not Redefine Business Truth

Copilot is a **read-only consumer** of governed semantic products. It does not:

- Write back to the lakehouse (no table creation, no row insertion, no schema modification)
- Create ad-hoc business rules or calculated fields outside the governed pipeline
- Override data quality flags or freshness SLA violations
- Serve as a source of truth for any downstream system
- Cache answers as if they were new data products

Copilot answers are derived from governed data. If the underlying gold table changes, Copilot's answers change accordingly. There is no Copilot-specific data layer that can diverge from the governed source.

---

## Grounding Sources Table

| Domain | Gold Table Pattern | Refresh Cadence | Copilot Capabilities |
|--------|-------------------|-----------------|---------------------|
| Finance | `gold.finance.monthly_revenue`, `gold.finance.ar_aging`, `gold.finance.gl_balance` | Daily (06:00 UTC) | Revenue trends, aging analysis, balance summaries, period comparisons |
| HR | `gold.hr.headcount`, `gold.hr.attendance_summary`, `gold.hr.expense_summary` | Daily (06:00 UTC) | Headcount metrics, attendance patterns, expense aggregates |
| Sales | `gold.sales.order_summary`, `gold.sales.pipeline_stage`, `gold.sales.product_performance` | Hourly | Pipeline status, win/loss analysis, product performance ranking |
| Inventory | `gold.inventory.stock_level`, `gold.inventory.turnover`, `gold.inventory.reorder_alert` | Hourly | Stock availability, turnover analysis, reorder recommendations |
| Purchasing | `gold.purchasing.po_summary`, `gold.purchasing.vendor_performance` | Daily (06:00 UTC) | Purchase order trends, vendor scorecards |
| CRM | `gold.crm.lead_funnel`, `gold.crm.conversion_rate`, `gold.crm.activity_summary` | Hourly | Lead funnel analysis, conversion tracking, activity trends |

Each gold table listed above must be a complete semantic product (table + metadata + access policy + freshness SLA + owner) before it is registered as a Copilot grounding source.

---

## Freshness Contract

Data freshness is a first-class contract term. Copilot must know how stale its grounding data can be and must communicate this to the user when relevant.

### Freshness by Grounding Mode

| Mode | Freshness Guarantee | Mechanism |
|------|-------------------|-----------|
| Operational (Odoo ORM) | Real-time | Direct database query; no caching layer |
| Analytical (Gold Layer) | Pipeline-dependent | DLT pipeline schedule defines maximum staleness |

### Freshness by Domain

| Domain | Pipeline Schedule | Maximum Staleness | Notes |
|--------|------------------|-------------------|-------|
| Sales | Hourly | 1 hour | High-velocity; hourly refresh justified |
| Inventory | Hourly | 1 hour | Stock levels change frequently |
| CRM | Hourly | 1 hour | Lead/opportunity movement is time-sensitive |
| Finance | Daily at 06:00 UTC | 24 hours | Financial data refreshed after nightly close |
| HR | Daily at 06:00 UTC | 24 hours | Headcount/attendance aggregated daily |
| Purchasing | Daily at 06:00 UTC | 24 hours | PO activity aggregated daily |

### Freshness Enforcement

- Each gold table carries a `_last_refreshed_at` metadata column (or Unity Catalog table property)
- Copilot gateway checks freshness before serving an analytical answer
- If staleness exceeds the declared SLA, Copilot must either:
    1. Fall back to operational grounding (if the question can be answered via ORM)
    2. Serve the answer with an explicit staleness warning (e.g., "This data was last refreshed 26 hours ago, exceeding the 24-hour SLA")
    3. Decline to answer if neither fallback is appropriate

### Freshness Is Not Accuracy

Freshness guarantees that data is recent. It does not guarantee that data is correct. Data quality is enforced by DLT expectations at each pipeline stage. Freshness and quality are independent contract terms.

---

*Last updated: 2026-03-28*
