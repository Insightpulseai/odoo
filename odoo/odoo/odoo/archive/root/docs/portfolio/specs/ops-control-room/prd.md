# Ops Control Room — Product Requirements Document (PRD)

**Spec Bundle**: `spec/ops-control-room/`
**Status**: Canonical
**Last Updated**: 2026-01-08

---

## 0) Problem Statement

**Current State**:
- Manual runbook execution is error-prone and slow
- No visibility into parallel task execution
- Claude Code Web / Codex Web UI shows "Invalid schema: ops" errors
- PostgREST only exposes `public` schema by default
- No atomic claiming mechanism → risk of double execution
- No stuck-run recovery → zombie processes accumulate
- No real-time telemetry → operators fly blind

**Target State**:
- Parallel execution across 4 lanes (A, B, C, D) per session
- Atomic run claiming with `FOR UPDATE SKIP LOCKED`
- Real-time status updates (<2s latency)
- Automatic stuck-run recovery (30s timeout)
- Clean schema isolation (`ops` schema, not polluting `public`)
- Production-grade reliability with heartbeats and health checks

---

## 1) Solution Overview

**Architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│                    Ops Control Room                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Vercel UI (Runboard)                                        │
│       │                                                      │
│       │ HTTP + WebSocket (Realtime)                          │
│       │                                                      │
│  ┌────▼──────────────────────────────────────┐               │
│  │  Supabase (Control Plane)                 │               │
│  │  ├── PostgreSQL (ops schema)              │               │
│  │  │   ├── ops.sessions                     │               │
│  │  │   ├── ops.runs                         │               │
│  │  │   ├── ops.run_events                   │               │
│  │  │   └── ops.artifacts                    │               │
│  │  ├── Realtime (postgres_changes)          │               │
│  │  ├── Storage (artifacts bucket)           │               │
│  │  └── Edge Function (ops-executor)         │               │
│  └────┬──────────────────────────────────────┘               │
│       │                                                      │
│       │ RPC / HTTP                                           │
│       │                                                      │
│  ┌────▼──────────────────────────────────────┐               │
│  │  DigitalOcean Workers (Executors)         │               │
│  │  ├── Worker 1 (lanes: A, B, C, D)         │               │
│  │  ├── Worker 2 (lanes: A, B, C, D)         │               │
│  │  └── Worker N (lanes: A, B, C, D)         │               │
│  └────────────────────────────────────────────┘               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Stack**:
- **UI**: Vercel (React/Next.js)
- **Control Plane**: Supabase (PostgreSQL + Realtime + Edge Functions + Storage)
- **Workers**: DigitalOcean App Platform or Kubernetes
- **Realtime**: Supabase Realtime subscriptions

---

## 2) Schema Access Fix (Blocker Resolution)

**Problem**: PostgREST only exposes `public` schema → "Invalid schema: ops" errors

**Solution Options**:

### Option A: Expose `ops` Schema in PostgREST (Recommended)

```sql
-- 1) Create ops schema
CREATE SCHEMA IF NOT EXISTS ops;

-- 2) Update PostgREST config (supabase/config.toml or dashboard)
-- db-schemas = "public,ops,graphql_public"

-- 3) Grant usage
GRANT USAGE ON SCHEMA ops TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA ops TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA ops TO anon, authenticated;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA ops TO anon, authenticated;

-- 4) RLS policies apply normally
ALTER TABLE ops.runs ENABLE ROW LEVEL SECURITY;
```

**Pros**: Direct access, clean separation, standard Supabase pattern
**Cons**: Requires PostgREST config change (one-time)

### Option B: Public Views Over ops.* (Fallback)

```sql
-- Create views in public schema
CREATE OR REPLACE VIEW public.ops_runs AS
SELECT * FROM ops.runs;

CREATE OR REPLACE VIEW public.ops_sessions AS
SELECT * FROM ops.sessions;

-- RLS on views
ALTER VIEW public.ops_runs OWNER TO authenticated;
CREATE POLICY "ops_runs_policy" ON public.ops_runs FOR ALL USING (true);
```

**Pros**: Works without PostgREST config change
**Cons**: Duplicate layer, less clean, harder to maintain

**Recommendation**: Use Option A (expose `ops` schema in PostgREST)

---

## 3) Data Model

### 3.1) ops.sessions

