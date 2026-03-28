# Capability Model

> Taxonomy of Pulser capabilities organized by interaction class. Benchmarked
> against the SAP Joule capability model. Each class defines what the assistant
> can do, the Odoo models in scope, the authorization requirements, and example
> prompts.

---

## Three Capability Classes

Pulser capabilities are classified into three mutually exclusive interaction
classes. Every user prompt maps to exactly one class. The class determines the
authorization check, the audit log level, and the confirmation behavior.

| Class | Verb pattern | Odoo operation | Confirmation required | Audit level |
|-------|-------------|----------------|----------------------|-------------|
| Informational | answer, summarize, explain, compare, count | `search_read`, `read`, `fields_get` | No | Read log |
| Navigational | find, open, show, filter, list | `search_read` + URL construction | No | Read log |
| Transactional | create, update, approve, cancel, post | `create`, `write`, `unlink`, action methods | Yes (configurable) | Write log |

---

## Class 1: Informational (Answer and Summarize)

The assistant retrieves data from Odoo and/or the Databricks lakehouse,
computes aggregates or comparisons, and returns a natural-language answer.
No records are created or modified.

### Description

Informational capabilities cover any prompt where the user wants to understand
the current state of business data. The assistant translates the question into
Odoo ORM queries or Databricks SQL queries, executes them within the user's
permission scope, and formats the result.

### Example Prompts

| Prompt | Grounding source | Odoo models |
|--------|-----------------|-------------|
| "What is total accounts receivable aging over 90 days?" | Odoo | `account.move.line`, `res.partner` |
| "How many purchase orders were created this month?" | Odoo | `purchase.order` |
| "Summarize revenue by product category for Q1" | Databricks | Gold-tier `fact_invoice_line` |
| "What is the current inventory level for SKU WH-001?" | Odoo | `stock.quant`, `product.product` |
| "Compare this month's expenses to the same month last year" | Databricks | Gold-tier `fact_expense` |
| "What is the average days-to-close for sales orders this quarter?" | Odoo | `sale.order` |
| "List the top 10 vendors by purchase volume" | Odoo | `purchase.order.line`, `res.partner` |
| "What leave balances remain for the engineering team?" | Odoo | `hr.leave.allocation`, `hr.employee` |

### Authorization Requirements

- User must have read access to the queried Odoo models (enforced by `ir.model.access` and `ir.rule`)
- Databricks queries execute through a service account with row-level security mapped from the user's Odoo company and groups
- No `sudo()` elevation -- queries run in the user's security context
- Document grounding (Azure AI Search) is filtered by the user's department/company membership

### Grounding Sources

| Source | Access method | Latency | Use case |
|--------|-------------|---------|----------|
| Odoo ORM | `search_read` via JSON-RPC tool | Low (< 500ms) | Operational queries on live data |
| Databricks SQL Warehouse | SQL query via REST API | Medium (1-5s) | Analytical queries on curated datasets |
| Azure AI Search | Semantic search via REST API | Medium (1-3s) | Policy documents, SOPs, contracts |

---

## Class 2: Navigational (Find, Open, Filter)

The assistant locates records matching the user's criteria, constructs a
filtered Odoo view URL, and either presents the results inline or directs the
user to the appropriate list/form view.

### Description

Navigational capabilities bridge the gap between knowing what you want and
finding it in the ERP. The assistant translates natural-language filter
descriptions into Odoo domain expressions, executes the search, and returns
either a summary with a deep link or a structured list of matching records.

### Example Prompts

| Prompt | Navigation target | Odoo models |
|--------|------------------|-------------|
| "Show me all draft purchase orders from last week" | PO list view, filtered | `purchase.order` |
| "Open the most recent bank reconciliation" | Bank statement form view | `account.bank.statement` |
| "Find all invoices for Acme Corp that are overdue" | Invoice list view, filtered | `account.move`, `res.partner` |
| "Show employees whose contracts expire this month" | Employee list view, filtered | `hr.employee`, `hr.contract` |
| "List all products with zero stock in Warehouse Manila" | Product list view, filtered | `product.product`, `stock.quant` |
| "Open the sales order with the highest untaxed total this quarter" | SO form view | `sale.order` |

### Navigation Output Formats

