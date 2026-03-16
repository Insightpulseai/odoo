# Skill: Azure Foundry Tool Catalog

## Metadata

| Field | Value |
|-------|-------|
| **id** | `azure-foundry-tool-catalog` |
| **domain** | `azure_foundry` |
| **source** | https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/tool-catalog |
| **extracted** | 2026-03-15 |
| **applies_to** | agents, foundry |
| **tags** | tools, mcp, openapi, function-calling, code-interpreter, web-search |

---

## Built-In Tools

| Tool | Description | Auth | Status |
|------|-------------|------|--------|
| **Web Search** | Real-time public web search with inline citations | Auto | GA |
| **Code Interpreter** | Sandboxed Python execution for data analysis, math, charts | Auto | GA |
| **Custom Code Interpreter** | Customizable resources, packages, Container Apps env | Auto | Preview |
| **File Search** | Vector search over uploaded files/proprietary docs | Auto | GA |
| **Azure AI Search** | Ground agents with existing Azure AI Search index | Connection | GA |
| **Function Calling** | Agent calls custom functions, app executes and returns result | App-managed | GA |
| **Image Generation** | Generate images in conversations | Auto | Preview |
| **Browser Automation** | Browser tasks via natural language | Auto | Preview |
| **Computer Use** | Interact with computer UIs | Auto | Preview |
| **Microsoft Fabric** | Connect to Fabric data agent for data analysis | Connection | Preview |
| **SharePoint** | Chat with private SharePoint documents | Connection | Preview |

## Custom Tools

| Tool | Description | Auth Options |
|------|-------------|--------------|
| **MCP (Model Context Protocol)** | Connect to tools on MCP server endpoints | Key, Entra (managed identity), OAuth (user passthrough) |
| **OpenAPI** | Connect to HTTP APIs via OpenAPI 3.0/3.1 spec | Anonymous, API key, Managed identity |
| **Agent-to-Agent (A2A)** | Cross-agent communication via A2A endpoints | Agent identity (preview) |

## Structured Inputs (Runtime Overrides)

Override tool config at runtime without creating new agent versions:

| Tool | Property | Use Case |
|------|----------|----------|
| `file_search` | `vector_store_ids` | Different vector stores per user |
| `code_interpreter` | `container`, `container.file_ids` | Different files per request |
| `mcp` | `server_label`, `server_url`, `headers` | Different MCP servers per env |

## MCP Authentication Methods

```python
# Key-based
tool = MCPTool(
    server_label="github",
    server_url="https://api.githubcopilot.com/mcp",
    require_approval="always",
    project_connection_id="my-github-connection",
)

# Entra managed identity — recommended
# No secrets to manage, auto token rotation

# OAuth identity passthrough — per-user auth
# Generates consent link, user authorizes on first use
```

## IPAI Tool Mapping

| Foundry Tool | IPAI Equivalent | Notes |
|-------------|-----------------|-------|
| Web Search | Deep research skill | Foundry version is built-in |
| Code Interpreter | None | Gap — useful for data analysis agents |
| File Search | Supabase pgvector + Azure AI Search | Already have this pattern |
| Function Calling | n8n webhook + Edge Function | Same pattern, different runtime |
| MCP | `agents/mcp/` servers | Foundry adds portal discovery + auth |
| A2A | Subagent delegation | Foundry adds protocol standardization |
| Browser Automation | None | Gap — useful for web scraping agents |
| SharePoint | None | Gap — useful if M365 integration needed |
