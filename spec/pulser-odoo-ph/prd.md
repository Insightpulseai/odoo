# PRD — Pulser: Odoo 18 PH Copilot

## Status
Active

## Feature Branch
`pulser-odoo-ph`

## Supersedes
`spec/pulser-odoo/` (tax-adapter-only scope)

---

# Product

## Name
Pulser — Odoo 18 PH Copilot

## One-line positioning
An agentic, approval-gated finance, tax, and operations copilot for Odoo 18 in the Philippines.

## Problem
Odoo users in finance and operations lose time switching between ERP records, policy documents,
tax rules, supporting documents, and manual review steps. Generic chat assistants can answer
questions, but they are usually not record-aware, workflow-aware, or Philippines-compliance-aware.
They also fail to provide audit-ready traces for recommendations and actions.

## Why now
- Microsoft Foundry now cleanly separates:
  - project-native agent/app capabilities via the Foundry SDK
  - OpenAI-compatible model access via project-derived or `/openai/v1` clients
  - service-specific AI tooling via Foundry Tools SDKs
- This makes it practical to build Pulser as an Odoo-native copilot shell backed by a governed
  agent runtime instead of a thin "chat with model" feature. The Foundry guidance explicitly
  positions the Foundry SDK for agents, evaluations, and tracing, while the OpenAI-compatible
  client is used for model-shaped interactions such as Responses API calls.

## Target users
- Accountant
- AP reviewer
- Controller
- Operations manager
- Founder / admin

## Jobs to be done
- Explain why a record is in its current state
- Summarize chatter, documents, invoices, partners, journals, tasks, and projects
- Suggest next actions based on Odoo context and company policy
- Review AP and expense documents with accounting/tax suggestions
- Prepare PH compliance workpapers and exception summaries
- Ground answers in internal policies, prior transactions, and approved reference material

## Goals
1. Reduce manual finance and ops review time inside Odoo
2. Make recommendations contextual to the active record and user permissions
3. Support PH tax/compliance assistance without autonomous filing or posting
4. Produce audit-ready traces for prompts, tools, approvals, and outputs
5. Keep Odoo as the transactional system of record

## Non-goals
- Replace Odoo workflows or UI for core ERP transactions
- Perform autonomous accounting posting by default
- Perform autonomous tax filing or regulatory submission
- Build a general-purpose multi-agent platform in V1
- Recreate ERP logic already present in Odoo or OCA

## Product principles
- Record-aware: every answer should be tied to Odoo context
- Workflow-aware: responses should reflect current process state
- Policy-aware: recommendations must use approved internal guidance where available
- Compliance-aware: PH-specific tax/document logic must be first-class, not an afterthought
- Human-governed: high-risk actions require approval
- Explainable: recommendations must expose rationale and source context

---

## MVP scope

### Capability lane A — Contextual Odoo Copilot
- Record summary for invoices, bills, partners, projects, tasks, journals, and chatter threads
- "Why is this in this state?" explanation flows
- Draft note, email, follow-up, activity, and summary generation
- Next-best-action suggestions

### Capability lane B — Finance review copilot
- AP invoice review
- Expense classification assistance
- Account suggestion assistance
- Tax code / tax treatment suggestion assistance
- Variance and anomaly explanation

### Capability lane C — PH compliance copilot
- VAT / EWT guidance assistance
- Document metadata validation
- Invoice / receipt checklist assistance
- Filing workpaper draft preparation
- Exception queue summarization

### Capability lane D — Retrieval and grounding
- Company policy grounding
- PH tax/compliance grounding
- Historical transaction grounding
- Internal audit/explanation traces

---

## In-context document action UX

For document-centric workflows, Pulser must not rely on free-form chat output alone.

### Required interaction pattern

1. Detect and classify the uploaded artifact
2. Perform extraction automatically where confidence is sufficient
3. Present a structured extraction summary
4. Surface governed next actions in Odoo terms
5. Persist and display workflow state

### Minimum UI outputs for invoice workflows

- Document type classification
- Extraction summary card (vendor, invoice number, date, total, tax, line items)
- Confidence / warning indicators
- Missing required fields
- Matched Odoo entities (vendor, journal, taxes, duplicates)
- Action buttons for governed next steps

