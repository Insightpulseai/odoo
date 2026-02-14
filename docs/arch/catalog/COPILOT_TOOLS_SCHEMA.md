# IPAI Copilot Tools Schema

This document defines the canonical tool schema for `ipai_ask_ai` integration with the Unity Catalog-like asset registry.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         IPAI Copilot Stack                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ipai_ask_ai (OWL UI)                                              │
│       │                                                              │
│       ▼                                                              │
│   ipai_catalog_bridge (Odoo)                                        │
│       │                                                              │
│       ├──► catalog.tools (Supabase) ◄── Tool definitions            │
│       │                                                              │
│       └──► catalog-sync (Edge Function) ◄── Tool execution          │
│                   │                                                  │
│                   ├──► odoo_rpc: Odoo server actions                │
│                   ├──► edge_function: Supabase functions            │
│                   ├──► n8n_webhook: n8n workflows                   │
│                   └──► mcp_server: MCP tool calls                   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Request/Response Contract

### Copilot Request Payload

```typescript
interface CopilotRequest {
  // Context from current Odoo view
  context: {
    model: string;           // e.g., "account.move"
    res_id?: number;         // Current record ID
    res_ids?: number[];      // Selected record IDs (list view)
    view_type: string;       // "form" | "list" | "kanban"
    company_id: number;
    user_id: number;
    user_role: string;       // Odoo group XML ID
    lang: string;
  };

  // User intent
  intent: {
    mode: "ask" | "do_preview" | "apply";
    message: string;         // User's natural language query
    tool_hint?: string;      // Optional tool_key hint from UI
  };

  // Scope constraints
  scope: {
    assets?: string[];       // FQDNs to restrict context to
    time_range?: {
      start: string;         // ISO date
      end: string;
    };
    org_scope?: "company" | "global";
  };
}
```

### Copilot Response Payload

```typescript
interface CopilotResponse {
  // Conversational messages
  messages: Array<{
    role: "assistant" | "system";
    content: string;         // Markdown-formatted response
  }>;

  // Data citations
  citations: Array<{
    fqdn: string;            // Asset FQDN
    uri: string;             // Deep link URL
    title: string;           // Display title
    snippet?: string;        // Relevant excerpt
  }>;

  // Proposed actions (for do_preview mode)
  actions: Array<{
    tool_key: string;        // e.g., "odoo.post_invoice"
    name: string;            // Human-readable action name
    args: Record<string, unknown>;
    preview_diff?: {
      before: Record<string, unknown>;
      after: Record<string, unknown>;
    };
    requires_confirm: boolean;
    status: "pending" | "approved" | "executed" | "failed";
  }>;

  // Audit trail
  run_id: string;            // Links to ops.runs table
  model_used: string;        // LLM model name
  tokens_used: number;
}
```

## Tool Definition Schema

Tools are defined in `catalog.tools` using OpenAPI-compatible schemas:

```json
{
  "tool_key": "odoo.create_record",
  "tool_type": "action",
  "name": "Create Odoo Record",
  "description": "Create a new record in any Odoo model. Use this when the user wants to create a new invoice, partner, expense, or other business object.",
  "parameters": {
    "type": "object",
    "properties": {
      "model": {
        "type": "string",
        "description": "Odoo model name (e.g., 'account.move', 'res.partner')"
      },
      "values": {
        "type": "object",
        "description": "Field values for the new record"
      }
    },
    "required": ["model", "values"]
  },
  "returns": {
    "type": "object",
    "properties": {
      "id": { "type": "integer", "description": "New record ID" },
      "display_name": { "type": "string" }
    }
  },
  "requires_confirmation": true,
  "allowed_roles": ["base.group_user"],
  "tags": ["odoo", "create", "write"]
}
```

## Tool Categories

### Query Tools (Read-Only)

| Tool Key | Description | Parameters |
|----------|-------------|------------|
| `catalog.search_assets` | Search for data assets | query, asset_type, system |
| `odoo.search_records` | Search Odoo records | model, domain, fields, limit |
| `odoo.read_record` | Read a specific record | model, id, fields |
| `scout.query_analytics` | Query Scout gold views | view, filters, group_by, limit |

### Action Tools (Write)

| Tool Key | Description | Requires Confirm |
|----------|-------------|------------------|
| `odoo.create_record` | Create new record | Yes |
| `odoo.update_record` | Update existing record | Yes |
| `odoo.execute_action` | Run server action | Yes |
| `odoo.post_invoice` | Post draft invoice | Yes |
| `odoo.register_payment` | Register payment | Yes |
| `odoo.approve_expense` | Approve expense report | Yes |

### Navigation Tools

