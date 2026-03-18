# Skill Eval Authoring — Evals (Meta-Eval)

## Eval Dimensions

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| Test case coverage | 25% | Positive and negative cases present |
| Grading quality | 25% | Method matches skill complexity |
| Output-focused grading | 20% | Grades outputs not paths |
| Partial credit | 15% | Multi-component scoring defined |
| Pass criteria | 15% | Threshold is defined and reasonable |

## Test Cases

### TC-1: Simple skill
- Input: "Write evals for a classification skill"
- Expected: Code-based grader, >=3 test cases, pass@1 threshold
- Fail if: Model-based grader for objective task

### TC-2: Complex skill
- Input: "Write evals for an autonomous debugging agent"
- Expected: Agent eval type, model-based grader, partial credit, pass@3 threshold
- Fail if: Single-turn eval type for multi-step agent

## Pass threshold: All eval designs match skill complexity
