# Skill: PPO Design

## Purpose

Design PPO (Proximal Policy Optimization) training pipelines — the default RL algorithm for most problems.

## Owner

reinforcement-learning-architect

## Classification

capability_uplift

## Benchmark Source

- HF Deep RL Course: PPO
- Implementation: SB3, CleanRL docs (canonical)

## When to Use

- Default choice for most RL problems
- Both discrete and continuous action spaces
- Need stable training without excessive tuning
- Production RL systems

## Key Principle

PPO is the default starting algorithm. Start with PPO unless there is a specific reason to use something else. It is stable, general-purpose, and well-supported across all major RL libraries.

## Key Concepts

- Clipped surrogate objective prevents destructive policy updates
- Multiple epochs of mini-batch updates per data collection
- GAE for advantage estimation
- KL divergence monitoring (not hard constraint in clipped variant)

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Formal contract |
| `prompt.md` | Agent prompt |
| `checklist.md` | Design checklist |
| `examples.md` | Worked examples |
| `EVALS.md` | Evaluation criteria |
