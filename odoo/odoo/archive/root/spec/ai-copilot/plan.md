# AI Copilot — Implementation Plan

Version: 1.0.0 | Status: Active | Last updated: 2026-02-27

## Architecture Overview

```
Browser (OWL 2)                 Odoo Controller              IPAI Bridge (Vercel)
─────────────────               ─────────────────            ────────────────────
CopilotSidebar                  /ipai/copilot/chat           POST /api/ai/gemini/tools
CopilotPalette       ────────►  context_injection()  ──────► Gemini function calling
CopilotToggle                   tool_dispatch()              ▼
                    ◄────────   confirmation_required()      Tool declarations
                                execute_tool()     ◄──────── Tool call response
                                session._append()
                                                   ──────►  Plain text response
ipai.copilot.session            ipai.copilot.tool
ipai.copilot.insight            ipai.copilot.session
```

## Phase 1: Foundation

**Goal**: Working addon shell with sidebar that communicates with bridge.

### 1.1 Addon Scaffold
- `addons/ipai/ipai_ai_copilot/__manifest__.py` — CE-only, depends: mail, web, base
- `addons/ipai/ipai_ai_copilot/__init__.py` — import controllers, models
- `addons/ipai/ipai_ai_copilot/security/ir.model.access.csv` — access rules
- `addons/ipai/ipai_ai_copilot/data/copilot_tools.xml` — seed 8 default tools

### 1.2 Session Model
- `models/copilot_session.py` — `ipai.copilot.session`
  - Fields: name, user_id, history_json (JSON), active
  - Methods: `_get_or_create(session_id)`, `_get_history(max_turns=50)`, `_append(role, content)`
  - Max 50 turns with FIFO truncation

### 1.3 Copilot Controller
- `controllers/copilot.py` — `IpaiCopilotController`
  - POST `/ipai/copilot/chat` — main conversational endpoint
  - POST `/ipai/copilot/execute_tools` — confirmed tool execution
  - GET `/ipai/copilot/insights` — proactive insights for sidebar
  - GET `/ipai/copilot/tools` — tool list for UI display
  - Error codes: BRIDGE_URL_NOT_CONFIGURED, AI_KEY_NOT_CONFIGURED, BRIDGE_TIMEOUT, etc.

### 1.4 Copilot Sidebar (OWL 2)
- `static/src/js/copilot_service.js` — reactive service, registered as "ipai_copilot"
  - state: open, loading, messages, insights, sessionId, currentContext
  - methods: sendMessage, confirmTools, loadInsights, setContext, toggle
- `static/src/js/copilot_sidebar.js` — CopilotSidebar component
  - Registered in `main_components` registry
  - CopilotToggle registered in `systray` registry (sequence: 5)
- `static/src/xml/copilot_sidebar.xml` — sidebar + toggle templates
- `static/src/css/copilot.css` — sidebar, typing indicator, message bubbles

## Phase 2: Tool Engine

**Goal**: Gemini function calling → tools → confirmation → execution.

### 2.1 Tool Registry Model
- `models/copilot_tool.py` — `ipai.copilot.tool`
  - Fields: name (snake_case), display_name, description, category, parameters_json, active, requires_confirmation
  - Method: `_to_gemini_declaration()` → Gemini function calling format

### 2.2 Gemini Tools Bridge
- `platform/ai/providers/gemini_tools.ts` — `generateWithTools(payload)`
  - Accepts `tools: GeminiToolDeclaration[]`
  - Uses `FunctionCallingMode.AUTO` for automatic tool detection
  - MODEL_PRO for tool-heavy queries, MODEL_FAST for simple messages
  - Returns `{text?, tool_calls?, provider, model, trace_id}`
- `apps/ops-console/app/api/ai/gemini/tools/route.ts` — Next.js API route
  - POST handler wrapping `generateWithTools`
  - 503 on missing GEMINI_API_KEY

### 2.3 Tool Execution
- `_dispatch_tool(name, args)` — read-only preview for confirmation display
- `_execute_tool_confirmed(name, args)` — actual execution after user confirms
- Core tools implemented: search_records, read_record, navigate_to, create_record,
  update_record, send_chatter_message, schedule_activity, trigger_workflow

### 2.4 Confirmation Dialog
- `static/src/xml/copilot_sidebar.xml` — tool_confirmation message type
  - Shows tool name + human-readable preview of each action
  - "Confirm" button → calls `/ipai/copilot/execute_tools`
  - "Cancel" button → sets `msg.dismissed = true`

## Phase 3: Business Tools

**Goal**: Finance, Sales, Inventory, HR tools for common ERP workflows.

### 3.1 Finance Tools
- `confirm_invoice(invoice_id)` — validate draft invoice → action_post()
- `create_payment(invoice_id, amount, journal_id)` — register payment
- `run_aged_receivables()` — return aged receivable summary
- All require confirmation; respect user's account group membership

