# Tasks — Lakehouse Control Room

## A) Backlog (Full)

### EPIC A1 — CI / Spec Kit Gates
- [x] Add PR gate workflow to repo(s) consuming Spec Kit
- [ ] Enforce required check on `main`
- [ ] Add CODEOWNERS + templates (org pack)

### EPIC A2 — Ops Schema + RLS
- [x] `ops.runs` table + indexes
- [x] `ops.run_events` append-only table
- [x] `ops.run_artifacts` registry table
- [x] `ops.executors` registry table
- [x] `ops.caps` + `ops.cap_usage` tables
- [x] `ops.routing_matrix` + `ops.alert_rules` + `ops.notifications` tables
- [x] `ops.signal_weights` + `ops.signals` + `ops.run_scores` tables
- [ ] RLS policies (org/project/env)
- [x] RPC: `claim_run(executor_id)` with lease token + timeout
- [x] RPC: `heartbeat_run(run_id, phase)`
- [x] RPC: `start_run(run_id)`
- [x] RPC: `complete_run(run_id)`
- [x] RPC: `fail_run(run_id, error_code, error_message, error_data)`
- [x] RPC: `cancel_run(run_id)`
- [x] RPC: `compute_run_score(run_id)`
- [x] RPC: `cap_allow(cap_key, amount)`
- [x] RPC: `requeue_stale_runs(stale_minutes)`

### EPIC A3 — Lakehouse Executor
- [ ] Edge Function executor skeleton
- [ ] Phase handler registry (ingest/validate/transform/publish/query)
- [ ] Idempotency + retries
- [ ] Artifact upload + registration
- [ ] Lease renewal / timeout handling
- [ ] Structured logging + event emission
- [ ] Docker worker mode (heavier compute)

### EPIC A4 — Medallion Pipelines
- [ ] Pipeline spec format (YAML/JSON)
- [ ] Bronze landing (raw)
- [ ] Silver normalization
- [ ] Gold marts/views
- [ ] Data quality checks (row counts, schema drift, null thresholds)
- [ ] Deterministic hashing for outputs

### EPIC A5 — SQL + BI
- [ ] SQL run phase: store text + results manifest
- [ ] Result preview artifact (sample rows)
- [ ] Superset dataset publish pipeline (gold)
- [ ] Permissions mapping (RLS ↔ BI roles)

### EPIC A6 — Odoo-Live Integration
- [ ] Connection contract for Odoo DB
- [ ] Table grouping plan (finance/ops/masterdata)
- [ ] Freshness SLA monitors
- [ ] Backfill + replay strategy
- [ ] Cutover checklist (prod)

---

## B) Routing Matrix (Ownership / Execution)

| Area | Primary Owner | Secondary | Execution Surface |
|---|---|---|---|
| Spec + PRD | @spec-owners | @platform-owners | GitHub PR + Spec Kit gate |
| Ops schema + RLS | @data-owners | @security-owners | Supabase migrations + CI |
| Executor runtime | @platform-owners | @data-owners | Edge Functions + DO workers |
| Pipelines/Medallion | @data-owners | @platform-owners | Executor phases |
| BI publishing | @product-owners | @data-owners | Superset + views |
| Odoo ingestion | @data-owners | @platform-owners | CDC/ingest phase |
| Security + secrets | @security-owners | @platform-owners | CI + secret management |

---

## C) CAPS Report (Capabilities Coverage vs Databricks)

Legend: ✅ supported, ⏳ planned, ❌ not planned

| Capability | Databricks | Our Open Stack Target | MVP | V1 | V2 |
|---|---|---|---|---|---|
| Jobs/Workflows | Native | Control Room Runs/Phases | ✅ | ✅ | ✅ |
| Pipeline authoring | DLT | YAML/JSON pipeline specs + dbt optional | ✅ | ✅ | ✅ |
| SQL Warehouse | DBSQL | Trino / Postgres+FDW | ✅ | ✅ | ✅ |
| Table format | Delta | Delta-rs or Iceberg | ✅ | ✅ | ✅ |
| Notebooks | Native | JupyterHub / markdown+SQL | ❌ | ⏳ | ✅ |
| Catalog/Governance | Unity | OpenMetadata/DataHub + policies | ❌ | ⏳ | ⏳ |
| Dashboards | Native | Superset / Metabase | ✅ | ✅ | ✅ |
| NLQ (Genie) | Native | WrenAI-style templates + RAG | ❌ | ⏳ | ⏳ |
| ML tracking | MLflow | MLflow OSS | ❌ | ⏳ | ✅ |
| Model serving | Native | BentoML/KServe | ❌ | ⏳ | ⏳ |
| Lineage | Native | OpenLineage + Metadata | ❌ | ⏳ | ✅ |

---

## D) "Control Room ↔ Executor" Acceptance Criteria (Gate to V1)

- [x] Ops schema deployed with runs, events, artifacts tables
- [x] RPCs for run lifecycle (claim, start, complete, fail, cancel)
- [ ] A run can be created with 3+ phases and completes end-to-end
- [ ] Every phase emits start/progress/finish events
- [ ] Artifacts are registered with sha256 and immutable URLs
- [ ] Re-running the same run definition produces identical output hashes (where deterministic)
- [ ] Lease prevents double execution under concurrent executors
- [ ] RLS prevents cross-project visibility of runs/artifacts

---

## E) Current Sprint Tasks

### Sprint 1: Executor Foundation
- [ ] Create Edge Function executor skeleton (`supabase/functions/executor/`)
- [ ] Implement phase handler interface
- [ ] Add ingest phase handler (MVP)
- [ ] Add validate phase handler (schema checks)
- [ ] Add transform phase handler (SQL-based)
- [ ] Add publish phase handler (artifact registration)
- [ ] Integration tests for executor loop

### Sprint 2: Pipeline Specs
- [ ] Define pipeline YAML schema
- [ ] Create reference pipeline: `odoo_ingest_bronze`
- [ ] Create reference pipeline: `bronze_to_silver`
- [ ] Create reference pipeline: `silver_to_gold`
- [ ] Pipeline validation in CI

---

## F) Task Status Legend

- Lane: DEV (Development), OPS (Operations), SEC (Security)
- Priority: P1 (Critical), P2 (High), P3 (Medium), P4 (Low)
- Status: `[ ]` Pending, `[x]` Complete, `[-]` Blocked
