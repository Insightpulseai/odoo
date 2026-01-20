# MCP Jobs System

**Purpose**: Central job orchestration + observability service for MCP agents across IPAI stack

**Status**: ✅ Implemented (Ready for deployment)

---

## Overview

The MCP Jobs System provides a shared jobs + observability backend for all MCP-enabled applications: Odoo, Supabase Edge Functions, Vercel apps, and n8n workflows.

**Key Features**:
- Centralized job queue with state machine tracking
- Worker claim system with atomic job locking
- Automatic retry logic with exponential backoff
- Dead letter queue for failed jobs
- Detailed execution logs and event tracking
- Metrics aggregation for monitoring
- Next.js UI app for job visualization

---

## Architecture

```
MCP-Enabled Apps (Odoo, n8n, Vercel, Edge Functions)
    ↓ HTTP POST /api/jobs/enqueue
v0 Next.js App (mcp-jobs UI)
    ↓ Supabase Client
Supabase PostgreSQL (mcp_jobs schema)
    ├── jobs (queue + state machine)
    ├── job_runs (execution history)
    ├── job_events (detailed logs)
    ├── dead_letter_queue (failed jobs after max retries)
    └── metrics (aggregated stats)
```

---

## Components

### 1. Database Schema (`mcp_jobs`)

**Location**: `supabase/migrations/20260120_mcp_jobs_schema.sql`

**Tables**:
- **`jobs`**: Main job queue with state machine
- **`job_runs`**: Execution history for each run/retry
- **`job_events`**: Detailed event log (started, progress, completed, failed)
- **`dead_letter_queue`**: Failed jobs after max retries exhausted
- **`metrics`**: Aggregated job metrics per hour

**Functions**:
- **`enqueue_job()`**: Add new job to queue
- **`claim_next_job()`**: Worker claims next available job (atomic with SKIP LOCKED)
- **`complete_job()`**: Mark job as completed
- **`fail_job()`**: Mark job as failed, retry or move to DLQ

### 2. Next.js UI App (v0-generated)

**Location**: `mcp/servers/mcp-jobs/` (git submodule)
**Repository**: https://github.com/jgtolentino/mcp-jobs.git
**Deployed**: https://v0-open-in-v0-aw4uzb0sw-tbwa.vercel.app/

**Purpose**: Job visualization dashboard, manual job enqueue, DLQ management

**API Routes**:
- **POST `/api/jobs/enqueue`**: Enqueue new job
- **GET `/api/jobs/list`**: List jobs with filters (source, jobType, status)
- **GET `/api/jobs/[id]`**: Get job details with runs and events
- **DELETE `/api/jobs/[id]`**: Cancel queued job

**Client Library**: `lib/supabaseJobsClient.ts`
- TypeScript client for all job operations
- Type-safe interfaces for Job, JobRun, JobEvent
- Helper functions: `enqueueJob()`, `listJobs()`, `getJobStats()`

### 3. Integration Pattern

**Python Example** (Odoo, discovery scripts):
```python
import os
import requests

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

def enqueue_discovery_job(source: str, payload: dict):
    """Enqueue infrastructure discovery job"""
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/rpc/enqueue_job",
        headers={
            'Authorization': f'Bearer {SUPABASE_SERVICE_ROLE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        },
        json={
            'p_source': source,
            'p_job_type': 'discovery',
            'p_payload': payload,
            'p_priority': 5
        }
    )
    response.raise_for_status()
    return response.json()

# Usage
job_id = enqueue_discovery_job('vercel', {
    'project_id': 'xyz123',
    'fetch_integrations': True
})
print(f"Job ID: {job_id}")
```

**Bash Example** (DigitalOcean, Docker discovery):
```bash
#!/bin/bash

SUPABASE_URL="${SUPABASE_URL}"
SUPABASE_SERVICE_ROLE_KEY="${SUPABASE_SERVICE_ROLE_KEY}"

enqueue_job() {
    local source="$1"
    local job_type="$2"
    local payload="$3"

    curl -s -X POST "$SUPABASE_URL/rest/v1/rpc/enqueue_job" \
        -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
        -H "Content-Type: application/json" \
        -H "Prefer: return=representation" \
        -d "{
            \"p_source\": \"$source\",
            \"p_job_type\": \"$job_type\",
            \"p_payload\": $payload
        }"
}

# Usage
PAYLOAD=$(cat <<EOF
{
    "droplet_id": "12345",
    "action": "discovery"
}
EOF
)

JOB_ID=$(enqueue_job "digitalocean" "discovery" "$PAYLOAD")
echo "Job ID: $JOB_ID"
```

