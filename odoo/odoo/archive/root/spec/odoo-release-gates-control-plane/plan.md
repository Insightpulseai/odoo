# Implementation Plan — Odoo Release Gates Control Plane (Supabase SSOT)

**Spec Bundle**: `spec/odoo-release-gates-control-plane/`
**Status**: Draft v1.0
**Date**: 2026-02-24

---

## Overview

This plan implements the `ops.*` control plane in Supabase. It proceeds in 8 phases: from schema design through Edge Function ingest, gate evaluation logic, RLS enforcement, reporting views, CI/agent event producers, and dry-run validation.

The plan assumes `spec/odoo-platform-personas/` provides the canonical persona and gate model as upstream SSOT.

---

## Phase 0 — Spec Finalization and Prerequisites

**Goal**: Lock spec and verify all prerequisites before any schema work.

**Prerequisites**:
- `spec/odoo-platform-personas/` spec bundle complete and consistent
- Supabase project `spdtwktxdalcfigzeqrz` active with admin access
- `supabase/` directory initialized in repo with CLI linked to project
- `ops` schema does not yet exist (or is empty — verify before Phase 1)

**Outputs**:
- [ ] Confirmed ops schema is empty or non-existent in target Supabase project
- [ ] Supabase CLI authenticated and linked (`supabase link --project-ref spdtwktxdalcfigzeqrz`)
- [ ] Spec bundle consistency check passed (no cross-spec contradictions)

**Acceptance**: CI can run `supabase db diff` without error.

---

## Phase 1 — Schema Migration: Core Tables

**Goal**: Create all 11 `ops.*` tables in correct dependency order.

**Migration files** (append-only, in `supabase/migrations/`):
1. `2026XXXXXXXXXXX_ops_schema.sql` — Create `ops` schema, `ops_event_type` enum
2. `2026XXXXXXXXXXX_ops_releases.sql` — `ops.releases`
3. `2026XXXXXXXXXXX_ops_release_gates.sql` — `ops.release_gates` (FK → releases)
4. `2026XXXXXXXXXXX_ops_gate_checks.sql` — `ops.gate_checks` (FK → release_gates)
5. `2026XXXXXXXXXXX_ops_approvals.sql` — `ops.approvals` (FK → releases, release_gates)
6. `2026XXXXXXXXXXX_ops_evidence_artifacts.sql` — `ops.evidence_artifacts`
7. `2026XXXXXXXXXXX_ops_exceptions.sql` — `ops.exceptions` (FK → releases)
8. `2026XXXXXXXXXXX_ops_deployments.sql` — `ops.deployments` (FK → releases)
9. `2026XXXXXXXXXXX_ops_environment_events.sql` — `ops.environment_events` (append-only trigger)
10. `2026XXXXXXXXXXX_ops_event_ingest_log.sql` — `ops.event_ingest_log`
11. `2026XXXXXXXXXXX_ops_incidents.sql` and `ops_recovery_drills.sql`

**Constraints to enforce in DDL**:
- `ops.exceptions.expires_at` NOT NULL (constitution NR-5)
- `ops.environment_events` has a `BEFORE UPDATE OR DELETE` trigger that raises exception (append-only)
- `ops.evidence_artifacts`: CHECK that at least one of `release_id`, `gate_id`, `check_id` is non-null when `artifact_type != 'reference'`
- Unique index on `ops.event_ingest_log (idempotency_key)` for deduplication
- All tables: `created_at TIMESTAMPTZ DEFAULT now() NOT NULL`

**Acceptance**: `supabase db push` applies all migrations cleanly; `supabase db diff` shows no residual drift.

---

## Phase 2 — Edge Function: Event Ingest

**Goal**: Implement the canonical event ingestion Edge Function with idempotency and schema validation.

**Function**: `supabase/functions/ops-event-ingest/index.ts`

