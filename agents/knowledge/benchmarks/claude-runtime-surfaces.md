# Benchmark: Claude Runtime Surfaces

> Source: Claude Developer Platform docs, Claude Cookbooks repo
>
> Role: Runtime and API surface reference for Claude integration
>
> This is the runtime/example layer — NOT top-level architecture doctrine.

---

## Claude Platform Surfaces (March 2026)

| Surface | Purpose | Docs |
|---------|---------|------|
| **Messages API** | Core text generation, tool use, streaming | platform.claude.com/docs |
| **Agent Skills** | Reusable skill definitions with triggers | platform.claude.com/docs |
| **Agent SDK** | Python/TS orchestration framework | claude-agent-sdk |
| **MCP** | Model Context Protocol — standard tool/resource integration | modelcontextprotocol.io |
| **Remote MCP servers** | Server-side MCP hosting for tools | Foundry + standalone |
| **Evaluations** | Built-in eval framework | platform.claude.com/docs |
| **Guardrails** | Safety and policy enforcement | platform.claude.com/docs |
| **Usage/Cost/Admin APIs** | Billing, rate limits, org management | platform.claude.com/docs |
| **Claude on Foundry** | Claude as model provider in Azure AI Foundry | Azure AI model catalog |

---

## Integration Paths

### Direct API

```
App → Claude API → Messages + Tools + Streaming
```

Best for: custom applications, batch processing, fine-grained control.

### MCP-Mediated

```
Claude → MCP Client → MCP Server → External Tool/Resource
```

Best for: standardized tool integration, reusable across providers.

### Foundry-Hosted

```
App → Azure AI Foundry → Claude (model provider) → Tools via MCP
```

Best for: enterprise governance, model routing, cost management.

---

## Cookbook Organization (Reference Pattern)

The claude-cookbooks repo provides implementation examples in:

| Folder | Content |
|--------|---------|
| `patterns/agents` | Agent architecture examples |
| `skills` | Skill definition examples |
| `tests` | Test fixture patterns |
| `tool_use` | Tool integration examples |
| `tool_evaluation` | Tool quality assessment |
| `observability` | Monitoring and tracing |
| `claude_agent_sdk` | SDK usage patterns |

This maps to our repo as:
- `agents/skills/` — our bounded skill contracts (not examples)
- `agents/knowledge/benchmarks/` — our benchmark references (not implementations)
- `docs/evidence/` — our eval evidence (not experiments)

---

## Tool Design (Claude-Specific)

From Anthropic's tool-authoring guidance specific to Claude:

- Claude improved 40% on task time after tool description refinements alone
- When Claude appended "2025" to web searches, the fix was improving the tool description, not code
- Code execution via MCP reduced token usage by up to 98.7% compared to individual tool calls
- Dynamic tool discovery (defer_loading + search) improved accuracy from 49% to 74%

---

## MCP Auth (Our Hierarchy)

1. **Managed identity** (preferred) — zero-secret, Azure-native
2. **Entra OAuth2** — token-based, auditable
3. **API key** — last resort, must be Key Vault-sourced

---

## Canonical Fit in Our Stack

```
Anthropic engineering/blogs = workflow-pattern and skill-quality doctrine
Claude docs                = Claude-specific runtime/API surface ← THIS FILE
Claude cookbooks           = implementation examples and test fixtures
Foundry/Azure              = current hosted control/runtime plane
Repo skills/personas       = our actual bounded contracts
```

---

## Sources

- [Claude Developer Platform](https://platform.claude.com/docs/en/home)
- [Claude Cookbooks](https://github.com/anthropics/claude-cookbooks)
- [Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)
- [Advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use)
