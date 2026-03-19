# Skill: Model Data Curation

## Purpose

Select, filter, and validate training data for corpus quality, task/domain fit, and proper train/validation/test splits. Dataset quality is the single highest-leverage factor in model training outcomes.

## Owner

- **Persona**: Dataset Curator (`agents/personas/dataset-curator.md`)

## Scope

- Corpus selection and source evaluation
- Quality filtering pipeline (dedup, language, toxicity, domain)
- Train/validation/test split design with stratification
- Data card and provenance documentation

## Key Principle

Quality over quantity. A small, clean, well-curated dataset produces better models than a large, noisy one.

## Files

| File | Purpose |
|------|---------|
| `skill-contract.yaml` | Formal skill contract |
| `prompt.md` | Execution prompt |
| `checklist.md` | Verification checklist |
| `examples.md` | Worked examples |
| `EVALS.md` | Evaluation criteria |

## Benchmark Source

- [HuggingFaceTB](https://huggingface.co/HuggingFaceTB)
- [Smol Training Playbook](https://huggingface.co/spaces/HuggingFaceTB/smol-training-playbook)