### 3.2 Sales Tools
- `create_quotation(partner_id, order_lines)` — draft sale.order
- `confirm_sale_order(order_id)` — action_confirm()
- `get_pipeline_summary()` — active leads grouped by stage

### 3.3 Inventory Tools
- `check_stock(product_id, location_id)` — current on-hand quantity
- `create_transfer(picking_type_id, move_lines)` — draft stock.picking

### 3.4 HR Tools
- `get_employee_info(employee_id)` — name, department, job_title, manager
- `create_leave_request(employee_id, leave_type_id, date_from, date_to)` — draft hr.leave

## Phase 4: Proactive Insights

**Goal**: Background analysis → push to sidebar "Insights" tab.

### 4.1 Insight Model
- `models/copilot_insight.py` — `ipai.copilot.insight`
  - Fields: title, body, category, priority, date, user_id, action_model, action_domain, dismissed
  - Method: `_to_dict()` for JSON serialization

### 4.2 Cron Jobs
- `data/copilot_cron.xml` — `run_proactive_insights` (daily at 06:00)
- Default insight rules:
  - Overdue invoices (account.move): amount_residual > 0, invoice_date_due < today
  - Low stock (product.product): qty_available < reorder_point
  - Deals closing this week (crm.lead): date_deadline within 7 days, stage not won/lost
  - Pending approvals (hr.leave): state = 'validate1'

### 4.3 Sidebar Integration
- "Insights" tab in sidebar shows `state.insights`
- Badge count on tab button showing number of active insights
- Priority-colored left border (red=critical, yellow=important, blue=normal)
- "Ask Copilot →" link sends insight title to chat for follow-up

## Phase 5: Supabase RAG

**Goal**: External document knowledge injected into copilot context.

### 5.1 Supabase Edge Function
- `supabase/functions/match_copilot_documents/index.ts`
  - Accepts: `{query_embedding: number[], match_count: number}`
  - Returns: `{documents: [{content, similarity, source}]}`
  - Uses pgvector `<=>` operator for cosine similarity

### 5.2 n8n Sync Workflow
- `automations/n8n/workflows/odoo_copilot_embed_records.json`
  - Trigger: webhook or schedule
  - Steps: fetch Odoo records → generate embeddings (Gemini) → upsert to Supabase pgvector
  - Record types: product.product, res.partner, knowledge.article

### 5.3 Context Injection
- Controller: before bridge call, retrieve relevant chunks via Supabase Edge Function
- Append to context string: "Relevant knowledge: [chunk1] [chunk2]..."
- Chunks are top-k by cosine similarity to user's current message

## Phase 6: n8n Automation Bridge

**Goal**: AI can trigger real n8n workflows from natural language.

### 6.1 trigger_workflow Tool
- Tool registered in `data/copilot_tools.xml` with `requires_confirmation=True`
- `_execute_tool_confirmed("trigger_workflow", {workflow_id, data})`
  - Looks up webhook URL: `ir.config_parameter:ipai_ai_copilot.n8n_webhook.<workflow_id>`
  - HMAC validation using `ipai_ai_copilot.n8n_secret` parameter
  - Returns status code from n8n webhook

### 6.2 Allowlist Management
- `ssot/bridges/catalog.yaml` — register n8n workflows that can be triggered
- Each workflow entry: name, display_name, webhook_id, description
- CI validation: check_parity_and_bridges_ssot.py validates catalog.yaml schema

### 6.3 Security
- `ipai_ai_copilot.n8n_secret` ir.config_parameter → HMAC-SHA256 signature
- Signature appended as `X-IPAI-Signature` header
- n8n webhook validates signature via Code node

---

## Delivery Sequence

```
Commit 1: feat(spec): add ai-copilot spec bundle
  → spec/ai-copilot/{constitution,prd,plan,tasks}.md

Commit 2: feat(ipai): add ipai_ai_copilot addon
  → addons/ipai/ipai_ai_copilot/ (all Python, XML, CSV)
  → static/src/ (JS, XML, CSS)

Commit 3: feat(platform): add gemini_tools bridge
  → platform/ai/providers/gemini_tools.ts
  → apps/ops-console/app/api/ai/gemini/tools/route.ts

Commit 4: chore(ssot): register ipai_ai_copilot bridge + contract doc
  → ssot/bridges/catalog.yaml (append)
  → docs/contracts/AI_COPILOT_CONTRACT.md (new)
```

---

## Dependency Matrix

| Component | Depends On | Notes |
|-----------|-----------|-------|
| CopilotSidebar | copilotService | OWL 2 useService hook |
| copilotService | rpc, notification | Odoo core services |
| /ipai/copilot/chat | ipai.copilot.session, ipai.copilot.tool | Session + tool registry |
| ipai.copilot.session | res.users | Per-user sessions |
| ipai.copilot.tool | — | Self-contained registry |
| gemini_tools.ts | @google/generative-ai | Platform dep |
| route.ts | gemini_tools.ts | Thin API wrapper |
| trigger_workflow | n8n webhook URL | ir.config_parameter |
