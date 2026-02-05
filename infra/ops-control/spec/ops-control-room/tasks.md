# Tasks — Ops Control Room

## Legend
- ✅ Complete
- ⏳ In Progress
- ❌ Not Started
- 🔒 Blocked

---

## T0 — Spec Kit + CI ✅ COMPLETE

- [x] T0.1 Create `spec/ops-control-room/{constitution,prd,plan,tasks}.md`
- [x] T0.2 Add CI workflow to enforce Spec Kit presence + minimal structure
- [x] T0.3 Add validator script `scripts/validate_spec_kit.py`
- [x] T0.4 Test CI workflow locally
- [x] T0.5 Document Spec Kit structure in README

**Completed:** January 8, 2026

---

## T1 — DB + Schema Setup ✅ COMPLETE

- [x] T1.1 Create `public` schema tables (sessions, runs, run_events, artifacts, run_templates, spec_docs, run_steps)
- [x] T1.2 Migration: create indexes for performance
- [x] T1.3 Migration: create SQL functions (claim_runs, heartbeat_run, cancel_run, enqueue_run, complete_run)
- [x] T1.4 Migration: enable RLS policies
- [x] T1.5 Migration: create realtime publication
- [x] T1.6 Create comprehensive `FULL_SETUP.sql` migration
- [x] T1.7 Smoke test: verify tables exist and are queryable
- [x] T1.8 Create automated database setup wizard (DatabaseSetup.tsx)
- [x] T1.9 Test setup wizard flow (copy SQL → run → refresh)
- [x] T1.10 Documentation: DATABASE_SETUP_FIXED.md

**Completed:** January 8, 2026

---

## T2 — Edge Function: ops-executor ⏳ IN PROGRESS

### Core Endpoints
- [ ] T2.1 Implement `/runs.create`
  - [ ] T2.1.1 Validate input schema
  - [ ] T2.1.2 Insert run with status=queued
  - [ ] T2.1.3 Return run_id
  - [ ] T2.1.4 Error handling

- [ ] T2.2 Implement `/runs.claim` with SKIP LOCKED
  - [ ] T2.2.1 Parse worker_id, lanes, session_id, limit
  - [ ] T2.2.2 Call SQL function `claim_runs()`
  - [ ] T2.2.3 Return claimed runs array
  - [ ] T2.2.4 Handle empty queue gracefully

- [ ] T2.3 Implement `/runs.heartbeat`
  - [ ] T2.3.1 Validate run_id and worker_id
  - [ ] T2.3.2 Call SQL function `heartbeat_run()`
  - [ ] T2.3.3 Return success/error

- [ ] T2.4 Implement `/runs.cancel`
  - [ ] T2.4.1 Validate run_id
  - [ ] T2.4.2 Call SQL function `cancel_run()`
  - [ ] T2.4.3 Append cancellation event
  - [ ] T2.4.4 Return confirmation

- [ ] T2.5 Implement `/events.append`
  - [ ] T2.5.1 Parse events array
  - [ ] T2.5.2 Batch insert into run_events
  - [ ] T2.5.3 Handle large event batches
  - [ ] T2.5.4 Return inserted count

- [ ] T2.6 Implement `/artifacts.put`
  - [ ] T2.6.1 Handle small text artifacts (direct insert)
  - [ ] T2.6.2 Handle file uploads (Supabase Storage)
  - [ ] T2.6.3 Generate signed URLs
  - [ ] T2.6.4 Return artifact_id + access URL

### Infrastructure
- [ ] T2.7 Add CORS headers
- [ ] T2.8 Add request logging
- [ ] T2.9 Add error handling middleware
- [ ] T2.10 Add rate limiting (optional)
- [ ] T2.11 Contract tests (basic)
- [ ] T2.12 Integration tests with test database
- [ ] T2.13 Deploy to Supabase

**Dependencies:** T1 complete

---

## T3 — Worker Fleet ❌ NOT STARTED

### Reference Worker Implementation
- [ ] T3.1 Worker core loop
  - [ ] T3.1.1 Initialize worker (load config, connect to Supabase)
  - [ ] T3.1.2 Main loop: poll /runs.claim every N seconds
  - [ ] T3.1.3 Execute claimed runs in parallel (configurable concurrency)
  - [ ] T3.1.4 Handle graceful shutdown (SIGTERM/SIGINT)
  - [ ] T3.1.5 Error recovery and retry logic

