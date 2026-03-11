# AP Invoice Control - Task Checklist

## Phase 1: Invoice Ingestion + Three-Way Match Model

- [ ] Create `ipai_finance_ap_control` module scaffold (`__init__.py`, `__manifest__.py`)
- [ ] Implement `ap.invoice.match` model (links PO, receipt, invoice)
- [ ] Implement `ap.match.line` model (per-line match details)
- [ ] Build three-way matching algorithm (product, quantity, price comparison)
- [ ] Add configurable tolerance thresholds on `res.company` (price %, quantity %)
- [ ] Compute match status: fully_matched, partially_matched, exception
- [ ] Extend `account.move` with match_status field (vendor bills only)
- [ ] Create OCR ingestion wizard (upload PDF/image, extract fields)
- [ ] Implement auto-suggest PO match (by vendor + approximate amounts)
- [ ] Build match results list view with filters
- [ ] Create security groups: ap_clerk, ap_supervisor, ap_manager, ap_director
- [ ] Write security access rules (`ir.model.access.csv`)
- [ ] Add menu structure under Accounting > AP Control
- [ ] Write unit tests for three-way matching algorithm

## Phase 2: Exception Handling + Approval Routing

- [ ] Implement `ap.match.exception` model with status workflow
- [ ] Add exception types: price_variance, quantity_variance, no_po, partial_receipt, duplicate_invoice
- [ ] Build exception queue view (filtered by type, age, status)
- [ ] Enforce required justification on exception approval
- [ ] Implement rejection workflow (return to AP Clerk with reason)
- [ ] Implement `ap.approval.threshold` model (amount-based routing config)
- [ ] Load default approval thresholds data
- [ ] Add approval fields on `account.move` (approval_status, approved_by, approved_date)
- [ ] Implement multi-level approval routing based on invoice amount
- [ ] Add activity scheduling for pending approvals
- [ ] Create notification templates (Odoo mail)
- [ ] Configure Slack webhook for approval notifications
- [ ] Implement escalation cron (auto-escalate after configurable days)
- [ ] Enforce separation of duties (recorder != approver)
- [ ] Write unit tests for exception workflow and approval routing

## Phase 3: Payment Readiness Gate

- [ ] Add computed `payment_ready` field on `account.move` (vendor bills)
- [ ] Implement gate conditions: match_ok AND approved AND gl_coded AND tax_validated
- [ ] Build payment readiness checklist widget on invoice form
- [ ] Block `account.payment` creation when `payment_ready = False`
- [ ] Implement Finance Director override with logged justification
- [ ] Create batch payment view filtered by `payment_ready = True`
- [ ] Add GL coding verification field on invoice lines
- [ ] Integrate tax validation (withholding tax, VAT input)
- [ ] Build payment batch creation wizard
- [ ] Write unit tests for payment readiness gate and override

## Phase 4: Aging + Reconciliation

- [ ] Build AP aging report (current, 30, 60, 90, 120+ days)
- [ ] Add aging grouping by vendor, GL account, department
- [ ] Create vendor statement reconciliation wizard
- [ ] Implement vendor statement import (CSV/Excel)
- [ ] Build auto-match logic (invoice number + amount)
- [ ] Generate discrepancy report (unmatched items both sides)
- [ ] Build AP dashboard (summary cards, match rate, exception count)
- [ ] Add aging distribution chart to dashboard
- [ ] Implement Excel/PDF export for aging report
- [ ] Add drill-down from aging bucket to individual invoices
- [ ] Integrate with close orchestration (AP completeness as gate input)
- [ ] Write unit tests for aging calculation and reconciliation

## Validation Criteria

- [ ] Three-way match correctly identifies fully matched invoices (PO + receipt + invoice aligned)
- [ ] Price variance exception auto-created when price exceeds tolerance
- [ ] Quantity variance exception auto-created when qty exceeds tolerance
- [ ] No-PO invoices flagged as exception automatically
- [ ] Duplicate invoice detection works (same vendor + invoice number)
- [ ] Approval routing sends to correct approver based on amount
- [ ] Separation of duties enforced (recorder != approver != payment processor)
- [ ] Payment blocked for invoices failing readiness gate
- [ ] Director override works with justification logged in chatter
- [ ] Aging report buckets calculate correctly based on due date
- [ ] Vendor statement reconciliation identifies discrepancies
- [ ] All state transitions logged with user, timestamp, and details
