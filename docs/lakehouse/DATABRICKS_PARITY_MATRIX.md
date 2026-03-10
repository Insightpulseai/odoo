# Databricks Lakehouse Parity Matrix (Self-Hosted)

> **Last Updated**: 2026-03-08
> **Spec Bundle**: `spec/lakehouse/`

Goal: Implement a Lakehouse architecture (Delta Lake + object storage + Postgres/Supabase + BI) that mirrors the core benefits of the Databricks Lakehouse, **fully self-hosted** on our own infrastructure and built exclusively from open-source components and licensed connectors.

Key points:

- No Databricks SaaS runtime or SKU is used.
- All compute/storage is on our own infra (e.g., DigitalOcean, Supabase, self-managed clusters).
- We still strictly respect open-source licenses for all components (Apache-2.0, LGPL-3.0, AGPL-3.0, MIT, etc.).

Reference components:

- **Delta Lake** -- Open-source storage layer adding ACID reliability and time travel to data lakes (Apache-2.0).
- **Postgres / Supabase** -- Warehouse, control plane, vector search, and observability.
- **Object Storage** -- Lake storage (MinIO, S3-compatible).
- **BI Layer** -- Superset (self-hosted).
- **Orchestration** -- n8n + MCP tools for ELT, jobs, and AI-driven workflows.

---

## Parity Table

| Category | Databricks Feature | OSS Component | Status | Notes |
|----------|--------------------|---------------|--------|-------|
| **Storage** | | | | |
| | DBFS (Databricks File System) | MinIO (S3-compatible) | DONE | `compose.lakehouse.yml`, port 9000/9001. Path-style access enabled. |
| | Delta Lake format | Delta Lake 2.4.0 (via Spark) | DONE | Jars in `infra/lakehouse/jars/`. ACID transactions on MinIO. |
| | Parquet read/write | Spark 3.5 built-in | DONE | Native Parquet support in Spark and Trino. |
| | Managed/External tables | Trino external tables | DONE | Tables defined with `location` pointing to MinIO paths. |
| **ACID / Time Travel** | | | | |
| | ACID transactions | Delta Lake (via Spark) | DONE | Transaction log in `_delta_log/` on MinIO. |
| | Time travel (VERSION AS OF) | Delta Lake time travel | PARTIAL | Available in Spark. Trino Delta connector supports read-only time travel. |
| | VACUUM (data cleanup) | Delta Lake VACUUM | PARTIAL | Available via Spark. Not yet automated on schedule. |
| | Change Data Feed (CDF) | Delta Lake CDF | PLANNED | Requires Spark-side enablement. Not yet configured. |
| **Medallion Architecture** | | | | |
| | Bronze layer (raw ingestion) | Bronze tables on MinIO | DONE | `s3://lakehouse/bronze/`. Contract: `bronze_raw_pages`. DDL in Trino. |
| | Silver layer (cleaned/normalized) | Silver tables on MinIO | DONE | `s3://lakehouse/silver/`. Contract: `silver_normalized_docs`. DDL in Trino. |
| | Gold layer (aggregated/ML-ready) | Gold tables on MinIO | DONE | `s3://lakehouse/gold/`. Contracts: `gold_chunks`, `gold_embeddings`. DDL in Trino. |
| | Pipeline templates | YAML pipeline specs | DONE | `ops/pipelines/templates/` -- 3 templates (ingest, b-to-s, s-to-g). |
| | Contract enforcement | `contracts/delta/*.yaml` + validator | DONE | `src/lakehouse/contracts.py` + `scripts/lakehouse/validate_contracts.py`. |
| **SQL Warehouse** | | | | |
| | Databricks SQL Warehouse | Trino | DONE | Port 8082. Delta + PostgreSQL catalogs configured. |
| | SQL endpoint (HTTP) | Trino v1/statement API | DONE | HTTP-based SQL execution used by mirror and audit scripts. |
| | Query result caching | Trino query caching | PARTIAL | Trino has built-in caching. Not tuned for production. |
| | Serverless SQL | -- | NOT PLANNED | Self-hosted model; Trino runs continuously. |
| | SQL permissions (fine-grained) | Trino access control | PLANNED | Requires Trino system access control plugin configuration. |
| **Streaming / Jobs** | | | | |
| | Structured Streaming | Spark Structured Streaming | PLANNED | Spark 3.5 supports it. Not yet configured for lakehouse pipelines. |
| | Lakeflow Jobs (workflows) | n8n | DONE | `compose.lakehouse.yml`, port 5678. Webhook + cron scheduling. |
| | Job clusters (auto-scaling) | Spark Master/Worker | PARTIAL | Fixed worker count. No auto-scaling. Scale by adjusting `compose.lakehouse.yml`. |
| | Lakeflow Connect (connectors) | Custom Python + Spark | PARTIAL | Odoo PostgreSQL connector via pipeline templates. No GUI connector catalog. |
| | DLT (Declarative Pipelines) | Pipeline YAML templates | PARTIAL | `ops/pipelines/templates/` define declarative transforms. No live DLT runtime yet. |
| **ML / AI** | | | | |
| | MLflow (experiments/models) | MLflow OSS | DONE | `compose.lakehouse.yml`, port 5000. Backend: PostgreSQL. Artifacts: MinIO. |
| | Model Registry | MLflow Model Registry | DONE | Available via MLflow OSS. Not yet populated with models. |
| | Feature Store | -- | NOT PLANNED | Use gold-layer tables directly for features. |
| | Model Serving | -- | PLANNED | Will use self-hosted inference (FastAPI or similar). |
| | Vector Search | Supabase pgvector | PARTIAL | Gold mirror script exists. Supabase tables not yet created. |
| | Mosaic AI (LLM training) | -- | NOT PLANNED | Use external API providers for LLM inference. |
| **Governance / Security** | | | | |
| | Unity Catalog | -- | PLANNED | No direct equivalent yet. Contracts provide schema governance. |
| | Data lineage | Pipeline templates + run events | PARTIAL | Pipeline templates define input/output manifests. No UI lineage graph. |
| | Access control (table-level) | Trino access control | PLANNED | Requires Trino plugin. Currently single-user. |
| | Audit logging | n8n + Supabase ops schema | PARTIAL | Run events logged to Supabase `ops.run_events`. No unified audit log. |
| | Data masking | -- | PLANNED | Not yet implemented. |
| | Secret management | `.env` files + Supabase Vault | DONE | Secrets in `.env` (local), env vars (runtime). Never in code. |
| **Developer Experience** | | | | |
| | Notebooks (interactive) | -- | PLANNED | JupyterHub integration deferred. |
| | Repos (Git integration) | Git (native) | DONE | All pipeline code, contracts, and config version-controlled in this repo. |
| | Workspace (collaborative) | -- | NOT PLANNED | Single-developer workflow. |
| | Databricks CLI | Custom scripts | DONE | `scripts/lakehouse/` -- validate, audit, mirror, DDL create. |
| | REST API | Trino HTTP + Supabase REST | DONE | Trino v1/statement for SQL. Supabase REST for gold mirror. |
| **Monitoring / Observability** | | | | |
| | Job run monitoring | n8n + coverage audit | PARTIAL | `scripts/lakehouse/coverage_audit.py` for layer completeness. No real-time dashboard. |
| | Query profiling | Trino EXPLAIN | DONE | Available via Trino. |
| | Cost management | Fixed infrastructure cost | DONE | No per-query charges. DigitalOcean droplet pricing. |
| | Cluster metrics | Docker stats | PARTIAL | Basic container metrics. No Prometheus/Grafana yet. |

