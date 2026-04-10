# ADLS ETL + Reverse ETL Architecture

> Canonical architecture for data flows between Supabase (SSOT),
> Odoo (SoR), and Azure Data Lake Storage (ADLS Gen2).
>
> Spec: `spec/adls-etl-reverse-etl/`
> Contracts: `docs/contracts/DATA_AUTHORITY_CONTRACT.md`,
>            `docs/contracts/REVERSE_ETL_GUARDRAILS.md`
> SSOT: `ssot/integrations/adls-etl-reverse-etl.yaml`

---

## 1. System Authority Model

```
Supabase (SSOT)              Odoo (SoR)
  Platform control-plane       ERP operations
  App metadata                 Accounting / invoicing
  Workflow state               Projects / tasks
  Vector embeddings            BIR tax compliance
  Agent memory                 Employees / vendors
  Auth identity                Analytic accounts

                    ↓ ETL ↓

              ADLS Gen2 (Analytical Lake)
              Authoritative for nothing operational
              Bronze → Silver → Gold

                    ↓ Reverse ETL ↓
                    (bounded, typed, contract-governed)

Supabase enrichment columns    Odoo enrichment fields
Supabase materialized tables   Odoo draft documents
Slack/n8n notifications
```

## 2. Target Enterprise Architecture

```
              AI Agents
           Azure AI Foundry

                 ↑ scoring / embeddings

           Databricks / ML (optional)
              ADLS Gen2

                 ↑ ETL (Extract API / CDC / batch)

            Odoo (SoR)          Supabase (SSOT)

                 ↑ Reverse ETL (bounded)
            JSON-2 API           Supabase client

           ADLS curated/gold
```

## 3. Odoo Integration Surfaces

The Odoo 18 developer reference defines 7 integration mechanisms:

| Surface | ETL Role | Reverse ETL Role |
|---------|----------|-----------------|
| **Extract API** | Primary: bulk data extraction for bronze | — |
| **JSON-2 API** | Secondary: targeted extractions | Primary: bounded writebacks |
| **XML-RPC / JSON-RPC** | Legacy — avoid in new pipelines | — |
| **ir.cron** | Trigger scheduled extractions | Trigger reverse ETL consumption |
| **ORM API** | Internal module logic | Process writebacks inside Odoo |
| **Data files (XML/CSV)** | Seed data for mapping tables | — |
| **CLI (`odoo-bin`)** | CI/CD: module install, DB init | — |

### Extract API (recommended for ETL)

Purpose-built for large-scale data extraction:

```
Extract request → Parse → Dataset generation → Result retrieval
```

Use for: Odoo → ADLS bronze landing. Preferred over heavy RPC queries.

### JSON-2 API (recommended for reverse ETL)

Modern API with API key authentication:

```
POST /jsonrpc
{
  "model": "account.analytic.account",
  "method": "write",
  "args": [[record_id], {"x_forecast_amount": 150000}]
}
```

Use for: ADLS → Odoo bounded writebacks (enrichment, draft creation).

## 4. ADLS Zone Layout

```
adls-ipai-dev/
├── raw/bronze/
│   ├── supabase/{table}/dt={date}/     Append-only, schema-on-read
│   └── odoo/{model}/dt={date}/         Append-only, schema-on-read
│
├── standardized/silver/
│   ├── supabase/                       Normalized, typed, deduplicated
│   └── odoo/                           Normalized, typed, deduplicated
│
├── curated/gold/
│   ├── finance/                        Budget, actuals, variance
│   ├── projects/                       Portfolio, resource, timeline
│   ├── compliance/                     BIR filing status, deadlines
│   ├── platform/                       User activity, events
│   └── ml_features/                    Feature tables for Azure AI
│
├── reverse_etl_exports/
│   ├── supabase/                       Staged writebacks
│   └── odoo/                           Staged writebacks
│
├── rejected/quarantine/                Failed records + error metadata
│
└── audit/
    ├── run_logs/                       Per-flow execution logs
    ├── watermarks/                     High-water marks per entity
    └── lineage/                        Data lineage metadata
```

## 5. Data Flow Catalog

