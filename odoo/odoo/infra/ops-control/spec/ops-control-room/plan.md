# Plan — Ops Control Room

## A) Decisions Locked
1) Schema strategy: **public schema** (simpler than ops schema exposure; PostgREST compatible out of the box).
2) Execution: claim semantics via **`FOR UPDATE SKIP LOCKED`** in SQL functions.
3) Observability: store structured events + artifacts; stream via Realtime.
4) Setup: automated wizard guides users through database creation.

## B) Phased Implementation

### Phase 0 — Stabilize Database Foundation ✅ COMPLETE
**Status:** ✅ Shipped (January 8, 2026)

Deliverables:
- [x] All tables in `public` schema (sessions, runs, run_events, artifacts, run_templates, spec_docs, run_steps)
- [x] SQL functions: `claim_runs()`, `heartbeat_run()`, `cancel_run()`, `enqueue_run()`, `complete_run()`
- [x] RLS policies for security
- [x] Real-time publication configured
- [x] Automated database setup wizard (DatabaseSetup.tsx)
- [x] UI tabs: Chat, Templates, Runs, Spec Kit, Runboard
- [x] Basic Runboard with lanes A/B/C/D

Verification:
- ✅ UI loads without schema errors
- ✅ Templates/runs/sessions query successfully
- ✅ Setup wizard appears when tables don't exist
- ✅ Real-time subscriptions configured

### Phase 1 — Control Plane API (Edge Function) ⏳ IN PROGRESS
**Status:** Partially implemented

Tasks:
- [x] Basic `/supabase/functions/ops-executor/index.ts` structure
- [ ] `POST /runs.create` - Create queued run
- [ ] `POST /runs.claim` - Atomic claim with SKIP LOCKED
- [ ] `POST /runs.heartbeat` - Update heartbeat timestamp
- [ ] `POST /runs.cancel` - Cancel run
- [ ] `POST /events.append` - Append structured events
- [ ] `POST /artifacts.put` - Store artifacts (small text + signed upload for files)
- [ ] Error handling + logging
- [ ] Contract tests

Implementation details:
```typescript
// Edge Function API structure
import { serve } from 'https://deno.land/std/http/server.ts'
import { createClient } from '@supabase/supabase-js'

serve(async (req) => {
  const url = new URL(req.url)
  const path = url.pathname
  
  switch (path) {
    case '/runs.create': return handleCreateRun(req)
    case '/runs.claim': return handleClaimRuns(req)
    case '/runs.heartbeat': return handleHeartbeat(req)
    case '/runs.cancel': return handleCancel(req)
    case '/events.append': return handleAppendEvents(req)
    case '/artifacts.put': return handlePutArtifact(req)
    default: return new Response('Not Found', { status: 404 })
  }
})
```

### Phase 2 — Worker Fleet (Reference + Deployment) ❌ NOT STARTED
**Status:** Not started

Tasks:
- [ ] Reference worker implementation (Node.js/TypeScript)
  - [ ] Poll `/runs.claim` endpoint
  - [ ] Execute step DSL
  - [ ] Heartbeat loop (background thread)
  - [ ] Cancellation checks between steps
  - [ ] Append events + artifacts
- [ ] Containerize worker (Dockerfile)
- [ ] Deploy to DigitalOcean
  - [ ] Droplet with systemd service
  - [ ] App Platform
  - [ ] DOKS (Kubernetes) - optional
- [ ] Configuration management
  - [ ] Environment variables
  - [ ] Secrets injection
  - [ ] Worker scaling

Worker architecture:
```
Worker Loop:
1. Claim run(s) from queue
2. Initialize run context
3. For each step:
   - Check cancellation flag
   - Execute step (shell/docker/api/mcp)
   - Send heartbeat
   - Append events
4. Complete run (success/failure)
5. Upload artifacts
6. Return to step 1
```

### Phase 3 — UI Completion ⏳ PARTIALLY COMPLETE
**Status:** Basic UI exists, needs enhancement

