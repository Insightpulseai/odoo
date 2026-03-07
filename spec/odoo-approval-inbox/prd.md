# Approval Inbox — Product Requirements Document

## Problem

TBWA Philippines has multiple approval workflows across different Odoo modules, each with its own UI:

1. Expense approvals in `hr_expense`
2. Invoice approvals in `account.move`
3. Month-end close approvals in `ipai_close_orchestration`
4. Travel request approvals in `ipai_finance_tne_control`
5. Cash advance approvals in `ipai_finance_tne_control`
6. BIR filing approvals in `ipai_finance_bir_compliance`

This creates:
- Approvers must check 5+ different screens daily
- Approvals missed because approver didn't check the right module
- No delegation when approver is on leave — items stall
- No escalation — items can sit unapproved for weeks
- No batch operations — each item approved individually
- Inconsistent approval audit trails across modules

## Users

| Role | Description | Key Actions |
|------|-------------|-------------|
| **Approver** | Any user with approval authority | Review, approve, reject, delegate, batch-approve |
| **Delegate** | Temporary approval proxy | Approve on behalf of absent approver |
| **Requester** | Employee who submitted the item | View approval status, respond to rejection |
| **Admin** | System administrator | Configure escalation rules, manage delegation policies |
| **Finance Director** | Escalation endpoint | Handle escalated approvals, view analytics |

## Functional Requirements

### FR-1: Domain Connector Registry

A mixin pattern that allows any Odoo module to register its approval types with the inbox.

**Connector Interface: `ipai.approval.connector` (Abstract Model)**

```python
class ApprovalConnector(models.AbstractModel):
    _name = 'ipai.approval.connector'

    def get_approval_domain(self):
        """Return domain identifier string (e.g., 'expense', 'invoice')"""
        raise NotImplementedError

    def get_pending_approvals(self, user):
        """Return recordset of items pending approval by this user"""
        raise NotImplementedError

    def get_approval_summary(self, record):
        """Return dict with: title, amount, requester, submitted_date, priority, url"""
        raise NotImplementedError

    def execute_approve(self, record, user, comment):
        """Execute domain-specific approval logic"""
        raise NotImplementedError

    def execute_reject(self, record, user, comment):
        """Execute domain-specific rejection logic"""
        raise NotImplementedError
```

**Acceptance Criteria:**
- [ ] Abstract model defines connector interface
- [ ] Domain modules implement connector to register their approval types
- [ ] Inbox discovers all registered connectors at runtime
- [ ] Adding a new domain requires ZERO changes to the inbox module
- [ ] Connector provides: domain name, display icon, color

### FR-2: Unified Inbox View

Single view showing all pending approvals across all registered domains.

**Data Model: `ipai.approval.item` (Transient/Virtual)**

| Field | Type | Description |
|-------|------|-------------|
| domain | Char | Source domain (expense, invoice, close, etc.) |
| domain_icon | Char | Icon class for the domain |
| source_model | Char | Source Odoo model name |
| source_id | Integer | Source record ID |
| title | Char | Human-readable title |
| requester_id | Many2one(hr.employee) | Who submitted |
| amount | Monetary | Amount (if applicable) |
| currency_id | Many2one(res.currency) | Currency |
| submitted_date | Datetime | When submitted |
| age_days | Integer | Days since submission (computed) |
| priority | Selection | low / normal / high / urgent |
| delegated_from_id | Many2one(res.users) | Original approver if delegated |
| state | Selection | pending / approved / rejected / escalated / delegated |

**Acceptance Criteria:**
- [ ] Single list view showing all pending items sorted by priority then age
- [ ] Kanban view grouped by domain
- [ ] Each item shows: domain badge, title, requester, amount, age, priority
- [ ] Click item to view full details (opens source record in side panel or new tab)
- [ ] Filter by: domain, priority, age range, requester, amount range
- [ ] Sort by: date submitted, priority, amount, requester name
- [ ] Search by: title, requester name, amount
- [ ] Badge count in menu showing total pending items

### FR-3: Approve/Reject Actions

**Acceptance Criteria:**
- [ ] Single-item approve with optional comment
- [ ] Single-item reject with required comment (reason for rejection)
- [ ] Approval/rejection delegates to domain connector's execute method
- [ ] Requester notified immediately on approve/reject
- [ ] Approver sees confirmation with item details before executing

### FR-4: Batch Operations

**Acceptance Criteria:**
- [ ] Multi-select checkbox on list view
- [ ] "Approve Selected" and "Reject Selected" action buttons
- [ ] Batch operations require a single comment applied to all items
- [ ] Batch operations restricted to same domain (cannot mix)
- [ ] Progress indicator for batch operations (processing X of Y)
- [ ] Summary of results after batch completes (N approved, M failed)
- [ ] Failed items in batch do not block successful items

### FR-5: Delegation

Out-of-office approval forwarding to a designated delegate.

**Data Model: `ipai.approval.delegation`**

| Field | Type | Description |
|-------|------|-------------|
| delegator_id | Many2one(res.users) | User delegating approval authority |
| delegate_id | Many2one(res.users) | User receiving delegation |
| date_start | Date | Delegation start date |
| date_end | Date | Delegation end date |
| domain_ids | Many2many | Domains to delegate (empty = all) |
| active | Boolean | Whether delegation is active |

