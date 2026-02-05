# Parallel OCR Setup Guide

This guide walks you through setting up the parallel execution system that transforms Ops Control Room into a Claude Code Web / Codex-style platform with concurrent session lanes and multi-worker execution.

## Overview

**Architecture:**
```
┌─────────────┐      ┌──────────────────┐      ┌─────────────┐
│  Figma Make │ ────▶│  Supabase Edge   │◀──── │   Worker 1  │
│  Runboard   │      │  Function (API)  │      │ (concur=4)  │
└─────────────┘      └──────────────────┘      └─────────────┘
                              ▲                        
                              │                        
                              ▼                        
                     ┌──────────────────┐      ┌─────────────┐
                     │   ops.runs       │      │   Worker 2  │
                     │   (SKIP LOCKED)  │◀──── │ (concur=4)  │
                     └──────────────────┘      └─────────────┘
```

**Key Features:**
- ✅ **Parallel sessions** (A/B/C/D lanes per session)
- ✅ **SKIP LOCKED claiming** (N workers claim runs atomically)
- ✅ **Heartbeat mechanism** (alive detection + stuck run recovery)
- ✅ **Cancelable runs** via UI
- ✅ **Realtime streaming** logs + artifacts
- ✅ **Worker-aware** execution (tracks which worker owns each run)

## Step 1: Run the Database Migration

### 1.1 Access Supabase SQL Editor

1. Go to your Supabase project dashboard
2. Click **SQL Editor** in the left sidebar
3. Click **New Query**

### 1.2 Run the Parallel Operations Migration

Copy and paste the contents of `/supabase/migrations/20250107000000_ops_parallel.sql` and execute it.

This migration creates:
- `ops.sessions` table (like "Claude Code tabs")
- New columns in `ops.runs`: `session_id`, `lane`, `priority`, `claimed_by`, `claimed_at`, `heartbeat_at`, `canceled_at`
- `ops.run_steps` table (optional, for per-step status tracking)
- `ops.claim_runs()` function (atomic SKIP LOCKED claiming)
- `ops.heartbeat_run()` function (keep-alive signal)
- `ops.cancel_run()` function (UI cancel action)
- Realtime publication for sessions + run_steps

### 1.3 Verify Migration

Run this query to verify the migration succeeded:

