# pulser-odoo-foundry-runtime -- Worked Examples

## Example 1: SDK v1 to v2 Migration for Pulser Agent

**Scenario**: `scripts/foundry/register_agent_v2.py` still uses `from_connection_string`
with the legacy Odoo 19 instruction string.

**Before (v1 debt + stale metadata)**:
```python
# scripts/foundry/register_agent_v2.py  -- BEFORE
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

client = AIProjectClient.from_connection_string(       # v1 anti-pattern
    conn_str=os.environ["AZURE_AI_PROJECT_CONNECTION_STRING"],
    credential=DefaultAzureCredential(),
)

agent = client.agents.create_agent(
    model="gpt-4o",
    name="wg-pulser",
    instructions="You are Pulser, an AI assistant for Odoo 19 ERP.",  # stale: Odoo 19
)
```

**After (v2 canonical + corrected metadata)**:
```python
# scripts/foundry/register_agent_v2.py  -- AFTER
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],  # project-scoped URL
    credential=credential,
)

agent = client.agents.create_agent(
    model="gpt-4.1",                                   # baseline model; matches ssot/ai/models.yaml
    name="wg-pulser",                                  # canonical Pulser name
    instructions="You are Pulser, an AI assistant for Odoo 18 CE ERP.",  # corrected
    tools=[{"type": "file_search"}],                   # File Search preferred (tool policy)
)
print(f"Registered agent: {agent.id}")
```

**SSOT alignment check**:
```yaml
# ssot/ai/models.yaml  -- gpt-4.1 must appear here
deployments:
  - name: gpt-4.1
    model: gpt-4.1
    resource: ipai-copilot-resource
    region: eastus2
    status: active
```

**Verification**:
```bash
python -c "from azure.ai.projects import AIProjectClient; print('OK')"
grep -r "from_connection_string" scripts/foundry/  # must return empty
grep -r "Odoo 19" ssot/ai/                         # must return empty
ruff check scripts/foundry/register_agent_v2.py
```

---

## Example 2: Adding a Bounded Tool for Expense Liquidation

**Scenario**: Adding a Foundry tool that can read and flag expense liquidation
records in Odoo. Must not write records without an approval gate.

**Tool binding in SSOT**:
```yaml
# ssot/ai/agents.yaml  -- excerpt for wg-pulser
agents:
  - name: wg-pulser
    model_deployment_name: gpt-4.1
    tools:
      - type: file_search            # File Search first (per tool policy)
        approval: not_required
      - type: function
        name: get_expense_liquidation_summary
        approval: not_required       # read-only: no gate needed
        odoo_write: false
        description: "Returns liquidation status for a given expense ID from Odoo."
      - type: function
        name: flag_liquidation_discrepancy
        approval: required           # creates activity in Odoo: gate mandatory
        odoo_write: false
        odoo_activity_create: true
        description: "Creates a follow-up activity on the liquidation record."
```

**Tool policy confirmation**:
```yaml
# ssot/agent-platform/foundry_tool_policy.yaml  -- tool preference order
preference_order:
  - file_search                      # built-in, always first
  - function_tool                    # second: direct Odoo function calls
  - openapi_tool                     # third: external API schemas
  - mcp_tool                         # fourth: MCP only when justified
approval_rules:
  odoo_write: required
  odoo_activity_create: required
  odoo_read: not_required
```

**MCP query that confirmed this pattern**:
```
microsoft_docs_search("Azure AI Foundry agent tool approval human-in-the-loop enterprise")
Result: Tools that mutate external systems should use the approval pattern.
        Read-only tools may operate without approval.
        Approval gates are configured at the tool definition level, not the agent level.
```

---

## Example 3: Blocking a Non-Baseline Model Deployment

**Scenario**: A team member proposes adding `gpt-4o-mini` as a cheaper alternative
for the Pulser agent to reduce costs during dev.

**SSOT check**:
```yaml
# ssot/ai/models.yaml  -- current baseline
deployments:
  - name: gpt-4.1
    model: gpt-4.1
    status: active
  - name: wg-pulser
    model: gpt-4.1            # wg-pulser is an agent name, not a separate model
    status: active
  - name: text-embedding-3-small
    model: text-embedding-3-small
    status: active
# gpt-4o-mini: NOT present
```

**Decision**: Blocked. `gpt-4o-mini` is not in the baseline. Proposing it requires:

1. Add to `ssot/ai/models.yaml` with `status: proposed`.
2. Architecture review via `pulser-odoo-architecture` skill.
3. Explicit SSOT approval from the platform admin.
4. Only then run `az cognitiveservices account deployment create ...`.

**Guardrail check**:
```bash
# Confirm no unapproved model exists in the Foundry project
az cognitiveservices account deployment list \
  --name ipai-copilot-resource \
  --resource-group rg-ipai-dev \
  --query "[].name" -o tsv
# Cross-reference output against ssot/ai/models.yaml deployments list
```
