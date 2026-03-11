# T&E Control — Implementation Plan

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                    ipai_finance_tne_control                          │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────────────────┐ │
│  │ Travel       │──▶│ Cash         │──▶│ Expense Report           │ │
│  │ Request      │   │ Advance      │   │ (extends hr.expense)     │ │
│  └──────────────┘   └──────────────┘   │ + OCR via ipai_expense_  │ │
│         │                  │            │   ocr                    │ │
│         │                  │            └──────────────────────────┘ │
│         │                  ▼                       │                 │
│         │           ┌──────────────┐               ▼                │
│         │           │ Liquidation  │        ┌──────────────┐        │
│         │           │ Engine       │        │ Policy       │        │
│         │           └──────────────┘        │ Engine       │        │
│         │                  │                └──────────────┘        │
│         │                  ▼                       │                │
│         │           ┌──────────────┐               ▼                │
│         └──────────▶│ Reimbursement│◀──────────────┘                │
│                     │ Queue        │                                │
│                     └──────────────┘                                │
│                            │                                        │
├────────────────────────────┼────────────────────────────────────────┤
│  Integrations              ▼                                        │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────────┐ │
│  │ Approval   │  │ Close      │  │ Slack      │  │ Accounting   │ │
│  │ Inbox      │  │ Orchestr.  │  │ Connector  │  │ (account)    │ │
│  └────────────┘  └────────────┘  └────────────┘  └──────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

## Module Structure

```
addons/ipai/ipai_finance_tne_control/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── travel_request.py          # ipai.tne.travel_request
│   ├── travel_cost_line.py        # ipai.tne.cost_line
│   ├── cash_advance.py            # ipai.tne.cash_advance
│   ├── expense_report.py          # ipai.tne.expense_report (extends hr.expense.sheet)
│   ├── liquidation.py             # ipai.tne.liquidation
│   ├── policy_rule.py             # ipai.tne.policy_rule
│   ├── policy_violation.py        # ipai.tne.policy_violation
│   └── reimbursement.py           # ipai.tne.reimbursement
├── views/
│   ├── travel_request_views.xml
│   ├── cash_advance_views.xml
│   ├── expense_report_views.xml
│   ├── liquidation_views.xml
│   ├── policy_rule_views.xml
│   ├── reimbursement_views.xml
│   └── menu.xml
├── security/
│   ├── ir.model.access.csv
│   └── tne_security.xml
├── data/
│   ├── policy_rules_data.xml      # Default TBWA policy rules
│   ├── mail_template_data.xml     # Email templates
│   ├── cron_data.xml              # Scheduled actions (overdue checks)
│   └── sequence_data.xml          # TR-YYYY-NNNN, CA-YYYY-NNNN sequences
├── wizards/
│   ├── __init__.py
│   ├── batch_reimburse.py         # Batch reimbursement wizard
│   └── batch_reimburse_views.xml
├── reports/
│   ├── expense_by_category.xml
│   ├── policy_violation_summary.xml
│   └── cash_advance_aging.xml
├── static/
│   └── description/
│       └── icon.png
└── tests/
    ├── __init__.py
    ├── test_travel_request.py
    ├── test_cash_advance.py
    ├── test_liquidation.py
    └── test_policy_engine.py
```

## Milestones

### Phase 1: Travel Request + Cash Advance (Week 1-2)

**Goal**: Employees can request travel approval and cash advances.

- [ ] Create `ipai.tne.travel_request` model with full state machine
- [ ] Create `ipai.tne.cost_line` model for itemized estimates
- [ ] Build travel request form, tree, and Kanban views
- [ ] Implement approval routing (amount-based thresholds)
- [ ] Create `ipai.tne.cash_advance` model linked to travel requests
- [ ] Build cash advance form and tree views
- [ ] Implement liquidation deadline auto-calculation
- [ ] Add sequence generators (TR-YYYY-NNNN, CA-YYYY-NNNN)
- [ ] Security groups: tne_user, tne_manager, tne_finance, tne_director
- [ ] Register travel request and cash advance with `ipai_platform_approval_inbox`

**Verification:**
```bash
docker compose exec -T web odoo -d odoo -i ipai_finance_tne_control --stop-after-init
# Verify models registered
docker compose exec -T web odoo shell -d odoo -c "print(env['ipai.tne.travel_request'].search_count([]))"
```

### Phase 2: Expense Report + Receipt OCR Integration (Week 3-4)

**Goal**: Employees can submit expense reports with OCR-powered receipt capture.

