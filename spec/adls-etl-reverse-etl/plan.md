# Plan — ADLS ETL + Reverse ETL

> Phased implementation plan for the canonical data flow architecture.

---

## System Authority Matrix

| Entity | Authoritative System | ADLS Layer | Reverse ETL Eligible | Reverse ETL Mode |
|--------|---------------------|------------|---------------------|-----------------|
| Users / identities | Supabase (`auth.users`) | bronze → silver → gold | Yes | `scoring_writeback` to `_segment`, `_risk_score` columns |
| App events | Supabase (`platform_events`) | bronze → silver | No | — |
| Platform metadata | Supabase (config tables) | bronze | No | — |
| Workflow state | Supabase (n8n records) | bronze → silver | No | — |
| Vector embeddings | Supabase (pgvector) | bronze | No | — |
| Projects | Odoo (`project.project`) | bronze → silver → gold | Yes | `enrichment_writeback` to forecast fields |
| Tasks | Odoo (`project.task`) | bronze → silver → gold | No | — |
| Journal entries | Odoo (`account.move`) | bronze → silver → gold | No | **Never** — posted entries are immutable |
| Invoices | Odoo (`account.move`) | bronze → silver → gold | No | — |
| BIR filings | Odoo (`bir.tax.return`) | bronze → silver | No | — |
| Employees | Odoo (`hr.employee`) | bronze → silver → gold | No | — |
| Vendors | Odoo (`res.partner`) | bronze → silver → gold | No | — |
| Analytic accounts | Odoo (`account.analytic.account`) | bronze → silver → gold | Yes | `enrichment_writeback` to `x_forecast_*` fields |
| Expense documents | Odoo (`hr.expense`) | bronze → silver → gold | Yes | `draft_record_creation` only |
| ML feature tables | ADLS (computed) | gold | Yes | `scoring_writeback` to Supabase/Odoo enrichment columns |
| AI scoring outputs | Azure AI Foundry | gold | Yes | `scoring_writeback` or `notification_trigger` |
| Dashboard summaries | ADLS (aggregated) | gold | Yes | `read_model_refresh` to Supabase materialized tables |

---

## ADLS Zone Layout

```
adls-ipai-dev/
├── raw/
│   ├── supabase/
│   │   ├── auth_users/          dt=2026-03-13/
│   │   ├── platform_events/     dt=2026-03-13/
│   │   ├── workflow_state/      dt=2026-03-13/
│   │   └── pgvector/            dt=2026-03-13/
│   └── odoo/
│       ├── account_move/        dt=2026-03-13/
│       ├── account_move_line/   dt=2026-03-13/
│       ├── project_project/     dt=2026-03-13/
│       ├── project_task/        dt=2026-03-13/
│       ├── hr_employee/         dt=2026-03-13/
│       ├── res_partner/         dt=2026-03-13/
│       └── bir_tax_return/      dt=2026-03-13/
│
├── standardized/
│   ├── supabase/                (normalized, typed, deduplicated)
│   └── odoo/                    (normalized, typed, deduplicated)
│
├── curated/
│   ├── finance/                 (gold marts: budget, actuals, variance)
│   ├── projects/                (gold marts: portfolio, resource, timeline)
│   ├── compliance/              (gold marts: BIR filings, deadlines)
│   ├── platform/                (gold marts: user activity, events)
│   └── ml_features/             (feature tables for Azure AI)
│
├── reverse_etl_exports/
│   ├── supabase/                (staged writebacks)
│   └── odoo/                    (staged writebacks)
│
├── rejected/
│   └── quarantine/              (failed records + error metadata)
│
└── audit/
    ├── run_logs/                (per-flow execution logs)
    ├── watermarks/              (high-water marks per entity)
    └── lineage/                 (data lineage metadata)
```

---

## Odoo Integration Surfaces (from Odoo 19 Developer Reference)

| Surface | Use in ETL | Use in Reverse ETL |
|---------|-----------|-------------------|
| **Extract API** | Primary: bulk data extraction for bronze landing | — |
| **JSON-2 API** | Secondary: targeted small extractions | Primary: bounded writebacks (draft creation, field enrichment) |
| **XML-RPC / JSON-RPC** | Legacy only — avoid in new pipelines | — |
| **ir.cron** | Trigger scheduled extractions from Odoo side | Trigger scheduled reverse ETL consumption |
| **ORM API** | Internal module logic for reverse ETL consumption | Internal module logic for processing writebacks |
| **Data files (XML/CSV)** | Seed data for mapping tables | — |
| **CLI (`odoo-bin`)** | CI/CD: module install, DB init | — |

---

## Phase 1 — Contract and Topology (Spec-Only)

**Deliverables:**
- `docs/contracts/DATA_AUTHORITY_CONTRACT.md` — system authority matrix
- `docs/contracts/REVERSE_ETL_GUARDRAILS.md` — writeback rules and prohibited paths
- `ssot/integrations/adls-etl-reverse-etl.yaml` — machine-readable flow catalog
- Authority matrix reviewed and approved

