# Approval Inbox — Task Checklist

## Phase 1: Generic Approval Model + Inbox UI

### Core Models
- [ ] Create `ipai.approval.connector` abstract model with interface methods
  - [ ] `get_approval_domain()` — return domain identifier
  - [ ] `get_pending_approvals(user)` — return pending items for user
  - [ ] `get_approval_summary(record)` — return display dict (title, amount, requester, date, priority)
  - [ ] `execute_approve(record, user, comment)` — approve via domain logic
  - [ ] `execute_reject(record, user, comment)` — reject via domain logic
- [ ] Create `ipai.approval.item` transient model for aggregated inbox view
- [ ] Create `ipai.approval.log` model for immutable audit trail
  - [ ] Fields: user_id, action (approve/reject/delegate/escalate), comment, timestamp, source_model, source_id, delegated_from_id
  - [ ] Enforce immutability (no write/unlink on confirmed records)

### Inbox UI
- [ ] List view: domain badge, title, requester, amount, age, priority
- [ ] Kanban view grouped by domain
- [ ] Calendar view by submitted date
- [ ] Filter presets: By Domain, By Priority, Overdue, This Week
- [ ] Sort options: date submitted, priority, amount, requester
- [ ] Search: title, requester name, amount range
- [ ] Badge count on "My Approvals" menu item

### Actions
- [ ] Single-item approve button with comment dialog
- [ ] Single-item reject button with required comment dialog
- [ ] Approve/reject executes domain connector method
- [ ] Audit log entry created on every action
- [ ] Success/failure toast notification after action

### Security
- [ ] Create security groups: approval_user (all employees), approval_admin
- [ ] Access rules: users see only their own pending approvals
- [ ] Admin can view all approvals and configure settings

### Reference Connector
- [ ] Implement `hr_expense` connector as reference implementation
- [ ] Register connector on module install
- [ ] Test: expense approval appears in inbox

### Tests
- [ ] Test connector registration and discovery
- [ ] Test approval item aggregation from single connector
- [ ] Test approve action delegates to connector
- [ ] Test reject action delegates to connector
- [ ] Test audit log creation on approve/reject
- [ ] Test audit log immutability

## Phase 2: Domain Connectors

### Expense Connector (ipai_finance_tne_control)
- [ ] Implement travel request approval connector
- [ ] Implement cash advance approval connector
- [ ] Implement expense report approval connector
- [ ] Summary: employee name, destination/purpose, amount, date range
- [ ] Include policy violation count in summary

### Close Connector (ipai_close_orchestration)
- [ ] Implement close task review connector
- [ ] Implement approval gate connector
- [ ] Summary: cycle name, task name, department, due date
- [ ] Include completion percentage in summary

### Invoice Connector (accounts payable)
- [ ] Implement vendor invoice approval connector
- [ ] Summary: vendor name, invoice number, amount, due date
- [ ] Include matching status (PO matched / unmatched)

### BIR Filing Connector (ipai_finance_bir_compliance)
- [ ] Implement BIR return filing approval connector
- [ ] Summary: form type, period, amount, filing deadline
- [ ] Include compliance status indicator

