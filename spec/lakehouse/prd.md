# Lakehouse -- Product Requirements Document

> **Version**: 1.0.0
> **Status**: Active
> **Last Updated**: 2026-03-08
> **Spec Bundle**: `spec/lakehouse/`

---

## Problem

InsightPulse AI needs Databricks-class data engineering capabilities (medallion pipelines, SQL warehouse, model tracking, vector search) without Databricks licensing costs or cloud vendor lock-in. The platform must support two primary workloads:

1. **RAG Pipeline**: Document crawling, normalization, chunking, and embedding generation for AI-powered search and retrieval.
2. **Analytics Pipeline**: Odoo ERP data ingestion, transformation, and aggregation for business intelligence dashboards.

---

## Goal

Build an OSS Databricks-parity data platform using self-hosted components that implements:

- Medallion data processing (Bronze, Silver, Gold layers)
- Contract-driven schema management
- SQL warehouse for ad-hoc queries
- ML model tracking for embedding models
- Gold-layer mirroring to Supabase for pgvector search
- Multi-tenant data isolation

---

## Users

| Role | Needs |
|------|-------|
| Data Engineer | Medallion pipelines, contract validation, schema management |
| AI/ML Engineer | Embedding model tracking, vector search, RAG pipeline |
| Analyst/BI | SQL queries via Trino, Superset dashboards from gold layer |
| Platform/Ops | Pipeline monitoring, coverage audits, Supabase mirror health |

---

## Functional Requirements

### FR-1: Medallion Pipeline for Document Processing

The primary pipeline processes documents through three layers:

**Bronze (Raw Crawled Pages)**
- Ingest raw HTML/text from web crawlers
- Preserve original content with metadata (source, URL, HTTP status, content hash)
- Partition by `source` and `crawled_date`
- Contract: `contracts/delta/bronze_raw_pages.yaml`

**Silver (Normalized Documents)**
- Convert raw pages to normalized markdown/text
- Extract metadata (title, language, product, version)
- Deduplicate by `content_hash`
- Partition by `source` and `normalized_date`
- Contract: `contracts/delta/silver_normalized_docs.yaml`

**Gold (Chunks + Embeddings)**
- Split normalized documents into semantic chunks with positional metadata
- Generate vector embeddings with model version tracking
- Partition chunks by `source` and `chunk_date`
- Partition embeddings by `model` and `embed_date`
- Contracts: `contracts/delta/gold_chunks.yaml`, `contracts/delta/gold_embeddings.yaml`

### FR-2: Trino SQL Warehouse

- Trino serves as the SQL query interface for all lakehouse data
- Delta Lake connector reads tables from MinIO (S3-compatible)
- PostgreSQL connector provides access to metadata and RAG serving tables
- Catalog configuration at `infra/lakehouse/trino/catalog/`
- Tables created via `scripts/lakehouse/create_delta_tables_trino.sql`

### FR-3: MLflow Model Tracking

- Track embedding model versions, hyperparameters, and metrics
- Store model artifacts in MinIO (`s3://mlflow/`)
- Backend metadata store in PostgreSQL (`mlflow` database)
- Accessible at `http://localhost:5000`

### FR-4: Supabase Gold Mirror

- Mirror gold-layer tables (chunks, embeddings) to Supabase for pgvector search
- Incremental sync based on configurable lookback window
- Upsert semantics with conflict resolution on primary key
- Script: `scripts/lakehouse/mirror_gold_to_supabase.py`
- Configuration via `config/pipeline.yaml` (mirror_to_supabase section)

### FR-5: Multi-Tenant Isolation

- All tables include `tenant_id` column (type: `uuid`)
- Queries must scope by `tenant_id` in application code
- Row-level security enforced at the Supabase mirror level

### FR-6: n8n Orchestration

- Pipeline triggers via n8n webhooks
- Scheduled pipeline runs via n8n cron
- n8n metadata stored in dedicated PostgreSQL database (`n8n`)

### FR-7: Odoo Data Ingestion (Analytics Pipeline)

- Ingest Odoo PostgreSQL tables to Bronze layer via pipeline templates
- Transform through Silver (normalized) to Gold (aggregated marts)
- Pipeline templates in `ops/pipelines/templates/`:
  - `odoo_ingest_bronze.yaml`: Core, accounting, sales tables
  - `bronze_to_silver.yaml`: Partners, invoices, sales normalization
  - `silver_to_gold.yaml`: Customer 360, revenue, AR aging marts

---

## Non-Functional Requirements

### NFR-1: Performance

- Bronze ingestion: process 10,000 pages/hour minimum
- Silver normalization: 5,000 documents/hour minimum
- Gold embedding generation: bounded by model inference speed
- Trino query latency: < 10s for standard aggregations on gold tables

### NFR-2: Reliability

- Pipeline retries with configurable backoff (per pipeline template caps)
- Health checks on all Docker services (defined in compose.lakehouse.yml)
- Coverage audit detects missing or stale data (`scripts/lakehouse/coverage_audit.py`)

### NFR-3: Observability

- Structured logging from all pipeline scripts
- Coverage audit with JSON output mode for machine consumption
- Contract validation reports error counts and warnings

### NFR-4: Cost

- Entire stack runs on a single DigitalOcean droplet for development
- Production may scale to 2-3 droplets (compute, storage, metadata)
- No per-query or per-hour compute charges

---

## Out of Scope

- Real-time streaming ingestion (batch-only for now)
- Unity Catalog equivalent (planned for later phases)
- Notebook interface (JupyterHub integration deferred)
- CDC (Change Data Capture) from Odoo (planned, not implemented)

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Contract validation pass rate | 100% on every PR |
| Bronze-to-Gold pipeline completion | < 30 minutes for full run |
| Supabase mirror freshness | < 1 hour for gold data |
| Trino query success rate | > 99% for valid SQL |
| Coverage audit completeness | > 95% for active sources |