Tasks:
- [x] Basic Runboard with lanes A/B/C/D
- [ ] Enhanced Runboard features:
  - [ ] Queue depth visualization
  - [ ] Active run details card
  - [ ] Heartbeat indicator (pulse animation)
  - [ ] Cancel button with confirmation
  - [ ] Live log streaming
- [ ] Templates UI:
  - [x] List templates
  - [ ] Create/edit template form
  - [ ] Params schema builder
  - [ ] Template validation
  - [ ] Default lane assignment
- [ ] Runs list:
  - [x] Basic run history
  - [ ] Advanced filters (status, lane, template, date range)
  - [ ] Bulk actions
  - [ ] Export run data
- [ ] Artifact viewer:
  - [ ] Markdown renderer
  - [ ] JSON viewer
  - [ ] File download links
  - [ ] Diff viewer
  - [ ] Screenshot viewer
- [x] Real-time subscriptions for live updates

### Phase 4 — Spec Kit Run Types ❌ NOT STARTED
**Status:** Not started

Tasks:
- [ ] Template: `generate_spec_kit`
  - [ ] Input: project name, description
  - [ ] Generate: constitution.md, prd.md, plan.md, tasks.md
  - [ ] Output: zip artifact + individual files
- [ ] Template: `validate_spec_kit`
  - [ ] Check required files exist
  - [ ] Validate structure
  - [ ] Check for acceptance criteria
  - [ ] Output: validation report JSON
- [ ] Artifact storage:
  - [ ] Supabase Storage integration
  - [ ] Zip file generation
  - [ ] Markdown previews
  - [ ] Validation report rendering
- [ ] CI integration:
  - [ ] GitHub Actions workflow
  - [ ] Automated spec validation
  - [ ] PR comments with results

### Phase 5 — Stuck Run Recovery & Advanced Reliability ❌ NOT STARTED
**Status:** Not started

Tasks:
- [ ] Stuck run sweeper (Edge Function cron or worker)
  - [ ] Query runs where `now() - heartbeat_at > timeout`
  - [ ] Increment attempt counter
  - [ ] Requeue if `attempt < max_attempts`
  - [ ] Mark failed if exceeded max attempts
  - [ ] Send notification events
- [ ] Retry logic:
  - [ ] Exponential backoff
  - [ ] Configurable retry strategies
  - [ ] Idempotency checks
- [ ] Graceful shutdown:
  - [ ] Worker signal handling
  - [ ] Complete current step before exit
  - [ ] Update run status
- [ ] Monitoring & alerting:
  - [ ] Worker health dashboard
  - [ ] Stuck run alerts
  - [ ] Queue depth metrics
  - [ ] Performance tracking

### Phase 6 — Production Deployment ❌ NOT STARTED
**Status:** Not started

Tasks:
- [ ] Vercel deployment:
  - [ ] Production build configuration
  - [ ] Environment variables setup
  - [ ] Custom domain
  - [ ] Edge caching
- [ ] Supabase production setup:
  - [ ] Database backups
  - [ ] Performance tuning
  - [ ] Connection pooling
  - [ ] Monitoring
- [ ] Worker deployment:
  - [ ] DigitalOcean Droplet setup
  - [ ] Systemd service configuration
  - [ ] Auto-scaling (DOKS)
  - [ ] Log aggregation
- [ ] CI/CD pipelines:
  - [ ] GitHub Actions workflows
  - [ ] Automated tests
  - [ ] Deploy on merge
  - [ ] Rollback strategy

## C) Verification Checklist

### Claim Safety
- [ ] Run same queue with 2 workers; verify no duplicate executions
- [ ] Stress test: 10 workers, 100 queued runs
- [ ] Verify SKIP LOCKED prevents double-claiming

### Recovery
- [ ] Kill worker mid-run; verify stuck-run requeue/failover
- [ ] Test timeout thresholds
- [ ] Verify max attempts enforcement

