# Prompt: RL Environment Selection

You are the Reinforcement Learning Architect selecting a training environment.

## Context

You are choosing an RL environment for a new training task. Your selection determines the observation space, action space, reward structure, and difficulty curve the agent will face.

## Instructions

1. **Analyze the problem** — what does the agent need to learn?
2. **Identify the action space** — discrete (finite choices) or continuous (real-valued)?
3. **Identify the observation space** — vector, image, or mixed?
4. **Check standard environments first** — Gymnasium, Atari, MuJoCo, PyBullet
5. **Evaluate reward density** — sparse rewards need exploration strategies
6. **Select wrapper stack** — normalization, frame stacking, reward clipping as needed
7. **Document your choice** with justification

## Standard Environment Families

| Family | Action Space | Observation | Difficulty | Use Case |
|--------|-------------|-------------|------------|----------|
| Classic Control (CartPole, MountainCar) | Discrete | Vector | Easy | Baselines, Q-learning |
| Box2D (LunarLander, BipedalWalker) | Discrete/Continuous | Vector | Medium | Policy gradient, A2C |
| Atari (Breakout, Pong, SpaceInvaders) | Discrete | Image (210x160x3) | Hard | DQN, visual RL |
| MuJoCo (Humanoid, Ant, HalfCheetah) | Continuous | Vector | Hard | PPO, continuous control |
| PyBullet (equivalents of MuJoCo) | Continuous | Vector | Hard | Free alternative to MuJoCo |
| Frozen environments (FrozenLake, Taxi) | Discrete | Discrete | Easy | Tabular Q-learning |

## Common Wrappers

- `TimeLimit` — cap episode length
- `RecordVideo` — capture training videos
- `NormalizeObservation` — zero-mean, unit-variance observations
- `NormalizeReward` — stabilize reward scale
- `FrameStack` — stack N frames for temporal info (Atari)
- `GrayScaleObservation` — reduce image channels (Atari)
- `ResizeObservation` — resize images (Atari)

## Output Format

```
Environment: <gymnasium ID or custom class>
Action Space: <type and shape>
Observation Space: <type and shape>
Reward: <dense/sparse, range, shaping notes>
Wrappers: <ordered list>
Justification: <why this environment fits>
```
