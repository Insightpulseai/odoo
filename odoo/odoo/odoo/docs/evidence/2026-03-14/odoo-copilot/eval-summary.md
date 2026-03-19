# Odoo Copilot — Eval Summary

> Date: 2026-03-14
> Build: N/A (no evaluations run yet)
> Status: **NOT EVALUATED**

## Current State

Foundry Evaluations dashboard shows **0 evaluations**.

No quality, safety, grounding, runtime, or action evaluations have been executed against the copilot agent.

## Consequence

The copilot is classified as **Internal Prototype Only**. It cannot be promoted to Advisory Release until:

1. Evaluation dataset populated with minimum 150 cases (see `evals/odoo-copilot/dataset.jsonl`)
2. Evaluation run executed against Foundry agent
3. Results recorded in `evals/odoo-copilot/results/<build-id>.json`
4. All thresholds in `evals/odoo-copilot/thresholds.yaml` passing
5. This summary updated with actual results

## Thresholds Required

| Metric | Threshold | Current |
|--------|-----------|---------|
| Relevance | >= 0.80 | N/A |
| Task adherence | >= 0.90 | N/A |
| Citation coverage | >= 0.90 | N/A |
| Citation accuracy | >= 0.95 | N/A |
| Refusal correctness | >= 0.95 | N/A |
| Hallucination rate | <= 0.05 | N/A |
| PII leakage | = 0 | N/A |
| Latency p95 | <= 8s | N/A |
| Error rate | <= 0.02 | N/A |

## Next Action

Populate `evals/odoo-copilot/dataset.jsonl` with real test cases and run the first evaluation against the Foundry agent.