| Tool Key | Description |
|----------|-------------|
| `odoo.open_record` | Generate deep link to record |
| `odoo.open_action` | Navigate to menu action |

## Tool Binding Configuration

Each tool maps to an execution target via `catalog.tool_bindings`:

### Odoo RPC Binding

```json
{
  "target_type": "odoo_rpc",
  "target_config": {
    "model": "account.move",
    "method": "action_post",
    "endpoint": "/web/dataset/call_kw"
  }
}
```

### Edge Function Binding

```json
{
  "target_type": "edge_function",
  "target_config": {
    "function_name": "three-way-match",
    "action": "validate"
  }
}
```

### n8n Webhook Binding

```json
{
  "target_type": "n8n_webhook",
  "target_config": {
    "webhook_url": "https://n8n.example.com/webhook/abc123",
    "workflow_id": "wf_123"
  }
}
```

### MCP Server Binding

```json
{
  "target_type": "mcp_server",
  "target_config": {
    "server_name": "odoo-erp-server",
    "tool_name": "create_record"
  }
}
```

## FQDN Conventions

| Pattern | Example | Description |
|---------|---------|-------------|
| `odoo.<db>.<model>` | `odoo.odoo_core.account.move` | Odoo model |
| `odoo.<db>.action.<xmlid>` | `odoo.odoo_core.action.account.action_move_out_invoice_type` | Odoo action |
| `supabase.<project>.<schema>.<object>` | `supabase.ipai.scout_gold.sales_by_store` | Supabase table/view |
| `scout.<layer>.<object>` | `scout.gold.customer_360` | Scout analytics view |
| `uc.<catalog>.<schema>.<table>` | `uc.main.default.transactions` | Unity Catalog (future) |

## Integration with ipai_ask_ai

### Python Service

```python
# In ipai_ask_ai/models/llm_client.py

def get_tools_for_context(self, context):
    """Get relevant tools based on current context."""
    CatalogTool = self.env["ipai.catalog.tool"]

    # Filter tools by context
    tags = ["odoo"]
    if context.get("model"):
        model_prefix = context["model"].split(".")[0]
        tags.append(model_prefix)

    return CatalogTool.get_tools_for_copilot(tags=tags)

def execute_tool(self, tool_key, args, context):
    """Execute a tool and return result."""
    CatalogSync = self.env["ipai.catalog.sync"]
    client = CatalogSync.get_catalog_client()

    # Get binding
    binding = client.get_tool_binding(tool_key)
    if not binding.get("ok"):
        return {"ok": False, "error": binding.get("error")}

    # Execute based on target type
    target_type = binding["binding"]["target_type"]
    target_config = binding["binding"]["target_config"]

    if target_type == "odoo_rpc":
        return self._execute_odoo_rpc(target_config, args, context)
    elif target_type == "edge_function":
        return self._execute_edge_function(target_config, args)
    # ... etc
```

### JavaScript Integration (OWL)

```javascript
// In ipai_ask_ai/static/src/js/ask_ai_chat.js

async getAvailableTools() {
    const result = await this.rpc("/ipai/catalog/tools", {
        tags: ["odoo", this.props.resModel?.split(".")[0]].filter(Boolean)
    });
    return result.ok ? result.tools : [];
}

async previewAction(toolKey, args) {
    const result = await this.rpc("/ipai/ask_ai/preview_action", {
        tool_key: toolKey,
        args: args,
        context: this.getContext()
    });

    if (result.ok && result.preview_diff) {
        // Show diff dialog
        this.showPreviewDialog(result.preview_diff);
    }

    return result;
}
```

## Security Considerations

1. **Role-Based Access**: Tools define `allowed_roles`; copilot checks before execution
2. **Preview Pattern**: Write operations require user confirmation
3. **Audit Trail**: All tool executions logged to `ops.runs`
4. **RLS Enforcement**: Supabase RLS applied to catalog queries
5. **Token Scoping**: Service role keys only used server-side

## Example Flows

### Ask Mode (Read-Only)

```
User: "What invoices are overdue?"

1. ipai_ask_ai receives query
2. Calls catalog.search_assets for relevant models
3. Calls odoo.search_records with domain [('state','=','posted'),('payment_state','=','not_paid'),('invoice_date_due','<',today)]
4. LLM generates summary
5. Returns response with citations
```

### Do Preview Mode

```
User: "Post invoice INV/2024/0001"

1. ipai_ask_ai identifies intent: post_invoice
2. Gets tool: odoo.post_invoice
3. Calls preview: shows before/after state
4. User confirms
5. Executes action
6. Returns success with citation
```

## Versioning

- Schema version: `1.0.0`
- Migration path: Tools are additive; deprecate via `active=false`
- Breaking changes require new tool_key
