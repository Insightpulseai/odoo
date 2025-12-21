# Control Room API — Implementation Plan

> **Version**: 1.0.0
> **Status**: In Progress
> **Last Updated**: 2024-12-21

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Control Room API                             │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    FastAPI Application                       ││
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        ││
│  │  │  Jobs   │  │  Runs   │  │Lineage  │  │Artifacts│        ││
│  │  │ Router  │  │ Router  │  │ Router  │  │ Router  │        ││
│  │  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        ││
│  │       │            │            │            │              ││
│  │  ┌────────────────────────────────────────────────┐        ││
│  │  │               Service Layer                     │        ││
│  │  │  JobService | RunService | LineageService      │        ││
│  │  └────────────────────────────────────────────────┘        ││
│  │       │                                                     ││
│  │  ┌────────────────────────────────────────────────┐        ││
│  │  │             Supabase Repository                 │        ││
│  │  │   jobs | runs | artifacts | lineage_edges      │        ││
│  │  └────────────────────────────────────────────────┘        ││
│  └─────────────────────────────────────────────────────────────┘│
│                          │                                       │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              Execution Dispatcher                            ││
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐                ││
│  │  │ K8s Jobs  │  │DO Runner  │  │ n8n Hook  │                ││
│  │  └───────────┘  └───────────┘  └───────────┘                ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Database Schema

### 2.1 Core Tables (Supabase)

```sql
-- runtime.cr_jobs
CREATE TABLE runtime.cr_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL,
  job_type TEXT NOT NULL,  -- spark_etl, diagram_export, etc.
  spec JSONB NOT NULL,     -- Natural language + inputs
  code JSONB,              -- Generated code files
  repo JSONB,              -- Git repo context
  callbacks JSONB,         -- on_complete, on_fail URLs
  created_by TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- runtime.cr_runs
CREATE TABLE runtime.cr_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id UUID REFERENCES runtime.cr_jobs(id),
  tenant_id UUID NOT NULL,
  status TEXT NOT NULL DEFAULT 'queued',
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  result JSONB,
  logs_url TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- runtime.cr_artifacts
CREATE TABLE runtime.cr_artifacts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id UUID REFERENCES runtime.cr_runs(id),
  tenant_id UUID NOT NULL,
  path TEXT NOT NULL,
  content_type TEXT,
  size_bytes BIGINT,
  storage_url TEXT,
  checksum TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- runtime.cr_lineage_edges
CREATE TABLE runtime.cr_lineage_edges (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL,
  source_entity TEXT NOT NULL,  -- schema.table
  target_entity TEXT NOT NULL,  -- schema.table
  job_id UUID REFERENCES runtime.cr_jobs(id),
  run_id UUID REFERENCES runtime.cr_runs(id),
  edge_type TEXT DEFAULT 'data_flow',
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT now(),
  deleted_at TIMESTAMPTZ  -- Soft delete
);
```

### 2.2 Indexes

```sql
CREATE INDEX idx_cr_runs_status ON runtime.cr_runs(status);
CREATE INDEX idx_cr_runs_job_id ON runtime.cr_runs(job_id);
CREATE INDEX idx_cr_artifacts_run_id ON runtime.cr_artifacts(run_id);
CREATE INDEX idx_cr_lineage_source ON runtime.cr_lineage_edges(source_entity);
CREATE INDEX idx_cr_lineage_target ON runtime.cr_lineage_edges(target_entity);
```

---

## 3. API Implementation

### 3.1 Project Structure

