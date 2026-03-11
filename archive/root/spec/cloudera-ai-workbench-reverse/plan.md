# WorkbenchX — Implementation Plan

## Architecture

### Control plane (Supabase)

| Table | Purpose |
|-------|---------|
| `ops.projects` | Project registry with repo + dataset + runtime refs |
| `ops.datasets` | Dataset refs only (not raw data) |
| `ops.runtimes` | Approved container image allowlist |
| `ops.sessions` | Interactive compute session lifecycle |
| `ops.experiments` / `ops.experiment_runs` | Experiment tracking with params/metrics |
| `ops.models` / `ops.model_deployments` | Model registry and endpoint management |
| `ops.apps` / `ops.app_deployments` | Analytical app deployments |
| `ops.run_events` | Append-only event log (existing) |
| `ops.artifacts` | Indexed pointers to Supabase Storage |

### Execution plane

**Vercel Sandbox** for:
- Safe code execution and reproduction
- Small/medium runs (tests, builds, evaluations)
- Evidence: `ops.sandbox_runs` (migration `20260301000080`)

**DigitalOcean runners** for:
- Long-running processes and GPU workloads
- Ingestion jobs and backfills
- Evidence: `ops.run_events` + `ops.artifacts`

### Data plane (Supabase Postgres + Storage)

* Governed access via: RLS policies, RPC functions, signed URLs for storage artifacts
* Vector (`pgvector`) for RAG use-cases if enabled

### Work surfaces (ops-console routes)

| Route | Purpose | Maturity |
|-------|---------|----------|
| `/studio` | Chat → code changes (Lovable-style) | scaffold |
| `/sessions` | Interactive compute sessions | scaffold |
| `/experiments` | Experiment tracking + comparisons | scaffold |
| `/models` | Model deployments + endpoints | scaffold |
| `/apps` | Analytical app deployments + logs | scaffold |
| `/templates` | Accelerators marketplace | scaffold |

### Provider adapters

```yaml
sandbox_provider:
  options: [vercel_sandbox, do_runner]
  ssot: ssot/providers/vercel/sandbox.yaml

inference_provider:
  options: [ai_gateway, do_gradient, local_llm]
  ssot: ssot/providers/ai/provider.yaml

storage_provider:
  options: [supabase_storage, s3_compatible]
  default: supabase_storage
```

## Security model

* Project membership enforced via Supabase Auth + RLS
* Runtimes allowlist with digest pinning
* Audit trail: immutable `ops.run_events`
* Artifact signing: sha256 stored alongside URLs

## Operational model

Every operation:
1. Enqueues a job → produces a `run_id`
2. Logs events to `ops.run_events` (append-only)
3. Stores artifacts in `ops.artifacts` + Supabase Storage
4. Auto-remediation (optional): failed runs can trigger FixBot to propose PRs — always PR-only, never direct push

## Phase 0 (this PR — foundation)

1. SSOT provider declarations: `ssot/providers/vercel/sandbox.yaml`, `ssot/providers/ai/provider.yaml`
2. `ops.sandbox_runs` migration (`20260301000080`)
3. Streaming AI route: `apps/ops-console/app/api/ai/stream/route.ts`

## Phase 1 (next PRs — P0 data model)

Per `tasks.md` items 1–3:
1. Create `ops.projects`, `ops.datasets`, `ops.runtimes` migration
2. Create `ops.sessions` migration
3. Create `ops.experiments`, `ops.experiment_runs` migration
