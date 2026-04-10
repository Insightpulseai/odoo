# PRD — Expense Management Parity for Odoo 18

## 1. Product Name

**Expense Management Parity for Odoo 18** (CE + OCA + thin delta + bridges)

## 2. Product Goal

Formalize the expense management stack as a CE/OCA-first composition with
justified custom delta for PH-specific liquidation and compliance workflows.

## 3. Reverse Benchmark

**Benchmark product**: SAP Concur Expense

SAP Concur provides expense report management, receipt capture, travel booking,
approval routing, policy enforcement, corporate card reconciliation, mileage
tracking, and analytics. It is heavyweight, expensive, and not Odoo-native.

The target is to achieve >=80% Concur Expense capability parity using Odoo CE
and OCA modules, with custom code only for PH-specific features and external
service bridges.

## 4. Current State

### Architecture assessment

Unlike the PPM case, the expense stack is **already correctly layered**:

- CE `hr_expense` serves as the execution baseline
- OCA `hr-expense` modules extend with cash advance, approval, payment
- Two custom modules (`ipai_hr_expense_liquidation` v3, `ipai_expense_ops` v1)
  are scoped to PH-specific delta
- No monolithic overreach, no deprecated infrastructure residue

**No architectural rewrite required; only boundary hardening, adjacent-module
wiring, and proof of current install/runtime state.**

### Custom module inventory

| Module | Version | Models | Assessment |
|--------|---------|--------|-----------|
| `ipai_hr_expense_liquidation` | v18.0.3.0.0 | `cash.advance`, `cash.advance.line`, `hr.expense.liquidation`, `hr.expense.liquidation.line`, `hr.expense.policy.rule`, `hr.expense.policy.violation` | **Keep** — justified PH liquidation delta |
| `ipai_expense_ops` | v18.0.1.0.0 | Compliance exception model, 5-level approval chain | **Keep** — justified PH compliance delta |

## 5. Proven vs Assumed Coverage

This artifact distinguishes:

- **Proven coverage**: capability is implemented and verified in the current runtime/baseline
- **Declared coverage**: capability is mapped to CE/OCA/custom modules but not runtime-verified here
- **Candidate coverage**: capability likely exists compositionally but needs proof

Status labels in the capability matrix below reflect which level applies.
Architecture truth must not be confused with deployment verification.

## 6. Capability Matrix

| Capability | Concur Equivalent | Source | Status |
|---|---|---|---|
| Expense report creation & submission | Core | **CE** `hr_expense` | Verified in current baseline |
| Multi-currency expense entry | Core | **CE** `hr_expense` | Verified in current baseline |
| Analytic account allocation | Core | **CE** `hr_expense` | Verified in current baseline |
| Duplicate detection | Core | **CE** `hr_expense` (hash-based) | Verified in current baseline |
| Manager approval routing | Core | **CE** `hr_expense` | Verified in current baseline |
| Vendor bill / payment posting | Core | **CE** `hr_expense` | Verified in current baseline |
| Reinvoicing to customers | Core | **CE** `sale_expense` | Verified in current baseline |
| Cash advance request & clearing | Cash Advance | **OCA** `hr_expense_advance_clearing` | Verified in current baseline |
| Advance clearing sequencing | Cash Advance | **OCA** `hr_expense_advance_clearing_sequence` | Verified in current baseline |
| Expense payment management | Payments | **OCA** `hr_expense_payment` | Verified in current baseline |
| Expense report sequencing | Operations | **OCA** `hr_expense_sequence` | Verified in current baseline |
| Multi-tier approval (configurable) | Approval Engine | **OCA** `hr_expense_tier_validation` + `base_tier_validation` | Verified in current baseline |
| Cash advance lifecycle (3 types) | Liquidation | **Delta** `ipai_hr_expense_liquidation` v3 | Verified in current baseline |
| Policy engine (limits, receipts, overdue) | Policy | **Delta** `ipai_hr_expense_liquidation` | Verified in current baseline |
| Idempotent accounting entries | Accounting | **Delta** `ipai_hr_expense_liquidation` | Verified in current baseline |
| Overdue monitoring cron | Monitoring | **Delta** `ipai_hr_expense_liquidation` | Verified in current baseline |
| 5-step compliance approval chain | Compliance | **Delta** `ipai_expense_ops` | Verified in current baseline |
| BIR validation hook | Tax Compliance | **Delta** `ipai_expense_ops` | Verified in current baseline |
| Compliance exception/violation model | Audit | **Delta** `ipai_expense_ops` | Verified in current baseline |
| Receipt document archival | DMS | **OCA** `dms` + `dms_field` | Composable candidate |
| Policy document versioning | Compliance | **OCA** `document_page_approval` | Composable candidate |
| Async OCR processing | Digitization | **OCA** `queue_job` + **Azure** Doc Intelligence | Composable candidate |
| Audit trail on expense changes | Audit | **OCA** `auditlog` | Composable candidate |
| Budget-vs-actual for expense budgets | Finance | **OCA** `mis_builder` | Composable candidate |
| Expense dispute ticketing | Support | **OCA** `helpdesk_mgmt` | Composable candidate |
| OCR receipt scanning | Digitization | **Bridge** — CE uses IAP (EE-only), no OCA equivalent | Bridge-required |
| Corporate card feed import | Card Mgmt | Likely composable via bank/account statement import surfaces, but no proven expense-native CE/OCA pattern yet | Candidate composition / candidate bridge |
| Mileage/per-diem calculator | Travel | No CE/OCA module for PH rates | Unresolved |
| Mobile receipt capture (native) | Mobile | CE web only | Unresolved |

