---
name: foundry-routing
description: Azure AI Foundry routing policy for agent workloads
triggers:
  - keywords: ["Foundry", "AI Foundry", "CLAUDE_CODE_USE_FOUNDRY", "agent routing"]
layer: C-governance
---

# Foundry Routing Policy Skill

Routing rules for AI/agent workloads:

1. Default runtime: Claude Code (local CLI or IDE extension)
2. Foundry routing: opt-in via `CLAUDE_CODE_USE_FOUNDRY=1` env var
3. Foundry is the agent platform for production agent orchestration — not for dev-time coding
4. Never auto-enable Foundry routing in CI/CD pipelines without explicit configuration
5. Foundry workspace: `aifoundry-ipai-dev` in `rg-ipai-ai-dev` (East US 2)
6. Model deployment: Azure OpenAI (`oai-ipai-dev`) is the inference backend
7. Agent identity: Entra ID managed identity (not API keys in env vars)
8. MCP servers: project `.mcp.json` for shared tools, user config for personal
9. Transport: HTTP remote-first for MCP (no SSE as default)
10. Copilot gateway: `ipai-copilot-gateway` (internal, port 8088) — bridges Odoo UI to AI backend
11. Never route sensitive Odoo business data through external AI endpoints without data classification
12. Spec bundle: `spec/foundry-agent-platform/` for architecture decisions
