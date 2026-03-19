# Sequential Workflow Design — Prompt

You are designing a **sequential workflow** (prompt chaining pattern). The task has been confirmed to require ordered steps with dependencies.

## Design Process

1. **Decompose**: Break the task into the minimum number of sequential steps. Each step should do one thing well.

2. **Define interfaces**: For each step, specify:
   - Input: what it receives (from previous step or external)
   - Processing: what transformation it performs
   - Output: what it produces for the next step
   - Gate: validation criteria before proceeding

3. **Add quality gates**: Between each step, define what "good enough to proceed" means. Gates catch errors early and prevent cascading failures.

4. **Optimize**: Review the chain. Can any adjacent steps be merged without quality loss? Fewer steps = less latency and cost.

## Output Format

```
Step 1: [name]
  Input: [what]
  Process: [what transformation]
  Output: [what]
  Gate: [validation before step 2]

Step 2: [name]
  ...

Fallback: [what happens on gate failure]
Total steps: [N]
```

## Rules

- Prefer fewer steps over more
- Every step must have a testable output
- Gates are mandatory, not optional
- If you can't define clear step boundaries, this might not be a sequential task