Pulser should default to "show and confirm" rather than "recommend and ask".

### Priority document use cases

- Uploaded invoice → extracted fields → draft vendor bill
- Duplicate bill detection before draft creation
- Vendor matching and missing-master-data detection
- Exception routing when confidence or required fields are insufficient

## Document accounting classification rules

For uploaded accounting documents, Pulser must classify the accounting direction before
proposing a draft record.

Examples:

- Issuer sends invoice to customer → draft customer invoice / receivable
- Supplier sends invoice to company → draft vendor bill / payable

Pulser must not default to "vendor bill" unless the document direction and active company
context support that conclusion. The active Odoo company determines which side of the
transaction the user is on.

## High-confidence extraction rule

If an uploaded document is a high-confidence invoice candidate and core fields are visually
extractable, Pulser should:

1. Extract automatically
2. Show structured fields
3. Run duplicate/master-data/tax checks
4. Offer governed next actions

Pulser should not stop at a generic recommendation to extract first. The user uploaded the
document — extraction is the implied intent.

## Canonical invoice and expense scenario universe

Pulser must support the following scenario families:

- Customer invoices (AR)
- Vendor bills (AP)
- Credit/debit corrections
- Employee expenses
- Reimbursements
- Customer re-invoiced expenses
- Payments and batch payments
- Bank reconciliation
- OCR / digitized documents
- EDI / Peppol documents
- PO-matched AP bills

### Classification dimensions

Every incoming document/event must be classified on these axes:

1. **Business direction** — receivable, payable, employee expense, reimbursement, correction,
   payment/reconciliation artifact
2. **Source** — manual entry, uploaded file, emailed file, OCR result, EDI import, PO-linked,
   expense app flow, bank sync/reconciliation
3. **Accounting object** — customer invoice, vendor bill, credit note, vendor refund, debit
   note, expense line, expense report, payment, batch payment, journal entry/write-off
4. **Payer/beneficiary** — customer owes company, company owes vendor, company owes employee,
   employee owes company, company paid directly, bank settles
5. **Confidence/automation level** — deterministic, high-confidence extracted, needs review,
   ambiguous, blocked
6. **Settlement state** — draft, posted, partially settled, fully settled, exception,
   canceled/reversed
7. **Active company/branch context**
8. **Currency/tax/payment-term modifiers**

### Pulser decision rules

1. If the document is a **clear invoice/bill candidate**, extract first — do not ask first
2. Never choose **vendor bill vs customer invoice** from document appearance alone — always
   include active company context and issuer/recipient role
3. Expense receipts are not invoices by default — if employee-originated with Paid By =
   Employee, route to expense flow, not AP bill flow
4. If a purchase order match exists, prefer **PO matching/auto-complete** over raw OCR line
   creation
5. Validated invoice changes must go through **credit/debit note** logic, not silent mutation
6. Payment completion is not accounting completion — operationally separate document creation,
   posting, payment registration, and bank reconciliation

### Canonical state machines

**Invoice/bill:** detected → classified → extracted → partner-matched → tax/journal-validated
→ duplicate-checked → draft-created → posted → payment-registered → reconciled → corrected/exception

**Expense:** logged → grouped to report → submitted → approved/refused → posted →
reimbursable/company-paid → reimbursed → re-invoiced if applicable → exception

**Payment:** initiated → registered → batched if applicable → matched → reconciled →
write-off/residual → exception

### Exception categories

- **Direction exceptions:** issued invoice in wrong context, refund mistaken for invoice
- **Master-data exceptions:** vendor/customer not found, wrong company, missing journal/tax
- **Financial exceptions:** line ≠ header total, VAT arithmetic mismatch, duplicate reference,
  PO price differs, OCR fields but not taxes
- **Workflow exceptions:** not approved, not posted, not reconciled, connection lost, idempotency
  risk, auto-post rule misfires, multi-company behavior differs

## Canonical Pulser decision table

Pulser must resolve every finance intake through a deterministic decision table using:

- Intake signal
- Active company context
- Scenario family
- Required validation checks
- Safe default action
- Automation boundary

Pulser must not directly create accounting objects before:

1. Directionality is resolved
2. Required blockers are checked
3. The selected action is allowed for the current confidence band

### Safe action vocabulary (fixed enum)

