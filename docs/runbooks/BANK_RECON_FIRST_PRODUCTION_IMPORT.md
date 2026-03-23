# Bank Reconciliation Agent — First Production Import Runbook

## Objective
Execute the first live production statement import under a controlled window with fail-closed safeguards, evidence capture, and rollback readiness.

## Scope
This runbook applies only to the first controlled production statement import of one known-safe statement batch.

## Preconditions
All of the following must be true before import begins:
- Bank Reconciliation Agent status is **`conditional-approved`**.
- Latest staging rehearsal evidence is present and verified.
- Production release gates are passing.
- Runtime topology matches SSOT contracts (Replicas=1).
- Rollback path has been rehearsed and is ready.
- Operator is assigned and present for the whole run.
- Statement batch is pre-selected and known-safe.
- Evidence/log capture is enabled.

## Approved Batch Constraints
- Limited in size (e.g., < 20 lines).
- Limited to one account / one statement source.
- Free of known malformed format variants.
- Reviewed in advance for expected reconciliation characteristics.

## Execution Steps

### 1. Preflight
- Verify release gate pass status and production eligibility artifact.
- Verify health/readiness of the Odoo runtime and the Actions Agent.
- Confirm DB backup or rollback checkpoint availability.

### 2. Import
- Import only the approved statement batch.
- **DO NOT** widen matching heuristics during the run.
- **DO NOT** bypass any evidence or posting gates.
- Monitor logs live for any `exception` or `quarantined` states.

### 3. Review
- Confirm happy-path matches reconcile correctly in the General Ledger.
- Confirm ambiguous cases remain blocked/quarantined.
- Confirm no duplicate posting occurs.
- Verify the generation of the `agent_evidence_pack` for every posted line.

### 4. Closeout
- Capture outcome metrics and refresh acceptance/evidence artifacts.
- Record any anomalies or residual risks.
- Decide whether to continue soak observation or halt expansion.

## Stop Conditions
Abort immediately if:
- Illegal post path observed (posting from non-approved state).
- Duplicate posting observed.
- Ambiguous line auto-posts.
- Evidence pack missing for a posted line.
- Deployment topology deviates from SSOT (Replicas > 1).

## Evidence Required
- `production-import.log`
- `reconciliation-outcomes.json`
- `anomaly-report.md`
- `operator-review.md`
- `acceptance.json` (Validated against SSOT schema)
- Refreshed `production-eligibility.json`