**Acceptance Criteria:**
- [ ] User can set a delegate with start/end dates
- [ ] Delegation can be scoped to specific domains or all domains
- [ ] While delegation is active, new approvals auto-forward to delegate
- [ ] Delegate sees "on behalf of [delegator]" indicator
- [ ] Delegator can revoke delegation early
- [ ] Multiple delegations allowed (different domains to different people)
- [ ] Delegation audit trail: who delegated to whom, when, which domains

### FR-6: Escalation Engine

Auto-escalate approvals that exceed configurable time thresholds.

**Data Model: `ipai.approval.escalation_rule`**

| Field | Type | Description |
|-------|------|-------------|
| domain | Char | Domain this rule applies to (or 'all') |
| threshold_hours | Integer | Hours before escalation triggers |
| escalate_to | Selection | manager / director / specific_user |
| escalate_user_id | Many2one(res.users) | Specific user (if escalate_to = specific_user) |
| notify_original | Boolean | Whether to notify original approver on escalation |
| active | Boolean | Whether rule is active |

**Default Escalation Rules:**

| Domain | Threshold | Escalate To |
|--------|-----------|-------------|
| expense | 48 hours | Director |
| invoice | 72 hours | Finance Director |
| travel_request | 24 hours | Director |
| cash_advance | 24 hours | Director |
| close_task | 24 hours | Finance Director |
| all (fallback) | 72 hours | Manager's manager |

**Acceptance Criteria:**
- [ ] Cron job checks for overdue approvals (runs every 4 hours)
- [ ] Escalated items marked with escalation indicator in inbox
- [ ] Original approver notified of escalation
- [ ] Escalation target notified with urgency indicator
- [ ] Multiple escalation levels: Level 1 (reminder), Level 2 (reassign)
- [ ] Escalation history tracked in audit log

### FR-7: Notification System

Multi-channel notifications for approval events.

**Events and Channels:**

| Event | Slack | Email | In-App |
|-------|-------|-------|--------|
| New approval request | Yes | Yes | Yes |
| Reminder (approaching threshold) | Yes | No | Yes |
| Escalation | Yes | Yes | Yes |
| Delegation activated | Yes | Yes | Yes |
| Item approved | No | Yes | Yes |
| Item rejected | Yes | Yes | Yes |

**Acceptance Criteria:**
- [ ] Slack notifications via `ipai_slack_connector` with action buttons
- [ ] Email notifications via `mail.template` with one-click approve link
- [ ] In-app notifications via Odoo `mail.activity`
- [ ] User can configure notification preferences per channel
- [ ] Notification deduplication (no double-notifications)

### FR-8: Mobile-Responsive Interface

**Acceptance Criteria:**
- [ ] Inbox list view functional on mobile web browsers
- [ ] Swipe gestures: swipe right to approve, swipe left to reject (stretch goal)
- [ ] Approve/reject confirmation dialog works on mobile
- [ ] Delegation management accessible on mobile
- [ ] Touch-friendly batch select

### FR-9: Analytics and Reporting

**Reports:**

| Report | Audience | Description |
|--------|----------|-------------|
| Approval Turnaround | Admin | Average time from submission to decision, by domain |
| Bottleneck Analysis | Admin | Users with highest pending queue, longest turnaround |
| Escalation Report | Finance Director | Escalation frequency by domain and approver |
| Delegation Usage | Admin | Delegation coverage, most common delegates |
| Volume by Domain | Admin | Approval volume trends over time |

**Acceptance Criteria:**
- [ ] Dashboard view with key metrics: pending count, avg turnaround, escalation rate
- [ ] Drill-down from dashboard to individual items
- [ ] Export to CSV for all reports

## Non-Functional Requirements

- **Load time**: Inbox loads in < 2 seconds with 500+ pending items
- **Notification latency**: < 60 seconds from event to Slack notification
- **Concurrency**: Handle simultaneous approve by delegate and original approver (first wins)
- **Accessibility**: WCAG 2.1 AA compliance for inbox views

## Integration Points

| Domain Module | Approval Types Registered | Cross-Reference |
|---------------|---------------------------|-----------------|
| `ipai_finance_tne_control` | Travel requests, cash advances, expense reports | `spec/odoo-tne-control/` |
| `ipai_close_orchestration` | Close cycle tasks (review, approval gates) | `spec/close-orchestration/` |
| `ipai_finance_bir_compliance` | BIR filing approvals | `spec/bir-tax-compliance/` |
| `ipai_finance_ap_control` | Vendor invoice approvals | `spec/odoo-ap-invoice-control/` (planned) |
| `hr_expense` (CE) | Basic expense approvals (pre-TNE) | Odoo CE native |
| `account` (CE) | Journal entry approvals | Odoo CE native |

## Success Metrics

| Metric | Target |
|--------|--------|
| Approval turnaround (P50) | < 24 hours |
| Approval turnaround (P95) | < 72 hours |
| Approver inbox adoption | > 90% |
| Escalation rate | < 10% |
| Batch approval usage | > 40% |
| Mobile approval rate | > 20% |
