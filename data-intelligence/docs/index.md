# Data Intelligence Operating Model

## Purpose

Define the canonical data platform operating model for the IPAI platform, benchmarked against the Databricks + Fabric data intelligence reference architecture.

This document covers lakehouse architecture, data ingestion, governance, real-time and batch processing, BI consumption, and AI-ready data foundations — the data-platform equivalent of what SAP on Azure provides for ERP workloads.

## Scope

- Lakehouse architecture (medallion: Bronze → Silver → Gold → Platinum)
- Data ingestion patterns (JDBC extract, CDC, streaming)
- Data governance (Unity Catalog, lineage, access control)
- BI consumption (Power BI primary, Superset supplemental)
- Real-time and batch processing (DLT pipelines, Spark jobs)
- AI-ready data (feature stores, embeddings, training datasets)

Out of scope:
- AI model operations (see `platform/docs/ai-platform/`)
- Odoo ERP business logic (see `docs/odoo-on-azure/runtime/`)
- CI/CD and engineering workflow (see `agents/docs/engineering/`)

## When to Use This

- Designing or modifying data pipelines
- Adding a new data source or ingestion pattern
- Reviewing data governance posture
- Planning BI dashboard architecture
- Building AI-ready datasets from operational data

## Benchmark: Databricks + Fabric Data Intelligence

| Microsoft/Databricks Capability | IPAI Equivalent | Status |
|---|---|---|
| Databricks workspace | `dbw-ipai-dev` (Southeast Asia) | Operational |
| Unity Catalog | Catalog: `ipai_dev` | Scaffold |
| DLT pipelines | Pipeline definitions in `data-intelligence/` | Scaffold |
| Medallion architecture | Bronze → Silver → Gold → Platinum | Design |
| JDBC/CDC ingestion | Databricks JDBC extract from PostgreSQL | Design |
| Fabric mirroring | `pg-ipai-odoo` → Fabric OneLake | Design |
| Power BI consumption | Power BI (primary BI surface) | Scaffold |
| Superset (supplemental) | `ipai-superset-dev` ACA app | Operational |
| Feature store | Not started | Planned |

## Architecture / Concepts

### Medallion Architecture

```
Source Systems (Odoo PG, APIs, files)
  └→ Bronze (raw ingestion, append-only)
       └→ Silver (cleaned, deduplicated, typed)
            └→ Gold (business-level aggregates, dimensions, facts)
                 └→ Platinum (ML features, embeddings, training sets)
```

| Layer | Storage | Governance | Consumers |
|---|---|---|---|
| Bronze | Delta Lake (ADLS) | Raw, schema-on-read | Data engineers |
| Silver | Delta Lake (ADLS) | Cleaned, Unity Catalog | Data engineers, analysts |
| Gold | Delta Lake (ADLS) | Business semantics, row-level security | Power BI, Superset, analysts |
| Platinum | Delta Lake / Feature Store | ML-ready, versioned | AI platform, agents, models |

### Ingestion Patterns

| Pattern | Source | Method | Frequency |
|---|---|---|---|
| JDBC extract | Odoo PostgreSQL (`pg-ipai-odoo`) | Databricks JDBC connector | Scheduled (hourly/daily) |
| Fabric mirroring | Odoo PostgreSQL | Fabric OneLake mirroring | Near-real-time |
| API ingestion | External APIs (n8n, webhooks) | DLT pipeline | Event-driven |
| File ingestion | Azure Storage, Document Intelligence | DLT pipeline | On-arrival |

**Note**: Supabase ETL is deprecated (Private Alpha, self-hosted N/A). Use Databricks JDBC extract instead.

### Data Governance

- **Unity Catalog** (`ipai_dev`): Schema-level access control, column masking, row filters
- **Lineage**: Automatic lineage tracking through DLT pipelines
- **Catalog naming**: `ipai_dev.{schema}.{table}` (e.g., `ipai_dev.bronze.odoo_sale_order`)
- **Access control**: Workspace groups mapped to Unity Catalog permissions

### BI Consumption

| Surface | Role | Authority |
|---|---|---|
| Power BI | Primary mandatory business-facing reporting | Canonical |
| Superset | Supplemental operational dashboards | Supplemental only |
| Azure Workbooks | Platform/infra operational visibility | Infrastructure |

Power BI connects to Gold-layer Delta tables via Databricks SQL warehouse or Fabric DirectLake.

### AI-Ready Data

- Gold-layer tables provide clean business entities for RAG grounding
- Platinum-layer features feed model training and agent context
- Embeddings stored in Delta Lake, served via AI Search index
- Feature freshness tracked as operational metric

## Prerequisites

- Databricks workspace (`dbw-ipai-dev`) provisioned
- Unity Catalog (`ipai_dev`) configured
- ADLS storage account for Delta Lake
- PostgreSQL source (`pg-ipai-odoo`) accessible via JDBC
- Power BI workspace provisioned

## Procedure / Guidance

### Adding a New Data Source

1. Define ingestion spec in `data-intelligence/`
2. Create DLT pipeline definition
3. Register schema in Unity Catalog
4. Configure access control
5. Add data quality expectations (DLT expectations)
6. Document in this file

### Creating a New BI Dashboard

1. Define Gold-layer tables needed
2. Create/update DLT pipeline to produce Gold tables
3. Grant Power BI service principal read access
4. Build Power BI report against Databricks SQL warehouse
5. Publish to Power BI workspace

### Building AI-Ready Datasets

1. Define Platinum-layer requirements with AI platform team
2. Create feature engineering pipeline (DLT)
3. Version dataset in Unity Catalog
4. Configure AI Search index refresh from Platinum tables
5. Document freshness SLA

## Outputs / Expected State

- Medallion architecture operational (Bronze → Silver → Gold → Platinum)
- All Odoo operational data accessible in lakehouse
- Unity Catalog governing all data assets
- Power BI dashboards connected to Gold layer
- AI-ready datasets feeding agent and model workflows
- Data lineage tracked end-to-end

## Related Documents

- `docs/architecture/ODOO_ON_AZURE_REFERENCE_ARCHITECTURE.md` — Layer 3: Data Layer
- `lakehouse/` — legacy lakehouse code (migration target: `data-intelligence/`)
- `infra/databricks/` — Databricks IaC
- `ssot/azure/odoo_bridge_matrix.yaml` — bridges: `database`, `backup_and_dr`
- `platform/docs/ai-platform/index.md` — AI platform (Foundry benchmark)
- `agents/docs/engineering/index.md` — engineering (SDLC benchmark)

## Evidence / Source of Truth

- Databricks workspace: `dbw-ipai-dev` (Southeast Asia)
- Unity Catalog: `ipai_dev`
- PostgreSQL source: `pg-ipai-odoo` (General Purpose, Fabric mirroring)
- Superset: `ipai-superset-dev` (ACA)
- Power BI: primary BI authority (per `ssot/governance/platform-authority-split.yaml`)

---

*Created: 2026-04-05 | Benchmark: Databricks + Fabric data intelligence | Version: 1.0*
