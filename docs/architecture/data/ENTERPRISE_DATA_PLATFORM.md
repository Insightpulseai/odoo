# Enterprise Data Platform Doctrine

> Consolidated enterprise data platform architecture covering ingestion,
> medallion/lakehouse design, data domains, governance, cost controls,
> BI serving, and ML/MLOps path.
>
> Ref: https://learn.microsoft.com/en-us/azure/architecture/solution-ideas/articles/ingest-etl-stream-with-adb
> Cross-references:
>   - `docs/architecture/ADLS_ETL_REVERSE_ETL_ARCHITECTURE.md` (integration surfaces)
>   - `infra/ssot/azure/PLATFORM_TARGET_STATE.md` §Analytics (serving surfaces)
>   - `ssot/governance/azdo-execution-hierarchy.yaml` (OBJ-004 Epic)
>   - `docs/contracts/DATA_AUTHORITY_CONTRACT.md` (authority model)

---

## 1. System Authority Model

```
Odoo (System of Record)         Supabase (Control Plane)
  Finance, HR, CRM, Projects      Platform metadata, workflow state
  Operational transactions         Agent memory, vector embeddings
  BIR tax compliance               Auth identity

            ↓ ETL (Extract API / CDC)           ↓ ETL (Supabase client)

                    ADLS Gen2 (Analytical Lake)
                    Bronze → Silver → Gold
                    Authoritative for NOTHING operational

            ↓ Serve                              ↓ Reverse ETL (bounded)

  Databricks SQL    Power BI    Odoo (enrichment fields)
  (ad-hoc queries)  (exec dashboards) (ops metrics) (draft docs, forecasts)
```

**Invariant**: The analytical lake is never the source of truth for operational data.
Reverse ETL is bounded, typed, and contract-governed.

### Platform Role Separation

| Platform | Role | Not |
| -------- | ---- | --- |
| **Databricks** | Governed lakehouse, transformation, AI/ML, SQL serving | Not a BI tool |
| **Fabric** | BI consumption, Power BI semantic models, Copilot analytics | Not the engineering/transformation plane |
| **Unity Catalog** | Data + AI governance, lineage, RBAC | Not optional |
| **Purview** | Estate-wide metadata visibility, sensitivity classification | Not a replacement for Unity Catalog |
| **ADLS Gen2** | Analytical lake storage (Bronze/Silver/Gold) | Not an operational database |

