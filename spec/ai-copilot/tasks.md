# AI Copilot — Task Breakdown

Version: 1.0.0 | Status: Active | Last updated: 2026-02-27

## Phase 1: Foundation

### T-01: Create addon manifest and __init__ files
- Create `addons/ipai/ipai_ai_copilot/__manifest__.py` with CE-only dependencies
- Create `addons/ipai/ipai_ai_copilot/__init__.py` importing controllers and models
- Create `addons/ipai/ipai_ai_copilot/controllers/__init__.py`
- Create `addons/ipai/ipai_ai_copilot/models/__init__.py`
- Acceptance: module imports cleanly, manifest validates with Odoo module validator

### T-02: Create session model (ipai.copilot.session)
- Create `models/copilot_session.py`
- Fields: name (Char), user_id (Many2one res.users), history_json (Text), active (Boolean)
- Methods: `_get_or_create`, `_get_history(max_turns=50)`, `_append(role, content)`
- 50-turn FIFO truncation enforced in `_append`
- Acceptance: session creates on first message, history persists and truncates at 50

### T-03: Create tool model (ipai.copilot.tool)
- Create `models/copilot_tool.py`
- Fields: name, display_name, description, category (selection), parameters_json, active, requires_confirmation
- Method: `_to_gemini_declaration()` returns Gemini function calling format dict
- Acceptance: `_to_gemini_declaration()` matches Gemini API spec

### T-04: Create insight model (ipai.copilot.insight)
- Create `models/copilot_insight.py`
- Fields: title, body, category, priority, date, user_id, action_model, action_domain, dismissed
- Method: `_to_dict()` returns JSON-serializable dict
- Acceptance: model installs, insights can be created and queried

### T-05: Create main copilot controller
- Create `controllers/copilot.py`
- Implement POST `/ipai/copilot/chat` endpoint
- Implement POST `/ipai/copilot/execute_tools` endpoint
- Implement GET `/ipai/copilot/insights` endpoint
- Implement GET `/ipai/copilot/tools` endpoint
- Error handling: all 6 error codes (BRIDGE_URL_NOT_CONFIGURED, AI_KEY_NOT_CONFIGURED, BRIDGE_TIMEOUT, TOOL_EXECUTION_FAILED, ACCESS_DENIED, MESSAGE_REQUIRED)
- Acceptance: each endpoint returns correct structure, errors return expected codes

### T-06: Implement tool dispatch and execution
- Implement `_dispatch_tool(name, args)` preview function (read-only)
- Implement `_execute_tool_confirmed(name, args)` execution function
- Core tools: search_records, read_record, navigate_to, create_record, update_record, send_chatter_message, schedule_activity, trigger_workflow
- Acceptance: each tool returns correct data or action; errors bubble correctly

### T-07: Create security access rules
- Create `security/ir.model.access.csv`
- Access rules for: ipai.copilot.session (user: rw create), ipai.copilot.tool (user: r, admin: rwcd), ipai.copilot.insight (user: r, admin: rwcd)
- Acceptance: non-admin users can read tools and insights but not create/modify them

### T-08: Create default tool seed data
- Create `data/copilot_tools.xml` with 8 default tools:
  - search_records, read_record, navigate_to (category: read/navigation, no confirmation)
  - create_record, update_record, send_chatter_message, schedule_activity (category: write, confirmation required)
  - trigger_workflow (category: automation, confirmation required)
- Each tool includes full JSON Schema for parameters
- Acceptance: tools install with `noupdate="1"`, appear in tools endpoint

## Phase 2: OWL 2 Frontend

### T-09: Create copilot service (copilot_service.js)
- Implement reactive service using `@odoo/owl reactive`
- state: {open, loading, messages, insights, sessionId, currentContext}
- Methods: sendMessage (calls /ipai/copilot/chat), confirmTools (calls /ipai/copilot/execute_tools), loadInsights (calls /ipai/copilot/insights), setContext, toggle
- Register as "ipai_copilot" in `registry.category("services")`
- Acceptance: service starts, state is reactive, RPC calls work

### T-10: Create copilot sidebar component (copilot_sidebar.js)
- CopilotSidebar: useService("ipai_copilot"), two tabs (Chat/Insights)
- Chat tab: message list with user/assistant bubbles, typing indicator, input area
- Insights tab: insight cards with priority borders
- Tool confirmation: shows tool previews, Confirm/Cancel buttons
- CopilotToggle: systray button, sequence 5
- Register CopilotSidebar in `main_components`, CopilotToggle in `systray`
- Acceptance: sidebar renders, tabs switch, messages display, toggle works

### T-11: Create command palette component (copilot_palette.js)
- CopilotPalette: overlay modal triggered by Ctrl+Space hotkey
- Uses `useHotkey("control+space", ...)` from @web/core/hotkeys/hotkey_hook
- Input field, Enter submits → opens sidebar and sends message
- Escape closes overlay
- Register in `main_components`
- Acceptance: Ctrl+Space opens palette from any view, Enter submits message

### T-12: Create sidebar XML template (copilot_sidebar.xml)
- CopilotToggle template: systray button with fa-magic icon
- CopilotSidebar template: header with tabs, chat messages area, input area
- Message types: regular (user/assistant), tool_confirmation (with confirm/cancel buttons), tool_result
- Insights tab: priority-colored cards with "Ask Copilot" action links
- Empty state: suggested starter questions as buttons
- Acceptance: template renders without errors, all conditional blocks work

### T-13: Create palette XML template (copilot_palette.xml)
- Overlay with semi-transparent backdrop
- Centered card with large text input
- Keyboard shortcut hints
- Acceptance: template renders, backdrop click closes, Enter submits

