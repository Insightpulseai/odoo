# T&E Control — Constitution

## Purpose

Full Travel & Expense (T&E) lifecycle management for TBWA Philippines, replacing SAP Concur with Odoo CE-native workflows. Covers the complete cycle from travel request through reimbursement, NOT just OCR receipt processing (that is `spec/expense-automation/`).

## Non-Negotiables

### 1. Module Identity

- **Module name**: `ipai_finance_tne_control`
- **Extends**: `hr_expense` (CE), `ipai_expense_ocr` (receipt pipeline)
- **Depends**: `hr`, `account`, `mail`, `ipai_platform_approvals`
- **Naming**: All models use `ipai.tne.*` namespace

### 2. CE Only, OCA First

- **Rule**: No Odoo Enterprise modules. No odoo.com IAP.
- **OCA preference**: Use `OCA/hr-expense` extensions before building custom logic.
- **Cost**: Zero per-seat licensing. Self-hosted stack only.

### 3. Full Traceability

- **Rule**: Every expense must be traceable from request to reimbursement.
- **Chain**: Travel Request -> Cash Advance -> Expense Report -> Liquidation -> Reimbursement
- **Audit**: All state changes logged via `mail.thread` + `mail.activity.mixin`.
- **Evidence**: Supporting documents (receipts, approvals) attached at every stage.

### 4. Cash Advance Discipline

- **Rule**: Cash advances MUST have liquidation deadlines.
- **Default deadline**: 5 business days after trip return date.
- **Enforcement**: Auto-escalation cron after deadline. Block new advances if unliquidated balance exists.
- **Reconciliation**: Excess returned to company, shortfall reimbursed to employee.

### 5. Policy Engine Required

- **Rule**: All expenses validated against configurable policy limits before approval.
- **Policies**: Per-diem rates, meal limits, transportation caps, hotel limits, category-specific caps.
- **Override**: Policy violations flagged but can be approved with justification (audit-trailed).

### 6. Approval Integration

- **Rule**: All approvals route through `ipai_platform_approval_inbox` (see `spec/odoo-approval-inbox/`).
- **No separate approval UI**: T&E approvals appear in the unified approval queue.
- **Threshold routing**: Configurable amount-based routing (manager, director, VP).

### 7. Month-End Close Integration

- **Rule**: Outstanding travel advances and unreimbursed expenses must surface in month-end close.
- **Cross-ref**: `spec/close-orchestration/` for close task integration.
- **Accrual**: Auto-generate accrual entries for approved-but-unpaid expenses at period end.

## Boundaries

### In Scope

- Travel request and pre-trip approval workflow
- Cash advance request, issuance, tracking, and liquidation
- Expense report creation with OCR receipt capture (via `ipai_expense_ocr`)
- Policy validation engine (per-diem, meal, transport, hotel limits)
- Liquidation and reconciliation of cash advances
- Reimbursement queue and payment integration
- Mobile-first receipt capture workflow
- Slack notifications for approval events
- Integration with month-end close (`spec/close-orchestration/`)
- Reporting: expense analytics, policy compliance, aging

### Out of Scope

- OCR pipeline internals (handled by `spec/expense-automation/`)
- Corporate credit card integration (Phase 2)
- Mileage tracking and GPS-based claims (Phase 2)
- Multi-currency conversion beyond PHP (Phase 2)
- Per-project expense allocation (handled by `ipai_finance_ppm`)

## Success Criteria

| Metric | Target |
|--------|--------|
| Time from submission to reimbursement | < 5 business days |
| Policy compliance rate | > 95% |
| Cash advance liquidation on-time rate | > 90% |
| Expense report auto-categorization accuracy | > 85% |
| User satisfaction (submitter) | > 4/5 |
| Audit findings on T&E | Zero material findings |

## Cost Constraints

| Component | Monthly Cost |
|-----------|--------------|
| Odoo hr_expense (CE) | $0 |
| ipai_expense_ocr (PaddleOCR-VL) | $0 (self-hosted) |
| ipai_finance_tne_control | $0 |
| n8n workflows | $0 (self-hosted) |
| **Total** | **$0** |
