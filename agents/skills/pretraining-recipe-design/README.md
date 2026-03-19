# Skill: Pretraining Recipe Design

## Purpose

Design pretraining or continued pretraining recipes including architecture selection, training arguments, checkpoint strategy, and loss monitoring. Covers both training from scratch and extending pretrained models on new domain data.

## Owner

- **Persona**: Training Architect (`agents/personas/training-architect.md`)

## Scope

- Full pretraining vs continued pretraining decision
- Model architecture and size selection
- Training arguments (learning rate, batch size, warmup, scheduler, max steps)
- Checkpoint frequency and evaluation cadence
- Loss monitoring and divergence detection

## Key Principle

Full pretraining requires orders of magnitude more data and compute than continued pretraining. Choose the minimum sufficient approach for the objective.

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Formal skill contract |
| `prompt.md` | Execution prompt |
| `checklist.md` | Verification checklist |
| `examples.md` | Worked examples |
| `EVALS.md` | Evaluation criteria |

## Benchmark Source

- [Transformers Trainer](https://huggingface.co/docs/transformers/trainer)
- [Smol Training Playbook](https://huggingface.co/spaces/HuggingFaceTB/smol-training-playbook)
