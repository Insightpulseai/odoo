# Evals: Actor-Critic Design

## Evaluation Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Agent learns | Required | Mean return improves over training |
| Outperforms REINFORCE | High | Lower variance and/or faster convergence |
| Critic learns | Required | Value loss decreases over training |
| Advantage estimation used | Required | Not raw returns |
| Architecture documented | High | Shared vs separate justified |
| Entropy maintained | Medium | Entropy does not collapse to zero |

## Automated Checks

```python
from stable_baselines3 import A2C
from stable_baselines3.common.evaluation import evaluate_policy

model = A2C("MlpPolicy", env, verbose=0)
model.learn(total_timesteps=total_steps)

mean_reward, std_reward = evaluate_policy(model, eval_env, n_eval_episodes=100)

# Check value function is not constant
obs_samples = [eval_env.observation_space.sample() for _ in range(100)]
values = [model.policy.predict_values(torch.FloatTensor(o).unsqueeze(0)).item()
          for o in obs_samples]
value_range = max(values) - min(values)
assert value_range > 0.1, "Critic outputs near-constant values"
```

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Critic not learning | Learning rate too low for critic | Increase vf_coef or use separate lr |
| Entropy collapses | ent_coef too low | Increase entropy coefficient |
| Training unstable | GAE lambda or n_steps wrong | Try lambda=1.0 or increase n_steps |
| Worse than REINFORCE | Architecture mismatch | Try separate networks, different lr |
| Value loss explodes | Returns not properly computed | Check gamma, normalize advantages |

## Promotion Gate

Actor-critic design passes when:
1. Mean eval return exceeds random baseline significantly
2. Value loss is decreasing or stable (not diverging)
3. Training variance is lower than pure REINFORCE (if compared)
4. Entropy stays above a minimum threshold throughout training
5. Architecture choice and hyperparameters are documented