### Integration Tests
- [ ] Test multi-domain inbox aggregation
- [ ] Test domain filter shows only selected domain items
- [ ] Test cross-domain sort (by date, priority)
- [ ] Test connector failure isolation (one failing connector doesn't break inbox)

## Phase 3: Delegation + Escalation Engine

### Delegation
- [ ] Create `ipai.approval.delegation` model
  - [ ] Fields: delegator_id, delegate_id, date_start, date_end, domain_ids, active
- [ ] Build "Set Delegation" wizard
  - [ ] Select delegate user
  - [ ] Set date range
  - [ ] Optionally scope to specific domains
- [ ] Implement auto-forwarding logic
  - [ ] New approval items check for active delegation
  - [ ] Forward to delegate if delegation active and in-scope
- [ ] "On behalf of [delegator]" indicator in inbox
- [ ] Delegation revocation (early end)
- [ ] Multiple delegation support (different domains, different delegates)
- [ ] Delegation audit trail

### Escalation
- [ ] Create `ipai.approval.escalation_rule` model
  - [ ] Fields: domain, threshold_hours, escalate_to (manager/director/specific_user), escalate_user_id, notify_original, active
- [ ] Load default escalation rules (seed data XML)
- [ ] Implement escalation cron job (every 4 hours)
  - [ ] Query all pending items older than threshold
  - [ ] Level 1 (50% of threshold): Send reminder to original approver
  - [ ] Level 2 (100% of threshold): Reassign to escalation target
- [ ] Escalation indicator in inbox (visual badge)
- [ ] Notification on escalation (to original approver and escalation target)
- [ ] Escalation history in audit log

### Batch Operations
- [ ] Build batch approve wizard
  - [ ] Accept list of approval item IDs
  - [ ] Single comment field applied to all
  - [ ] Same-domain validation
  - [ ] Process each item independently (failure isolation)
  - [ ] Return summary: N approved, M failed with reasons
- [ ] Build batch reject wizard (same pattern)
- [ ] List view multi-select checkboxes
- [ ] "Approve Selected" and "Reject Selected" toolbar buttons
- [ ] Progress indicator during batch processing

### Tests
- [ ] Test delegation creation and auto-forwarding
- [ ] Test delegation scoped to specific domain
- [ ] Test delegation revocation
- [ ] Test delegate sees "on behalf of" indicator
- [ ] Test escalation cron detects overdue items
- [ ] Test Level 1 reminder vs Level 2 reassignment
- [ ] Test batch approve within same domain
- [ ] Test batch reject with required comment
- [ ] Test batch operation cross-domain rejection
- [ ] Test batch partial failure handling

## Phase 4: Mobile + Slack Integration

### Mobile Responsiveness
- [ ] Responsive CSS for inbox list view (stacked layout on small screens)
- [ ] Touch-friendly approve/reject buttons (min 44px tap target)
- [ ] Mobile-friendly batch select (long-press to enter select mode)
- [ ] Delegation management accessible on mobile

### Slack Integration
- [ ] Slack notification on new approval request
  - [ ] Include: domain, title, requester, amount, priority
  - [ ] Action buttons: Approve, Reject, View in Odoo
- [ ] Slack notification on escalation
  - [ ] Include: urgency level, original approver, how overdue
- [ ] Slack notification on delegation activation
- [ ] Approve/reject directly from Slack (via webhook callback)
- [ ] Rate limiting: max 1 notification per item per channel per hour

### Email Integration
- [ ] Email template for new approval request
- [ ] Email template for escalation
- [ ] One-click approve link in email (token-based, single-use)
- [ ] Email digest option: daily summary of pending items

### Notification Preferences
- [ ] Create `ipai.approval.notification_pref` model
  - [ ] Per-user, per-channel (Slack/email/in-app) opt-in/out
  - [ ] Per-event-type preferences
- [ ] Settings page for users to manage preferences

### Analytics Dashboard
- [ ] Dashboard view with KPI tiles:
  - [ ] Total pending approvals
  - [ ] Average turnaround time (24h trend)
  - [ ] Escalation rate (30-day rolling)
  - [ ] Top bottleneck approvers
- [ ] Drill-down from KPI tile to filtered inbox view
- [ ] Approval turnaround report (by domain, by approver)
- [ ] Bottleneck analysis report
- [ ] Escalation frequency report
- [ ] CSV export for all reports

### Tests
- [ ] Test Slack notification dispatch
- [ ] Test email notification dispatch
- [ ] Test notification preference enforcement
- [ ] Test one-click email approve link
- [ ] Test dashboard data accuracy
- [ ] Test report export to CSV

## Verification Checkpoints

### Phase 1 Complete
- [ ] Module installs without error (`--stop-after-init`)
- [ ] Reference connector (hr_expense) populates inbox
- [ ] Single-item approve/reject works
- [ ] Audit log records created
- [ ] Security groups enforce access control

### Phase 2 Complete
- [ ] All 4 domain connectors registered
- [ ] Inbox shows items from all domains
- [ ] Domain filter works correctly
- [ ] Connector failure doesn't break inbox

### Phase 3 Complete
- [ ] Delegation auto-forwards approvals
- [ ] Escalation cron detects and escalates overdue items
- [ ] Batch approve processes multiple items
- [ ] All delegation and escalation audit-trailed

### Phase 4 Complete
- [ ] Inbox functional on mobile browser
- [ ] Slack notifications with action buttons
- [ ] Email one-click approve works
- [ ] Dashboard shows accurate KPIs
- [ ] Full test suite passes
