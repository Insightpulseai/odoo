# PRD — DocFlow Agentic Finance

## Objective

Reduce manual encoding of expenses and vendor bills by ≥80% using local OCR + LLM reasoning integrated with Odoo.

## Scope

### In Scope

- Expense receipts (hr.expense draft)
- Vendor invoices/bills (account.move draft, move_type=in_invoice)
- Local OCR + layout hints
- LLM classification + schema extraction (text-only)
- Audit logging

### Out of Scope (v1)

- AR invoices
- Payment matching/reconciliation
- Bank statement import

## Functional Requirements

- Directory ingestion (inbox/archive)
- OCR for PDF/image
- Classify doc type (expense/invoice/unknown)
- Extract schema (invoice/expense)
- Validate totals/dates + confidence threshold routing
- Create Odoo drafts with attachments
- Persist artifacts (OCR + LLM JSON + Odoo links)

## Success Metrics

- < 2 minutes per doc end-to-end
- ≥95% accuracy for totals/dates on accepted drafts
- ≤20% manual correction rate
