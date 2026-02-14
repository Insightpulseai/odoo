# ADK Control Room — Product Requirements Document

## Product Overview

Control Room is a Databricks-class orchestration layer built on:
- **ADK-TS** (agent runtime)
- **Continue** (headless + CLI) (docs → PR automation)
- **Supabase** (catalog, lineage, artifacts)
- **n8n / DO Jobs** (execution)
- **Odoo CE + OCA** (business state + approvals)

It replaces:
- ❌ Databricks Jobs, Unity Catalog, Workflows
- ❌ Ad-hoc scripts, manual PRs, spreadsheet ops
- ❌ Notion (knowledge base, automation, AI actions)

## Users

### Platform Engineer
- **Needs**: Deploy agents, monitor jobs, debug failures
- **Goals**: 99.9% uptime, <5min mean time to recovery
- **Success Metric**: Zero production incidents from agent bugs

### Finance Systems Lead
- **Needs**: Trigger month-end close, validate compliance
- **Goals**: 100% audit trail, zero manual interventions
- **Success Metric**: Month-end close completes in <5 business days

### Data/AI Engineer
- **Needs**: Run ETL pipelines, track data lineage
- **Goals**: Full observability, reproducible runs
- **Success Metric**: All data transformations have lineage

### Auditor / Reviewer
- **Needs**: Reconstruct period, verify compliance
- **Goals**: Complete audit trail, immutable logs
- **Success Metric**: Period reconstruction without engineer help

### Agent (Non-Human)
- **Needs**: Execute jobs, access tools, write artifacts
- **Goals**: Deterministic runs, safe rollback
- **Success Metric**: 100% idempotent job executions

## Core Capabilities (MVP)

### 1. Job Orchestration

**Submit Jobs**:
- ETL pipelines (Bronze → Silver → Gold)
- Schema sync (Odoo → Supabase)
- Diagram export (Mermaid, PlantUML)
- Code validation (lint, type-check, test)

**Execution Targets**:
- n8n workflows
- DigitalOcean App Platform workers
- Kubernetes Jobs (future)

**Job States**:
```
queued → running → success | failed | cancelled
```

**Features**:
- Idempotency keys
- Retry with exponential backoff
- Timeout enforcement
- Priority queuing

### 2. Agent Runtime (ADK-TS)

**Typed Agents**:
- TypeScript interfaces for all agents
- Tool registry with input/output validation
- Versioned agent definitions
- Agent composition (planner → executor → verifier)

**Multi-Agent Workflows**:
- Sequential execution
- Parallel execution with join
- Conditional branching
- Error handling + rollback

**Model Support**:
- Claude (Anthropic)
- Gemini (Google)
- OpenAI (GPT-4)
- Local models (Ollama)

### 3. Docs → Code

**Watch Patterns**:
- `/spec/**/*.md` (spec bundles)
- `/docs/**/*.md` (documentation)
- Odoo module configs (`__manifest__.py`)

**Continue Integration**:
- Headless Continue worker
- Spec change → PR generation
- CI validates spec compliance
- Auto-merge if tests pass

**Validation Gates**:
- Spec bundle completeness
- Tool contract compliance
- Agent test coverage ≥80%
- No security violations

### 4. Lineage & Artifacts

**Lineage Graph** (Databricks-style):
- Inputs: Source tables, files, API endpoints
- Outputs: Target tables, files, reports
- Logs: Execution logs, error traces
- Upstream/Downstream: Full dependency graph

**Artifact Storage**:
- PDFs (BIR forms, reports)
- CSVs (exports, reconciliations)
- JSON (API responses, configs)
- Logs (structured, queryable)

**Queryable Interface**:
```sql
SELECT * FROM cr_lineage
WHERE job_id = 'month-end-close-2025-11'
  AND artifact_type = 'bir_form';
```

### 5. Business Integration

**Odoo Approvals**:
- Job submission requires approval (if configured)
- Approval workflow: submit → review → approve/reject
- Approvers mapped to Odoo roles
- Approval history tracked

**Results Write-Back**:
- Job outputs written as Odoo attachments
- Status updates posted to Odoo notes/messages
- KPIs updated in real-time (completion %, overdue tasks)

**Period Locks**:
- Finance periods locked after closing
- Jobs blocked if period locked
- Override requires Finance Director approval

## APIs (v1)

### Jobs API

**POST /jobs/run**
```json
{
  "job_type": "month_end_close",
  "params": {
    "period": "2025-11",
    "employee": "RIM"
  },
  "idempotency_key": "mec-2025-11-rim-001"
}
```

**Response**:
```json
{
  "run_id": "run_abc123",
  "status": "queued",
  "created_at": "2025-11-24T08:00:00Z"
}
```

**GET /runs/{id}**
```json
{
  "run_id": "run_abc123",
  "status": "success",
  "started_at": "2025-11-24T08:00:00Z",
  "completed_at": "2025-11-24T08:15:00Z",
  "artifacts": [
    {
      "type": "bir_form",
      "url": "https://storage.supabase.co/..."
    }
  ]
}
```

