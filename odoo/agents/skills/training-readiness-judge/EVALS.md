# Training Readiness Judge — Evals

## Eval Dimensions

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| Gate coverage | 25% | All four gates (data, eval, training, reproducibility) assessed |
| Decision correctness | 25% | Right decision for the evidence presented |
| Gap identification | 25% | Specific, actionable gaps listed when rejecting |
| Strictness | 25% | Does not promote with insufficient evidence |

## Test Cases

### TC-1: Complete submission
- Input: Checkpoint with full data card, all benchmarks, converged loss, full config
- Expected: PROMOTE with justification citing all four gates passing
- Fail if: Rejects a complete submission or promotes without checking all gates

### TC-2: Missing data card
- Input: Good training health, good eval, but no data card
- Expected: REJECT with specific gap: "Create data card with provenance"
- Fail if: Promotes despite missing data card

### TC-3: Loss divergence
- Input: All documentation present but loss spiked 3x during training
- Expected: REJECT citing training health failure
- Fail if: Promotes despite loss divergence

### TC-4: Partial eval coverage
- Input: Task-specific eval present but no general benchmarks
- Expected: NEEDS_MORE_EVAL with specific missing benchmarks listed
- Fail if: Promotes without general benchmark coverage

### TC-5: No seed documented
- Input: Everything else passes but seed not documented
- Expected: REJECT on reproducibility gate
- Fail if: Promotes without reproducibility

## Pass threshold: Correct decision for evidence, all four gates assessed, specific gaps listed
