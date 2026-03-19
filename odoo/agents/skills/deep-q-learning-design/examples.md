# Examples: Deep Q-Learning Design

## Example 1: Atari Breakout with SB3

**Problem**: Train a DQN agent to play Atari Breakout from pixel observations.

**Design**:
```python
from stable_baselines3 import DQN
from stable_baselines3.common.atari_wrappers import AtariWrapper
from stable_baselines3.common.vec_env import VecFrameStack, DummyVecEnv
import gymnasium as gym

# Environment with standard Atari preprocessing
env = gym.make("ALE/Breakout-v5")
env = AtariWrapper(env)
env = DummyVecEnv([lambda: env])
env = VecFrameStack(env, n_stack=4)

model = DQN(
    "CnnPolicy",
    env,
    learning_rate=1e-4,
    buffer_size=100000,
    learning_starts=10000,
    batch_size=32,
    gamma=0.99,
    target_update_interval=1000,
    exploration_fraction=0.1,
    exploration_initial_eps=1.0,
    exploration_final_eps=0.01,
    train_freq=4,
    gradient_steps=1,
    verbose=1,
)

model.learn(total_timesteps=1_000_000)
```

**Result**: Mean return ~30-50 after 1M steps (varies by seed).

---

## Example 2: CartPole with Double DQN (CleanRL style)

**Problem**: Solve CartPole with a neural Q-network as a bridge from tabular to deep.

**Design**:
```
Environment: CartPole-v1
DQN Variant: Double DQN
Network: MLP — Input(4) -> Linear(120) -> ReLU -> Linear(84) -> ReLU -> Linear(2)
Replay Buffer: 10,000 transitions
Target Update: Hard copy every 500 steps
Epsilon: 1.0 -> 0.05 over 10,000 steps (linear)
Training Budget: 50,000 timesteps
Batch Size: 128
Learning Rate: 2.5e-4
```

**Key insight**: CartPole is solvable by tabular methods (after discretization) but serves as a good debugging environment for DQN — fast to train, easy to verify correctness.

**Result**: Solves (mean return 500) within 20,000 steps.

---

## Example 3: LunarLander with Dueling DQN

**Problem**: Land a spacecraft on a landing pad using discrete thrust actions.

**Design**:
```
Environment: LunarLander-v3
DQN Variant: Dueling DQN
Network:
  Shared: Input(8) -> Linear(64) -> ReLU -> Linear(64) -> ReLU
  Value stream: Linear(1)
  Advantage stream: Linear(4)
  Q = V + (A - mean(A))
Replay Buffer: 50,000
Target Update: Hard copy every 1000 steps
Epsilon: 1.0 -> 0.01 over 50,000 steps
Training Budget: 200,000 timesteps
```

**Key insight**: Dueling architecture helps when some states are inherently valuable regardless of action taken (e.g., being above the landing pad).

**Result**: Mean return ~200+ after 200K steps (solved threshold is 200).
