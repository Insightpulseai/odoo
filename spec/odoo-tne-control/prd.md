# T&E Control — Product Requirements Document

## Problem

TBWA Philippines relies on manual, spreadsheet-driven processes for travel requests, cash advances, expense reports, and reimbursements. This creates:

1. Slow reimbursement cycles (10-15 business days average)
2. Untracked cash advances with missed liquidation deadlines
3. Policy violations discovered only during audit
4. No integration between expense data and month-end close
5. Finance team spends 20+ hours/month on manual reconciliation

## Users

| Role | Description | Key Actions |
|------|-------------|-------------|
| **Employee** | Any staff member incurring business expenses | Submit travel requests, capture receipts, file expense reports, liquidate advances |
| **Manager** | Direct supervisor of the employee | Approve/reject travel requests, expense reports, cash advances |
| **Director/VP** | Senior leadership | Approve high-value requests, view spending analytics |
| **Finance Staff** | Accounts payable team | Process reimbursements, reconcile advances, generate accruals |
| **Finance Director** | Head of finance | Final approval authority, policy configuration, compliance oversight |

## Functional Requirements

### FR-1: Travel Request

Pre-trip approval workflow for planned business travel.

**Data Model: `ipai.tne.travel_request`**

| Field | Type | Description |
|-------|------|-------------|
| employee_id | Many2one(hr.employee) | Requesting employee |
| destination | Char | Travel destination |
| purpose | Text | Business justification |
| date_depart | Date | Departure date |
| date_return | Date | Return date |
| estimated_cost | Monetary | Total estimated cost |
| cost_line_ids | One2many(ipai.tne.cost_line) | Itemized cost estimates |
| advance_requested | Boolean | Whether cash advance is needed |
| advance_amount | Monetary | Requested advance amount |
| state | Selection | draft / submitted / approved / rejected / cancelled |

**Acceptance Criteria:**
- [ ] Employee can create travel request with destination, dates, purpose, and estimated costs
- [ ] Estimated costs broken down by category (airfare, hotel, meals, transport, other)
- [ ] Approval routing based on estimated total cost (configurable thresholds)
- [ ] Approved travel request can trigger cash advance request
- [ ] Travel request linked to resulting expense reports
- [ ] Calendar integration showing approved travel dates

### FR-2: Cash Advance

Request, approval, issuance, and tracking of pre-trip cash disbursements.

**Data Model: `ipai.tne.cash_advance`**

| Field | Type | Description |
|-------|------|-------------|
| employee_id | Many2one(hr.employee) | Receiving employee |
| travel_request_id | Many2one(ipai.tne.travel_request) | Linked travel request |
| amount_requested | Monetary | Amount requested |
| amount_approved | Monetary | Amount approved |
| amount_issued | Monetary | Amount actually issued |
| date_issued | Date | Issuance date |
| liquidation_deadline | Date | Deadline for liquidation |
| amount_liquidated | Monetary | Amount accounted for via expenses |
| amount_excess | Monetary | Computed: issued - liquidated (positive = return to company) |
| state | Selection | draft / submitted / approved / issued / liquidating / liquidated / overdue |

**Acceptance Criteria:**
- [ ] Cash advance linked to approved travel request
- [ ] Liquidation deadline auto-calculated: return date + 5 business days (configurable)
- [ ] Block new advance requests if employee has unliquidated balance > 0
- [ ] Auto-transition to `overdue` state via cron when deadline passes
- [ ] Escalation notification to finance director on overdue advances
- [ ] Journal entries: debit Advance Receivable, credit Cash on issuance

### FR-3: Expense Report

Receipt capture, categorization, and submission of incurred expenses.

**Data Model: extends `hr.expense.sheet` + `ipai.tne.expense_report`**

| Field | Type | Description |
|-------|------|-------------|
| travel_request_id | Many2one(ipai.tne.travel_request) | Linked travel request (optional) |
| cash_advance_id | Many2one(ipai.tne.cash_advance) | Linked cash advance (optional) |
| expense_line_ids | One2many(hr.expense) | Individual expense items |
| policy_violation_ids | One2many(ipai.tne.policy_violation) | Detected policy violations |
| total_claimed | Monetary | Sum of all expense lines |
| total_approved | Monetary | Sum of approved lines |

**Acceptance Criteria:**
- [ ] Receipt capture via mobile camera triggers OCR (delegates to `ipai_expense_ocr`)
- [ ] OCR results auto-fill: vendor, amount, date, category
- [ ] Employee can edit/correct OCR results before submission
- [ ] Each expense line validated against policy engine (FR-5)
- [ ] Policy violations flagged with severity (warning vs blocking)
- [ ] Expense report can be linked to travel request and/or cash advance
- [ ] Support for non-travel expenses (office supplies, client meals, etc.)
- [ ] Draft save and resume capability
- [ ] Attachments: receipt images, PDF invoices

### FR-4: Liquidation

Reconciliation of cash advance against actual expenses incurred.

**Data Model: `ipai.tne.liquidation`**

