# PRD — Fabric Warehouse and Power BI Serving Model

> Product requirements for the canonical workload-allocation policy
> across Databricks, Fabric, and Power BI.

---

## 1. Problem Statement

Microsoft Fabric is an end-to-end SaaS analytics platform with multiple workloads operating over OneLake as the centralized logical data lake. The platform has a live Databricks engineering lane (medallion pipeline, SQL Warehouse, Unity Catalog) but no codified policy for how Fabric's serving surfaces — Lakehouse, SQL analytics endpoint, Data Warehouse — relate to Databricks engineering, or how Power BI Desktop and Service divide authoring from distribution responsibilities.

The Fabric documentation distinguishes Fabric Data Warehouse as the governed relational serving surface (star/snowflake, T-SQL, ACID), the SQL analytics endpoint as the lightweight SQL bridge over lake data (read-only, views, security), and Power BI as the modeling/reporting/distribution workload. This distinction must be encoded as the canonical target state.

Without a single workload-allocation policy:

- Teams may duplicate Gold data into Fabric without governance
- Semantic models may proliferate without source control
- Power BI reports may connect directly to operational databases
  (Odoo PG), bypassing the governed Gold layer
- Fabric Data Warehouse and Lakehouse SQL analytics endpoint roles
  overlap without clear decision criteria
- Databricks engineering authority erodes through ad-hoc Fabric usage

## 2. Goals

1. **Single canonical workload-allocation policy** that assigns every
   analytics workload class to exactly one platform surface
2. **Decision rules** that teams can apply without escalation
3. **Non-goals table** that prevents layer misuse before it starts
4. **Semantic model governance** ensuring one model per domain, authored
   in Desktop, published to Service
5. **Fabric Warehouse scoping** limited to curated BI marts with
   star/snowflake schemas
6. **Power BI connection policy** mandating Databricks SQL or Fabric
   Warehouse as the only approved data sources

## 3. Non-Goals

| Non-Goal | Rationale |
|----------|-----------|
| Replace Databricks with Fabric for engineering | Databricks is the mandatory engineering lane per `MEDALLION_ARCH.md` |
| Move Odoo operational data into Fabric | Odoo PG is SoR; Fabric receives only governed replicas via mirroring |
| Adopt Tableau as a primary BI surface | Power BI is the mandatory primary reporting surface; Tableau is secondary |
| Build real-time streaming in Fabric | Streaming workloads belong in Databricks Structured Streaming |
| Provision Fabric capacity for all environments | Start with dev workspace only; prod capacity gated by review |

## 4. Functional Requirements

### FR-1: Workload Classification Matrix

Publish a table mapping every analytics workload class (ETL, feature
engineering, BI mart curation, semantic modeling, report distribution,
ad-hoc exploration) to its canonical platform surface. The table must
be committed to `docs/architecture/ANALYTICS_TARGET_STATE.md`.

### FR-2: Decision Rules

Codify at least 6 decision rules (DR-1 through DR-6) that resolve
ambiguous cases. Each rule must state the condition, the correct
surface, and what is prohibited.

### FR-3: Fabric Data Warehouse Scope

Define Fabric Data Warehouse as the surface for:
- Star/snowflake schemas with conformed dimensions
- Multi-table ACID fact loads
- T-SQL-first enterprise BI/OLAP consumers

Prohibit its use for raw ingestion, streaming, or ML feature storage.

### FR-4: Lakehouse SQL Analytics Endpoint Scope

Define the SQL analytics endpoint as a read-only SQL view layer over
Delta data in OneLake. Writes are prohibited. Use cases: analyst
exploration, row/column security, view creation.

### FR-5: Power BI Governance

- Semantic models authored in Power BI Desktop, committed as `.pbip`
- One semantic model per Gold domain (finance, projects, compliance, platform)
- Published to Power BI Service with RLS, scheduled refresh, app distribution
- Direct connections to Odoo PG or raw Bronze data prohibited

### FR-6: Connection Policy

Power BI may connect only to:
1. Databricks SQL Warehouse (via Partner Connect or ODBC/JDBC)
2. Fabric Data Warehouse (via DirectQuery or Direct Lake)
3. Fabric Lakehouse SQL analytics endpoint (via DirectQuery)

All other data sources require an exception documented in
`docs/architecture/ANALYTICS_TARGET_STATE.md`.

### FR-7: Platform Language Consistency

Fabric platform language must consistently reflect that Fabric is a SaaS analytics platform over OneLake with multiple workloads sharing common governance and storage services. OneLake is the centralized logical lake with zero-copy reuse. Power BI is a workload within Fabric, not the storage or warehouse substrate.

## 5. Acceptance Criteria

| # | Criterion | Verification |
|---|-----------|-------------|
| AC-1 | `ANALYTICS_TARGET_STATE.md` exists with workload table, decision rules, non-goals | File review |
| AC-2 | Spec bundle `spec/fabric-power-bi-serving/` has prd, plan, tasks | File review |
| AC-3 | Decision rules cover Databricks vs Fabric Warehouse vs Lakehouse endpoint vs Power BI | Content review of DR-1 through DR-6 |
| AC-4 | Non-goals table explicitly prohibits Databricks replacement, direct Odoo PG connections, ungoverned Excel exports | Content review |
| AC-5 | `MEDALLION_ARCH.md` language preserved (Databricks = mandatory engineering core) | Diff review — no contradictions |
| AC-6 | Current-state table reflects actual resource status as of 2026-03-21 | Cross-reference with Azure resource inventory |

---

*Last updated: 2026-03-21*