- [ ] T3.2 Heartbeat mechanism
  - [ ] T3.2.1 Background heartbeat thread/interval
  - [ ] T3.2.2 Send heartbeat every 2-5 seconds
  - [ ] T3.2.3 Stop heartbeat on run completion
  - [ ] T3.2.4 Handle heartbeat failures

- [ ] T3.3 Step execution engine
  - [ ] T3.3.1 Parse step DSL (shell/docker/api/mcp)
  - [ ] T3.3.2 Execute shell commands
  - [ ] T3.3.3 Execute docker commands
  - [ ] T3.3.4 Execute API calls
  - [ ] T3.3.5 Execute MCP tool calls (future)
  - [ ] T3.3.6 Capture stdout/stderr
  - [ ] T3.3.7 Stream output as events

- [ ] T3.4 Cancellation handling
  - [ ] T3.4.1 Check cancellation flag between steps
  - [ ] T3.4.2 Abort current step on cancellation
  - [ ] T3.4.3 Send cancellation acknowledgment event
  - [ ] T3.4.4 Clean up resources

- [ ] T3.5 Event and artifact streaming
  - [ ] T3.5.1 Buffer events locally
  - [ ] T3.5.2 Batch send to /events.append
  - [ ] T3.5.3 Upload artifacts to /artifacts.put
  - [ ] T3.5.4 Handle upload failures

### Containerization
- [ ] T3.6 Create Dockerfile
  - [ ] T3.6.1 Base image selection (node:20-alpine or python:3.12-slim)
  - [ ] T3.6.2 Install dependencies
  - [ ] T3.6.3 Copy worker code
  - [ ] T3.6.4 Set entrypoint
  - [ ] T3.6.5 Health check endpoint

- [ ] T3.7 Build and test container locally
- [ ] T3.8 Push to container registry (GHCR or DO Registry)

### Deployment
- [ ] T3.9 DigitalOcean Droplet deployment
  - [ ] T3.9.1 Create droplet with Docker installed
  - [ ] T3.9.2 Create systemd service file
  - [ ] T3.9.3 Configure environment variables
  - [ ] T3.9.4 Set up log rotation
  - [ ] T3.9.5 Enable auto-restart
  - [ ] T3.9.6 Deploy and test

- [ ] T3.10 DigitalOcean App Platform deployment (alternative)
  - [ ] T3.10.1 Create app spec
  - [ ] T3.10.2 Configure environment
  - [ ] T3.10.3 Deploy worker as service
  - [ ] T3.10.4 Test scaling

- [ ] T3.11 DOKS (Kubernetes) deployment (optional)
  - [ ] T3.11.1 Create Kubernetes deployment manifest
  - [ ] T3.11.2 Create ConfigMap for config
  - [ ] T3.11.3 Create Secret for credentials
  - [ ] T3.11.4 Set up HPA (Horizontal Pod Autoscaler)
  - [ ] T3.11.5 Deploy to DOKS cluster
  - [ ] T3.11.6 Test auto-scaling

**Dependencies:** T2 complete
**Estimated:** 5-7 days

---

## T4 — UI Enhancement ⏳ PARTIALLY COMPLETE

### Runboard
- [x] T4.1 Basic Runboard component with lanes A/B/C/D
- [ ] T4.2 Enhanced lane visualization
  - [ ] T4.2.1 Queue depth counter
  - [ ] T4.2.2 Active run card with details
  - [ ] T4.2.3 Heartbeat indicator (pulse animation)
  - [ ] T4.2.4 Last completed run status
  - [ ] T4.2.5 Lane color coding by status

- [ ] T4.3 Run controls
  - [ ] T4.3.1 Cancel button with confirmation modal
  - [ ] T4.3.2 Retry button for failed runs
  - [ ] T4.3.3 View logs button
  - [ ] T4.3.4 View artifacts button

- [ ] T4.4 Live log streaming
  - [ ] T4.4.1 Real-time event subscription
  - [ ] T4.4.2 Auto-scroll to bottom
  - [ ] T4.4.3 Log level filtering
  - [ ] T4.4.4 Search in logs
  - [ ] T4.4.5 Export logs

### Templates
- [x] T4.5 List templates
- [ ] T4.6 Create/edit template form
  - [ ] T4.6.1 Basic template info (name, description)
  - [ ] T4.6.2 Params schema builder (JSON Schema)
  - [ ] T4.6.3 Default lane selection
  - [ ] T4.6.4 Step DSL editor
  - [ ] T4.6.5 Template preview
  - [ ] T4.6.6 Save and validation

- [ ] T4.7 Template usage
  - [ ] T4.7.1 Fill params form (auto-generated from schema)
  - [ ] T4.7.2 Preview generated run
  - [ ] T4.7.3 Submit to queue