**Duration:** Spec pass (this PR)

## Phase 2 — ADLS Infrastructure

**Deliverables:**
- ADLS Gen2 storage account provisioned (`adlsipaidev`)
- Container/filesystem structure created per zone layout
- Azure Key Vault secrets for Supabase and Odoo access
- Managed identity bindings for ETL compute
- Storage RBAC: separate roles for ETL-write, analytics-read, reverse-ETL-read

**Open decisions:**
- Storage account name and region (recommend `southeastasia` to match ACA)
- Delta Lake format: optional for silver/gold, not mandatory
- Databricks workspace: provision only if ML/transform workloads justify it

## Phase 3 — Bronze Ingestion (Supabase)

**Deliverables:**
- Supabase → ADLS bronze pipeline for priority tables
- CDC mechanism selected and documented (Realtime, logical replication, or batch)
- Watermark tracking for incremental loads
- Quarantine path for failed records
- Evidence: row counts, run logs, watermarks per run

**Priority tables:**
1. `auth.users` (identity)
2. `platform_events` (app events)
3. `ops.task_queue` (workflow state)

## Phase 4 — Bronze Ingestion (Odoo)

**Deliverables:**
- Odoo → ADLS bronze pipeline via Extract API
- Mapping tables for Odoo model → ADLS path
- Watermark tracking (using `write_date` or sequence IDs)
- Quarantine path for failed records
- Evidence: row counts, run logs, watermarks per run

**Priority models:**
1. `account.move` + `account.move.line` (finance)
2. `project.project` + `project.task` (projects)
3. `hr.employee` + `res.partner` (master data)

## Phase 5 — Silver Normalization

**Deliverables:**
- Bronze → silver transforms (dedup, type casting, null handling)
- Cross-source entity resolution (Supabase user ↔ Odoo employee/partner)
- Schema validation (reject records that fail type/constraint checks)
- Silver datasets partitioned by date and source

**Compute options (decide in Phase 2):**
- Azure Data Factory mapping data flows
- Databricks notebooks/jobs
- Azure Functions (for small-scale transforms)

## Phase 6 — Gold Curation

**Deliverables:**
- Gold marts for each domain:
  - `finance/` — budget vs. actual, variance, period close status
  - `projects/` — portfolio health, resource utilization, timeline
  - `compliance/` — BIR filing status, deadline adherence
  - `platform/` — user activity, event aggregates, feature adoption
  - `ml_features/` — feature tables for Azure AI scoring
- Power BI connector pointed at Unity Catalog
- BI dashboard validation against gold marts

## Phase 7 — Reverse ETL (Bounded)

**Deliverables:**
- Reverse ETL pipeline for each approved flow
- Writeback validation (field-level guards per REVERSE_ETL_GUARDRAILS.md)
- Idempotency enforcement (dedup key check before write)
- Dead-letter queue for failed writebacks
- Evidence: writeback counts, target field audit, error logs

**Initial approved flows:**
1. ML scoring → Supabase `_risk_score` column
2. Budget forecast → Odoo `x_forecast_*` analytic fields
3. Dashboard summaries → Supabase materialized tables

## Phase 8 — Deprecate Legacy Export Paths

**Deliverables:**
- Inventory existing Supabase exports/jobs that duplicate ADLS pipelines
- Inventory existing Odoo data extraction scripts
- Redirect consumers to ADLS gold layer
- Deprecate and remove legacy duplicate paths
- Evidence: consumer migration checklist

---

## Observability and Evidence

| Artifact | Location | Content |
|----------|----------|---------|
| Run logs | `audit/run_logs/{flow_id}/{dt}/` | Execution status, duration, row counts |
| Watermarks | `audit/watermarks/{entity}.json` | High-water mark per entity per source |
| Schema drift | `audit/evidence/{flow_id}/schema_changes.json` | Detected schema changes |
| Quarantine | `rejected/quarantine/{source}/{entity}/{dt}/` | Failed records + error metadata |
| Lineage | `audit/lineage/{flow_id}.json` | Source → bronze → silver → gold → reverse ETL chain |

---

## Open Decisions

| Decision | Options | Recommendation | Status |
|----------|---------|----------------|--------|
| Databricks required? | Yes / No | Optional — introduce only for ML and complex transforms | Open |
| Delta Lake format? | Mandatory / Optional | Optional for silver/gold — Parquet is sufficient baseline | Open |
| Reverse ETL orchestrator | Azure Functions / Data Factory / Databricks jobs | Azure Functions for simplicity; Data Factory for complex flows | Open |
| Supabase CDC mechanism | Realtime / logical replication / batch | Batch (incremental) for Phase 3; Realtime for Phase 8+ | Open |
| Odoo extraction method | Extract API / JSON-2 API / DB replica | Extract API (primary); DB replica for initial historical load | Open |
| ADLS region | `southeastasia` / other | `southeastasia` to co-locate with ACA | Open |
