# TaxPulse BIR Integration — Constitution

> Spec bundle: `spec/taxpulse-bir-integration/`
> Status: Active
> Last updated: 2026-04-02

---

## Non-Negotiable Rules

1. **Odoo 18 is the accounting SoR.** TaxPulse never duplicates or replaces Odoo ledger data. All tax bases, journals, partner records, and attachments originate from Odoo.

2. **Workflow-assist first, direct API second.** TaxPulse prepares data, guides the operator, and captures evidence. Direct BIR system-to-system submission is a later capability and only where BIR formally supports it.

3. **No filing marked complete without evidence.** The system must store a filing reference, payment reference, eAFS TRN / Confirmation Receipt, or equivalent proof artifact before any period can transition to a terminal state.

4. **BIR eService scope is bounded.** Only the eServices listed in the PRD scope tiers (P0/P1/P2) are in scope. Do not invent integrations with unpublished or unsupported BIR interfaces.

5. **PH-only.** This spec governs Philippine BIR compliance exclusively. Do not generalize to other tax jurisdictions.

6. **CE-only Odoo stack.** All Odoo modules referenced or created must be CE-compatible. No Enterprise dependencies, no odoo.com IAP.

7. **OCA-first for accounting primitives.** Use OCA accounting modules (mis_builder, account_financial_report, etc.) before creating ipai_* overrides.

8. **Evidence is append-only.** Filing evidence records and audit trail entries are immutable once created. No deletion, no silent overwrite.

9. **Operator attribution required.** Every state transition must record who performed it and when. Anonymous or system-only transitions are prohibited for filing-critical paths.

10. **AvaTax is a design benchmark, not a PH implementation.** AvaTax patterns (US/CA/BR) inform API design quality, not PH tax rules. PH grounding comes from BIR issuances, RMCs, and RMOs exclusively.
