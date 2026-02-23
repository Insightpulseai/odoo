# PRD — Odoo Release Gates Control Plane (Supabase SSOT)

**Spec Bundle**: `spec/odoo-release-gates-control-plane/`
**Status**: Draft v1.0
**Date**: 2026-02-24

---

## Problem Statement

The InsightPulseAI Odoo platform has no durable, queryable record of release decisions, gate outcomes, approvals, or evidence artifacts. Release governance state lives in:
- CI logs (ephemeral, vendor-locked)
- Chat messages (unstructured, unqueryable)
- Manual spreadsheets (not real-time, not agent-accessible)

This means:
- Post-mortems cannot reconstruct the release decision chain
- Auditors cannot verify gate compliance without manual investigation
- Agents and CI systems cannot read current release state to make promotion decisions
- Exception/bypass actions are not time-bounded or auditable

This spec defines a **Supabase-based control plane** for release governance, implemented under the `ops.*` schema.

---

## Goals

1. Persist every release, gate outcome, approval, evidence artifact, exception, and deployment as queryable records in Supabase
2. Provide CI and agent systems a stable, idempotent event ingestion contract
3. Support RLS-enforced role-scoped access aligned with persona operating contracts
4. Make all production promotions fully auditable from SSOT alone
5. Enable real-time reporting views for release health and gate status

## Non-Goals

- This spec does not define the persona/gate model (covered by `spec/odoo-platform-personas/`)
- This spec does not define CI workflow YAML implementation
- This spec does not define UI admin panels or dashboards
- This spec does not define Odoo module changes
- This spec does not cover vendor-specific secrets configuration

---

## Functional Requirements

### FR-1: ops.releases — Release Records

Each release cycle MUST have a record with:

| Field | Type | Notes |
|-------|------|-------|
| `release_id` | UUID | Stable identifier, generated at release creation |
| `project` | text | Repo/project identifier (e.g., `insightpulseai/odoo`) |
| `release_name` | text | Human-readable (e.g., `v2026.02.4`) |
| `environment_target` | text | `dev` \| `staging` \| `production` |
| `source_ref` | text | Git SHA, branch, or tag |
| `scope_metadata` | jsonb | Arbitrary structured metadata (modules changed, OCA updates, etc.) |
| `initiating_actor` | text | User ID, agent ID, or CI system identifier |
| `status` | text | `draft` \| `in_progress` \| `promoted` \| `rolled_back` \| `failed` |
| `created_at` | timestamptz | Set on insert |
| `created_by` | text | Auth UID or service account |

### FR-2: ops.release_gates — Gate Instances

Each gate check for each release MUST have a record:

| Field | Type | Notes |
|-------|------|-------|
| `gate_id` | UUID | |
| `release_id` | UUID | FK → ops.releases |
| `gate_code` | text | `G1` \| `G2` \| `G3` \| `G4` |
| `gate_name` | text | Derived from gate_code (denormalized for readability) |
| `status` | text | `pending` \| `in_progress` \| `passed` \| `failed` \| `bypassed` |
| `entered_at` | timestamptz | When gate evaluation began |
| `resolved_at` | timestamptz | When gate reached terminal state |
| `resolved_by` | text | Actor who resolved the gate |
| `exception_id` | UUID | FK → ops.exceptions (if bypassed) |

**Gate Semantics**:
- `G1` Build Integrity: passes when branch build succeeds and required checks pass
- `G2` Validation Readiness: passes when acceptance criteria mapped, test evidence attached
- `G3` Promotion Readiness: passes when evidence package complete, rollback criteria confirmed, accountable signoff recorded
- `G4` Post-Deploy Operational Confirmation: passes when health checks green and monitoring baseline confirmed

### FR-3: ops.gate_checks — Atomic Check Records

Individual checks that feed into a gate:

| Field | Type | Notes |
|-------|------|-------|
| `check_id` | UUID | |
| `gate_id` | UUID | FK → ops.release_gates |
| `check_name` | text | e.g., `unit_tests`, `lint`, `staging_deploy_health` |
| `source_system` | text | `github_actions` \| `agent` \| `manual` \| `monitoring` |
| `status` | text | `pass` \| `fail` \| `warning` \| `skipped` |
| `artifact_ref` | text | URL or path to supporting artifact |
| `created_at` | timestamptz | |
| `metadata` | jsonb | Check-specific detail |

### FR-4: ops.approvals — Approval Records

Every approval or rejection event MUST be persisted:

| Field | Type | Notes |
|-------|------|-------|
| `approval_id` | UUID | |
| `release_id` | UUID | FK → ops.releases |
| `gate_id` | UUID | FK → ops.release_gates (if gate-scoped) |
| `approver_id` | text | Auth UID or agent ID |
| `persona_role` | text | `developer` \| `qa_tester` \| `release_manager` \| `sre` |
| `decision` | text | `approved` \| `rejected` \| `request_changes` |
| `scope` | text | `release` \| `gate` \| `exception` |
| `rationale_structured` | jsonb | Structured checklist or key-value rationale |
| `rationale_text` | text | Optional free-text |
| `created_at` | timestamptz | |

### FR-5: ops.evidence_artifacts — Evidence Records

Each piece of evidence MUST be a structured record:

| Field | Type | Notes |
|-------|------|-------|
| `artifact_id` | UUID | |
| `release_id` | UUID | FK → ops.releases |
| `gate_id` | UUID | FK → ops.release_gates (optional) |
| `check_id` | UUID | FK → ops.gate_checks (optional) |
| `artifact_type` | text | `build_log` \| `test_result` \| `uat_summary` \| `approval_record` \| `rollback_plan` \| `health_check` \| `restore_drill` \| `incident_report` \| `reference` |
| `source_system` | text | CI/agent/manual/monitoring |
| `artifact_url` | text | Canonical URL or repo-relative path |
| `sha256` | text | Optional content hash for integrity |
| `created_at` | timestamptz | |
| `metadata` | jsonb | |

