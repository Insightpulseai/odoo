# AP Invoice Control - Implementation Plan

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Odoo CE 19 + OCA                               │
│                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │  purchase    │  │    stock    │  │   account   │                 │
│  │ (PO mgmt)   │  │ (Receipts)  │  │ (Invoices)  │                 │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                 │
│         │                │                │                         │
│         └────────┬───────┴────────┬───────┘                         │
│                  ▼                ▼                                  │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              ipai_finance_ap_control                         │   │
│  │                                                             │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │   │
│  │  │   Invoice    │  │  Three-Way   │  │  Exception   │      │   │
│  │  │  Ingestion   │  │   Matching   │  │  Handling    │      │   │
│  │  │  (OCR)       │  │   Engine     │  │  Workflow    │      │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘      │   │
│  │                                                             │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │   │
│  │  │  Approval    │  │  Payment     │  │  Aging &     │      │   │
│  │  │  Routing     │  │  Readiness   │  │  Reconcile   │      │   │
│  │  │  (Amount)    │  │  Gate        │  │              │      │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘      │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                  │                                                   │
│                  ▼                                                   │
│  ┌──────────────────────┐    ┌──────────────────────┐               │
│  │ ipai_close_           │    │ ipai_finance_tax_    │               │
│  │ orchestration         │    │ return               │               │
│  │ (Approval Gates)     │    │ (WHT Validation)     │               │
│  └──────────────────────┘    └──────────────────────┘               │
└─────────────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    n8n + Slack                                       │
│  - Approval notifications                                           │
│  - Exception escalation alerts                                      │
│  - Payment batch reminders                                          │
└─────────────────────────────────────────────────────────────────────┘
```

## Module Structure

```
addons/ipai/ipai_finance_ap_control/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── ap_invoice_match.py            # Three-way match model
│   ├── ap_match_line.py               # Per-line match details
│   ├── ap_match_exception.py          # Exception model + workflow
│   ├── ap_approval_threshold.py       # Amount-based approval config
│   ├── account_move_ext.py            # Extend vendor bills
│   ├── purchase_order_ext.py          # Extend PO for match tracking
│   └── res_company_ext.py             # Company-level config
├── views/
│   ├── ap_invoice_match_views.xml
│   ├── ap_match_exception_views.xml
│   ├── ap_approval_views.xml
│   ├── ap_payment_readiness_views.xml
│   ├── ap_aging_views.xml
│   ├── ap_dashboard_views.xml
│   ├── account_move_views_ext.xml
│   └── menu.xml
├── security/
│   ├── ir.model.access.csv
│   └── ap_control_security.xml        # Groups, record rules
├── data/
│   ├── ap_approval_threshold_data.xml # Default thresholds
│   ├── ir_cron.xml                    # Escalation cron
│   └── mail_template.xml             # Notification templates
├── wizard/
│   ├── __init__.py
│   ├── ap_invoice_ocr_wizard.py       # OCR ingestion wizard
│   ├── ap_vendor_reconcile_wizard.py  # Vendor statement reconciliation
│   └── ap_payment_batch_wizard.py     # Payment batch creation
├── reports/
│   ├── ap_aging_report.xml
│   ├── ap_match_status_report.xml
│   └── ap_vendor_reconcile_report.xml
└── tests/
    ├── __init__.py
    ├── test_three_way_match.py
    ├── test_exception_workflow.py
    ├── test_approval_routing.py
    └── test_payment_readiness.py
