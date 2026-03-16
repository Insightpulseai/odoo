# Databricks Agent Training

This directory contains the training infrastructure for Databricks-focused AI agents using the "Courses → Competency Map → Your Data → Smol Train → RL" approach.

## Overview

**Key Principle**: Use Databricks courses for competency specification, NOT as training data.

See [docs/infra/DATABRICKS_TRAINING_GUIDELINES.md](../../../docs/infra/DATABRICKS_TRAINING_GUIDELINES.md) for licensing details and recommended approach.

## Directory Structure

```
training/
├── competencies.yaml          # Skill curriculum specification
├── data/                      # Generated training data
│   ├── sft_tasks.jsonl       # Supervised fine-tuning tasks
│   ├── preference_pairs.jsonl # DPO preference pairs
│   └── eval_holdout.jsonl    # Evaluation holdout set
├── validators/                # Reward validators
│   ├── __init__.py
│   ├── bundle.py             # DAB validation
│   ├── sql.py                # SQL/UC validation
│   ├── safety.py             # Policy safety checks
│   └── contracts.py          # Tool contract validation
├── scripts/                   # Training scripts
│   ├── generate_data.py      # Data generation
│   ├── run_sft.sh            # SFT training
│   ├── run_dpo.sh            # DPO training
│   ├── run_rl.sh             # RL training loop
│   └── eval.sh               # Evaluation harness
└── artifacts/                 # Model checkpoints
    └── models/
        ├── sft/
        ├── dpo/
        └── rl/
```

## Quick Start

### 1. Generate Training Data

```bash
cd infra/databricks/training
python scripts/generate_data.py --count 200 --output data/sft_tasks.jsonl
```

### 2. Run Training Pipeline

```bash
# Supervised Fine-Tuning
./scripts/run_sft.sh

# Direct Preference Optimization
./scripts/run_dpo.sh

# Reinforcement Learning with Validators
./scripts/run_rl.sh
```

### 3. Evaluate Model

```bash
./scripts/eval.sh
```

## Competency Domains

| Domain | Description |
|--------|-------------|
| lakehouse_fundamentals | Core architecture, UC, Delta |
| unity_catalog_governance | Security, grants, lineage |
| asset_bundles_ci_cd | DAB deployment workflows |
| lakeflow_pipelines | DLT and declarative pipelines |
| lakeflow_connect | Managed ingestion connectors |
| lakeflow_jobs | Job orchestration |
| databricks_apps | App development and auth |
| ai_agents | Agent development on Databricks |
| mcp_openapi_server | MCP server integration |
| security_privacy | Security and data privacy |
| streaming | Spark Structured Streaming |

## Validators

Validators provide deterministic reward signals for RL training:

| Validator | Purpose |
|-----------|---------|
| `bundle_validate_passes` | Validate DAB configuration |
| `sql_compiles` | SQL syntax validation |
| `grants_audit_passes` | UC grant verification |
| `policy_safety` | Block destructive actions |
| `tool_contract_valid` | Tool call schema validation |

## Training Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_NAME` | `microsoft/phi-2` | Base model for SFT |
| `NUM_EPOCHS` | `3` | Training epochs |
| `BATCH_SIZE` | `4` | Batch size |
| `LEARNING_RATE` | `2e-5` | Learning rate |
| `OUTPUT_DIR` | `artifacts/models/sft` | Model output path |

### Hardware Requirements

- **Minimum**: 16GB RAM, GPU with 8GB VRAM
- **Recommended**: 32GB RAM, GPU with 24GB VRAM
- **CPU-only**: Possible but slow; reduce batch size

## References

- [HF Deep RL Course](https://huggingface.co/learn/deep-rl-course)
- [Smol Training Playbook](https://huggingface.co/spaces/HuggingFaceTB/smol-training-playbook)
- [Databricks Training Terms](https://www.databricks.com/learn/training/terms-and-conditions)
