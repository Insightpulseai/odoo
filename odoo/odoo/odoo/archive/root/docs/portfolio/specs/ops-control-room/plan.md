# Ops Control Room — Implementation Plan

**Spec Bundle**: `spec/ops-control-room/`
**Status**: Canonical
**Last Updated**: 2026-01-08

---

## 0) Overview

**Goal**: Production-grade parallel runbook executor with atomic claiming, real-time telemetry, and automatic recovery.

**Timeline**: 4 milestones (M0 → M1 → M2 → M3)

**Critical Path**: M0 (Schema Access) → M1 (Execution Core) → M2 (Scale) → M3 (Spec Kit Integration)

---

## 1) Milestones

### M0: Fix Schema Access (Blocker)
**Duration**: 1 day
**Status**: CRITICAL - Blocks all other work

**Objective**: Resolve "Invalid schema: ops" errors

**Tasks**:
1. Update Supabase PostgREST config to expose `ops` schema
2. Create `ops` schema with proper grants
3. Verify API access to `ops` schema from UI
4. Document schema exposure in constitution.md

**Acceptance**:
- ✅ `GET /rest/v1/ops.runs` returns 200
- ✅ No "Invalid schema: ops" errors in UI
- ✅ RLS policies enforced on ops.* tables

**Dependencies**: Supabase project access with admin privileges

---

### M1: Execution Core (Minimal Viable)
**Duration**: 3-5 days
**Status**: Foundation

**Objective**: Atomic run claiming + execution + telemetry

**Tasks**:
1. Database schema migrations
   - ops.sessions, ops.runs, ops.run_events, ops.artifacts tables
   - ops.lane_type ENUM
   - Indexes for performance
   - RLS policies

2. Supabase Edge Function: `ops-executor`
   - Create session endpoint
   - Enqueue run endpoint
   - Claim runs endpoint (atomic with FOR UPDATE SKIP LOCKED)
   - Update run status endpoint
   - Heartbeat endpoint
   - Upload artifact endpoint

3. Worker reference implementation
   - Claim runs (4 lanes: A, B, C, D)
   - Execute run (mock implementation first)
   - Send heartbeat every 5s
   - Handle cancellation
   - Upload artifacts to Supabase Storage

4. Stuck-run recovery cron job
   - Scheduled Edge Function (every 30s)
   - Mark stuck runs as failed (heartbeat_at > 30s)
   - Log recovery events

5. Basic UI (Runboard)
   - Session list view
   - Run list view (4 lanes)
   - Real-time status updates (Supabase Realtime)
   - Cancel run button

**Acceptance**:
- ✅ Create session + enqueue runs via API
- ✅ Workers claim runs atomically (no double execution)
- ✅ Workers send heartbeat every 5s
- ✅ Stuck runs recovered within 35s (30s timeout + 5s cron)
- ✅ Run status changes reflect in UI within 2s
- ✅ Cancel run stops worker within 10s

**Dependencies**: M0 complete, Supabase Edge Functions enabled

---

### M2: Scale & Reliability
**Duration**: 2-3 days
**Status**: Production-Ready

**Objective**: Handle 100+ concurrent runs, horizontal scaling, monitoring

**Tasks**:
1. Worker deployment (DigitalOcean)
   - Dockerfile with health check endpoint
   - App Platform spec (auto-scaling)
   - Environment variable config (SUPABASE_URL, SUPABASE_KEY, WORKER_ID)
   - Deploy 3 workers (initial)

2. Template system
   - ops.run_templates table
   - Template versioning
   - Template execution logic in worker

3. Artifact storage optimization
   - Supabase Storage bucket config (artifacts)
   - File upload via presigned URLs
   - Artifact retention policy (90 days)

4. Error handling & logging
   - Structured error format (jsonb with type/message/stack/context)
   - Event logging (ops.run_events)
   - Error rate monitoring

5. Health checks & monitoring
   - Worker /health endpoint
   - Supabase health check
   - Metrics dashboard (basic)