```sql
CREATE TABLE ops.sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

  -- Metadata
  name TEXT NOT NULL,
  description TEXT,
  triggered_by TEXT, -- 'manual', 'schedule', 'github', 'spec_kit'

  -- Status
  status TEXT NOT NULL DEFAULT 'active', -- active | completed | cancelled

  -- Telemetry
  total_runs INT DEFAULT 0,
  succeeded_runs INT DEFAULT 0,
  failed_runs INT DEFAULT 0,

  -- Context
  context JSONB DEFAULT '{}'::jsonb,

  CONSTRAINT sessions_status_check CHECK (status IN ('active', 'completed', 'cancelled'))
);

CREATE INDEX idx_sessions_status ON ops.sessions(status);
CREATE INDEX idx_sessions_created_at ON ops.sessions(created_at DESC);
```

### 3.2) ops.runs

```sql
CREATE TYPE ops.lane_type AS ENUM ('A', 'B', 'C', 'D');

CREATE TABLE ops.runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID NOT NULL REFERENCES ops.sessions(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

  -- Execution
  lane ops.lane_type NOT NULL,
  priority INT DEFAULT 0, -- higher = more urgent

  -- Status
  status TEXT NOT NULL DEFAULT 'queued', -- queued | claimed | running | succeeded | failed | cancelled
  claimed_by TEXT, -- worker_id
  claimed_at TIMESTAMPTZ,
  started_at TIMESTAMPTZ,
  finished_at TIMESTAMPTZ,
  heartbeat_at TIMESTAMPTZ,

  -- Payload
  kind TEXT NOT NULL, -- 'spec_kit_generate', 'github_deploy', 'docker_build', etc.
  params JSONB NOT NULL DEFAULT '{}'::jsonb,

  -- Results
  result JSONB,
  error JSONB, -- { type, message, stack, context }

  CONSTRAINT runs_status_check CHECK (status IN ('queued', 'claimed', 'running', 'succeeded', 'failed', 'cancelled'))
);

CREATE INDEX idx_runs_session ON ops.runs(session_id);
CREATE INDEX idx_runs_status_lane ON ops.runs(status, lane);
CREATE INDEX idx_runs_priority ON ops.runs(priority DESC, created_at ASC);
CREATE INDEX idx_runs_heartbeat ON ops.runs(heartbeat_at) WHERE status IN ('claimed', 'running');
```

### 3.3) ops.run_events

```sql
CREATE TABLE ops.run_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id UUID NOT NULL REFERENCES ops.runs(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

  -- Event
  level TEXT NOT NULL, -- 'debug', 'info', 'warn', 'error'
  message TEXT NOT NULL,
  data JSONB,

  CONSTRAINT events_level_check CHECK (level IN ('debug', 'info', 'warn', 'error'))
);

CREATE INDEX idx_events_run ON ops.run_events(run_id, created_at DESC);
```

### 3.4) ops.artifacts

```sql
CREATE TABLE ops.artifacts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  run_id UUID NOT NULL REFERENCES ops.runs(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

  -- Artifact
  kind TEXT NOT NULL, -- 'file', 'link', 'text'
  name TEXT NOT NULL,

  -- Storage
  storage_path TEXT, -- Supabase Storage path (for kind='file')
  content_text TEXT, -- Direct text (for kind='text')
  content_url TEXT,  -- External URL (for kind='link')

  -- Metadata
  size_bytes BIGINT,
  mime_type TEXT,
  metadata JSONB
);

CREATE INDEX idx_artifacts_run ON ops.artifacts(run_id);
```

### 3.5) ops.run_templates

```sql
CREATE TABLE ops.run_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

  -- Identity
  name TEXT NOT NULL,
  version INT NOT NULL DEFAULT 1,
  description TEXT,

  -- Template
  kind TEXT NOT NULL,
  steps JSONB NOT NULL, -- Array of step definitions

  -- Metadata
  timeout_seconds INT DEFAULT 300,
  retry_policy JSONB,

  UNIQUE(name, version)
);

CREATE INDEX idx_templates_name ON ops.run_templates(name, version DESC);
```

---

## 4) API Contracts

### 4.1) Supabase Edge Function: `ops-executor`

**Endpoint**: `https://<project>.supabase.co/functions/v1/ops-executor`

**Operations**:

