# Evals: RL Environment Selection

## Evaluation Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Environment runs | Required | 100 random steps complete without error |
| Space match | Required | Observation/action spaces match algorithm requirements |
| Reward signal | Required | Non-degenerate (not always zero, not exploding) |
| Standard env preference | High | Standard env used when one fits the problem |
| Wrapper justification | Medium | Each wrapper has stated purpose |
| Documentation complete | Medium | All fields in output format filled |

## Automated Checks

```python
# Minimum viability check
import gymnasium as gym

env = gym.make(env_id)
obs, info = env.reset(seed=42)
assert env.observation_space.contains(obs), "Observation out of space"

total_reward = 0
for _ in range(100):
    action = env.action_space.sample()
    obs, reward, terminated, truncated, info = env.step(action)
    total_reward += reward
    if terminated or truncated:
        obs, info = env.reset()

assert total_reward != 0 or env_has_sparse_reward, "Reward always zero — check reward function"
```

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Observation shape mismatch | Missing wrapper | Add appropriate preprocessing wrapper |
| Reward always zero | Sparse reward + random policy | Expected for sparse envs — document explicitly |
| Action out of bounds | Continuous action not clipped | Add ClipAction wrapper |
| Episode never terminates | Missing TimeLimit | Add TimeLimit wrapper |
| Slow training | Environment too complex for compute budget | Simplify or use lighter environment |

## Promotion Gate

Environment selection passes when:
1. All automated checks pass
2. At least one training run completes without environment errors
3. Documentation covers all required fields
4. Wrapper stack is justified and ordered correctly
