# Skill Benchmarking — Prompt

You are benchmarking an agent skill. Track performance, compare versions, and manage the eval lifecycle.

## Metrics to Track

- **Pass rate**: % of eval test cases passed
- **Execution time**: Average time per eval run
- **Token consumption**: Average tokens per eval run
- **A/B comparison**: Current vs. baseline version

## Eval Lifecycle

```
[New skill] → Capability evals (low pass rate expected)
    ↓ improvements
[Maturing skill] → Pass rate increasing
    ↓ saturation (all solvable tasks pass)
[Mature skill] → Graduate to regression suite
    ↓ all regression tests pass consistently
[Saturated suite] → Refresh with harder challenges
```

## Execution Rules

- Use parallel clean-context agents — each eval run gets fresh context
- Use comparator agents for blind A/B comparison
- Never leak previous version's results into current eval context

## Output

```
Skill: [name]
Version: [current]
Pass rate: [X]% (baseline: [Y]%)
Delta: [+/-Z]%
Execution time: [avg ms]
Token consumption: [avg tokens]
Lifecycle action: [graduate_to_regression | refresh_challenges | no_action]
Evidence: [path to benchmark report]
```