**Acceptance**:
- ✅ 3+ workers running concurrently
- ✅ 100+ runs executed without failure
- ✅ 10MB artifact uploads successfully
- ✅ Workers auto-restart on crash (Kubernetes/DO)
- ✅ Error rate <1% (P95)
- ✅ Health checks pass for all workers

**Dependencies**: M1 complete, DigitalOcean App Platform access

---

### M3: Spec Kit Integration
**Duration**: 2-3 days
**Status**: Feature Complete

**Objective**: Auto-generate Spec Kit bundles using Ops Control Room

**Tasks**:
1. Spec Kit generator worker
   - kind: `spec_kit_generate`
   - Input: feature name, file list (constitution, prd, plan, tasks)
   - Output: 4 markdown files in `spec/<feature>/`
   - Artifact upload to Supabase Storage
   - Git commit automation

2. GitHub integration
   - GitHub App setup (repo access)
   - Webhook receiver (PR opened, push, etc.)
   - Auto-enqueue runs (lint, test, build)
   - Status check reporting

3. CI enforcement
   - GitHub Actions workflow: `spec-kit-enforce.yml`
   - Verify 4-file structure in `spec/*`
   - Fail if any file missing

4. UI enhancements
   - Spec Kit generation form
   - File preview (artifact viewer)
   - Download all artifacts (ZIP)

**Acceptance**:
- ✅ Generate Spec Kit bundle via UI
- ✅ 4 files created in `spec/<feature>/`
- ✅ Files committed to git automatically
- ✅ CI enforces 4-file structure
- ✅ GitHub integration triggers runs on PR/push

**Dependencies**: M2 complete, GitHub App credentials

---

## 2) Technical Architecture

