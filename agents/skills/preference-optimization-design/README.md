# Skill: Preference Optimization Design

## Purpose

Design DPO (Direct Preference Optimization) and GRPO (Group Relative Policy Optimization) stages for post-SFT alignment refinement. These methods refine an SFT-aligned model using preference data to better match desired behavior.

## Owner

- **Persona**: Post-Training Engineer (`agents/personas/post-training-engineer.md`)

## Scope

- DPO vs GRPO method selection
- Preference data design and formatting
- Beta parameter tuning and loss configuration
- Reward hacking detection
- Comparison to SFT baseline

## Key Principle

Preference optimization is a refinement stage, not a replacement for SFT. Always start with a good SFT checkpoint and always compare back to it. The beta parameter controls how strongly preferences are enforced -- too high leads to over-optimization and degenerate outputs.

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Formal skill contract |
| `prompt.md` | Execution prompt |
| `checklist.md` | Verification checklist |
| `examples.md` | Worked examples |
| `EVALS.md` | Evaluation criteria |

## Benchmark Source

- [TRL DPO Trainer](https://huggingface.co/docs/trl/dpo_trainer)
- [Smol Training Playbook](https://huggingface.co/spaces/HuggingFaceTB/smol-training-playbook)
