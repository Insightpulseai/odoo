# Skill: Deep Q-Learning Design

## Purpose

Design DQN agents with neural function approximation for large or continuous observation spaces.

## Owner

policy-optimization-engineer

## Classification

capability_uplift

## Benchmark Source

- HF Deep RL Course: Deep Q-Learning with Atari
- Implementation: SB3, CleanRL docs (canonical)

## When to Use

- Observation space too large for tabular methods
- Visual/image observations
- Discrete action spaces (DQN requires discrete actions)
- Need experience replay and target network stability

## Key Concepts

- Neural network approximates Q(s, a) instead of a table
- Experience replay buffer breaks temporal correlation
- Target network provides stable learning targets
- Epsilon scheduling for exploration/exploitation

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Formal contract |
| `prompt.md` | Agent prompt |
| `checklist.md` | Design checklist |
| `examples.md` | Worked examples |
| `EVALS.md` | Evaluation criteria |