| Field | Type | Description |
|-------|------|-------------|
| cash_advance_id | Many2one(ipai.tne.cash_advance) | Advance being liquidated |
| expense_report_id | Many2one(ipai.tne.expense_report) | Supporting expense report |
| amount_advanced | Monetary | Original advance amount |
| amount_expensed | Monetary | Total approved expenses |
| amount_excess | Monetary | Computed: advanced - expensed (employee owes company) |
| amount_shortfall | Monetary | Computed: expensed - advanced (company owes employee) |
| state | Selection | draft / submitted / approved / settled |

**Acceptance Criteria:**
- [ ] Auto-compute excess (return to company) or shortfall (reimburse to employee)
- [ ] Excess triggers accounts receivable entry; shortfall triggers reimbursement
- [ ] Liquidation must reference a submitted expense report
- [ ] Finance staff can approve liquidation independently of expense approval
- [ ] Journal entries auto-generated on liquidation approval
- [ ] Close the cash advance record upon settlement

### FR-5: Policy Engine

Configurable expense policy validation applied at submission time.

**Data Model: `ipai.tne.policy_rule`**

| Field | Type | Description |
|-------|------|-------------|
| name | Char | Rule name |
| category_id | Many2one(product.category) | Expense category this rule applies to |
| limit_type | Selection | per_day / per_trip / per_item / per_month |
| limit_amount | Monetary | Maximum allowed amount |
| applies_to | Selection | all / department / job_position |
| severity | Selection | warning / blocking |
| active | Boolean | Whether rule is enforced |

**Default Policy Rules (TBWA Philippines):**

| Category | Limit Type | Amount (PHP) | Severity |
|----------|-----------|--------------|----------|
| Meals - Client | per_day | 2,500 | warning |
| Meals - Team | per_day | 1,500 | warning |
| Hotel | per_night | 5,000 | warning |
| Domestic Airfare | per_trip | 15,000 | warning |
| International Airfare | per_trip | 50,000 | blocking |
| Ground Transport | per_day | 1,000 | warning |
| Per Diem (Domestic) | per_day | 3,000 | blocking |
| Per Diem (International) | per_day | 8,000 | blocking |

**Acceptance Criteria:**
- [ ] Policy rules configurable per expense category
- [ ] Rules can be scoped to department or job position
- [ ] Warning-level violations allow submission with justification text
- [ ] Blocking-level violations prevent submission entirely
- [ ] Policy violations visible to approvers in approval queue
- [ ] Policy rule changes audit-trailed

### FR-6: Reimbursement

Approved expenses queued for payment processing.

**Acceptance Criteria:**
- [ ] Approved expense reports auto-create payment queue entries
- [ ] Finance staff can batch-process reimbursements
- [ ] Reimbursement linked to accounting journal entries (debit Expense, credit AP/Cash)
- [ ] Employee notified via Slack when reimbursement is processed
- [ ] Support for both bank transfer and petty cash reimbursement methods

### FR-7: Mobile Receipt Capture

Mobile-optimized interface for capturing receipts in the field.

**Acceptance Criteria:**
- [ ] Camera capture directly from Odoo mobile web interface
- [ ] Image auto-compressed before upload (< 2MB)
- [ ] Offline capture with sync when connectivity returns (stretch goal)
- [ ] Multiple receipts per expense report
- [ ] OCR processing triggered automatically on upload

### FR-8: Reporting and Analytics

**Reports:**

| Report | Audience | Frequency |
|--------|----------|-----------|
| Expense by Category | Finance Director | Monthly |
| Policy Violation Summary | Finance Director | Monthly |
| Cash Advance Aging | Finance Staff | Weekly |
| Reimbursement Status | All Employees | On-demand |
| T&E Budget vs Actual | Department Heads | Monthly |
| Travel Request Pipeline | Finance Staff | On-demand |

## Non-Functional Requirements

- **Approval notification latency**: < 60 seconds (via Slack)
- **OCR processing time**: < 30 seconds per receipt
- **Mobile responsiveness**: Full functionality on mobile web
- **Audit trail**: All state changes logged with user, timestamp, and comments
- **Data retention**: Expense records retained for 10 years (BIR requirement)

## Integration Points

| System | Integration | Direction |
|--------|-------------|-----------|
| `ipai_expense_ocr` | Receipt OCR processing | Outbound (send image) / Inbound (receive data) |
| `ipai_platform_approval_inbox` | Unified approval queue | Outbound (register approval requests) |
| `spec/close-orchestration/` | Month-end accruals and reporting | Outbound (surface outstanding items) |
| `spec/odoo-workspace-os/` Layer 2 | Expense AI module context | Architectural alignment |
| Slack (`ipai_slack_connector`) | Notifications for all T&E events | Outbound |
| n8n | Workflow automation (escalation crons, report generation) | Bidirectional |
| Accounting (`account`) | Journal entries for advances, expenses, reimbursements | Outbound |

## Success Metrics

| Metric | Target |
|--------|--------|
| Time to submit expense report | < 3 minutes |
| Approval turnaround | < 24 hours |
| End-to-end reimbursement cycle | < 5 business days |
| Policy compliance rate | > 95% |
| Cash advance liquidation on-time | > 90% |
| OCR auto-fill accuracy | > 85% |
