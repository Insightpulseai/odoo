# Documents AI

Odoo 19 AI Agents feature parity for CE/OCA deployments.

AI document classification

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

1. Install the module
2. Go to Settings > IPAI > Documents AI
3. Configure as needed

## License

LGPL-3

## References

- [Odoo 19 AI Agents Documentation](https://www.odoo.com/documentation/19.0/applications/productivity/ai/agents.html)
- [Spec Bundle](../../spec/ipai-ai-agent-builder/)
