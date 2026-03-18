# Examples: Actor-Critic Design

## Example 1: LunarLander A2C with SB3

**Problem**: Land a spacecraft using discrete thrust actions with A2C.

**Design**:
```python
from stable_baselines3 import A2C
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.evaluation import evaluate_policy

# 4 parallel environments
env = make_vec_env("LunarLander-v3", n_envs=4)

model = A2C(
    "MlpPolicy",
    env,
    learning_rate=7e-4,
    n_steps=5,
    gamma=0.99,
    gae_lambda=0.95,
    ent_coef=0.01,
    vf_coef=0.5,
    max_grad_norm=0.5,
    verbose=1,
)

model.learn(total_timesteps=500_000)

# Evaluate
eval_env = make_vec_env("LunarLander-v3", n_envs=1)
mean_reward, std_reward = evaluate_policy(model, eval_env, n_eval_episodes=100)
print(f"Mean reward: {mean_reward:.2f} +/- {std_reward:.2f}")
```

**Result**: Mean return ~200+ after 500K steps. Lower variance than REINFORCE.

---

## Example 2: CartPole A2C with Shared Backbone

**Problem**: Solve CartPole with a minimal A2C implementation.

**Design**:
```
Environment: CartPole-v1
Architecture: Shared backbone
  Shared: Input(4) -> Linear(64) -> ReLU -> Linear(64) -> ReLU
  Actor: Linear(2) [logits for left/right]
  Critic: Linear(1) [state value]
Advantage: GAE with lambda=0.95
Parallel Envs: 4
Learning Rate: 7e-4
N-steps: 5
Training Budget: 100,000 timesteps
```

**Key insight**: A2C with 4 parallel environments collects diverse experience simultaneously. The shared backbone is efficient for simple problems. GAE with lambda=0.95 provides a good bias-variance tradeoff.

**Result**: Solves CartPole (mean return 500) within ~50K steps — faster and more stable than REINFORCE.

---

## Example 3: Continuous Control A2C

**Problem**: BipedalWalker locomotion with continuous actions.

**Design**:
```
Environment: BipedalWalker-v3
Architecture: Separate networks (more stable for continuous control)
  Actor: Input(24) -> Linear(256) -> ReLU -> Linear(256) -> ReLU -> Linear(4) [mean]
    + learnable log_std
  Critic: Input(24) -> Linear(256) -> ReLU -> Linear(256) -> ReLU -> Linear(1)
Advantage: GAE with lambda=0.95
Parallel Envs: 8
Learning Rate: 3e-4
N-steps: 128
Training Budget: 2,000,000 timesteps
```

**Key insight**: Continuous control benefits from separate networks and longer n-steps. BipedalWalker is challenging — A2C can solve it but PPO typically converges faster and more reliably.

**Result**: Mean return ~250+ after 2M steps. Consider PPO if A2C struggles.
