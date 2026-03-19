# Checklist: PPO Design

## Prerequisites

- [ ] PPO is the right choice (default unless reason to use something else)
- [ ] Environment observation and action spaces characterized
- [ ] Compute budget established (GPU availability, wall-clock time)
- [ ] Baseline performance established (random, or simpler algorithm)

## Rollout Configuration

- [ ] n_steps set (2048 default, shorter for simple envs)
- [ ] n_envs set (more envs = more diverse data per rollout)
- [ ] Total data per rollout = n_steps * n_envs
- [ ] Observation and reward normalization applied (VecNormalize)

## Update Configuration

- [ ] batch_size set (must divide n_steps * n_envs evenly)
- [ ] n_epochs set (10 default, fewer for complex envs)
- [ ] clip_range set (0.2 default)
- [ ] Learning rate set (3e-4 default)
- [ ] Learning rate schedule defined (constant or linear decay)

## Advantage Estimation

- [ ] GAE lambda set (0.95 default)
- [ ] Gamma set (0.99 default)
- [ ] Advantages normalized before updates

## Network Architecture

- [ ] Shared backbone or separate actor/critic
- [ ] Actor output matches action space
- [ ] Critic outputs single V(s) scalar
- [ ] Orthogonal initialization used (SB3 default)

## Diagnostics Monitoring

- [ ] KL divergence tracked per update
- [ ] Clip fraction tracked (should be 0.1-0.3)
- [ ] Explained variance tracked (should increase)
- [ ] Entropy tracked (should not collapse to zero)
- [ ] Policy loss and value loss tracked

## Evaluation

- [ ] Periodic evaluation with deterministic policy
- [ ] Separate evaluation environment
- [ ] Mean and std over 10+ episodes
- [ ] Learning curve plotted
- [ ] Compared to A2C or other baselines

## Common PPO Pitfalls

- [ ] batch_size not dividing rollout buffer size evenly
- [ ] n_epochs too high causing overfitting to rollout data
- [ ] clip_range too tight (no learning) or too loose (instability)
- [ ] Missing observation normalization for continuous observations
- [ ] Missing reward normalization for varying reward scales
