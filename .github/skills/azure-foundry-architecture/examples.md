# azure-foundry-architecture -- Worked Examples

## Example 1: SDK v1 to v2 Migration

Before (v1 debt):
```python
# scripts/foundry/register_agent_v2.py  -- BEFORE (v1 pattern)
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# v1 anti-pattern: connection string from env
client = AIProjectClient.from_connection_string(
    conn_str=os.environ["AZURE_AI_PROJECT_CONNECTION_STRING"],
    credential=DefaultAzureCredential(),
)
```

After (v2 canonical):
```python
# scripts/foundry/register_agent_v2.py  -- AFTER (v2 pattern)
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],   # e.g. https://ipai-copilot-resource.services.ai.azure.com/api/projects/ipai-copilot
    credential=credential,
)

agent = client.agents.create_agent(
    model="gpt-4o",                  # must match a deployment in ssot/ai/models.yaml
    name="pulser-copilot",
    instructions="You are the IPAI copilot...",
    tools=[{"type": "code_interpreter"}],
)
print(f"Created agent: {agent.id}")
```

Key decisions:
- `AIProjectClient(endpoint=..., credential=...)` is the v2 constructor.
- `from_connection_string` is v1 legacy — removed in SDK >= 1.0.0b11.
- `endpoint` is the project-scoped endpoint, not the resource endpoint.

## Example 2: SSOT Agent Definition Alignment

```yaml
# ssot/ai/agents.yaml
agents:
  - name: pulser-copilot
    description: Primary copilot for Odoo ERP context
    model_deployment_name: gpt-4o-ipai-dev     # must exist in ssot/ai/models.yaml
    tools:
      - type: code_interpreter
        approval: not_required
      - type: azure_ai_search
        index: odoo-kb-index
        approval: not_required
      - type: function
        name: create_odoo_task
        approval: required                       # destructive: requires gate
    registered_by: scripts/foundry/register_agent_v2.py
    foundry_project: ipai-copilot
    foundry_resource: ipai-copilot-resource
    region: eastus2
```

```yaml
# ssot/ai/models.yaml -- referenced deployment must exist
deployments:
  - name: gpt-4o-ipai-dev
    model: gpt-4o
    version: "2024-11-20"
    resource: ipai-copilot-resource
    region: eastus2
    quota_tpm: 100000
    status: active
```

## Example 3: MCP Query Sequence

```
Step 1: microsoft_docs_search("Azure AI Foundry Agent Service Python SDK create agent")
Result: Canonical import is `from azure.ai.projects import AIProjectClient`.
        `client.agents.create_agent(model, name, instructions, tools)` returns
        an Agent object with `.id`. Threads are managed via `client.agents.threads`.

Step 2: microsoft_docs_search("Azure AI Foundry SDK v2 migration from v1")
Result: `from_connection_string` was removed in v2. Use endpoint + credential.
        `AZURE_AI_PROJECT_ENDPOINT` is the project-scoped URL.
        `DefaultAzureCredential` is the recommended credential type.

Step 3: microsoft_docs_search("Azure AI Foundry model deployments catalog Python")
Result: Model deployments are listed via Azure AI Studio or
        `az cognitiveservices account deployment list`.
        The `model` param in `create_agent` must match a deployment name
        in the connected project, not the base model name.
```
