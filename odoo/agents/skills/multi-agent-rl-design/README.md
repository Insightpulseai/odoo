# Skill: Multi-Agent RL Design

## Purpose

Design multi-agent RL coordination strategies for cooperative, competitive, and mixed environments.

## Owner

policy-optimization-engineer

## Classification

capability_uplift

## Benchmark Source

- HF Deep RL Course: Multi-Agents and AI vs AI
- Implementation: Sample Factory, PettingZoo docs (canonical)
- Note: HF course AI vs AI unit is NON-FUNCTIONAL. Do not depend on it.

## When to Use

- Multiple agents interacting in shared environment
- Cooperative tasks requiring coordination
- Competitive games or adversarial training
- Self-play for training robust policies

## Key Concepts

- Independent learners: each agent trains independently
- Centralized training, decentralized execution (CTDE)
- Self-play: agent trains against copies of itself
- PettingZoo: standard multi-agent environment API

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Formal contract |
| `prompt.md` | Agent prompt |
| `checklist.md` | Design checklist |
| `examples.md` | Worked examples |
| `EVALS.md` | Evaluation criteria |
