# Plan — Implement Goal-Based Parity for Odoo 19 EE Surfaces

## Phase A — Catalog + Goals (SSOT)

1. Create `docs/parity/EE_SURFACE_CATALOG.yaml` (surfaces, tiers, acceptance tests).
2. Create `config/parity/PARITY_GOALS.yaml` (scoring weights, thresholds, gating rules).

## Phase B — Parity Check Engine

1. Implement `scripts/parity/parity_check.py`
   - Reads catalog + goals
   - Runs checks (scriptable probes)
   - Outputs JSON report + Markdown summary
2. Ensure deterministic exit codes for CI gating.

## Phase C — Evidence & CI Integration

1. Store run artifacts under `docs/evidence/<timestamp>/parity/`
2. Wire into existing CI workflow (or add new) to:
   - Run parity_check.py
   - Fail PRs if Tier-0 fails or score < threshold

## Phase D — Extend Surfaces (optional)

Add Tier-2 surfaces (Studio-like workflow, etc.) only after Tier-0 is stable.
