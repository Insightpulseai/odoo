# UAT and Cutover Controls — Pulser for Odoo

This document defines the methodology for User Acceptance Testing (UAT) and the rigid control checkpoints required for the production cutover window.

---

## 1. Scenario-based UAT (BOM 13)

Technically verified data must be validated through user-scenario execution.

### UAT-80: Project to Profit
Validate the end-to-end profitability lifecycle:
- **WBS & Resourcing**: Verify project structure and resource costs.
- **Time/Expense**: Verify labor burn and expense posting accuracy.
- **Billing**: Verify the generation of accurate customer invoices per contract.

### UAT-90: Record to Report
Validate the financial integrity and close cycle:
- **Reconciliation**: Verify bank and sub-ledger reconciliation precision.
- **Tax Accuracy**: Verify BIR-linked tax determination and form prep.
- **Reporting**: Verify Trial Balances and Board Packs vs. Legacy ground truth.

## 2. The Cutover Window Checklist (T-Minus)

The "Cutover Window" is the period of legacy-system lock and final sync.

| Timeline | Action Item | Success Criteria |
|----------|-------------|------------------|
| **T-Minus 24h** | Legacy Freeze | Legacy system set to read-only; no new entries. |
| **T-Minus 12h** | Final Delta Sync | Last batch of Invoices/Bills/Expenses ingested. |
| **T-Minus 4h** | Master Balance Check | FACT-DG-01 Reconciliation returns Zero Variance. |
| **T-Minus 2h** | User Readiness Check | Final confirmation from Tenant Process Owners. |
| **Zero Hour** | System Unlock | Odoo instance set to "Live Site" status (Active). |

## 3. Activation Authorization

Activation is only permitted upon the filing of the **Activation Authorization Log**, which must contain:
1. **Scenario UAT Sign-off**: Verified by the Tenant Process Owner.
2. **Technical Validation Log**: Verified by the Pulser Platform Lead.
3. **Cutover Readiness Log**: Verified by the Tenant Finance Director.

---

*Last updated: 2026-04-11*
