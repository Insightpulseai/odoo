# AP Invoice Control - Constitution

## Non-Negotiables

### 1. Module Identity

- **Module name**: `ipai_finance_ap_control`
- **Extends**: `account` (Odoo CE accounting), `purchase` (Odoo CE purchase)
- **Dependencies**: `account`, `purchase`, `stock`, `mail`
- **CE only**: No Odoo Enterprise modules, no odoo.com IAP
- **OCA first**: Use OCA modules (`account_invoice_triple_discount`, `purchase_order_approved`, etc.) before building custom logic

### 2. Three-Way Match Mandate

- **PO <-> Receipt <-> Invoice** matching is mandatory for all purchase invoices
- No invoice can reach "payment ready" status without a completed three-way match
- Exceptions (no-PO invoices, partial receipts) must go through documented exception workflow
- Match tolerance thresholds are configurable per company (default: 0% price, 0% quantity)

### 3. Exception Workflow

- All match exceptions must be explicitly resolved (approved or rejected)
- Exception types: price_variance, quantity_variance, no_po, partial_receipt, duplicate_invoice
- Exception approval follows amount-based routing (thresholds configurable)
- Unresolved exceptions block payment processing
- Exception resolution requires documented justification

### 4. Payment Readiness Gate

- An invoice can only be paid when ALL of the following are true:
  - Three-way match completed (or exception approved)
  - Approval workflow completed (amount-based routing)
  - GL coding verified
  - Tax validation passed (withholding tax, VAT input)
- Payment readiness is a computed boolean, not a manual checkbox
- Gate status visible on invoice form and in payment batch views

### 5. Audit Trail

- All matching actions logged with user, timestamp, and match details
- Exception approvals logged with justification and approver
- Payment readiness gate changes logged
- No deletion of matched invoices or resolved exceptions

### 6. Separation of Duties

- Invoice recorder cannot approve the same invoice
- Three-way match reviewer cannot be the payment processor
- Exception approver must have appropriate authority level (amount-based)

### 7. Integration Constraints

- OCR ingestion leverages patterns from `spec/expense-automation/` (receipt scanning pipeline)
- Approval gates follow patterns from `spec/close-orchestration/` (three-stage workflow)
- Vendor master data from Odoo `res.partner` (no separate vendor database)
- Withholding tax validation integrates with `spec/bir-tax-compliance/`
