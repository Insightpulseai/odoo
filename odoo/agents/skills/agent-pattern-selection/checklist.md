# Agent Pattern Selection — Checklist

## Pre-Assessment
- [ ] Task description is clear and bounded
- [ ] Success criteria are defined
- [ ] Latency and cost constraints are known

## Pattern Hierarchy (work in order)
- [ ] **Single call**: Can one LLM call with retrieval/tools solve this?
- [ ] **Sequential**: Do subtasks form a fixed dependency chain?
- [ ] **Parallel**: Are subtasks independent and concurrent-safe?
- [ ] **Evaluator-optimizer**: Do measurable criteria exist for iteration?
- [ ] **Autonomous agent**: Is the problem truly open-ended?

## Decision Quality
- [ ] Simplest viable pattern selected (not the most impressive)
- [ ] Justification documents why simpler patterns were rejected
- [ ] Cost/latency tradeoff is acceptable for the chosen pattern
- [ ] If agent selected: guardrails defined (sandbox, limits, monitoring, human review)

## Evidence
- [ ] Pattern decision record created
- [ ] Alternatives documented with rejection reasons
