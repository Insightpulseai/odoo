# Evals: RL Training Benchmarking

## Evaluation Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Multiple seeds | Required | Minimum 3, prefer 5 |
| Fair comparison | Required | Same timesteps, eval protocol, seeds |
| Random baseline included | Required | Context for performance |
| Statistics reported | Required | Mean, std, confidence intervals |
| Learning curves plotted | High | Return vs timesteps with error bands |
| No single-run conclusions | Required | All claims based on aggregated results |

## Automated Checks

```python
def validate_benchmark(results: dict):
    """Validate benchmark meets minimum rigor standards."""
    for algo, runs in results.items():
        n_seeds = len(runs)
        assert n_seeds >= 3, f"{algo}: only {n_seeds} seeds (minimum 3)"

        returns = [r["final_return"] for r in runs]
        mean = np.mean(returns)
        std = np.std(returns)

        # Check for degenerate results
        assert std > 0, f"{algo}: zero variance — check if seeds are actually different"
        assert mean != 0 or "sparse_reward" in runs[0], f"{algo}: zero mean return"

    # Check random baseline exists
    assert "Random" in results, "Random baseline missing"
```

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Misleading winner | Too few seeds | Increase to 5+ seeds |
| Overlapping confidence intervals | Algorithms similar on this env | Acknowledge no significant difference |
| Single outlier skews mean | One seed dominates | Report median as well, inspect outlier |
| Unfair comparison | Different timestep budgets | Equalize total timesteps |
| Missing context | No random baseline | Always include random baseline |

## Promotion Gate

Benchmark passes when:
1. Minimum 3 seeds per configuration (5 preferred)
2. Random baseline included
3. Mean and standard deviation reported for all algorithms
4. Learning curves plotted with confidence intervals
5. No conclusions drawn from single runs
6. Statistical significance assessed for claimed performance differences
7. Compute cost documented
