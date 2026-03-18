# Skill: Training Readiness Judge

## Purpose

Decide whether a trained checkpoint is ready to advance from experiment to shared/internal/production use. Verify data quality, eval completeness, training health, and reproducibility before promotion.

## Owner

- **Persona**: Training Eval Judge (`agents/personas/training-eval-judge.md`)

## Scope

- Data quality gate (curation evidence, data card, filtering)
- Eval completeness check (all required benchmarks run)
- Training health verification (loss convergence, no divergence)
- Reproducibility assessment (config, seeds, data versions documented)
- Promotion decision: promote, reject, or needs_more_eval

## Key Principle

No checkpoint advances without eval evidence. This is a hard gate, not advisory. Incomplete evaluation is grounds for blocking, not for a warning. Reproducibility is non-negotiable.

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Formal skill contract |
| `prompt.md` | Execution prompt |
| `checklist.md` | Verification checklist |
| `examples.md` | Worked examples |
| `EVALS.md` | Evaluation criteria |

## Benchmark Source

- [Smol Training Playbook](https://huggingface.co/spaces/HuggingFaceTB/smol-training-playbook)