**Integrity Rule**: Orphan evidence records (unlinked to any release, deployment, check, or gate) are disallowed except for `artifact_type = 'reference'`.

### FR-6: ops.exceptions — Exception Records

Every gate bypass or policy deviation MUST be persisted:

| Field | Type | Notes |
|-------|------|-------|
| `exception_id` | UUID | |
| `release_id` | UUID | FK → ops.releases |
| `exception_type` | text | e.g., `gate_bypass`, `evidence_waiver`, `timing_override` |
| `impacted_gates` | text[] | Array of gate codes affected |
| `reason` | text | Rationale |
| `risk_statement` | text | Documented risk |
| `approver_id` | text | Auth UID |
| `effective_from` | timestamptz | |
| `expires_at` | timestamptz | MUST NOT be null |
| `compensating_controls` | jsonb | |
| `post_review_status` | text | `pending` \| `complete` \| `waived` |
| `created_at` | timestamptz | |

### FR-7: ops.deployments — Deployment Records

| Field | Type | Notes |
|-------|------|-------|
| `deployment_id` | UUID | |
| `release_id` | UUID | FK → ops.releases |
| `environment` | text | `staging` \| `production` |
| `deployed_at` | timestamptz | |
| `deployed_by` | text | Actor |
| `source_ref` | text | Git SHA deployed |
| `status` | text | `in_progress` \| `succeeded` \| `failed` \| `rolled_back` |
| `rollback_of` | UUID | FK → ops.deployments (if rollback) |
| `g4_status` | text | `pending` \| `passed` \| `failed` |
| `g4_resolved_at` | timestamptz | |

### FR-8: ops.environment_events — Operational Events

Append-only event log for environment lifecycle and operational signals:

| Field | Type | Notes |
|-------|------|-------|
| `event_id` | UUID | |
| `environment` | text | |
| `event_type` | text | `deploy_start` \| `deploy_complete` \| `rollback_trigger` \| `health_check` \| `alert_fired` \| `backup_complete` \| `restore_drill` etc. |
| `source_system` | text | |
| `payload` | jsonb | Event-specific data |
| `created_at` | timestamptz | |
| `idempotency_key` | text | Unique per event emission; retries must use same key |

**Integrity Rule**: `ops.environment_events` is APPEND-ONLY. No deletes or updates.

### FR-9: ops.event_ingest_log — Ingest Audit Trail

Every CI/agent event submission MUST be logged before processing:

| Field | Type | Notes |
|-------|------|-------|
| `ingest_id` | UUID | |
| `source_system` | text | |
| `event_type` | text | |
| `idempotency_key` | text | Caller-provided; unique per logical event |
| `schema_version` | text | e.g., `v1.0` |
| `payload_hash` | text | SHA256 of raw payload |
| `received_at` | timestamptz | |
| `processing_status` | text | `accepted` \| `duplicate` \| `rejected` \| `error` |
| `error_detail` | text | If rejected/error |

**Idempotency Contract**: If `idempotency_key` is already present with `processing_status = 'accepted'`, return 200 with the original result and set `processing_status = 'duplicate'` on the retry log row. Do NOT create a second accepted record.

### FR-10: ops.incidents and ops.recovery_drills

**ops.incidents** — Track production incidents linked to releases/deployments:
- `incident_id`, `deployment_id`, `severity`, `detected_at`, `resolved_at`, `timeline`, `root_cause`, `postmortem_status`

**ops.recovery_drills** — Track scheduled backup/restore drills:
- `drill_id`, `environment`, `drill_type`, `executed_by`, `executed_at`, `outcome`, `restore_validated`, `evidence_artifact_id`

---

## Event Ingestion Envelope

All CI and agent systems MUST use this envelope when posting events:

```json
{
  "schema_version": "v1.0",
  "idempotency_key": "<caller-generated unique key per logical event>",
  "event_type": "<event type string>",
  "source_system": "<github_actions | agent | manual | monitoring>",
  "release_id": "<UUID>",
  "gate_code": "<G1|G2|G3|G4> (optional)",
  "payload": { },
  "emitted_at": "<ISO8601 timestamp>"
}
```

**Rules**:
- `idempotency_key` format: `<source_system>/<release_id>/<event_type>/<sequence_or_hash>`
- Callers MUST reuse the same `idempotency_key` on retry
- `schema_version` MUST be included for all writes
- Payloads with unknown `schema_version` are rejected with HTTP 422

---

## RLS Access Boundaries (Conceptual)

| Role | Read | Write |
|------|------|-------|
| `ci_service_role` | ops.releases, ops.release_gates, ops.gate_checks | ops.event_ingest_log, ops.gate_checks, ops.environment_events |
| `release_manager` | All ops.* | ops.approvals, ops.exceptions, ops.release_gates (status update) |
| `qa_tester` | ops.releases, ops.gate_checks, ops.evidence_artifacts | ops.approvals (own), ops.evidence_artifacts (own) |
| `sre` | ops.deployments, ops.environment_events, ops.recovery_drills | ops.deployments (own), ops.recovery_drills (own) |
| `developer` | ops.releases, ops.gate_checks (own release) | ops.gate_checks (own) |
| `audit_reader` | All ops.* (read-only) | — |

---

## Success Criteria

This PRD is complete when:
- All 11 `ops.*` domains have implemented migrations in `supabase/migrations/`
- Event ingest Edge Function accepts and idempotency-deduplicates CI events
- At least one production release is traced end-to-end in `ops.*`
- RLS policies enforce role boundaries per the table above
- `ops.event_ingest_log` receives events from at least one CI workflow
