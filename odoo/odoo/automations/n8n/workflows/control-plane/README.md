# Control Plane Workflows

n8n workflows that use **Supabase as the control plane** for job orchestration, health monitoring, and audit trails.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONTROL PLANE (Supabase)                      │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  observability.jobs      → Job queue + state machine        ││
│  │  observability.job_runs  → Execution history                ││
│  │  observability.job_events→ Audit trail                      ││
│  │  observability.services  → Service registry                 ││
│  │  observability.service_health → Health samples              ││
│  │  ops.events (view)       → Event-style interface            ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ HTTP/PostgREST
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR (n8n)                            │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐      │
│  │ deploy-trigger │ │ health-check   │ │ backup-        │      │
│  │                │ │ -scheduler     │ │ scheduler      │      │
│  └────────────────┘ └────────────────┘ └────────────────┘      │
│         │                   │                   │                │
│         ▼                   ▼                   ▼                │
│  ┌────────────────────────────────────────────────────────────┐│
│  │  1. Record event in Supabase (enqueue_job)                 ││
│  │  2. Execute action (SSH/HTTP/Docker)                       ││
│  │  3. Update job status (complete_job/fail_job)              ││
│  │  4. Create alerts on failure (enqueue alert job)           ││
│  └────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXECUTION TARGETS                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐│
│  │ Odoo CE    │  │ Vercel     │  │ DO Droplet │  │ S3/Spaces  ││
│  │ (ERP)      │  │ (Frontend) │  │ (Docker)   │  │ (Backups)  ││
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## Workflow Pattern

All control plane workflows follow this pattern:

```
Trigger → Normalize → Record Event → Execute → Update Status → Alert on Failure
```

1. **Trigger**: Webhook, schedule, or external event
2. **Normalize**: Validate and transform input to standard schema
3. **Record Event**: `POST /rest/v1/rpc/enqueue_job` with correlation_id
4. **Execute**: Run the actual work (deploy, backup, health check)
5. **Update Status**: `POST /rest/v1/rpc/complete_job` or `fail_job`
6. **Alert**: On failure, enqueue an alert job for notification

## Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `deploy-trigger.json` | Webhook | Deploy to staging/production |
| `health-check-scheduler.json` | Every 5 min | Check all registered services |
| `backup-scheduler.json` | Daily 3 AM | Backup databases to DO Spaces |

## Required Environment Variables

Set these in n8n:

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key

# Optional: DO Spaces
DO_SPACES_BUCKET=odoo-backups

# Optional: Vercel
VERCEL_DEPLOY_HOOK_URL=https://api.vercel.com/v1/integrations/deploy/...
```

## Required Supabase Functions

These workflows use the functions defined in `db/migrations/20260121_observability_schema.sql`:

- `observability.enqueue_job(source, job_type, payload, context, priority)`
- `observability.complete_job(job_id, result, metrics)`
- `observability.fail_job(job_id, error)`
- `observability.record_health(service_id, status, response_time_ms, ...)`

## Import Workflows

```bash
# Using n8n CLI (if available)
n8n import:workflow --input=n8n/workflows/control-plane/deploy-trigger.json

# Or via API
curl -X POST "https://n8n.example.com/api/v1/workflows" \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d @n8n/workflows/control-plane/deploy-trigger.json
```

## Test Deploy Trigger

```bash
# Request a staging deploy
curl -X POST "https://n8n.example.com/webhook/deploy-request" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "manual",
    "target": "staging",
    "service": "odoo-core",
    "commit_sha": "HEAD",
    "triggered_by": "test"
  }'
```

## Query Control Plane

```sql
-- Recent jobs
SELECT id, source, job_type, status, created_at
FROM observability.jobs
ORDER BY created_at DESC
LIMIT 20;

-- Queue depth
SELECT * FROM ops.get_queue_depth();

-- Trace a correlation
SELECT * FROM ops.get_trace('deploy-20260124T030000');

-- Health summary
SELECT * FROM observability.get_health_summary();
```

## Key Principles

1. **Supabase is truth**: All job state lives in Supabase, not n8n
2. **n8n is stateless**: Workflows don't hold state; they read/write Supabase
3. **Correlation IDs everywhere**: Every job has a `correlation_id` for tracing
4. **Fail loudly**: On error, create an alert job and update status
5. **Audit everything**: Every state change creates a `job_events` row