| Format | When used |
|--------|----------|
| Deep link URL | Single record -- opens directly in Odoo form view |
| Filtered list URL | Multiple records -- opens Odoo list view with domain applied |
| Inline summary table | When the user's context suggests they want data without leaving the chat |
| Record card | When a single record is found, show key fields inline with a link |

### Authorization Requirements

- Same as Informational: read access to the target models
- Deep links respect Odoo's native access control -- if the user cannot access the record, Odoo returns a 403
- No additional authorization beyond what Odoo enforces natively

---

## Class 3: Transactional (Create, Update, Approve)

The assistant performs write operations in Odoo on behalf of the authenticated
user. Every transactional action requires explicit user confirmation (unless
the administrator has configured auto-approve for low-risk operations).

### Description

Transactional capabilities are the most powerful and most governed class. The
assistant can create records, update field values, trigger workflow transitions
(confirm, approve, cancel, post), and execute business logic methods. Every
transactional action is logged with the agent identity, the delegated user, the
specific method called, and the before/after state of modified fields.

### Example Prompts

| Prompt | Action | Odoo models | Method |
|--------|--------|-------------|--------|
| "Create a vendor bill from this PDF" | Create | `account.move` | `create()` + OCR extraction |
| "Approve all expense reports under 5,000 PHP" | Batch approve | `hr.expense.sheet` | `action_approve_expense_sheets()` |
| "Post the January closing journal entry" | Workflow | `account.move` | `action_post()` |
| "Cancel purchase order PO-2026-0142" | Workflow | `purchase.order` | `button_cancel()` |
| "Update the unit price of line 3 on SO-2026-0089 to 450 PHP" | Update | `sale.order.line` | `write()` |
| "Create a leave request for March 31 to April 4" | Create | `hr.leave` | `create()` |
| "Confirm the manufacturing order for 500 units of Widget-A" | Workflow | `mrp.production` | `action_confirm()` |
| "Allocate 10 days of sick leave to all new hires from January" | Batch create | `hr.leave.allocation` | `create()` (loop) |

### Confirmation Protocol

| Risk level | Behavior | Example |
|------------|----------|---------|
| Low | Auto-execute (configurable) | Update a draft record's description |
| Medium | Show diff, require "Confirm" | Create a journal entry, approve a leave request |
| High | Show diff + impact summary, require "Confirm" | Post a journal entry, cancel a confirmed PO |
| Critical | Require dual confirmation (copilot + Odoo native approval) | Batch approve invoices over threshold |

Risk levels are assigned per tool in the copilot tool registry (`ipai_copilot_actions` module).
Administrators can override risk levels via the Odoo Settings interface.

### Authorization Requirements

- User must have write/create/unlink access to the target model
- Workflow transitions require the same group membership as clicking the button in the UI
- Approval workflows (e.g., `hr_expense` multi-level approval) are enforced -- the copilot cannot bypass approval chains
- `sudo()` is never used for transactional actions -- all writes execute in the user's security context
- Multi-company rules apply: the user can only modify records in companies they have access to

### Audit Trail

Every transactional action produces an audit record:

| Field | Value |
|-------|-------|
| `agent_id` | Foundry agent identifier |
| `user_id` | Delegated Odoo user (the human who initiated the prompt) |
| `model` | Odoo model name (e.g., `account.move`) |
| `method` | Method called (e.g., `action_post`) |
| `record_ids` | List of affected record IDs |
| `before_state` | Snapshot of modified fields before the action |
| `after_state` | Snapshot of modified fields after the action |
| `timestamp` | UTC timestamp |
| `session_id` | Copilot conversation session identifier |
| `confirmation` | Whether the user confirmed and how (auto, single, dual) |

---

## Action-Taking vs. Answer-Summarize Boundary

The boundary between informational and transactional capabilities is strictly
enforced at the tool level. This is a design decision, not an implementation
detail.

**Informational tools** are registered with `readonly=True` in the tool
registry. They can call `search_read`, `read`, `fields_get`, and
`name_search`. They cannot call `create`, `write`, `unlink`, or any action
method.

**Transactional tools** are registered with `readonly=False` and must include
a `risk_level` declaration. The copilot gateway rejects any tool call that
attempts a write operation through a read-only tool.

