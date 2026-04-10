# Constitution — Expense Management Parity for Odoo 18

## 1. Purpose

Formalize the expense management capability stack in Odoo 18 by composing
CE + OCA + thin custom delta + external bridges, consistent with the
CE/OCA-first doctrine established in the PPM Clarity spec.

This is a **composition formalization**, not a rewrite. The existing custom
modules are justified delta. The work is boundary hardening, adjacent-module
wiring, and proof of current install/runtime state.

## 2. Architecture Doctrine

### 2.1 CE + OCA first for expense management

The expense management stack must use:

1. **Odoo CE 18 `hr_expense`** as the base expense-execution surface
2. **OCA `hr-expense`** modules as the default extension path for cash
   advance, approval routing, payment management, and sequencing
3. **OCA adjacent modules** (DMS, audit, queue, MIS, helpdesk) as
   composable infrastructure wired into the expense flow
4. **Thin `ipai_hr_expense_liquidation` + `ipai_expense_ops` delta** only
   for PH-specific liquidation lifecycle and BIR compliance
5. **External bridges** (`ipai_document_intelligence`) only for capabilities
   requiring non-Odoo services (OCR extraction)

### 2.2 Custom delta scope restriction

The custom expense delta **may own**:

- PH liquidation lifecycle (cash advance request, 3 liquidation types, clearing)
- PH compliance/policy semantics (BIR validation, receipt requirements, overdue thresholds)
- Expense-specific exception/violation models
- Orchestration hooks into bridge services (OCR, card feeds)
- Multi-step approval chain specific to PH finance control requirements

The custom expense delta **must not reimplement**:

- Baseline `hr_expense` submission, approval, or posting workflow
- Generic tier-validation engine (use OCA `base_tier_validation`)
- Generic DMS / document archival primitives (use OCA `dms` + `dms_field`)
- Generic audit trail infrastructure (use OCA `auditlog`)
- Generic async job processing (use OCA `queue_job`)
- Generic MIS / budget reporting primitives (use OCA `mis_builder`)
- Generic helpdesk / ticketing (use OCA `helpdesk_mgmt`)

### 2.3 OCR bridge boundary

OCR/receipt digitization follows a strict boundary split:

- **External bridge** owns: extraction, classification, confidence scoring
- **Odoo** owns: review queue, attachment linkage, exception handling, posting readiness
- **`queue_job`** is the async orchestration substrate, not business logic

OCR logic must not creep into `ipai_hr_expense_liquidation` or `ipai_expense_ops`.
The bridge module (`ipai_document_intelligence`) is the sole extraction surface.

### 2.4 Proven vs assumed coverage

This spec distinguishes three coverage levels:

- **Proven coverage**: capability is implemented and verified in the current runtime/baseline
- **Declared coverage**: capability is mapped to CE/OCA/custom modules but not runtime-verified here
- **Candidate coverage**: capability likely exists compositionally but needs proof

Architecture claims must not be confused with deployment verification. Status
labels in capability matrices must reflect which level applies.

## 2.5 MVP Doctrine

This feature is an explicit MVP baseline for the IPAI platform workstream.

The TBWA cash advance request and itemized expense/liquidation forms are
the MVP deliverable. Non-MVP bridge capabilities (OCR, AI review, card
feeds, governed Azure runtime) are not required baseline. They are
promotion-lane work.

## 2.6 Addon-first implementation for internal finance forms

TBWA cash advance request and itemized expense/liquidation forms must be
implemented as Odoo addons only.

These forms must not introduce a separate standalone app, parallel workflow
service, or external system of record.

Odoo remains the source of truth for:

- Cash advance requests
- Approvals
- Disbursement status
- Liquidation
- Refund / receivable balance
- Accounting outcomes
- Printable operational forms

External services, if added later, are limited to bounded bridge roles such
as OCR, AI review assistance, or card-feed ingestion and must not replace
the addon-owned workflow truth.

## 3. Mandatory Guardrails

### 3.1 No capability duplication
If CE or OCA provides it, the delta module must not reimplement it.

### 3.2 No deprecated infrastructure
The expense modules must not contain Supabase webhook/event-bus code, n8n
workflow bindings, or other deprecated integration patterns. External
service integration follows current platform doctrine (Azure-native).

### 3.3 No unrelated coupling
The expense modules must not own copilot tool bindings, AI widget patches,
or other features outside expense management scope.

### 3.4 Multi-company by default
All delta models must use `company_id` fields and respect multi-company
rules, consistent with CE/OCA expense behavior.

