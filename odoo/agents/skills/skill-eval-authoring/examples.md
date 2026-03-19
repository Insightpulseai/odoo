# Skill Eval Authoring — Examples

## Example: Evals for agent-pattern-selection skill

### Eval Type: Single-turn (classification task)

### Grader: Code-based (pattern name match) + Model-based (justification quality)

### Test Cases

```
Test: simple_task_single_call
Prompt: "Summarize this 500-word document"
Expected pattern: single_call
Grading: Exact match on pattern name

Test: dependency_chain_sequential
Prompt: "Extract data from API, transform, validate, load into DB"
Expected pattern: sequential
Grading: Exact match + justification mentions "dependencies"

Negative test: ambiguous_without_context
Prompt: "Help me with my project"
Expected: Request clarification, do not select a pattern
Grading: No pattern selected
```

### Pass Criteria
- pass@1 >= 80% on pattern selection
- Justification quality >= 7/10 (model-graded)