```

## Implementation Phases

### Phase 1: Invoice Ingestion + Three-Way Match Model

**Scope:** Core matching infrastructure and OCR-assisted ingestion

**Deliverables:**
- `ap.invoice.match` model linking PO, receipt (stock.picking), and invoice (account.move)
- `ap.match.line` model for per-line match details
- Three-way matching algorithm: product + quantity + price comparison
- Configurable tolerance thresholds on `res.company`
- Match status computation: fully_matched, partially_matched, exception
- Invoice extension: match_status field on `account.move` (vendor bills)
- OCR ingestion wizard (upload PDF/image, extract key fields)
- Auto-suggest PO match based on vendor + amounts
- Basic list view for match results

**Dependencies:** `account`, `purchase`, `stock`, `mail`

**Verification:**
- Create PO, receive goods, create invoice -> auto-match succeeds
- Create invoice with price variance -> match status shows exception
- Upload invoice PDF -> OCR extracts vendor, amount, invoice number
- Tolerance threshold respected (within tolerance = matched)

### Phase 2: Exception Handling + Approval Routing

**Scope:** Exception workflow and amount-based approvals

**Deliverables:**
- `ap.match.exception` model with workflow: open -> under_review -> approved -> rejected
- Exception types: price_variance, quantity_variance, no_po, partial_receipt, duplicate_invoice
- Exception queue view (filtered by type, age, status)
- Required justification on approval
- `ap.approval.threshold` model (amount-based routing configuration)
- Approval fields on `account.move`: approval_status, approved_by, approved_date
- Multi-level approval for high-value invoices
- Activity scheduling for pending approvals
- Notification templates (Odoo mail + Slack webhook)
- Escalation cron (auto-escalate after configurable days)

**Dependencies:** Phase 1 complete

**Verification:**
- Price variance exception auto-created on match
- Exception approved with justification -> match status updated
- Invoice routed to correct approver based on amount
- Escalation fires after threshold days
- Separation of duties: recorder cannot approve

### Phase 3: Payment Readiness Gate

**Scope:** Payment blocking and readiness checklist

**Deliverables:**
- Computed `payment_ready` field on `account.move` (vendor bills)
- Gate conditions: match_ok AND approved AND gl_coded AND tax_validated
- Payment readiness checklist widget on invoice form
- Block `account.payment` creation when `payment_ready = False`
- Finance Director override with logged justification
- Batch payment view filtered by `payment_ready = True`
- GL coding verification field
- Tax validation integration (withholding tax computed, VAT input captured)

**Dependencies:** Phase 2 complete, `ipai_finance_tax_return` for tax validation

**Verification:**
- Invoice with incomplete match cannot be paid
- Invoice with all gates passed shows payment_ready = True
- Payment creation blocked for non-ready invoices
- Director override works with justification logged
- Batch view shows only payment-ready invoices

### Phase 4: Aging + Reconciliation

**Scope:** Reporting, reconciliation, and monitoring

**Deliverables:**
- AP aging report (current, 30, 60, 90, 120+ days)
- Aging grouped by vendor, GL account, department
- Vendor statement reconciliation wizard (import CSV/Excel)
- Auto-match vendor statement lines to Odoo invoices
- Discrepancy report (unmatched items on both sides)
- AP dashboard: summary cards, match rate, exception count, aging distribution
- Export to Excel/PDF
- Drill-down from aging to individual invoices
- Integration with close orchestration (AP completeness as gate input)

**Dependencies:** Phase 3 complete

**Verification:**
- Aging report groups correctly by period buckets
- Vendor statement import matches invoices by number + amount
- Unmatched items highlighted on both sides
- Dashboard shows accurate summary metrics
- Excel export produces valid file with correct data

## Dependencies

| Dependency | Type | Purpose |
|-----------|------|---------|
| `account` | Odoo CE | Vendor bills, payments, GL |
| `purchase` | Odoo CE | Purchase orders |
| `stock` | Odoo CE | Goods receipts (stock.picking) |
| `mail` | Odoo CE | Chatter, notifications, activities |
| `ipai_finance_tax_return` | IPAI | Withholding tax validation |
| `ipai_close_orchestration` | IPAI (optional) | Close cycle gate integration |

## OCA Modules to Evaluate

| OCA Module | Repository | Purpose |
|-----------|-----------|---------|
| `purchase_order_approved` | purchase-workflow | PO approval workflow |
| `account_invoice_triple_discount` | account-invoicing | Invoice discount handling |
| `account_move_line_purchase_info` | account-invoicing | PO info on invoice lines |
| `purchase_stock_picking_return_invoicing` | purchase-workflow | Return invoice handling |

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| OCR accuracy below threshold | Manual data entry burden | Confidence scoring + manual review queue |
| Complex PO structures (blanket, multi-receipt) | Matching logic complexity | Start with simple 1:1 match, iterate |
| Vendor resistance to structured invoicing | Low auto-match rate | Vendor communication + flexible matching |
| Performance on large invoice volumes | Slow matching | Index optimization, batch processing |
