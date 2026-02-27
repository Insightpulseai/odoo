# AI Copilot Contract — ipai_ai_copilot

Version: 1.0.0 | Status: planned | Created: 2026-02-27

## Identity

- Bridge: `ipai_ai_copilot`
- Replaces: Odoo EE AI Agents + M365 Copilot + SAP Joule
- Status: planned → active on deployment
- Spec: `spec/ai-copilot/` (constitution, prd, plan, tasks)

---

## Architecture

```
Browser (OWL 2 sidebar/palette)
         ↕ rpc
Odoo controller (/ipai/copilot/chat, /ipai/copilot/execute_tools)
         ↕ HTTP POST (requests library, 30s timeout)
IPAI Bridge — POST /api/ai/gemini/tools (ops-console Next.js on Vercel)
         ↕ @google/generative-ai SDK
Gemini API (function calling with FunctionCallingMode.AUTO)
         ↓ tool_calls or text
Odoo controller → tool dispatch → user confirmation → execute_tool_confirmed
         ↓
Odoo ORM (request.env — user access rights always enforced)
```

---

## Endpoint Contract

### POST /api/ai/gemini/tools

**Request** (Content-Type: application/json):

```json
{
  "system_prompt": "string (optional)",
  "context": "string (optional) — current model, record_id, user info",
  "history": [
    { "role": "user|assistant", "content": "string" }
  ],
  "message": "string (required)",
  "tools": [
    {
      "name": "string — snake_case tool name",
      "description": "string — sent to Gemini as function description",
      "parameters": { "type": "object", "properties": {}, "required": [] }
    }
  ]
}
```

**Response — plain text**:

```json
{
  "text": "string",
  "provider": "google",
  "model": "gemini-2.0-flash-preview | gemini-1.5-pro-latest",
  "trace_id": "uuid"
}
```

**Response — tool call**:

```json
{
  "tool_calls": [
    { "name": "search_records", "args": { "model": "sale.order", "query": "Acme" } }
  ],
  "provider": "google",
  "model": "gemini-1.5-pro-latest",
  "trace_id": "uuid"
}
```

---

## Error Codes

| Code | HTTP Status | Meaning |
|------|------------|---------|
| `AI_KEY_NOT_CONFIGURED` | 503 | `GEMINI_API_KEY` env var missing in Vercel deployment |
| `BRIDGE_URL_NOT_CONFIGURED` | 503 | `ipai_ai_copilot.bridge_url` ir.config_parameter missing in Odoo |
| `BRIDGE_TIMEOUT` | 504 | Bridge did not respond within 30 seconds |
| `BRIDGE_ERROR` | 500 | Non-2xx response from bridge |
| `TOOL_EXECUTION_FAILED` | 500 | Tool function raised an unhandled exception |
| `ACCESS_DENIED` | 403 | User lacks Odoo access rights for the tool action |
| `MESSAGE_REQUIRED` | 400 | Empty or missing message field |

---

## Configuration

### Odoo ir.config_parameter

| Key | Value | Purpose |
|-----|-------|---------|
| `ipai_ai_copilot.bridge_url` | `https://ops.insightpulseai.com/api/ai/gemini/tools` | IPAI bridge endpoint |
| `ipai_ai_copilot.n8n_webhook.<workflow_id>` | `https://n8n.insightpulseai.com/webhook/<uuid>` | n8n workflow webhook URL (per workflow) |
| `ipai_ai_copilot.n8n_secret` | `<hmac_secret>` | HMAC signing secret for n8n webhook requests |

### Vercel Environment Variables

| Variable | Source | Purpose |
|----------|--------|---------|
| `GEMINI_API_KEY` | ssot/secrets/registry.yaml#gemini_api_key | Google AI Studio API key |

---

## Tool Confirmation Requirement

All tools with `requires_confirmation = True` in `ipai.copilot.tool` MUST:

1. Return a `tool_confirmation` response from `/ipai/copilot/chat` (not execute immediately)
2. Display a confirmation dialog in the OWL sidebar showing exactly what will happen
3. Only execute via `/ipai/copilot/execute_tools` after explicit user clicks "Confirm"
4. Support "Cancel" which sets `dismissed = True` without execution

**Tools requiring confirmation** (as seeded in `data/copilot_tools.xml`):
- `create_record`, `update_record` — write any model
- `send_chatter_message` — post to chatter
- `schedule_activity` — create activity
- `confirm_invoice` — validate/post invoice
- `create_quotation` — draft sale order
- `confirm_sale_order` — confirm sale order
- `trigger_workflow` — trigger n8n webhook

---

## Security Model

### Access Control
- All tool executions use `request.env` (authenticated user context)
- Odoo record rules (`ir.rule`) and model access (`ir.model.access`) are enforced automatically
- Users cannot access records they do not have permission to view/edit
- `sudo()` is used only for tool registry and config parameter lookups, not for data operations

### n8n Webhook Security
- Webhook URLs are stored in `ir.config_parameter`, not in source code
- Workflow IDs must be registered in `ssot/bridges/catalog.yaml` (allowlist)
- Requests are signed with HMAC-SHA256 using `ipai_ai_copilot.n8n_secret`
- Signature sent as `X-IPAI-Signature: sha256=<hex>` header

### Confirmation Gate
- Frontend CopilotSidebar shows confirmation dialog for all write tools
- Dialog displays human-readable preview of each action (from `_dispatch_tool_preview`)
- Write tools never execute directly from `/ipai/copilot/chat` — only from `/ipai/copilot/execute_tools`

---

## Model Routing

| Condition | Model | Rationale |
|-----------|-------|-----------|
| No tools in payload | `gemini-2.0-flash-preview` | Cost-optimised for simple queries |
| Tools present in payload | `gemini-1.5-pro-latest` | Better function calling accuracy |

---

## Surpasses EE AI Agents In

| Capability | Odoo EE AI | IPAI Copilot CE |
|-----------|------------|-----------------|
| Multi-provider LLM | Locked to OpenAI/Gemini | Any IPAI-supported model |
| Cross-system automation | No | n8n workflow triggering via `trigger_workflow` tool |
| Provider cost routing | No | Flash (simple) / Pro (tools) auto-routing |
| External knowledge RAG | pgvector (EE-only DB) | Supabase pgvector (external, scalable) |
| Extensible tool registry | Not extensible by CE modules | `ipai.copilot.tool` — any module can register tools |
| CE compatible | No — requires Enterprise license | Yes — depends only on mail, web, base |

---

## Testing Checklist

```
□ POST /api/ai/gemini/tools with tools array → returns tool_calls or text
□ POST /api/ai/gemini/tools without GEMINI_API_KEY → 503 AI_KEY_NOT_CONFIGURED
□ Missing message field → 400 MESSAGE_REQUIRED
□ Tool execution without confirmation → BLOCKED by UI (execute_tools never called)
□ Ctrl+Space opens command palette from list, form, kanban views
□ Sidebar renders and persists across intra-app navigation
□ Session history persists within a session (not across page reload)
□ Proactive insights appear after running _run_proactive_insights() manually
□ trigger_workflow with unlisted workflow_id → error "not in allowlist"
□ All write tools show confirmation dialog before executing
□ Module installs cleanly on Odoo 19 CE (no EE deps): pip install odoo-module-check
```

---

## Change Log

| Date | Version | Change |
|------|---------|--------|
| 2026-02-27 | 1.0.0 | Initial contract created |
