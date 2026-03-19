# Evals: Q-Learning Baseline Design

## Evaluation Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Q-table converges | Required | Q-values stabilize within training budget |
| Greedy policy outperforms random | Required | Mean return > random policy baseline |
| Hyperparameters documented | Required | All values specified with rationale |
| Terminal states handled | Required | No future value added at terminal states |
| Epsilon decay appropriate | High | Agent explores enough early, exploits late |
| Learning curve plotted | Medium | Episode returns show upward trend |

## Automated Checks

```python
# Convergence check
def check_convergence(returns, window=100, threshold=0.01):
    if len(returns) < 2 * window:
        return False
    recent = np.mean(returns[-window:])
    earlier = np.mean(returns[-2*window:-window])
    return abs(recent - earlier) / (abs(earlier) + 1e-8) < threshold

# Performance check
def check_performance(q_table, env, n_eval=100):
    returns = []
    for _ in range(n_eval):
        state, _ = env.reset()
        total = 0
        done = False
        while not done:
            action = np.argmax(q_table[state])
            state, reward, terminated, truncated, _ = env.step(action)
            total += reward
            done = terminated or truncated
        returns.append(total)
    return np.mean(returns), np.std(returns)
```

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Q-values diverge | Learning rate too high | Reduce lr or add lr decay |
| No learning | Epsilon too low too fast | Slow epsilon decay |
| Oscillating returns | No convergence | Increase episodes, tune lr/gamma |
| Always zero Q-values | Sparse reward + insufficient exploration | More episodes, optimistic initialization |

## Promotion Gate

Q-learning baseline passes when:
1. Greedy policy mean return > random policy by statistically significant margin
2. Q-values have stabilized (convergence check passes)
3. Learning curve shows clear improvement trend
4. Hyperparameters are documented with rationale
