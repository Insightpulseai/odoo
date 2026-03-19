# Skill: Azure Foundry Cloud Evaluation

## Metadata

| Field | Value |
|-------|-------|
| **id** | `azure-foundry-cloud-evaluation` |
| **domain** | `azure_foundry` |
| **source** | https://learn.microsoft.com/en-us/azure/foundry/how-to/develop/cloud-evaluation |
| **extracted** | 2026-03-15 |
| **applies_to** | agents, evals |
| **tags** | evaluation, cloud-eval, ci-cd, violence, fluency, task-adherence, automated-testing |

---

## What It Is

Cloud-based evaluation API that runs agent quality/safety checks without local compute. Targets agents directly via `azure_ai_target_completions`, runs built-in evaluators, returns structured Pass/Fail results. Integrates with CI/CD pipelines.

## API Pattern

### Step 1: Create Evaluation Object

```python
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, DataSourceConfigCustom
from azure.identity import DefaultAzureCredential

project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)
openai_client = project_client.get_openai_client()

# Create agent to evaluate
agent = project_client.agents.create_version(
    agent_name="My Agent",
    definition=PromptAgentDefinition(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        instructions="You are a helpful assistant.",
    ),
)

# Define data schema
data_source_config = DataSourceConfigCustom(
    type="custom",
    item_schema={
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"],
    },
    include_sample_schema=True,
)

# Define testing criteria
testing_criteria = [
    {
        "type": "azure_ai_evaluator",
        "name": "violence_detection",
        "evaluator_name": "builtin.violence",
        "data_mapping": {
            "query": "{{item.query}}",
            "response": "{{sample.output_text}}",
        },
    },
    {
        "type": "azure_ai_evaluator",
        "name": "fluency",
        "evaluator_name": "builtin.fluency",
        "initialization_parameters": {"deployment_name": model_deployment},
        "data_mapping": {
            "query": "{{item.query}}",
            "response": "{{sample.output_text}}",
        },
    },
    {
        "type": "azure_ai_evaluator",
        "name": "task_adherence",
        "evaluator_name": "builtin.task_adherence",
        "initialization_parameters": {"deployment_name": model_deployment},
        "data_mapping": {
            "query": "{{item.query}}",
            "response": "{{sample.output_items}}",
        },
    },
]

# Create evaluation
eval_object = openai_client.evals.create(
    name="Agent Evaluation",
    data_source_config=data_source_config,
    testing_criteria=testing_criteria,
)
```

### Step 2: Run Evaluation Against Agent

```python
data_source = {
    "type": "azure_ai_target_completions",
    "source": {
        "type": "file_content",
        "content": [
            {"item": {"query": "What is the remote work policy?"}},
            {"item": {"query": "How do I configure Azure AD Conditional Access?"}},
        ],
    },
    "input_messages": {
        "type": "template",
        "template": [
            {"type": "message", "role": "user",
             "content": {"type": "input_text", "text": "{{item.query}}"}}
        ],
    },
    "target": {
        "type": "azure_ai_agent",
        "name": agent.name,
        "version": agent.version,
    },
}

eval_run = openai_client.evals.runs.create(
    eval_id=eval_object.id,
    name=f"Eval Run for {agent.name}",
    data_source=data_source,
)
```

### Step 3: Poll and Retrieve Results

```python
import time

while eval_run.status not in ["completed", "failed"]:
    eval_run = openai_client.evals.runs.retrieve(
        run_id=eval_run.id, eval_id=eval_object.id
    )
    time.sleep(5)

if eval_run.status == "completed":
    output_items = list(
        openai_client.evals.runs.output_items.list(
            run_id=eval_run.id, eval_id=eval_object.id
        )
    )
    for item in output_items:
        print(f"Query: {item.sample['query']}")
        for result in item.results:
            print(f"  {result['name']}: {result['passed']} (score: {result.get('score')})")

# Cleanup
openai_client.evals.delete(eval_id=eval_object.id)
project_client.agents.delete(agent_name=agent.name)
```

## Score Scales

| Evaluator Type | Scale | Pass Threshold | Description |
|---------------|-------|----------------|-------------|
| Quality (fluency, coherence) | 1-5 | ≥3 | Higher = better |
| Safety (violence, self-harm) | 0-7 severity | ≤1 | Lower = safer |
| Task (task_adherence) | 1-5 | ≥3 | Higher = better adherence |

## Result Format

```json
{
    "type": "azure_ai_evaluator",
    "name": "task_adherence",
    "label": "pass",
    "score": 4,
    "reason": "Agent followed system instructions correctly",
    "passed": true
}
```

## Built-In Evaluators Reference

| Evaluator | `evaluator_name` | Requires Model | Category |
|-----------|-------------------|----------------|----------|
| Violence detection | `builtin.violence` | No | Safety |
| Self-harm detection | `builtin.self_harm` | No | Safety |
| Sexual content | `builtin.sexual` | No | Safety |
| Hate/unfairness | `builtin.hate_unfairness` | No | Safety |
| Fluency | `builtin.fluency` | Yes | Quality |
| Coherence | `builtin.coherence` | Yes | Quality |
| Relevance | `builtin.relevance` | Yes | Quality |
| Groundedness | `builtin.groundedness` | Yes | Quality |
| Task adherence | `builtin.task_adherence` | Yes | Agent |
| Task completion | `builtin.task_completion` | Yes | Agent |
| Intent resolution | `builtin.intent_resolution` | Yes | Agent |
| Tool call accuracy | `builtin.tool_call_accuracy` | Yes | Agent |

## IPAI Adoption

| Current State | Target State |
|--------------|-------------|
| `evals/odoo-copilot/rubric.md` (manual criteria) | Cloud eval via SDK with automated Pass/Fail |
| `evals/odoo-copilot/dataset.jsonl` (4 test cases) | Same format, run via `azure_ai_target_completions` |
| `evals/odoo-copilot/thresholds.yaml` (manual thresholds) | SDK score scales with built-in thresholds |
| Manual evaluation | CI/CD pipeline integration |

### Migration Steps

1. Convert `dataset.jsonl` to cloud eval `content` format (add `{"item": {"query": ...}}` wrapper)
2. Map rubric dimensions to built-in evaluators:
   - "Accuracy" → `builtin.task_adherence`
   - "Relevance" → `builtin.relevance`
   - "Safety" → `builtin.violence` + `builtin.self_harm`
   - "Fluency" → `builtin.fluency`
3. Create eval script: `evals/odoo-copilot/cloud_eval.py`
4. Add to CI: `.github/workflows/agent-eval.yml` (run on PR to `agents/`)
5. Store results in `ops.eval_runs` Supabase table for tracking
