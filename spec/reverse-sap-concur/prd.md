# PRD — Reverse SAP Concur on Odoo 18

## 1. Product Name

**Reverse SAP Concur** — Odoo-native Spend Control Plane

## 2. Product Goal

Reverse SAP Concur by productizing and augmenting Odoo CE 18 Finance as a
unified spend control plane, not by building a greenfield autonomous spend OS.

- **System of workflow**: Odoo CE 18 Finance
- **Extension surface**: OCA expense/accounting/document/AI-adjacent modules
- **Digitization bridge**: Azure Document Intelligence
- **AI bridge/orchestration**: OCA `ai_oca_bridge*` modules plus IPAI bridge logic

## 3. Reverse Benchmark

**Benchmark product**: SAP Concur (Expense, Request, Drive, ExpenseIt,
Company Bill Statements, Detect, Travel, TripLink, Invoice, Budget, Analytics)

SAP Concur serves 92M users and processes ~1B expense transactions/year.
Recent 2026 updates add Joule + Microsoft 365 Copilot integration, new
expense automation and pre-submit audit agents, virtual card support, and
real-time card notifications.

The reverse move is not to out-feature SAP Concur SKU-by-SKU. It is to
replace the portfolio of spend products with a unified operating model
built on an existing finance workflow substrate.

## 4. Source-of-Truth Architecture

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

AI and OCR are not treated as replacements for Odoo workflow truth. They are
bridge capabilities layered onto Odoo-owned business objects.

## 5. Reverse Thesis

SAP Concur already proves the market values integrated travel, expense,
invoice, request, mileage, p-card, analytics, and audit workflows.

The reverse move:
- **from product family** to **operating model on existing ERP finance**
- **from report-centric** to **event-centric**
- **from exception review** to **prevention**
- **from AI assistant** to **AI bridge with policy gates**
- **from admin configuration** to **policy-as-code**
- **from closed suite** to **open control plane on Odoo + OCA + Azure**

The sharper positioning:

> Reverse SAP Concur on Odoo CE 18 by treating Odoo Finance as the
> transactional spend workflow core, OCA as the composition layer,
> Azure Document Intelligence as the extraction/classification bridge,
> and OCA AI bridges as the controlled AI ingress path.

## 6. Capability Allocation

### CE-native (proven)

- Expense submission/reporting/reimbursement
- Accounting posting
- Analytic distribution
- Budgets / analytic accounting
- Withholding tax support
- Bank sync / reconciliation
- Receipt attachment / upload / email ingestion
- Multi-currency / multi-company

### OCA-native / composable

- Cash advance / clearing lifecycle (`hr_expense_advance_clearing`)
- Multi-tier approval routing (`hr_expense_tier_validation`)
- Payment management (`hr_expense_payment`)
- Sequencing (`hr_expense_sequence`)
- AI bridge modules (`ai_oca_bridge*`)
- Document archival (`dms`, `dms_field`)
- Audit trails (`auditlog`)
- Async processing (`queue_job`)
- Budget reporting (`mis_builder`)
- Document/approval surfaces (`document_page_approval`)

### External bridge

- Azure Document Intelligence for OCR / classification / extraction
- Confidence-scored outputs feeding Odoo review queues

### Thin IPAI delta

- Company/country-specific policy logic
- Expense-review orchestration
- PH compliance, liquidation, and exception semantics
- BIR validation hooks

## 7. Functional Requirements

### FR-1: Unified Spend Graph

One canonical graph linking: employee, approver, cost object, budget,
request, trip, booking, card, transaction, receipt, expense line, invoice,
merchant, policy, tax profile, reimbursement, audit case.

Built on Odoo's existing relational model, not a parallel data store.

### FR-2: Event-Centric Spend Lifecycle

Spend as a continuous lifecycle: pre-spend request, transaction event,
evidence capture, policy evaluation, approval, posting, payment/reimbursement,
audit, recovery/remediation.

### FR-3: Unified Policy Engine

Policy-as-code across: request, booking, card, expense, invoice, budget,
audit, and local compliance rules. Extends Odoo's existing approval and
analytic controls.

### FR-4: Autonomous Drafting

Auto-create draft spend cases from: travel bookings, card swipes, uploaded
receipts, emailed invoices, mileage events, ERP events. Drafts are
advisory — employee reviews, not AI.

### FR-5: AI Bridge with Explainability

