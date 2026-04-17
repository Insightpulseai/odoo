# Constitution — Reverse SAP Concur on Odoo 18

## 1. Purpose

Reverse SAP Concur by treating Odoo CE 18 Finance as the transactional spend
workflow core, OCA as the composition layer, Azure Document Intelligence as
the extraction/classification bridge, and OCA AI bridges as the controlled
AI ingress path.

This is not a greenfield autonomous spend OS. It is a **productization and
augmentation of an existing finance workflow substrate** that already covers
the core Concur capability set natively.

## 2. Architecture Doctrine

### 2.1 Odoo CE 18 Finance is the workflow core

Execution and accounting truth lives in Odoo CE 18 Finance.

Native baseline includes:
- Expense categories, logging, and submission
- Receipt attachment / upload / email expense ingestion
- Expense reports and approval routing
- Posting to accounting
- Reimbursements and re-invoicing
- Analytic distribution
- Accounting, budgets, analytic accounting, withholding taxes
- Bank synchronization and reconciliation
- Multi-currency and multi-company support

No custom module may reimplement these capabilities.

### 2.2 OCA is the composition layer

OCA modules extend the CE baseline for:
- Cash advance / clearing lifecycle
- Multi-tier approval routing
- Payment management and sequencing
- Document archival and audit trails
- Async job processing
- Budget reporting (MIS)
- Helpdesk / dispute ticketing

### 2.3 AI boundary

AI must enter through a bridge boundary, not directly into core accounting logic.

Preferred bridge pattern:
- OCA `ai_oca_bridge` — base AI provider integration
- OCA `ai_oca_bridge_chatter` — AI via Odoo chatter/messaging
- OCA `ai_oca_bridge_document_page` — AI for document synchronization
- OCA `ai_oca_bridge_extra_parameters` — extended AI payload parameters

Native generation providers may be swappable, but business-state transitions
remain owned by Odoo modules and explicit policy logic. AI actions are
advisory, confidence-scored, and audit-logged. AI must not directly mutate
posted accounting state without explicit workflow gates.

### 2.4 OCR / document intelligence boundary

Receipt and invoice digitization belong in an external document-intelligence
bridge. Azure Document Intelligence is the preferred bridge substrate for:
- Read / layout extraction
- Custom field extraction
- Custom classification
- Query field extraction
- Batch analysis
- Confidence-scored outputs

Odoo owns:
- Attachment lifecycle
- Review queue
- Exception handling
- Approval readiness
- Accounting posting state

`queue_job` is the async orchestration substrate, not business logic.
OCR logic must not enter expense or accounting modules.

### 2.5 Custom delta is thin and PH-specific

Custom `ipai_*` modules may own:
- PH liquidation lifecycle (cash advance request, 3 types, clearing)
- PH compliance/policy semantics (BIR validation, receipt requirements)
- Expense-specific exception/violation models
- Orchestration hooks into bridge services

Custom modules must not reimplement:
- Baseline expense submission/posting/reimbursement
- Generic tier-validation engine
- Generic DMS / audit / queue / MIS primitives
- Native Odoo accounting, budgets, or reconciliation

## 3. Mandatory Guardrails

### 3.1 No capability duplication
If CE or OCA provides it, no custom module may reimplement it.

### 3.2 No AI in accounting core
AI actions are advisory. Posting, reimbursement, and accounting truth remain
Odoo-owned. AI enters through OCA bridge modules only.

### 3.3 No OCR in expense modules
Extraction lives in external bridge. Odoo owns review, linkage, exceptions.

### 3.4 No deprecated infrastructure
No Supabase, n8n, Cloudflare, Vercel, or other deprecated services.

### 3.5 Multi-company by default
All models must respect multi-company rules.

### 3.6 Explainability required
Every AI action must emit: rationale, referenced policy, confidence level,
and reversible action log. No opaque autonomous decisions.

## 4. MVP Doctrine

This feature is an explicit MVP baseline for the IPAI platform workstream.

### MVP includes

- Cash advance request lifecycle (request, approval, release/disbursement)
- Cash advance monitoring views / queues / statuses
- Liquidation / itemized expense linkage to advance
- Net due / refundable computation
- Finance review / posting / approval metadata
- Printable operational outputs (QWeb reports)
- Lightweight mobile companion for:
  - Request status
  - Approval status
  - Advance monitoring
  - Liquidation reminders
  - Limited companion actions appropriate to mobile use

### MVP boundaries

- Odoo remains workflow, approval, accounting, and document truth
- The mobile companion is a subordinate companion surface, not a separate
  workflow engine or system of record
- The mobile companion must read/write only through Odoo-owned workflows
- Do not create a standalone Concur-style platform as MVP
- Do not require a separate portal as MVP

### Non-MVP bridge capabilities are not required baseline