#### Create Session
```typescript
POST /ops-executor/sessions
{
  "name": "Deploy v1.1.0",
  "description": "Fresh deployment from ship-aiux-v1.1.0 tag",
  "triggered_by": "manual"
}

Response:
{
  "session_id": "uuid",
  "status": "active"
}
```

#### Enqueue Run
```typescript
POST /ops-executor/runs
{
  "session_id": "uuid",
  "kind": "spec_kit_generate",
  "lane": "A",
  "priority": 5,
  "params": {
    "feature": "ops-control-room",
    "files": ["constitution", "prd", "plan", "tasks"]
  }
}

Response:
{
  "run_id": "uuid",
  "status": "queued"
}
```

#### Claim Runs (Worker)
```typescript
POST /ops-executor/claim
{
  "worker_id": "worker-1",
  "lanes": ["A", "B", "C", "D"],
  "limit": 4
}

Response:
{
  "runs": [
    { "id": "uuid", "kind": "...", "params": {...} }
  ]
}
```

#### Update Run Status
```typescript
PATCH /ops-executor/runs/:id
{
  "status": "running",
  "started_at": "2026-01-08T10:00:00Z"
}
```

#### Heartbeat
```typescript
POST /ops-executor/runs/:id/heartbeat
{
  "worker_id": "worker-1"
}
```

#### Upload Artifact
```typescript
POST /ops-executor/runs/:id/artifacts
{
  "kind": "file",
  "name": "constitution.md",
  "storage_path": "runs/uuid/constitution.md"
}
```

### 4.2) Direct SQL (Atomic Claiming)

```sql
-- Claim runs atomically
WITH claimed AS (
  SELECT id FROM ops.runs
  WHERE status = 'queued'
    AND (lane = ANY($1) OR $1 IS NULL)
  ORDER BY priority DESC, created_at ASC
  LIMIT $2
  FOR UPDATE SKIP LOCKED
)
UPDATE ops.runs
SET
  status = 'claimed',
  claimed_by = $3,
  claimed_at = now()
WHERE id IN (SELECT id FROM claimed)
RETURNING *;
```

### 4.3) Realtime Subscription (UI)

```typescript
supabase
  .channel('runs')
  .on('postgres_changes', {
    event: '*',
    schema: 'ops',
    table: 'runs'
  }, (payload) => {
    console.log('Run changed:', payload);
    updateUI(payload.new);
  })
  .subscribe();
```

---

## 5) UI/UX Specifications

### 5.1) Runboard (Main View)

```
┌──────────────────────────────────────────────────────────┐
│  Session: Deploy v1.1.0                    [Cancel]       │
├──────────────────────────────────────────────────────────┤
│  Lane A          Lane B          Lane C          Lane D   │
├──────────┬───────────────┬───────────────┬───────────────┤
│ ✓ Build  │ 🔄 Test       │ ⏳ Deploy     │ 📋 Queued    │
│   2m 15s │   Running...  │   Waiting     │   Pending    │
│          │   45s elapsed │               │              │
├──────────┼───────────────┼───────────────┼───────────────┤
│ ✓ Lint   │ ✓ Security    │ 📋 Verify     │ 📋 Notify    │
│   1m 30s │   3m 45s      │   Queued      │   Queued     │
└──────────┴───────────────┴───────────────┴───────────────┘

Summary: 2 succeeded | 2 running | 4 queued | 0 failed
```

**States**:
- ✓ (green) - Succeeded
- 🔄 (blue) - Running
- ⏳ (yellow) - Claimed/waiting
- 📋 (gray) - Queued
- ❌ (red) - Failed
- 🚫 (orange) - Cancelled

### 5.2) Run Details (Expanded View)

```
┌──────────────────────────────────────────────────────────┐
│  Run: spec_kit_generate (Lane A)                         │
├──────────────────────────────────────────────────────────┤
│  Status: Running                                         │
│  Started: 2026-01-08 10:00:00                            │
│  Duration: 45s                                           │
│  Worker: worker-1                                        │
├──────────────────────────────────────────────────────────┤
│  Events:                                                 │
│  10:00:00 [info] Started constitution.md generation      │
│  10:00:15 [info] Constitution.md complete (2.3 KB)       │
│  10:00:16 [info] Started prd.md generation               │
│  10:00:30 [info] PRD.md complete (8.7 KB)                │
│  10:00:31 [info] Started plan.md generation              │
│  10:00:45 [warn] Plan.md requires dependency review      │
├──────────────────────────────────────────────────────────┤
│  Artifacts:                                              │
│  📄 constitution.md (2.3 KB) [Download]                  │
│  📄 prd.md (8.7 KB) [Download]                           │
│  📄 plan.md (in progress...)                             │
└──────────────────────────────────────────────────────────┘
```