This separation ensures that:

1. A prompt like "What would happen if I approved this?" remains informational (the assistant simulates or explains, but does not act)
2. A prompt like "Approve this" triggers the transactional flow with confirmation
3. There is no ambiguous middle ground where the assistant might accidentally mutate data during a query

---

## Grounding Sources

### Odoo Data (Primary)

Live operational data from the Odoo PostgreSQL database, accessed through the
Odoo ORM. This is the system of record for all transactional state.

- Access: JSON-RPC tool calls through the copilot gateway
- Freshness: Real-time (current transaction)
- Security: Odoo ACL and record rules
- Models: All installed Odoo models (base, account, sale, purchase, hr, stock, mrp, etc.)

### ADLS Lakehouse (Analytical)

Curated analytical datasets in Azure Data Lake Storage, processed through
Databricks DLT pipelines and served via SQL Warehouse endpoints.

- Access: Databricks SQL REST API via service principal
- Freshness: Near-real-time (DLT pipeline cadence, typically 15-minute lag)
- Security: Unity Catalog row-level security, mapped from Odoo company/group membership
- Datasets: Medallion architecture (bronze/silver/gold/platinum)

### Azure AI Search (Document Knowledge)

Indexed document corpus for retrieval-augmented generation. Includes policy
documents, standard operating procedures, contracts, and reference materials.

- Access: Azure AI Search REST API via managed identity
- Freshness: Batch-indexed (daily or on-document-change)
- Security: Index-level filtering by department and document classification
- Content types: PDF, DOCX, TXT, HTML

---

## Capability Maturity Stages

Pulser capabilities are rolled out in three maturity stages. Each stage expands
the scope of what the assistant can do.

### Crawl (Current)

| Capability | Status |
|------------|--------|
| Informational queries on core Odoo models (account, sale, purchase, HR) | Active |
| Deep link navigation to records and filtered views | Active |
| Single-record create/update with explicit confirmation | Active |
| Finance-specific read tools (aging, trial balance, reconciliation status) | Active |
| Grounding on Odoo data only | Active |

### Walk (Target: Q2 2026)

| Capability | Status |
|------------|--------|
| Batch transactional actions (approve N records, bulk update) | Planned |
| Databricks SQL warehouse grounding for analytical queries | Planned |
| Azure AI Search document grounding | Planned |
| Multi-step workflows (create draft, review, confirm in sequence) | Planned |
| M365 Copilot plugin for cross-surface invocation | Planned |
| Resumable conversation state (interrupt and continue later) | Planned |

### Run (Target: Q4 2026)

| Capability | Status |
|------------|--------|
| Proactive notifications (anomaly detection, deadline reminders) | Planned |
| Cross-module orchestration (SO to PO to invoice chain) | Planned |
| Custom tool authoring by administrators (low-code tool builder) | Planned |
| Voice input via M365 Copilot surface | Planned |
| Evaluation-gated auto-promotion of new tools | Planned |
| Full Platinum-tier analytics surfacing via Power BI semantic models | Planned |

---

## Odoo Model Scope

The following table lists the Odoo models currently in scope for copilot tools,
organized by domain.

| Domain | Models | Capability classes |
|--------|--------|--------------------|
| Accounting | `account.move`, `account.move.line`, `account.payment`, `account.bank.statement`, `account.reconcile.model` | I, N, T |
| Sales | `sale.order`, `sale.order.line`, `crm.lead` | I, N, T |
| Purchase | `purchase.order`, `purchase.order.line` | I, N, T |
| Inventory | `stock.picking`, `stock.move`, `stock.quant`, `product.product`, `product.template` | I, N, T |
| HR | `hr.employee`, `hr.contract`, `hr.leave`, `hr.leave.allocation`, `hr.expense`, `hr.expense.sheet` | I, N, T |
| Manufacturing | `mrp.production`, `mrp.bom` | I, N |
| Contacts | `res.partner` | I, N, T |
| Configuration | `ir.config_parameter`, `res.company` | I |

I = Informational, N = Navigational, T = Transactional

Additional models can be added by registering new tools in the
`ipai_copilot_actions` module. Each tool registration requires a model scope
declaration, a risk level, and a test case.
