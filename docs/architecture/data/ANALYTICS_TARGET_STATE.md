# Analytics Target State — Canonical Workload Split

> Governs which analytics workloads run on which platform surface.
> Extends `MEDALLION_ARCH.md`. Never contradicts it.

---

## Platform Frame

Microsoft Fabric is an end-to-end SaaS analytics platform with multiple workloads (Data Factory, Data Engineering, Data Science, Real-Time Intelligence, Data Warehouse, Databases, and Power BI) operating over shared platform services. OneLake is the centralized logical data lake — tenant-wide, built on ADLS Gen2, with zero-copy reuse across workloads and shortcut support so data remains in place rather than being duplicated.

The architecture is intentionally converged: different compute surfaces operate over the same underlying data estate. Governance is inherited across Fabric items. Power BI is one of the Fabric workloads, not the storage or warehouse layer.

For InsightPulseAI, Databricks remains the primary engineering lane (Spark, medallion, ML). Fabric extends the platform with governed relational serving (Warehouse) and business consumption (Power BI). These are complementary, not competing surfaces.

---

## Workload Allocation Table

| Surface | Role | Data Format | Query Language | Governance Layer | Use When |
|---------|------|-------------|----------------|------------------|----------|
| **Databricks** (engineering lane) | Heavy ETL, feature engineering, ML training, medallion transforms, streaming | Delta Lake (UniForm) on ADLS Gen2 | PySpark, Spark SQL, Python | Unity Catalog | Complex transforms, ML pipelines, cross-source joins, data quality rules, anything needing Spark |
| **Fabric Lakehouse + SQL analytics endpoint** | Read-only SQL view over Delta data in OneLake | Delta tables (mirrored or shortcutted) | T-SQL (read-only views, functions, security) | OneLake + workspace RBAC | Lightweight SQL access to lake data without moving it; ad-hoc exploration; Fabric-native notebook prototyping |
| **Fabric Data Warehouse** | Curated corporate data marts, star/snowflake BI schemas | Managed columnar (Fabric-internal) | T-SQL (full DML/DDL, multi-table ACID) | OneLake + workspace RBAC | Governed BI marts that need full ACID writes, dimensional modeling, T-SQL-first consumers, enterprise OLAP |
| **Power BI Desktop** | Semantic model authoring, DAX measures, report design | Import / DirectQuery / Direct Lake | DAX, M (Power Query) | `.pbip` source control | Building and testing semantic models, report layout, measure authoring |
| **Power BI Service** | Publishing, collaboration, scheduled refresh, RLS enforcement, app distribution | Hosted datasets + reports | DAX (queries), REST API | Power BI workspace RBAC, sensitivity labels | Governed consumption: dashboards, paginated reports, alerts, subscriptions, embedded analytics |

---

## Decision Rules

### DR-1: Default to Databricks for engineering

All ETL, CDC processing, schema enforcement, feature engineering, and ML workloads run on Databricks. Fabric does not replace Databricks for engineering.

### DR-2: Fabric Data Warehouse for BI marts only

Use Fabric Data Warehouse when the consumer is a T-SQL BI tool and the data requires:
- Star or snowflake schema with referential integrity
- Multi-table ACID transactions for dimension/fact loads
- Corporate data mart semantics (conformed dimensions, business keys)

Do not use Fabric Data Warehouse for raw ingestion, streaming, or ML feature tables.

### DR-3: Lakehouse SQL analytics endpoint for read-only access

Use the Lakehouse SQL analytics endpoint when:
- Analysts need SQL access to Delta tables without copying data
- Security policies (column/row-level) need to be applied at the SQL layer
- The workload is read-only exploration or view creation

Never write data through the SQL analytics endpoint. All writes flow through Databricks or Fabric Data Warehouse.

### DR-4: Power BI Desktop for authoring, Service for distribution

- **Desktop**: Build semantic models, author DAX measures, design reports. Commit `.pbip` files to source control.
- **Service**: Publish, schedule refresh, enforce RLS, distribute via apps. Never author measures directly in Service without backporting to Desktop source.

### DR-5: One semantic model per domain

Each Gold domain mart (finance, projects, compliance, platform) has exactly one semantic model. Duplicating semantic models across workspaces is prohibited.

### DR-6: Databricks SQL Warehouse remains primary query endpoint

The Databricks SQL Warehouse (`e7d89eabce4c330c`) serves Gold tables to both Power BI (via connector) and Fabric (via shortcut/mirroring). It is the primary governed query endpoint for analytical consumers.

---

## Non-Goals (Layer Misuse Prevention)

| Prohibited Pattern | Why | Correct Alternative |
|--------------------|-----|---------------------|
| Running Spark jobs in Fabric Lakehouse | Databricks is the engineering lane | Use Databricks notebooks/jobs |
| Storing raw Bronze data in Fabric Data Warehouse | Warehouse is for curated marts only | Land raw data in ADLS via Databricks |
| Moving Odoo tables into Fabric via direct copy | Breaks authority boundary; Odoo PG is SoR | Use Fabric Mirroring or Databricks ingestion |
| Authoring DAX measures only in Power BI Service | No source control, no review | Author in Desktop, publish `.pbip` |
| Using Fabric Data Warehouse for ML feature storage | Wrong tool; no Spark, no MLflow | Use Databricks Feature Store |
| Replacing Databricks with Fabric for medallion transforms | Violates `MEDALLION_ARCH.md` mandatory pillar | Databricks + Unity Catalog for all medallion work |
| Connecting Power BI directly to Odoo PG | Bypasses governed Gold layer | Connect Power BI to Databricks SQL or Fabric Warehouse |
| Creating ad-hoc Excel exports from Gold tables | Ungoverned distribution | Use Power BI apps with RLS |

---

## Current State (2026-03-21)

| Component | Status | Detail |
|-----------|--------|--------|
| Databricks workspace | Active | `dbw-ipai-dev`, premium, Unity Catalog enabled |
| Medallion pipeline | Data flowing | Odoo PG -> Lakehouse Federation -> Bronze -> Silver -> Gold |
| SQL Warehouse | Running | `e7d89eabce4c330c` |
| Databricks Dashboard | Published | IPAI Finance PPM Analytics |
| Power BI | Free tier | `admin@insightpulseai.com`, not yet connected to Databricks |
| Fabric Mirroring | Ready | `pg-ipai-odoo` WAL=logical, mirroring not yet activated |
| Fabric Data Warehouse | Not provisioned | Pending workspace capacity allocation |
| Tableau Cloud | Registered | `insightpulseai` site, Entra SAML app — secondary surface only |

---

## Operating Note

Fabric should be treated as a converged analytics platform over OneLake, with workload-specific surfaces rather than a single monolithic tool. The architecture must preserve this split rather than collapsing engineering, serving, and reporting into one layer. Each workload surface has its own strengths: Databricks for engineering scale, Fabric Warehouse for relational BI marts, SQL analytics endpoint for lightweight lake access, and Power BI for semantic modeling and business distribution.

Default semantic model behavior changed in Fabric: auto-created default semantic models are no longer generated for warehouse/lakehouse/mirrored items. Semantic modeling is now intentional and explicit — align with DR-5 (one semantic model per domain).

---

## References

- `docs/architecture/MEDALLION_ARCH.md` — Mandatory medallion lanes
- `spec/adls-etl-reverse-etl/` — ETL/reverse-ETL spec bundle
- `spec/fabric-power-bi-serving/` — This workload-split spec bundle
- `data-intelligence/` — Databricks code and notebooks

---

*Last updated: 2026-03-21*
