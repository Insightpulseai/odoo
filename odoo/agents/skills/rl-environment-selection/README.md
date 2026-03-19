# Skill: RL Environment Selection

## Purpose

Select and configure RL training environments appropriate for the problem, algorithm, and compute budget.

## Owner

reinforcement-learning-architect

## Classification

encoded_preference

## Benchmark Source

- HF Deep RL Course: Intro to Deep RL
- Implementation: Gymnasium docs (canonical)

## When to Use

- Starting a new RL project and need to choose an environment
- Evaluating whether a standard environment fits or a custom one is needed
- Configuring environment wrappers for preprocessing

## Key Decisions

1. **Standard vs custom environment** — use standard whenever possible
2. **Discrete vs continuous** — action and observation space types
3. **Reward density** — sparse rewards need different algorithms than dense
4. **Wrapper stack** — frame stacking, normalization, clipping

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Formal contract |
| `prompt.md` | Agent prompt |
| `checklist.md` | Decision checklist |
| `examples.md` | Worked examples |
| `EVALS.md` | Evaluation criteria |
