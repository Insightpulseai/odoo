# Examples: RL Readiness Judge

## Example 1: PPO Agent Promoted to Staging

**Agent**: PPO on LunarLander-v3, requesting promotion to staging.

**Evidence**:
```
VERDICT: PROMOTE

Evidence:
  Convergence: PASS — return stabilized at ~250 for last 200 episodes
  Performance: PASS — mean=247.3, std=18.5, threshold=200
  Generalization: PASS — tested 5 different seeds, min return=218, max=271
  Safety: PASS — 0 violations in 100 episodes
  Reproducibility: PASS — 5 seeds, std across seed means = 15.2
  Documentation: PASS — hyperparameters and training curve saved

Blockers: None
```

**Rationale**: All criteria pass for staging. Mean return exceeds threshold (200) with low variance. Consistent across seeds. Zero safety violations.

---

## Example 2: DQN Agent Blocked

**Agent**: DQN on Atari Breakout, requesting promotion to staging.

**Evidence**:
```
VERDICT: BLOCK

Evidence:
  Convergence: FAIL — return still climbing at end of training (slope > 5%)
  Performance: PASS — mean=38.2, std=12.1, threshold=30
  Generalization: NOT TESTED — blocked before generalization
  Safety: PASS — no applicable constraints
  Reproducibility: FAIL — only 2 seeds run (minimum 3)
  Documentation: PASS

Blockers:
  - Training not converged — increase total timesteps or verify learning rate
  - Only 2 seeds — run minimum 3 seeds before re-evaluation
```

**Rationale**: Two blockers. First, the return curve is still climbing, meaning the agent has not finished learning. Second, only 2 seeds were run, which is below the minimum for staging. Fixing these may also improve mean return.

---

## Example 3: Conditional Promotion

**Agent**: PPO on custom task scheduling environment, requesting promotion to production.

**Evidence**:
```
VERDICT: CONDITIONAL

Evidence:
  Convergence: PASS — stable for 500 episodes
  Performance: PASS — mean=87.3, std=4.2, threshold=80
  Generalization: CONDITIONAL — passes on +/-10% param variation, not tested beyond
  Safety: PASS — 0 violations in 200 episodes
  Reproducibility: PASS — 5 seeds, std=3.8
  Documentation: PASS

Conditions for promotion to production:
  - Generalization must be tested with +/-25% parameter variation
  - Add 100 additional eval episodes with adversarial initial conditions
  - Document behavior when task queue is empty or overloaded
```

**Rationale**: Agent meets all staging criteria and most production criteria. Generalization testing needs to be expanded for production promotion. The custom environment has edge cases (empty queue, overloaded queue) that must be explicitly tested.