```
show_structured_review_card
create_draft_customer_invoice
create_draft_vendor_bill
create_draft_vendor_refund
create_credit_note_from_source_invoice
create_debit_note_from_source_document
create_expense_line_employee_paid
create_expense_line_company_paid
group_into_expense_report
create_expense_and_attach_to_sales_order
register_customer_payment_or_route_to_reconcile
register_vendor_payment_or_route_to_reconcile
open_reconciliation_with_preselected_match
create_or_update_batch_payment
auto_complete_from_po_then_review
block_and_link_existing_record
route_for_master_data_resolution
mark_not_accounting_document
resume_or_show_final_status
```

The machine-readable decision table and directionality overrides are maintained in
`evals/finance/schema/pulser_decision_table.yaml`.

### Document workflow states

- Uploaded
- Classifying
- Extracted
- Needs confirmation
- Draft created
- Posted / rejected / routed

---

## User stories

### Story 1 — Record explanation
As an accountant, I want Pulser to explain the current state of an invoice or journal entry so
that I can review faster without manually tracing every related record.

#### Acceptance criteria
- Given an active Odoo record, when the user asks for an explanation, then Pulser returns a
  concise explanation tied to record fields, related records, and recent workflow actions.
- Given insufficient context, when Pulser cannot determine a reliable explanation, then it
  states uncertainty and requests or retrieves additional allowed context instead of guessing.

### Story 2 — Finance review assistance
As an AP reviewer, I want Pulser to review incoming invoices and suggest classifications or tax
handling so that I can reduce manual review effort.

#### Acceptance criteria
- Given an AP document, when Pulser reviews it, then it returns suggested account/tax treatment,
  identified discrepancies, and a confidence/rationale summary.
- Given a high-risk or low-confidence recommendation, then Pulser routes the action for review
  and does not auto-post changes.

### Story 3 — PH compliance assistance
As a controller in the Philippines, I want Pulser to help prepare workpapers and validate
document requirements so that compliance work is faster and more consistent.

#### Acceptance criteria
- Given a PH-scoped entity, when Pulser evaluates a document/work item, then it applies the
  PH compliance rules configured for that entity.
- Given missing required metadata or documentary support, then Pulser flags the exception and
  produces a checklist or workpaper draft instead of silently proceeding.

### Story 4 — Governed action execution
As an admin, I want Pulser to assist with actions in Odoo while enforcing approval gates so that
the system remains safe and auditable.

#### Acceptance criteria
- Given a low-risk action, when approved by policy, then Pulser may execute through a tool path.
- Given a high-risk action, then Pulser must require explicit human approval before execution.
- All tool calls, approvals, and outputs must be logged for traceability.

---

## Functional requirements
- Pulser shall run as an Odoo-native assistant surface for supported record types.
- Pulser shall use Microsoft Foundry as the primary agent runtime for agent, tracing, and
  evaluation workflows. The Foundry SDK is the intended integration path for these features.
- Pulser shall use an OpenAI-compatible client for model-shaped interactions such as Responses API calls.
- Pulser shall support grounding against approved internal knowledge and selected Odoo context.
- Pulser shall expose tool paths for safe Odoo actions behind policy and approval checks.
- Pulser shall support PH finance/tax assistance in MVP scope.
- Pulser shall record trace metadata for prompts, tool calls, approvals, and outputs.

## In-form context resolution

When Pulser is invoked from an active Odoo form view, it must ground answers in the current
record context before asking generic clarification questions.

Minimum context for Expenses:

- Current app/module
- Record state (new/draft/posted)
- Visible core fields (category, amount, taxes, date)
- Company
- Employee
- Paid by (employee/company)
- Attached receipt presence

If the user asks a short or noisy question such as "tax?", "is it correct?", or "is it
computed?", Pulser should resolve the question against the active form context.

## Expense tax validation behavior

For expense records, Pulser must distinguish:

- Tax not applicable
- Tax not yet computable because required fields are missing
- Tax computed from category defaults
- Tax inconsistent with extracted receipt evidence
- Tax mapping missing or misconfigured

Pulser should answer with record-specific status and next actions, not generic clarifying
prompts.

## Foundry runtime authority

Pulser uses Microsoft Foundry as the canonical AI application platform.

This includes:

