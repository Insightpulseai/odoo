# AP Invoice / Supplier Bill Agent — Product Requirements Document (AP-01)

## Objective
Implement an autonomous AP Invoice Agent that utilizes **TaxPulse** for Philippine-compliant tax verification and enforces **fail-closed** posting gates for supplier bills in Odoo.

## Product Goals
- **Automatic Matching**: Match vendor bills (PDF/OCR) to Purchase Orders or Receipts.
- **Tax Compliance**: Calculate EWT/VAT based on TaxPulse SSOT rules.
- **Fail-Closed Governance**: Prevent posting of bills with ambiguous tax mappings or missing evidence.
- **Evidence-Backed**: Generate an agent evidence pack for every posted bill.

## Success Criteria
- 95%+ accuracy on tax-rule selection for clean vendor invoices.
- 0% auto-posting of unsupported tax scenarios (routed to manual audit).
- 100% auditability via the agent task bus and evidence vault.

## Release Lane order
1. **Spec Kit & SSOT Bundle** (Contracts, Policies, Evaluation Scenarios).
2. **Runtime Implementation** (Odoo Module, OCR Bridge).
3. **Acceptance & Red Team** (Adversarial testing of posting gates).
4. **Production Rehearsal** (Staging).
5. **Operational Soak Window**.

## Documentation Reference
- [TaxPulse Acceptance](file:///Users/tbwa/.gemini/antigravity/brain/706fb290-55e8-41c0-82d6-358506acd2c3/tax-pulse-acceptance.md)
- [Agent Platform Constitution](file:///Users/tbwa/Documents/GitHub/Insightpulseai/spec/agent-factory/constitution.md)
