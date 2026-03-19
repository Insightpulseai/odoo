# Examples: Q-Learning Baseline Design

## Example 1: FrozenLake Q-Learning

**Problem**: Navigate a 4x4 frozen lake grid to reach the goal without falling in holes.

**Design**:
```python
import gymnasium as gym
import numpy as np

env = gym.make("FrozenLake-v1", map_name="4x4", is_slippery=True)

# Q-table: 16 states x 4 actions
q_table = np.zeros((16, 4))

# Hyperparameters
lr = 0.7
gamma = 0.95
epsilon = 1.0
epsilon_end = 0.05
epsilon_decay = 0.0005
n_episodes = 10000

for episode in range(n_episodes):
    state, _ = env.reset()
    done = False

    while not done:
        # Epsilon-greedy
        if np.random.random() < epsilon:
            action = env.action_space.sample()
        else:
            action = np.argmax(q_table[state])

        next_state, reward, terminated, truncated, _ = env.step(action)
        done = terminated or truncated

        # Q-update (no future value if terminal)
        if terminated:
            q_table[state, action] += lr * (reward - q_table[state, action])
        else:
            q_table[state, action] += lr * (
                reward + gamma * np.max(q_table[next_state]) - q_table[state, action]
            )

        state = next_state

    epsilon = max(epsilon_end, epsilon * (1 - epsilon_decay))
```

**Result**: ~70% success rate after 10,000 episodes (slippery variant adds stochasticity).

---

## Example 2: Taxi-v3 Q-Learning

**Problem**: Pick up and drop off a passenger at the correct location.

**Design**:
```
Environment: Taxi-v3
State Space: Discrete(500) — 5x5 grid x 5 passenger locations x 4 destinations
Action Space: Discrete(6) — south, north, east, west, pickup, dropoff
Q-Table Shape: (500, 6)
Hyperparameters:
  learning_rate: 0.7
  discount_factor: 0.95
  epsilon: 1.0 -> 0.01 (decay: 0.001)
  episodes: 5000
```

**Key insight**: Taxi has a larger state space (500) but still tractable for Q-tables. The reward structure is dense (small negative per step, large negative for wrong pickup/dropoff, large positive for correct dropoff), which aids learning.

**Result**: Mean return ~8.0 after 5,000 episodes (optimal is ~8-10).
