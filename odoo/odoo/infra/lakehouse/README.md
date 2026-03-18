# OSS Lakehouse Stack

**Special-Purpose Environment** - Not part of canonical Odoo deployment.

Self-hosted "Databricks-like" execution layer using open-source components.

> **Note**: This is a standalone subsystem. Do not use for Odoo application deployment.
> See `../../SANDBOX.md` for canonical Odoo environments.

## Why Not Databricks CE?

**Reality check**: Databricks Community Edition is cloud-hosted, not self-hostable. The `databricksruntime/*` docker images aren't a supported self-host path.

This stack provides Databricks patterns with fully self-hosted OSS:

| Databricks | OSS Equivalent | Purpose |
|------------|----------------|---------|
| Databricks Runtime | **Spark 3.5** | Distributed compute |
| Delta Lake | **Delta Lake** (via Spark) | ACID tables, medallion |
| MLflow | **MLflow** | Model registry, experiments |
| Databricks SQL | **Trino** | SQL warehouse |
| DBFS | **MinIO** | S3-compatible storage |
| Workflows | **n8n** | Orchestration |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Continue IDE                               │
│                      /docs /pipeline /sql                       │
└──────────────────────────────┬──────────────────────────────────┘
                               │ REST API
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                            │
│  /v1/answer  /v1/pipelines  /v1/compute/sql  /v1/compute/job   │
└──────────────────────────────┬──────────────────────────────────┘
           ┌───────────────────┼───────────────────┐
           ↓                   ↓                   ↓
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│      n8n         │  │      Trino       │  │      Spark       │
│  Orchestration   │  │   SQL Queries    │  │   Batch Jobs     │
└──────────────────┘  └──────────────────┘  └──────────────────┘
           │                   │                   │
           └───────────────────┴───────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│              PostgreSQL + MinIO + MLflow                        │
│         Metadata   │   Object Storage   │   Model Registry      │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# 1. Configure environment
cd infra/lakehouse
cp .env.example .env
# Edit .env with your passwords

# 2. Start the stack (non-canonical compose file)
docker compose -f compose.lakehouse.yml up -d

# 3. Verify health
curl -fsS http://localhost:5678/healthz  # n8n
curl -fsS http://localhost:5000/health   # MLflow
curl -fsS http://localhost:8082/v1/info  # Trino
curl -fsS http://localhost:8080          # Spark Master
```

## Services

| Service | Port | UI URL | Purpose |
|---------|------|--------|---------|
| PostgreSQL | 5432 | - | Metadata store |
| MinIO | 9000/9001 | http://localhost:9001 | Object storage |
| Spark Master | 7077/8080 | http://localhost:8080 | Compute cluster |
| Trino | 8082 | http://localhost:8082 | SQL warehouse |
| MLflow | 5000 | http://localhost:5000 | Model registry |
| n8n | 5678 | http://localhost:5678 | Workflows |

## Usage

### Run SQL Query (via Trino)

```bash
# Using Trino CLI
docker exec -it lakehouse-trino trino --execute "SELECT * FROM postgresql.public.rag_documents LIMIT 10"

# Using API (when enabled)
curl -X POST http://localhost:8000/v1/compute/sql \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM delta.bronze.github_repos LIMIT 10"}'
```

### Submit Spark Job

```bash
# Using spark-submit
docker exec -it lakehouse-spark-master spark-submit \
  --master spark://spark-master:7077 \
  /path/to/your/job.py

# Using API (when enabled)
curl -X POST http://localhost:8000/v1/compute/job \
  -H "Content-Type: application/json" \
  -d '{"job_name": "bronze_crawl", "params": {"org": "databricks"}}'
```

### Trigger Pipeline (via n8n)

```bash
# Using n8n API
curl -X POST http://localhost:5678/webhook/pipeline-trigger \
  -H "Content-Type: application/json" \
  -d '{"pipeline": "bronze_crawl_github", "inputs": {"org": "OCA"}}'
```

## Medallion Architecture

| Layer | Storage | Purpose |
|-------|---------|---------|
| **Bronze** | `s3://lakehouse/bronze/` | Raw data (JSON, crawled pages) |
| **Silver** | `s3://lakehouse/silver/` | Validated, chunked, normalized |
| **Gold** | `s3://lakehouse/gold/` | Aggregates, embeddings, capability maps |

### Bronze → Silver → Gold Pipeline

```
[Crawler]          [Normalizer]         [Embedder]
    │                   │                    │
    ↓                   ↓                    ↓
┌─────────┐        ┌─────────┐         ┌─────────┐
│ Bronze  │   →    │ Silver  │    →    │  Gold   │
│ raw/*   │        │ chunks/*│         │ embed/* │
└─────────┘        └─────────┘         └─────────┘
```

## Integration with Continue

The FastAPI backend exposes a stable API that Continue IDE talks to:

| Command | API Endpoint | Backend |
|---------|--------------|---------|
| `/docs <query>` | `POST /v1/answer` | Supabase BM25 + pgvector |
| `/pipeline run <name>` | `POST /v1/pipelines/run` | n8n |
| `/sql <query>` | `POST /v1/compute/sql` | Trino |
| `/job <name>` | `POST /v1/compute/job` | Spark |

This abstraction lets you:
1. Self-host with OSS Lakehouse (this stack)
2. Migrate to real Databricks later (just swap backend)
3. Keep Continue IDE stable regardless of compute backend

## Delta Lake Support

To use Delta Lake tables, add the Delta jars to Spark:

```bash
# Create jars directory
mkdir -p infra/lakehouse/jars

# Download Delta jars (for Spark 3.5)
wget https://repo1.maven.org/maven2/io/delta/delta-core_2.12/2.4.0/delta-core_2.12-2.4.0.jar -P infra/lakehouse/jars/
wget https://repo1.maven.org/maven2/io/delta/delta-storage/2.4.0/delta-storage-2.4.0.jar -P infra/lakehouse/jars/
```

## Troubleshooting

### Spark worker won't connect
```bash
# Check master is healthy
docker logs lakehouse-spark-master
# Check network connectivity
docker exec lakehouse-spark-worker ping spark-master
```

### Trino can't read Delta tables
```bash
# Ensure MinIO bucket exists
docker exec lakehouse-minio mc mb minio/lakehouse/delta
# Check Trino logs
docker logs lakehouse-trino
```

### MLflow artifacts not saving
```bash
# Ensure MinIO bucket exists
docker exec lakehouse-minio mc mb minio/mlflow
# Check MLflow logs
docker logs lakehouse-mlflow
```

## Production Deployment

For production, consider:

1. **External PostgreSQL**: Use managed database (DO, RDS, Supabase)
2. **External S3**: Use real S3 or DO Spaces instead of MinIO
3. **Kubernetes**: Deploy with Helm charts for scalability
4. **Monitoring**: Add Prometheus + Grafana for observability
5. **Security**: Enable TLS, authentication, network policies