OCR, AI review, corporate card feeds, external tax enrichment, and governed
Azure runtime are promotion-lane capabilities. They are not required for
MVP delivery.

### Deferred / post-MVP

- Mandatory OCR baseline
- Mandatory AI review baseline
- Mandatory corporate card feed baseline
- Mandatory external tax enrichment baseline
- Heavy enterprise travel stack unless already defined elsewhere
- Any standalone platform behavior
- Governed Azure landing-zone deployment

## 5. Anti-Patterns

Do not:
- Put OCR logic inside accounting/expense modules
- Let AI directly mutate posted accounting state without explicit workflow gates
- Treat OCA AI as the source of truth for spend decisions
- Rebuild native Odoo expense/report/reimbursement flows as custom modules
- Embed opaque AI logic deep inside expense/accounting models
- Build a monolithic "spend OS" that ignores Odoo's existing finance surface

## 6. MVP Is a Viable Horizontal Slice

For ERP/SaaS-adjacent features, MVP must be defined as the smallest viable
cross-cutting slice that delivers end-to-end value. Avoid isolated
component-only MVPs when the user workflow depends on multiple tightly
connected business objects.

## 7. SaaS and Multitenancy Are Separate Decisions

SaaS is the delivery/business model. Multitenancy is an architecture choice.
Tenant model, data isolation, and shared-component boundaries must be chosen
explicitly per feature.

## 8. Azure-First, Single-Cloud Focus

The near-term platform baseline is Azure-first. Do not introduce multicloud
requirements into MVP unless explicitly required by business scope.

## 9. Control Plane Is First-Class

Administrative control, tenant/workspace/project configuration, and
operational rollout controls are part of the product architecture, not an
afterthought.

## 10. External Checklists Inform Review, Not Source-of-Truth Design

Community and external review checklists may be used to validate readiness
and catch omissions, but they do not replace the feature bundle as the
source of truth.

- Azure review checklists are review aids and promotion-lane controls.
- Odoo go-live checklists are operational readiness aids.
- Neither may override Odoo-first workflow/accounting truth or the MVP
  scope defined in this bundle.

## 11. Odoo-Native Testing Is Required

Addon and bridge code must follow Odoo-native testing patterns.

At minimum:

- model/business logic tests use Odoo test case classes
- form-driven behaviors use server-side `Form` tests
- HTTP / tour behavior uses `HttpCase` only where UI flow coverage is actually required
- test selection must be explicit through tags
- browser-critical end-to-end flows may use Playwright where backend/form
  coverage is insufficient
- MVP is not complete without executable tests for core workflows

## 12. Browser Automation Is Targeted, Not Default

Playwright is reserved for browser-critical flows and smoke coverage.
Chrome DevTools is a debugging surface, not the primary test framework.
Manual QA and ad hoc scripts do not replace executable automated tests.

## 13. MCP Tooling Is Optional and Bounded

MCP servers are optional developer and operator tooling surfaces. They
assist with automation, debugging, reference lookup, and platform
validation. They must never own workflow state, business logic, or
approval truth.

Allowed roles:

- Playwright MCP for browser automation
- Chrome DevTools MCP for debugging
- Azure MCP Server for platform/runtime validation
- Microsoft Learn MCP for documentation lookup
- Azure DevOps MCP only if work-item sync is explicitly in scope

Prohibited role: MCP as the primary owner of workflow or business state.

## 14. Experimental MCP Integrations Are Non-Critical

Experimental or preview MCP integrations (e.g., Azure AI Foundry MCP)
must not be on the MVP critical path. They may be evaluated and adopted
when stable, but must not block delivery or become implicit dependencies.

## 15. Foundry Project Connections Are Optional and Minimum-Necessary

The Foundry project (`ipai-copilot`) supports attachable connections (Azure OpenAI,
AI Search, Cosmos DB, Storage, Fabric, etc.). These are optional enrichments, not
mandatory baseline dependencies.

- Do not assume any connection is already configured unless explicitly proven.
- For the SAP Concur / mobile companion surface: attach Azure OpenAI only where
  the mobile companion or bounded assistant requires inference (reminders, status
  summarization, bounded responses); omit AI Search unless policy retrieval or
  evidence grounding is in scope; access Document Intelligence via the AI Services
  endpoint, not a separate project connection.
- Add only the minimum connections required for MVP.
- Microsoft Fabric is preview and must not be on the MVP critical path.
- Document every new project connection before implementation depends on it.

## 16. API Edge Replacement Is Facade-Only

FastAPI or external API layers may replace the public/mobile API edge,
but they must not replace Odoo/OCA as the owner of workflow, approvals,
accounting, tax, or ERP state. The FastAPI edge may package, orchestrate,
proxy, or expose workflows, but Odoo remains the authoritative write path
for all ERP business objects.
