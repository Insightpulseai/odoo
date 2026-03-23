# Release Gates Hardening PRD

## Problem
Subsystem hardening guarantees are only as strong as the workflow that enforces them. Manual or ad-hoc releases risk drifting from documented assumptions and invalidating production readiness.

## Goal
Convert all Agent Factory contracts into enforced, automated release barriers that block production deployment on any contract violation or missing evidence.

## Non-Goals
- Replacing application-level fail-closed logic.
- Automating 100% of the release decision (human sign-off still required on the transition from `ready_for_acceptance_review` to `accepted`).

## Functional Requirements
- Automated validation of all Spec bundles and SSOT contracts.
- Automated verification of `acceptance.json` artifacts for all subsystems.
- Rollup `production-eligibility.json` artifact generation.
- GitHub Actions workflow that blocks on any validation failure.
- Enforcement of `runtime_production_status` and topology compatibility.

## Acceptance Criteria
- Every subsystem has a verified `acceptance.json`.
- Production release is blocked if any subsystem evidence is missing or stale.
- Topology mismatch (e.g., multi-replica for single-writer) triggers a hard fail in CI.
- No subsystem claims unconditional production readiness.

## Risks
- CI flakiness blocking legitimate releases.
- Stale evidence artifacts if the rollup logic is not robust.
- "Hidden" environment variables or infra drift not captured by manifests.