**n8n Workflow Example**:
```json
{
  "nodes": [
    {
      "parameters": {
        "url": "={{ $env.SUPABASE_URL }}/rest/v1/rpc/enqueue_job",
        "authentication": "headerAuth",
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "p_source",
              "value": "n8n"
            },
            {
              "name": "p_job_type",
              "value": "sync"
            },
            {
              "name": "p_payload",
              "value": "={{ $json }}"
            }
          ]
        }
      },
      "name": "Enqueue Job",
      "type": "n8n-nodes-base.httpRequest"
    }
  ]
}
```

---

## Deployment

### Prerequisites

**Environment Variables**:
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY` - Admin access key
- `NEXT_PUBLIC_SUPABASE_URL` - Client-safe URL (for v0 app)

### 1. Deploy Database Schema

```bash
# Via psql
psql "$POSTGRES_URL" -f supabase/migrations/20260120_mcp_jobs_schema.sql

# OR via Supabase CLI
supabase db push
```

**Verification**:
```sql
-- Check tables created
SELECT schemaname, tablename
FROM pg_tables
WHERE schemaname = 'mcp_jobs'
ORDER BY tablename;

-- Expected: dead_letter_queue, job_events, job_runs, jobs, metrics
```

### 2. Deploy v0 App to Vercel

**Note**: App is already deployed to https://v0-open-in-v0-aw4uzb0sw-tbwa.vercel.app/

**Update Environment Variables** (Vercel Dashboard):
```
NEXT_PUBLIC_SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>
```

**Manual Redeploy** (if needed):
```bash
cd mcp/servers/mcp-jobs
vercel --prod
```

### 3. Test API Endpoints

```bash
# Test enqueue
curl -X POST "https://v0-open-in-v0-aw4uzb0sw-tbwa.vercel.app/api/jobs/enqueue" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "test",
    "jobType": "discovery",
    "payload": {"test": true}
  }'

# Expected: {"ok":true,"jobId":"<uuid>"}

# Test list
curl "https://v0-open-in-v0-aw4uzb0sw-tbwa.vercel.app/api/jobs/list?limit=10"

# Test get job
curl "https://v0-open-in-v0-aw4uzb0sw-tbwa.vercel.app/api/jobs/[id]?id=<uuid>"
```

---

## Usage Patterns

### Discovery Jobs (Infra Memory Job)

Integrate with all 5 discovery scripts to track execution:

```python
# Before discovery
job_id = enqueue_discovery_job('vercel', {'full_scan': True})

# During discovery
# ... perform discovery logic ...

# After discovery (complete or fail)
if success:
    complete_job(job_id, result={'nodes_count': 42, 'edges_count': 38})
else:
    fail_job(job_id, error='Discovery timeout')
```

### Scheduled Jobs (BIR, Month-End Close)

```python
# Schedule monthly BIR job
job_id = enqueue_job(
    source='odoo',
    job_type='bir_1601c',
    payload={'period': '2026-01', 'agency': 'RIM'},
    options={
        'priority': 1,  # High priority
        'scheduledAt': '2026-02-01T00:00:00Z',  # Run on specific date
        'maxRetries': 5  # More retries for critical jobs
    }
)
```

### Real-time Job Status (UI)

```typescript
// In Next.js page component
import { useEffect, useState } from 'react'

export default function JobMonitor({ jobId }: { jobId: string }) {
  const [job, setJob] = useState(null)

  useEffect(() => {
    const interval = setInterval(async () => {
      const response = await fetch(`/api/jobs/${jobId}`)
      const data = await response.json()
      setJob(data.job)

      // Stop polling when job finishes
      if (['completed', 'failed', 'cancelled'].includes(data.job.status)) {
        clearInterval(interval)
      }
    }, 1000) // Poll every second

    return () => clearInterval(interval)
  }, [jobId])

  return (
    <div>
      <h3>Job Status: {job?.status}</h3>
      {job?.error && <p>Error: {job.error}</p>}
    </div>
  )
}
```

---

## Monitoring & Alerts

### Key Metrics

```sql
-- Job queue depth by source
SELECT
    source,
    status,
    COUNT(*) as count,
    MIN(created_at) as oldest_job
