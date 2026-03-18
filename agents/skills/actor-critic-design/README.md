# Skill: Actor-Critic Design

## Purpose

Design A2C/A3C actor-critic agents that combine policy gradient (actor) with value function approximation (critic).

## Owner

policy-optimization-engineer

## Classification

capability_uplift

## Benchmark Source

- HF Deep RL Course: Actor-Critic (A2C)
- Implementation: SB3 docs (canonical)

## When to Use

- REINFORCE is too high-variance for the problem
- Need per-step updates (not full episodes)
- Moderate complexity environments
- Stepping stone to PPO

## Key Concepts

- Actor: policy network that selects actions
- Critic: value network that estimates state value V(s)
- Advantage: A(s,a) = R + gamma*V(s') - V(s)
- GAE (Generalized Advantage Estimation): weighted average of n-step advantages

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Formal contract |
| `prompt.md` | Agent prompt |
| `checklist.md` | Design checklist |
| `examples.md` | Worked examples |
| `EVALS.md` | Evaluation criteria |