---

## 6) Integration Points

### 6.1) GitHub Integration

**Trigger**: GitHub webhook → Edge Function → Enqueue runs

```typescript
// Example: PR opened → run linter + tests
POST /ops-executor/runs
{
  "session_id": "github-pr-123",
  "kind": "github_pr_check",
  "lane": "A",
  "params": {
    "pr_number": 123,
    "sha": "abc123",
    "checks": ["lint", "test", "build"]
  }
}
```

### 6.2) Docker Integration

**Worker Dockerfile**:
```dockerfile
FROM node:20-alpine
RUN apk add --no-cache git docker-cli
COPY . /app
WORKDIR /app
CMD ["node", "worker.js"]
```

**Worker Logic**:
```typescript
async function claimAndExecute() {
  const runs = await supabase.rpc('claim_runs', {
    worker_id: WORKER_ID,
    lanes: ['A', 'B', 'C', 'D'],
    limit: 4
  });

  for (const run of runs) {
    await executeRun(run);
  }
}

setInterval(claimAndExecute, 5000);
```

### 6.3) Spec Kit Generator Integration

**Trigger**: User creates spec bundle → enqueue generation runs

```typescript
POST /ops-executor/runs
{
  "session_id": "spec-kit-ops-control-room",
  "kind": "spec_kit_generate",
  "lane": "A",
  "params": {
    "feature": "ops-control-room",
    "files": ["constitution", "prd", "plan", "tasks"]
  }
}
```

---

## 7) Acceptance Criteria

### 7.1) Functional Requirements

- ✅ Create session via API
- ✅ Enqueue runs with priority and lane
- ✅ Workers claim runs atomically (no double execution)
- ✅ Workers send heartbeat every 5s
- ✅ Stuck runs recovered after 30s timeout
- ✅ Run status changes propagate to UI within 2s
- ✅ Cancel runs gracefully (workers stop within 10s)
- ✅ Artifacts stored in Supabase Storage (files >1MB)
- ✅ Structured error reporting (jsonb with type/message/stack/context)

### 7.2) Non-Functional Requirements

- ✅ 99.9% uptime for control plane
- ✅ <2s real-time update latency
- ✅ <100ms API response time (P95)
- ✅ Support 100+ concurrent runs
- ✅ Horizontal scaling for workers
- ✅ 90-day artifact retention (configurable)

### 7.3) Quality Gates

- ✅ All ops tables in `ops` schema
- ✅ RLS policies enforced on all tables
- ✅ Zero secrets in `ops.runs.params`
- ✅ Health checks pass for all workers
- ✅ CI enforces 4-file Spec Kit structure
- ✅ Production deploys only to Vercel/Supabase/DO

---

## 8) Out of Scope

- ❌ Multi-tenancy (single-tenant only for v1)
- ❌ Advanced scheduling (cron, recurring runs)
- ❌ Run dependencies (DAG execution)
- ❌ Custom worker images (Docker registry integration)
- ❌ Advanced analytics (Grafana, Prometheus)

---

## 9) Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Double execution | `FOR UPDATE SKIP LOCKED` in claiming logic |
| Zombie runs | Heartbeat + 30s stuck-run recovery |
| Schema access errors | Expose `ops` schema in PostgREST config |
| Artifact loss | Supabase Storage with versioning enabled |
| Worker crashes | Health checks + auto-restart (Kubernetes) |
| UI stale data | Realtime subscriptions with <2s latency |

---

## 10) Success Metrics

- **Reliability**: 99.9% successful run completion rate
- **Performance**: <100ms P95 API response time
- **Real-time**: <2s status update propagation
- **Recovery**: <35s stuck-run detection and recovery
- **Throughput**: 100+ concurrent runs supported

---

**Version**: 1.0.0
**Status**: Ready for Implementation
**Next**: Create `plan.md` and `tasks.md`
