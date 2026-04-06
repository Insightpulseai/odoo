# Skill Pack: Copilot & Agent Architecture for ERP

## Scope

AI copilot and autonomous agent patterns for enterprise resource planning: document
intelligence, MCP (Model Context Protocol) tool integration, agent governance,
prompt engineering for business context, and safe automation of ERP workflows.
Targets capabilities analogous to SAP Joule, Microsoft Copilot for Dynamics 365,
and Oracle AI Agents -- built on Odoo 18 CE + Azure AI Foundry + MCP.

---

## Concepts

| Concept | SAP/Industry Equivalent | IPAI Platform Surface |
|---------|------------------------|----------------------|
| ERP Copilot | SAP Joule | Odoo Ask AI + `ipai_ai_copilot` |
| Document Extraction | SAP Document Information Extraction | Azure Document Intelligence |
| Agent Tool | SAP BTP Destination / API | MCP Tool Server |
| Agent Governance | SAP AI Core guardrails | Agent passport + Foundry safety |
| Prompt Template | Joule Skill | Prompt registry in `ipai_ai_copilot` |
| Workflow Trigger | SAP Intelligent RPA | Odoo `base.automation` + agent action |
| Knowledge Grounding | SAP HANA Vector Engine | Azure AI Search + pgvector |
| Agent Identity | SAP BTP Service Binding | Entra Agent ID (Managed Identity) |

---

## Must-Know Vocabulary

- **MCP (Model Context Protocol)**: Open protocol (Anthropic) for connecting AI models
  to external tools and data sources. Defines tool schemas, invocation patterns, and
  context windows. Replaces bespoke API integrations with a standard interface.
- **Agent Passport**: Metadata document defining an agent's identity, capabilities,
  allowed tools, rate limits, and audit requirements. Stored in agent registry.
- **Tool Server**: An MCP-compliant service exposing tools (functions) that agents
  can invoke. Example: an Odoo MCP server exposing `create_invoice`, `search_partner`.
- **Grounding**: Providing factual context (retrieved documents, DB records) to an
  LLM to reduce hallucination. Essential for ERP where accuracy is non-negotiable.
- **Document Intelligence**: Azure service for extracting structured data from
  documents (invoices, receipts, BIR forms). Pre-built and custom models.
- **Copilot**: Interactive AI assistant that suggests actions but requires human
  confirmation. Contrasted with autonomous agents that execute independently.
- **Autonomous Agent**: AI that plans and executes multi-step workflows without
  human-in-the-loop. Requires strict governance in ERP context.
- **Prompt Registry**: Version-controlled collection of prompt templates mapped to
  ERP operations. Ensures consistent, tested prompts across agent interactions.
- **A2A (Agent-to-Agent)**: Protocol for agents communicating with each other.
  Example: document extraction agent passes structured data to AP processing agent.

---

## Core Workflows

### 1. Copilot-Assisted Record Creation

Flow: User describes intent in natural language -> Copilot translates to Odoo action.

```
User: "Create an invoice for Acme Corp, 10 units of Widget A at 500 each,
       due in 30 days, apply 12% VAT"

Copilot resolves:
  - partner_id: search res.partner where name ilike 'Acme%' -> id=42
  - product_id: search product.product where name ilike 'Widget A%' -> id=17
  - quantity: 10, price_unit: 500
  - payment_term: search account.payment.term where name ilike '30%' -> id=3
  - tax_ids: search account.tax where name ilike 'Output VAT 12%' -> id=7

Action: create account.move with above values
Confirmation: "Draft invoice INV/2026/0042 created for PHP 56,000. Confirm?"
```

The copilot NEVER posts/confirms without explicit human approval. It operates on
Odoo workflow primitives (stages, activities, tasks) -- it triggers them, never replaces them.

### 2. Document Intelligence Pipeline

```
Source Document (PDF/image)
  -> Azure Document Intelligence (pre-built invoice model)
  -> Extracted fields: vendor name, TIN, line items, amounts, taxes
  -> MCP tool: odoo.match_partner(name, tin) -> partner_id
  -> MCP tool: odoo.match_product(description) -> product_id
  -> MCP tool: odoo.create_vendor_bill(partner_id, lines, taxes)
  -> Human review queue: AP clerk validates and posts
```

Key models in Document Intelligence:
- `prebuilt-invoice`: Vendor invoices (name, address, line items, totals, tax).
- `prebuilt-receipt`: POS receipts (merchant, items, total, date).
- Custom model: BIR 2307 certificate extraction (TIN, ATC, amounts, period).

### 3. MCP Tool Server for Odoo

