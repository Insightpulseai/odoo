# Skill: Q-Learning Baseline Design

## Purpose

Design tabular Q-learning agents as RL baselines for discrete state/action problems.

## Owner

policy-optimization-engineer

## Classification

capability_uplift

## Benchmark Source

- HF Deep RL Course: Q-Learning
- Implementation: Custom / SB3 docs (canonical)

## When to Use

- Discrete state and action spaces
- Small enough state space for a table (< ~10,000 states)
- Need a simple baseline before trying deep methods
- Educational or prototyping contexts

## Key Concepts

- Q-table: maps (state, action) pairs to expected returns
- Epsilon-greedy: balance exploration and exploitation
- Temporal difference: update Q-values from one-step transitions
- Discount factor (gamma): weight future vs immediate rewards

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Formal contract |
| `prompt.md` | Agent prompt |
| `checklist.md` | Design checklist |
| `examples.md` | Worked examples |
| `EVALS.md` | Evaluation criteria |
