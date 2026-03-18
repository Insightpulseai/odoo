# AP Invoice Control - Product Requirements Document

## Overview

The AP Invoice Control module (`ipai_finance_ap_control`) provides end-to-end accounts payable control for TBWA Philippines within Odoo CE 19. It enforces three-way matching (PO <-> Receipt <-> Invoice), manages exceptions, routes approvals by amount, and gates payment readiness. The module ensures no invoice is paid without proper verification and authorization.

## Problem Statement

Current AP processing at TBWA Philippines suffers from:
1. Manual three-way matching using spreadsheets (error-prone, time-consuming)
2. No systematic exception handling for price/quantity variances
3. Approval routing based on informal email chains (no audit trail)
4. Invoices paid without complete matching (compliance risk)
5. No centralized view of payment readiness across all payables
6. Manual vendor statement reconciliation (month-end bottleneck)

## User Stories

### US-1: AP Clerk — Invoice Ingestion

> As an AP Clerk, I want to scan vendor invoices and have key data auto-extracted so I can reduce manual data entry errors.

**Acceptance Criteria:**
- Upload invoice PDF/image triggers OCR extraction
- OCR extracts: vendor name, invoice number, date, line items, amounts, tax
- Auto-match vendor by TIN or name against `res.partner`
- Auto-suggest matching PO based on vendor + amounts
- Confidence score displayed; low-confidence fields highlighted for review
- Manual override available for all extracted fields

### US-2: AP Clerk — Three-Way Matching

> As an AP Clerk, I want the system to automatically match invoices against POs and receipts so I can quickly identify discrepancies.

**Acceptance Criteria:**
- System matches invoice lines to PO lines by product, quantity, and unit price
- System matches invoice quantities to goods receipt quantities
- Match status per line: matched, quantity_variance, price_variance, unmatched
- Overall invoice match status: fully_matched, partially_matched, unmatched
- Configurable tolerance thresholds (per company): price %, quantity %
- Auto-match runs on invoice creation; manual re-match available

### US-3: AP Supervisor — Exception Handling

> As an AP Supervisor, I want to see all matching exceptions in one queue so I can review and approve or reject them efficiently.

**Acceptance Criteria:**
- Exception queue view filtered by type, severity, age
- Exception types: price_variance, quantity_variance, no_po, partial_receipt, duplicate_invoice
- Each exception shows: invoice details, PO details, variance amount, variance %
- Approve with justification (text field, required)
- Reject with reason (returns invoice to AP Clerk)
- Escalation for exceptions above supervisor threshold

### US-4: Finance Manager — Approval Routing

> As a Finance Manager, I want invoices routed to the correct approver based on amount so I can ensure proper authorization levels.

**Acceptance Criteria:**
- Approval thresholds configurable (e.g., < 50K: Supervisor, < 500K: Manager, >= 500K: Director)
- Multi-level approval for high-value invoices
- Approver sees: invoice, PO, receipt, match status, exception status
- Approve/reject with comments
- Delegation support (temporary approval authority transfer)
- Notifications via Odoo activity + Slack

### US-5: AP Manager — Payment Readiness

> As an AP Manager, I want a clear view of which invoices are ready for payment so I can process payment batches confidently.

**Acceptance Criteria:**
- Payment readiness checklist per invoice:
  - [ ] Three-way match completed (or exception approved)
  - [ ] Approval workflow completed
  - [ ] GL coding verified (expense account assigned)
  - [ ] Tax validated (withholding tax computed, VAT input captured)
- Payment readiness is computed (not manual)
- Batch view: all payment-ready invoices with due dates
- Filter by vendor, due date range, payment method
- Block payment for invoices that fail readiness gate

### US-6: Controller — Aging & Reconciliation

> As a Controller, I want aging reports and vendor statement reconciliation so I can manage cash flow and maintain vendor relationships.

**Acceptance Criteria:**
- AP aging report: current, 30, 60, 90, 120+ days
- Aging by vendor, by GL account, by department
- Vendor statement reconciliation: compare vendor statement to Odoo balances
- Identify discrepancies (missing invoices, payment differences)
- Export aging report to Excel/PDF
- Drill-down from aging bucket to individual invoices

## Feature Requirements

### F1: Invoice Ingestion (OCR Pipeline)

- Upload vendor invoice (PDF, image)
- OCR extraction using pipeline from `spec/expense-automation/` (adapted for AP invoices)
- Extract: vendor TIN, invoice number, invoice date, due date, line items, amounts, VAT
- Auto-match vendor by TIN against `res.partner`
- Auto-suggest PO match based on vendor + approximate amounts
- Confidence scoring per field; flag low-confidence for manual review
- Support for multi-page invoices
- Batch upload support (multiple invoices at once)