An MCP server exposes Odoo operations as tools with JSON Schema definitions:

```json
{
  "name": "odoo.search_records",
  "description": "Search Odoo records by model and domain",
  "parameters": {
    "model": { "type": "string", "description": "Odoo model name, e.g. res.partner" },
    "domain": { "type": "array", "description": "Odoo domain filter" },
    "fields": { "type": "array", "description": "Fields to return" },
    "limit": { "type": "integer", "default": 10 }
  }
}
```

Tools to expose:
- `odoo.search_records` -- read any model (respects `ir.model.access` + `ir.rule`)
- `odoo.create_record` -- create in any allowed model (draft state only)
- `odoo.execute_action` -- trigger a server action or workflow transition
- `odoo.get_report` -- generate and return a report (PDF/XLSX)
- `odoo.get_dashboard_data` -- aggregated KPI data for copilot summaries

Security: MCP server authenticates as a service user with Entra Managed Identity.
Tool calls inherit the requesting user's Odoo permissions via `X-Odoo-User` header.

### 4. Agent Governance Framework

```
Agent Passport Schema:
  agent_id: "agent-ap-processor-001"
  display_name: "AP Processing Agent"
  identity: Entra Managed Identity (client_id: <uuid>)
  allowed_tools:
    - odoo.search_records (models: [res.partner, product.product, account.move])
    - odoo.create_record (models: [account.move], constraint: state=draft)
    - odoo.execute_action (actions: [action_post_vendor_bill] -- DENIED)
  rate_limit: 100 calls/minute
  requires_human_approval:
    - any state transition (draft -> posted)
    - any payment creation
    - any record deletion
  audit_level: FULL (all tool calls logged)
  escalation_target: "ap-manager@insightpulseai.com"
```

Governance rules:
1. **No agent may post/confirm a financial document** without human approval.
2. **No agent may delete records** -- only archive (active=False).
3. **All agent actions are logged** with tool call, parameters, result, and user context.
4. **Agent permissions are a strict subset** of the mapped human role.
5. **Circuit breaker**: If agent error rate exceeds 5% in 10 minutes, halt and alert.

### 5. Prompt Engineering for ERP Context

Prompt template structure:
```
SYSTEM: You are an ERP assistant for {company_name} running Odoo 18 CE.
You have access to tools for searching and creating records.

CONTEXT (grounding):
- Company: {company_name}, TIN: {company_tin}
- Fiscal year: {fiscal_year_start} to {fiscal_year_end}
- Currency: PHP (Philippine Peso)
- Tax regime: VAT-registered, 12% output VAT, EWT per BIR schedule
- Active fiscal positions: {fiscal_positions}

CONSTRAINTS:
- Never create records in posted state. Always draft first.
- Always verify partner exists before creating transactions.
- When amounts exceed PHP {threshold}, flag for manager review.
- For tax-related operations, always apply the partner's fiscal position.

USER REQUEST: {user_message}
```

Grounding data injection:
- Recent transactions with the mentioned partner (last 5 invoices/bills).
- Product catalog matches for mentioned items.
- Current account balances if financial query.
- Open activities/tasks if project query.

### 6. Knowledge-Grounded Q&A

```
User: "What is our outstanding receivable from Acme Corp?"

Agent flow:
  1. odoo.search_records(model='res.partner', domain=[('name','ilike','Acme')])
     -> partner_id = 42
  2. odoo.search_records(model='account.move',
     domain=[('partner_id','=',42),('move_type','=','out_invoice'),
             ('payment_state','!=','paid'),('state','=','posted')],
     fields=['name','amount_residual','invoice_date_due'])
     -> [{name: 'INV/2026/0038', amount_residual: 150000, due: '2026-04-15'}, ...]
  3. Summarize: "Acme Corp has PHP 350,000 in outstanding receivables across
     3 invoices. The oldest is INV/2026/0038 (PHP 150,000, due April 15)."
```

No hallucinated numbers. Every figure comes from a tool call with a traceable record.

---

## Edge Cases

1. **Ambiguous partner names**: "Create invoice for Manila Trading" matches 3 partners.
   Agent must present disambiguation options, never guess.
2. **Stale grounding data**: If agent caches partner data but partner was archived
   since cache refresh, the create will fail. Always verify before mutating.
3. **Multi-step rollback**: Agent creates SO line 1, line 2 succeeds, line 3 fails.
   Must rollback lines 1 and 2. Use Odoo's ORM transaction (all-or-nothing on `create`
   with list of vals) rather than sequential creates.
4. **Prompt injection via record data**: A partner's name field could contain
   adversarial text. Sanitize all Odoo field values before injecting into prompts.