**Responsibilities**:
1. Parse and validate inbound event envelope (`schema_version`, `idempotency_key`, `event_type`, `source_system`, `release_id`)
2. Insert row to `ops.event_ingest_log` with `processing_status = 'accepted'` or `'duplicate'` or `'rejected'`
3. If duplicate (`idempotency_key` already accepted): return HTTP 200 with original result, no further processing
4. If valid: route to appropriate domain handler (release event, gate event, check event, approval event)
5. Domain handler inserts/updates the relevant `ops.*` tables
6. Return structured response: `{ "ingest_id": "...", "status": "accepted" | "duplicate" | "rejected", "detail": {...} }`

**Idempotency Implementation**:
```sql
-- On INSERT attempt for ops.event_ingest_log:
INSERT INTO ops.event_ingest_log (idempotency_key, ...)
ON CONFLICT (idempotency_key) DO UPDATE
  SET processing_status = 'duplicate', received_at = now()
RETURNING processing_status, ingest_id
```

**Error Handling**:
- Unknown `schema_version`: HTTP 422 with `{ "error": "unsupported_schema_version" }`
- Missing required fields: HTTP 400
- FK constraint violation (unknown `release_id`): HTTP 409
- Server error: HTTP 500, `processing_status = 'error'`

**Acceptance**:
- Unit tests cover: first-time accept, duplicate retry, invalid schema version, missing fields
- Load test: 100 concurrent events with 30% duplicates → zero duplicate terminal outcomes

---

## Phase 3 — Gate Evaluation Logic

**Goal**: Implement the gate status evaluation function that determines if a gate passes, fails, or is in progress.

**Function or RPC**: `ops.evaluate_gate(gate_id UUID)` → `gate_status text`

**Evaluation Rules** (per constitution data integrity rules):
- `G1 passed` when: all required `ops.gate_checks` for this `gate_id` have `status = 'pass'`
- `G2 passed` when: G2 evidence artifacts present AND no `status = 'fail'` checks
- `G3 passed` when: approval record with `decision = 'approved'` exists, rollback plan evidence artifact exists, G2 gate passed
- `G4 passed` when: deployment `g4_status = 'passed'` AND health check evidence artifact exists

**Production Promotion Block**:
- Enforce as Supabase DB function or RPC: `ops.is_eligible_for_promotion(release_id UUID, target_env text) → boolean`
- Returns `false` if any required gate for `target_env` is not `passed` (or `bypassed` with active exception)

**Acceptance**:
- Unit tests: release with all gates passed → `is_eligible_for_promotion = true`
- Release with G2 failed → `is_eligible_for_promotion = false` for staging and production
- Release with G3 bypassed via active exception → `is_eligible_for_promotion = true` for production

---

## Phase 4 — Row-Level Security Policies

**Goal**: Enforce RLS boundaries from the PRD access boundary table.

**Service Roles to Create**:
- `ci_service_role` — used by GitHub Actions and agent CI pipelines
- `release_manager` — used by human release managers and release orchestration agents
- `qa_tester` — used by QA personas
- `sre` — used by SRE personas
- `developer` — used by developer personas
- `audit_reader` — read-only for audit/compliance queries

**Policy Pattern** (example for ops.approvals):
```sql
-- release_manager can read all approvals for their releases
CREATE POLICY "release_manager_read_approvals"
  ON ops.approvals FOR SELECT
  TO release_manager
  USING (release_id IN (SELECT release_id FROM ops.releases WHERE created_by = auth.uid()));

-- qa_tester can insert their own approvals
CREATE POLICY "qa_tester_insert_approvals"
  ON ops.approvals FOR INSERT
  TO qa_tester
  WITH CHECK (approver_id = auth.uid() AND persona_role = 'qa_tester');
```

**Acceptance**:
- Integration tests verify: ci_service_role cannot insert to ops.approvals
- qa_tester cannot update ops.exceptions
- audit_reader has SELECT on all ops.* tables, no INSERT/UPDATE/DELETE

