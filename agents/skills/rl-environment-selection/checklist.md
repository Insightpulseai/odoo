# Checklist: RL Environment Selection

## Pre-Selection

- [ ] Problem statement is clear — what must the agent learn?
- [ ] Action space type identified (discrete, continuous, multi-discrete)
- [ ] Observation space type identified (vector, image, mixed)
- [ ] Reward density assessed (dense vs sparse)
- [ ] Compute budget established (minimal, moderate, large)

## Environment Search

- [ ] Checked Gymnasium built-in environments
- [ ] Checked domain-specific registries (Atari, MuJoCo, PyBullet)
- [ ] Evaluated standard env fit before designing custom
- [ ] If custom: confirmed it implements `gymnasium.Env` interface
- [ ] If custom: defined `observation_space`, `action_space`, `reset()`, `step()`

## Configuration

- [ ] Wrapper stack defined and ordered
- [ ] Observation normalization applied if needed
- [ ] Reward clipping/normalization applied if needed
- [ ] Episode length limit set appropriately
- [ ] Seed reproducibility verified (`env.reset(seed=N)`)

## Validation

- [ ] Environment runs without error for 100 random steps
- [ ] Observation shape matches expected
- [ ] Action space matches algorithm requirements
- [ ] Reward range is reasonable (not exploding or always zero)
- [ ] Rendering works (if visual debugging needed)

## Documentation

- [ ] Environment ID or class documented
- [ ] Observation and action spaces documented with shapes
- [ ] Reward structure documented (what triggers +/- reward)
- [ ] Termination conditions documented
- [ ] Justification for selection recorded
