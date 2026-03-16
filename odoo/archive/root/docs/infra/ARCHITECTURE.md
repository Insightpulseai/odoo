# Lakehouse Architecture

> **Last Updated**: 2026-03-08
> **Spec Bundle**: `spec/lakehouse/`
> **Infrastructure**: `infra/lakehouse/compose.lakehouse.yml`

---

## Overview

The lakehouse is a self-hosted data platform that provides Databricks-class capabilities using open-source components. It runs as a standalone Docker Compose stack, separate from the Odoo ERP deployment, and processes data through a medallion architecture (Bronze, Silver, Gold).

---

## Component Diagram

```
                            ┌────────────────────────────┐
                            │        n8n (5678)          │
                            │     Workflow Orchestration  │
                            └─────┬──────────┬───────────┘
                                  │          │
                   Trigger Jobs   │          │  Trigger Pipelines
                                  │          │
              ┌───────────────────▼──┐   ┌──▼───────────────────┐
              │   Spark Master (7077) │   │    Trino (8082)      │
              │   + Worker            │   │    SQL Warehouse     │
              │   Batch Compute       │   │    Ad-hoc Queries    │
              └───────────┬───────────┘   └───────┬──────────────┘
                          │                       │
                          │  Read/Write Delta     │  Read Delta + PG
                          │                       │
              ┌───────────▼───────────────────────▼──────────────┐
              │                   MinIO (9000)                    │
              │              S3-Compatible Storage                │
              │                                                   │
              │  s3://lakehouse/bronze/   Raw crawled pages       │
              │  s3://lakehouse/silver/   Normalized documents    │
              │  s3://lakehouse/gold/     Chunks + embeddings     │
              │  s3://mlflow/             Model artifacts         │
              └──────────────────────────────────────────────────┘
                          │
              ┌───────────▼──────────────────────────────────────┐
              │               PostgreSQL (5432)                   │
              │                                                   │
              │  lakehouse   Metadata, RAG serving tables         │
              │  mlflow      MLflow backend store                 │
              │  n8n         n8n workflow metadata                │
              │                                                   │
              │  Schemas: rag, gold, runtime                      │
              └──────────────────────────────────────────────────┘
                          │
              ┌───────────▼──────────────────────────────────────┐
              │              MLflow (5000)                        │
              │         Model Registry + Experiments              │
              │  Backend: PostgreSQL │ Artifacts: MinIO            │
              └──────────────────────────────────────────────────┘
```

---

## Service Map

| Service | Image | Port(s) | Purpose | Health Check |
|---------|-------|---------|---------|--------------|
| PostgreSQL | `postgres:15` | 5432 | Metadata store (lakehouse, mlflow, n8n databases) | `pg_isready` |
| MinIO | `minio/minio:latest` | 9000 (S3), 9001 (Console) | S3-compatible object storage for Delta tables and artifacts | `curl /minio/health/live` |
| Spark Master | `bitnami/spark:3.5` | 7077 (RPC), 8080 (UI) | Distributed compute cluster master | `curl :8080` |
| Spark Worker | `bitnami/spark:3.5` | -- | Compute worker (2G RAM, 2 cores default) | Depends on master |
| Trino | `trinodb/trino:latest` | 8082 (mapped from 8080) | SQL warehouse with Delta + PostgreSQL catalogs | `curl /v1/info` |
| MLflow | `ghcr.io/mlflow/mlflow:latest` | 5000 | Model registry, experiment tracking | `curl /health` |
| n8n | `n8nio/n8n:latest` | 5678 | Workflow orchestration, pipeline scheduling | `wget /healthz` |

---

## Medallion Data Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Sources    │     │   Bronze     │     │   Silver     │     │    Gold      │
│              │     │              │     │              │     │              │
│ Web Crawlers │────>│ raw_pages    │────>│ normalized   │────>│ chunks       │
│ Odoo PG      │     │              │     │ _docs        │     │ embeddings   │
│ APIs         │     │ Append-only  │     │ Deduplicated │     │ Aggregated   │
│              │     │ Raw content  │     │ Schema-clean │     │ ML-ready     │
└──────────────┘     └──────────────┘     └──────────────┘     └──────┬───────┘
                                                                      │
                                                                      │ Mirror
                                                                      ▼
                                                               ┌──────────────┐
                                                               │  Supabase    │
                                                               │  pgvector    │
                                                               │              │
                                                               │ rag.chunks   │
                                                               │ rag.embed    │
                                                               └──────────────┘
```

### Layer Details

**Bronze Layer** (`s3://lakehouse/bronze/`)
- Raw data as received from sources, no transformation
- Schema defined by `contracts/delta/bronze_raw_pages.yaml`
- Partitioned by `source` + `crawled_date`
- Append-only (never updated, only vacuumed by retention policy)

**Silver Layer** (`s3://lakehouse/silver/`)
- Cleaned and normalized data
- HTML converted to markdown, metadata extracted
- Deduplicated by `content_hash`
- Schema defined by `contracts/delta/silver_normalized_docs.yaml`
- Partitioned by `source` + `normalized_date`