\`\`\`sql
-- Check sessions table
select count(*) from ops.sessions;

-- Check new run columns
select id, lane, session_id, claimed_by, heartbeat_at, canceled_at
from ops.runs
limit 5;

-- Check claim function exists
select proname from pg_proc where proname = 'claim_runs';
\`\`\`

## Step 2: Update the Edge Function Executor

The ops-executor edge function has been updated to support both:
- `/run` endpoint (single run, UI-triggered)
- `/claim` endpoint (batch claiming, worker-triggered)

**No action needed** - the file `/supabase/functions/ops-executor/index.ts` has already been updated.

To deploy the updated function:

\`\`\`bash
cd supabase
supabase functions deploy ops-executor
\`\`\`

## Step 3: Test the Runboard UI

1. **Start your Figma Make app**
2. **Navigate to the "Runboard" tab**
3. **Create a session:**
   - Click "New Session"
   - Enter an intent (e.g., "Deploy prod + run migrations")
   - Click "Create"
4. **Run tasks in parallel lanes:**
   - Each lane (A/B/C/D) has an input box
   - Enter different intents in multiple lanes
   - Click the Play button for each
   - Watch them execute concurrently

## Step 4: Deploy Parallel Workers (Optional)

For production-grade parallel execution, deploy worker processes that poll the `/claim` endpoint.

### 4.1 Local Testing (Development)

\`\`\`bash
cd workers
npm install

export SUPABASE_FN_URL="https://<project-ref>.supabase.co/functions/v1/ops-executor"
export SUPABASE_ANON="<your-anon-key>"
export WORKER_ID="ocr-worker-local"
export CONCURRENCY=4

npm run dev
\`\`\`

### 4.2 Production Deployment (DigitalOcean / K8s)

See `/workers/README.md` for detailed deployment instructions including:
- **DigitalOcean App Platform** (Dockerfile + doctl)
- **Kubernetes** (Deployment YAML with replicas)
- **GitHub Actions** (long-running workflow)

## Step 5: Verify Parallel Execution

### 5.1 Check Active Workers

\`\`\`sql
select distinct claimed_by, count(*) as active_runs
from ops.runs
where status = 'running'
group by claimed_by;
\`\`\`

### 5.2 Watch Runs Being Claimed (Realtime)

\`\`\`sql
select id, status, lane, claimed_by, claimed_at, heartbeat_at
from ops.runs
order by created_at desc
limit 20;
\`\`\`

### 5.3 Check for Stuck Runs

\`\`\`sql
select id, claimed_by, heartbeat_at,
       extract(epoch from (now() - heartbeat_at)) as seconds_since_heartbeat
from ops.runs
where status = 'running'
  and heartbeat_at < now() - interval '10 seconds';
\`\`\`

## Step 6: Understanding Session Lanes

**Sessions** are like "Claude Code workspace tabs":
- Each session has a title + intent
- Sessions contain multiple runs across different lanes (A/B/C/D)
- UI shows all lanes for the active session

**Lanes** are parallel execution tracks:
- Lane A, B, C, D (can add more if needed)
- Each lane can run one task at a time
- Lanes update independently via realtime subscriptions

**Example workflow:**
1. Create session: "Production deployment + hotfix"
2. Lane A: "Deploy v2.3.0 to prod"
3. Lane B: "Apply schema migration 003"
4. Lane C: "Generate deployment spec"
5. Lane D: "Run smoke tests"

All four lanes execute concurrently, each with its own live log stream.

## Step 7: Scaling

### Horizontal Scaling (More Workers)

Deploy multiple worker instances:

\`\`\`bash
# Worker 1
WORKER_ID=ocr-worker-1 CONCURRENCY=4 node workers/ocr-worker.js

# Worker 2
WORKER_ID=ocr-worker-2 CONCURRENCY=4 node workers/ocr-worker.js

# Worker 3
WORKER_ID=ocr-worker-3 CONCURRENCY=4 node workers/ocr-worker.js
\`\`\`

Total capacity: 3 workers × 4 concurrency = **12 parallel runs**

### Vertical Scaling (More Concurrency per Worker)

Increase the `CONCURRENCY` env var:

\`\`\`bash
WORKER_ID=ocr-worker-1 CONCURRENCY=8 node workers/ocr-worker.js
\`\`\`

### Priority Queue

Set the `priority` field on runs (lower = higher priority):

\`\`\`ts
await createRun({
  session_id: sessionId,
  lane: "A",
  intent: "Critical hotfix",
  priority: 1, // will be claimed before priority 100
});
\`\`\`

## Troubleshooting

### Workers Not Claiming Runs

1. **Check worker logs** for connection errors
2. **Verify SUPABASE_FN_URL** is correct
3. **Check RPC permissions** (anon role should be able to call `claim_runs`)

\`\`\`sql
-- Grant claim_runs to anon (if needed)
grant execute on function ops.claim_runs to anon;
\`\`\`

### Runs Stuck in "queued"

1. **No workers running** - start at least one worker
2. **Workers crashed** - check worker logs
3. **RPC function errors** - check Supabase logs

### Runs Stuck in "running"

1. **Worker crashed** - heartbeat will expire after 5 minutes, allowing re-claim
2. **Check heartbeat_at timestamp:**

\`\`\`sql
select id, claimed_by, heartbeat_at,
       now() - heartbeat_at as staleness
from ops.runs
where status = 'running'
order by heartbeat_at asc;
\`\`\`

### Realtime Updates Not Working

1. **Check Realtime is enabled** in Supabase dashboard
2. **Verify publication includes tables:**

\`\`\`sql
select schemaname, tablename
from pg_publication_tables
where pubname = 'supabase_realtime';
\`\`\`

Should include:
- `ops.runs`
- `ops.run_events`
- `ops.artifacts`
- `ops.sessions`
- `ops.run_steps`

## Next Steps

1. **Wire real MCP tools** - Replace simulation in executor with actual tool calls
2. **Add workspace isolation** - Checkout repos + create branches per lane
3. **Implement diff artifacts** - Stream code changes to UI
4. **Add push notifications** - Webhook to Poke/Slack when runs need input
5. **Create template library** - Pre-built runbooks for common tasks

## Files Changed

- ✅ `/supabase/migrations/20250107000000_ops_parallel.sql` (new)
- ✅ `/supabase/functions/ops-executor/index.ts` (updated)
- ✅ `/src/lib/runs.ts` (updated: sessions, createRun params, cancelRun)
- ✅ `/src/app/components/Runboard.tsx` (new)
- ✅ `/src/app/components/RunLane.tsx` (new)
- ✅ `/src/app/App.tsx` (updated: added Runboard tab)
- ✅ `/workers/ocr-worker.ts` (new)
- ✅ `/workers/package.json` (new)
- ✅ `/workers/README.md` (new)

## Resources

- [Supabase Realtime](https://supabase.com/docs/guides/realtime)
- [PostgreSQL SKIP LOCKED](https://www.2ndquadrant.com/en/blog/what-is-select-skip-locked-for-in-postgresql-9-5/)
- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