### 3.5 Branch dependency is acceptable
`ipai_hr_expense_liquidation` depends on `ipai_branch_profile` for
office/branch structure. This is acceptable for a company-specific module
but must be documented as a coupling point.

## 4. OCA Expense Modules (Odoo 18)

### Direct (OCA/hr-expense)

| Module | Capability | Status |
|--------|-----------|--------|
| `hr_expense_advance_clearing` | Cash advance clearing on expense reports | Verified |
| `hr_expense_payment` | Expense payment management | Verified |
| `hr_expense_tier_validation` | Multi-tier expense approval | Verified |
| `hr_expense_sequence` | Expense report sequencing | Verified |
| `hr_expense_advance_clearing_sequence` | Sequenced advance clearing | Verified |

### Adjacent (composable infrastructure)

| Module | Wiring Purpose | Status |
|--------|---------------|--------|
| `dms` + `dms_field` | Receipt attachment archival | Composable candidate |
| `auditlog` | Expense change audit trail | Composable candidate |
| `queue_job` | Async OCR pipeline orchestration | Composable candidate |
| `document_page_approval` | Expense policy versioning | Composable candidate |
| `mis_builder` | Expense budget tracking | Composable candidate |
| `helpdesk_mgmt` | Expense dispute ticketing | Composable candidate |

## 5. Known Gaps

| Gap | Impact | Status |
|-----|--------|--------|
| OCR receipt scanning | CE uses IAP (EE-only), no OCA equivalent | Bridge-required (Azure Document Intelligence) |
| Corporate card feed import | Likely composable via bank/account statement import surfaces, but no proven expense-native CE/OCA pattern yet | Candidate composition / candidate bridge |
| Mileage/per-diem calculator | No CE/OCA module for PH-specific rates | Unresolved |

## 6. MVP Is a Viable Horizontal Slice

For ERP/SaaS-adjacent features, MVP must be defined as the smallest viable
cross-cutting slice that delivers end-to-end value. Avoid isolated
component-only MVPs when the user workflow depends on multiple tightly
connected business objects.

## 7. SaaS and Multitenancy Are Separate Decisions

SaaS is the delivery/business model. Multitenancy is an architecture choice.
Tenant model, data isolation, and shared-component boundaries must be chosen
explicitly per feature.

## 8. External Checklists Inform Review, Not Source-of-Truth Design

Community and external review checklists may be used to validate readiness
and catch omissions, but they do not replace the feature bundle as the
source of truth.

- Azure review checklists are review aids and promotion-lane controls.
- Odoo go-live checklists are operational readiness aids.
- Neither may override Odoo-first workflow/accounting truth or the MVP
  scope defined in this bundle.

## 9. Odoo-Native Testing Is Required

Addon and bridge code must follow Odoo-native testing patterns.

At minimum:

- model/business logic tests use Odoo test case classes
- form-driven behaviors use server-side `Form` tests
- HTTP / tour behavior uses `HttpCase` only where UI flow coverage is actually required
- test selection must be explicit through tags
- browser-critical end-to-end flows may use Playwright where backend/form
  coverage is insufficient
- MVP is not complete without executable tests for core workflows

## 10. Browser Automation Is Targeted, Not Default

Playwright is reserved for browser-critical flows and smoke coverage.
Chrome DevTools is a debugging surface, not the primary test framework.
Manual QA and ad hoc scripts do not replace executable automated tests.

## 11. MCP Tooling Is Optional and Bounded

MCP servers are optional developer and operator tooling surfaces. They
assist with automation, debugging, reference lookup, and platform
validation. They must never own workflow state, business logic, or
approval truth.

Allowed roles:

- Playwright MCP for browser automation
- Chrome DevTools MCP for debugging
- Azure MCP Server for platform/runtime validation
- Microsoft Learn MCP for documentation lookup

Prohibited role: MCP as the primary owner of workflow or business state.

## 12. Experimental MCP Integrations Are Non-Critical

Experimental or preview MCP integrations (e.g., Azure AI Foundry MCP)
must not be on the MVP critical path. They may be evaluated and adopted
when stable, but must not block delivery or become implicit dependencies.

## 13. API Edge Replacement Is Facade-Only

FastAPI or external API layers may replace the public/mobile API edge,
but they must not replace Odoo/OCA as the owner of workflow, approvals,
accounting, tax, or ERP state. The FastAPI edge may package, orchestrate,
proxy, or expose workflows, but Odoo remains the authoritative write path
for all ERP business objects.
