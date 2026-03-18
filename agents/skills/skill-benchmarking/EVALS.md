# Skill Benchmarking — Evals

## Eval Dimensions

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| Metric completeness | 25% | All metrics collected |
| Comparison validity | 25% | Clean context, no leakage |
| Lifecycle management | 25% | Correct graduation/refresh decisions |
| Report quality | 25% | Complete, evidence-backed |

## Test Cases

### TC-1: Improving skill
- Input: Skill with pass rate 60% → 75%
- Expected: Report improvement, recommend continuing capability evals
- Fail if: Recommends graduation at 75%

### TC-2: Saturated skill
- Input: Skill with pass rate 99% for 5 consecutive runs
- Expected: Recommend graduation to regression
- Fail if: Continues as capability eval

## Pass threshold: Correct lifecycle actions in all cases
