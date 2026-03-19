# Constitution — Odoo Release Gates Control Plane (Supabase SSOT)

## Purpose
Define the canonical Supabase-based control plane for Odoo release governance, gate enforcement telemetry, approvals, evidence artifacts, exceptions, and post-deploy operational confirmation.

This constitution translates the persona/gate operating model into a durable, auditable, automation-first system of record.

---

## Scope

### In Scope
- Canonical control-plane domains under `ops.*`
- Release/gate/evidence/approval/exception data contracts
- CI/agent event ingestion contract (provider-agnostic)
- Auditability, traceability, and evidence retention policy requirements
- RLS design principles and role boundaries (conceptual)
- Idempotency and integrity requirements for event writes

### Out of Scope
- Exact SQL migrations (implementation spec)
- CI provider workflow YAML
- UI dashboards / admin panels
- Odoo module implementation details
- Vendor-specific secrets management setup

---

## Foundational Principles

### 1. Supabase as Control-Plane SSOT
Release governance state MUST be persisted in Supabase (`ops.*`) and be queryable independent of CI vendor logs.

### 2. Event-Sourced Observability with Current-State Read Models
Write immutable operational events where possible, while maintaining normalized current-state tables for fast querying/reporting.

### 3. Gate Integrity over Convenience
Production promotion decisions MUST be based on explicit gate outcomes and evidence completeness, not inferred from ad hoc chat/manual notes.

### 4. Idempotent Ingestion
CI and agents may retry. Event ingestion MUST support idempotency keys and duplicate-safe writes.

### 5. Evidence First-Class Citizenship
Build/test/QA/release/ops evidence MUST be represented as structured records, not only unstructured text.

### 6. Exception Discipline
Bypass/override actions MUST be time-bounded, attributable, risk-documented, and reviewable.

### 7. Vendor-Agnostic Contracts
The control-plane contract must be stable across GitHub Actions, other CI systems, human operators, and agents.

---

## Canonical Domains (`ops.*`)

Minimum conceptual domains:
- `ops.releases`
- `ops.release_gates`
- `ops.gate_checks`
- `ops.approvals`
- `ops.evidence_artifacts`
- `ops.exceptions`
- `ops.environment_events`
- `ops.deployments`
- `ops.incidents`
- `ops.recovery_drills`
- `ops.event_ingest_log` (or equivalent immutable event sink)

---

## Normative Requirements

### NR-1 Release Identity
Each release record MUST have a stable release identifier and link to:
- repo/project identity
- environment target
- source revision(s)
- release scope metadata
- initiating actor/system

### NR-2 Gate Model Parity
The control plane MUST encode gates `G1`–`G4` as canonical values matching the persona/gate SSOT:
- G1 Build Integrity
- G2 Validation Readiness
- G3 Promotion Readiness
- G4 Post-Deploy Operational Confirmation

### NR-3 Evidence Linkage
Evidence artifacts MUST be linkable to:
- release
- gate (optional if release-wide)
- check/approval/exception (optional)
- environment
- source system (CI/agent/manual/monitoring)

### NR-4 Approval Traceability
Approvals MUST record:
- approver identity
- approval role/persona
- decision (approve/reject/request_changes)
- timestamp
- scope (release/gate/exception)
- rationale (structured + optional free text)

### NR-5 Exception Governance
Exceptions MUST record:
- exception type
- reason/risk statement
- approver
- effective window / expiry
- impacted gate(s)
- compensating controls
- post-event review status

### NR-6 Deployment Correlation
Deployments MUST be correlated to releases and environments and support post-deploy health evidence linkage.

### NR-7 Auditability
All governance-significant writes MUST preserve created_at/created_by and change provenance.

---

## Data Integrity Rules (Conceptual)

1. A `G3` success for production MUST NOT be recorded as final unless required approvals/evidence are present OR an active approved exception exists.
2. `G4` may be pending immediately after deployment but must transition to terminal state per policy/SLA.
3. Expired exceptions MUST NOT authorize new promotions.
4. Orphan evidence records (unlinked to any release/deployment/check) are disallowed except explicitly typed "reference" artifacts.
5. Duplicate event ingestion attempts must not create duplicate terminal outcomes for the same idempotency key.

---

## Security & Access Principles (Conceptual RLS Guidance)

### Write Paths
- CI/agent service roles write via authenticated server-side paths only
- Human approvals write via scoped authenticated roles
- No anonymous writes to governance tables

### Read Paths
- Operational roles can read relevant `ops.*` records
- Sensitive fields (e.g., internal URLs/secrets-adjacent metadata) should be masked/restricted
- Audit reviewers may require broader read-only access

### Separation of Duties
Approvals and exceptions should support policy-enforced role separation where required.

---

## Success Criteria
This constitution is successful when:
- every production promotion is queryable with gates, approvals, and evidence
- exceptions are explicit, time-bounded, and audited
- CI/agent retries do not corrupt release state
- postmortems and audits can reconstruct release decisions from SSOT