**GET /lineage/graph**
```json
{
  "nodes": [
    {"id": "odoo.account_move", "type": "source"},
    {"id": "run_abc123", "type": "job"},
    {"id": "supabase.bir_forms", "type": "target"}
  ],
  "edges": [
    {"from": "odoo.account_move", "to": "run_abc123"},
    {"from": "run_abc123", "to": "supabase.bir_forms"}
  ]
}
```

### Catalog API

**GET /catalog/search**
```json
{
  "query": "bir_form",
  "filters": {
    "type": "artifact",
    "period": "2025-11"
  }
}
```

**POST /catalog/register**
```json
{
  "name": "bir_1601c_form",
  "type": "artifact",
  "schema": {
    "period": "string",
    "employee": "string",
    "amount": "number"
  }
}
```

### Webhooks

**POST /webhooks/continue**
- Triggered on spec changes
- Generates PR via Continue
- Returns PR URL

**POST /webhooks/n8n**
- Triggered by n8n workflows
- Submits jobs to Control Room
- Returns run ID

**POST /webhooks/github**
- Triggered on PR merge
- Deploys agents/tools
- Returns deployment status

## Non-Functional Requirements

### Performance
- **Job Submission**: <100ms (p95)
- **Job Execution**: Depends on job type (ETL: <30min, BIR: <5min)
- **Lineage Query**: <1s (p95)
- **API Availability**: 99.9%

### Determinism
- Same inputs → same outputs (100%)
- Idempotency: Duplicate submissions deduplicated (100%)
- Retry safety: Jobs safe to retry N times (100%)

### Auditability
- All job runs logged (100%)
- Artifacts stored for 7 years (BIR requirement)
- Lineage queryable (100%)
- User actions traceable (100%)

### Cloud-Agnostic
- No vendor lock-in
- Can run on AWS, GCP, DigitalOcean, on-prem
- Data export: JSON, CSV, Parquet

## Success Metrics

### Platform
- **Uptime**: 99.9%
- **MTTR**: <5 minutes
- **Job Success Rate**: >95%
- **Lineage Coverage**: 100% of jobs

### Business
- **Month-End Close**: <5 business days (from 10 days)
- **BIR Compliance**: 100% on-time filings
- **Manual Interventions**: <5% of jobs
- **Audit Queries**: <1 hour to reconstruct period

### Developer
- **Spec → PR**: <10 minutes
- **PR → Deploy**: <5 minutes
- **Agent Test Coverage**: >80%
- **Tool Contract Violations**: 0

## Roadmap

### MVP (Q4 2025) — CURRENT FOCUS
- ✅ Job orchestration (queued → running → success/failed)
- ✅ ADK-TS runtime
- ✅ Lineage + artifacts
- ✅ Odoo approvals
- ⏳ Continue headless worker
- ⏳ Spec validation gate

### V1 (Q1 2026)
- Visual lineage UI (D3.js graph)
- Retry policies + circuit breakers
- RBAC / RLS (role-based access control)
- Observability (Prometheus + Grafana)

### V2 (Q2 2026)
- Kubernetes Jobs support
- Multi-tenant isolation
- Advanced scheduling (cron, triggers)
- ML model versioning + lineage

### V3 (Q3 2026)
- Real-time lineage updates
- Data quality checks (Great Expectations)
- Cost optimization (spot instances)
- Multi-cloud support

## Out of Scope (Explicitly)

- ❌ Databricks replacement (we reference their patterns, not re-implement)
- ❌ Airflow replacement (n8n handles DAGs)
- ❌ Data warehouse (Supabase PostgreSQL is sufficient)
- ❌ ML training (agents orchestrate, not train)
- ❌ Real-time streaming (batch-first approach)

## Dependencies

### Critical
- Supabase (catalog, lineage, artifacts)
- Odoo CE 18 (business state, approvals)
- n8n (workflow execution)
- DigitalOcean App Platform (job workers)

### Important
- Continue CLI (docs → PR automation)
- TypeScript (agent runtime)
- PostgreSQL 15 (Supabase backend)

### Optional
- Kubernetes (future execution target)
- Grafana (observability)
- Great Expectations (data quality)

## Risks & Mitigations

### Risk 1: Agent Hallucinations
- **Impact**: High (incorrect business logic)
- **Probability**: Medium
- **Mitigation**: Tool contracts enforce validation, human approval for critical jobs

### Risk 2: Lineage Drift
- **Impact**: Medium (audit trail incomplete)
- **Probability**: Low
- **Mitigation**: Lineage validation required before job marked success

### Risk 3: Performance Bottlenecks
- **Impact**: Medium (slow job execution)
- **Probability**: Medium
- **Mitigation**: Connection pooling, batch operations, job priority queuing

### Risk 4: Security Violations
- **Impact**: High (data breach)
- **Probability**: Low
- **Mitigation**: Tool boundaries, secret rotation, immutable audit logs

## Version History

- **v1.0.0** (2025-11-24): Initial PRD
  - Core capabilities defined
  - APIs specified
  - Success metrics set
