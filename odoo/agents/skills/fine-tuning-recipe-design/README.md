# Skill: Fine-Tuning Recipe Design

## Purpose

Design fine-tuning recipes for domain adaptation, instruction tuning, and supervised downstream tasks. Covers both full fine-tuning and parameter-efficient methods (LoRA, QLoRA).

## Owner

- **Persona**: Training Architect (`agents/personas/training-architect.md`)

## Scope

- Full fine-tuning vs PEFT method selection
- Training arguments tuned for fine-tuning (lower lr, fewer epochs)
- Task-specific evaluation metrics
- Catastrophic forgetting monitoring
- Early stopping and best model selection

## Key Principle

Fine-tuning requires far less compute and data than pretraining. Use PEFT methods when compute is limited. Always monitor for catastrophic forgetting by evaluating on general benchmarks alongside task-specific ones.

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Formal skill contract |
| `prompt.md` | Execution prompt |
| `checklist.md` | Verification checklist |
| `examples.md` | Worked examples |
| `EVALS.md` | Evaluation criteria |

## Benchmark Source

- [Fine-tuning guide](https://huggingface.co/docs/transformers/training)
- [Smol Training Playbook](https://huggingface.co/spaces/HuggingFaceTB/smol-training-playbook)
