# Sequential Workflow Design — Evals

## Eval Dimensions

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| Step minimality | 25% | No unnecessary steps |
| Interface clarity | 25% | Input/output contracts are unambiguous |
| Gate quality | 25% | Gates are testable and catch real errors |
| Fallback design | 15% | Failure behavior is defined and practical |
| Latency awareness | 10% | Total chain latency is considered |

## Test Cases

### TC-1: ETL pipeline
- Input: "Load data from API, clean it, store in DB"
- Expected: 3 steps (extract, transform, load) with gates
- Fail if: >5 steps or missing gates

### TC-2: Report generation
- Input: "Query data, compute metrics, format as PDF"
- Expected: 3 steps with validation between compute and format
- Fail if: Compute and format merged without validation

## Pass threshold: All test cases produce valid step chains with gates
