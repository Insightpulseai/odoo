# TaxPulse BIR Integration — Implementation Plan

> Spec bundle: `spec/taxpulse-bir-integration/`
> Status: Active
> Last updated: 2026-04-02

---

## Implementation Plan

### Phase 1 — Filing Prep and Payment Orchestration

**Goal**: End-to-end filing preparation from Odoo data through payment handoff.

Deliver:
- **Tax period workbench** — entity + period + tax type matrix with readiness indicators
- **Filing-pack generator** — Odoo data extraction, tax base computation, pre-filled form output (XML/CSV per BIR spec)
- **eBIRForms / eFPS routing logic** — taxpayer classification lookup, channel recommendation with rationale
- **Payment summary and ePAY handoff state** — payment amount computation, channel options (AABs, GCash, PayMaya, LandBank), payment reference capture
- **Filing timeline model** — state machine: `draft` -> `prepared` -> `validated` -> `filed` -> `payment_pending` -> `paid`
- **Exception engine** — blocking-item detection, resolution hints, explicit human-action-required queue

Dependencies:
- Odoo 18 accounting module with PH chart of accounts
- BIR form specifications (field layouts, computation rules) per form type
- Taxpayer classification data (large taxpayer flag, RDO assignment)

### Phase 2 — eAFS Submission Pack and Evidence

**Goal**: Complete the filing lifecycle with attachment submission and immutable evidence capture.

Deliver:
- **eAFS attachment pack builder** — form-specific attachment manifest (AFS, SAWT, MAP, QAP, BIR Form 2307)
- **Attachment checklist validation** — per-form required document list, metadata completeness enforcement (TIN, period, form type, page count)
- **TRN / Confirmation Receipt capture** — structured capture flow with operator confirmation
- **Evidence store per filing period** — append-only evidence records with artifact links, timestamps, and operator attribution
- **Filing-period evidence checklist** — visual checklist showing which evidence milestones are captured vs pending
- **Completion gate** — prevent terminal state without required evidence artifacts

Dependencies:
- Phase 1 filing timeline model
- RMC 17-2024 attachment requirements
- Odoo document/attachment storage integration

### Phase 3 — ORUS Registration Workflow Support

**Goal**: Structured workflow support for BIR registration operations.

Deliver:
- **Taxpayer registration status model** — TIN, RDO, business activity, registration type, lifecycle state
- **Registration update task flow** — guided workflow for RDO transfer, activity update, closure
- **Registration metadata completeness checks** — required-document checklist per registration action
- **ORUS task queue / operator worklist** — pending registration actions with priority and deadlines

Dependencies:
- Phase 1 entity model (taxpayer/entity records)
- BIR ORUS requirements per registration action type

### Phase 4 — eTSPCert Readiness

**Goal**: Prepare evidence and validation infrastructure for future BIR software certification.

Deliver:
- **Versioned output schemas** — BIR form field mappings with version tracking (form layout changes across BIR revisions)
- **Validation rules registry** — computation accuracy rules, cross-form consistency checks, BIR test case validation
- **Evidence pack for product/compliance alignment** — structured evidence bundle demonstrating output fidelity
- **Release gate for BIR-output changes** — CI/manual gate preventing BIR form output changes without validation re-run

Dependencies:
- Phase 1 filing-pack generator (output schemas)
- BIR form specifications with revision history
- eTSPCert requirements documentation (when published)

---

## Architecture

### Source of Record (SoR)
- **Odoo 18** remains the source of record for accounting and tax-source data.
- TaxPulse never duplicates Odoo ledger data. It reads via Odoo ORM (for Odoo-hosted modules) or FastAPI endpoints (for external agent access).
- Chart of accounts, journal entries, partner records, withholding agent setup, and document attachments all originate from Odoo.

### Control Plane
- **TaxPulse** owns:
  - Form/workflow mapping (which BIR forms apply to which entity/period/tax type)
  - Validation (data completeness, computation accuracy, cross-form reconciliation)
  - Readiness classification (ready, blocked, awaiting human action)
  - Evidence capture (filing references, payment references, eAFS TRN, artifacts)
  - Operator status and audit timeline (who did what, when)
  - Exception management (blocking items, resolution hints)

### Evidence Model
Per filing period, persist (append-only, immutable):

| Field | Type | Description |
|-------|------|-------------|
| `entity_id` | FK | Taxpayer entity |
| `period` | Date range | Filing period (month, quarter, annual) |
| `tax_type` | Selection | Income tax, VAT, withholding, percentage, etc. |
| `filing_channel` | Selection | eBIRForms, eFPS |
| `filing_reference` | Char | BIR filing confirmation number |
| `payment_channel` | Selection | AAB, GCash, PayMaya, LandBank |
| `payment_reference` | Char | Payment confirmation number |
| `payment_amount` | Monetary | Amount paid |
| `eafs_trn` | Char | eAFS Transaction Reference Number |
| `eafs_confirmation` | Char | eAFS Confirmation Receipt number |
| `timestamps` | JSON | Milestone timestamps (prepared, filed, paid, submitted, evidenced) |
| `actor_id` | FK | Operator who performed the action |
| `artifact_ids` | M2M | Linked evidence documents (receipts, screenshots, PDFs) |
| `notes` | Text | Operator notes or exception details |

### Module Structure

| Module | Purpose |
|--------|---------|
| `ipai_taxpulse_core` | Filing period model, state machine, evidence store |
| `ipai_taxpulse_filing` | Filing-pack generator, form mappings, channel routing |
| `ipai_taxpulse_payment` | Payment orchestration, channel handoff, reference capture |
| `ipai_taxpulse_eafs` | Attachment pack builder, eAFS validation, TRN capture |
| `ipai_taxpulse_orus` | Registration workflow, ORUS task queue |
| `ipai_taxpulse_cert` | eTSPCert readiness, output validation, schema versioning |

---

## Delivery Rules

1. **Assisted workflow before deep direct integration.** Every feature must work as operator-guided workflow before any direct BIR API path is considered.
2. **No public feature may imply BIR submission certainty without stored evidence.** UI and API must never indicate "filed" or "paid" without a captured reference.
3. **Every filing state transition must be traceable and reviewable.** All transitions are logged with actor, timestamp, and reason.
4. **Evidence is required for completion.** A filing period cannot reach terminal state without: filing reference (where applicable), payment reference (where applicable), and eAFS TRN / Confirmation Receipt (where applicable).
5. **PH grounding hierarchy applies.** Tax computation rules and form specifications must cite BIR primary sources (NIRC, RMCs, RMOs, RRs). AvaTax patterns inform API design quality only.
6. **Degrade gracefully.** When BIR portals are unavailable or change behavior, TaxPulse must not block the operator. Allow manual override with evidence capture.