- model access through the Foundry model catalog
- managed agent execution through Foundry Agent Service
- enterprise grounding through Foundry IQ / retrieval-augmented generation
- evaluation, safeguards, and production monitoring through Azure-managed controls

Copilot Studio remains an optional extension surface for Microsoft 365 scenarios, not the
primary runtime authority.

## Knowledge and grounding model

Pulser is RAG-first.

Grounding sources may include:

- Odoo records and metadata
- Odoo attachments and uploaded business documents
- policies, SOPs, accounting references, and operational guidance
- indexed enterprise knowledge stores

Pulser should prefer retrieval and tool use before model-only generation.
Fine-tuning is optional and should only be used when retrieval, prompt design, and
workflow/tool integration are insufficient for the target use case.

## Platform security and control expectations

Pulser production design should assume:

- managed identity-based service authentication where possible
- secret storage outside application code and pipeline YAML
- private or internal connectivity for protected services where feasible
- centralized monitoring, tracing, and safety/quality evaluation
- protected access paths to knowledge stores and model endpoints

The platform design should favor enterprise-managed controls over application-embedded
credentials and ad hoc networking.

## Hosting pattern

Pulser should target an Azure-managed container hosting pattern suitable for:

- API endpoints
- background processing jobs
- event-driven processing
- internal microservices

The deployment model must support:

- automatic scaling
- revision-based rollout and rollback
- secure internal-only service communication
- managed secrets and configuration
- centralized logs and observability

This hosting posture aligns with Azure Container Apps capabilities and is the preferred
application-hosting baseline for Pulser-facing services and worker processes.

## Runtime topology

### Interactive path

- Odoo UI invokes Pulser application endpoints for chat, explain, navigate, and action-draft flows.
- Interactive endpoints must support HTTP ingress and scale according to request demand.

### Background path

- Long-running or finite tasks such as document extraction, reconciliation batch analysis,
  index refresh, and evidence-pack generation should run as background jobs or event-driven workers.

### Service boundaries

- User-facing request handlers
- Retrieval / grounding services
- Transaction orchestration services
- Multimodal processing workers

These services may be deployed as separate containerized units with controlled internal
communication and independent scaling behavior.

## Guardrails
- No autonomous posting to books by default
- No autonomous tax filing or external submission
- No hidden execution of high-risk tools
- No fabricated policy or tax advice when source context is absent
- No access beyond the current user's permitted Odoo scope

## Success metrics
- Reduce AP review time by at least 30% in pilot workflows
- Reduce manual policy lookup time by at least 50%
- Achieve trace coverage for 100% of tool-executed actions
- Achieve first-pass useful answer rate above 80% on supported record explanation flows
- Keep approval-gated action compliance at 100%

## Non-functional requirements (runtime)

- Interactive endpoints should be able to scale based on request load
- Worker services should support event-driven or scheduled execution where appropriate
- Deployment must support revision-based rollback and controlled rollout
- Internal service-to-service communication should prefer private/internal ingress over
  unnecessary public exposure
- Logs, traces, and operational telemetry must be centralized for runtime diagnosis
- Delivery automation must support staged promotion with separate build, test, staging, and
  production control points
- Protected deployments must support human validation before execution
- Required compliance/security stages must not be silently bypassable
- Production deployment must be restricted to approved branches and protected resources
- Secrets consumed by delivery pipelines must use explicitly authorized variable/resource
  access paths
- Delivery design must preserve a clear rollback or alternate deployment procedure
- Model selection must account for latency, cost, privacy, and task fit
- RAG over protected enterprise data is preferred before fine-tuning
- Agent runtimes must support tool invocation and multi-agent orchestration where needed
- Protected services should not require broad public exposure unless explicitly justified
- Production deployments must include runtime monitoring for safety, quality, and consumption
- Asynchronous document workflows must expose visible processing state
- Action execution must be idempotent across reconnect/retry scenarios
- Degraded connectivity must not leave action state ambiguous
- Document workflows must emit audit-friendly source-to-action traceability

## Eval dataset requirements

Pulser must be evaluated with a multi-task finance dataset covering:

