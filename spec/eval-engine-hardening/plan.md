# Eval Engine Hardening Plan

## Phase 1 — Contracts
- `eval_engine.yaml` SSOT
- `eval_score_contract.schema.json`
- `eval_metrics_contract.yaml`

## Phase 2 — Implementation
- Harden `runner.ts` (Fail Closed bounds)
- Harden `llm.ts` judge (Schema conformity)
- Implement `metrics.ts`

## Phase 3 — Observability & Specs
- `EVAL_ENGINE_HARDENING.md`
- `EVAL_OPERATIONS.md`

## Phase 4 — CI Gates & Tests
- Ambiguity rejection proofs
- Schema validation tests
- Threshold math tests

## Phase 5 — Acceptance
- Evidence pack generation
