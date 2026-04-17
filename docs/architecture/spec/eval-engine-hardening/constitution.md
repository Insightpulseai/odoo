# Eval Engine Hardening Constitution

## Purpose
Define strict, bounded evaluation semantics for the Agent Factory Evaluation Engine.

## Authority Model
- `spec/eval-engine-hardening/*` = specification truth
- `ssot/agents/eval_engine.yaml` = intended-state truth
- eval code/tests = implementation truth
- evidence pack = operational proof

## Execution Invariants
- Every evaluation yields a deterministic pass/fail or explicit quarantine.
- Ambiguous or malformed LLM judge outputs must fail closed.
- Evidence thresholds must be explicitly met, not probabilistically assumed.
- Metrics are immutably emitted upon completion.

## Failure Contract
- Ambiguous Judge Output -> Fail Closed (Quarantine).
- Missing Evidence -> Fail Closed.
- Provider Outage / Timeout -> Fail Closed (Retry context up to Supervisor).

## Drift Policy
- Reject undocumented scoring structures or hidden relaxed grading criteria.
