# Databricks Training Guidelines for Agent Development

## Overview

This document provides guidelines for using Databricks training materials and courses when building AI agents and training models. It addresses licensing considerations, recommended approaches, and practical implementation patterns.

**Key Principle**: Databricks courses are for **human upskilling**, not for direct model training data ingestion.

---

## Licensing Constraints

### What You CAN Do

| Use Case | Permitted | Notes |
|----------|-----------|-------|
| Human upskilling | Yes | Curriculum for engineers/ops via Databricks Academy |
| Agent policy design | Yes | Extract competency checklists and scenarios |
| Skill requirements definition | Yes | Define what agents must do (without copying course text) |
| Generate your own training data | Yes | Create datasets based on learned competencies |

### What You CANNOT Do

| Use Case | Permitted | Notes |
|----------|-----------|-------|
| Scrape course PDFs/videos | No | Limited, non-transferable license |
| Feed course content into LLM training | No | Internal educational use only |
| Use quizzes as training corpora | No | Violates Databricks training terms |

**Reference**: [Databricks Training Terms and Conditions](https://www.databricks.com/learn/training/terms-and-conditions)

---

## Recommended Approach

```
Courses → Competency Map → Your Data → Smol Train → RL
```

### 1. Convert Courses to Competency Rubric

Extract competency buckets from Databricks course list (without copying content):

| Domain | Competencies |
|--------|-------------|
| Lakehouse Fundamentals | Unity Catalog, Delta, governance |
| Ingestion & Pipelines | Lakeflow Connect, Spark Declarative Pipelines, streaming |
| Orchestration & DevOps | Lakeflow Jobs, Asset Bundles, CI/CD |
| Apps & Agents | Databricks Apps, AI Agents on Databricks |
| Security & Privacy | AI security fundamentals, data privacy |

### 2. Generate Your Own Training Data

Create datasets that mirror real tasks:

- **Tool-use trajectories**: Databricks CLI/API call sequences with expected outputs
- **Failure/repair traces**: Broken bundle configs, failing jobs/pipelines, permission errors → agent fixes
- **SQL + governance tasks**: UC grants, schemas, external locations, table/view creation
- **App scaffolds**: Databricks Apps progression (hello app → auth → UC query → monitoring)

### 3. Train with Open-Source Resources

Use explicitly open-source training resources:

| Resource | License | Purpose |
|----------|---------|---------|
| [HF Deep RL Course](https://huggingface.co/learn/deep-rl-course) | Free/Open-source | RL foundations and workflows |
| [Smol Training Playbook](https://huggingface.co/spaces/HuggingFaceTB/smol-training-playbook) | Open | Pre-training/post-training/infrastructure guidance |

---

## Implementation

### Competencies Specification

Create `infra/databricks/training/competencies.yaml`:

```yaml
competencies:
  - name: asset_bundles_ci_cd
    description: DAB deployment and rollback workflows
    tasks:
      - validate_bundle
      - deploy_bundle_dev
      - deploy_bundle_prod
      - rollback_bundle
    validators:
      - bundle_validate_passes
      - deploy_status_check

  - name: lakeflow_pipelines
    description: Delta Live Tables and streaming pipelines
    tasks:
      - build_declarative_pipeline
      - debug_pipeline_failure
      - enforce_expectations
    validators:
      - pipeline_compiles
      - expectations_defined

  - name: unity_catalog_governance
    description: UC security and data governance
    tasks:
      - create_catalog_schema
      - manage_grants
      - data_lineage_checks
    validators:
      - grants_audit_passes
      - lineage_traced

  - name: databricks_apps
    description: Databricks Apps development
    tasks:
      - scaffold_app
      - add_user_auth
      - query_uc_tables
    validators:
      - app_health_check
      - auth_flow_works

  - name: ai_agents
    description: AI agent development on Databricks
    tasks:
      - tool_selection
      - retrieval_grounding
      - safe_action_constraints
    validators:
      - tool_contract_valid
      - safety_constraints_enforced
```

### Training Data Generation

Generate synthetic tool-use tasks:

```python
#!/usr/bin/env python3
"""Generate synthetic training tasks for Databricks agent training."""

import json
import pathlib
from typing import Any

def generate_bundle_repair_task(task_id: int) -> dict[str, Any]:
    """Generate bundle repair training task."""
    return {
        "id": f"bundle_repair_{task_id:04d}",
        "instruction": "Fix a Databricks Asset Bundle deploy failure caused by a missing variable in databricks.yml.",
        "context": {
            "error": "Variable 'catalog' referenced but not defined",
            "files": {
                "databricks.yml": "resources:\n  jobs:\n    x:\n      name: test-${var.catalog}\n"
            }
        },
        "expected": {
            "patch": "variables:\n  catalog:\n    default: main\n",
            "validator": "bundle_validate_passes"
        }
    }

def generate_uc_grant_task(task_id: int) -> dict[str, Any]:
    """Generate UC grants training task."""
    return {
        "id": f"uc_grant_{task_id:04d}",
        "instruction": "Create Unity Catalog grants for a new data engineering team.",
        "context": {
            "catalog": "analytics",
            "schema": "bronze",
            "team_group": "data_engineers"
        },
        "expected": {
            "sql": "GRANT USAGE ON CATALOG analytics TO `data_engineers`;\nGRANT USE SCHEMA ON SCHEMA analytics.bronze TO `data_engineers`;",
            "validator": "grants_audit_passes"
        }
    }

def generate_tasks(output_path: str, count: int = 200):
    """Generate training task dataset."""
    pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    tasks = []
    for i in range(count):
        if i % 2 == 0:
            tasks.append(generate_bundle_repair_task(i))
        else:
            tasks.append(generate_uc_grant_task(i))

    with open(output_path, "w") as f:
        for task in tasks:
            f.write(json.dumps(task) + "\n")

    print(f"Generated {len(tasks)} tasks to {output_path}")

if __name__ == "__main__":
    generate_tasks("training/data/sft_tasks.jsonl")
```

### Reward Validators

Implement deterministic validators for RL training:

```python
#!/usr/bin/env python3
"""Reward validators for Databricks agent RL training."""

import subprocess
import json
from typing import Any

def bundle_validate_passes(workspace_path: str) -> tuple[bool, str]:
    """
    Validate DAB bundle configuration.

    Returns:
        (success, message)
    """
    try:
        result = subprocess.run(
            ["databricks", "bundle", "validate"],
            cwd=workspace_path,
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            return True, "Bundle validation passed"
        return False, f"Bundle validation failed: {result.stderr}"
    except subprocess.TimeoutExpired:
        return False, "Bundle validation timed out"
    except Exception as e:
        return False, f"Validation error: {e}"

def sql_compiles(sql: str, dialect: str = "databricks") -> tuple[bool, str]:
    """
    Validate SQL syntax.

    Returns:
        (success, message)
    """
    try:
        result = subprocess.run(
            ["sqlfluff", "lint", "--dialect", dialect, "-"],
            input=sql,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return True, "SQL syntax valid"
        return False, f"SQL errors: {result.stdout}"
    except Exception as e:
        return False, f"SQL validation error: {e}"

def tool_contract_valid(tool_call: dict[str, Any], schema: dict[str, Any]) -> tuple[bool, str]:
    """
    Validate tool call matches expected schema.

    Returns:
        (success, message)
    """
    try:
        # Basic schema validation
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in tool_call:
                return False, f"Missing required field: {field}"
        return True, "Tool contract valid"
    except Exception as e:
        return False, f"Contract validation error: {e}"

def policy_safety(action: str, forbidden_patterns: list[str] = None) -> tuple[bool, str]:
    """
    Ensure agent action doesn't contain destructive commands.

    Returns:
        (success, message)
    """
    if forbidden_patterns is None:
        forbidden_patterns = [
            "DROP DATABASE",
            "DROP CATALOG",
            "DELETE FROM",
            "TRUNCATE",
            "--force",
            "-rf /",
        ]

    action_upper = action.upper()
    for pattern in forbidden_patterns:
        if pattern.upper() in action_upper:
            return False, f"Forbidden pattern detected: {pattern}"

    return True, "Action passes safety check"
```

---

## Training Pipeline

### Directory Structure

```
infra/databricks/training/
├── competencies.yaml          # Skill curriculum spec
├── data/
│   ├── sft_tasks.jsonl       # Supervised fine-tuning tasks
│   ├── preference_pairs.jsonl # DPO preference pairs
│   └── eval_holdout.jsonl    # Evaluation holdout set
├── validators/
│   ├── __init__.py
│   ├── bundle.py             # DAB validators
│   ├── sql.py                # SQL validators
│   ├── safety.py             # Policy safety validators
│   └── contracts.py          # Tool contract validators
├── scripts/
│   ├── generate_data.py      # Data generation
│   ├── run_sft.sh            # SFT training
│   ├── run_dpo.sh            # DPO training
│   ├── run_rl.sh             # RL training loop
│   └── eval.sh               # Evaluation harness
└── artifacts/
    └── models/               # Trained model checkpoints
```

### Training Commands

```bash
# Install dependencies
cd infra/databricks/training
python -m venv .venv
. .venv/bin/activate
pip install torch transformers datasets accelerate trl peft evaluate

# Generate training data
python scripts/generate_data.py

# Run SFT
./scripts/run_sft.sh

# Run DPO (preference optimization)
./scripts/run_dpo.sh

# Run RL loop with reward validators
./scripts/run_rl.sh

# Evaluate on holdout set
./scripts/eval.sh
```

---

## Agent Stack Integration

For production deployment, integrate with the Databricks Agent Stack:

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Databricks Agent Stack                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   Chat UI    │───▶│ Agent Service│───▶│  MCP Server  │      │
│  │  (Optional)  │    │ (FastAPI)    │    │  (OpenAPI)   │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                              │                   │               │
│                              ▼                   ▼               │
│                    ┌──────────────────────────────────┐         │
│                    │      Databricks Workspace         │         │
│                    │  ┌─────────┐  ┌─────────────────┐│         │
│                    │  │   UC    │  │  DAB / Jobs     ││         │
│                    │  └─────────┘  └─────────────────┘│         │
│                    └──────────────────────────────────┘         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Deployment Pattern

```bash
# Validate bundle
databricks bundle validate

# Deploy to dev
databricks bundle deploy --target dev

# Smoke test
curl -fsS https://<agent-service>/health
curl -fsS -X POST https://<agent-service>/chat \
  -H 'content-type: application/json' \
  -d '{"message":"test query"}'

# Rollback (if needed)
git checkout v<previous-tag>
databricks bundle deploy --target dev
```

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Databricks course license violation | Use courses for competency specs only, not as training data |
| Low-quality synthetic data | Implement rigorous validators; prefer deterministic checks |
| Reward hacking in RL | Use multiple diverse validators; include human evaluation |
| Model safety issues | Enforce safety validators; include forbidden pattern checks |
| Overfitting to synthetic tasks | Use varied task templates; include real-world examples |

---

## References

- [Databricks Training Terms](https://www.databricks.com/learn/training/terms-and-conditions)
- [Databricks Free Training](https://docs.databricks.com/aws/en/getting-started/free-training)
- [HF Deep RL Course](https://huggingface.co/learn/deep-rl-course)
- [Smol Training Playbook](https://huggingface.co/spaces/HuggingFaceTB/smol-training-playbook)
- [Databricks Free Edition Terms](https://www.databricks.com/legal/databricks-free-edition)

---

*Last updated: 2026-01-25*
