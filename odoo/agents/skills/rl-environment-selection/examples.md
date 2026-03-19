# Examples: RL Environment Selection

## Example 1: Q-Learning Baseline

**Problem**: Learn a tabular Q-learning baseline for a simple navigation task.

**Selection**:
```
Environment: FrozenLake-v1
Action Space: Discrete(4) — up, down, left, right
Observation Space: Discrete(16) — 4x4 grid positions
Reward: Sparse — +1 at goal, 0 elsewhere
Wrappers: None (tabular, no preprocessing needed)
Justification: Small discrete state/action space fits tabular Q-learning.
  FrozenLake is the canonical environment for learning Q-tables.
  Slippery variant (is_slippery=True) tests stochastic transitions.
```

---

## Example 2: DQN for Visual Input

**Problem**: Train a DQN agent on a visual game environment.

**Selection**:
```
Environment: ALE/Breakout-v5
Action Space: Discrete(4) — noop, fire, left, right
Observation Space: Box(84, 84, 4) — after wrappers
Reward: Dense — +1 per brick destroyed
Wrappers:
  1. AtariPreprocessing (frame skip=4, grayscale, resize 84x84)
  2. FrameStack(4) — stack 4 frames for motion detection
  3. ClipReward(-1, 1) — stabilize reward scale
Justification: Breakout is the benchmark Atari environment for DQN.
  Visual input requires CNN feature extraction. Frame stacking provides
  temporal information (ball direction). Dense reward signal enables
  stable training without exploration tricks.
```

---

## Example 3: Continuous Control with PPO

**Problem**: Train a locomotion agent for a simulated robot.

**Selection**:
```
Environment: HalfCheetah-v4 (Gymnasium MuJoCo)
Action Space: Box(6,) — continuous torques for 6 joints
Observation Space: Box(17,) — joint angles, velocities, body position
Reward: Dense — forward velocity minus control cost
Wrappers:
  1. NormalizeObservation — zero-mean, unit-variance
  2. NormalizeReward — running mean/std reward normalization
  3. ClipAction — clip to action space bounds
Justification: HalfCheetah is a standard continuous control benchmark.
  17-dim observation and 6-dim action are moderate complexity. Dense
  reward with velocity component provides clear learning signal.
  PPO with observation/reward normalization is the standard approach.
```

---

## Example 4: Custom Environment

**Problem**: Train an agent to manage a task queue with varying priorities.

**Selection**:
```
Environment: Custom TaskQueueEnv(gymnasium.Env)
Action Space: Discrete(N) — select which task to process next
Observation Space: Box(N, 3) — [priority, age, estimated_duration] per task
Reward: Dense — weighted sum of completed priority and queue wait time
Wrappers:
  1. NormalizeObservation
  2. TimeLimit(max_episode_steps=1000)
Justification: No standard environment matches this domain.
  Custom env implements gymnasium.Env interface for compatibility with
  SB3/CleanRL. Discrete action space (task selection) enables DQN or
  PPO with discrete head. Dense reward provides actionable signal.
```
