# Examples: Policy Gradient Design

## Example 1: CartPole REINFORCE with Baseline

**Problem**: Balance a pole on a cart using REINFORCE with mean-return baseline.

**Design**:
```python
import torch
import torch.nn as nn
from torch.distributions import Categorical
import gymnasium as gym
import numpy as np

class PolicyNetwork(nn.Module):
    def __init__(self, obs_dim, n_actions):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, n_actions),
        )

    def forward(self, x):
        return Categorical(logits=self.net(x))

env = gym.make("CartPole-v1")
policy = PolicyNetwork(4, 2)
optimizer = torch.optim.Adam(policy.parameters(), lr=0.001)
gamma = 0.99

for episode in range(3000):
    states, actions, rewards, log_probs = [], [], [], []
    state, _ = env.reset()
    done = False

    while not done:
        state_t = torch.FloatTensor(state)
        dist = policy(state_t)
        action = dist.sample()

        next_state, reward, terminated, truncated, _ = env.step(action.item())
        done = terminated or truncated

        states.append(state)
        actions.append(action)
        rewards.append(reward)
        log_probs.append(dist.log_prob(action))

        state = next_state

    # Compute discounted returns
    returns = []
    G = 0
    for r in reversed(rewards):
        G = r + gamma * G
        returns.insert(0, G)
    returns = torch.FloatTensor(returns)

    # Baseline: subtract mean
    returns = (returns - returns.mean()) / (returns.std() + 1e-8)

    # Policy gradient loss
    log_probs = torch.stack(log_probs)
    loss = -(log_probs * returns).mean()

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
```

**Result**: Solves CartPole (mean return 500) within ~1500 episodes.

---

## Example 2: Continuous Control with Gaussian Policy

**Problem**: Pendulum swing-up with continuous torque control.

**Design**:
```
Environment: Pendulum-v1
Action Space: Continuous Box(-2.0, 2.0)
Policy Network:
  Input(3) -> Linear(64) -> Tanh -> Linear(64) -> Tanh -> Linear(1) [mean]
  Separate learnable log_std parameter
Baseline: Mean return normalization
Learning Rate: 0.001
Discount Factor: 0.99
Episodes: 5000
```

**Key insight**: For continuous actions, the policy outputs the mean of a Gaussian. The log standard deviation is a learnable parameter (not state-dependent for simplicity). Actions are sampled from this Gaussian, and log probability is computed for the gradient.

**Result**: Mean return improves from ~-1500 (random) to ~-200 after 5000 episodes. REINFORCE is slow here — actor-critic methods converge faster.
