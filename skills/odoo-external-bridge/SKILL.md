# Odoo external bridge skill

Use this skill when the request involves:
- AI agents or copilot features
- RAG/retrieval or knowledge base indexing
- OCR/document extraction
- Runtime orchestration or multi-agent workflows
- External APIs (Azure, GitHub, third-party)
- Azure-native services (Foundry, AI Search, Service Bus)
- SDK/gateway work (packages/odoo-sdk, copilot-gateway)
- MCP tools or MCP server implementations

## Rules

1. **Keep heavy logic outside Odoo.** Agent runtime, MCP servers, SDK clients, LLM chains, eval frameworks — all belong in `packages/`, `apps/`, `agent-platform/`, or `mcp/servers/`.
2. **Only add thin Odoo connector surfaces if needed.** Justified patterns: thin connector, action launch point, auth/session mapping, status/result sync, minimal UI hook.
3. **Prefer external services/apps** for runtime, orchestration, retrieval, OCR, and agent execution.
4. **If atomic business behavior is required**, use a narrow server-side helper in `ipai_odoo_bridge` rather than embedding the whole system in Odoo.
5. **No SDK code in addons.** SDK libraries (copilot-sdk, azure-skills, odoo-sdk) must not be vendored, pip-installed, or imported inside `addons/ipai/` modules.

## Platform Bridge Reference

Check `ssot/azure/odoo_bridge_matrix.yaml` for:
- Which Azure services bridge which Odoo capabilities
- Which bridges are `present`, `partial`, or `missing`
- Approved external repos (Tier 1: github/copilot-sdk, microsoft/skills, microsoft/azure-skills)

## Boundary Decision Table

| Request | Correct Location | Wrong Location |
|---------|-----------------|----------------|
| LLM inference call | `packages/odoo-sdk/` or `apps/copilot-gateway/` | `addons/ipai/ipai_ai_*` |
| MCP tool function | `mcp/servers/` | `addons/ipai/` controller |
| Agent orchestration | `agent-platform/` | `addons/ipai/ipai_agent` |
| RAG pipeline | `packages/odoo-docs-kb/` | `addons/ipai/ipai_knowledge_base` |
| OCR extraction | Azure Document Intelligence or Extract API | Fat addon with CV logic |
| Webhook receiver for external event | `addons/ipai/ipai_odoo_bridge/` (thin) | OK if <50 lines |
| Odoo button that triggers external agent | `addons/ipai/ipai_*` (launch point only) | OK if thin |

## Refuse or Escalate If

- The request embeds an SDK, ML model, or agent runtime inside an Odoo addon
- The request creates an addon >200 lines for what should be an external service
- The request duplicates an existing Azure bridge capability
- The request adds MCP server logic to an Odoo controller