### Cancellation
- [ ] Cancel from UI; verify worker halts gracefully
- [ ] Check cancellation events logged
- [ ] Verify partial artifacts saved

### Schema & Tables
- [x] No errors `Could not find table`
- [x] Templates load from `public.run_templates`
- [x] Real-time subscriptions work
- [x] Automated setup wizard functional

### Real-time Updates
- [ ] Runboard updates within 2s of status change
- [ ] Events stream live during execution
- [ ] Heartbeat indicator pulses

## D) Pulser SDK Requirement (Documentation)

Add section in operator docs (`docs/ops/PULSER_INTEGRATION.md`):

**Install Pulser SDK**
```bash
npm install @pulser/sdk
# or
pip install pulser-sdk
```

**Define Adapter Interface** (future)
- Templates can be executed by Pulser agents
- Runbook DSL compatible with Pulser IR
- Event streaming to Pulser control plane

## E) Deliverables Mapping

### Database
- ✅ `supabase/migrations/FULL_SETUP.sql` - Complete schema
- ✅ `supabase/migrations/20250108000000_move_to_public_schema.sql`
- ⏳ `supabase/migrations/*_stuck_recovery.sql` - Future

### Edge Functions
- ⏳ `supabase/functions/ops-executor/index.ts` - Enhanced API
- ❌ `supabase/functions/stuck-run-sweeper/index.ts` - Future

### UI Components
- ✅ `src/app/App.tsx` - Main app with tabs
- ✅ `src/app/components/Runboard.tsx` - Lane visualization
- ✅ `src/app/components/DatabaseSetup.tsx` - Setup wizard
- ⏳ `src/app/components/RunLane.tsx` - Enhanced lane component
- ❌ `src/app/components/ArtifactViewer.tsx` - Future
- ❌ `src/app/components/SpecKitGenerator.tsx` - Future

### Worker
- ❌ `workers/executor-worker.ts` - Main worker loop
- ❌ `workers/Dockerfile` - Container image
- ❌ `workers/systemd/ops-worker.service` - Systemd config

### CI/CD
- ✅ `.github/workflows/spec-kit-enforce.yml` - Spec validation
- ❌ `.github/workflows/deploy-ui.yml` - Vercel deploy
- ❌ `.github/workflows/deploy-workers.yml` - DO deploy

### Documentation
- ✅ `spec/ops-control-room/{constitution,prd,plan,tasks}.md`
- ✅ `DATABASE_SETUP_FIXED.md` - Setup guide
- ❌ `docs/ops/OPERATOR_MANUAL.md` - Future
- ❌ `docs/ops/PULSER_INTEGRATION.md` - Future

### Scripts
- ✅ `scripts/validate_spec_kit.py` - Spec validation

## F) Timeline Estimate

- **Phase 0** ✅ Complete (2 days)
- **Phase 1** ⏳ In Progress (3-5 days)
- **Phase 2** ❌ Not Started (5-7 days)
- **Phase 3** ⏳ Partial (3-5 days)
- **Phase 4** ❌ Not Started (3-4 days)
- **Phase 5** ❌ Not Started (2-3 days)
- **Phase 6** ❌ Not Started (3-5 days)

**Total estimated:** 21-33 days for full MVP

## G) Next Immediate Tasks

Priority order for next implementation sprint:

1. **Complete Phase 1 - Edge Function API** (2-3 days)
   - Implement all 6 endpoints
   - Add error handling
   - Write contract tests

2. **Start Phase 2 - Reference Worker** (3-5 days)
   - Basic worker loop
   - Step execution engine
   - Heartbeat mechanism

3. **Enhance Phase 3 - UI** (2-3 days)
   - Better Runboard visualization
   - Artifact viewer
   - Advanced filters

4. **Phase 5 - Stuck Recovery** (1-2 days)
   - Sweeper implementation
   - Retry logic

This plan provides a clear roadmap from current state to production-ready parallel execution platform.
