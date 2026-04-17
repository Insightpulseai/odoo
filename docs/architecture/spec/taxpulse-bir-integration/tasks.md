# TaxPulse BIR Integration — Tasks

> Spec bundle: `spec/taxpulse-bir-integration/`
> Status: Active
> Last updated: 2026-04-02

---

## Phase 1 — Filing Prep and Payment Orchestration

- [ ] Define filing-period domain model (entity, period, tax type, state machine)
- [ ] Define tax-workpaper aggregation from Odoo (journal entries, tax lines, withholding records)
- [ ] Implement PH chart of accounts mapping for BIR form line items
- [ ] Implement filing-pack generator (XML/CSV output per BIR form spec)
- [ ] Implement eBIRForms vs eFPS routing rules (taxpayer classification, large taxpayer flag, RDO)
- [ ] Implement payment summary computation (tax due, penalties, surcharges, interest)
- [ ] Implement ePAY channel routing (AABs, GCash, PayMaya, LandBank Link.BizPortal)
- [ ] Implement payment reference capture flow (reference number, channel, amount, timestamp)
- [ ] Implement filing-status timeline model with state machine transitions
- [ ] Implement filing-status timeline UI (period matrix view per entity)
- [ ] Add exception states for missing or conflicting data (blocking-item detection)
- [ ] Add resolution hints for each exception type
- [ ] Add human-action-required queue with operator assignment

## Phase 2 — eAFS Attachment Pack and Evidence

- [ ] Define eAFS attachment manifest model (form-specific required documents)
- [ ] Implement attachment manifest per BIR form type (AFS, SAWT, MAP, QAP, 2307)
- [ ] Implement attachment completeness validator (required docs, metadata checks)
- [ ] Implement metadata enforcement (TIN, period, form type, page count per RMC 17-2024)
- [ ] Implement submission artifact store (append-only, immutable)
- [ ] Add TRN / Confirmation Receipt capture flow with structured input
- [ ] Add filing-period evidence checklist UI (captured vs pending milestones)
- [ ] Implement evidence artifact linking (receipts, screenshots, PDF confirmations)
- [ ] Implement completion gate: prevent terminal state without required evidence
- [ ] Add operator attribution for all evidence capture actions

## Phase 3 — ORUS Registration Support

- [ ] Define taxpayer registration profile model (TIN, RDO, business activity, registration type)
- [ ] Add registration lifecycle states (active, pending transfer, pending update, closed)
- [ ] Add registration-update workflow states (RDO transfer, activity update, closure)
- [ ] Implement required-document checklist per registration action type
- [ ] Add missing-registration-data checks with resolution hints
- [ ] Add ORUS task queue / operator worklist with priority and deadlines
- [ ] Add registration acknowledgment capture (BIR confirmation of registration action)

## Phase 4 — eTSPCert Readiness

- [ ] Version BIR-facing output schemas (form field mappings with revision tracking)
- [ ] Define validation-rules registry (computation accuracy, cross-form consistency)
- [ ] Implement BIR test case validation runner (expected vs actual output comparison)
- [ ] Create certification evidence pack template (output fidelity documentation)
- [ ] Add release gate for BIR-output changes (CI/manual gate on form output modifications)
- [ ] Document Odoo field -> BIR form field mapping registry

## Cross-Cutting

- [ ] Add audit logging for all filing state changes (actor, timestamp, previous state, new state, reason)
- [ ] Add document retention / attachment linkage (Odoo ir.attachment integration)
- [ ] Add dashboard for period readiness by entity (matrix: entity x period x tax type x status)
- [ ] Add explicit human-action-required queue (cross-phase, unified operator worklist)
- [ ] Add BIR calendar integration (filing deadlines per tax type, penalty date awareness)
- [ ] Add multi-entity support (consolidated view across multiple taxpayer entities)
- [ ] Add form-version change detection (alert when BIR publishes revised forms)
- [ ] Add evidence export for external audit (zip pack per entity per period)
