# Skill Eval Authoring — Prompt

You are writing evaluations for an agent skill. Evals are mandatory quality gates.

## Process

### 1. Choose Eval Type
- **Single-turn**: Simple input→output. Use for straightforward skills.
- **Multi-turn**: Tool calls, state changes. Use for interactive skills.
- **Agent evals**: Mistakes compound, creative solutions possible. Use for complex skills.

### 2. Choose Grader
- **Code-based**: String match, regex, static analysis. Fast, objective, brittle.
- **Model-based**: Rubric scoring, natural language assertions. Flexible, requires calibration.
- **Human**: Gold standard. Expensive, slow. Use for calibration.

### 3. Write Test Cases
For each test case:
```
Test: [name]
Prompt: [input to the skill]
Files: [any required context files]
Expected: [what good output looks like]
Grading: [how to score — code/model/human]
Partial credit: [if applicable]
```

### 4. Write Negative Cases
Cases where the skill should NOT produce output:
```
Negative test: [name]
Prompt: [input that should NOT trigger the skill]
Expected: No output or explicit rejection
```

### 5. Define Pass Criteria
- pass@k: probability of >=1 success in k trials (one good answer suffices)
- pass^k: all k trials succeed (reliability matters)

### Rules
- Grade outputs, not paths
- Implement partial credit for multi-component tasks
- Read transcripts regularly to verify grading fairness
- Refresh with harder challenges when pass rates saturate
