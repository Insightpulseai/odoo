# PRD — Ops Control Room (Parallel Runbook Executor)

## 1) Problem
Need one control plane to run many tasks concurrently with safe claiming, realtime telemetry, cancellation, retries, proof bundles, and deployment portability (Vercel + Supabase + DO/K8s + GitHub Actions).

Observed production blockers (resolved):
- `Invalid schema: ops` because PostgREST only exposes `public, graphql_public`.
- `Could not find table public.run_templates` because tables didn't exist yet.

**Solution implemented:** All tables now in `public` schema with automated setup wizard.

## 2) Goals
### Success criteria
1. Parallel lanes per session (A/B/C/D default).
2. Atomic claiming with Postgres locking (`FOR UPDATE SKIP LOCKED`).
3. Realtime UI updates (runs/events/artifacts) within ~2s.
4. Heartbeat + stuck-run recovery + cancellation + retries.
5. Deployable: UI on Vercel, control plane on Supabase, workers on DO/DOKS/GHA.
6. Spec Kit run type generates `constitution/prd/plan/tasks` + attaches artifacts.

## 3) Non-Goals (v1)
- Full in-browser IDE
- Billing/tenant provisioning
- Secret vault UI

## 4) Personas
- **Ops Operator** - Triggers deployments, health checks, fixes; needs proofs
- **Worker Executor** - Stateless runner that claims runs and executes steps
- **Auditor/Reviewer** - Needs deterministic logs, artifacts, and "what shipped"

## 5) UX / Information Architecture
Tabs:
- **Chat** - Command entry + suggested quick actions
- **Templates** - List, create, edit; shows params schema + default lane
- **Runs** - Searchable run history with filters (status, lane, template, repo)
- **Spec Kit** - Spec generator/validator + artifact viewer
- **Runboard** - Primary dashboard with lanes A/B/C/D per selected session

Runboard features:
- Queue count, active run card, heartbeat indicator
- Cancel button
- Logs + Artifacts viewer
- Real-time updates

## 6) Architecture
### Control Plane (Supabase)
- Postgres schema: `public`
- Realtime on: `runs`, `run_events`, `artifacts`, `sessions`
- Edge Function: `ops-executor` API (create/claim/heartbeat/cancel/events/artifacts)

### Data Plane (Workers)
- Stateless workers poll `/runs.claim`
- Execute run steps
- Stream events + artifacts back
- Send heartbeats

## 7) Data Model (MVP)
Schema: `public`

### Tables
- **sessions** - Groups of related runs; status tracking
- **run_templates** - Reusable runbook templates with params schema
- **runs** - Individual execution tasks with claiming metadata
- **run_events** - Real-time log entries
- **artifacts** - Generated outputs (links, files, diffs, markdown)
- **spec_docs** - Spec Kit documentation
- **run_steps** - Granular step tracking

### Indexes
- `runs(session_id, lane, status, priority, created_at)`
- `runs(status, priority, created_at)` - for claiming
- `run_events(run_id, ts)`
- `artifacts(run_id, ts)`
- `runs(status, heartbeat_at)` - for stuck run recovery

## 8) API Contract (Edge Function)
Base: `/functions/v1/ops-executor`

Endpoints:
- `POST /runs.create` - Create a run (queued)
- `POST /runs.claim` - Atomic claim with SKIP LOCKED
- `POST /runs.heartbeat` - Update heartbeat timestamp
- `POST /runs.cancel` - Cancel a running job
- `POST /events.append` - Append log events
- `POST /artifacts.put` - Store artifacts (text or file upload)

## 9) Concurrency + Reliability
### Claiming rules
- Only `queued` runs claimable
- Claim transitions: `queued → claimed` sets `claimed_by/claimed_at/heartbeat_at`
- Worker sets `running` after init
- Uses `FOR UPDATE SKIP LOCKED` for atomic claiming

### Heartbeat + stuck recovery
- Heartbeat every 2–5s
- Stuck sweeper: if `now() - heartbeat_at > timeout`, requeue (attempt++) or fail
- Max attempts configurable per run

### Cancellation
- Sets status to `cancelled`
- Worker checks cancellation flag between steps
- Graceful shutdown with final event

## 10) Schema Strategy (Implemented)
**Current implementation: public schema**
- All tables in `public` schema for PostgREST compatibility
- Query using `supabase.from('<table>')`
- No custom schema exposure needed
- Automated setup wizard for first-time database creation

### Acceptance test
- ✅ UI can load templates/runs/sessions via `supabase.from(...)` without errors
- ✅ Automated database setup wizard appears when tables don't exist
- ✅ Real-time subscriptions work out of the box

## 11) Security / RLS
- Row Level Security enabled on all tables
- Authenticated users scoped by session membership (future)
- Anon policies for prototyping (current)
- Workers use service-role key server-side only
- Artifacts stored in Supabase Storage with scoped access

## 12) Deployment Targets
- **UI**: Vercel (Next.js/React)
- **DB/Functions**: Supabase (Postgres + Edge Functions)
- **Workers**: DO Droplet / DOKS / GitHub Actions
- **CI/CD**: GitHub Actions

## 13) MVP Functional Requirements
1. ✅ Sessions CRUD + archive
2. ✅ Templates CRUD
3. ✅ Runs create/list/filter
4. ✅ Claim endpoint with SKIP LOCKED (SQL function)
5. ⏳ Worker reference implementation
6. ⏳ Heartbeat + stuck recovery
7. ✅ Cancel run (SQL function)
8. ✅ Realtime Runboard UI
9. ⏳ Artifacts upload + viewer
10. ⏳ Spec Kit generate/validate runs

Legend: ✅ Implemented | ⏳ In Progress | ❌ Not Started

## 14) Acceptance Criteria (Hard)
- Multiple workers execute in parallel with zero double-runs
- Runboard updates within 2s of status changes
- Worker death triggers recovery within timeout
- No database errors in production (schema/table not found)
- "Generate Spec Kit" produces 4 files + attaches artifacts
- Automated setup wizard guides new users through database creation

## 15) Current Implementation Status

### ✅ Completed (M0 - Database Foundation)
- Database schema in `public` with 7 tables
- Automated setup wizard with 3-step guide
- SQL functions for atomic claiming, heartbeat, cancel
- RLS policies for security
- Real-time publication configured
- UI tabs: Chat, Templates, Runs, Spec Kit, Runboard
- Basic Runboard with lanes A/B/C/D

### ⏳ In Progress (M1 - Execution Core)
- Enhanced Edge Function executor
- Worker reference implementation
- Stuck run recovery sweeper
- Enhanced Runboard visualization

### ❌ Not Started (M2 - Scale & M3 - Spec Kit)
- Multi-worker deployment
- Artifact storage integration
- Spec Kit generator run type
- Production deployment configs

## 16) Pulser SDK Install Instruction (Required)
Documentation must include:
- Install Pulser SDK section
- Adapter interface definition
- Integration with run templates
- Future: templates can be executed by Pulser agents
