# Examples: RL Training Benchmarking

## Example 1: PPO vs A2C on LunarLander

**Protocol**:
```
Environment: LunarLander-v3
Algorithms: PPO, A2C
Seeds: 5 (0, 1, 2, 3, 4)
Total Timesteps: 500,000 per run
Evaluation: every 25,000 steps, 20 episodes
Random Baseline: mean return = -180.3 (std 77.2)
```

**Results**:

| Algorithm | Mean Return | Std | Sample Efficiency (200+ threshold) |
|-----------|-------------|-----|------------------------------------|
| PPO | 247.3 | 18.5 | ~200K steps |
| A2C | 198.7 | 45.2 | ~350K steps |
| Random | -180.3 | 77.2 | N/A |

**Conclusion**: PPO achieves higher mean return with lower variance and better sample efficiency on LunarLander. PPO is the recommended default.

---

## Example 2: DQN Variants on Atari

**Protocol**:
```
Environment: ALE/Breakout-v5
Algorithms: DQN, Double DQN, Dueling DQN
Seeds: 3 (limited by GPU budget)
Total Timesteps: 2,000,000 per run
Evaluation: every 100,000 steps, 10 episodes
Hardware: 1x NVIDIA T4 GPU
```

**Results**:

| Variant | Mean Score | Std | Wall-Clock (hours) |
|---------|-----------|-----|--------------------|
| DQN | 32.1 | 8.4 | 3.2 |
| Double DQN | 41.7 | 6.1 | 3.4 |
| Dueling DQN | 38.9 | 7.3 | 3.5 |

**Conclusion**: Double DQN outperforms vanilla DQN with minimal compute overhead. Dueling DQN shows improvement but less consistent than Double DQN on this environment.

**Caveat**: Only 3 seeds — results should be verified with more seeds before strong conclusions.

---

## Example 3: Hyperparameter Sensitivity Analysis

**Protocol**:
```
Environment: HalfCheetah-v4
Algorithm: PPO
Variable: learning_rate
Values: [1e-4, 3e-4, 1e-3, 3e-3]
Seeds: 3 per value
Total Timesteps: 1,000,000
```

**Results**:

| Learning Rate | Mean Return | Std | Notes |
|---------------|-------------|-----|-------|
| 1e-4 | 2847 | 312 | Slow but stable |
| 3e-4 | 4123 | 456 | Best overall (SB3 default) |
| 1e-3 | 3891 | 891 | Good performance, higher variance |
| 3e-3 | 1204 | 1523 | Unstable training |

**Conclusion**: 3e-4 (SB3 default) is indeed a good learning rate for PPO on HalfCheetah. Higher rates increase variance, 3e-3 is unstable.
