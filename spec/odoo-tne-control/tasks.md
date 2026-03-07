# T&E Control — Task Checklist

## Phase 1: Travel Request + Cash Advance

### Models
- [ ] Create `ipai.tne.travel_request` model with state machine (draft/submitted/approved/rejected/cancelled)
- [ ] Create `ipai.tne.cost_line` model for itemized travel cost estimates
- [ ] Create `ipai.tne.cash_advance` model with state machine (draft/submitted/approved/issued/liquidating/liquidated/overdue)
- [ ] Add sequence generators: TR-YYYY-NNNN, CA-YYYY-NNNN
- [ ] Implement liquidation deadline auto-calculation (return_date + 5 business days)
- [ ] Add constraint: block new advance if employee has unliquidated balance > 0

### Views
- [ ] Travel request form view with cost line inline editing
- [ ] Travel request tree and Kanban views
- [ ] Cash advance form view linked to travel request
- [ ] Cash advance tree view with aging indicators
- [ ] Menu items under Expenses > Travel & Entertainment

### Security
- [ ] Create security groups: tne_user, tne_manager, tne_finance, tne_director
- [ ] Access rules: employees see own records, managers see team, finance sees all
- [ ] Record rules by company

### Approval Integration
- [ ] Register travel request approval type with `ipai_platform_approvals`
- [ ] Register cash advance approval type with `ipai_platform_approvals`
- [ ] Configure amount-based approval routing thresholds

### Tests
- [ ] Test travel request state transitions
- [ ] Test cost line total computation
- [ ] Test cash advance deadline calculation
- [ ] Test advance blocking constraint

## Phase 2: Expense Report + OCR Integration

### Models
- [ ] Extend `hr.expense.sheet` with travel_request_id and cash_advance_id fields
- [ ] Create `ipai.tne.expense_report` proxy/extension model
- [ ] Add OCR result fields to `hr.expense` (ocr_confidence, ocr_raw_data)

### OCR Integration
- [ ] Hook into `ipai_expense_ocr` receipt processing pipeline
- [ ] Implement auto-fill from OCR results (vendor, amount, date, category)
- [ ] Build employee correction/review UI for OCR results
- [ ] Add confidence threshold display (green/yellow/red indicator)

### Views
- [ ] Expense report form with travel request linkage
- [ ] Mobile-responsive receipt capture view
- [ ] Multi-receipt upload interface
- [ ] Draft save/resume indicator

### Approval Integration
- [ ] Register expense report approval type with `ipai_platform_approvals`
- [ ] Include policy violation summary in approval context

### Tests
- [ ] Test OCR auto-fill mapping
- [ ] Test expense report linkage to travel request
- [ ] Test multi-receipt handling
- [ ] Test draft save and resume

## Phase 3: Liquidation + Reimbursement

### Models
- [ ] Create `ipai.tne.liquidation` model with reconciliation computation
- [ ] Create `ipai.tne.reimbursement` queue model
- [ ] Auto-compute excess vs shortfall amounts
- [ ] Implement journal entry generation for liquidation settlement

### Workflows
- [ ] Liquidation submission and approval flow
- [ ] Excess return: AR entry against employee
- [ ] Shortfall reimbursement: payment queue entry
- [ ] Cash advance record closure on settlement

### Batch Processing
- [ ] Create batch reimbursement wizard
- [ ] Support bank transfer and petty cash methods
- [ ] Generate payment batch report

### Automation
- [ ] Overdue cash advance detection cron (daily)
- [ ] Auto-escalation to finance director on overdue
- [ ] Slack notification on reimbursement completion
- [ ] Email fallback for Slack notification failures

### Tests
- [ ] Test liquidation excess computation
- [ ] Test liquidation shortfall computation
- [ ] Test journal entry generation
- [ ] Test overdue detection cron
- [ ] Test advance blocking on overdue

## Phase 4: Policy Engine + Reports

### Policy Engine
- [ ] Create `ipai.tne.policy_rule` model with configurable limits
- [ ] Create `ipai.tne.policy_violation` model for tracking
- [ ] Load default TBWA policy rules (seed data XML)
- [ ] Implement per-day, per-trip, per-item, per-month limit types
- [ ] Implement department and job position scoping
- [ ] Warning severity: flag but allow submission with justification
- [ ] Blocking severity: prevent submission entirely
- [ ] Policy validation hook on expense report submission
- [ ] Policy override audit trail

### Reports
- [ ] Expense by Category report (monthly, by department)
- [ ] Policy Violation Summary report (monthly)
- [ ] Cash Advance Aging report (weekly)
- [ ] Reimbursement Status report (on-demand, per employee)
- [ ] T&E Budget vs Actual report (monthly, per department)
- [ ] Travel Request Pipeline report (on-demand)

### Month-End Close Integration
- [ ] Surface outstanding advances in close orchestration tasks
- [ ] Surface unreimbursed expenses in close orchestration tasks
- [ ] Auto-generate accrual entries for approved-but-unpaid expenses
- [ ] Close period validation: check for stale advances

### Tests
- [ ] Test policy rule validation (per-day limit)
- [ ] Test policy rule validation (per-trip limit)
- [ ] Test warning vs blocking severity enforcement
- [ ] Test policy override with justification
- [ ] Test department-scoped policy rules
- [ ] Test accrual entry generation
- [ ] Test close period validation

## Verification Checkpoints

### Phase 1 Complete
- [ ] Module installs without error (`--stop-after-init`)
- [ ] Travel request can be created and approved
- [ ] Cash advance linked to travel request
- [ ] Liquidation deadline computed correctly
- [ ] Security groups enforce access control

### Phase 2 Complete
- [ ] Receipt upload triggers OCR pipeline
- [ ] OCR results auto-fill expense fields
- [ ] Expense report links to travel request
- [ ] Mobile capture functional on phone browser

### Phase 3 Complete
- [ ] Liquidation correctly computes excess/shortfall
- [ ] Journal entries post to correct accounts
- [ ] Batch reimbursement wizard processes multiple records
- [ ] Overdue cron detects and escalates stale advances

### Phase 4 Complete
- [ ] All default policy rules loaded
- [ ] Policy violations flagged on submission
- [ ] All 6 reports render correctly
- [ ] Month-end close surfaces outstanding T&E items
- [ ] Full test suite passes