## 7. Sourcing Doctrine Result

```
Config -> OCA -> Delta (ipai_*)
```

| Layer | Module Count | Coverage |
|---|---|---|
| **CE `hr_expense` baseline** | 1 core + 3 auto-deps | ~40% — core ops, workflow, posting |
| **OCA direct** (hr-expense repo) | 5 installed | ~20% — cash advance, approval, sequencing |
| **OCA adjacent** (composable) | 6 available | ~10% — archival, audit, async, budget |
| **Custom delta** | 2 modules | ~20% — PH liquidation, BIR compliance |
| **Known gaps** | 4 capabilities | ~10% — OCR, card feeds, mileage, mobile |

**Verdict**: The sourcing doctrine is already correctly applied. The custom
modules are justified delta, not monolithic overreach.

## 8. Custom Delta Boundary

### `ipai_hr_expense_liquidation` v18.0.3.0.0 — KEEP (justified)

| Model | Purpose | CE/OCA Alternative |
|---|---|---|
| `cash.advance` | Pre-spend request with 3 types | None — OCA covers clearing but not the full request lifecycle |
| `cash.advance.line` | Line items for advance requests | None |
| `hr.expense.liquidation` | Liquidation header (links advance to expense) | None |
| `hr.expense.liquidation.line` | Liquidation line items | None |
| `hr.expense.policy.rule` | Configurable policy rules | None |
| `hr.expense.policy.violation` | Violation records from policy engine | None |

Depends: `base`, `hr`, `hr_expense`, `account`, `calendar`, `ipai_branch_profile`

### `ipai_expense_ops` v18.0.1.0.0 — KEEP (justified)

| Feature | Purpose | CE/OCA Alternative |
|---|---|---|
| 5-level approval chain | Manager, Budget, Cost Object, External, Accounting | OCA `base_tier_validation` provides the framework but not the specific chain |
| BIR compliance hook | Philippine tax validation on expense reports | None — jurisdiction-specific |
| Compliance exception model | Structured violation/exception tracking | OCA `base_exception` provides framework but not expense-specific rules |

Depends: `hr_expense`, `mail`

### Custom delta doctrine

The custom expense delta **may own**:
- PH liquidation lifecycle
- PH compliance/policy semantics
- Expense-specific exception models
- Orchestration hooks into bridge services

The custom expense delta **must not reimplement**:
- Baseline `hr_expense` submission/posting
- Generic tier-validation engine
- Generic DMS / audit / queue primitives
- Generic MIS reporting primitives

## 9. External Bridge Boundary

| Capability | Bridge Target | Module | Status |
|---|---|---|---|
| Receipt OCR/digitization | Azure Document Intelligence | `ipai_document_intelligence` | Exists in `addons/ipai/` |
| Corporate card feed | Bank statement import | CE `account_bank_statement_import` + OCA `account_statement_import_*` | Candidate — evaluate |
| Mileage/per-diem | PH DOLE/BIR rate tables | Future `ipai_expense_travel` | Not started |

