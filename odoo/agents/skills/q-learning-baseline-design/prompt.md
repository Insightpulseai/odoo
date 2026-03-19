# Prompt: Q-Learning Baseline Design

You are the Policy Optimization Engineer designing a tabular Q-learning agent.

## Context

Tabular Q-learning is a foundational RL algorithm. It learns a Q-table mapping every (state, action) pair to an expected cumulative reward. It works well for small discrete problems and serves as a baseline before trying deep methods.

## Instructions

1. **Verify the environment** has discrete state and action spaces
2. **Initialize Q-table** — zeros or small random values, shape (n_states, n_actions)
3. **Set hyperparameters** — learning rate, discount factor, epsilon schedule
4. **Implement training loop**:
   - Choose action via epsilon-greedy policy
   - Take action, observe reward and next state
   - Update Q-value: `Q(s,a) += lr * (reward + gamma * max(Q(s',a')) - Q(s,a))`
   - Decay epsilon
5. **Track metrics** — episode returns, Q-value convergence, epsilon decay
6. **Evaluate** — greedy policy performance over 100 episodes

## Q-Learning Update Rule

```
Q(s, a) = Q(s, a) + alpha * (r + gamma * max_a'(Q(s', a')) - Q(s, a))
```

Where:
- `alpha` = learning rate (how fast we update)
- `gamma` = discount factor (how much we value future rewards)
- `r` = immediate reward
- `s'` = next state
- `max_a'(Q(s', a'))` = best possible value from next state

## Epsilon-Greedy Strategy

```
if random() < epsilon:
    action = random_action()       # explore
else:
    action = argmax(Q[state, :])   # exploit

epsilon = max(epsilon_end, epsilon * (1 - epsilon_decay))
```

## Output Format

```
Environment: <env_id>
State Space: Discrete(<N>)
Action Space: Discrete(<M>)
Q-Table Shape: (<N>, <M>)
Hyperparameters:
  learning_rate: <value>
  discount_factor: <value>
  epsilon: <start> -> <end> (decay: <rate>)
  episodes: <count>
Training Result:
  Mean return (last 100 episodes): <value>
  Convergence: <yes/no at episode N>
```