5. **Rate limiting on Document Intelligence**: Azure DI has per-second limits.
   Queue documents and process with backpressure. Do not retry aggressively.

---

## Controls & Compliance

| Control | Implementation |
|---------|---------------|
| Human-in-the-loop for financial state changes | Agent passport `requires_human_approval` list |
| Tool call audit trail | All MCP calls logged to `ipai_agent_log` model + Azure Monitor |
| Prompt version control | Prompt templates in `ipai_ai_copilot` with `mail.thread` versioning |
| PII filtering | Strip PII from LLM context unless explicitly needed for the operation |
| Cost tracking | Token usage per agent per day logged; alert on anomalous spikes |
| Model selection governance | Only approved models (GPT-4o, Claude) in Foundry deployment |

---

## Odoo/OCA Implementation Surfaces

| Module | Source | Purpose |
|--------|--------|---------|
| `mail` | Core | Activity scheduling, chatter for agent annotations |
| `base_automation` | Core | Server actions triggered by agent recommendations |
| `web` (Ask AI) | Core | Native Odoo 18 AI assistant interface |
| `ipai_ai_copilot` | Custom | Prompt registry, tool routing, governance engine |
| `ipai_ai_tools` | Custom | MCP tool server implementation for Odoo |
| `ipai_agent_log` | Custom | Agent action audit trail model |
| `ipai_doc_intelligence` | Custom | Azure Document Intelligence integration |

---

## Azure/Platform Considerations

- **Azure AI Foundry**: Host agent orchestration. Deploy GPT-4o for copilot,
  Claude for code/analysis tasks. Foundry manages model endpoints, safety filters,
  and token metering.
- **Azure Document Intelligence**: Deploy in Southeast Asia region for latency.
  Use pre-built models for invoices; train custom model for BIR 2307 extraction.
- **Azure AI Search**: Vector index over Odoo knowledge base articles, product
  catalogs, and policy documents for RAG grounding.
- **Entra Agent ID**: Each agent gets a Managed Identity. No shared secrets.
  Identity lifecycle managed in Entra, not in Odoo.
- **Azure Container Apps**: MCP tool server runs as a sidecar container alongside
  Odoo. Internal-only ingress (not exposed to internet).
- **Azure Monitor + Application Insights**: Trace every agent interaction end-to-end.
  Correlation ID links user request -> copilot -> MCP tool call -> Odoo ORM -> response.

---

## Exercises

### Exercise 1: MCP Tool Definition
Define 3 MCP tools for Odoo: `search_partners`, `create_draft_invoice`, and
`get_invoice_pdf`. Write the JSON Schema for each. Include parameter validation
(e.g., `amount` must be positive, `partner_id` must exist). Test with a mock agent call.

### Exercise 2: Document Intelligence Pipeline
Upload 3 sample vendor invoices (PDF) to Azure Document Intelligence. Extract
vendor name, TIN, line items, and totals. Map extracted vendor to `res.partner`
by TIN match. Create draft `account.move` records. Verify extracted amounts match
the PDF content.

### Exercise 3: Agent Passport Design
Design agent passports for 3 agents: (1) AP Processing Agent, (2) Sales Order
Assistant, (3) Inventory Reorder Agent. For each, define: allowed tools, forbidden
actions, human approval gates, rate limits, and escalation targets.

### Exercise 4: Prompt Template Testing
Write a prompt template for "create customer invoice" operation. Test with 5 variations:
simple (1 line), complex (5 lines with different taxes), ambiguous partner, missing
product, and amount exceeding threshold. Verify the copilot handles each correctly.

---

## Test Prompts for Agents

1. "I just received 15 vendor invoices as PDFs. Set up the Document Intelligence
   pipeline to extract them, match vendors by TIN, and create draft bills in Odoo.
   Show me the queue and any that failed matching."

2. "Design an MCP tool server for Odoo that exposes read-only access to partners,
   invoices, and inventory. Ensure it respects Odoo's record rules and cannot be
   used to create or modify records."

3. "The copilot suggested creating an invoice for PHP 5,000,000 which exceeds our
   approval threshold. Walk through the governance flow: what happens at each step,
   who gets notified, and how is the approval recorded?"

4. "Write the agent passport for a 'Treasury Agent' that can view bank statements,
   reconcile payments, but cannot create manual journal entries or modify bank
   statement lines. Include the exact tool permissions and denial list."

5. "A user typed 'delete all invoices from last month' into the copilot. Demonstrate
   how the governance layer prevents this: the prompt constraint, the tool permission
   check, and the audit log entry for the denied request."
