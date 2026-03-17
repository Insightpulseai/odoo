# Evaluator-Optimizer Design — Evals

## Eval Dimensions

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| Prerequisite validation | 25% | Confirms fit before designing |
| Criteria measurability | 25% | Rubric is objective and scoreable |
| Stopping criteria | 25% | Both threshold and max iterations defined |
| Feedback quality | 15% | Evaluator feedback is actionable |
| Efficiency | 10% | Iteration count is practical |

## Test Cases

### TC-1: Good fit
- Input: "Improve code review comments to match team style guide (scored 1-10)"
- Expected: Valid evaluator-optimizer design with rubric
- Fail if: Missing stopping criteria

### TC-2: Bad fit — deterministic tool available
- Input: "Fix Python formatting"
- Expected: Reject pattern, recommend Black formatter
- Fail if: Evaluator-optimizer designed for a deterministic task

### TC-3: Bad fit — subjective criteria
- Input: "Make this essay more beautiful"
- Expected: Flag subjective criteria, require operationalization
- Fail if: Accepted without measurable rubric

## Pass threshold: 3/3 correct assessments