AI enters through OCA bridge modules. Each AI action must emit: rationale,
referenced policy, confidence level, reversible action log. AI must not
directly mutate posted accounting state.

Actions are classified as:
- Advisory (suggest, no state change)
- Blocking (flag, require human decision)
- Auto-routable (low-risk, policy-compliant, auto-approve with audit log)

### FR-6: Card-Native Control

Live card transaction ingestion, virtual cards, merchant/category controls,
personal vs business classification, card-to-trip and card-to-request linkage.
Corporate card feeds are candidate composition via bank/account statement
import surfaces.

### FR-7: Travel + Expense Convergence

Unify travel request, itinerary, booking, expected expenses, out-of-policy
review, post-trip reconciliation under one Odoo-native flow.

### FR-8: AP + Employee Spend Convergence

Both employee-paid reimbursement flows and company-paid / AP / invoice /
p-card flows under one spend model in Odoo.

### FR-9: Local Compliance Packs

Packaged country/region policy packs for: receipt compliance, VAT/GST,
withholding, mileage/per diem, evidence retention, approval delegation,
statutory audit requirements. PH pack is the first implementation.

### FR-10: Continuous Audit

Risk scoring before and after payment: duplicates, merchant anomalies,
route anomalies, split transactions, timing anomalies, policy circumvention,
peer deviation. Built on Odoo data, surfaced via bridge AI.

### FR-11: Unified Operator Console

One console for: spend queue, exceptions, risk cases, reimbursement status,
card program monitoring, country pack health, automation success/failure.

### FR-12: Open Integration Fabric

APIs and adapters for: ERP/GL (Odoo-native), HRIS, IdP/SSO (Entra),
travel providers, OCR providers (Azure Doc Intelligence), card issuers,
BI (Power BI), document storage (DMS), event bus (queue_job).

## 8. Non-Functional Requirements

### NFR-1: Auditability
Every state transition, rule evaluation, override, and AI action logged immutably.

### NFR-2: Explainability
No autonomous action without a retrievable explanation.

### NFR-3: Extensibility
Country packs, policy packs, and connectors installable without core fork.

### NFR-4: Latency
Card-event policy decisions complete fast enough for near-real-time control.

### NFR-5: Multi-Entity Support
Multi-company, multi-country, multi-currency operations.

### NFR-6: Data Portability
Full spend graph data and rule history exportable without lock-in.

## 9. Differentiators vs SAP Concur

1. **Built on existing ERP finance**, not a parallel spend silo
2. **Event-first model** instead of report-first model
3. **Policy-as-code** instead of admin-heavy configuration sprawl
4. **AI through bridge pattern**, not opaque embedded intelligence
5. **Card and invoice parity** inside the same Odoo control plane
6. **Local compliance packs** as first-class versioned artifacts
7. **Open composition** via OCA + Azure services
8. **Operator console** for finance/audit, not just employee workflow polish

## 10. MVP Scope

### MVP includes

- Cash advance request lifecycle (request, approval, release, monitoring)
- Cash advance monitoring (queues, statuses, overdue tracking)
- Liquidation / itemized expense linked to advance
- Settlement computation (due to employee / refundable from employee)
- Finance review / posting / approval metadata
- Printable QWeb reports matching current operational forms
- Lightweight mobile companion:
  - Request and approval status
  - Advance monitoring
  - Liquidation reminders
  - Limited companion actions (mobile reads/writes through Odoo workflows only)

### Deferred / post-MVP

- Mandatory OCR / receipt scanning baseline
- Mandatory AI review baseline
- Mandatory corporate card feed baseline
- Mobile-first capture as required baseline
- External tax enrichment as required baseline
- Standalone Concur-style platform behavior
- Governed Azure landing-zone deployment as default baseline
- Full AP/invoice convergence (Phase 4 scope)
- Full continuous anomaly detection (Phase 3 scope)

## 11. Explicit Non-Goals

- Recreating SAP Concur's SKU map one-for-one
- Building a greenfield spend OS that ignores Odoo's existing surface
- Treating AI as a chatbot or embedding it in accounting core
- Limiting to post-spend reimbursement only
- Requiring services-heavy implementation for basic policy rollout
- Full task dependency / CPM scheduling (PPM scope, not expense)

## 11. Success Metrics

### Adoption
- >85% of spend events auto-draft without manual report creation
- >70% of low-risk cases resolve without human finance touch
- >90% of employees complete submission in under 3 minutes

