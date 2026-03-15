# Knowledge: Agentic SDLC — Microsoft Reference Architecture

## Source

- **Article**: [An AI-Led SDLC: Building an End-to-End Agentic Software Development Lifecycle with GitHub](https://techcommunity.microsoft.com/blog/appsonazureblog/an-ai-led-sdlc-building-an-end-to-end-agentic-software-development-lifecycle-wit/4491896)
- **Framework**: [microsoft/agent-framework](https://github.com/microsoft/agent-framework) (MIT, 7.2k stars, Python + .NET)
- **VS Code extension**: [Azure AI Foundry for VS Code](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/vs-code-agents-workflow-pro-code)
- **Extracted**: 2026-03-15

---

## Framework Capabilities vs IPAI Stack

| Capability | Agent Framework | IPAI Current |
|------------|----------------|--------------|
| Graph-based workflows | Native | n8n (linear/branching) |
| Multi-agent orchestration | Native | Manual via n8n + Claude |
| Streaming + checkpointing | Built-in | Custom Supabase queues |
| Human-in-the-loop | Built-in | Custom review tables |
| Time-travel / replay | Built-in | `ops.run_events` (DIY) |
| OpenTelemetry observability | Built-in | DIY via OTLP |
| DevUI for local debugging | `python/packages/devui` | None |
| Multi-provider LLM | Multi-provider | Claude-first |
| Self-hosted / portable | MIT, no Foundry required | Yes |

---

## VS Code Extension Workflow (Pro-Code Path)

### Setup

```bash
# 1. Scaffold project
# Ctrl+Shift+P → "Microsoft Foundry: Create a New Hosted Agent"

# 2. Install framework
python -m venv .venv && source .venv/bin/activate
pip install azure-ai-agentserver-agentframework

# 3. Configure .env (never commit)
# AZURE_AI_PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
# AZURE_AI_MODEL_DEPLOYMENT_NAME=<deployment>
```

### Auth

Uses `DefaultAzureCredential` — `az login` or VS Code account for local dev. Service principal env vars for CI:
- `AZURE_TENANT_ID`
- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_SECRET`

### Run Modes

| Mode | How |
|------|-----|
| Interactive (debug) | F5 → HTTP server + AI Toolkit Agent Inspector |
| Container mode | Command palette → Open Container Agent Playground → `main.py` |

### Observability

```python
from agent_framework.observability import setup_observability
setup_observability(vs_code_extension_port=4319)
# Enable sensitive data tracing (local only!):
# setup_observability(vs_code_extension_port=4319, enable_sensitive_data=True)
```

Visualizer: `Ctrl+Shift+P` → "Microsoft Foundry: Open Visualizer for Hosted Agents"

### Deploy

```
Command palette → "Microsoft Foundry: Deploy Hosted Agent"
Entry point: container.py
Post-deploy: appears under Hosted Agents (Preview) in extension tree
```

---

## Prerequisites for IPAI Deployment

- Foundry project managed identity needs `Azure AI User` + `AcrPull` roles
- Verify Southeast Asia region support for hosted agents
- `DefaultAzureCredential` maps to existing ACA managed identity pattern
- OTLP port 4319: check for conflicts with existing n8n/Supabase stack

---

## Architectural Decision

**Verdict**: Use as reference architecture for agent sequencing and observability patterns. Do not adopt wholesale.

**Why**: IPAI's agent layer stays vendor-agnostic and Supabase-SSOT-anchored per doctrine. The framework is more useful for:
1. Graph-based agent orchestration patterns
2. OTLP tracing integration
3. Checkpoint/replay patterns (wire to `ops.runs`)
4. DevUI for local agent debugging

**Do not use for**: Replacing n8n for simple integration/webhook routing where n8n is simpler.

---

## Repo Structure (microsoft/agent-framework)

```
microsoft/agent-framework/
├── python/
│   ├── packages/          # installable sub-packages (incl. devui, lab)
│   └── samples/
│       ├── 01-get-started/
│       ├── 02-agents/     # tools, middleware, providers, observability
│       └── 03-workflows/  # graph-based multi-agent
├── dotnet/
│   └── samples/GettingStarted/
├── schemas/               # typed workflow/agent schema contracts
├── workflow-samples/
└── docs/
    ├── design/
    └── decisions/         # ADRs
```

Key directories to pull from:
- `schemas/` — typed workflow contracts for SSOT contract layer reference
- `python/samples/03-workflows/` — graph-based multi-agent patterns
- `docs/decisions/` — ADRs for architectural rationale