Ref: [Data Intelligence E2E with Databricks and Fabric](https://techcommunity.microsoft.com/blog/azurearchitectureblog/data-intelligence-end-to-end-with-azure-databricks-and-microsoft-fabric/4232621)

---

## 2. Medallion / Lakehouse Design

### Bronze (Raw Landing)

| Source | Extraction Method | Landing Path | Cadence |
|--------|-------------------|-------------|---------|
| Odoo PG | Extract API (bulk) | `bronze/odoo/{table}/{date}/` | Daily |
| Supabase | Client SDK | `bronze/supabase/{table}/{date}/` | Daily |
| External APIs | n8n workflows | `bronze/external/{source}/{date}/` | Varies |

**Format**: Parquet (columnar, compressed)
**Retention**: 90 days raw, then archive to cool tier
**Schema**: Schema-on-read (no enforcement at bronze)

### Silver (Cleansed, Conformed)

| Domain | Key Tables | Transformations |
|--------|-----------|-----------------|
| Finance | `fact_invoices`, `dim_accounts`, `dim_partners` | Dedup, null handling, currency normalization |
| CRM | `fact_opportunities`, `dim_stages`, `dim_sales_team` | Status mapping, date normalization |
| HR | `fact_employees`, `dim_departments` | PII masking, role normalization |
| Platform | `fact_platform_events`, `dim_workflows` | Event dedup, timestamp normalization |

**Schema**: Enforced via Delta Lake schema evolution
**Quality**: Expectations defined per table (null checks, range checks, referential integrity)
**SCD**: Type 2 for dimension tables (track history)

### Gold (Business-Ready Aggregates)

| Data Product | Consumers | Refresh |
|-------------|-----------|---------|
| Customer 360 | Power BI | Daily |
| Revenue Dashboard | Power BI | Daily |
| BIR Tax Summary | `ipai_bir_tax_compliance` (reverse ETL) | Monthly |
| Campaign Performance | Power BI | Weekly |
| Platform Health | Superset | Hourly |

**Format**: Delta Lake tables exposed via Databricks SQL endpoints
**Access**: Unity Catalog RBAC — no direct ADLS access for consumers

---

## 3. Data Domains / Products

### Domain Model

| Domain | Owner | Source System | Key Entities |
|--------|-------|--------------|-------------|
| Finance | Engineering lead | Odoo (`account.*`) | Invoices, payments, journal entries, tax returns |
| Sales | Engineering lead | Odoo (`sale.*`, `crm.*`) | Orders, opportunities, quotations |
| HR | Engineering lead | Odoo (`hr.*`) | Employees, contracts, attendance |
| Platform | Platform lead | Supabase, n8n | Events, workflow runs, agent executions |
| External | Product lead | APIs, web scraping | Market data, competitor intelligence |

### Data Product Contract

Each gold-layer data product must have:
- **Schema**: Defined in Unity Catalog
- **Owner**: Named domain owner
- **SLA**: Refresh cadence + staleness tolerance
- **Quality**: Defined expectations (Great Expectations or Databricks DQ rules)
- **Lineage**: Tracked via Unity Catalog lineage

---

## 4. Governance

### Unity Catalog Hierarchy

```
Unity Catalog
└── ipai_dev (catalog)
    ├── bronze (schema)
    │   ├── odoo_*
    │   └── supabase_*
    ├── silver (schema)
    │   ├── finance_*
    │   ├── crm_*
    │   └── platform_*
    └── gold (schema)
        ├── customer_360
        ├── revenue_dashboard
        └── bir_tax_summary
```

### Access Control

| Role | Bronze | Silver | Gold | Reverse ETL |
|------|--------|--------|------|-------------|
| Platform lead | Read/Write | Read/Write | Read/Write | Approve |
| Engineering lead | Read | Read/Write | Read/Write | Execute |
| Data analyst | — | Read | Read | — |
| BI consumer | — | — | Read | — |
| Reverse ETL service | — | — | Read | Execute |

### Data Quality

- **Bronze**: No enforcement (raw landing)
- **Silver**: Expectations on every table (nulls, types, ranges, referential integrity)
- **Gold**: SLA-backed quality (staleness alerts, row count anomaly detection)
- **Monitoring**: Databricks DQ rules + alerting to Slack

### Lineage & Cataloging

- **Lineage**: Unity Catalog automatic lineage tracking
- **Cataloging**: All tables tagged with domain, owner, sensitivity, refresh cadence
- **PII**: Classified at silver layer; masked for non-privileged consumers
- **Purview**: Unity Catalog publishes metadata to Purview for estate-wide visibility

### Ingestion Technology Map

| Pattern | Technology | Use Case |
| ------- | ---------- | -------- |
| Batch (relational) | Auto Loader / Extract API | Odoo PG daily extracts to Bronze |
| Streaming | Event Hubs | Real-time operational events |
| Relational federation | Lakehouse Federation | Live queries against Odoo PG without extraction |
| External APIs | n8n workflows → ADLS | Third-party data landing |

### Serving & Consumption

Gold-layer data products are served through a two-stage model:

1. **Databricks SQL** — concurrency-optimized warehouse for analyst and service queries
2. **Power BI semantic models** — published from Databricks SQL, consumed in Fabric dashboards and Copilot experiences

Business users access Power BI dashboards and Copilot in Fabric. They never query Databricks directly. Superset remains supplemental for platform-internal operational dashboards only.

---

## 5. Cost Controls

| Control | Mechanism |
|---------|-----------|
| Cluster policies | Max node count, auto-termination (30 min idle) |
| Spot instances | Use for non-critical batch jobs (silver → gold) |
| Storage tiering | Bronze → cool after 90 days, archive after 1 year |
| Query governance | Databricks SQL warehouse with auto-stop |
| Budget alerts | Azure Cost Management alerts at 80% / 100% thresholds |
| Reservation | Consider 1-year reserved DBU commitment once usage stabilizes |

### Estimated Monthly Cost Envelope

| Component | Estimate |
|-----------|---------|
| Databricks workspace (interactive + jobs) | $200-400 |
| ADLS Gen2 storage (hot + cool) | $20-50 |
| Databricks SQL warehouse | $100-200 |
| Total | $320-650/mo |

*Estimates based on single-developer, low-volume initial deployment.*

---

## 6. ML/MLOps Path

### Current State

No ML models in production. Foundry agents use Azure OpenAI (GPT-4.1) for
inference, not custom-trained models.

### Target State (Deferred)

| Capability | Tool | Timeline |
|-----------|------|----------|
| Feature engineering | Databricks Feature Store | Phase 3 |
| Model training | Databricks MLflow | Phase 3 |
| Model registry | Unity Catalog + MLflow | Phase 3 |
| Model serving | Databricks Model Serving | Phase 3 |
| Experiment tracking | MLflow | Phase 3 |
| A/B testing | Custom (Databricks notebooks) | Phase 4 |

### ML Use Cases (Planned)

| Use Case | Input | Output | Priority |
|---------|-------|--------|----------|
| Revenue forecasting | `gold.revenue_dashboard` | Monthly revenue prediction | Medium |
| Customer churn | `gold.customer_360` | Churn probability score | Low |
| Expense categorization | Document Intelligence OCR | Expense category + amount | High |
| Tax anomaly detection | `gold.bir_tax_summary` | Anomaly flags | Medium |

---

## 7. Operational Model

### RACI

| Activity | Platform Lead | Engineering Lead | Data Analyst |
|----------|--------------|-----------------|-------------|
| Cluster management | A | R | — |
| Pipeline development | I | R/A | C |
| Data quality rules | A | R | C |
| Dashboard creation | I | C | R |
| Cost monitoring | R/A | I | — |
| Schema changes | A | R | I |
| Access provisioning | R/A | I | — |

R = Responsible, A = Accountable, C = Consulted, I = Informed

### Persona Enablement

| Persona | Primary Tool | Access Level | Enablement |
|---------|-------------|-------------|-----------|
| Platform lead | Databricks workspace + Azure portal | Admin | Self-serve |
| Engineering lead | Databricks workspace + notebooks | Contributor | Guided |
| Data analyst | Databricks SQL + Power BI | Reader + SQL | Training path (see learning model) |
| Business user | Power BI dashboards | Viewer | Dashboard walkthrough |

---

## 8. Databricks Marketing Accelerator References

These are **external reference patterns** — pre-built notebook accelerators from Databricks.
They are starting points for the marketing/ad-tech lane, **not** canonical product architecture.
Canonical authority remains: Odoo (SoR), platform (SSOT), Databricks (data-intelligence),
Foundry (agents), Azure Boards (execution coordination).

| Accelerator | Use Case | Maps To |
|-------------|----------|---------|
| [Media Mix Modeling (MMM)](https://www.databricks.com/solutions/accelerators/media-mix-modeling) | Channel-level spend optimization, scenario simulation, cross-channel unification | FEAT-004-03 Campaign measurement cloud |
| [Multi-Touch Attribution (MTA)](https://www.databricks.com/solutions/accelerators/multi-touch-attribution) | Journey/channel attribution, real-time dashboarding | FEAT-004-03 Campaign measurement cloud |
| [Customer Lifetime Value (CLV)](https://www.databricks.com/solutions/accelerators/customer-lifetime-value) | Retention, acquisition prioritization, high-value customer modeling | FEAT-004-02 Customer 360 intelligence fabric |
| [Sales Forecasting and Attribution](https://www.databricks.com/solutions/accelerators/sales-forecasting) | Linking ad metrics and sales data, batch/streaming ad+sales fusion | FEAT-004-03 Campaign measurement cloud |
| [Meta Conversions API](https://www.databricks.com/blog/activate-first-party-data-meta-conversions-api-databricks) | First-party activation from lakehouse to Meta ad platform | FEAT-007-03 TBWA/SMP packaging |

**Recommended sequencing** (measure → attribute → forecast → segment → activate):

1. MMM — channel-level measurement baseline
2. MTA — granular journey attribution
3. Sales Forecasting + Attribution — connecting ad spend to revenue
4. CLV — customer segmentation and retention modeling
5. Meta CAPI — governed activation back to ad platforms

**Integration with medallion architecture**:
- Bronze: ad platform data (Meta, Google Ads, etc.) via n8n or connector
- Silver: conformed marketing fact tables (impressions, clicks, conversions, spend)
- Gold: attribution models, CLV scores, MMM outputs → Power BI

See [marketing_analytics_reference_model.md](marketing_analytics_reference_model.md) for
detailed accelerator evaluation and adoption criteria.

---

## 9. Databricks Production-Readiness Benchmark

Databricks "production ready" is a benchmark for production discipline, not a blanket trust label. A Databricks capability is production-grade in our doctrine only when:

- release maturity is acceptable (GA or Public Preview with stable interface/SLA/support)
- deployment path is codified (IaC, CI/CD, bundle)
- observability/evaluation exists
- rollback/recovery expectations are defined

### Production-readiness lanes

| Lane | Benchmark surface | Assessor skill |
|------|-------------------|----------------|
| Data pipelines | Spark Declarative Pipelines, Jobs/Workflows | `databricks-pipeline-production-readiness` |
| Internal data/AI apps | Databricks Apps (serverless) | `databricks-app-production-readiness` |
| Agents | Agent Framework, Genie | `databricks-agent-production-readiness` |
| Model serving | Model Serving, Unity Catalog models | `databricks-model-serving-production-readiness` |

### Release maturity classification

| Classification | Production use | Doctrine treatment |
|---------------|---------------|-------------------|
| **GA** | Fully supported, production-ready | Canonical baseline |
| **Public Preview** | Allowed with stable interface/SLA/support | Acceptable with conditions |
| **Beta** | Limited support, interface may change | Not acceptable as canonical production baseline |
| **Private Preview** | Invitation-only, no SLA | Not acceptable |
| **Experimental** | No guarantees | Not acceptable |

### Cross-cutting judge

`databricks-production-readiness-judge` validates whether a proposed Databricks surface is mature enough for the canonical stack. It classifies: production-ready, preview-acceptable, or not-production-grade.

See `agents/skills/databricks-*/` and `agent-platform/ssot/learning/databricks_production_ready_skill_map.yaml`.

---

*Last updated: 2026-03-17*