### Runs
- [x] T4.8 Basic run history list
- [ ] T4.9 Advanced filtering
  - [ ] T4.9.1 Filter by status (queued/running/success/error/cancelled)
  - [ ] T4.9.2 Filter by lane (A/B/C/D)
  - [ ] T4.9.3 Filter by template
  - [ ] T4.9.4 Filter by date range
  - [ ] T4.9.5 Search by run ID or params

- [ ] T4.10 Run details view
  - [ ] T4.10.1 Full run metadata
  - [ ] T4.10.2 Timeline visualization
  - [ ] T4.10.3 Events list with filtering
  - [ ] T4.10.4 Artifacts gallery
  - [ ] T4.10.5 Export run data (JSON/Markdown)

### Artifacts
- [ ] T4.11 Artifact viewer component
  - [ ] T4.11.1 Markdown renderer
  - [ ] T4.11.2 JSON viewer with syntax highlighting
  - [ ] T4.11.3 Diff viewer (side-by-side)
  - [ ] T4.11.4 Image/screenshot viewer
  - [ ] T4.11.5 File download links
  - [ ] T4.11.6 Artifact search and filtering

### Real-time
- [x] T4.12 Basic real-time subscriptions
- [ ] T4.13 Enhanced real-time features
  - [ ] T4.13.1 Connection status indicator
  - [ ] T4.13.2 Auto-reconnect on disconnect
  - [ ] T4.13.3 Optimistic UI updates
  - [ ] T4.13.4 Offline queue for actions

**Dependencies:** T1 complete, T2 partial
**Estimated:** 3-5 days

---

## T5 — Spec Kit Run Types ❌ NOT STARTED

### Generator Template
- [ ] T5.1 Create `generate_spec_kit` template
  - [ ] T5.1.1 Input schema (project name, description, goals)
  - [ ] T5.1.2 Generate constitution.md from template
  - [ ] T5.1.3 Generate prd.md from inputs
  - [ ] T5.1.4 Generate plan.md with phases
  - [ ] T5.1.5 Generate tasks.md breakdown
  - [ ] T5.1.6 Create zip artifact with all files
  - [ ] T5.1.7 Store individual files as separate artifacts

### Validator Template
- [ ] T5.2 Create `validate_spec_kit` template
  - [ ] T5.2.1 Check required files exist
  - [ ] T5.2.2 Validate file structure (headers, sections)
  - [ ] T5.2.3 Check for acceptance criteria in PRD
  - [ ] T5.2.4 Check for tasks breakdown
  - [ ] T5.2.5 Generate validation report JSON
  - [ ] T5.2.6 Store validation results as artifact

### UI Integration
- [ ] T5.3 Spec Kit panel enhancements
  - [ ] T5.3.1 "Generate New Spec Kit" button
  - [ ] T5.3.2 Form for spec kit inputs
  - [ ] T5.3.3 Preview generated files
  - [ ] T5.3.4 Download zip button
  - [ ] T5.3.5 Validation status display

### CI Integration
- [x] T5.4 GitHub Actions workflow for validation
- [x] T5.5 Python validation script
- [ ] T5.6 PR comment with validation results
- [ ] T5.7 Block merge on validation failure

**Dependencies:** T2 complete, T3 partial
**Estimated:** 3-4 days

---

## T6 — Stuck Run Recovery ❌ NOT STARTED

### Sweeper Implementation
- [ ] T6.1 Create stuck-run sweeper Edge Function
  - [ ] T6.1.1 Query runs where `now() - heartbeat_at > timeout`
  - [ ] T6.1.2 Check attempt counter vs max_attempts
  - [ ] T6.1.3 Requeue if attempts remaining
  - [ ] T6.1.4 Mark as failed if max attempts exceeded
  - [ ] T6.1.5 Send notification events

- [ ] T6.2 Configure cron trigger
  - [ ] T6.2.1 Set up Supabase cron job
  - [ ] T6.2.2 Run every 30-60 seconds
  - [ ] T6.2.3 Add monitoring/logging

### Retry Logic
- [ ] T6.3 Implement retry strategies
  - [ ] T6.3.1 Exponential backoff calculation
  - [ ] T6.3.2 Configurable retry delays
  - [ ] T6.3.3 Max attempts per run
  - [ ] T6.3.4 Idempotency checks

