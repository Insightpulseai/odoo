# Evals: Policy Gradient Design

## Evaluation Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Agent learns | Required | Mean return improves over training |
| Outperforms random | Required | Final mean return > random baseline |
| Complete episodes used | Required | Returns computed from full episodes |
| Baseline applied | High | Variance reduction mechanism in place |
| Policy output correct | High | Categorical for discrete, Gaussian for continuous |
| Gradient direction correct | Required | Maximizing expected return (not minimizing) |

## Automated Checks

```python
# Verify policy improves
early_returns = training_returns[:100]
late_returns = training_returns[-100:]
assert np.mean(late_returns) > np.mean(early_returns), "No learning detected"

# Verify baseline reduces variance
with_baseline_var = np.var(late_returns)
# Compare to a run without baseline if available

# Verify action distribution
obs = torch.FloatTensor(env.observation_space.sample())
dist = policy(obs)
action = dist.sample()
assert env.action_space.contains(action.numpy()), "Action out of bounds"
```

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Extremely high variance | No baseline | Add mean-return baseline or learned value |
| Policy collapses to single action | Entropy too low | Add entropy bonus to loss |
| No learning | Learning rate too high or low | Tune lr; try 1e-3 as starting point |
| NaN in loss | Log prob of impossible action | Clamp log probs, check action bounds |
| Very slow convergence | REINFORCE sample inefficiency | Switch to actor-critic (A2C, PPO) |

## Promotion Gate

Policy gradient design passes when:
1. Mean return over final 100 episodes exceeds random baseline
2. Learning curve shows upward trend (even if noisy)
3. Baseline is applied and justified
4. Policy output type matches action space
5. Gradient computation is correct (ascent on returns)