- Classification (document type, scenario family, accounting direction)
- Extraction (header, partner, dates, line items, tax, totals)
- Odoo object/action selection (customer invoice, vendor bill, expense, credit note, payment)
- Validation/blocker detection (duplicate, partner match, tax mapping, PO match)
- Workflow reliability (idempotency, retry, reconnect, async state)
- Explanation quality (rationale for chosen object and action)

### Dataset layers

- **Smoke** (50-100 samples): one clean example per major scenario, runs on every PR
- **Core** (800-1500 samples): balanced representative production scenarios, primary release gate
- **Edge** (400-800 samples): OCR noise, low confidence, tax anomalies, duplicates, missing data
- **Adversarial** (150-300 samples): directionality traps, context traps, arithmetic traps
- **Regression** (continuously growing): every production failure becomes a locked eval case

### Release thresholds

- Document family classification: >= 97%
- High-risk directionality confusion (vendor bill vs customer invoice): <= 0.5%
- Odoo object selection: >= 95%
- Unsafe auto-action rate: 0% target, hard fail above 0.1%
- Duplicate detection recall: >= 95%
- Blocker recall on exception set: >= 92%

### Context-sensitive evaluation

The same artifact must be evaluated under multiple company contexts. A single invoice
must produce different correct answers depending on whether the active company is the
issuer or recipient.

---

## Existing IPAI Modules (Foundation)

| Module | Role in Pulser PH |
|--------|------------------|
| `ipai_odoo_copilot` | Canonical copilot shell (systray, chat panel, context packaging) |
| `ipai_copilot_actions` | Agent action queue + human approval framework |
| `ipai_tax_intelligence` | Core tax determination kernel (55 tests) |
| `ipai_bir_tax_compliance` | PH compliance pack prototype |
| `ipai_bir_notifications` | PH filing notification framework |
| `ipai_document_intelligence` | Document extraction for AP invoice intake |
| `ipai_expense_ops` | AP discrepancy control pattern |
| `ipai_branch_profile` | Multi-entity / branch-aware operations |

---

## References

- [Azure AI Foundry SDK — Choosing Your Path](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/sdk-overview)
- [spec/pulser-odoo/](../pulser-odoo/) — predecessor tax-adapter spec
- [spec/pulsetax-agentic-control-plane/](../pulsetax-agentic-control-plane/) — PulseTax product spec

## 22. Identity, access, and Azure sign-in

Pulser for PH must include a formal identity and access model for Odoo, Pulser runtime surfaces, and supporting gateways.

### 22.1 Identity surfaces
Required identity surfaces:
- Odoo login for internal users
- Pulser gateway or web app surfaces
- agent/runtime service identities
- document/evidence access
- MCP and read-only data access
- admin/operator governance surfaces

### 22.2 Odoo Azure sign-in support
Pulser must support Odoo's Microsoft Azure sign-in path for internal users.

Required Odoo-side configuration model:
- system parameter `auth_oauth.authorization_header = 1`
- Entra app registration for Odoo login
- redirect URL using `/auth_oauth/signin`
- OAuth provider configuration in Odoo
- provider fields including:
  - client ID
  - authorization URL
  - userinfo URL
  - scope
  - allowed state
  - login label

The Odoo reference flow distinguishes supported account type by audience:
- single-tenant organizational directory for internal employee use
- personal-account-oriented setup only where portal-style usage is intentionally desired

### 22.3 User experience rule
Pulser must respect Odoo's first-link behavior for Azure sign-in:
- existing users link through the password reset flow
- invited new users link through the invitation/reset path
- users should not be forced into a parallel unsupported identity-linking path for first use

### 22.4 Pulser custom web and gateway auth
For Pulser custom JS/web surfaces, use Microsoft Authentication Library (MSAL) as the canonical authentication client family.

Supported library families include:
- `@azure/msal-browser`
- `@azure/msal-react`
- `@azure/msal-node`

Package-managed or bundled delivery is required; deprecated CDN delivery should not be used for new Pulser surfaces.

### 22.5 Access model
Pulser must distinguish:
- end-user sign-in
- admin/operator sign-in
- service principal or managed identity access
- read-only grounding access
- write-capable business action access

### 22.6 Product rule
Identity success is not just "user can log in."
Pulser identity must support:
- correct tenant/audience alignment
- correct first-link user flow
- least-privilege runtime access
- explicit separation of internal vs portal audiences
- auditable access to finance and document surfaces
