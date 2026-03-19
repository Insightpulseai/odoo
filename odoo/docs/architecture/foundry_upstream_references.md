# Microsoft Foundry upstream references

## Canonical docs

- Microsoft Foundry quickstart: get-started-code (Python)
- API family: azure-ai-projects v2 (incompatible with 1.x/classic)
- Auth: DefaultAzureCredential via azure-identity
- Connection: project endpoint from Foundry welcome screen

## Canonical sample repos to watch

- foundry-samples — embedded samples in Azure AI Foundry docs
- foundry-agent-webapp — web app with Entra ID integrated with Azure AI Foundry Agents
- Foundry-Local-Lab — local RAG/agents/multi-agent workflows

## Reference-only / not canonical runtime dependency

- mcp-foundry — moved to cloud, points to new Foundry MCP Server
- foundry-mcp-playground — experimental

## SDK pattern (v2)

```python
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

project = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
)

# Model / Responses API
openai_client = project.get_openai_client()
response = openai_client.responses.create(
    model=MODEL_NAME,
    input=user_input,
)

# Agent lifecycle
from azure.ai.projects.models import PromptAgentDefinition

agent = project.agents.create_version(
    agent_name=AGENT_NAME,
    definition=PromptAgentDefinition(
        model=MODEL_NAME,
        instructions=INSTRUCTIONS,
    ),
)
```

## Notes

- Use the docs quickstart as the API contract source of truth
- Use sample repos as implementation reference only
- Do not bind production runtime to archived/experimental MCP repos
- classic 1.x projects API is not supported
