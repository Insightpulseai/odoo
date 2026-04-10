# PRD — Reverse AvaTax for Odoo 18 Pulser

## Problem

External tax engines (Avalara AvaTax, Vertex, Thomson Reuters ONESOURCE)
solve tax calculation and content problems, but can fragment ERP truth if
allowed to own business-state decisions. They create dependency on external
SaaS for every invoice, require expensive per-transaction pricing, and
push tax logic outside the ERP's audit and approval boundaries.

## Users

- Finance controllers
- AP teams
- AR/invoicing teams
- Expense operations
- Country compliance owners
- Tax analysts

## Outcomes

- Pre-posting tax validation with explainable results
- Explainable tax exceptions routed through Pulser review
- Connector-portable tax intelligence (swap engine without core rewrite)
- Pack-based local compliance (BIR, VAT, GST, withholding)
- Odoo-native tax audit trail

---

## 1. Product Name

**Reverse AvaTax** — Odoo-native Tax Intelligence with Pulser

## 2. Product Goal

Replace external tax engine dependency with an Odoo-native tax intelligence
platform that uses connectors for external enrichment and Pulser for
explainable review, while keeping all transactional truth in Odoo.

## 3. Reverse Benchmark

**Benchmark product**: Avalara AvaTax

AvaTax provides real-time tax calculation, address validation, jurisdiction
determination, exemption certificate management, returns filing, and
compliance content updates. It processes billions of tax calculations/year
across 12,000+ jurisdictions.

The reverse move is not to rebuild AvaTax's tax content database. It is to:

- **Own tax computation orchestration** in Odoo, not outsource it
- **Use connectors** for jurisdiction data and rate enrichment, not full delegation
- **Use Pulser** for exception review, not black-box auto-correction
- **Use packs** for local compliance, not monolithic configuration

## 4. Reverse Thesis

AvaTax proves the market values automated tax calculation, jurisdiction
awareness, and compliance content. But the AvaTax model:

- Externalizes tax truth from the ERP
- Creates per-transaction SaaS dependency
- Requires expensive licensing for high-volume scenarios
- Makes tax audit trails span two systems

The reverse:

- **from external tax SaaS** to **Odoo-native tax orchestration**
- **from black-box calculation** to **explainable tax proposals**
- **from per-transaction pricing** to **pack-based local compliance**
- **from external truth** to **connector-enriched Odoo truth**
- **from admin configuration** to **policy-as-code with Pulser review**

## 5. Source-of-Truth Architecture

Odoo CE 18 owns:

- Invoice tax lines
- Vendor bill tax computation
- Expense tax allocation
- Withholding tax records
- Journal entries and postings
- Fiscal positions and tax mappings
- Tax reports and declarations

Connectors may enrich:

- Address normalization / validation
- Jurisdiction determination
- Rate lookups from external sources
- Exemption certificate verification

Pulser may:

- Review tax exceptions
- Explain tax computation rationale
- Route edge cases for human decision
- Audit continuous tax accuracy

## 6. Functional Requirements

### FR-1: Odoo-Native Tax Computation

Tax computation runs inside Odoo's native tax engine (`account.tax`).
External connectors enrich inputs (jurisdiction, rates, exemptions) but
do not replace the computation surface.

### FR-2: Connector-Portable Tax Intelligence

External tax data sources are accessed through swappable connector
contracts. The system must support:

- Address validation connector
- Jurisdiction lookup connector
- Rate enrichment connector
- Exemption verification connector

Connectors are adapters with defined input/output contracts, not embedded
business logic.

### FR-3: Pre-Posting Tax Validation

Before invoice/bill posting, the system validates tax computation against:

- Applicable fiscal position rules
- Jurisdiction-specific rate tables
- Exemption certificates
- Withholding requirements
- Policy pack rules

Validation results are proposals; posting requires approval.

### FR-4: Pulser Tax Review

Pulser provides explainable review for:

- Tax computation exceptions (rate mismatch, jurisdiction ambiguity)
- Missing exemption certificates
- Withholding classification decisions
- Cross-border tax treatment
- Policy pack rule violations

Each review action includes rationale, source inputs, confidence, and
audit trace.

### FR-5: Local Compliance Packs

Pack-based compliance for:

- PH BIR (withholding tax, VAT, percentage tax, expanded withholding)
- Configurable for additional jurisdictions
- Versioned and independently deployable
- Inherit/override semantics for multi-entity scenarios

### FR-6: Tax Audit Trail

Every tax computation, validation, exception, and review action produces:

- Structured audit log entry
- Policy reference
- Computation inputs and outputs
- Human review decisions with reason codes

## 7. Non-Functional Requirements

### NFR-1: Auditability
Every tax decision traceable to inputs, rules, and human decisions.

### NFR-2: Explainability
No autonomous tax action without retrievable explanation.

### NFR-3: Extensibility
New jurisdiction packs installable without core fork.

### NFR-4: Performance
Tax validation must not materially slow invoice posting workflow.

### NFR-5: Multi-Entity
Multi-company, multi-country, multi-currency tax computation.

## 8. MVP Scope

### MVP includes

- Pre-posting validation for draft invoices, vendor bills, and expenses
- Explainable tax exception handling (exception objects, queues, review UI)
- Approval-aware blocking or rerouting on tax exceptions
- Audit trail for every tax computation, validation, and review action
- Connector-bound external tax intelligence as optional enrichment
- Local compliance-pack design surface / boundary (PH BIR as first pack)

### Deferred / post-MVP

- Full multi-country filing automation
- Broad autonomous tax operations
- Mandatory external tax engine dependence
- Global parity claims not yet proven
- Returns filing automation
- Exemption certificate management as standalone product
- Governed Azure landing-zone deployment as default baseline

## 9. Non-Goals

- Rebuilding AvaTax's tax content database
- Real-time tax calculation as external SaaS
- Replacing Odoo's native `account.tax` engine
- Returns filing automation (Phase 2+ scope)
- Exemption certificate management as standalone product

## 10. MVP Framing

MVP is a viable horizontal slice across the minimum required workflow
components, not a disconnected feature fragment.

## 11. External Validation Inputs

This feature may be validated against:

- Azure architecture review checklists for promotion-lane cloud and SaaS controls
- Odoo 18 go-live accounting/operations checklists for cutover and finance readiness

These references support review and go-live readiness only. They do not
redefine MVP scope or architecture ownership.

## 12. Testability Requirements

MVP requires executable Odoo-native tests for all core business flows
introduced by this feature.

Required coverage classes:

- business/model logic
- form/onchange/default behavior
- approval/routing logic
- critical browser flows only where backend/form coverage is insufficient

## 13. Optional Tooling Surfaces

This feature may use MCP servers for testing, debugging, documentation
lookup, and controlled platform operations. These are implementation aids
only and do not redefine product scope or ownership boundaries.

## 14. API Edge Decision

This feature may expose a FastAPI-based Azure API edge as a connector or
review facade, but only as a sidecar. Odoo remains the source of truth
for tax, accounting, invoices, vendor bills, expenses, and related ERP
state. FastAPI may own exception/review/orchestration APIs only. It must
not become a standalone tax ledger.

## 15. SaaS / Tenant Framing

This feature may participate in a SaaS or multitenant operating model, but
tenant boundaries and isolation strategy must be specified explicitly and
must not be assumed.
