# BIR Filing Control - Constitution

## Scope Boundary

This spec covers the **filing lifecycle** — calendar management, obligation tracking, submission evidence, and audit trail. Tax **computation** (rates, brackets, form line amounts) is owned by `spec/bir-tax-compliance/` and the `ipai_finance_tax_return` module. This module consumes computed returns and manages what happens after computation: scheduling, filing, evidence capture, and compliance monitoring.

## Non-Negotiables

### 1. Module Identity

- **Module name**: `ipai_finance_bir_filing`
- **Extends**: `ipai_finance_tax_return` (computed returns as input)
- **Dependencies**: `account`, `mail`, `calendar`
- **CE only**: No Odoo Enterprise modules, no odoo.com IAP
- **OCA first**: Use OCA modules before building custom logic

### 2. Filing Evidence Requirement

- Every BIR form submission **must** have filing evidence before it can be marked as "filed"
- Evidence includes at minimum: confirmation number OR filing receipt OR eFPS transaction reference
- Evidence records are **immutable** — no deletion, no modification after creation
- Screenshots, PDFs, and receipt images stored via Odoo attachments (ir.attachment)

### 3. Filing Calendar Integrity

- Filing calendar must be **auditable** — all deadline changes logged with user and timestamp
- Calendar auto-populates from BIR statutory schedule (monthly, quarterly, annual)
- Philippine holiday calendar (`ph.holiday`) adjusts deadlines per BIR rules (next working day)
- Late filings are flagged automatically with penalty computation reference

### 4. Separation of Duties

- The person who prepares a filing cannot be the same person who marks it as submitted
- Filing approval follows the RACI pattern from `spec/close-orchestration/`
- All state transitions logged via `mail.thread` (Odoo chatter)

### 5. Data Retention

- 10-year retention for all filing records and evidence (BIR requirement)
- No archival or deletion of filed returns within retention window
- Audit trail preserved even if related accounting entries are modified

### 6. BIR Forms Covered

| Form | Description | Frequency |
|------|-------------|-----------|
| 1601-C | Withholding Tax on Compensation | Monthly |
| 0619-E | Expanded Withholding Tax Remittance | Monthly |
| 1601-EQ | Quarterly Expanded Withholding Tax | Quarterly |
| 1702-RT | Annual Income Tax (Regular) | Annual |
| 1702-EX | Annual Income Tax (Exempt) | Annual |
| 2550Q | Quarterly VAT Return | Quarterly |
| 1702Q | Quarterly Income Tax | Quarterly |
| 2316 | Certificate of Compensation Payment/Tax Withheld | Annual |
| Alphalist | Annual Information Return (1604-CF) | Annual |

### 7. Integration Constraints

- Filing status must be visible in close orchestration dashboard (`spec/close-orchestration/`)
- Tax computation module provides the data; this module provides the workflow
- n8n handles deadline alert notifications (5-day and 1-day warnings)
- Slack notifications for overdue filings (replaces deprecated Mattermost)
