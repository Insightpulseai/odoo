# Evals: Robotics RL Design

## Evaluation Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Environment runs | Required | Agent can interact without physics errors |
| Task completed | Required | Agent achieves success criteria |
| Safety constraints respected | Required | No constraint violations in eval |
| Reward well-shaped | High | No reward hacking observed |
| Observation space justified | High | All components have clear purpose |
| Action space matches physics | High | Actions within physical bounds |

## Automated Checks

```python
# Physics stability check
env = RobotEnv()
for _ in range(10000):
    action = env.action_space.sample()
    obs, reward, terminated, truncated, info = env.step(action)
    assert not np.any(np.isnan(obs)), "NaN in observations — physics unstable"
    assert not np.any(np.isinf(obs)), "Inf in observations — physics unstable"
    assert np.all(np.abs(obs) < 1e6), "Observation explosion"
    if terminated or truncated:
        obs, info = env.reset()

# Safety constraint check during evaluation
violations = 0
for episode in range(100):
    obs, _ = eval_env.reset()
    done = False
    while not done:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = eval_env.step(action)
        if info.get("constraint_violation", False):
            violations += 1
        done = terminated or truncated

assert violations == 0, f"Safety violations in eval: {violations}"
```

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Physics explosion | Timestep too large or bad model | Reduce timestep, check URDF/MJCF |
| Reward hacking | Unintended reward shortcut | Redesign reward, add constraints |
| No grasping learned | Reward too sparse for manipulation | Add shaping (reach + grasp phases) |
| Sim-to-real gap | Insufficient domain randomization | Widen randomization ranges |
| Unsafe behavior | No safety penalty | Add explicit constraint violation penalty |
| Agent exploits physics | Unrealistic simulator behavior | Improve simulator fidelity |

## Promotion Gate

Robotics RL design passes when:
1. Agent achieves task success criteria in simulation
2. Zero safety constraint violations during 100 evaluation episodes
3. Reward function does not exhibit hacking behavior
4. Physics remains stable throughout long training runs
5. Domain randomization plan documented (if sim-to-real)
6. All observation and action components justified