FROM mcp_jobs.jobs
WHERE status IN ('queued', 'running')
GROUP BY source, status
ORDER BY count DESC;

-- Success rate by source and job_type
SELECT
    source,
    job_type,
    COUNT(*) FILTER (WHERE status = 'completed') as completed,
    COUNT(*) FILTER (WHERE status = 'failed') as failed,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE status = 'completed') /
        NULLIF(COUNT(*) FILTER (WHERE status IN ('completed', 'failed')), 0),
        2
    ) as success_rate_pct
FROM mcp_jobs.jobs
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY source, job_type
ORDER BY success_rate_pct ASC;

-- Dead letter queue (unresolved failures)
SELECT
    source,
    job_type,
    COUNT(*) as count,
    MAX(created_at) as last_failure
FROM mcp_jobs.dead_letter_queue
WHERE NOT resolved
GROUP BY source, job_type
ORDER BY count DESC;

-- Average job duration by type
SELECT
    j.source,
    j.job_type,
    COUNT(*) as total_jobs,
    AVG(EXTRACT(EPOCH FROM (j.finished_at - j.started_at)) * 1000) as avg_duration_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (j.finished_at - j.started_at)) * 1000) as p95_duration_ms
FROM mcp_jobs.jobs j
WHERE
    j.finished_at IS NOT NULL
    AND j.created_at > NOW() - INTERVAL '7 days'
GROUP BY j.source, j.job_type
ORDER BY p95_duration_ms DESC;
```

### Alert Thresholds

**Critical**:
- Queue depth >100 jobs for single source
- Dead letter queue >10 unresolved failures
- Success rate <80% for any job type
- Job stuck in 'running' for >1 hour

**Warning**:
- Queue depth >50 jobs
- Dead letter queue >5 unresolved failures
- Success rate <90%
- P95 duration >30 seconds

---

## Troubleshooting

### Job Stuck in "queued"

**Cause**: No worker claiming jobs, or all workers busy
**Fix**:
1. Check worker processes are running
2. Verify worker can connect to Supabase
3. Check worker logs for errors
4. Manual claim: `SELECT mcp_jobs.claim_next_job('manual-worker');`

### Job Stuck in "running"

**Cause**: Worker crashed or lost connection
**Fix**:
```sql
-- Reset stuck jobs (running >1 hour)
UPDATE mcp_jobs.jobs
SET
    status = 'queued',
    worker_id = NULL,
    started_at = NULL
WHERE
    status = 'running'
    AND started_at < NOW() - INTERVAL '1 hour';
```

### High Failure Rate

**Cause**: Payload validation, external service errors, timeout
**Fix**:
1. Check dead letter queue for error patterns
2. Review recent job events for stack traces
3. Adjust max_retries or retry_delay_seconds
4. Fix root cause in worker code

### Dead Letter Queue Growing

**Cause**: Persistent failures not being resolved
**Fix**:
```sql
-- Investigate most common failures
SELECT
    final_error,
    COUNT(*) as count
FROM mcp_jobs.dead_letter_queue
WHERE NOT resolved
GROUP BY final_error
ORDER BY count DESC
LIMIT 10;

-- Mark as resolved after manual fix
UPDATE mcp_jobs.dead_letter_queue
SET
    resolved = true,
    resolved_at = NOW(),
    resolved_by = 'admin',
    resolution_notes = 'Fixed upstream service issue'
WHERE id = '<dlq-item-id>';
```

---

## Production Checklist

- [x] Database schema deployed to Supabase
- [ ] v0 app environment variables configured
- [ ] v0 app deployed to Vercel
- [ ] Test API endpoints (enqueue, list, get)
- [ ] Integrate with discovery scripts (5 sources)
- [ ] Setup monitoring alerts (queue depth, failure rate)
- [ ] Document worker implementation (separate service)
- [ ] Test retry logic and DLQ behavior
- [ ] Setup cron job for metrics aggregation
- [ ] Add dashboards to v0 UI app

---

**Last Updated**: 2026-01-20
**Status**: Ready for deployment
**Next Steps**:
1. Deploy schema to Supabase
2. Configure v0 app environment variables
3. Test API endpoints end-to-end
4. Integrate with discovery scripts
5. Implement worker service (separate repo/service)
