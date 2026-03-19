# Examples: PPO Design

## Example 1: MuJoCo Humanoid with SB3

**Problem**: Train a simulated humanoid to walk using PPO.

**Design**:
```python
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv, VecNormalize
from stable_baselines3.common.env_util import make_vec_env

# 8 parallel environments with normalization
env = make_vec_env("Humanoid-v4", n_envs=8)
env = VecNormalize(env, norm_obs=True, norm_reward=True, clip_obs=10.0)

model = PPO(
    "MlpPolicy",
    env,
    learning_rate=3e-4,
    n_steps=2048,
    batch_size=64,
    n_epochs=10,
    gamma=0.99,
    gae_lambda=0.95,
    clip_range=0.2,
    ent_coef=0.0,
    vf_coef=0.5,
    max_grad_norm=0.5,
    verbose=1,
    policy_kwargs=dict(net_arch=[256, 256]),
)

model.learn(total_timesteps=10_000_000)
```

**Result**: Mean return ~5000+ after 10M steps. Humanoid is one of the hardest MuJoCo benchmarks.

---

## Example 2: CartPole PPO (Minimal)

**Problem**: Solve CartPole as a sanity check for PPO setup.

**Design**:
```python
from stable_baselines3 import PPO

model = PPO("MlpPolicy", "CartPole-v1", verbose=1)
model.learn(total_timesteps=50_000)

# Should solve within 50K steps
mean_reward, _ = evaluate_policy(model, "CartPole-v1", n_eval_episodes=100)
assert mean_reward > 450, f"PPO failed on CartPole: {mean_reward}"
```

**Key insight**: If PPO cannot solve CartPole quickly, something is wrong with your setup. Use this as a smoke test.

**Result**: Solves (mean return 500) within ~25K steps.

---

## Example 3: PPO with CleanRL (Single File)

**Problem**: Implement PPO from scratch for research/understanding.

**Design**:
```
Environment: HalfCheetah-v4
Implementation: CleanRL ppo_continuous_action.py
Network:
  Actor: Input(17) -> Linear(64) -> Tanh -> Linear(64) -> Tanh -> Linear(6) [mean]
    + learnable log_std
  Critic: Input(17) -> Linear(64) -> Tanh -> Linear(64) -> Tanh -> Linear(1)
Rollout: n_steps=2048, n_envs=1
Update: batch_size=64, n_epochs=10, clip_range=0.2
GAE: gamma=0.99, lambda=0.95
Learning Rate: 3e-4 (linear decay to 0)
Training Budget: 1,000,000 timesteps
```

**Key insight**: CleanRL provides single-file PPO implementations that are easy to read, modify, and debug. Use SB3 for standard training, CleanRL for understanding or modifying the algorithm.

**Result**: Mean return ~3000+ after 1M steps on HalfCheetah.

---

## Example 4: PPO Hyperparameter Tuning

**Problem**: Tune PPO for a specific environment.

**Tuning order** (most impactful first):
1. **n_steps** and **n_envs** — data collection efficiency
2. **learning_rate** — too high = instability, too low = slow
3. **n_epochs** — too many = overfitting to rollout
4. **batch_size** — affects gradient noise
5. **clip_range** — rarely needs changing from 0.2
6. **gae_lambda** — rarely needs changing from 0.95

**SB3 Zoo configs**: Check RL Baselines3 Zoo for tuned hyperparameters for standard environments. These are excellent starting points.