### T-14: Create copilot CSS styles (copilot.css)
- Sidebar: fixed right panel, 360px width, below navbar (top: 46px)
- Message bubbles: user (blue-tinted, right-aligned), assistant (gray, left-aligned)
- Typing indicator: 3-dot bounce animation
- Command palette: centered overlay, blur backdrop, 600px wide card
- Systray toggle button styling
- Acceptance: sidebar does not overlap Odoo navbar, message bubbles are readable

## Phase 3: Platform Bridge

### T-15: Create gemini_tools.ts provider
- Create `platform/ai/providers/gemini_tools.ts`
- Implement `generateWithTools(payload: CopilotPayload): Promise<CopilotResponse>`
- MODEL_PRO for tool-enabled requests, MODEL_FAST for plain queries
- FunctionCallingMode.AUTO for automatic tool invocation
- trace_id: crypto.randomUUID()
- Acceptance: returns {text} for plain response, {tool_calls} when AI invokes a tool

### T-16: Create Next.js API route for gemini tools
- Create `apps/ops-console/app/api/ai/gemini/tools/route.ts`
- POST handler: validate message field, call generateWithTools, return result
- 503 on missing GEMINI_API_KEY
- maxDuration: 60 (Vercel Pro function timeout)
- Acceptance: curl POST with tools payload returns correct response; missing key returns 503

## Phase 4: Proactive Insights

### T-17: Create cron job for insights analysis
- Create `data/copilot_cron.xml`
- Cron model: ir.cron
- Method: `ipai.copilot.insight._run_proactive_insights()`
- Schedule: daily at 06:00 UTC
- Acceptance: cron job appears in Settings > Technical > Automation > Scheduled Actions

### T-18: Implement default insight rules in model
- Add `_run_proactive_insights()` class method to `ipai.copilot.insight`
- Rule 1: Overdue invoices — account.move with amount_residual > 0 and invoice_date_due < today
- Rule 2: Low stock — product.product with qty_available < 5 (configurable)
- Rule 3: Deals closing this week — crm.lead within 7 days, not won/lost
- Rule 4: Pending approvals — hr.leave in validate1 state
- Each rule creates/updates an insight record, avoiding duplicates
- Acceptance: running cron manually creates insight records for matching data

## Phase 5: SSOT and Contract

### T-19: Update ssot/bridges/catalog.yaml
- Append ipai_ai_copilot bridge entry with all required fields
- Include: capabilities list, endpoints (generate + tools), secrets list
- Acceptance: `python3 scripts/ci/check_parity_and_bridges_ssot.py` exits 0

### T-20: Create AI_COPILOT_CONTRACT.md
- Create `docs/contracts/AI_COPILOT_CONTRACT.md`
- Include: endpoint contract, request/response schemas, error codes, configuration
- Include: tool confirmation requirement, security model
- Include: comparison table showing where copilot surpasses EE
- Acceptance: file exists, is well-formed markdown

### T-21: Register contract in PLATFORM_CONTRACTS_INDEX.md
- Add row for AI_COPILOT_CONTRACT.md to `docs/contracts/PLATFORM_CONTRACTS_INDEX.md`
- Acceptance: index updated with correct path and description

## Phase 6: Validation and Packaging

### T-22: Create models/__init__.py with all imports
- Import: copilot_session, copilot_tool, copilot_insight
- Acceptance: `from odoo.addons.ipai_ai_copilot import models` imports cleanly

### T-23: Validate CI scripts
- Run `python3 scripts/ci/check_parity_and_bridges_ssot.py`
- Run `python3 scripts/ci/check_secrets_ssot.py`
- Acceptance: both scripts exit 0

### T-24: Git commits and PR
- Commit 1: feat(spec): add ai-copilot spec bundle (constitution/prd/plan/tasks)
- Commit 2: feat(ipai): add ipai_ai_copilot addon (Gemini function calling + sidebar + tool registry)
- Commit 3: feat(platform): add gemini_tools bridge (function calling endpoint)
- Commit 4: chore(ssot): register ipai_ai_copilot bridge + contract doc
- Push: git push -u origin feat/ai-copilot
- PR: title "feat(ipai): IPAI AI Copilot — M365/SAP Joule-class AI for Odoo 19 CE"
- Acceptance: PR opens, all commits visible, CI starts

---

## Task Status Matrix

| Task | Phase | Status | Blocker |
|------|-------|--------|---------|
| T-01 | 1 | pending | none |
| T-02 | 1 | pending | T-01 |
| T-03 | 1 | pending | T-01 |
| T-04 | 1 | pending | T-01 |
| T-05 | 1 | pending | T-02, T-03, T-04 |
| T-06 | 1 | pending | T-05 |
| T-07 | 1 | pending | T-01 |
| T-08 | 1 | pending | T-03 |
| T-09 | 2 | pending | T-05 |
| T-10 | 2 | pending | T-09 |
| T-11 | 2 | pending | T-09 |
| T-12 | 2 | pending | T-10 |
| T-13 | 2 | pending | T-11 |
| T-14 | 2 | pending | T-10, T-11 |
| T-15 | 3 | pending | none |
| T-16 | 3 | pending | T-15 |
| T-17 | 4 | pending | T-04 |
| T-18 | 4 | pending | T-17 |
| T-19 | 5 | pending | none |
| T-20 | 5 | pending | none |
| T-21 | 5 | pending | T-20 |
| T-22 | 6 | pending | T-02, T-03, T-04 |
| T-23 | 6 | pending | T-19 |
| T-24 | 6 | pending | T-23 |