### 2.1) Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Ops Control Room                         │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Vercel UI  │    │   Supabase   │    │ DO Workers   │
│  (Runboard)  │    │ Control Plane│    │  (Executors) │
│              │    │              │    │              │
│ - React      │    │ - PostgreSQL │    │ - Node.js    │
│ - Next.js    │    │ - Realtime   │    │ - Docker     │
│ - Tailwind   │    │ - Edge Fns   │    │ - K8s        │
│ - Realtime   │    │ - Storage    │    │ - Health /   │
│   Subs       │    │ - RLS        │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
```

### 2.2) Data Flow

```
1. User creates session (UI → Edge Function → DB)
2. User enqueues runs (UI → Edge Function → DB)
3. Worker polls for runs (Worker → Edge Function → DB)
4. Worker claims runs atomically (FOR UPDATE SKIP LOCKED)
5. Worker executes run (Worker → External systems)
6. Worker sends heartbeat every 5s (Worker → Edge Function → DB)
7. Worker uploads artifacts (Worker → Supabase Storage)
8. Worker updates run status (Worker → Edge Function → DB)
9. UI subscribes to run changes (UI → Realtime → DB)
10. UI updates in real-time (<2s latency)
```

### 2.3) Database Schema

**Core Tables**:
- `ops.sessions` - Execution sessions (1 session = N runs)
- `ops.runs` - Individual tasks with status/lane/priority
- `ops.run_events` - Event log (debug, info, warn, error)
- `ops.artifacts` - File/link/text outputs
- `ops.run_templates` - Reusable run templates (versioned)

**Indexes**:
- `idx_runs_status_lane` - Fast claiming by status + lane
- `idx_runs_priority` - Priority ordering
- `idx_runs_heartbeat` - Stuck-run detection
- `idx_events_run` - Event log query performance

**RLS Policies**:
- All tables: `authenticated` role can read/write
- `anon` role: read-only access to sessions/runs (no events/artifacts)

---

## 3) Dependencies

### 3.1) External Services

| Service | Purpose | Status |
|---------|---------|--------|
| Supabase | Control plane (DB, Realtime, Storage, Edge Functions) | ✅ Configured |
| DigitalOcean | Worker hosting (App Platform or K8s) | ⏳ TBD |
| Vercel | UI hosting | ✅ Configured |
| GitHub | Source control + webhook integration | ✅ Configured |

### 3.2) Internal Dependencies

| Dependency | Required For | Status |
|------------|--------------|--------|
| PostgREST config | M0 (schema access) | ❌ Blocked |
| Supabase Edge Functions | M1 (execution core) | ✅ Available |
| Supabase Storage | M2 (artifacts) | ✅ Available |
| GitHub App credentials | M3 (GitHub integration) | ⏳ TBD |

### 3.3) Skill Dependencies

| Milestone | Required Skills |
|-----------|-----------------|
| M0 | Supabase admin, PostgREST config |
| M1 | PostgreSQL, Supabase Edge Functions, TypeScript |
| M2 | Docker, DigitalOcean, Kubernetes, monitoring |
| M3 | GitHub API, Git automation, CI/CD |

---

## 4) Risk Mitigation

### 4.1) Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Schema access blocked | HIGH - Blocks all work | Priority fix in M0, Option B fallback (public views) |
| Double execution | HIGH - Data corruption | `FOR UPDATE SKIP LOCKED` + integration test |
| Zombie runs | MEDIUM - Wasted resources | Heartbeat + 30s recovery cron |
| Worker crashes | MEDIUM - Lost progress | Health checks + auto-restart |
| Artifact loss | MEDIUM - Missing outputs | Supabase Storage with versioning |
| UI stale data | LOW - Poor UX | Realtime subscriptions + fallback polling |

### 4.2) Operational Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Worker scaling | MEDIUM - Bottleneck | Horizontal scaling (DO/K8s) |
| Cost overruns | LOW - Budget | Monitor usage, set quotas |
| Security breach | HIGH - Data leak | RLS policies, secrets in vault |
| Downtime | MEDIUM - Service unavailable | 99.9% SLA, health checks, monitoring |

---

## 5) Testing Strategy

### 5.1) Unit Tests

**Scope**: Individual functions (claiming logic, heartbeat, artifact upload)

**Tools**: Jest, Vitest

**Coverage Target**: ≥80%

**Example**:
```typescript
describe('claim_runs', () => {
  it('should claim runs atomically', async () => {
    // Setup: Enqueue 10 runs
    // Execute: 2 workers claim 5 runs each concurrently
    // Assert: Each run claimed by exactly 1 worker
  });
});
```

### 5.2) Integration Tests

**Scope**: End-to-end workflows (create session → enqueue → claim → execute → complete)

**Tools**: Playwright, Supabase test database

**Example**:
```typescript
test('parallel execution across 4 lanes', async () => {
  const session = await createSession();
  await enqueueRuns(session.id, 16); // 4 runs per lane
  await startWorker();
  await waitForCompletion();
  expect(getAllRuns()).toHaveLength(16);
  expect(getFailedRuns()).toHaveLength(0);
});
```

### 5.3) Performance Tests

**Scope**: Load testing (100+ concurrent runs)

**Tools**: k6, Artillery

**Metrics**:
- API response time (P95 <100ms)
- Realtime latency (<2s)
- Stuck-run recovery time (<35s)

### 5.4) Security Tests

**Scope**: RLS policies, secret handling

**Tools**: Manual testing, Bandit (Python), ESLint security plugin

**Checks**:
- RLS policies enforced (no public access to sensitive data)
- No secrets in `ops.runs.params`
- HTTPS only for all API calls

---

## 6) Deployment Plan

### 6.1) M0 Deployment (Schema Access)

**Steps**:
1. Update Supabase PostgREST config via dashboard
2. Apply migration: `CREATE SCHEMA ops`
3. Grant permissions: `GRANT USAGE ON SCHEMA ops TO anon, authenticated`
4. Verify API access: `curl https://<project>.supabase.co/rest/v1/ops.runs`

**Rollback**: Revert PostgREST config, drop `ops` schema

