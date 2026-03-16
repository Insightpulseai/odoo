# Tasks — Odoo Release Gates Control Plane (Supabase SSOT)

**Spec Bundle**: `spec/odoo-release-gates-control-plane/`

---

## T0 — Spec Finalization and Prerequisites

- [ ] Confirm `spec/odoo-platform-personas/` spec bundle is complete and consistent
- [ ] Run `/speckit.analyze` on both spec bundles to detect cross-spec contradictions
- [ ] Verify Supabase CLI is authenticated and linked to `spdtwktxdalcfigzeqrz`
- [ ] Confirm `ops` schema does not yet exist in the Supabase project (`\dn` in psql)
- [ ] Confirm `supabase db diff` runs without error
- [ ] Mark `spec/odoo-release-gates-control-plane/*` as SSOT for control-plane schema

**Done when**:
- No spec contradictions between personas spec and this spec
- Supabase project is accessible and ops schema is confirmed empty
- CI can run `supabase db diff` cleanly

---

## T1 — Schema Migration: ops Schema and Enums

- [ ] Author migration: create `ops` schema
- [ ] Define enum types: `ops_gate_code` (`G1`, `G2`, `G3`, `G4`), `ops_release_status`, `ops_gate_status`, `ops_decision_type`, `ops_processing_status`
- [ ] Run migration against local Supabase (`supabase db reset`)
- [ ] Verify schema and enums present via `\dn` and `\dT`

**Done when**: `ops` schema exists; all enums defined; no migration errors

---

## T2 — Schema Migration: Core Tables (In Dependency Order)

- [ ] `ops.releases` — with all required fields and constraints from FR-1
- [ ] `ops.release_gates` — FK to releases; unique on `(release_id, gate_code)`
- [ ] `ops.gate_checks` — FK to release_gates
- [ ] `ops.approvals` — FK to releases and release_gates
- [ ] `ops.evidence_artifacts` — FK to releases, gate, check; CHECK constraint for orphan protection
- [ ] `ops.exceptions` — FK to releases; `expires_at NOT NULL` constraint enforced
- [ ] `ops.deployments` — FK to releases; self-FK for rollback_of
- [ ] `ops.environment_events` — append-only BEFORE trigger (raises exception on UPDATE/DELETE)
- [ ] `ops.event_ingest_log` — unique index on `idempotency_key`
- [ ] `ops.incidents` — FK to deployments
- [ ] `ops.recovery_drills` — FK to evidence_artifacts
- [ ] Run `supabase db push` against staging Supabase project
- [ ] Confirm zero drift: `supabase db diff` returns no output

**Done when**: All 11 tables created; FK constraints verified; append-only trigger on environment_events confirmed; zero drift

---

## T3 — Edge Function: ops-event-ingest

- [ ] Scaffold `supabase/functions/ops-event-ingest/index.ts`
- [ ] Implement envelope parsing and schema version validation
- [ ] Implement idempotency key deduplication (unique conflict strategy in ops.event_ingest_log)
- [ ] Implement routing to domain handlers:
  - `build_complete` → gate_checks insert (G1)
  - `gate_signoff` → release_gates update + approvals insert
  - `deployment_event` → deployments insert/update
  - `health_check` → gate_checks insert (G4) + deployment g4_status update
  - `environment_event` → environment_events insert
- [ ] Write unit tests covering:
  - First-time accept → `processing_status = 'accepted'`
  - Duplicate retry → `processing_status = 'duplicate'`, no second terminal record
  - Unknown schema version → HTTP 422
  - Missing required field → HTTP 400
  - Unknown release_id → HTTP 409
- [ ] Deploy function: `supabase functions deploy ops-event-ingest`

**Done when**: All unit tests pass; function deployed; manual curl test returns HTTP 200 with `status: accepted`

---

## T4 — Gate Evaluation RPC

- [ ] Implement `ops.evaluate_gate(gate_id UUID) RETURNS text` in a migration
- [ ] Implement `ops.is_eligible_for_promotion(release_id UUID, target_env text) RETURNS boolean`
- [ ] Write SQL unit tests covering:
  - All gates passed → eligible = true
  - G2 failed → eligible = false for staging and production
  - G3 bypassed with active exception → eligible = true for production
  - G3 bypassed with expired exception → eligible = false
