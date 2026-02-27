# AI Copilot — Product Requirements

Version: 1.0.0 | Status: Active | Last updated: 2026-02-27

## Vision

Surpass Odoo EE AI Agents + M365 Copilot + SAP Joule in Odoo 19 CE. Deliver enterprise-grade AI
assistance that any organization running Odoo CE can use without purchasing Odoo Enterprise or
third-party AI subscriptions beyond a single Gemini API key.

---

## What Odoo EE AI provides (and we must match/beat)

- EE: Top-bar Ask AI button + Ctrl+K palette (RAG agents, pgvector)
- EE: Html editor AI action (Knowledge/Discuss/email/notes)
- EE: AI fields (Studio, OpenAI only)
- EE: Voice transcription
- EE: AI server actions
- EE: AI live chat (lead generation)

---

## What M365 Copilot / SAP Joule adds (our target)

- Pervasive sidebar — always accessible from every screen
- Tool-capable — AI EXECUTES actions (create PO, confirm SO, send email)
- Cross-module awareness — understands relationships Sales↔Inventory↔Finance
- Proactive insights — surfaces "3 invoices overdue, 2 SOs pending" without being asked
- Natural language navigation — "show me overdue invoices from last quarter"
- Multi-step automation — "confirm all SOs for Acme, create picking, email customer"
- Meeting/document intelligence — summarize chatter, draft from context
- External knowledge RAG — Supabase pgvector for docs outside Odoo

---

## Objectives

### O1: Pervasive Sidebar
- ipai.copilot OWL 2 sidebar accessible from every Odoo view
- Collapsible, context-aware, keyboard shortcut Ctrl+Space
- Registered as both `main_components` (sidebar) and `systray` (toggle button)
- Context injection: current model, record ID, active_ids passed with every message
- Success metric: sidebar renders on list, form, and kanban views without page reload

### O2: Tool-Capable AI (Gemini Function Calling)
- Gemini function calling → registered Odoo tools → confirmation dialog → execute
- Core tools: search_records, read_record, create_record, update_record,
  execute_action, navigate_to, send_chatter_message, schedule_activity
- Business tools: confirm_invoice, create_payment, create_quotation, confirm_sale_order,
  check_stock, get_pipeline_summary, run_aged_receivables
- n8n tool: trigger_workflow(workflow_id, data) for cross-system automation
- Success metric: AI can create a sale order from natural language in fewer than 5 turns

### O3: Cross-Module Awareness
- Context injection: current model, record id, user, company, active_ids
- Related records: copilot resolves partner→orders→invoices→payments chain
- Success metric: on a sale.order form, copilot can answer "what's their payment history?"

### O4: Proactive Insights
- Scheduled analysis (Odoo cron) → push to ipai.copilot.insight model
- Surfaces in copilot sidebar as "Insights" tab
- Default insights: overdue invoices, low stock, deals closing this week, pending approvals
- Success metric: insights panel shows 3 or more business-relevant alerts on first load

### O5: Multi-Surface
- Sidebar (primary) — persistent panel on the right side of every view
- Command palette (Ctrl+Space) — quick action mode, overlay dialog
- Chatter compose enhancement — AI draft button in chatter composer
- Html editor integration — via OCA ai_oca_native_generate_ollama bridge
- Success metric: AI accessible from 4 or more surfaces without installing EE modules

### O6: Supabase RAG
- Embed Odoo records (products, contacts, knowledge articles) in Supabase pgvector
- Retrieval via Supabase Edge Function: match_documents(query_embedding)
- Injected into copilot context as retrieved chunks
- Success metric: copilot answers product knowledge questions from external docs

### O7: n8n Automation Bridge
- Tool: trigger_workflow(workflow_id, data) → POST to n8n webhook
- Allowlist in ssot/bridges/catalog.yaml
- HMAC signature validation for webhook security
- Success metric: AI can trigger an n8n workflow from natural language command

### O8: Surpass EE in 3 Key Areas
- Multi-provider: not locked to OpenAI+Gemini (any IPAI-supported model)
- Cross-system: n8n workflow triggering (EE AI cannot do this)
- Cost routing: simple queries → Gemini Flash, complex → Pro model

---

## Non-Requirements

- Not replacing Odoo native UI — copilot is additive only
- Not storing embeddings in Odoo PostgreSQL (Supabase pgvector only)
- Not modifying OCA modules (use _inherit overrides only)
- Not requiring Odoo Enterprise license or odoo.com IAP
- Not implementing voice transcription in v1 (future objective)

---

## Parity Matrix

| Feature | Odoo EE | M365 Copilot | SAP Joule | IPAI Copilot CE |
|---------|---------|--------------|-----------|-----------------|
| Pervasive AI panel | Partial (top bar only) | Full sidebar | Full sidebar | Full sidebar (O1) |
| Execute actions | No | Yes (M365 apps) | Yes (SAP apps) | Yes (tool registry) |
| Cross-module context | Partial | Yes | Yes | Yes (O3) |
| Proactive insights | No | Yes | Yes | Yes (O4) |
| External knowledge RAG | pgvector (EE only) | SharePoint | SAP corpus | Supabase pgvector (O6) |
| n8n automation bridge | No | No | No | Yes (O7) |
| Multi-provider LLM | No (locked) | No (Azure OpenAI) | No (SAP AI) | Yes (any IPAI model) |
| CE compatible | No | No | No | Yes — CE only |
| Cost routing | No | No | No | Flash/Pro auto-routing |

---

## Constraints

- CE only: depends on ["mail", "web", "base"] — no enterprise module dependencies
- OCA first: use OCA modules for infrastructure (no reinventing mail, discuss, etc.)
- IPAI bridge: all LLM calls go through the platform bridge (no direct API calls from Odoo)
- Secrets: GEMINI_API_KEY lives in Vercel env vars, never in Odoo DB or git
- Confirmation: all write operations require explicit user confirmation in the UI

---

## Success Criteria

1. `ipai_ai_copilot` module installs cleanly on Odoo 19 CE with `depends = ["mail","web","base"]`
2. Copilot sidebar renders on list, form, kanban views (no EE modules required)
3. Ctrl+Space opens command palette from any view
4. AI can search records and navigate to them via natural language
5. Write tools (create, update, chatter message) require and enforce confirmation dialog
6. Session history persists across same-session navigation
7. Proactive insights appear in sidebar after cron run
8. trigger_workflow tool correctly posts to allowlisted n8n webhook
