# Agent Pattern Selection — Evals

## Eval Dimensions

| Dimension | Weight | Criteria |
|-----------|--------|----------|
| Simplicity adherence | 30% | Selected simplest viable pattern |
| Hierarchy compliance | 25% | Assessed patterns in correct order |
| Justification quality | 20% | Clear reasoning for selection and rejection of alternatives |
| Guardrail completeness | 15% | Appropriate safety measures for chosen pattern |
| Evidence quality | 10% | Decision record is complete and actionable |

## Test Cases

### TC-1: Simple task → single call
- Input: "Summarize this 500-word document"
- Expected: Single call
- Fail if: Any workflow or agent recommended

### TC-2: Dependency chain → sequential
- Input: "Extract data from API, transform, validate, load into DB"
- Expected: Sequential workflow
- Fail if: Parallel or agent recommended

### TC-3: Independent subtasks → parallel
- Input: "Check security posture of 5 independent Azure resources"
- Expected: Parallel workflow
- Fail if: Sequential or agent recommended

### TC-4: Iterative quality → evaluator-optimizer
- Input: "Write marketing copy that must score >8/10 on brand voice rubric"
- Expected: Evaluator-optimizer
- Fail if: Single call or agent recommended

### TC-5: Open-ended → agent
- Input: "Debug a production incident with unknown root cause"
- Expected: Autonomous agent with guardrails
- Fail if: Any fixed workflow recommended

## Grading

- Code-based: pattern name match
- Model-based: justification quality rubric
- Pass threshold: 4/5 correct patterns, all justifications rated ≥7/10
