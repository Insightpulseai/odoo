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

  Databricks SQL    Tableau Cloud    Superset     Odoo (enrichment fields)
  (ad-hoc queries)  (exec dashboards) (ops metrics) (draft docs, forecasts)
```

**Invariant**: The analytical lake is never the source of truth for operational data.
Reverse ETL is bounded, typed, and contract-governed.

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
| Customer 360 | Tableau Cloud, Superset | Daily |
| Revenue Dashboard | Tableau Cloud | Daily |
| BIR Tax Summary | `ipai_bir_tax_compliance` (reverse ETL) | Monthly |
| Campaign Performance | Tableau Cloud | Weekly |
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
| Data analyst | Databricks SQL + Tableau Cloud | Reader + SQL | Training path (see learning model) |
| Business user | Tableau Cloud dashboards | Viewer | Dashboard walkthrough |

---

*Last updated: 2026-03-17*
