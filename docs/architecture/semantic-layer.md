# Semantic Layer — Unity Catalog as Canonical Metric Definition Surface

> Where business metric definitions live, who owns them, who consumes them.
> Doctrine anchor: `CLAUDE.md` Cross-Repo Invariant #9 — Unity Catalog is the mandatory governed transformation / engineering / serving plane.
> Parent: `docs/architecture/data-model-erd.md`, `docs/architecture/cdm-odoo-mapping.md`.
> Locked 2026-04-15.

---

## 0. Principle

Per Databricks: a semantic layer is an **abstraction layer providing unified
business definitions, metrics, and dimensions atop diverse data sources for
consistent reporting across tools** — establishing a **single source of truth
for business definitions**.

IPAI implements this as **Unity Catalog metrics views on `dbw-ipai-dev`**.
One canonical SQL definition per metric; every consumer (Power BI, Fabric
Data Agent, Pulser agents, mis_builder) reads from that definition.

**Forbidden:** redefining a metric in Power BI DAX, in `mis_builder`, in
a Pulser agent prompt, or in a Fabric semantic model. If a metric exists in
Unity Catalog, consumers reference it; they do not reimplement it.

---

## 1. Unity Catalog namespace assignment

Unity Catalog three-level namespace `catalog.schema.table` maps cleanly to IPAI's architecture:

| UC level | IPAI value | Examples |
|---|---|---|
| Metastore | `metastore_sea` (per Azure region, SEA) | Shared across all Databricks workspaces in SEA |
| Catalog | `ipai_dev` / `ipai_staging` / `ipai_prod` | Matches Odoo DB separation |
| Schema (Bronze) | `bronze` | Raw Odoo-shaped landing (CSV → Parquet) |
| Schema (Silver) | `silver` | Cleaned, typed; Odoo naming preserved |
| Schema (Gold) | `gold` | CDM-shaped entities per `platform/contracts/cdm-entity-map.yaml` |
| Schema (Metrics) | `metrics` | **Canonical semantic layer — metrics views only** |
| Schema (Features) | `features` | ML feature store when needed (Phase 3+ for fine-tune corpus) |
| Table (Gold) | `Account`, `Invoice`, `Payment`, `IPAI_BIRFiling` | CDM entity names |
| Table (Metrics) | `metric_dso`, `metric_dpo`, `metric_days_to_close`, … | One row per period or dimension slice |

**Rule:** metric tables in `metrics` schema are **views over `gold`**, not materialized tables — ensures they always reflect current Gold state. Materialization only when performance demands it (documented per metric).

---

## 2. Canonical metrics — initial set

Every metric in this table MUST have exactly one SQL definition in
`dbw-ipai-dev` Unity Catalog `ipai_<env>.metrics.*`. Consumers reference the
metric view; they do not recompute.

| Metric | Owner agent | UC view | Source | Refresh |
|---|---|---|---|---|
| Days Sales Outstanding (DSO) | `pulser-finance` + `ipai_ar_collections` | `metrics.dso_daily` | `gold.Invoice` + `gold.Payment` | Daily |
| Days Payable Outstanding (DPO) | `pulser-finance` / AP Invoice | `metrics.dpo_daily` | `gold.VendorInvoice` + `gold.Payment` | Daily |
| Days to close (D+N) | Finance Close | `metrics.days_to_close_per_period` | `gold.Invoice` posting lag + `silver.account_fiscal_year.date_stop` | Period-end |
| Filing on-time rate | Tax Guru | `metrics.filing_on_time_rate` | `gold.IPAI_BIRFiling` | Daily |
| Filing penalty-free rate | Tax Guru | `metrics.filing_penalty_free_rate` | `gold.IPAI_BIRFiling` + penalty flags | Daily |
| First-pass-yield AP | AP Invoice | `metrics.first_pass_yield_ap` | `gold.VendorInvoice` + match status | Daily |
| Cost per analysis request | Pulser (all agents) | `metrics.cost_per_agent_request_daily` | `appi-ipai-dev-agent-sea` custom metrics + OpenAI usage | Daily |
| Outsourcing spend ratio | Finance Close | `metrics.outsourcing_spend_ratio` | `gold.VendorInvoice` + category classification | Monthly |
| Reconciliation exception count | Bank Recon | `metrics.recon_exceptions_open` | `gold.BankStatementLine` where `isReconciled=false` | Hourly |
| Risk management composite | All agents | `metrics.risk_composite` | Composite of recon + filing + audit metrics | Daily |

