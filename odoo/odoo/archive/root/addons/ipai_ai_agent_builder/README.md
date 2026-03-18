# IPAI AI Agent Builder

Odoo 19 AI Agents feature parity for CE/OCA deployments.

## Overview

This module provides a comprehensive AI Agent Builder that replicates Odoo 19's AI Agents functionality for Odoo CE environments. It enables organizations to create intelligent agents that combine LLM capabilities with structured tool execution and RAG-based knowledge retrieval.

## Features

- **Agents**: Configurable AI assistants with system prompts and response styles
- **Topics**: Instruction bundles that assign specific tools to agents
- **Tools**: Callable business actions with permission gating and audit trails
- **Multi-provider**: Support for OpenAI (ChatGPT) and Google (Gemini)
- **Observability**: Full audit logging of runs, events, and tool calls
- **Config-as-code**: YAML-based configuration for reproducible deployments

## Installation

```bash
# Install via Docker
docker compose exec odoo-core odoo -d odoo_core -i ipai_ai_agent_builder --stop-after-init

# Verify installation
curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/health
```

## Configuration

### API Keys

Set API keys via environment variables:

```bash
export OPENAI_API_KEY=sk-...
export GOOGLE_API_KEY=AIza...
```

Or configure in Odoo Settings > AI Agent Builder.

### Config-as-Code

Create agent configurations in `config/ipai_ai/agents/`:

```yaml
version: "1.0"
agents:
  - name: "Sales Assistant"
    system_prompt: |
      You are a helpful sales assistant...
    style: "professional"
    provider: "openai"
    model: "gpt-4o"
    topics:
      - name: "Lead Management"
        tools:
          - "crm_create_lead"
```

Load configurations:

```bash
./scripts/ipai_ai_seed.sh
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ipai/ai/v1/agent/<id>/chat` | POST | Chat with an agent |
| `/ipai/ai/v1/agent/<id>/runs` | GET | Get agent run history |
| `/ipai/ai/v1/source/<id>/ingest` | POST | Trigger source ingestion |
| `/ipai/ai/v1/tool/<key>/invoke` | POST | Invoke a tool directly |
| `/ipai/ai/v1/agents` | GET | List all active agents |
| `/ipai/ai/v1/tools` | GET | List all active tools |

## Dependencies

- Python: `openai`, `pyyaml`
- Odoo: `base`, `web`, `mail`
- Related modules: `ipai_ai_rag`, `ipai_ai_tools`

## Security

- Permission gating via Odoo groups
- Multi-company isolation with record rules
- API keys stored securely (env vars recommended)
- Full audit trail for all operations

## License

LGPL-3

## References

- [Odoo 19 AI Agents Documentation](https://www.odoo.com/documentation/19.0/applications/productivity/ai/agents.html)
- [Spec Bundle](../../spec/ipai-ai-agent-builder/)
