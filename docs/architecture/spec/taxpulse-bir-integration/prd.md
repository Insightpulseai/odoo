# TaxPulse BIR Integration — PRD

> Spec bundle: `spec/taxpulse-bir-integration/`
> Status: Active
> Last updated: 2026-04-02

---

## Scope

TaxPulse will support the BIR operating workflow in this priority order:

### P0 Operational Lane
1. **eBIRForms / eFPS** — preparation and filing-assist workflows for periodic returns (income tax, VAT, withholding tax, percentage tax)
2. **ePAY** — payment orchestration with channel routing (AABs, GCash, PayMaya, land bank link.bizportal)
3. **eAFS** — attachment-pack generation and submission evidence capture (AFS, SAWT, MAP, BIR Form 2307, QAP)

### P1 Administrative / Compliance Lane
4. **ORUS** — registration and registration-update support (new TIN, RDO transfer, business activity update, closure)
5. **eTSPCert** — certification-readiness controls for tax software outputs (form layout fidelity, computation accuracy, data mapping validation)

### P2 Specialized Lane
6. **eONETT** — one-time transaction tax (CGT, DST on property transfers)
7. **eTCBP-TCVC** — tax clearance for bidding purposes and tax compliance verification certificate
8. **eTCS** — electronic tax compliance system

---

## Problem Statement

Current tax operations are fragmented across return preparation, filing, payment, and attachment submission. Each BIR eService operates as an isolated channel with its own authentication, data format, and confirmation mechanism. This creates:

- **Manual reconciliation overhead** — operators cross-reference Odoo accounting data against multiple BIR portals per period
- **Status ambiguity** — no single view of whether a period is prepared, filed, paid, and attachment-submitted
- **Evidence gaps** — filing receipts, payment confirmations, and eAFS TRNs are stored ad hoc (email, screenshots, local folders) rather than linked to the accounting period
- **Compliance drift** — without structured readiness checks, filings may proceed with incomplete data or stale reconciliation

TaxPulse must reduce manual reconciliation and status ambiguity by treating Odoo as the accounting source of record and TaxPulse as the BIR workflow/control layer.

---

## Product Position

TaxPulse is **not** assumed to be a direct BIR API replacement. The initial product posture is **workflow-assist first**:

1. **Prepare** compliant filing data and attachment packs from Odoo source data
2. **Orchestrate** taxpayer/operator actions across BIR systems with structured handoff
3. **Capture** proof-of-filing / proof-of-submission / proof-of-payment artifacts
4. **Maintain** an auditable filing timeline per entity and period

Direct system-to-system submission is treated as a capability upgrade path, enabled only where BIR formally supports API-based filing (currently limited to eFPS for large taxpayers and select eBIRForms scenarios).

---

## External Systems of Record

| System | Role | Data Flow |
|--------|------|-----------|
| **Odoo 18** | Accounting SoR | Tax bases, journals, partner records, attachments, chart of accounts, withholding agent setup |
| **BIR eBIRForms** | Filing channel (offline/online) | Form data export -> manual upload or guided filing |
| **BIR eFPS** | Filing channel (online, large taxpayers) | Form data export -> guided filing |
| **BIR ePAY** | Payment channel | Payment summary -> channel handoff -> payment reference capture |
| **BIR eAFS** | Attachment submission rail | Attachment pack -> upload -> TRN / Confirmation Receipt capture |
| **BIR ORUS** | Registration/update rail | Registration metadata -> guided workflow -> status capture |
| **BIR eTSPCert** | Software certification rail | Output validation -> compliance evidence pack |

---

## Key Assumption

This spec assumes **workflow-assist and evidence-capture integration first**.

- Direct system-to-system filing/payment submission is treated as a later capability and only where formally supported by BIR.
- BIR portal behavior is volatile (maintenance windows, UI changes, authentication shifts). TaxPulse must degrade gracefully when portals are unavailable.
- The operator is always in the loop for filing submission and payment confirmation. No autonomous filing without explicit operator confirmation and evidence capture.

---

## Functional Requirements

### FR-1 Filing Pack Generation
The system shall generate filing-ready period packs for supported BIR forms using Odoo source data. Each pack includes:
- Computed tax bases per form line item
- Pre-filled form data (XML or CSV per BIR form spec)
- Validation summary (completeness, arithmetic consistency, cross-form reconciliation)
- Filing channel recommendation (eBIRForms vs eFPS based on taxpayer classification)

