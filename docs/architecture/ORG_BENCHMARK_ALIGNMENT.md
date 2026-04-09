# Org Benchmark Alignment — Data Model and Fabric

## Core position

The platform is aligned with the Microsoft/Databricks enterprise data benchmark **not because of repo count or tool presence**, but because the intended architecture separates:

1. **Transactional source** (Odoo/PostgreSQL)
2. **Semantic modeling** (Databricks/data-intelligence)
3. **Fabric consumption** (Power BI, Copilot, analyst-facing BI)

---

## Benchmark reading

The Microsoft Fabric reference architecture (used here for its data role, not for SAP positioning) gives Fabric a first-class role for:

- ERP data source connectivity and extraction
- Data transformation and modeling
- Business intelligence and reporting
- Semantic data model integration
- Business process analytics

Fabric is rated **Primary for data warehousing** and **Comprehensive for BI** in the service selection matrix.

Fabric is not optional. But it must sit on top of a **deliberate semantic data model**, not a blind mirror of raw ERP tables.

---

## The data model constraint

Enterprise operational systems (SAP, Odoo) expose multiple data layers that are **not equivalent**:

| Layer | What it is | Safe for direct BI? |
|-------|-----------|---------------------|
| Raw tables | Transactional storage, internal schema | No — business meaning is easy to misread |
| Business views / extractors | Business-oriented logic in the operational system | Partially — still coupled to source schema |
| Curated semantic model | Facts + dimensions, conformed entities, business definitions | Yes — this is what BI should consume |

**Key benchmark lesson**: Even when mirroring is supported, it does not remove the need for a modeled semantic layer. Mirroring is transport, not the data model.

---

## Alignment criteria

### Aligned if

- `data-intelligence` owns source-to-curated modeling
- Conformed business entities exist (dim_partner, fact_invoice, etc.)
- Gold / semantic contracts are explicit
- Fabric consumes curated data, not raw operational tables
- Business definitions live in the modeled data layer, not reconstructed in dashboards

### Not aligned if

- Fabric is used as a raw mirror sink
- Reporting is built directly on operational schemas
- Semantics are reconstructed ad hoc in Power BI reports
- No conformed entity layer exists between source and consumption

---

## Current platform state

### What exists

| Plane | System | Status | Evidence |
|-------|--------|--------|----------|
| Operational source | Odoo PostgreSQL (`pg-ipai-odoo`) | Operational | 12 account_move, 184 project_task rows |
| Lakehouse Federation | Databricks → Odoo PG (live read) | Operational | `odoo_erp.public.*` tables accessible |
| Bronze | `dbw_ipai_dev.bronze.*` | Operational | 33 tables |
| Silver | `dbw_ipai_dev.silver.*` | Operational | 18 tables (dim_partner, fact_invoice, fact_task) |
| Gold | `dbw_ipai_dev.gold.*` | Operational | 26 tables (fact_account_move, client_revenue, dim_project) |
| Fabric mirroring | `pg-ipai-odoo` → OneLake | In progress | F2 capacity active, mirrored DB created, PG connection pending |
| Power BI | Semantic models | Partial | OKR Dashboard exists, broader gold consumption not wired |

### Semantic model coverage

Gold layer tables that represent conformed business entities:

| Gold table | Business entity | Semantic quality |
|-----------|----------------|------------------|
| `fact_account_move` | Financial transactions | Conformed |
| `fact_project_task` | Project execution | Conformed |
| `client_revenue` | Revenue by client | Conformed |
| `dim_project` | Project dimension | Conformed |
| `dim_tag` | Tag dimension | Conformed |
| `dim_task_stage` | Task stage dimension | Conformed |
| `dim_analytic_account` | Analytic account dimension | Conformed |
| `expense_liquidation_health` | Expense health metric | Conformed |
| `ap_ar_cash_summary` | AP/AR cash position | Conformed |

This is a real semantic model, not raw table passthrough.

---

## Role split

| System | Role | Authority |
|--------|------|-----------|
| Odoo PostgreSQL | Operational SoR | Transactional truth |
| Azure Databricks | Data-intelligence plane | Governed lakehouse, medallion, Unity Catalog |
| Unity Catalog | Governance layer | Schema, ACL, lineage, data products |
| Databricks SQL | Serving layer | SQL access to gold for BI/AI |
| Fabric / Power BI | Consumption layer | Analyst-facing reports, dashboards, Copilot |
| Fabric Mirroring | Tactical complement | Quick operational mirrors, not primary analytics |
| data-intelligence repo | Modeling authority | Owns source-to-curated transformation contracts |

---

## What Fabric mirroring is and is not

### Good use

- Quick operational dashboards over recent transactional data
- Exploring data before investing in a Databricks pipeline
- Copilot-in-Fabric scenarios that need low-latency raw data access

