# Constitution — ADLS ETL + Reverse ETL

> Immutable rules governing data flows between Supabase (SSOT),
> Odoo (SoR), and Azure Data Lake Storage (ADLS Gen2).

---

## Rule 1: System Authority Is Non-Negotiable

| System | Authority | Owns |
|--------|-----------|------|
| **Supabase** | SSOT | Platform/control-plane entities, metadata, workflow state, app-side control tables, operational vector retrieval, agent memory |
| **Odoo** | SoR | ERP entities — accounting, invoicing, projects, tasks, master operational records, finance/operations workflows |
| **ADLS** | Analytical/lake only | Replicated, curated, partitioned, historical, analytical, ML, and interoperability data products |

ADLS is authoritative for **nothing operational**. It is a downstream
consumption surface. No operational system may treat ADLS as source of truth.

## Rule 2: Reverse ETL Is Bounded and Typed

Every reverse ETL flow must be classified as exactly one of:

| Type | Description | Example |
|------|-------------|---------|
| `read_model_refresh` | Update a pre-computed read model in an operational system | Refresh materialized analytics summary in Supabase |
| `enrichment_writeback` | Add derived fields to existing operational records | Append ML-computed risk score to Odoo partner record |
| `scoring_writeback` | Write ML/AI scoring outputs to operational systems | Customer segmentation flag on Supabase user profile |
| `notification_trigger` | Fire an alert or notification based on analytical results | Slack alert when anomaly detected in ADLS pipeline |
| `draft_record_creation` | Create draft (non-posted) records in operational systems | Draft expense document in Odoo from curated ADLS output |

Untyped, generic "sync" flows are prohibited.

## Rule 3: No Overwrite of Authoritative Fields

Reverse ETL must never overwrite authoritative fields in Supabase or Odoo
without an explicit ownership transfer contract registered in
`docs/contracts/REVERSE_ETL_GUARDRAILS.md`.

- Supabase: reverse ETL may write to designated `_enriched` or `_score`
  columns only. Core SSOT columns are read-only from ADLS perspective.
- Odoo: reverse ETL may create draft records or write to designated
  enrichment fields only. Posted accounting entries, approved workflows,
  and master data fields are immutable from ADLS perspective.

## Rule 4: Medallion Architecture Is Mandatory

ADLS storage follows bronze → silver → gold:

| Zone | Purpose | Format |
|------|---------|--------|
| `raw/bronze` | Append-only landing, schema-on-read | Parquet or JSON (source-native) |
| `standardized/silver` | Normalized, deduplicated, typed | Parquet (Delta optional) |
| `curated/gold` | Business-ready datasets, aggregated marts | Parquet (Delta optional) |
| `reverse_etl_exports` | Staged outputs approved for writeback | Parquet or JSON |
| `rejected/quarantine` | Failed records, schema violations | Source format + error metadata |
| `audit/evidence` | Run logs, row counts, watermarks, lineage | JSON + Parquet |

## Rule 5: Every Flow Has a Contract

Every data flow must define:

- Source system and target system
- Authority model (who owns the data)
- Data classification (PII, financial, operational, analytical)
- Cadence (batch schedule or event trigger)
- Idempotency key
- Failure handling (retry, dead-letter, quarantine)
- Replay behavior (safe to re-run?)
- Evidence output (row counts, watermarks, checksums)

Flows without contracts are prohibited.

## Rule 6: No Secrets in Repo

All credentials for Supabase, Odoo, ADLS, and orchestration runtimes
are resolved via Azure Key Vault (`kv-ipai-dev`) + managed identity.
No connection strings, API keys, or tokens in tracked files.

## Rule 7: No Uncontrolled Bidirectional Sync

There is no generic "sync" between Supabase and Odoo. Each direction
has a different authority model:

- Supabase → ADLS: ETL (Supabase is source)
- Odoo → ADLS: ETL (Odoo is source)
- ADLS → Supabase: Reverse ETL (bounded, typed, contract-required)
- ADLS → Odoo: Reverse ETL (bounded, typed, contract-required)
- Supabase → Odoo: Not via ADLS. Direct integration via existing contracts only.
- Odoo → Supabase: Not via ADLS. Direct integration via existing contracts only.

## Rule 8: Databricks Is Optional

The architecture is ADLS-first and tool-agnostic. Databricks may be
introduced for silver/gold transforms and ML workloads, but is not
mandatory. If introduced, it owns the compute layer only — never the
storage authority.

## Rule 9: Odoo Extraction Uses Extract API or DB Replica

Odoo data is extracted via:

1. **Extract API** (preferred) — purpose-built for ETL, large-scale
2. **JSON-2 API** — for smaller, targeted extractions
3. **DB replica** (read-only PostgreSQL replica) — for bulk historical loads

Never extract via XML-RPC in production ETL pipelines. Never write
directly to Odoo's PostgreSQL database from external systems.

## Rule 10: Supabase CDC Must Be Explicit

If Supabase change data capture is used, it must be via:

1. **Supabase Realtime** (postgres changes) — for event-driven CDC
2. **Logical replication** — for bulk CDC
3. **Periodic full/incremental export** — for batch ETL

CDC mechanism must be documented per flow. Emulated CDC (timestamp-based
incremental) must be explicitly labeled as such.
