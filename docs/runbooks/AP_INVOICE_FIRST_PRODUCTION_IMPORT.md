# Runbook: AP Invoice First Controlled Production Import

## Objective
Supervised execution of the first live AP invoice import to validate runtime stability and TaxPulse compliance under real accounting data.

## Scope
- **Batch Size**: 1 Known-Safe Supplier Bill.
- **Operator**: Required (Manual trigger of `AI Verify Tax`).
- **Safety**: No bulk auto-posting allowed.

## Pre-Flight Checklist
- [ ] Odoo module `ipai_ap_invoice` version 1.0.0 installed.
- [ ] TaxPulse specialist reachable.
- [ ] Vendor VAT registration verified in Odoo.
- [ ] Staging rehearsal evidence verified.

## Execution Steps
1. **Ingestion**: Run `action_ipai_ingest_ocr()` on the target bill.
2. **Review**: Verify OCR extraction accuracy.
3. **Validation**: Run `action_ipai_verify_tax()`.
4. **Posting**: If state is `approved_to_post`, execute `action_post()`.

## Post-Execution
- Capture logs into `docs/evidence/ap-invoice-first-prod/`.
- Sign off `operator-review.md`.