### Example SQL shape (not final — illustrative)

```sql
-- Unity Catalog: ipai_dev.metrics.dso_daily
CREATE OR REPLACE VIEW ipai_dev.metrics.dso_daily AS
SELECT
  DATE_TRUNC('day', invoiceDate) AS period_date,
  businessUnitId AS company_id,
  AVG(DATEDIFF(paymentDate, invoiceDate)) AS dso_days,
  COUNT(*) AS invoice_count,
  SUM(totalAmount) AS total_invoiced
FROM ipai_dev.gold.Invoice
WHERE paymentDate IS NOT NULL
  AND invoiceDate >= CURRENT_DATE - INTERVAL '365 DAYS'
GROUP BY 1, 2;
```

---

## 3. Consumer routing — who reads from where

| Consumer | Reads from | Does NOT redefine |
|---|---|---|
| Power BI semantic model | `ipai_dev.gold.*` (entities) + `ipai_dev.metrics.*` (measures) | metrics in DAX |
| Fabric Data Agent | Shortcut to UC `gold` + `metrics` schemas | metric logic anywhere |
| Pulser Finance agent | PG MCP for operational reads + `metrics.*` for KPI queries | metrics in agent prompts |
| `mis_builder` (Odoo operational reports) | Reads `gold` + `metrics` via Databricks SQL Warehouse endpoint | metric logic in XML reports |
| M365 Copilot Analyst | Fabric Data Agent MCP (consumes UC metrics) | any local metric |
| Customer-facing dashboards | Power BI workspace (reads UC) | any local metric |

**The rule, phrased as one sentence:** every consumer is a READER of Unity Catalog metrics. Only the Databricks metric view is the DEFINER.

---

## 4. Relationship to CDM

Common Data Model and the semantic layer are **orthogonal and complementary**:

| Aspect | CDM | Semantic layer (UC metrics) |
|---|---|---|
| Answers | "What is the shape of an Invoice?" | "What is the value of DSO for Q1 2026?" |
| Primitive | Entity + attributes + relationships | Measure (aggregation over entities) |
| Scope | Structural (schema) | Behavioral (business calculation) |
| Stored as | CDM manifest + Parquet in `stipaidevlake/gold/` | Unity Catalog view (or materialized table) |
| Consumer | Fabric / Power BI / Synapse / M365 Copilot | Same consumers, but for measures instead of entities |
| Source authority | `platform/contracts/cdm-entity-map.yaml` | This doc + UC view DDLs |

Together: CDM gives consumers a shape they recognize; the semantic layer gives them pre-agreed numbers that don't drift.

---

## 5. Unity Catalog governance applied

### 5.1 Access control model

| Role | Privileges | Who |
|---|---|---|
| `data_owner_ipai` | `OWN` on `ipai_dev` catalog | Platform lead |
| `data_engineer_ipai` | `USE CATALOG` + `USE SCHEMA` + `MODIFY` on `bronze`, `silver`, `gold` | Data engineering (Pulser Ops agent MI + humans) |
| `metrics_owner_ipai` | `OWN` on `metrics` schema | Finance lead + data engineering |
| `agent_reader_ipai` | `USE CATALOG` + `SELECT` on `gold` + `metrics` | All Pulser agent MIs (per-agent grants) |
| `bi_reader_ipai` | `SELECT` on `gold` + `metrics` | Power BI service principal |
| `auditor_ipai` | `SELECT` on `platform.audit_event` + UC audit logs | Compliance |

**Forbidden:**
- Pulser agents getting `MODIFY` on `gold` or `metrics` (read-only by design)
- BI service principal getting anything beyond `SELECT`
- Shared service principals across agents (each agent MI is distinct)

