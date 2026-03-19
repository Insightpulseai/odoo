# Evals: Deep Q-Learning Design

## Evaluation Criteria

| Criterion | Weight | Pass Condition |
|-----------|--------|----------------|
| Agent learns | Required | Mean eval return improves over training |
| Outperforms random | Required | Eval return > random policy by significant margin |
| Replay buffer used | Required | Training uses experience replay |
| Target network used | Required | Separate target network with periodic updates |
| Network architecture appropriate | High | CNN for images, MLP for vectors |
| Hyperparameters documented | High | All values specified |
| DQN variant justified | Medium | Reason given for vanilla/double/dueling choice |

## Automated Checks

```python
from stable_baselines3 import DQN
from stable_baselines3.common.evaluation import evaluate_policy

# Train
model = DQN("MlpPolicy", env, verbose=0)
model.learn(total_timesteps=total_steps)

# Evaluate
mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=100)

# Random baseline
random_rewards = []
for _ in range(100):
    obs, _ = env.reset()
    total = 0
    done = False
    while not done:
        obs, r, term, trunc, _ = env.step(env.action_space.sample())
        total += r
        done = term or trunc
    random_rewards.append(total)

random_mean = np.mean(random_rewards)

assert mean_reward > random_mean, f"DQN ({mean_reward}) did not beat random ({random_mean})"
```

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Loss diverges | Learning rate too high | Reduce lr, add gradient clipping |
| No learning after many steps | Buffer too small or learning_starts too high | Increase buffer, reduce learning_starts |
| Overestimation | Vanilla DQN bias | Switch to Double DQN |
| Catastrophic forgetting | Target network updated too frequently | Increase target_update_interval |
| Poor visual performance | Wrong CNN architecture | Match standard Atari CNN from Nature paper |

## Promotion Gate

DQN design passes when:
1. Mean eval return exceeds random baseline by 2+ standard deviations
2. Learning curve shows consistent improvement
3. No loss divergence during training
4. Architecture and hyperparameters are fully documented
5. DQN variant choice is justified