### ETL Flows (Inbound)

| Flow | Source | Target | Method | Cadence | Key |
|------|--------|--------|--------|---------|-----|
| `supabase_users_to_adls` | Supabase `auth.users` | ADLS bronze | Incremental batch | Daily | `user_id` |
| `supabase_events_to_adls` | Supabase `platform_events` | ADLS bronze | Incremental batch | Hourly | `event_id` |
| `odoo_journal_entries_to_adls` | Odoo `account.move` | ADLS bronze | Extract API | Daily | `id` |
| `odoo_projects_to_adls` | Odoo `project.project` | ADLS bronze | Extract API | Daily | `id` |
| `odoo_employees_to_adls` | Odoo `hr.employee` | ADLS bronze | Extract API | Daily | `id` |
| `odoo_bir_filings_to_adls` | Odoo `bir.tax.return` | ADLS bronze | Extract API | Weekly | `id` |

### Reverse ETL Flows (Outbound)

| Flow | Source | Target | Type | Cadence | Guard |
|------|--------|--------|------|---------|-------|
| `ml_scores_to_supabase` | ADLS gold | Supabase `_risk_score` | `scoring_writeback` | Daily | Enrichment column only |
| `dashboard_refresh_supabase` | ADLS gold | Supabase mat tables | `read_model_refresh` | Daily | Full table replace |
| `forecast_to_odoo_analytic` | ADLS gold | Odoo `x_forecast_*` | `enrichment_writeback` | Weekly | Enrichment fields only |

## 6. Supabase Vector Database Positioning

Supabase pgvector provides operational vector retrieval alongside relational data:

| Use Case | Storage | Why |
|----------|---------|-----|
| Semantic search over app documents | Supabase pgvector | App-native, close to relational data, RLS-governed |
| Agent memory / tool-routing context | Supabase pgvector | Low-latency operational retrieval |
| Operational knowledge retrieval | Supabase pgvector | Tied to app workflows |
| Historical ML feature embeddings | ADLS | Bulk analytical storage, not operational |
| Training dataset embeddings | ADLS → Azure AI | Compute-bound, not operational |

**Rule**: Supabase vector is for **operational RAG** close to app data.
ADLS is for **analytical/historical** embeddings at scale.

## 7. Security Model

| Component | Mechanism |
|-----------|-----------|
| Supabase credentials | Azure Key Vault → managed identity |
| Odoo API tokens | Azure Key Vault → managed identity |
| ADLS access | Storage RBAC + managed identity |
| ETL compute identity | Azure managed identity |
| Reverse ETL compute identity | Azure managed identity |
| Secrets in repo | **Prohibited** |

### Storage RBAC Separation

| Role | Access | Assigned To |
|------|--------|-------------|
| `Storage Blob Data Contributor` | Read/write bronze | ETL pipelines |
| `Storage Blob Data Reader` | Read silver/gold | BI tools, Tableau |
| `Storage Blob Data Reader` | Read reverse_etl_exports | Reverse ETL pipelines |

## 8. Observability

| Artifact | Location | Content |
|----------|----------|---------|
| Run logs | `audit/run_logs/{flow_id}/{dt}/` | Status, duration, row counts |
| Watermarks | `audit/watermarks/{entity}.json` | High-water mark per entity |
| Schema drift | `audit/evidence/{flow_id}/schema_changes.json` | Detected schema changes |
| Quarantine | `rejected/quarantine/{source}/{entity}/{dt}/` | Failed records + errors |
| Lineage | `audit/lineage/{flow_id}.json` | Source → bronze → silver → gold chain |

## 9. Open Decisions

| Decision | Recommendation | Status |
|----------|----------------|--------|
| Databricks required? | Optional — introduce for ML/complex transforms only | Open |
| Delta Lake format? | Optional — Parquet baseline sufficient | Open |
| Reverse ETL orchestrator | Azure Functions (simple) or Data Factory (complex) | Open |
| Supabase CDC mechanism | Incremental batch first; Realtime later | Open |
| Odoo extraction method | Extract API primary; DB replica for historical | Open |
| ADLS region | `southeastasia` (co-locate with ACA) | Open |