### 5.2 Lineage

Unity Catalog captures lineage automatically for SQL-defined views. For the metrics listed in §2:

```
pg-ipai-odoo.public.account_move
    ↓ (Databricks DLT Bronze ingestion)
ipai_dev.bronze.account_move
    ↓ (DLT Silver cleaning)
ipai_dev.silver.account_move
    ↓ (DLT Gold CDM projection)
ipai_dev.gold.Invoice
    ↓ (Metrics view definition)
ipai_dev.metrics.dso_daily
    ↓ (Consumer read)
Power BI / Fabric Data Agent / Pulser Finance
```

Lineage is queryable via `system.access.table_lineage` in UC.

### 5.3 Audit

Every UC operation is audited to `system.access.audit`. Retention per CLAUDE.md security baseline. Cross-joins with `platform.audit_event` on correlation_id when agent actions trigger UC queries.

---

## 6. What mis_builder does (and doesn't do) now

Previously treated `mis_builder` as a potential semantic layer owner. Revised posture:

| Concern | Previous | Locked |
|---|---|---|
| Where metric definitions live | Ambiguous — UC or `mis_builder`? | **Unity Catalog `metrics` schema only** |
| `mis_builder` purpose | Define + report | **Report only** — reads UC metrics via Databricks SQL Warehouse connector; displays in Odoo UI |
| Power BI semantic model | Implemented KPIs directly in DAX | **Forbidden** — DAX references UC metrics |
| Pulser agent prompts | Agent might compute metrics | **Forbidden** — agent queries UC metric view, reports the value |

This avoids three-copies-of-DSO syndrome.

---

## 7. Implementation path

### Phase 1 (blocked on Issue 26 — CDM export pipeline)
- [ ] Provision UC metastore for SEA region (or reuse existing)
- [ ] Create catalogs `ipai_dev`, `ipai_staging`, `ipai_prod`
- [ ] Create schemas `bronze`, `silver`, `gold`, `metrics`, `features`
- [ ] Role assignments per §5.1
- [ ] Bronze + Silver populated from `pg-ipai-odoo` via DLT

### Phase 2 (after Issue 26)
- [ ] Gold tables per CDM mapping (SSOT-driven)
- [ ] Metrics views: land DSO + DPO + Filing-on-time as the first three; validate against Odoo-direct SQL
- [ ] Grant `agent_reader_ipai` to each Pulser agent MI (6 agents currently)
- [ ] `mis_builder` reads via Databricks SQL Warehouse endpoint

### Phase 3
- [ ] All 10 canonical metrics landed
- [ ] Power BI semantic model published on Fabric `fcipaidev` (blocked on Issue 27)
- [ ] Fabric Data Agent wraps metrics for M365 Copilot

### Phase 4
- [ ] Add features schema for FT corpus (Phase 3 of fine-tune roadmap)
- [ ] ML feature groups for payment prediction, variance anomaly

---

## 8. Related artifacts

- `docs/architecture/data-model-erd.md` — DBMS + schemas
- `docs/architecture/cdm-odoo-mapping.md` — CDM entity shapes
- `platform/contracts/cdm-entity-map.yaml` — CDM SSOT
- `docs/backlog/open-issues-20260415.md` — Issue 26 (CDM export), Issue 27 (Fabric capacity)
- Memory: `reference_databricks_fabric_repos` (upstream adoption), `project_fabric_finance_ppm` (Fabric trial expiry)

---

## 9. New backlog issue (auto-land)

**Issue 28 — Unity Catalog namespace + metrics schema bootstrap** (P1)

Provision metastore (if needed), create 3 catalogs × 5 schemas, role assignments per §5.1, land first 3 canonical metric views (DSO, DPO, Filing-on-time) as proof. Dependencies: Issue 26 (Gold exists), `dbw-ipai-dev` access.

See backlog for full acceptance criteria.

---

*Locked 2026-04-15. UC is canonical for metric definitions; CDM is canonical for entity shape; together they're the complete semantic contract.*
