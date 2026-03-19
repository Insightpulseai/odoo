# Skill: Azure Foundry SDK Quickstart

## Metadata

| Field | Value |
|-------|-------|
| **id** | `azure-foundry-sdk-quickstart` |
| **domain** | `azure_foundry` |
| **source** | https://learn.microsoft.com/en-us/azure/foundry/quickstarts/get-started-code |
| **extracted** | 2026-03-15 |
| **applies_to** | agents, foundry, infra |
| **tags** | sdk, python, cli, quickstart, project-setup, agent-creation |

---

## Dev Environment Setup (macOS + Python)

### Prerequisites

| Tool | Install | Version |
|------|---------|---------|
| **Python** | `brew install python@3.12` or pyenv | 3.10+ (3.12 recommended) |
| **Azure CLI** | `brew update && brew install azure-cli` | Latest |
| **Azure Developer CLI** | [Install azd](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd) | Latest |
| **Git** | `brew install git` | Latest |
| **VS Code** | [Download](https://code.visualstudio.com/Download) | Latest |

### VS Code Extensions

| Extension | Purpose |
|-----------|---------|
| **Foundry** (`TeamsDevApp.vscode-ai-foundry`) | Deploy models, build agents from VS Code |
| **Python** (`ms-python.python`) | IntelliSense, debugging, formatting |

### Python Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --pre "azure-ai-projects>=2.0.0b4"
pip install azure-identity python-dotenv openai
```

### Authentication

```bash
az login
# Or for headless/CI:
az login --use-device-code
```

### RBAC Roles

| Role | For |
|------|-----|
| **Azure AI Project Manager** | Managing Foundry projects |
| **Owner** | Full subscription permissions (role assignments) |
| **Azure AI User** | Least-privilege for development |

---

## Environment Variables Contract

```bash
PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
MODEL_DEPLOYMENT_NAME=gpt-4.1-mini  # or any deployed model
AGENT_NAME=MyAgent
```

## 1. Project Setup via Azure CLI

```bash
# Create resource group
az group create --name my-foundry-rg --location eastus

# Create Foundry resource (AIServices kind)
az cognitiveservices account create \
  --name my-foundry-resource \
  --resource-group my-foundry-rg \
  --kind AIServices \
  --sku s0 \
  --location eastus \
  --allow-project-management

# Set custom subdomain (must be globally unique)
az cognitiveservices account update \
  --name my-foundry-resource \
  --resource-group my-foundry-rg \
  --custom-domain my-foundry-resource

# Create project
az cognitiveservices account project create \
  --name my-foundry-resource \
  --resource-group my-foundry-rg \
  --project-name my-foundry-project \
  --location eastus
```

## 2. Deploy a Model

```bash
az cognitiveservices account deployment create \
  --name my-foundry-resource \
  --resource-group my-foundry-rg \
  --deployment-name gpt-4.1-mini \
  --model-name gpt-4.1-mini \
  --model-version "2025-04-14" \
  --model-format OpenAI \
  --sku-capacity 10 \
  --sku-name Standard
```

## 3. Grant Team Access

```bash
# Get project resource ID
PROJECT_ID=$(az cognitiveservices account project show \
  --name my-foundry-resource \
  --resource-group my-foundry-rg \
  --project-name my-foundry-project \
  --query id -o tsv)

# Assign Azure AI User role
az role assignment create \
  --role "Azure AI User" \
  --assignee "user@contoso.com" \
  --scope $PROJECT_ID
```

## 4. Python SDK Install

```bash
pip install --pre "azure-ai-projects>=2.0.0b4"
pip install python-dotenv azure-identity
```

**Note**: Uses Azure AI Projects 2.x API — incompatible with 1.x.

## 5. Chat with a Model (Direct)

```python
import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

openai_client = project_client.get_openai_client()

response = openai_client.responses.create(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    input="What is the size of France in square miles?",
)
print(response.output_text)
```

## 6. Create an Agent

```python
from azure.ai.projects.models import PromptAgentDefinition

agent = project_client.agents.create_version(
    agent_name="MyAgent",
    definition=PromptAgentDefinition(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        instructions="You are a helpful assistant.",
    ),
)
print(f"Agent created: {agent.name} v{agent.version}")
```

## 7. Multi-Turn Conversation

```python
openai_client = project_client.get_openai_client()

# Create conversation for context persistence
conversation = openai_client.conversations.create()

# First turn
response = openai_client.responses.create(
    conversation=conversation.id,
    extra_body={"agent_reference": {"name": "MyAgent", "type": "agent_reference"}},
    input="What is the size of France?",
)
print(response.output_text)

# Follow-up (agent remembers context)
response = openai_client.responses.create(
    conversation=conversation.id,
    extra_body={"agent_reference": {"name": "MyAgent", "type": "agent_reference"}},
    input="And what is the capital city?",
)
print(response.output_text)
```

## 8. Add Tools to Agent

```python
from azure.ai.projects.models import (
    PromptAgentDefinition,
    WebSearchTool,
    MCPTool,
    SharepointPreviewTool,
    SharepointGroundingToolParameters,
    ToolProjectConnection,
)

tools = [
    WebSearchTool(),
    MCPTool(
        server_url="https://learn.microsoft.com/api/mcp",
        server_label="Microsoft_Learn",
        require_approval="always",
    ),
]

agent = project_client.agents.create_version(
    agent_name="ToolAgent",
    definition=PromptAgentDefinition(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        instructions="You are a helpful assistant with web search and docs.",
        tools=tools,
    ),
)
```

## Claude Code on Azure Foundry

### Setup (macOS/bash)

```bash
# Install Claude Code CLI
curl -fsSL https://claude.ai/install.sh | bash
# Or: brew install --cask claude-code

# Enable Foundry integration
export CLAUDE_CODE_USE_FOUNDRY=1
export ANTHROPIC_FOUNDRY_RESOURCE=<your-resource-name>
# Or full URL: export ANTHROPIC_FOUNDRY_BASE_URL=https://<name>.services.ai.azure.com

# Optional: pin model deployment names
export ANTHROPIC_DEFAULT_SONNET_MODEL="claude-sonnet-4-6"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="claude-haiku-4-5"
export ANTHROPIC_DEFAULT_OPUS_MODEL="claude-opus-4-6"
```

### Authentication

| Method | How | Best For |
|--------|-----|----------|
| **Entra ID** (recommended) | `az login` → Claude Code detects automatically | Enterprise, teams, CI/CD |
| **API key** | `export ANTHROPIC_FOUNDRY_API_KEY=<key>` | Quick testing, no Azure CLI |

### Claude Code Model Roles

| Role | Recommended Model | Purpose |
|------|-------------------|---------|
| Primary | `claude-sonnet-4-6` | General coding — balanced speed + quality |
| Fast | `claude-haiku-4-5` | Quick operations — file reads, small edits |
| Extended thinking | `claude-opus-4-6` | Complex reasoning tasks |

### VS Code Extension Config

```json
{
  "Claude Code: Environment Variables": {
    "CLAUDE_CODE_USE_FOUNDRY": "1",
    "ANTHROPIC_FOUNDRY_RESOURCE": "<your-resource-name>"
  }
}
```

### Validate

```bash
cd your-project && claude
> /status
# Expect: API provider = Microsoft Foundry
```

### GitHub Actions Integration

```yaml
name: Claude PR Review
on:
  issue_comment:
    types: [created]
jobs:
  respond:
    if: contains(github.event.comment.body, '@claude')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: anthropics/claude-code-action@v1
        with:
          prompt: ${{ github.event.comment.body }}
        env:
          CLAUDE_CODE_USE_FOUNDRY: "1"
          ANTHROPIC_FOUNDRY_RESOURCE: ${{ secrets.AZURE_FOUNDRY_RESOURCE }}
          ANTHROPIC_FOUNDRY_API_KEY: ${{ secrets.AZURE_FOUNDRY_API_KEY }}
```

### Region Availability

Claude models in Foundry: **East US 2** and **Sweden Central** only.

**Note**: IPAI's primary region is Southeast Asia. Claude Code on Foundry requires cross-region calls to East US 2 or Sweden Central. Latency acceptable for development; evaluate for production agent workloads.

### IPAI-Specific Config

Add to `~/.zshrc` (persist across sessions):

```bash
# Azure Foundry — Claude Code
export CLAUDE_CODE_USE_FOUNDRY=1
export ANTHROPIC_FOUNDRY_RESOURCE=<ipai-foundry-resource>
export ANTHROPIC_DEFAULT_SONNET_MODEL="claude-sonnet-4-6"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="claude-haiku-4-5"
export ANTHROPIC_DEFAULT_OPUS_MODEL="claude-opus-4-6"
```

---

## Foundry VS Code Extension

### Features

| Section | Contents |
|---------|----------|
| **Resources** | Deployed models, agents, connections, vector stores |
| **Tools** | Model Catalog, Playground, Agent Playgrounds (remote + local), Visualizer |
| **Help** | Docs, GitHub, community |

### Key Commands (F1 → "Foundry:")

- `Foundry: Open Model Catalog` — browse + deploy models
- `Foundry: Open Playground` — interactive chat with deployed model
- Right-click model → `Open code file` → select SDK + language + auth → generates starter code

### Model Deployment from VS Code

1. Open Model Catalog → select model → Deploy
2. Enter deployment name (this becomes the alias)
3. Select deployment type + version
4. Adjust tokens per minute
5. Model appears under Resources → Models

---

## SDK Architecture

```
DefaultAzureCredential (az login / managed identity / service principal)
    ↓
AIProjectClient(endpoint, credential)
    ├── .agents.create_version()     → Agent CRUD
    ├── .agents.delete()             → Agent cleanup
    └── .get_openai_client()         → OpenAI-compatible client
        ├── .responses.create()      → Model/agent chat
        ├── .conversations.create()  → Multi-turn context
        └── .evals.create()          → Cloud evaluation
```

## IPAI Mapping

| SDK Pattern | IPAI Equivalent | Action |
|-------------|-----------------|--------|
| `az cognitiveservices account project create` | Manual Azure portal setup | **Automate via CLI** |
| `AIProjectClient` | None (direct API calls) | **Adopt SDK** for Foundry copilot |
| `DefaultAzureCredential` | Same pattern in ACA (managed identity) | Already aligned |
| `agents.create_version` | `foundry/ipai-odoo-copilot-azure/metadata.yaml` | Wire copilot to SDK |
| `conversations.create` | Odoo Discuss thread | Bridge via `ipai_odoo_copilot` module |
| Multi-turn context | Not implemented | **Gap — need conversation persistence** |

### Adoption Path for ipai-odoo-copilot-azure

1. Install SDK: `pip install --pre "azure-ai-projects>=2.0.0b4"`
2. Create Foundry project in `rg-ipai-ai-dev` (Southeast Asia)
3. Deploy model (`gpt-4.1` per existing `metadata.yaml`)
4. Register copilot agent via `agents.create_version`
5. Connect knowledge base via Foundry IQ
6. Wire Odoo Discuss → Foundry conversation API