### Control
- 50% reduction in post-payment audit workload
- 40% reduction in policy-violation reimbursement events
- 30% reduction in approval-cycle time

### Data Quality
- <2% uncategorized spend after human review
- >95% evidence attachment completeness before final submission
- >99% traceability from transaction to policy decision to posting

### Platform
- <30-day baseline rollout for standard customers
- <7-day deployment of a new country compliance pack
- <1-day onboarding for new card program or OCR adapter

## 12. Phased Delivery

### Phase 1 — Autonomous Expense Core
- Unified spend graph on Odoo CE 18
- Receipt/card/travel ingestion via bridges
- Autonomous draft expense cases
- Explainable approval routing
- Basic reimbursement + posting

### Phase 2 — Card and Request Control Plane
- Virtual cards
- Live card eventing
- Pre-spend authorization
- Budget envelopes
- Merchant/category control

### Phase 3 — Audit and Local Compliance
- Continuous anomaly detection
- PH country pack (BIR, liquidation, receipt rules)
- Tax/evidence packs
- Recovery/remediation workflows

### Phase 4 — Full Spend Control Plane
- AP/invoice convergence
- Sourcing/procurement hooks
- Benchmarking and simulation
- Optimization recommendations
- Autonomous finance operations console

## 13. Delivery Topology

The product has two sanctioned Azure delivery paths:

### Lane A — Lightweight implementation path

Use a focused Azure accelerator/template for:

- Agent workflow shell
- Chat/review UI
- Multimodal document processing (receipt/invoice extraction)
- Managed-identity-secured model access

This path is preferred for first receipt/OCR/review-agent delivery.

### Lane B — Production governed path

Use the Microsoft "Deploy Your AI Application In Production" accelerator
when the target requires:

- Azure AI Foundry
- Azure AI Search
- Optional Fabric / Purview
- Private networking
- Managed identities with landing-zone controls
- `azd`-driven environment provisioning

This path is for governed production rollout, not the default baseline for
early expense capability delivery.

### Delivery selection rule

Do not start the expense/Concur-reverse implementation on the heavyweight
landing-zone accelerator by default.

Use the heavyweight path only when the workload explicitly requires:

- Production-grade private networking
- Foundry-centered agent hosting
- Enterprise governance hooks (compliance, data classification)
- Broader data foundation / search integration

Otherwise, begin with a narrower template and promote later. The Microsoft
production repo explicitly states it is heavier than needed for a small
Foundry demo or basic RAG sample, and recommends a lowest-risk first run
with Fabric and Purview disabled unless prerequisites already exist.

## 14. Risks

- Over-automation without explainability reduces trust
- Local compliance breadth can explode scope without pack-based approach
- Travel + expense + AP convergence can bloat without one-graph discipline
- Real-time card controls require reliable issuer/network integrations
- AI autonomy must be reversible and tightly permissioned
- OCA AI modules are on 18.0 but maturity varies — verify per-module

## 15. MVP Framing

MVP is a viable horizontal slice across the minimum required workflow
components, not a disconnected feature fragment.

## 16. External Validation Inputs

This feature may be validated against:

- Azure architecture review checklists for promotion-lane cloud and SaaS controls
- Odoo 18 go-live accounting/operations checklists for cutover and finance readiness

These references support review and go-live readiness only. They do not
redefine MVP scope or architecture ownership.

## 17. Testability Requirements

MVP requires executable Odoo-native tests for all core business flows
introduced by this feature.

Required coverage classes:

- business/model logic
- form/onchange/default behavior
- approval/routing logic
- settlement/totals logic where applicable
- critical browser flows only where backend/form coverage is insufficient

## 18. Optional Tooling Surfaces

This feature may use MCP servers for testing, debugging, documentation
lookup, and controlled platform operations. These are implementation aids
only and do not redefine product scope or ownership boundaries.

## 19. API Edge Decision

This feature may expose a FastAPI-based Azure API edge, but only as a
facade or sidecar. Odoo remains the source of truth for workflow,
approvals, accounting, tax, expenses, and related ERP state. The mobile
companion and cash advance monitoring APIs may use FastAPI as an external
surface, but all write paths must go through Odoo-owned services.

## 20. SaaS / Tenant Framing

This feature may participate in a SaaS or multitenant operating model, but
tenant boundaries and isolation strategy must be specified explicitly and
must not be assumed.
