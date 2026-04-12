# azure-ai-evals-governance -- Worked Examples

## Example 1: Cloud Eval Run for Production Agent

```python
# scripts/foundry/run_cloud_eval.py -- canonical pattern
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import EvaluatorConfiguration, InputDataset
from azure.identity import DefaultAzureCredential

PASS_THRESHOLDS = {
    "groundedness": 0.7,
    "relevance":    0.7,
    "coherence":    0.75,
}

client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

eval_response = client.evaluations.create(
    evaluation={
        "display_name": "pulser-copilot-eval-2026-04-10",
        "description": "Regression eval before prod promotion",
        "data": InputDataset(
            id=client.upload_file("agents/evals/pulser-copilot.jsonl")
        ),
        "evaluators": {
            "groundedness": EvaluatorConfiguration(
                id="azureml://registries/azureml/models/Groundedness-Evaluator/versions/1"
            ),
            "relevance": EvaluatorConfiguration(
                id="azureml://registries/azureml/models/Relevance-Evaluator/versions/1"
            ),
        },
    }
)

# Poll until done
result = client.evaluations.get(eval_response.id)
for metric, score in result.metrics.items():
    threshold = PASS_THRESHOLDS.get(metric, 0.7)
    status = "PASS" if score >= threshold else "FAIL"
    print(f"{metric}: {score:.3f}  {status}")
```

## Example 2: Stage Gate Definition

```yaml
# ssot/agent-platform/stage_gates.yaml
gates:
  - id: gate-dev-to-staging
    name: Dev to Staging Promotion
    required_for_environments: [staging]
    checks:
      - metric: groundedness
        threshold: 0.70
        evaluator: Groundedness-Evaluator
        blocking: true
      - metric: relevance
        threshold: 0.70
        evaluator: Relevance-Evaluator
        blocking: true
      - metric: content_safety_hate
        threshold: safe             # must be 'safe' — no hate content passes
        blocking: true
      - metric: content_safety_violence
        threshold: safe
        blocking: true
    eval_dataset_min_items: 50
    evidence_required: true

  - id: gate-staging-to-prod
    name: Staging to Production Promotion
    required_for_environments: [production]
    checks:
      - metric: groundedness
        threshold: 0.80            # stricter for prod
        evaluator: Groundedness-Evaluator
        blocking: true
      - metric: relevance
        threshold: 0.75
        evaluator: Relevance-Evaluator
        blocking: true
      - metric: coherence
        threshold: 0.75
        evaluator: Coherence-Evaluator
        blocking: true
    eval_dataset_min_items: 100
    evidence_required: true
    approver: platform-admin
```

## Example 3: Eval Dataset Format

```jsonl
{"query": "How do I post a vendor bill in Odoo?", "context": "Odoo 18 CE, accounts payable module", "expected_answer": "Navigate to Accounting > Vendors > Bills, create a new bill, add lines, and click Confirm."}
{"query": "What is the journal entry for a customer payment?", "context": "Odoo 18 CE, accounting", "expected_answer": "Customer payment debits the bank account and credits accounts receivable."}
{"query": "How do I reconcile bank statements in Odoo 18?", "context": "Odoo 18 CE, bank reconciliation", "expected_answer": "Go to Accounting > Bank > Bank Statements, import the statement, and match transactions to journal entries."}
```

Minimum 50 items per dataset. Each item must have `query`, `context`, and `expected_answer` fields.
The `context` field scopes the retrieval so groundedness evaluator can verify the answer is grounded.

## Example 4: MCP Query Sequence

```
Step 1: microsoft_docs_search("Azure AI Foundry evaluation SDK cloud eval pipeline Python")
Result: `client.evaluations.create()` submits async eval job.
        Built-in evaluators referenced by azureml registry IDs.
        Dataset must be uploaded first via `client.upload_file()`.
        Results available via `client.evaluations.get(eval_id).metrics`.

Step 2: microsoft_docs_search("Azure AI content safety filter severity threshold Foundry")
Result: Content filter categories: hate, violence, self-harm, sexual.
        Severity levels: safe, low, medium, high.
        Default threshold: medium (allows low-severity content through).
        Enterprise recommendation: set to low for all categories in ERP context.
        Configure via Azure AI Studio content filter blade or REST API.

Step 3: microsoft_docs_search("Azure Monitor AI Foundry agent metrics logging diagnostic")
Result: Enable via Diagnostic Settings on the Foundry resource.
        Categories: AllLogs (token usage, latency, errors).
        Send to Log Analytics workspace for KQL queries.
        Key metrics: completion_tokens_total, prompt_tokens_total, latency_ms.
```
