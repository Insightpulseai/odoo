# Skill: RL Readiness Judge

## Purpose

Judge whether a trained RL agent is ready for promotion from experiment to deployment, based on convergence, generalization, safety, and reproducibility.

## Owner

rl-eval-judge

## Classification

encoded_preference

## Benchmark Source

- HF Deep RL Course (overall curriculum)
- Implementation: Custom eval framework

## When to Use

- Before promoting an RL agent from experiment to staging
- Before deploying to production
- After significant retraining or hyperparameter changes
- As a gate in CI/CD for RL systems

## Key Principle

RL agents are particularly prone to reward hacking, distribution shift, and unsafe behavior. The readiness bar must be proportional to deployment risk. An agent that passes benchmarks but fails edge cases is not ready.

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Formal contract |
| `prompt.md` | Agent prompt |
| `checklist.md` | Readiness checklist |
| `examples.md` | Worked examples |
| `EVALS.md` | Evaluation criteria |
