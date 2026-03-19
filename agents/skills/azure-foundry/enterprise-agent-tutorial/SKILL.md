# Skill: Enterprise Agent Pattern (SharePoint + MCP)

## Metadata

| Field | Value |
|-------|-------|
| **id** | `azure-foundry-enterprise-agent-tutorial` |
| **domain** | `azure_foundry` |
| **source** | https://learn.microsoft.com/en-us/azure/foundry/tutorials/idea-to-prototype |
| **extracted** | 2026-03-15 |
| **applies_to** | agents, foundry |
| **tags** | enterprise, sharepoint, mcp, knowledge-grounding, graceful-degradation, tutorial |

---

## Pattern

Enterprise agent combining **internal knowledge** (SharePoint/proprietary docs) with **external knowledge** (Microsoft Learn via MCP) and **cloud evaluation**. Demonstrates graceful degradation — agent works even if tools are unavailable.

## Architecture

```
User Query
    ↓
Modern Workplace Assistant (Foundry Agent)
    ├── SharePoint Tool → Internal company policies
    ├── MCP Tool → Microsoft Learn documentation
    └── Model reasoning → Combined response with citations
```

## Three Scenario Types

| Scenario | Tools Used | Example |
|----------|-----------|---------|
| Internal policy | SharePoint only | "What is our remote work policy?" |
| Technical guidance | MCP only | "How to implement Azure AD Conditional Access?" |
| Combined implementation | SharePoint + MCP | "Based on our policy, how should I configure Azure security?" |

## Key Code Patterns

### Graceful Degradation

```python
sharepoint_tool = None
if sharepoint_connection_id:
    try:
        sharepoint_tool = SharepointPreviewTool(
            sharepoint_grounding_preview=SharepointGroundingToolParameters(
                project_connections=[
                    ToolProjectConnection(project_connection_id=sharepoint_connection_id)
                ]
            )
        )
        print("SharePoint tool configured successfully")
    except Exception as e:
        print(f"SharePoint tool unavailable: {e}")
        print("Agent will operate without SharePoint access")
        sharepoint_tool = None
else:
    print("SharePoint integration skipped (not configured)")
```

**Principle**: Never fail the agent because a tool is unavailable. Degrade gracefully and inform the user what capabilities are reduced.

### Tool Composition

```python
tools = []
if sharepoint_tool:
    tools.append(sharepoint_tool)
if mcp_tool:
    tools.append(mcp_tool)

agent = project_client.agents.create_version(
    agent_name="Enterprise Assistant",
    definition=PromptAgentDefinition(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        instructions=instructions,
        tools=tools if tools else None,
    ),
)
```

### MCP with Approval Gate

```python
mcp_tool = MCPTool(
    server_url="https://learn.microsoft.com/api/mcp",
    server_label="Microsoft_Learn_Documentation",
    require_approval="always",  # User must approve MCP tool calls
)
```

## Project Structure

```
enterprise-agent/
├── .env                          # Env vars (never committed)
├── main.py                       # Agent implementation
├── evaluate.py                   # Cloud evaluation script
├── questions.jsonl               # Test scenarios (4 questions)
├── requirements.txt              # Dependencies
└── sharepoint-sample-data/       # Sample internal documents
    ├── remote-work-policy.docx
    ├── security-guidelines.docx
    ├── collaboration-standards.docx
    └── data-governance-policy.docx
```

## Developer Journey (3 Stages)

| Stage | Focus | Key Activities |
|-------|-------|----------------|
| **1. Idea to Prototype** | Working agent | Tools + evaluation + graceful degradation |
| **2. Prototype to Production** | Safety + governance | Red-team testing, eval datasets, fleet monitoring, CI/CD |
| **3. Production to Adoption** | Continuous improvement | Trace data, fine-tuning, API gateway, compliance, cost optimization |

## IPAI Mapping

| Tutorial Pattern | IPAI Equivalent | Gap |
|-----------------|-----------------|-----|
| SharePoint (internal docs) | Azure AI Search index with Odoo/OCA/BIR docs | Index not yet created |
| MCP (Microsoft Learn) | MCP servers in `agents/mcp/` | Already have MCP infra |
| Graceful degradation | Not implemented | **Adopt this pattern** |
| Cloud evaluation | `evals/odoo-copilot/` (manual) | **Migrate to cloud eval** |
| Combined internal+external | Not implemented | **Key pattern for copilot** |

### Adoption Path for ipai-odoo-copilot-azure

Map the tutorial's architecture to IPAI:

```
User Query (via Odoo Discuss)
    ↓
IPAI Odoo Copilot (Foundry Agent)
    ├── Foundry IQ → Odoo docs + OCA docs + BIR rules (internal KB)
    ├── MCP Tool → Microsoft Learn (Azure/Foundry guidance)
    ├── Odoo API Tool → Live ERP data (read-only by default)
    └── Model reasoning → Response with citations
        ↓
    Odoo Discuss (response posted to thread)
```

**Internal knowledge sources**:
- Odoo 19 official docs (indexed in Azure AI Search)
- OCA module documentation (indexed)
- BIR tax rules and compliance guides (indexed)
- IPAI-specific procedures (from `agents/knowledge-base/`)

**External knowledge sources**:
- Microsoft Learn (via MCP)
- OCA GitHub repos (via MCP or API)

**Graceful degradation**:
- If Azure AI Search unavailable → agent uses model knowledge only
- If MCP unavailable → agent skips external docs, warns user
- If Odoo API unavailable → agent answers from cached knowledge, notes data may be stale