### 6.2) M1 Deployment (Execution Core)

**Steps**:
1. Apply database migrations (ops.sessions, ops.runs, etc.)
2. Deploy Edge Function: `ops-executor`
3. Deploy UI to Vercel
4. Start 1 worker locally for testing
5. Smoke test: Create session, enqueue run, verify execution

**Rollback**: Drop ops tables, delete Edge Function, revert UI deploy

### 6.3) M2 Deployment (Scale)

**Steps**:
1. Build worker Docker image
2. Deploy to DigitalOcean App Platform (3 workers)
3. Configure health checks
4. Enable auto-scaling (3-10 workers)
5. Monitor metrics dashboard

**Rollback**: Scale workers to 0, delete app

### 6.4) M3 Deployment (Spec Kit)

**Steps**:
1. Deploy Spec Kit generator worker
2. Configure GitHub App
3. Enable GitHub webhook
4. Deploy CI workflow: `spec-kit-enforce.yml`

**Rollback**: Disable webhook, delete CI workflow

---

## 7) Monitoring & Observability

### 7.1) Key Metrics

| Metric | Target | Alerts |
|--------|--------|--------|
| API response time (P95) | <100ms | >200ms |
| Realtime latency | <2s | >5s |
| Stuck-run recovery | <35s | >60s |
| Worker health | 100% | <80% |
| Error rate | <1% | >5% |
| Throughput | 100+ runs/min | <50 runs/min |

### 7.2) Logging

**Levels**:
- DEBUG: Run claiming, heartbeat
- INFO: Run start/complete, session lifecycle
- WARN: Stuck run detected, high latency
- ERROR: Run failure, worker crash

**Storage**: ops.run_events table + external log aggregator (optional)

### 7.3) Alerts

**Channels**: Slack, email, PagerDuty

**Triggers**:
- Worker health <80%
- Error rate >5%
- Stuck-run recovery time >60s
- API response time >200ms (P95)

---

## 8) Documentation

### 8.1) Required Docs

- ✅ `constitution.md` - Immutable rules (complete)
- ✅ `prd.md` - Product requirements (complete)
- ✅ `plan.md` - Implementation plan (this document)
- ⏳ `tasks.md` - Task checklist with status

### 8.2) API Documentation

**Format**: OpenAPI 3.0 spec

**Location**: `docs/api/ops-executor.yaml`

**Sections**:
- Endpoints (create session, enqueue run, claim runs, etc.)
- Request/response schemas
- Authentication (Bearer token)
- Error codes

### 8.3) Runbooks

**Location**: `docs/runbooks/ops-control-room/`

**Topics**:
- Worker deployment
- Stuck-run recovery manual trigger
- Schema migration rollback
- Incident response

---

## 9) Success Criteria

### 9.1) M0 Success

- ✅ No "Invalid schema: ops" errors
- ✅ API access to ops.* tables
- ✅ RLS policies enforced

### 9.2) M1 Success

- ✅ Atomic run claiming (zero double execution)
- ✅ Real-time UI updates (<2s)
- ✅ Stuck-run recovery (<35s)
- ✅ 100% worker uptime (manual testing)

### 9.3) M2 Success

- ✅ 3+ workers running concurrently
- ✅ 100+ runs executed without failure
- ✅ 10MB artifact uploads
- ✅ Error rate <1%

### 9.4) M3 Success

- ✅ Spec Kit bundles auto-generated
- ✅ GitHub integration triggers runs
- ✅ CI enforces 4-file structure

---

## 10) Next Steps

1. **Immediate**: Fix schema access (M0)
2. **Week 1**: Implement execution core (M1)
3. **Week 2**: Deploy workers, scaling, monitoring (M2)
4. **Week 3**: Spec Kit integration, GitHub hooks (M3)
5. **Ongoing**: Monitor metrics, iterate on UX

---

**Version**: 1.0.0
**Status**: Ready for Execution
**Next**: Create `tasks.md` with detailed task breakdown
