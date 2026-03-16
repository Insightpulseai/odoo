# Skill: Azure Foundry Agent Evaluators

## Metadata

| Field | Value |
|-------|-------|
| **id** | `azure-foundry-agent-evaluators` |
| **domain** | `azure_foundry` |
| **source** | https://learn.microsoft.com/en-us/azure/foundry/concepts/evaluation-evaluators/agent-evaluators |
| **extracted** | 2026-03-15 |
| **applies_to** | agents, evals |
| **tags** | evaluation, quality, safety, task-adherence, tool-accuracy |

---

## Evaluator Types

### System Evaluation (End-to-End Outcomes)

| Evaluator | Measures | Output | When to Use |
|-----------|----------|--------|-------------|
| **Task Completion** (preview) | Did the agent complete the requested task with a usable deliverable? | Pass/Fail | Workflow automation, goal-oriented interactions |
| **Task Adherence** (preview) | Did the agent follow its instructions, rules, and policy constraints? | Pass/Fail | Compliance, regulated environments |
| **Task Navigation Efficiency** | Did the agent take an optimal sequence of actions? (Requires ground truth) | Pass/Fail + precision/recall/F1 | Workflow optimization, regression testing |
| **Intent Resolution** (preview) | Did the agent correctly identify the user's intent? | Pass/Fail (1-5 scale → threshold) | Customer support, conversational AI |

### Process Evaluation (Step-by-Step)

| Evaluator | Measures | Output | When to Use |
|-----------|----------|--------|-------------|
| **Tool Call Accuracy** | Right tool calls with correct parameters? | Pass/Fail (1-5 scale → threshold) | Overall tool quality in agent systems |
| **Tool Selection** | Correct tools without unnecessary ones? | Pass/Fail | Validating tool choice, avoiding redundancy |
| **Tool Input Accuracy** | All parameters correct across 6 criteria? | Pass/Fail | Strict parameter validation in production |
| **Tool Output Utilization** | Correctly used tool results in reasoning? | Pass/Fail | Validating use of API responses, DB queries |
| **Tool Call Success** | Did tool calls succeed without errors? | Pass/Fail | Monitoring tool reliability, API failures |

## Tool Input Accuracy — 6 Criteria

1. Groundedness
2. Type compliance
3. Format compliance
4. Required parameters present
5. No unexpected parameters
6. Value appropriateness

## Navigation Efficiency Matching Modes

| Mode | Description |
|------|-------------|
| `exact_match` | Trajectory must match ground truth exactly (order + content) |
| `in_order_match` | All ground truth steps must appear in correct order (extra steps OK) |
| `any_order_match` | All ground truth steps must appear, any order (extra steps OK) |

## Recommended Judge Model

`gpt-5-mini` — best balance of performance, cost, and efficiency for evaluation.

## IPAI Eval Mapping

| Foundry Evaluator | IPAI Equivalent | Status |
|-------------------|-----------------|--------|
| Task Completion | `evals/odoo-copilot/rubric.md` (manual criteria) | Need to formalize as Pass/Fail |
| Task Adherence | Constitution compliance check | Need to automate |
| Tool Call Accuracy | None | **Gap — adopt this pattern** |
| Intent Resolution | None | **Gap — adopt for copilot** |
| Tool Call Success | n8n execution status | Already tracked in ops.run_events |

### Adoption Priority

1. **Task Adherence** — Apply to every agent using the constitution as baseline
2. **Tool Call Accuracy** — Apply to agents with tool integrations (OCR, Odoo API)
3. **Task Completion** — Apply to end-to-end workflow agents (BIR, expense)
4. **Intent Resolution** — Apply to the Foundry copilot (ipai-odoo-copilot-azure)

## Python Example

```python
testing_criteria = [
    {
        "type": "azure_ai_evaluator",
        "name": "task_adherence",
        "evaluator_name": "builtin.task_adherence",
        "initialization_parameters": {"deployment_name": model_deployment},
        "data_mapping": {
            "query": "{{item.query}}",
            "response": "{{item.response}}",
        },
    },
]
```

## Input Format (Conversation Array)

```json
{
  "query": [
    {"role": "system", "content": "You are a travel booking agent."},
    {"role": "user", "content": "Book a flight to Paris"}
  ],
  "response": [
    {"role": "assistant", "content": [{"type": "tool_call", "name": "search_flights", "arguments": {"destination": "Paris"}}]},
    {"role": "tool", "content": [{"type": "tool_result", "tool_result": {"flight": "AF123"}}]},
    {"role": "assistant", "content": "Booked flight AF123 to Paris."}
  ]
}
```
