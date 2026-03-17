# Skill Trigger Tuning — Evals

## Eval Dimensions

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| Precision improvement | 30% | False positives reduced |
| Recall improvement | 30% | False negatives reduced |
| Description quality | 20% | Capability-focused, not implementation-focused |
| Test coverage | 20% | Both positive and negative samples tested |

## Test Cases

### TC-1: Overfiring skill
- Input: Skill that triggers on 40% of unrelated prompts
- Expected: Precision improves to >90%
- Fail if: Only recall addressed, precision ignored

### TC-2: Underfiring skill
- Input: Skill that misses 50% of relevant prompts
- Expected: Recall improves to >85%
- Fail if: Only precision addressed, recall ignored

## Pass threshold: Both precision and recall improve from baseline
