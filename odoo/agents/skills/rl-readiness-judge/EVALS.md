# Evals: RL Readiness Judge

## Evaluation Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Verdict issued | Required | Clear promote/block/conditional |
| Evidence provided | Required | All dimensions assessed with metrics |
| Blockers actionable | Required | Each blocker has clear fix |
| Conditions measurable | Required | Each condition has pass/fail criteria |
| Proportional rigor | High | Staging < production requirements |
| Conservative default | High | When in doubt, block |

## Automated Checks

```python
def readiness_check(model, env, tier="staging"):
    results = {}

    # 1. Convergence
    training_returns = load_training_returns()
    results["convergence"] = check_convergence(training_returns)

    # 2. Performance
    eval_returns = evaluate(model, env, n_episodes=100)
    results["performance"] = {
        "mean": np.mean(eval_returns),
        "std": np.std(eval_returns),
        "passes_threshold": np.mean(eval_returns) > THRESHOLD
    }

    # 3. Safety
    violations = count_violations(model, env, n_episodes=100)
    results["safety"] = {"violations": violations, "passes": violations == 0}

    # 4. Reproducibility (requires multiple trained models)
    seed_means = [np.mean(evaluate(m, env, 20)) for m in seed_models]
    results["reproducibility"] = {
        "n_seeds": len(seed_models),
        "mean_of_means": np.mean(seed_means),
        "std_of_means": np.std(seed_means),
        "passes": len(seed_models) >= (3 if tier == "staging" else 5)
    }

    # Verdict
    all_pass = all(r.get("passes", True) for r in results.values() if isinstance(r, dict))
    return "PROMOTE" if all_pass else "BLOCK", results
```

## Failure Modes (of the Judge)

| Failure | Cause | Fix |
|---------|-------|-----|
| False promote | Insufficient eval episodes | Increase to 100+ episodes |
| False block | Threshold too strict | Calibrate thresholds per environment |
| Missing edge cases | Only tested happy path | Add adversarial and boundary tests |
| Ignoring variance | Only looked at mean | Always check std and worst-case |
| Inconsistent standards | Different rigor per eval | Use explicit tier-based requirements |

## Meta-Evaluation

The judge itself should be evaluated on:
1. **Consistency** — same evidence produces same verdict
2. **Calibration** — promoted agents succeed, blocked agents had real issues
3. **Completeness** — all dimensions assessed, no shortcuts
4. **Actionability** — blockers and conditions are concrete and fixable

## Promotion Gate

The readiness judge passes meta-evaluation when:
1. Every verdict includes evidence for all required dimensions
2. Every blocker has an actionable fix
3. Every condition has a measurable pass/fail criterion
4. No agent is promoted with any required dimension failing
5. Tier-appropriate rigor is consistently applied