### OCR orchestration boundary

- **Bridge** owns: extraction, classification, confidence scoring
- **Odoo** owns: review queue, attachment linkage, exception handling, posting readiness
- **`queue_job`** is the async orchestration substrate, not business logic

The bridge module (`ipai_document_intelligence`) is the sole extraction surface.
OCR logic must not creep into `ipai_hr_expense_liquidation` or `ipai_expense_ops`.

## 10. MVP Scope

### MVP includes

- Cash advance request lifecycle (request, approval, release/disbursement)
- Liquidation / itemized expense linked to advance
- Net due / refundable computation
- Finance review / posting / approval metadata
- Printable QWeb outputs matching current TBWA paper forms
- Cash advance monitoring views / queues / statuses

### Deferred / post-MVP

- OCR as required baseline
- AI review as required baseline
- Mobile-first capture as required baseline
- Corporate card feeds as required baseline
- External tax enrichment as required baseline
- Standalone platform behavior
- Governed Azure landing-zone deployment as default baseline

## 11. Scope Decision

The TBWA cash advance request form and TBWA itemized expense report /
liquidation form are in scope as addon-only functionality inside Odoo 18.

This feature does not require:

- A standalone expense application
- A separate web portal
- A separate workflow engine
- An external document system as the primary user surface

The required deliverable is:

- Addon data model support
- Addon workflow support
- Addon totals / settlement logic
- Addon printable QWeb reports that match current paper forms closely enough
  for operational continuity

## 12. Functional Scope — TBWA Forms

### Cash advance request

The addon must support:

- Payee
- Department
- Date needed
- Travel / event dates
- Payment method
- Purpose-of-advance rows
- Amount rows
- Client name
- CE number if chargeable
- Requester acknowledgment / signature metadata
- Approver metadata
- Finance metadata

### Itemized expense / liquidation

The addon must support:

- Employee / preparer
- Department or group
- Date prepared
- Related cash advance reference
- Line-item dates
- Particulars
- Client
- CE number if chargeable
- Meals
- Transpo
- Misc
- Page totals
- Prior-page carry totals where applicable
- Grand total
- Cash advanced
- Amount due to or refundable from agency
- Finance posting / review / approval metadata

## 13. Explicit Non-Goals

- Rebuilding OCA expense capabilities inside custom modules
- Treating `ipai_hr_expense_liquidation` as a monolithic Concur replacement
- Claiming complete Concur parity while known gaps remain
- Retaining deprecated external integration patterns
- Full corporate card program management (known gap)
- Native mobile receipt capture (EE-only, no CE/OCA equivalent)
- OCR capture as a required baseline
- Mobile-first capture as a required baseline
- Corporate card feed integration as a required baseline
- Autonomous AI review as a required baseline
- Replacement of Odoo accounting or approval workflows
- Creation of a Concur-style standalone platform for these forms

## 14. Success Metrics

- >=80% Concur Expense capability covered by CE + OCA + delta + bridges
- Custom delta limited to 2 modules (liquidation + ops)
- Zero deprecated infrastructure code in expense modules
- All generic expense features served by CE/OCA, not custom code
- Known gaps documented in SSOT parity matrix
- Adjacent OCA modules wired into expense flow where composable

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
- settlement/totals logic
- critical browser flows only where backend/form coverage is insufficient

## 18. Optional Tooling Surfaces

This feature may use MCP servers for testing, debugging, documentation
lookup, and controlled platform operations. These are implementation aids
only and do not redefine product scope or ownership boundaries.

## 19. API Edge Decision

This feature may expose a FastAPI-based Azure API edge, but only as a
facade or sidecar. Odoo remains the source of truth for workflow,
approvals, accounting, expenses, liquidations, and related ERP state.
FastAPI may be used for mobile/external API packaging only.

## 20. SaaS / Tenant Framing

This feature may participate in a SaaS or multitenant operating model, but
tenant boundaries and isolation strategy must be specified explicitly and
must not be assumed.
- Adjacent OCA modules wired into expense flow where composable