```
apps/control-room-api/
├── app.py                 # FastAPI application
├── requirements.txt       # Dependencies
├── .env.example           # Environment template
├── Dockerfile             # Container build
├── models/
│   ├── __init__.py
│   ├── job.py             # Job models
│   ├── run.py             # Run models
│   ├── artifact.py        # Artifact models
│   └── lineage.py         # Lineage models
├── routes/
│   ├── __init__.py
│   ├── jobs.py            # /api/v1/jobs
│   ├── runs.py            # /api/v1/runs
│   ├── artifacts.py       # /api/v1/artifacts
│   ├── lineage.py         # /api/v1/lineage
│   └── webhooks.py        # /api/v1/webhooks
├── services/
│   ├── __init__.py
│   ├── job_service.py     # Job business logic
│   ├── run_service.py     # Run execution
│   ├── lineage_service.py # Lineage graph
│   └── dispatcher.py      # Execution dispatch
└── utils/
    ├── __init__.py
    ├── supabase_client.py # Database access
    ├── auth.py            # JWT validation
    └── callbacks.py       # Webhook delivery
```

### 3.2 Endpoints Summary

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/jobs/run | Submit job for execution |
| POST | /api/v1/jobs/validate | Validate job without execution |
| GET | /api/v1/runs/{run_id} | Get run status |
| POST | /api/v1/runs/{run_id}/cancel | Cancel running job |
| POST | /api/v1/runs/{run_id}/events | Push event (internal) |
| GET | /api/v1/artifacts/{artifact_id} | Download artifact |
| POST | /api/v1/artifacts | Upload artifact |
| GET | /api/v1/lineage/graph | Query lineage |
| POST | /api/v1/webhooks/continue | Continue callback |

---

## 4. Skill: Visio-DrawIO-Export

### 4.1 Skill Package Structure

```
skills/visio-drawio-export/
├── README.md
├── skill.yaml             # Skill definition
├── src/
│   ├── index.ts           # Entry point
│   ├── validate.ts        # DrawIO validation
│   ├── export.ts          # PNG/SVG export
│   └── diff.ts            # Visual regression
├── docker/
│   └── Dockerfile         # Headless drawio
└── workflows/
    └── diagrams-qa.yml    # GitHub Actions
```

### 4.2 CLI Interface

```bash
visio-drawio-export \
  --input diagram.vsdx \
  --outdir artifacts/diagrams \
  --formats png,svg \
  --validate strict \
  --baseline baselines/ \
  --diff-threshold 0.003
```

### 4.3 Integration with Control Room

```json
{
  "job_type": "diagram_export",
  "spec": {
    "text": "Export architecture diagrams to PNG/SVG",
    "inputs": {
      "source_glob": "docs/**/*.vsdx",
      "output_dir": "artifacts/diagrams"
    }
  }
}
```

---

## 5. Implementation Phases

### Phase 1: Core API (Current)

- [x] Spec bundle creation
- [ ] Database migration
- [ ] FastAPI skeleton
- [ ] Job submission endpoint
- [ ] Run status endpoint

### Phase 2: Execution

- [ ] K8s Job dispatcher
- [ ] DO runner fallback
- [ ] Webhook callbacks
- [ ] Artifact storage

### Phase 3: Lineage

- [ ] Lineage edge creation
- [ ] Graph query API
- [ ] Visualization export

### Phase 4: Skills

- [ ] Visio-DrawIO skill
- [ ] GitHub Actions integration
- [ ] Visual regression

---

## 6. Deployment

### 6.1 Docker Compose

```yaml
control-room-api:
  build: ./apps/control-room-api
  ports:
    - "8789:8789"
  environment:
    - SUPABASE_URL=${SUPABASE_URL}
    - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
  depends_on:
    - postgres
```

### 6.2 Environment Variables

| Variable | Description |
|----------|-------------|
| SUPABASE_URL | Supabase project URL |
| SUPABASE_SERVICE_KEY | Service role key |
| K8S_NAMESPACE | Kubernetes namespace |
| DO_API_TOKEN | DigitalOcean token |
| WEBHOOK_SECRET | Callback signing key |

---

## 7. Testing Strategy

- Unit tests: pytest with mocks
- Integration tests: TestContainers
- E2E tests: Continue CLI scripts
- Load tests: Locust
