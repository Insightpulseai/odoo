# Skill: SFT Alignment Design

## Purpose

Design supervised fine-tuning (SFT) alignment pipelines using TRL SFTTrainer. Transform a pretrained or fine-tuned model into a chat/instruction-following model through supervised alignment on conversation data.

## Owner

- **Persona**: Post-Training Engineer (`agents/personas/post-training-engineer.md`)

## Scope

- Chat template application and conversation formatting
- SFTTrainer configuration (max sequence length, packing, truncation)
- Training with evaluation checkpoints
- Aligned model quality assessment

## Key Principle

The chat template used during SFT must exactly match the template used during inference. Mismatched templates produce misaligned behavior. Truncation must be explicit and intentional.

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Formal skill contract |
| `prompt.md` | Execution prompt |
| `checklist.md` | Verification checklist |
| `examples.md` | Worked examples |
| `EVALS.md` | Evaluation criteria |

## Benchmark Source

- [TRL SFTTrainer](https://huggingface.co/docs/trl/sft_trainer)
- [Smol Training Playbook](https://huggingface.co/spaces/HuggingFaceTB/smol-training-playbook)
