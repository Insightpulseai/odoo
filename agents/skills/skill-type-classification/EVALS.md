# Skill Type Classification — Evals

## Eval Dimensions

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| Classification accuracy | 40% | Correct type for the skill |
| Reasoning quality | 25% | Clear explanation of why |
| Eval strategy match | 20% | Correct strategy for the type |
| Durability assessment | 15% | Realistic durability estimate |

## Test Cases

### TC-1: Process encoding skill
- Input: "Skill that enforces commit message format"
- Expected: encoded_preference, fidelity validation, high durability
- Fail if: classified as capability_uplift

### TC-2: Knowledge enhancement skill
- Input: "Skill that provides current Azure pricing data"
- Expected: capability_uplift, regression testing, medium durability
- Fail if: classified as encoded_preference

### TC-3: Ambiguous skill
- Input: "Skill that writes Python docstrings"
- Expected: Reasoned classification with clear justification
- Fail if: No reasoning provided

## Pass threshold: 3/3 correct classifications
