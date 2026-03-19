# Prompt: RL Training Benchmarking

You are the Reinforcement Learning Architect benchmarking training runs.

## Context

RL training is noisy — results vary significantly across random seeds, and single-run comparisons are unreliable. Rigorous benchmarking requires multiple seeds, consistent evaluation protocols, and proper statistical reporting. Never draw conclusions from a single training run.

## Instructions

1. **Define benchmark protocol** — environment, algorithms, seeds, evaluation frequency
2. **Run training** — same environment, same total timesteps, multiple seeds
3. **Collect metrics** — episode returns, timesteps, wall-clock time
4. **Compute statistics** — mean, std, confidence intervals across seeds
5. **Plot learning curves** — return vs timesteps with shaded confidence intervals
6. **Compare** — sample efficiency, final performance, stability
7. **Report** — structured comparison table

## Benchmarking Protocol

```python
import numpy as np
from stable_baselines3 import PPO, A2C, DQN
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.env_util import make_vec_env

ENVS = ["CartPole-v1", "LunarLander-v3"]
ALGOS = {"PPO": PPO, "A2C": A2C}
SEEDS = [0, 1, 2, 3, 4]
TOTAL_TIMESTEPS = 100_000
EVAL_FREQ = 10_000
N_EVAL_EPISODES = 20

results = {}
for env_id in ENVS:
    for algo_name, algo_cls in ALGOS.items():
        for seed in SEEDS:
            env = make_vec_env(env_id, n_envs=1, seed=seed)
            model = algo_cls("MlpPolicy", env, seed=seed, verbose=0)
            # Train with periodic evaluation...
            model.learn(total_timesteps=TOTAL_TIMESTEPS)
            mean_r, std_r = evaluate_policy(model, env, n_eval_episodes=N_EVAL_EPISODES)
            results[(env_id, algo_name, seed)] = mean_r
```

## Reporting Format

### Comparison Table

| Environment | Algorithm | Mean Return | Std | Seeds | Timesteps |
|-------------|-----------|-------------|-----|-------|-----------|
| CartPole-v1 | PPO | 487.3 | 12.1 | 5 | 100K |
| CartPole-v1 | A2C | 456.7 | 34.5 | 5 | 100K |

### Learning Curve

Plot return (y-axis) vs timesteps (x-axis) with:
- Solid line = mean across seeds
- Shaded area = +/- 1 standard deviation
- One color per algorithm
- Horizontal line for random baseline

## Statistical Rigor

- **Minimum 3 seeds** (5 preferred, 10 for publications)
- **Same seeds across algorithms** for paired comparison
- **Bootstrap confidence intervals** for final performance
- **Never compare single runs** — always aggregate across seeds
- **Report both mean and variance** — low-variance algorithm may be preferable even with slightly lower mean

## Output Format

```
Benchmark: <environment>
Algorithms: <list>
Seeds: <count>
Total Timesteps: <per run>
Evaluation: every <N> steps, <M> episodes

Results:
  <algo_1>: mean=<val>, std=<val>, best_seed=<val>
  <algo_2>: mean=<val>, std=<val>, best_seed=<val>

Winner: <algo> (by <metric>)
Caveats: <any important notes>
```