- [ ] Extend `hr.expense.sheet` with T&E fields (travel_request_id, cash_advance_id)
- [ ] Build `ipai.tne.expense_report` view extensions
- [ ] Integrate with `ipai_expense_ocr` for receipt processing
- [ ] Implement mobile-responsive receipt capture UI
- [ ] Auto-fill expense line from OCR results (vendor, amount, date, category)
- [ ] Add employee edit/correction flow for OCR results
- [ ] Support multiple receipts per expense report
- [ ] Draft save and resume capability
- [ ] Register expense reports with `ipai_platform_approval_inbox`

**Verification:**
```bash
# Test OCR integration
docker compose exec -T web odoo -d odoo -u ipai_finance_tne_control --stop-after-init
curl -s http://localhost:8069/web/health | grep -q "ok"
```

### Phase 3: Liquidation + Reimbursement Workflow (Week 5-6)

**Goal**: Cash advances are reconciled and approved expenses are reimbursed.

- [ ] Create `ipai.tne.liquidation` model with reconciliation logic
- [ ] Auto-compute excess (employee owes) vs shortfall (company owes)
- [ ] Generate journal entries for liquidation settlement
- [ ] Create `ipai.tne.reimbursement` queue model
- [ ] Build batch reimbursement wizard for finance staff
- [ ] Journal entry generation: debit Expense accounts, credit AP/Cash
- [ ] Slack notifications on reimbursement processing
- [ ] Overdue cash advance cron job (daily check, auto-escalate)
- [ ] Block new advances for employees with overdue liquidations

**Verification:**
```bash
# Run liquidation tests
docker compose exec -T web odoo -d odoo --test-enable --test-tags ipai_finance_tne_control -u ipai_finance_tne_control --stop-after-init
```

### Phase 4: Policy Engine + Compliance Reports (Week 7-8)

**Goal**: All expenses validated against configurable policies; compliance reports available.

- [ ] Create `ipai.tne.policy_rule` model with limit types and scopes
- [ ] Create `ipai.tne.policy_violation` model for tracking violations
- [ ] Load default TBWA policy rules (per-diem, meal, hotel, transport limits)
- [ ] Implement policy validation on expense report submission
- [ ] Warning vs blocking severity enforcement
- [ ] Policy override with justification (audit-trailed)
- [ ] Build reports: Expense by Category, Policy Violations, Cash Advance Aging
- [ ] T&E Budget vs Actual report per department
- [ ] Month-end close integration: surface outstanding advances and unreimbursed expenses
- [ ] Generate accrual journal entries for approved-but-unpaid expenses at period end

**Verification:**
```bash
# Full test suite
docker compose exec -T web odoo -d odoo --test-enable --test-tags ipai_finance_tne_control --stop-after-init
# Policy engine validation
docker compose exec -T web odoo shell -d odoo -c "
rules = env['ipai.tne.policy_rule'].search([('active','=',True)])
print(f'{len(rules)} active policy rules')
"
```

## Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| OCR Provider | PaddleOCR-VL (self-hosted) | Zero per-scan cost, privacy, no vendor lock-in |
| Approval UI | Unified inbox (`ipai_platform_approval_inbox`) | Single queue, no fragmented approval UIs |
| Notifications | Slack + email fallback | Slack is primary channel (Mattermost deprecated) |
| Policy storage | Odoo model (`ipai.tne.policy_rule`) | Configurable by finance team without code changes |
| Journal entries | Odoo `account.move` | Native accounting integration |
| Mobile capture | Odoo web responsive | No separate mobile app needed |

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| OCR accuracy below 85% | Manual data entry burden | Confidence scoring, human review queue for low-confidence |
| Policy rules too restrictive | Employee frustration, workarounds | Warning severity for soft limits, blocking only for hard limits |
| Cash advance overdue accumulation | Financial exposure | Daily cron, escalation chain, new-advance blocking |
| Month-end accrual timing | Incorrect financial statements | Close integration validates outstanding T&E items |

## Dependencies

| Dependency | Status | Impact if Delayed |
|------------|--------|-------------------|
| `hr_expense` (CE) | Available | Blocks Phase 2 |
| `ipai_expense_ocr` | See `spec/expense-automation/` | Phase 2 OCR features deferred |
| `ipai_platform_approval_inbox` | See `spec/odoo-approval-inbox/` | Use basic Odoo approval until available |
| `ipai_slack_connector` | Existing | Notifications deferred if unavailable |
| `spec/close-orchestration/` | Existing | Month-end integration deferred to Phase 4 |
