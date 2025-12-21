# Control Room API — Constitution

> **Version**: 1.0.0
> **Status**: Active
> **Last Updated**: 2024-12-21

---

## 1. Purpose

Control Room API is the **unified orchestration layer** that mirrors Databricks Control Room patterns using our stack (Odoo CE 18 + OCA, Supabase, n8n, DO/K8s). It provides:

- **Job orchestration** (Spark ETL, schema migrations, diagram exports)
- **Data lineage tracking** (cross-system graph)
- **Continue CLI integration** (spec → code → execution → callback)
- **Artifact management** (code files, diagrams, SQL, notebooks)

The key insight: Continue CLI generates code, Control Room validates + executes + tracks lineage.

---

## 2. Governing Principles

### 2.1 Spec-First Execution

Every job starts with a **spec** (natural language description). The execution loop:

```
spec → Continue (code gen) → Control Room (validate) → Runner (execute) → Callback (notify)
```

### 2.2 Databricks Parity Without Lock-In

We map Databricks concepts to our stack:

| Databricks Concept | Control Room Equivalent |
|-------------------|------------------------|
| Unity Catalog (UC) | Supabase + catalog tables |
| Delta Lake Bronze/Silver/Gold | Schemas + materialized views |
| Jobs API | `/api/v1/jobs/run` endpoint |
| Lineage API | Graph tables + RPC |
| MLflow Registry | Artifact storage |
| Workflows | K8s Jobs / DO runners |

### 2.3 Headless-First Design

All operations must work in:
- **CI/CD pipelines** (`cn -p` headless mode)
- **GitHub Actions** (automated validation)
- **Interactive IDE** (Continue plugin callbacks)

### 2.4 Immutable Lineage

Lineage graph is append-only:
- Never delete lineage edges
- Soft-delete with `deleted_at` timestamp
- Full audit trail of data flow

---

## 3. Architecture Boundaries

### 3.1 Control Room Core (This System)

- Job intake and validation
- Execution dispatching (K8s/DO)
- Lineage graph management
- Artifact storage and retrieval
- Webhook callbacks

### 3.2 Execution Surfaces (External)

- **K8s Jobs**: Heavy compute (Spark, model training)
- **DO Droplet Runner**: Simple tasks
- **Continue CLI**: Code generation
- **n8n**: Integration workflows

### 3.3 Integration Patterns

```
┌─────────────────────────────────────────────────────────────┐
│                    CONTROL ROOM API                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │    Jobs     │  │   Lineage   │  │  Artifacts  │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│         │               │               │                    │
│  ┌─────────────────────────────────────────────────┐        │
│  │              EXECUTION DISPATCHER                │        │
│  │         (K8s Jobs / DO Runners)                 │        │
│  └─────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
   ┌──────────┐        ┌──────────┐        ┌──────────┐
   │ Continue │        │   K8s    │        │   n8n    │
   │   CLI    │        │   Jobs   │        │ Workflow │
   └──────────┘        └──────────┘        └──────────┘
```

---

## 4. Job Types

| Job Type | Description | Executor |
|----------|-------------|----------|
| `spark_etl` | Spark-based ETL pipelines | K8s Job |
| `diagram_export` | Visio→DrawIO→PNG/SVG | Docker container |
| `schema_migration` | Database schema changes | K8s Job |
| `kb_catalog` | Knowledge base cataloging | n8n workflow |
| `code_validation` | Lint, test, security scan | K8s Job |

---

## 5. Governance

### 5.1 Change Control

- All schema changes require migrations
- Breaking API changes require version bump
- Deprecations have 2-release sunset

### 5.2 Execution Limits

| Resource | Limit |
|----------|-------|
| Job timeout | 10 minutes (default) |
| Max file size | 50 MB per artifact |
| Concurrent jobs | 10 per tenant |
| Retry attempts | 3 |

### 5.3 Callback Requirements

All jobs must support:
- `on_complete`: Success callback
- `on_fail`: Failure callback
- `on_progress`: Optional progress updates

---

## 6. Security & Compliance

### 6.1 Authentication

- Bearer token (JWT) with claims:
  - `tenant_id`: Multi-tenant isolation
  - `user_id`: Actor identification
  - `role`: Permission level

### 6.2 Authorization

| Role | Permissions |
|------|-------------|
| `viewer` | Read jobs, runs, artifacts |
| `operator` | + Create/cancel jobs |
| `admin` | + Delete artifacts, manage lineage |

### 6.3 Data Classification

- **Internal**: Job metadata, run status
- **Confidential**: Source code, credentials
- **Restricted**: Secrets (never stored, passed via env)

---

## 7. Non-Goals

This system does NOT:
- Replace Databricks entirely (just key patterns)
- Execute arbitrary user code (sandboxed only)
- Provide data warehouse storage (use Supabase)
- Implement full MLflow (artifact storage only)

---

## 8. Success Metrics

| Metric | Target |
|--------|--------|
| Job success rate | > 99% |
| Mean execution time | < 5 min |
| Lineage coverage | 100% of data flows |
| Callback reliability | 100% delivery |

---

## Appendix A: Related Documents

- `prd.md` — Product Requirements
- `plan.md` — Implementation Plan
- `tasks.md` — Task Checklist
