# BIR Filing Control - Product Requirements Document

## Overview

The BIR Filing Control module (`ipai_finance_bir_filing`) manages the filing lifecycle for all Philippine Bureau of Internal Revenue obligations. It sits downstream of tax computation (`ipai_finance_tax_return`) and upstream of close orchestration (`ipai_close_orchestration`), ensuring every statutory filing is scheduled, tracked, submitted with evidence, and auditable.

## Problem Statement

TBWA Philippines currently tracks BIR filing obligations through:
- Manual spreadsheets for deadline tracking
- Email-based reminders for upcoming filings
- No centralized evidence vault for filing receipts
- No integration between tax computation and filing submission
- Risk of missed deadlines leading to 25% surcharge + 20% annual interest penalties

## User Stories

### US-1: Finance Manager — Filing Calendar

> As a Finance Manager, I want to see all upcoming BIR filing obligations in a calendar view so I can plan workload and ensure nothing is missed.

**Acceptance Criteria:**
- Calendar view shows all obligations for current and next month
- Color-coded by status: upcoming (blue), in-progress (yellow), filed (green), overdue (red)
- Click on an obligation opens the filing detail form
- Obligations auto-generated from BIR schedule each fiscal year

### US-2: Tax Preparer — Obligation Tracking

> As a Tax Preparer, I want to see which forms are due, their current status, and what data is needed so I can prioritize my work.

**Acceptance Criteria:**
- List view of obligations filtered by status, form type, or due date
- Each obligation links to the computed tax return (from `ipai_finance_tax_return`)
- Status workflow: draft -> in_preparation -> ready_for_review -> approved -> filed -> confirmed
- Checklist of required data sources per form type

### US-3: Finance Manager — eBIRForms Integration

> As a Finance Manager, I want to export computed tax data in eBIRForms-compatible format so I can file using the BIR offline application.

**Acceptance Criteria:**
- Export button generates eBIRForms XML/DAT file for each supported form
- Exported file validates against eBIRForms schema
- Export action logged with timestamp and user
- Re-export supported (new version tracked)

### US-4: Tax Preparer — eFPS Integration

> As a Tax Preparer, I want to track online filings made through eFPS (Electronic Filing and Payment System) so I have a complete record.

**Acceptance Criteria:**
- Record eFPS transaction reference number after filing
- Track payment confirmation number separately from filing confirmation
- Link payment amount and date to the filing record
- Support for amended returns (track original + amendment)

### US-5: Compliance Officer — Evidence Vault

> As a Compliance Officer, I want all filing evidence (receipts, confirmation numbers, screenshots) stored in a searchable vault so I can respond to BIR audits quickly.

**Acceptance Criteria:**
- Upload filing receipt (PDF, image) as attachment
- Record confirmation number (text field, required before marking as filed)
- Store eFPS transaction reference, payment reference, and filing timestamp
- Search by form type, period, date range, or confirmation number
- Evidence records are immutable after creation
- 10-year retention enforced

### US-6: Finance Director — Filing Dashboard

> As a Finance Director, I want a dashboard showing filing status across all BIR obligation types so I can monitor compliance at a glance.

**Acceptance Criteria:**
- Summary cards: upcoming filings, in-progress, filed this period, overdue
- Overdue counter with penalty exposure estimate (25% surcharge + 20% interest)
- Drill-down from summary to individual filings
- Filter by period (monthly, quarterly, annual), form type, preparer

## Feature Requirements

### F1: Filing Calendar Management

- Auto-populate annual filing calendar from BIR statutory schedule
- Adjust deadlines using Philippine holiday calendar (`ph.holiday`)
- BIR rule: if deadline falls on weekend/holiday, next working day applies
- Support for BIR-announced deadline extensions (manual override with audit log)
- Calendar entries linked to obligation records

### F2: Obligation Tracking

- Model: `bir.filing.obligation`
- Fields: form_type, period_start, period_end, due_date, status, assigned_to, tax_return_id
- Status workflow: draft -> in_preparation -> ready_for_review -> approved -> filed -> confirmed
- Each obligation links to one or more computed tax returns
- Overdue detection via scheduled action (ir.cron)
- Overdue notifications via n8n -> Slack

### F3: eBIRForms Integration

- Export computed tax data to eBIRForms-compatible format (XML/DAT)
- Supported forms: 1601-C, 0619-E, 1601-EQ, 2550Q, 1702-RT/EX, 1702Q
- Export wizard with period selection and validation
- Pre-export validation: check all required fields populated
- Export history tracked (version, timestamp, user)

### F4: eFPS Integration

- Track online filing submissions
- Fields: efps_transaction_ref, filing_timestamp, payment_ref, payment_amount, payment_date
- Support for amended returns (link to original filing)
- Payment status tracking: pending, paid, confirmed
- Bank reference capture for payment confirmation

### F5: Evidence Vault

- Model: `bir.filing.evidence`
- Fields: obligation_id, evidence_type (receipt/confirmation/screenshot/payment), attachment_ids, confirmation_number, notes
- Evidence types: filing_receipt, efps_confirmation, payment_receipt, bir_acknowledgment, screenshot
- Immutable: create-only, no update or delete after save
- Search and filter by form type, period, evidence type
- Bulk download for audit response packages

### F6: Filing Status Dashboard

- Kanban view by status (upcoming, in-progress, filed, overdue)
- Calendar view with color-coded obligations
- Summary statistics: total due, filed, overdue, compliance rate
- Penalty exposure widget (estimated penalties for overdue filings)
- Period selector (current month, current quarter, current year)

## Non-Functional Requirements

### NFR-1: Performance
- Dashboard loads in < 2 seconds for 200+ obligations
- Evidence search returns results in < 1 second
- Export generation completes in < 5 seconds per form

### NFR-2: Security
- Role-based access: preparer, reviewer, approver, admin
- Company-based record rules (multi-company support)
- Evidence vault read-only after creation (no update/delete ACL)
- Audit trail via `mail.thread` on all models

### NFR-3: Compliance
- 10-year data retention (no archive before retention window)
- Full audit trail on state changes
- Separation of duties enforced (preparer != approver)
- Filing evidence required before status = filed

## Cross-References

| Spec | Relationship |
|------|-------------|
| `spec/bir-tax-compliance/` | Provides computed tax returns consumed by this module |
| `spec/close-orchestration/` | Filing status feeds into close cycle approval gates |
| `spec/ipai-tbwa-finance/` | TBWA-specific filing context and team RACI |

## Success Metrics

| Metric | Target |
|--------|--------|
| On-time BIR filing rate | 100% |
| Evidence capture rate | 100% of filed returns |
| Overdue detection latency | < 1 hour after deadline |
| Audit response time | < 30 minutes (find any filing evidence) |
| Penalty avoidance | Zero late-filing penalties |
