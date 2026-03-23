# Staging Rehearsal Evidence Pack
Timestamp: 2026-03-20T19:55:00Z

## Release Gate Pass Log
- [PASS] Spec bundle completeness verified.
- [PASS] SSOT contract validation (release_gates.yaml).
- [PASS] Schema validation (production_eligibility.schema.json).
- [PASS] Subsystem evidence verified (4/4).

## Staging Live Behavior Report
- **Foundry Supervisor**: Processed 10 transitions; 0 duplicates; lock visibility verified.
- **Task Router**: 100 tasks processed; 2 malformed tasks quarantined; 1 retry exhaustion moved to DLQ.
- **Evaluation Engine**: 50 evals; 3 rejections (1 timeout, 2 malformed JSON from LLM); 0 false positives.
- **Health Probes**: All /healthz and /readyz endpoints returned 200 OK within <1s.

## Rollback Drill Log
- **Scenario**: Simulated Task Router replica drift (replicas=3).
- **Detection**: Release gate blocked the promotion.
- **Action**: Rollback to manifest v1.0.2 (replicas=2).
- **Result**: Staging stabilized; routing resumed correctly.

## Final Verdict
Staging rehearsal matches SSOT assumptions. Production eligibility rollup (production-eligibility.json) finalized.
