# Tasks — ADLS ETL + Reverse ETL

> Task breakdown for the canonical data flow architecture.

---

## T1 — Spec and Contract

- [x] **T1.1** Create spec bundle `spec/adls-etl-reverse-etl/`
- [x] **T1.2** Create `docs/contracts/DATA_AUTHORITY_CONTRACT.md`
- [x] **T1.3** Create `docs/contracts/REVERSE_ETL_GUARDRAILS.md`
- [x] **T1.4** Create `ssot/integrations/adls-etl-reverse-etl.yaml`
- [x] **T1.5** Create `docs/architecture/ADLS_ETL_REVERSE_ETL_ARCHITECTURE.md`
- [ ] **T1.6** Register contracts in `docs/contracts/PLATFORM_CONTRACTS_INDEX.md`

## T2 — ADLS Infrastructure

- [x] **T2.1** Provision ADLS Gen2 storage account (`adlsipaidev`)
- [x] **T2.2** Create container/filesystem structure (6 zones)
- [ ] **T2.3** Configure storage RBAC (ETL-write, analytics-read, reverse-ETL-read)
- [ ] **T2.4** Add ADLS credentials to Key Vault (`kv-ipai-dev`)
- [ ] **T2.5** Configure managed identity for ETL compute → ADLS
- [x] **T2.6** Provision mandatory Azure Databricks workspace (`dbw-ipai-dev`)
- [x] **T2.7** Enforce mandatory Delta Lake format (UniForm on ADLS Gen2)

## T3 — Supabase → ADLS Bronze

- [x] **T3.1** Inventory Supabase tables for ETL (priority: auth.users, platform_events, ops.task_queue)
- [x] **T3.2** Select CDC mechanism: supabase/etl (Rust CDC, pgoutput logical replication) + JDBC batch bootstrap
- [x] **T3.3** Build bronze landing pipeline (Supabase → ADLS raw/) — `ingest_supabase.py` + Databricks notebook + DAB job
- [x] **T3.4** Implement watermark tracking — uses existing `update_watermark()` in `bronze/ingest.py`
- [ ] **T3.5** Implement quarantine path for failed records
- [ ] **T3.6** Add run logging and evidence output
- [x] **T3.7** Create `iceberg` container on `stipaidevlake` ADLS Gen2 storage account
- [x] **T3.8** Create supabase/etl Docker Compose service definition for VM deployment
- [x] **T3.9** Create PG logical replication setup script (slot + publication)
- [x] **T3.10** Create Databricks secret scope setup script for Supabase PG credentials

## T4 — Odoo → ADLS Bronze

- [ ] **T4.1** Inventory Odoo models for ETL (priority: account.move, project.project, hr.employee)
- [ ] **T4.2** Build Extract API client for bulk extraction
- [ ] **T4.3** Build bronze landing pipeline (Odoo → ADLS raw/)
- [ ] **T4.4** Implement watermark tracking (using `write_date`)
- [ ] **T4.5** Implement quarantine path for failed records
- [ ] **T4.6** Add run logging and evidence output
- [ ] **T4.7** Decide: DB replica for initial historical load?

## T5 — Silver Normalization

- [ ] **T5.1** Build bronze → silver transforms (dedup, type casting, null handling)
- [ ] **T5.2** Implement cross-source entity resolution (Supabase user ↔ Odoo employee)
- [ ] **T5.3** Add schema validation (reject → quarantine)
- [ ] **T5.4** Partition silver by date and source
- [x] **T5.5** Use Azure Databricks for all complex transformations

## T6 — Gold Curation

- [ ] **T6.1** Build finance gold mart (budget, actuals, variance)
- [ ] **T6.2** Build projects gold mart (portfolio, resource, timeline)
- [ ] **T6.3** Build compliance gold mart (BIR filing status, deadlines)
- [ ] **T6.4** Build platform gold mart (user activity, events)
- [ ] **T6.5** Build ML feature tables for Azure AI
- [ ] **T6.6** Connect Power BI to Unity Catalog / Gold layer
- [ ] **T6.7** Validate BI dashboards against gold marts

## T7 — Reverse ETL

- [ ] **T7.1** Build scoring writeback pipeline (ML scores → Supabase)
- [ ] **T7.2** Build enrichment writeback pipeline (forecasts → Odoo analytic fields)
- [ ] **T7.3** Build materialized summary refresh (aggregates → Supabase)
- [ ] **T7.4** Implement field-level write guards per REVERSE_ETL_GUARDRAILS.md
- [ ] **T7.5** Implement idempotency enforcement (dedup key check)
- [ ] **T7.6** Implement dead-letter queue for failed writebacks
- [ ] **T7.7** Add writeback evidence (counts, field audit, errors)
- [x] **T7.8** Use Azure Functions or Databricks Jobs for reverse ETL orchestration

## T8 — Deprecate Legacy Paths

- [ ] **T8.1** Inventory existing Supabase export jobs
- [ ] **T8.2** Inventory existing Odoo extraction scripts
- [ ] **T8.3** Redirect consumers to ADLS gold layer
- [ ] **T8.4** Deprecate and remove legacy duplicate paths
- [ ] **T8.5** Evidence: consumer migration checklist

## T9 — Observability

- [ ] **T9.1** Implement schema drift detection
- [ ] **T9.2** Implement per-flow evidence artifacts
- [ ] **T9.3** Build production validation checklist
- [ ] **T9.4** Add alerting for pipeline failures
- [ ] **T9.5** Add lineage tracking per flow

---

## Dependency Map

```
T1 (spec/contract) ──► T2 (ADLS infra)
T2 ──► T3 (Supabase bronze) + T4 (Odoo bronze)
T3 + T4 ──► T5 (silver)
T5 ──► T6 (gold)
T6 ──► T7 (reverse ETL)
T7 ──► T8 (deprecate legacy)
T2–T8 ──► T9 (observability — runs in parallel from T3 onward)
```
