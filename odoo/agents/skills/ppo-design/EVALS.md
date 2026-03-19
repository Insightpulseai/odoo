# Evals: PPO Design

## Evaluation Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Agent learns | Required | Mean return improves over training |
| Clipped objective used | Required | PPO clip mechanism in place |
| GAE used | Required | Advantage estimation via GAE |
| Diagnostics healthy | High | KL, clip fraction, explained variance in range |
| Outperforms A2C | Medium | Same or better performance than A2C baseline |
| Hyperparameters documented | High | All values specified with rationale |

## Automated Checks

```python
from stable_baselines3 import PPO
from stable_baselines3.common.evaluation import evaluate_policy

model = PPO("MlpPolicy", env, verbose=0)
model.learn(total_timesteps=total_steps)

mean_reward, std_reward = evaluate_policy(model, eval_env, n_eval_episodes=100)

# Sanity: CartPole should solve easily
if env_id == "CartPole-v1":
    assert mean_reward > 450, f"PPO failed CartPole sanity check: {mean_reward}"
```

## Diagnostic Checks

```python
# After training, inspect logger
# Healthy PPO diagnostics:
# - approx_kl: 0.01-0.05 (not > 0.1)
# - clip_fraction: 0.1-0.3 (not 0 or > 0.5)
# - explained_variance: > 0.5 (not negative)
# - entropy_loss: not collapsed to 0
# - policy_gradient_loss: decreasing or stable
# - value_loss: decreasing or stable
```

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| KL divergence too high | Updates too large | Reduce lr or clip_range |
| Clip fraction = 0 | Clip range too wide or no learning | Reduce clip_range, check lr |
| Explained variance negative | Critic is worse than mean predictor | Increase vf_coef, train longer |
| Performance plateau | Overfitting to rollout data | Reduce n_epochs, increase n_steps |
| Training unstable | lr too high, no normalization | Reduce lr, add VecNormalize |
| Entropy collapse | ent_coef too low | Increase ent_coef |

## Promotion Gate

PPO design passes when:
1. Mean eval return exceeds baseline by significant margin
2. KL divergence stays below 0.05 throughout training
3. Clip fraction is in 0.1-0.3 range
4. Explained variance is positive and increasing
5. Learning curve shows consistent improvement
6. All hyperparameters documented with rationale
