# IPAI TBWA Finance - Constitution

## Purpose

This spec defines the unified financial operations module for TBWA Philippines, combining:
- Month-end closing automation (replacing SAP AFC)
- BIR tax compliance (Philippine statutory filings)

## Non-Negotiable Rules

### 1. Philippine Holiday Calendar

- All deadline calculations MUST use Philippine holidays
- Regular holidays: no government transactions
- Special non-working: banks may be closed
- Workday offsets MUST skip weekends AND holidays

### 2. BIR Compliance

- TIN format: XXX-XXX-XXX-XXX (12 digits, 3 dashes)
- All tax forms MUST have audit trail
- Filing deadlines are statutory - no extensions without BIR approval
- VAT computation must reconcile to Sales/Purchase journals

### 3. RACI Workflow

Every task follows RACI pattern:
- **Responsible**: Prepares/executes the task (RIM team)
- **Accountable**: Reviews and approves (BOM)
- **Consulted**: Provides input (CKVC for complex items)
- **Informed**: Receives notification (FD, stakeholders)

### 4. Period Controls

- Periods MUST be closed sequentially (no skipping months)
- All compliance checks MUST pass before closing
- Closed periods are locked - no edits without formal reversal

### 5. Audit Trail

- All state changes must be logged with user/timestamp
- Tax filings must retain reference numbers
- Journal entries must link to source task

## Team Assignments (Default RACI)

| Role | Assignment | Responsibilities |
|------|------------|------------------|
| Prep | RIM | Data entry, document gathering |
| Review | BOM | Accuracy check, compliance verification |
| Approve | FD/CFO | Final sign-off, filing authorization |

## Module Boundaries

This module handles:
- Task scheduling and tracking
- Deadline calculation with holiday awareness
- BIR form preparation workflow
- Period opening/closing
- Compliance check execution

This module does NOT handle:
- Actual journal entry creation (uses `account` module)
- Payroll processing (uses `hr_payroll`)
- Bank reconciliation (uses OCA `account_reconcile_oca`)

## Dependencies

- `base`: Core Odoo functionality
- `mail`: Notifications and chatter
- `account`: Journal entries, taxes, fiscal periods

## Supersedes

This unified module replaces:
- `ipai_month_end` (Phase 1 - internal closing tasks)
- `ipai_bir_tax_compliance` (Phase 1 - BIR filing tasks)
