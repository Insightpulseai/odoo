# Control Room API — Product Requirements Document

> **Version**: 1.0.0
> **Status**: Draft
> **Last Updated**: 2024-12-21

---

## 1. Overview

Control Room API provides a Databricks-style orchestration layer for our stack, enabling Continue CLI to submit jobs, track execution, and maintain data lineage.

---

## 2. User Personas

### 2.1 Developer (Primary)

- Uses Continue CLI to generate code
- Expects job execution and immediate feedback
- Needs artifact access (logs, outputs)

### 2.2 CI/CD Pipeline

- Runs `cn -p` in headless mode
- Requires deterministic execution
- Needs webhook callbacks for status

### 2.3 Platform Admin

- Monitors job execution
- Manages lineage graph
- Handles failed runs

---

## 3. Functional Requirements

### FR-1: Job Submission

**POST /api/v1/jobs/run**

```json
{
  "job_type": "spark_etl|diagram_export|schema_migration|kb_catalog",
  "spec": {
    "text": "Natural language description of the job",
    "inputs": {
      "source": "supabase://schema.table",
      "target": "supabase://schema.output_table"
    }
  },
  "code": {
    "files": [
      {"path": "jobs/etl.py", "content": "..."}
    ]
  },
  "created_by": "continue-ide-plugin",
  "repo": {"url": "git@github.com:org/repo.git", "ref": "main"},
  "callbacks": {
    "on_complete": "https://hook.example.com/complete",
    "on_fail": "https://hook.example.com/fail"
  }
}
```

**Response:**
```json
{
  "run_id": "uuid",
  "status": "queued",
  "created_at": "2024-12-21T00:00:00Z"
}
```

### FR-2: Job Validation

**POST /api/v1/jobs/validate**

Pre-flight validation without execution:
- Syntax check
- Schema validation
- Dependency verification

### FR-3: Run Status

**GET /api/v1/runs/{run_id}**

```json
{
  "run_id": "uuid",
  "job_type": "spark_etl",
  "status": "running|completed|failed|cancelled",
  "started_at": "...",
  "completed_at": "...",
  "artifacts": [
    {"path": "output/result.csv", "url": "..."}
  ],
  "logs_url": "..."
}
```

### FR-4: Event Streaming

**POST /api/v1/runs/{run_id}/events**

Real-time progress updates:
```json
{
  "event_type": "progress|log|artifact",
  "timestamp": "...",
  "data": {...}
}
```

### FR-5: Webhook Callbacks

**POST /api/v1/webhooks/continue**

Callback target for IDE integration:
```json
{
  "run_id": "uuid",
  "status": "completed",
  "summary": "ETL completed: 1000 rows processed",
  "artifacts": [...]
}
```

### FR-6: Lineage Graph

**GET /api/v1/lineage/graph?entity=schema.table**

Returns upstream/downstream lineage:
```json
{
  "entity": "schema.table",
  "upstream": [{"entity": "source.raw", "job_id": "..."}],
  "downstream": [{"entity": "gold.agg", "job_id": "..."}]
}
```

### FR-7: Artifact Management

**GET /api/v1/artifacts/{artifact_id}**
**POST /api/v1/artifacts**

Store and retrieve job artifacts (code, outputs, diagrams).

---

## 4. Non-Functional Requirements

### NFR-1: Performance

- Job submission: < 500ms response
- Run status: < 100ms response
- Lineage query: < 1s for 1000 edges

### NFR-2: Availability

- 99.9% uptime SLA
- Graceful degradation if Supabase unavailable

### NFR-3: Scalability

- Handle 100 concurrent jobs
- 1M lineage edges

### NFR-4: Security

- JWT authentication required
- Multi-tenant isolation
- Secrets never logged

---

## 5. Integration Points

### 5.1 Continue CLI

- `cn -p` for headless execution
- CONTINUE_API_KEY for authentication
- Webhook callback for status

### 5.2 Supabase

- Postgres for job/run storage
- Storage for artifacts

### 5.3 K8s/DO

- K8s Jobs for heavy compute
- DO droplets for simple tasks

### 5.4 n8n

- Workflow triggers
- Data sync operations

---

## 6. Out of Scope

- Full Databricks compatibility
- Streaming jobs (batch only)
- Interactive notebooks (export only)
- Model serving (artifacts only)