- [ ] Run tests via `supabase db reset && psql -c "SELECT * FROM ..."`

**Done when**: All evaluation cases return correct results; exception expiry check confirmed working

---

## T5 — RLS Policies

- [ ] Author migration: create roles `ci_service_role`, `release_manager`, `qa_tester`, `sre`, `developer`, `audit_reader`
- [ ] Enable RLS on all `ops.*` tables
- [ ] Author policies per PRD access boundary table
- [ ] Write integration tests:
  - `ci_service_role` cannot INSERT to `ops.approvals` → permission denied
  - `qa_tester` cannot UPDATE `ops.exceptions` → permission denied
  - `audit_reader` can SELECT all `ops.*` tables
  - `release_manager` can INSERT `ops.approvals`
- [ ] Deploy policies; run integration tests

**Done when**: All integration tests pass; no privilege escalation paths identified

---

## T6 — Reporting Views

- [ ] `ops.v_release_gate_summary` — per-release, per-gate: status, check counts, passed/failed/skipped
- [ ] `ops.v_promotion_eligibility` — current eligibility per release for staging and production
- [ ] `ops.v_evidence_completeness` — evidence artifact count per gate per release, gaps flagged
- [ ] `ops.v_exception_status` — active, expired, and pending-review exceptions with TTL remaining
- [ ] `ops.v_deployment_history` — deployment + rollback history with G4 resolution status
- [ ] Verify views return correct data against test release data from T3 test runs
- [ ] Grant SELECT on views to appropriate roles

**Done when**: All 5 views created; data verified against known test state; grants applied

---

## T7 — CI Event Producer (GitHub Actions)

- [ ] Identify target CI workflow (first workflow triggered on merge to `main`)
- [ ] Add step to POST to `ops-event-ingest` after build completes:
  - `event_type: build_complete`, `gate_code: G1`, `status: pass | fail`
  - `idempotency_key: github_actions/{run_id}/build_complete`
  - Auth: Supabase service role key from GitHub Actions secret
- [ ] Test: trigger a real merge → verify `ops.gate_checks` has G1 record
- [ ] Verify `ops.event_ingest_log` shows `processing_status = 'accepted'`

**Done when**: Real CI merge populates G1 gate_check record in ops.*

---

## T8 — Agent Event Producer (n8n or Direct)

- [ ] Identify QA signoff step in current release workflow (n8n or manual)
- [ ] Add event POST to `ops-event-ingest` after QA signoff:
  - `event_type: gate_signoff`, `gate_code: G2`, `decision: approved`
  - `idempotency_key: agent/{session_id}/gate_signoff/G2`
  - Include `approver_id`, `persona_role: qa_tester`, `rationale_structured`
- [ ] Test: execute QA signoff → verify `ops.release_gates` G2 status transitions to `passed`
- [ ] Verify `ops.approvals` record created with correct fields

**Done when**: QA signoff event populates G2 gate and approval record in ops.*

---

## T9 — Full Dry Run and Production Adoption

- [ ] Select a real upcoming release as dry-run subject
- [ ] Trace full cycle through G1 → G2 → G3 → deploy → G4:
  - [ ] Create `ops.releases` record
  - [ ] G1: CI event → gate_checks populated
  - [ ] G2: QA signoff → release_gates G2 passed
  - [ ] G3: Release manager approval → ops.approvals + G3 passed
  - [ ] Deploy to staging → ops.deployments record
  - [ ] G4: Health check event → G4 resolved
  - [ ] Deploy to production → ops.deployments production record
- [ ] Query `ops.v_release_gate_summary` and confirm full chain visible
- [ ] Confirm `ops.v_promotion_eligibility` reflected correct eligibility at each stage
- [ ] Document ambiguities found; update spec if needed
- [ ] Update release runbook to reference `ops.*` as canonical release state
- [ ] Tag spec bundle as `v1.0-production`

**Done when**:
- Full release chain reconstructible from `ops.*` alone
- Release runbook updated
- Spec bundle tagged `v1.0-production`
- No open ambiguities in gate or evidence requirements
