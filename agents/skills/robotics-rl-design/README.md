# Skill: Robotics RL Design

## Purpose

Design RL systems for robotics and simulation environments, including continuous control, sim-to-real transfer, and safety constraints.

## Owner

simulation-environment-designer

## Classification

capability_uplift

## Benchmark Source

- HF Deep RL Course: Actor-Critic with Robotics
- Implementation: SB3, PyBullet, MuJoCo docs (canonical)

## When to Use

- Continuous control problems (joint torques, velocities)
- Robotic manipulation or locomotion tasks
- Simulation-based training with potential real-world transfer
- Problems requiring reward shaping and safety constraints

## Key Concepts

- Continuous action spaces with physical constraints
- Reward shaping for complex behaviors
- Domain randomization for sim-to-real transfer
- Safety constraints (joint limits, collision avoidance)

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Formal contract |
| `prompt.md` | Agent prompt |
| `checklist.md` | Design checklist |
| `examples.md` | Worked examples |
| `EVALS.md` | Evaluation criteria |