### Not a substitute for

- Databricks medallion pipeline (bronze → silver → gold)
- Unity Catalog governance
- Conformed semantic model
- Data product quality gates

### Transport, not model

Mirroring moves data. It does not model data. The business data model must be built in the engineering/modeling plane (`data-intelligence` / Databricks), not in Fabric dashboards.

---

## Practical implications

### For Power BI reports

- Connect to **Databricks SQL Warehouse** (gold layer), not raw mirrored tables
- Use the conformed dimensions and facts from `dbw_ipai_dev.gold.*`
- Direct Lake mode on Fabric can consume gold Delta tables directly

### For Copilot in Fabric

- Ground Copilot on the **semantic model** built from gold data
- Do not ground Copilot on raw mirrored operational tables

### For new data products

- Build in `data-intelligence` repo → Databricks
- Publish to Unity Catalog
- Expose via Databricks SQL or Fabric shortcut
- Do not create parallel modeling in Fabric that duplicates Databricks work

---

## Bottom line

The platform is benchmark-aligned.

The decisive move is no longer additional mirroring. The gold layer already contains 26 conformed business entities, so the next step is to wire curated gold into the business consumption layer.

The benchmark supports Microsoft Fabric as a comprehensive analytics and business-intelligence destination, but only when downstream reporting sits on top of transformed and modeled data rather than raw replicated operational tables. Mirroring solves transport and currency; it does not replace conformance, semantic modeling, or report governance.

Accordingly, the target pattern is:

- Transactional source of record remains in Odoo/PostgreSQL
- Conformance and business entity modeling live in the gold layer
- Power BI connects through the Databricks SQL Warehouse
- Reports and semantic models consume governed serving objects, not arbitrary raw or semi-modeled tables

Current warehouse target:
- Databricks SQL Warehouse: `e7d89eabce4c330c`

Current reporting source pattern:
- `dbw_ipai_dev.gold.*` as the modeled source domain
- Preferred Power BI contract: curated serving views/tables over gold, with stable names and explicit business ownership

---

## Gold-to-Power BI serving contract

To keep benchmark alignment intact, Power BI should not bind indiscriminately to every object inside `dbw_ipai_dev.gold.*`.

Instead, the reporting contract should be:

- Gold remains the conformed business layer
- A narrow serving layer is designated for BI consumption
- Shared measures and dimensional semantics are stabilized before report sprawl begins
- Report authors consume approved serving objects only

Recommended contract options:
- `dbw_ipai_dev.gold.bi_*`
- `dbw_ipai_dev.gold.reporting_*`
- `dbw_ipai_dev.serving.*`

Any of these are acceptable as long as the contract is:
- stable
- documented
- owned
- versioned through the data-intelligence repo

See `docs/architecture/POWER_BI_ON_GOLD.md` for the full serving contract definition.

---

## Anti-patterns to avoid

The following patterns would weaken benchmark alignment:

- Adding more source mirroring without improving semantic conformance
- Building Power BI reports directly on mirrored PostgreSQL tables
- Allowing dashboards to define business logic independently of the gold layer
- Exposing all gold objects as ad hoc self-service reporting inputs
- Mixing experimental modeling tables with BI production contracts

---

## Restore focus: data model and Fabric

Benchmark alignment depends on **curated business modeling**, not merely enabling Fabric or mirroring source tables.

The platform is aligned when:
- `data-intelligence` owns source-to-curated transformation contracts
- Gold tables represent conformed business entities with explicit grain and business definitions
- Fabric consumes a **published semantic model** over governed gold data
- No Power BI report reads directly from raw mirrored ERP tables

The platform is NOT aligned when:
- Fabric mirroring is treated as the primary analytics architecture
- Business semantics are reconstructed ad hoc in dashboard measures
- Raw operational schemas are exposed directly to report consumers
- Multiple competing modeling paths exist without a canonical authority

The `Finance PPM` workspace is the first canonical Fabric workspace. Its target state is defined in `docs/architecture/FABRIC_FINANCE_PPM_TARGET_STATE.md`.

---

## References

- Microsoft/Databricks reference architecture: [Data Intelligence End-to-End](https://techcommunity.microsoft.com/blog/azurearchitectureblog/data-intelligence-end-to-end-with-azure-databricks-and-microsoft-fabric/4232621)
- Role split: `docs/architecture/DATABRICKS_FABRIC_ROLE_SPLIT.md`
- Finance PPM target state: `docs/architecture/FABRIC_FINANCE_PPM_TARGET_STATE.md`
- Power BI serving contract: `docs/architecture/POWER_BI_ON_GOLD.md`
- Data platform audit: `docs/audits/data-platform/20260328/`
- E2E verification: Bronze (33) → Silver (18) → Gold (26) — all verified with live data