### FR-2 Filing Status Timeline
The system shall track filing status by entity, tax type, filing period, and BIR channel. States include: `draft`, `prepared`, `validated`, `filed`, `payment_pending`, `paid`, `attachment_pending`, `evidenced`, `complete`. Each transition records timestamp, actor, and reference.

### FR-3 Payment Orchestration
The system shall generate payment-ready summaries and route the operator to the applicable ePAY / payment path. Supported channels: AABs (authorized agent banks), GCash, PayMaya, LandBank Link.BizPortal. The system captures the payment reference number, channel, amount, and timestamp upon operator confirmation.

### FR-4 eAFS Attachment Pack
The system shall build eAFS-ready attachment bundles per RMC 17-2024 and applicable RMOs. Required attachments are form-specific (AFS, SAWT, MAP, QAP, BIR Form 2307, etc.). The system enforces metadata completeness (TIN, period, form type, page count) and stores the resulting TRN / Confirmation Receipt as submission evidence.

### FR-5 Evidence Capture
The system shall store per filing period:
- Filing reference / confirmation number
- Payment reference number, channel, and amount
- eAFS TRN / Confirmation Receipt
- Timestamps for each milestone
- Operator attribution (who performed each action)
- Artifact links (uploaded receipts, screenshots, PDF confirmations)

Evidence records are append-only and immutable.

### FR-6 Registration Support
The system shall maintain ORUS-related registration workflow status and required taxpayer registration metadata. Supported workflows: new TIN application, RDO transfer, business activity update, and business closure. The system tracks required documents, submission status, and BIR acknowledgment.

### FR-7 Certification Readiness
The system shall maintain versioned output mappings, validation rules, and evidence needed to support future eTSPCert alignment. This includes:
- BIR form layout fidelity checks (field positions, computed totals)
- Computation accuracy validation against BIR test cases
- Data mapping registry (Odoo field -> BIR form field)
- Version tracking for BIR form changes

### FR-8 Exception Handling
The system shall explicitly classify periods/workflows as:
- `ready` — all data present, validated, ready to proceed
- `blocked_missing_data` — specific Odoo records or documents are absent
- `blocked_reconciliation` — unresolved reconciliation items prevent accurate filing
- `awaiting_human_action` — operator must complete a manual step (e.g., portal upload, payment)
- `submitted` — filing or attachment submitted, awaiting confirmation
- `paid` — payment confirmed with reference
- `evidenced` — all required evidence artifacts captured and linked

Each exception state includes a resolution hint and the specific blocking items.

---

## Non-Goals (Initial Release)

- **No universal direct API submission** — BIR does not expose stable public APIs for all eServices. Do not build integrations against undocumented or unsupported endpoints.
- **No ONETT-first workflows** — eONETT is P2 scope. One-time transaction workflows are deferred.
- **No tax clearance as blocker** — eTCBP-TCVC and eTCS are P2. Do not gate P0/P1 delivery on clearance capabilities.
- **No inventing unpublished BIR interfaces** — only integrate with documented, publicly available BIR eService channels.
- **No AvaTax PH rules** — AvaTax is a design benchmark for API quality only. PH tax computation rules come from BIR issuances (RMCs, RMOs, RRs) exclusively.

---

## Acceptance Criteria

1. A filer can generate a period-specific filing pack from Odoo data, including computed tax bases and pre-filled form data.
2. A filer can see whether the period should go through eBIRForms or eFPS based on taxpayer classification and can view the routing rationale.
3. A filer can complete payment orchestration, select a payment channel, and capture a payment reference with amount and timestamp.
4. A filer can generate an eAFS attachment pack, validate completeness against form-specific requirements, and record the TRN / Confirmation Receipt.
5. A filer can view a complete audit trail for a filing period:
   - preparation status and validation results
   - filing channel and filing reference
   - payment status, channel, and reference
   - attachment submission status and TRN
   - evidence artifacts (linked, viewable)
   - operator attribution for each step
6. The system never marks a filing as "complete" without the required evidence artifacts. A period in terminal state must have: filing reference, payment reference, and eAFS TRN / Confirmation Receipt (where applicable to the filing type).
