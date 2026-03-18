# Skill: Policy Gradient Design

## Purpose

Design REINFORCE and policy gradient methods for RL problems, especially those with continuous action spaces.

## Owner

policy-optimization-engineer

## Classification

capability_uplift

## Benchmark Source

- HF Deep RL Course: Policy Gradient (Reinforce)
- Implementation: SB3, CleanRL docs (canonical)

## When to Use

- Continuous action spaces (where DQN cannot apply)
- Stochastic policy needed (exploration via policy randomness)
- Simple problems where REINFORCE suffices
- As a stepping stone to actor-critic methods

## Key Concepts

- Policy network outputs action probabilities (discrete) or distribution parameters (continuous)
- REINFORCE: Monte Carlo policy gradient — complete episodes required
- Log probability gradient weighted by return
- Baseline subtraction reduces variance without introducing bias

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Formal contract |
| `prompt.md` | Agent prompt |
| `checklist.md` | Design checklist |
| `examples.md` | Worked examples |
| `EVALS.md` | Evaluation criteria |
