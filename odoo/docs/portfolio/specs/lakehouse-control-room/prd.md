# PRD — Lakehouse Control Room (Databricks-Class, No License)

## Problem Alignment

### Context
We need Databricks-class capabilities (jobs, pipelines, notebooks, SQL, dashboards, governance) without Databricks licensing, and we must operationalize this **after Odoo is live** so Odoo becomes a canonical upstream system for finance/ops/event streams.

### Users
- **Ops/Platform**: needs deterministic runs, incident visibility, rollback, audit trails.
- **Data Engineering**: needs medallion pipelines, scheduling, versioned artifacts, lineage.
- **Product/BI**: needs SQL exploration, dashboards, and shareable results.
- **AI/Agents**: needs a stable executor contract (claim work, run phases, emit events).

### Problems
1. Fragmented orchestration across tools; no single "control plane" for runs and artifacts.
2. Lack of deterministic, auditable pipeline execution tied to Git commits/specs.
3. No unified contract that agents (Claude/Codex/CI) can use to run lakehouse phases.
4. Odoo-live introduces new operational requirements: ingestion reliability, schema stability, and finance-grade auditability.

### Goals (MVP → V1)
- MVP: run orchestration + artifacts + SQL outputs with clear lineage and audit.
- V1: end-to-end Odoo ingestion → bronze/silver/gold → dashboards + AI query layer.

### Success Metrics
- 95% of runs have complete event trails (no missing phases/events).
- Median run enqueue-to-start < 30s for lightweight phases.
- Deterministic rebuild: same inputs + same code commit → identical output hashes.
- Odoo ingestion SLO: < 15 min data freshness for operational tables (V1 target).

---

## Solution Alignment

### Architecture Summary (Control Plane vs Data Plane)

**Control Plane**
- BuildOps Control Room UI (web) + API
- Supabase `ops` schema: `runs`, `run_events`, `artifacts`, `connections`, `secrets_refs`
- GitHub integration: PR gates + run triggers + artifact links

**Data Plane**
- Lakehouse Executor(s): stateless workers (Edge Function + optional Docker workers)
- Object Storage: S3-compatible bucket (artifacts + tables)
- SQL Engine: Trino (preferred) or DuckDB for MVP local mode
- Table Format: Delta Lake (delta-rs) OR Iceberg (MVP chooses one, interface supports both)

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Control Room UI (Next.js)                       │
├─────────────────────────────────────────────────────────────────────┤
│                    Supabase Control Plane (SSOT)                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │ops.runs │  │ops.events│  │artifacts│  │routing │  │  caps   │   │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │
├─────────────────────────────────────────────────────────────────────┤
│                      Executor Contract (OpenAPI)                      │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │
│  │  Spark  │  │  Trino  │  │   dbt   │  │ Python  │  │Notebook │   │
│  │Executor │  │Executor │  │Executor │  │Executor │  │Executor │   │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │
├─────────────────────────────────────────────────────────────────────┤
│                    Data Plane (Object Storage)                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  S3/MinIO  │  Delta Tables  │  Artifacts  │  Logs  │  Lineage │ │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### Control Room ↔ Lakehouse Executor Contract (Authoritative)

#### Entities
- **Run**: a unit of work consisting of ordered phases.
- **Phase**: deterministic step (ingest, validate, transform, publish, profile, etc.).
- **Artifact**: immutable output blob or structured dataset reference.

#### API Surface (logical)
1. `POST /ops/runs` create run with `spec_slug`, `git_sha`, `phases[]`, `input_manifest`
2. `POST /ops/runs/{run_id}/claim` executor claims next runnable phase (leases)
3. `POST /ops/runs/{run_id}/events` append run events (structured)
4. `POST /ops/artifacts` register artifacts with hashes + URLs
5. `POST /ops/runs/{run_id}/complete` finalize with output manifest

> Implementation note: these endpoints can be implemented as Supabase RPCs or Edge Functions, but the *contract* must remain stable.

#### Event Model (minimum)
- `RUN_CREATED`, `PHASE_CLAIMED`, `PHASE_STARTED`, `PHASE_PROGRESS`, `PHASE_FAILED`, `PHASE_SUCCEEDED`, `RUN_SUCCEEDED`, `RUN_FAILED`
- Each event includes: `run_id`, `phase`, `ts`, `level`, `message`, `payload(json)`

#### Idempotency
- `claim` uses lease tokens; repeated calls must not double-execute.
- `events` are append-only; duplicates tolerated via `event_id` de-dupe.
- `artifacts` are immutable; same sha may be referenced by multiple runs.

### Databricks Capability Mapping (Open Stack)

This product targets "capability parity", not brand parity.

| Databricks area | Open equivalent (recommended) | MVP scope |
|---|---|---|
| Jobs/Workflows | Temporal / Dagster / Argo Workflows | ✅ via Control Room runs/phases |
| DLT Pipelines | Dagster assets / dbt + orchestration | ✅ bronze/silver/gold |
| Notebooks | JupyterHub / VSCode web / markdown+SQL blocks | ⏳ optional (M2) |
| SQL Warehouse | Trino / ClickHouse / Postgres+FDW | ✅ Trino or Postgres+FDW MVP |
| Delta Lake | delta-rs / Spark optional | ✅ choose Delta or Iceberg |
| Unity Catalog | OpenMetadata / DataHub + policy layer | ⏳ M3+ |
| MLflow | MLflow OSS | ⏳ M3+ |
| Dashboards | Superset / Metabase | ✅ Superset path |
| Genie/NLQ | WrenAI-style semantic templates + RAG | ✅ integrate later |

### Odoo-Live Integration (V1)
- Ingest: Odoo Postgres → CDC (optional) → bronze
- Transform: bronze → silver normalized → gold marts
- Publish: gold views + Superset datasets + AI query endpoints

### Requirements (Functional)
1. Run lifecycle management (create, claim, execute, emit, complete).
2. Artifact registry with content-addressing and metadata.
3. Pipeline templates: medallion (bronze/silver/gold) + schema checks.
4. SQL outputs: store query text + result manifest + preview samples.
5. Git linkage: every run references `git_sha` and `spec_slug`.
6. Environment separation: dev/stage/prod.

### Requirements (Non-Functional)
- RLS enforcement for all ops tables.
- Structured logs/events (JSON).
- Backpressure + retry with exponential policy.
- Timeouts per phase.
- Minimal cost path for MVP (no always-on heavy clusters).

---

## Launch Readiness

### Release Phases
- **MVP (Control Plane)**: runs/events/artifacts + executor contract + basic pipeline execution
- **V1 (Odoo-Live)**: Odoo ingestion + medallion + Superset datasets + monitoring
- **V2**: notebook UX + catalog/lineage
- **V3**: MLflow + model serving + advanced governance

### Dependencies
- Supabase project + RLS policies
- Object storage bucket + service credentials
- Executor runtime: Edge Function + optional DO docker worker
- CI gate: Spec Kit validation + required checks

### Rollout Plan
- Dev: executor in dry-run mode + small sample datasets
- Stage: real Odoo staging connection + limited tables
- Prod: full ingestion with SLOs and alerting

### Monitoring
- Run success rate by phase
- Queue depth + lease timeouts
- Artifact upload failures
- Odoo ingestion freshness

### Security
- Secrets via vault/env; never in artifacts
- Audit trail: all run events persisted
- Signed artifact URLs or private bucket access

### Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Performance vs Databricks | Medium | Tuning + Trino + AQE |
| Governance complexity | High | Policy-as-code + CI gates |
| Executor reliability | High | Heartbeat + requeue + retry |
| Schema drift | Medium | Contract validation in PR gate |
