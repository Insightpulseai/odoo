# Release Gates Hardening Plan

## Phase 1 — Contracts
- `release_gates.yaml` SSOT
- `production_eligibility.schema.json`
- Inventory of all subsystem contracts and evidence paths.

## Phase 2 — Workflow Normalization
- Create `.github/workflows/agent-factory-release-gates.yml`.
- Standardize the validation logic for all subsystems (Supervisor, Router, Eval, Deployments).

## Phase 3 — Environment & Promotion Rules
- Implement the "Preflight Validator" for production promotion.
- Add topology compatibility checks.

## Phase 4 — Evidence Validation
- Generate the `production-eligibility.json` rollup artifact.
- Automated terminology drift enforcement (reject "absolute exactly-once").

## Phase 5 — Acceptance
- Final operational runbook for releases.
- Machine-readable proof pack for the whole Agent Factory.
