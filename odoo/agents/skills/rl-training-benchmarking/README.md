# Skill: RL Training Benchmarking

## Purpose

Benchmark RL training runs, track performance metrics, compare algorithms, and assess sample efficiency.

## Owner

reinforcement-learning-architect

## Classification

encoded_preference

## Benchmark Source

- HF Deep RL Course (overall curriculum)
- Implementation: SB3, Weights & Biases, TensorBoard (canonical)

## When to Use

- Comparing algorithm performance on same environment
- Tracking training progress and diagnosing issues
- Establishing baselines for new environments
- Validating hyperparameter changes

## Key Concepts

- Episode return (primary metric)
- Sample efficiency (return vs timesteps)
- Wall-clock efficiency (return vs time)
- Statistical significance (multiple seeds)
- Learning curves with confidence intervals

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Formal contract |
| `prompt.md` | Agent prompt |
| `checklist.md` | Benchmarking checklist |
| `examples.md` | Worked examples |
| `EVALS.md` | Evaluation criteria |
