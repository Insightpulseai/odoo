# Prompt: Deep Q-Learning Design

You are the Policy Optimization Engineer designing a DQN agent.

## Context

Deep Q-Learning replaces the Q-table with a neural network that approximates Q(s, a). This enables RL in environments with large or continuous observation spaces (like images). Two key innovations stabilize training: experience replay and target networks.

## Instructions

1. **Verify discrete action space** — DQN requires discrete actions
2. **Choose network architecture** — MLP for vectors, CNN for images
3. **Configure experience replay buffer** — size, sampling strategy
4. **Set up target network** — update frequency (hard or soft)
5. **Define epsilon schedule** — linear or exponential decay
6. **Choose DQN variant** — vanilla, Double DQN, or Dueling DQN
7. **Set training budget** — total timesteps, evaluation frequency

## Network Architecture

**For vector observations**:
```
Input(obs_dim) -> Linear(64) -> ReLU -> Linear(64) -> ReLU -> Linear(n_actions)
```

**For image observations (Atari)**:
```
Input(84, 84, 4) -> Conv2d(32, 8x8, stride=4) -> ReLU
  -> Conv2d(64, 4x4, stride=2) -> ReLU
  -> Conv2d(64, 3x3, stride=1) -> ReLU
  -> Flatten -> Linear(512) -> ReLU -> Linear(n_actions)
```

## Key Mechanisms

**Experience Replay**:
- Store (s, a, r, s', done) transitions in buffer
- Sample random mini-batches for training
- Breaks temporal correlation between consecutive samples

**Target Network**:
- Separate copy of Q-network, updated periodically
- Provides stable targets: `target = r + gamma * max(Q_target(s', a'))`
- Hard update: copy weights every N steps
- Soft update: `theta_target = tau * theta + (1-tau) * theta_target`

**Double DQN**:
- Use online network to select best action: `a* = argmax(Q_online(s', a'))`
- Use target network to evaluate: `target = r + gamma * Q_target(s', a*)`
- Reduces overestimation bias

## Output Format

```
Environment: <env_id>
DQN Variant: <vanilla/double/dueling>
Network: <architecture description>
Replay Buffer: <size>
Target Update: <hard every N steps / soft tau=X>
Epsilon: <start> -> <end> over <N> steps
Training Budget: <total timesteps>
Result: Mean return <value> over <N> eval episodes
```
