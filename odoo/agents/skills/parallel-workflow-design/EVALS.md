# Parallel Workflow Design — Evals

## Eval Dimensions

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| Independence verification | 30% | No hidden dependencies in design |
| Aggregation clarity | 25% | Strategy defined before implementation |
| Failure handling | 20% | Policy is explicit and practical |
| Contract quality | 15% | Branch I/O contracts are clear |
| Concurrency awareness | 10% | Limits are set |

## Test Cases

### TC-1: True parallel task
- Input: "Check 5 Azure resources for compliance"
- Expected: 5 parallel branches, merge aggregation
- Fail if: Sequential design or missing aggregation

### TC-2: Hidden dependency
- Input: "Build module A and module B (B depends on A)"
- Expected: Flag dependency, recommend sequential or hybrid
- Fail if: Pure parallel recommended despite dependency

## Pass threshold: Correct independence assessment in all cases
