# Lakehouse -- Task Checklist

> **Version**: 1.0.0
> **Status**: Active
> **Last Updated**: 2026-03-08
> **Spec Bundle**: `spec/lakehouse/`

---

## Phase 0: Infrastructure Scaffold

- [x] Create `infra/lakehouse/compose.lakehouse.yml` with all services
- [x] Configure Spark Master + Worker (bitnami/spark:3.5)
- [x] Configure Trino with Delta Lake and PostgreSQL catalogs
- [x] Configure MinIO for S3-compatible object storage
- [x] Configure MLflow with PostgreSQL backend and MinIO artifact store
- [x] Configure n8n with PostgreSQL backend
- [x] Create PostgreSQL init script (`01_init_databases.sql`)
- [x] Create `.env.example` with all required variables
- [x] Write `infra/lakehouse/README.md` with architecture diagram and quick start
- [x] Add health checks to all Docker services

## Phase 1: Contract System

- [x] Implement `DeltaContract` dataclass in `src/lakehouse/contracts.py`
- [x] Implement `ColumnSpec` dataclass with name, type, nullable, description
- [x] Implement `load_contracts()` to parse YAML files from `contracts/delta/`
- [x] Implement `generate_trino_ddl()` to produce CREATE TABLE SQL from contracts
- [x] Implement `DeltaContract.validate()` with partition and primary key checks
- [x] Implement `PipelineConfig` loader in `src/lakehouse/config.py`
- [x] Implement env var expansion (`${VAR}`, `${VAR:-default}`) in config
- [x] Create `src/lakehouse/__init__.py` with public API exports
- [x] Create `scripts/lakehouse/validate_contracts.py` (CI validator, exit codes)
- [x] Create `scripts/lakehouse/create_delta_tables_trino.sql` (hand-written DDL)
- [x] Create `scripts/lakehouse/coverage_audit.py` with text/JSON output
- [x] Create `scripts/lakehouse/mirror_gold_to_supabase.py` with Trino and Supabase clients
- [ ] Restore 4 contract YAML files to `contracts/delta/`:
  - [ ] `bronze_raw_pages.yaml`
  - [ ] `silver_normalized_docs.yaml`
  - [ ] `gold_chunks.yaml`
  - [ ] `gold_embeddings.yaml`

## Phase 2: Pipeline Implementation

- [ ] Implement Bronze crawler (web page fetcher, writes to MinIO)
- [ ] Implement Silver normalizer (HTML-to-markdown, metadata extraction)
- [ ] Implement Gold chunker (semantic splitting, positional metadata)
- [ ] Implement Gold embedder (vector generation with model tracking)
- [ ] Create n8n workflow: trigger Bronze crawl
- [ ] Create n8n workflow: trigger Silver normalization
- [ ] Create n8n workflow: trigger Gold embedding
- [ ] Create end-to-end integration test (single source through all layers)
- [ ] Validate pipeline templates match contract schemas:
  - [ ] `ops/pipelines/templates/odoo_ingest_bronze.yaml`
  - [ ] `ops/pipelines/templates/bronze_to_silver.yaml`
  - [ ] `ops/pipelines/templates/silver_to_gold.yaml`

## Phase 3: Supabase Gold Mirror

- [ ] Create Supabase migration for `rag.chunks` table
- [ ] Create Supabase migration for `rag.embeddings` table with pgvector column
- [ ] Test `mirror_gold_to_supabase.py` against live Trino instance
- [ ] Test upsert conflict resolution on primary key
- [ ] Create `config/pipeline.yaml` with mirror configuration
- [ ] Schedule mirror job via n8n cron
- [ ] Add mirror monitoring (row count, last sync, error rate)

## Phase 4: MLflow Integration

- [ ] Register embedding model in MLflow
- [ ] Log embedding metrics per pipeline run
- [ ] Tag gold.embeddings rows with MLflow model version
- [ ] Verify model artifacts stored in MinIO (`s3://mlflow/`)
- [ ] Create Superset dashboard for model performance

## Phase 5: CI/CD Gates and Monitoring

- [ ] Create GitHub Actions workflow: `ci-lakehouse-contracts.yml`
- [ ] Create GitHub Actions workflow: `ci-lakehouse-coverage.yml`
- [ ] Create Slack notification for pipeline failures (via n8n)
- [ ] Create Superset dashboard for pipeline health
- [ ] Implement schema drift detection (Trino schema vs contracts)
- [ ] Write runbook for common pipeline failures

## Documentation

- [x] `infra/lakehouse/README.md` -- Stack overview and quick start
- [x] `docs/lakehouse/DATABRICKS_PARITY_MATRIX.md` -- Parity matrix (stub, expanded)
- [x] `docs/portfolio/specs/lakehouse-control-room/prd.md` -- Control Room PRD
- [x] `docs/portfolio/specs/lakehouse-control-room/plan.md` -- Control Room plan
- [x] `spec/lakehouse/constitution.md` -- Non-negotiable rules
- [x] `spec/lakehouse/prd.md` -- Product requirements
- [x] `spec/lakehouse/plan.md` -- Implementation phases
- [x] `spec/lakehouse/tasks.md` -- This task checklist
- [x] `docs/lakehouse/ARCHITECTURE.md` -- Architecture document
- [x] `docs/lakehouse/CONTRACTS.md` -- Contract system documentation
