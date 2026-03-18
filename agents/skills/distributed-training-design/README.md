# Skill: Distributed Training Design

## Purpose

Design multi-GPU and multi-node training strategies with parallelism selection, memory optimization, and speed/cost tradeoffs. Covers data parallel, tensor parallel, pipeline parallel, FSDP, mixed precision, gradient checkpointing, and CPU offloading.

## Owner

- **Persona**: Distributed Training Engineer (`agents/personas/distributed-training-engineer.md`)

## Scope

- Memory requirement estimation (model + optimizer + gradients + activations)
- Single GPU vs multi-GPU decision
- Parallelism strategy selection (DDP, FSDP, tensor parallel, pipeline parallel)
- Memory optimization (mixed precision, gradient checkpointing, offloading)
- Small-scale validation before full runs

## Key Principle

Start simple. If the model fits on a single GPU, use a single GPU. Only distribute when necessary, and choose the simplest parallelism strategy that meets requirements.

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Formal skill contract |
| `prompt.md` | Execution prompt |
| `checklist.md` | Verification checklist |
| `examples.md` | Worked examples |
| `EVALS.md` | Evaluation criteria |

## Benchmark Source

- [Accelerate](https://huggingface.co/docs/transformers/accelerate)
- [Smol Training Playbook](https://huggingface.co/spaces/HuggingFaceTB/smol-training-playbook)