---

## Parity Score Summary

| Category | Features | Done | Partial | Planned | Not Planned | Parity % |
|----------|----------|------|---------|---------|-------------|----------|
| Storage | 4 | 4 | 0 | 0 | 0 | 100% |
| ACID / Time Travel | 4 | 1 | 2 | 1 | 0 | 50% |
| Medallion | 5 | 5 | 0 | 0 | 0 | 100% |
| SQL Warehouse | 5 | 2 | 1 | 1 | 1 | 50% |
| Streaming / Jobs | 5 | 1 | 3 | 1 | 0 | 50% |
| ML / AI | 6 | 2 | 1 | 1 | 2 | 42% |
| Governance | 6 | 1 | 2 | 2 | 1 | 33% |
| Developer Experience | 5 | 3 | 0 | 1 | 1 | 60% |
| Monitoring | 4 | 2 | 1 | 0 | 1 | 63% |
| **Total** | **44** | **21** | **10** | **7** | **6** | **59%** |

**Calculation**: Done = 100%, Partial = 50%, Planned = 0%, Not Planned = excluded from denominator.

**Weighted parity** (excluding "Not Planned"): **68%** (21 done + 10 partial out of 38 applicable features).

---

## Component License Matrix

| Component | Version | License | Self-Hostable | Used In |
|-----------|---------|---------|---------------|---------|
| Apache Spark | 3.5 | Apache-2.0 | Yes | Batch compute, Delta read/write |
| Delta Lake | 2.4.0 | Apache-2.0 | Yes | ACID storage format |
| Trino | latest | Apache-2.0 | Yes | SQL warehouse |
| MinIO | latest | AGPL-3.0 | Yes | S3-compatible object storage |
| MLflow | latest | Apache-2.0 | Yes | Model registry, experiments |
| PostgreSQL | 15 | PostgreSQL License | Yes | Metadata, RAG serving |
| n8n | latest | Sustainable Use | Yes (self-hosted) | Workflow orchestration |
| Supabase | hosted | Apache-2.0 (core) | Yes (or hosted) | Gold mirror, pgvector search |
| Apache Superset | latest | Apache-2.0 | Yes | BI dashboards |

---

## Databricks Features Intentionally Not Replicated

| Feature | Reason |
|---------|--------|
| Serverless SQL | Self-hosted model uses always-on Trino; no serverless billing model needed. |
| Feature Store | Gold tables serve as feature tables directly; no separate store needed at current scale. |
| Mosaic AI / LLM training | LLM inference via external APIs (OpenAI, Anthropic). Training not in scope. |
| Collaborative Workspace | Single-developer workflow. IDE-based development with Git. |
| Auto-scaling clusters | Fixed infrastructure on DigitalOcean. Scale manually by adding workers. |
