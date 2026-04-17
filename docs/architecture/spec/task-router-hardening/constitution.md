# Task Router Hardening Constitution

## Purpose
Define strict delivery semantics for the Agent Factory task router.

## Authority Model
- `spec/task-router-hardening/*` = specification truth
- `ssot/agents/task_router.yaml` = intended-state truth
- router code/tests = implementation truth
- evidence pack = operational proof

## Execution Invariants
- Every task has a deterministic `task_id`.
- Router may enqueue, claim, retry, dead-letter, or complete; no hidden states.
- Retries must be bounded and observable.
- Duplicate delivery must be detectable.
- Fail closed on malformed envelopes or missing required routing fields.

## Failure Contract
- Malformed input -> reject/quarantine.
- Exhausted retries -> dead-letter.
- Stale claim/lease -> reclaim only under documented rules.

## Drift Policy
- Reject undeclared queue states, undocumented retry paths, and hidden side effects.