---

## Phase 5 — Reporting Views

**Goal**: Implement queryable views for release health and gate status reporting.

**Views to Create**:
- `ops.v_release_gate_summary` — per-release, per-gate status with check counts
- `ops.v_promotion_eligibility` — current eligibility for staging/production per release
- `ops.v_evidence_completeness` — evidence artifact coverage per gate per release
- `ops.v_exception_status` — active, expired, and pending-review exceptions
- `ops.v_deployment_history` — deployment + rollback history with G4 status

**Acceptance**:
- All views return data for at least one test release inserted during Phase 2 testing
- `v_promotion_eligibility` correctly reflects gate evaluation from Phase 3

---

## Phase 6 — CI/Agent Event Producers

**Goal**: Wire at least one CI workflow and one agent to post events to the ingest function.

**CI Producer** (GitHub Actions):
- Target workflow: first workflow that triggers on merge to `main` (branch build)
- Action: POST to `ops-event-ingest` with `event_type = 'build_complete'`, `gate_code = 'G1'`, `status = 'pass' | 'fail'`
- `idempotency_key`: `github_actions/{run_id}/build_complete`

**Agent Producer** (n8n or direct):
- Target: QA validation signoff step
- Action: POST `event_type = 'gate_signoff'`, `gate_code = 'G2'`, approval metadata

**Acceptance**:
- After a PR merge, `ops.gate_checks` has a G1 record for the release
- After a QA signoff, `ops.release_gates` has G2 `status = 'passed'`
- `ops.event_ingest_log` shows `processing_status = 'accepted'` for both events

---

## Phase 7 — Dry Run and Production Adoption

**Goal**: Execute one full release cycle end-to-end through the control plane and promote to production SSOT.

**Dry Run Steps**:
1. Create release record for a real upcoming release
2. G1: merge + CI event → verify `ops.gate_checks` populated
3. G2: QA signoff → verify `ops.release_gates` G2 passed
4. G3: Release manager approval → verify `ops.approvals` record + G3 gate passed
5. Deploy to staging → verify `ops.deployments` record
6. G4: Health check → verify G4 gate resolved
7. Deploy to production → verify full chain queryable from SSOT

**Adoption Deliverables**:
- Release runbook updated to reference `ops.*` as the canonical release state
- Release manager uses `ops.v_promotion_eligibility` before promoting
- Exception process updated to use `ops.exceptions` instead of ad hoc chat

**Acceptance**:
- Full release chain is reconstructible from `ops.*` alone (no CI log lookup required)
- No gate step is ambiguous about role or evidence requirement
- Spec bundle tagged as `v1.0-production`

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Supabase migration conflicts with existing ops.* tables | Low | High | Phase 0 audit verifies empty schema before Phase 1 |
| CI workflow doesn't emit events reliably | Medium | High | Phase 6 targets a single high-reliability workflow first |
| Idempotency key collision (different logical events, same key) | Low | High | Key format specification enforces logical uniqueness |
| RLS policies block legitimate CI writes | Medium | Medium | Integration test suite in Phase 4 catches this before production |
| Dry run reveals incomplete gate model | Low | Medium | Feeds back to persona spec v1.1; dry run is required before adoption |

---

## Milestone Summary

| Milestone | Phase | Deliverable |
|-----------|-------|------------|
| M0 | 0 | Spec locked; Supabase CLI linked; ops schema verified empty |
| M1 | 1 | All 11 ops.* tables migrated; drift = 0 |
| M2 | 2 | Event ingest Edge Function deployed; idempotency tested |
| M3 | 3 | Gate evaluation RPC live; promotion eligibility queryable |
| M4 | 4 | RLS policies active; integration tests pass |
| M5 | 5 | Reporting views live |
| M6 | 6 | At least one CI workflow + one agent posting events |
| M7 | 7 | Full dry run complete; spec tagged v1.0-production |