### F2: Three-Way Matching Engine

- Model: `ap.invoice.match`
- Match invoice lines to PO lines (by product, quantity, price)
- Match invoice quantities to stock receipt quantities (stock.picking)
- Tolerance thresholds configurable per company:
  - Price tolerance: percentage (default 0%)
  - Quantity tolerance: percentage (default 0%)
- Match results per line: matched, price_variance, quantity_variance, no_match
- Overall invoice match: fully_matched, partially_matched, exception
- Auto-match on invoice creation
- Manual re-match trigger
- Match detail view showing PO line <-> receipt line <-> invoice line

### F3: Exception Handling Workflow

- Model: `ap.match.exception`
- Exception types:
  - `price_variance`: unit price differs from PO beyond tolerance
  - `quantity_variance`: invoiced qty differs from received qty beyond tolerance
  - `no_po`: invoice has no matching purchase order
  - `partial_receipt`: goods not fully received yet
  - `duplicate_invoice`: invoice number already exists for this vendor
- Exception workflow: open -> under_review -> approved -> rejected
- Approval routing by exception amount (configurable thresholds)
- Required justification text on approval
- Rejection returns invoice to AP Clerk with reason
- Escalation rules: auto-escalate after configurable days
- Exception dashboard: count by type, age, status

### F4: Approval Workflow (Amount-Based)

- Model: extend `account.move` with approval fields
- Approval thresholds (configurable per company):
  - Level 1 (< threshold_1): AP Supervisor
  - Level 2 (< threshold_2): Finance Manager
  - Level 3 (>= threshold_2): Finance Director
- Multi-level approval for amounts above Level 2
- Approval actions logged via `mail.thread`
- Activity scheduling for pending approvals
- Delegation: temporary authority transfer with date range
- Notifications: Odoo activities + Slack webhook

### F5: Payment Readiness Gate

- Computed field `payment_ready` on `account.move` (vendor bills)
- Gate conditions (ALL must be true):
  1. `match_status` in ('fully_matched', 'exception_approved')
  2. `approval_status` = 'approved'
  3. `gl_coding_verified` = True (expense accounts assigned to all lines)
  4. `tax_validated` = True (withholding tax and VAT input correct)
- Payment readiness displayed on invoice form (checklist widget)
- Batch payment view filters on `payment_ready = True`
- Block `account.payment` creation for invoices where `payment_ready = False`
- Override available for Finance Director role only (with logged justification)

### F6: Aging Reports & Vendor Statement Reconciliation

- AP aging report: current, 1-30, 31-60, 61-90, 91-120, 120+ days
- Group by: vendor, GL account, department, payment terms
- Vendor statement reconciliation wizard:
  - Import vendor statement (CSV/Excel)
  - Auto-match by invoice number and amount
  - Highlight unmatched items (both sides)
  - Generate reconciliation report
- Export to Excel/PDF
- Drill-down from aging bucket to individual invoices
- Integration with cash flow planning

## Non-Functional Requirements

### NFR-1: Performance
- Three-way match execution < 2 seconds per invoice (up to 50 lines)
- Aging report generation < 5 seconds for 10,000+ invoices
- Dashboard load < 2 seconds
- OCR extraction < 10 seconds per page

### NFR-2: Security
- Role-based access: ap_clerk, ap_supervisor, ap_manager, ap_director
- Company-based record rules
- Separation of duties enforced (recorder != approver != payment processor)
- Sensitive vendor data (bank details) restricted to ap_manager+

### NFR-3: Compliance
- Full audit trail on matching, exceptions, and approvals
- Separation of duties logging
- Payment readiness gate cannot be bypassed without Director override + justification
- BIR withholding tax integration for vendor payments

## Cross-References

| Spec | Relationship |
|------|-------------|
| `spec/close-orchestration/` | Approval gate pattern (three-stage workflow) |
| `spec/expense-automation/` | OCR pipeline for invoice scanning |
| `spec/bir-tax-compliance/` | Withholding tax validation on vendor payments |
| `spec/ipai-tbwa-finance/` | TBWA-specific AP context, team RACI |

## Success Metrics

| Metric | Target |
|--------|--------|
| Invoice processing time | < 5 minutes (scan to match) |
| Three-way match rate | > 85% auto-matched |
| Exception resolution time | < 48 hours |
| Payment accuracy | 100% (no payment without readiness gate) |
| AP aging > 90 days | < 5% of total payables |
| Duplicate invoice detection | 100% |
