# Lakehouse -- Implementation Plan

> **Version**: 1.0.0
> **Status**: Active
> **Last Updated**: 2026-03-08
> **Spec Bundle**: `spec/lakehouse/`

---

## Phase 0: Infrastructure Scaffold -- DONE

Delivered the foundational Docker Compose stack and supporting configuration.

**Deliverables**:
- [x] `infra/lakehouse/compose.lakehouse.yml` -- Docker Compose with Spark, Trino, MinIO, MLflow, n8n, PostgreSQL
- [x] `infra/lakehouse/trino/catalog/delta.properties` -- Trino Delta Lake connector pointing to MinIO
- [x] `infra/lakehouse/trino/catalog/postgresql.properties` -- Trino PostgreSQL connector
- [x] `infra/lakehouse/init/postgres/01_init_databases.sql` -- Init script for `mlflow`, `n8n` databases and `rag`, `gold`, `runtime` schemas
- [x] `infra/lakehouse/.env.example` -- Environment variable template
- [x] `infra/lakehouse/README.md` -- Stack overview, quick start, service ports, troubleshooting

**Verification**: `docker compose -f infra/lakehouse/compose.lakehouse.yml config` validates the compose file.

---

## Phase 1: Contract System -- DONE

Delivered the contract-driven schema management layer.

**Deliverables**:
- [x] `src/lakehouse/contracts.py` -- `DeltaContract` dataclass, `load_contracts()`, `generate_trino_ddl()`
- [x] `src/lakehouse/config.py` -- `PipelineConfig` loader with env var substitution
- [x] `src/lakehouse/__init__.py` -- Public API (`load_pipeline_config`, `load_contracts`, `DeltaContract`)
- [x] `scripts/lakehouse/validate_contracts.py` -- CI-ready contract validator (exit code 0/1)
- [x] `scripts/lakehouse/create_delta_tables_trino.sql` -- Hand-written Trino DDL for all 4 tables
- [x] `scripts/lakehouse/coverage_audit.py` -- Coverage audit with text and JSON output modes
- [x] `scripts/lakehouse/mirror_gold_to_supabase.py` -- Gold-to-Supabase mirror script with Trino + Supabase REST clients

**Verification**: `python scripts/lakehouse/validate_contracts.py` exits 0 when contracts are present and valid.

**Note**: The 4 contract YAML files (`contracts/delta/bronze_raw_pages.yaml`, `silver_normalized_docs.yaml`, `gold_chunks.yaml`, `gold_embeddings.yaml`) existed on a prior branch and must be restored for this system to function end-to-end. The Trino DDL in `scripts/lakehouse/create_delta_tables_trino.sql` documents the canonical schemas.

---

## Phase 2: Pipeline Implementation -- IN PROGRESS

Build the actual Bronze crawler, Silver normalizer, and Gold embedder.

**Deliverables**:
- [ ] Bronze crawler: fetch web pages, write raw content to MinIO via Spark/Delta
- [ ] Silver normalizer: parse HTML to markdown, extract metadata, deduplicate
- [ ] Gold chunker: split documents into semantic chunks with positional metadata
- [ ] Gold embedder: generate vector embeddings using a tracked MLflow model
- [ ] Pipeline orchestration: n8n workflows to trigger Bronze, Silver, Gold stages
- [ ] End-to-end test: single source crawled through all three layers

**Pipeline Templates** (already defined, need runtime implementation):
- `ops/pipelines/templates/odoo_ingest_bronze.yaml` -- Odoo PostgreSQL to Bronze
- `ops/pipelines/templates/bronze_to_silver.yaml` -- Bronze to Silver transforms
- `ops/pipelines/templates/silver_to_gold.yaml` -- Silver to Gold aggregations

**Dependencies**: Phase 0 (Docker stack running), Phase 1 (contracts loaded).

---

## Phase 3: Supabase Gold Mirror -- PLANNED

Connect the gold layer to Supabase for pgvector search.

**Deliverables**:
- [ ] Test `scripts/lakehouse/mirror_gold_to_supabase.py` against live Trino + Supabase
- [ ] Create Supabase tables (`rag.chunks`, `rag.embeddings`) with pgvector columns
- [ ] Verify upsert semantics and conflict resolution
- [ ] Add incremental sync with configurable lookback window
- [ ] Create `config/pipeline.yaml` with mirror configuration
- [ ] Schedule mirror via n8n cron (e.g., every 4 hours)
- [ ] Add monitoring: mirror row count, last sync timestamp, error rate

**Dependencies**: Phase 2 (gold tables populated with real data).

---

## Phase 4: MLflow Integration -- PLANNED

Wire MLflow into the embedding pipeline for model version tracking.

**Deliverables**:
- [ ] Register embedding models in MLflow (model name, version, hyperparameters)
- [ ] Log embedding metrics per run (dimensions, throughput, quality scores)
- [ ] Store model artifacts in MinIO (`s3://mlflow/`)
- [ ] Tag gold embeddings with `model` and `model_version` from MLflow
- [ ] Add MLflow health check to pipeline validation
- [ ] Create Superset dashboard for model performance metrics

**Dependencies**: Phase 2 (embedder writing to gold), MLflow service running (Phase 0).

---

## Phase 5: CI/CD Gates and Monitoring -- PLANNED

Add automated quality gates and operational monitoring.

**Deliverables**:
- [ ] GitHub Actions workflow: validate contracts on every PR
- [ ] GitHub Actions workflow: run coverage audit on schedule
- [ ] Alerting: notify on pipeline failures (via n8n to Slack)
- [ ] Dashboard: Superset dashboard for pipeline health (run counts, durations, error rates)
- [ ] Data quality gates: automated checks at each layer transition
- [ ] Schema drift detection: compare Trino schema against contracts
- [ ] Documentation: runbook for common pipeline failures

**Dependencies**: Phases 2-4 (pipelines running in production).

---

## Risk Register

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Contract YAML files missing from branch | High | Known | Restore from DDL in `create_delta_tables_trino.sql` |
| Spark memory limits on single droplet | Medium | Medium | Tune `SPARK_WORKER_MEMORY`, consider dedicated compute node |
| Trino Delta connector compatibility | Medium | Low | Pin Trino version, test with MinIO path-style access |
| Supabase mirror rate limits | Low | Low | Batch upserts, configurable `batch_size` in config |
| MLflow artifact storage quota | Low | Low | Prune old experiments, monitor MinIO usage |