**Gold Layer** (`s3://lakehouse/gold/`)
- Business-ready outputs split across two tables:
  - **chunks**: Semantic document chunks with headings, content, token counts
  - **embeddings**: Vector embeddings with model version tracking
- Schemas defined by `contracts/delta/gold_chunks.yaml` and `contracts/delta/gold_embeddings.yaml`
- Chunks partitioned by `source` + `chunk_date`
- Embeddings partitioned by `model` + `embed_date`

---

## Integration Points

### Odoo ERP (Ingest Source)

Odoo PostgreSQL data enters the lakehouse as a Bronze source via ingestion pipelines defined in `ops/pipelines/templates/odoo_ingest_bronze.yaml`. The pipeline extracts core, accounting, and sales tables and writes them to `s3://lakehouse/bronze/odoo_*`. The lakehouse never writes back to Odoo.

### Supabase (Gold Mirror Target)

Gold-layer tables are mirrored to Supabase for pgvector search via `scripts/lakehouse/mirror_gold_to_supabase.py`. The script:

1. Queries Trino for recent gold data (configurable lookback window)
2. Upserts rows to Supabase tables via REST API
3. Handles pagination for large result sets

Environment variables required: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`.

### n8n (Orchestration)

n8n triggers pipeline stages via webhooks and schedules recurring runs via cron. The n8n instance runs within the lakehouse Docker Compose stack and stores its workflow metadata in the shared PostgreSQL.

### Trino (Query Interface)

Trino provides SQL access to all lakehouse data via two catalogs:

- **delta**: Reads Delta tables from MinIO. Config at `infra/lakehouse/trino/catalog/delta.properties`.
- **postgresql**: Reads PostgreSQL tables directly. Config at `infra/lakehouse/trino/catalog/postgresql.properties`.

Queries use the pattern `SELECT * FROM delta.<schema>.<table>` (e.g., `delta.gold.chunks`).

### MLflow (Model Tracking)

MLflow tracks embedding model versions and stores artifacts in MinIO. The MLflow backend connects to the `mlflow` PostgreSQL database. Embedding pipeline runs log model metadata and metrics to MLflow before writing vectors to the gold layer.

---

## Contract Validation Flow

```
contracts/delta/*.yaml
        │
        │  load_contracts()
        ▼
src/lakehouse/contracts.py
  DeltaContract.validate()
        │
        │  Errors?
        ▼
scripts/lakehouse/validate_contracts.py
        │
        ├── Exit 0: All contracts valid
        └── Exit 1: Validation errors found
                     │
                     ▼
              CI blocks merge
```

The validation checks:
- Table name and location are present
- At least one column is defined
- Partition columns exist in the column list
- Primary key columns exist in the column list
- Column names do not collide with SQL reserved words (warning)
- Retention period is reasonable (warning if < 30 days)

---

## Storage Layout

```
MinIO (s3://lakehouse/)
├── bronze/
│   ├── raw_pages/
│   │   ├── source=confluence/
│   │   │   └── crawled_date=2026-03-01/
│   │   └── source=github/
│   │       └── crawled_date=2026-03-01/
│   └── odoo_core/           (Odoo ingestion)
│       └── _ingest_date=.../
├── silver/
│   └── normalized_docs/
│       ├── source=confluence/
│       │   └── normalized_date=2026-03-01/
│       └── source=github/
│           └── normalized_date=2026-03-01/
├── gold/
│   ├── chunks/
│   │   └── source=confluence/
│   │       └── chunk_date=2026-03-01/
│   ├── embeddings/
│   │   └── model=text-embedding-3-small/
│   │       └── embed_date=2026-03-01/
│   ├── customer_360/        (Odoo analytics)
│   ├── revenue_daily/
│   ├── revenue_monthly/
│   └── ar_aging/
└── delta/                   (Trino catalog root)

MinIO (s3://mlflow/)
└── <experiment-id>/
    └── <run-id>/
        └── artifacts/
```

---

## Network Topology

All services run on a single Docker network named `lakehouse`. Internal service discovery uses container names as hostnames (e.g., `postgres`, `minio`, `spark-master`, `trino`, `mlflow`, `n8n`).

External access is via localhost port mappings as defined in `compose.lakehouse.yml`. For production deployment, an nginx reverse proxy or similar should front the exposed services.

---

## Configuration Files

| File | Purpose |
|------|---------|
| `infra/lakehouse/compose.lakehouse.yml` | Docker Compose service definitions |
| `infra/lakehouse/.env.example` | Environment variable template |
| `infra/lakehouse/trino/catalog/delta.properties` | Trino Delta Lake connector |
| `infra/lakehouse/trino/catalog/postgresql.properties` | Trino PostgreSQL connector |
| `infra/lakehouse/init/postgres/01_init_databases.sql` | PostgreSQL initialization |
| `config/pipeline.yaml` | Pipeline configuration (planned) |
| `contracts/delta/*.yaml` | Delta table contract definitions |