### Monitoring
- [ ] T6.4 Add metrics collection
  - [ ] T6.4.1 Stuck run count per hour
  - [ ] T6.4.2 Recovery success rate
  - [ ] T6.4.3 Average time to recovery
  - [ ] T6.4.4 Alert on high stuck rate

**Dependencies:** T2 complete, T3 complete
**Estimated:** 2-3 days

---

## T7 — Production Deployment ❌ NOT STARTED

### Vercel Deployment
- [ ] T7.1 Production build configuration
  - [ ] T7.1.1 Optimize bundle size
  - [ ] T7.1.2 Configure environment variables
  - [ ] T7.1.3 Set up custom domain
  - [ ] T7.1.4 Enable edge caching
  - [ ] T7.1.5 Configure redirects and rewrites

- [ ] T7.2 CI/CD for UI
  - [ ] T7.2.1 GitHub Actions workflow for Vercel deploy
  - [ ] T7.2.2 Preview deployments on PRs
  - [ ] T7.2.3 Production deploy on merge to main
  - [ ] T7.2.4 Rollback strategy

### Supabase Production
- [ ] T7.3 Database optimization
  - [ ] T7.3.1 Connection pooling (PgBouncer)
  - [ ] T7.3.2 Index optimization
  - [ ] T7.3.3 Query performance tuning
  - [ ] T7.3.4 Automated backups

- [ ] T7.4 Monitoring and alerts
  - [ ] T7.4.1 Set up Supabase monitoring
  - [ ] T7.4.2 Database health checks
  - [ ] T7.4.3 Edge Function error alerts
  - [ ] T7.4.4 Usage metrics dashboard

### Worker Deployment
- [ ] T7.5 DigitalOcean production setup
  - [ ] T7.5.1 Provision production droplets
  - [ ] T7.5.2 Load balancer configuration
  - [ ] T7.5.3 Auto-scaling rules
  - [ ] T7.5.4 Log aggregation (Papertrail/Logtail)
  - [ ] T7.5.5 Monitoring (Prometheus/Grafana)

- [ ] T7.6 CI/CD for workers
  - [ ] T7.6.1 GitHub Actions workflow for worker deploy
  - [ ] T7.6.2 Build and push container image
  - [ ] T7.6.3 Deploy to DO via doctl
  - [ ] T7.6.4 Health checks and rollback

### Documentation
- [ ] T7.7 Operator manual
  - [ ] T7.7.1 Deployment guide
  - [ ] T7.7.2 Troubleshooting guide
  - [ ] T7.7.3 Runbook templates guide
  - [ ] T7.7.4 API reference

- [ ] T7.8 Architecture documentation
  - [ ] T7.8.1 System architecture diagram
  - [ ] T7.8.2 Data flow diagrams
  - [ ] T7.8.3 Security model
  - [ ] T7.8.4 Scaling guide

**Dependencies:** T2, T3, T4 complete
**Estimated:** 3-5 days

---

## T8 — Pulser SDK Integration ❌ NOT STARTED

### Documentation
- [ ] T8.1 Create Pulser integration guide
  - [ ] T8.1.1 Installation instructions
  - [ ] T8.1.2 Adapter interface definition
  - [ ] T8.1.3 Example runbook conversion
  - [ ] T8.1.4 Event streaming setup

### Adapter Layer (Future)
- [ ] T8.2 Design Pulser adapter interface
- [ ] T8.3 Implement adapter for run templates
- [ ] T8.4 Test Pulser agent execution
- [ ] T8.5 Documentation and examples

**Dependencies:** None (documentation only for v1)
**Estimated:** 1 day (docs only)

---

## Summary

### Completed: 2 task groups ✅
- T0: Spec Kit + CI
- T1: DB + Schema Setup

### In Progress: 2 task groups ⏳
- T2: Edge Function (0/13 subtasks)
- T4: UI Enhancement (3/27 subtasks)

### Not Started: 5 task groups ❌
- T3: Worker Fleet (0/26 subtasks)
- T5: Spec Kit Run Types (0/11 subtasks)
- T6: Stuck Run Recovery (0/8 subtasks)
- T7: Production Deployment (0/21 subtasks)
- T8: Pulser SDK Integration (0/5 subtasks)

### Total Tasks
- **111 total subtasks**
- **18 completed (16%)**
- **93 remaining (84%)**

### Critical Path for MVP
1. Complete T2 (Edge Function) - 2-3 days
2. Complete T3 (Worker Fleet) - 5-7 days
3. Complete T4 (UI Enhancement) - 3-5 days
4. Complete T6 (Stuck Recovery) - 2-3 days

**Estimated time to MVP:** 12-18 days
