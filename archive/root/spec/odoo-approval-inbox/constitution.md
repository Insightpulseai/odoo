# Approval Inbox — Constitution

## Purpose

Provide a single, unified approval queue for all pending approvals across every IPAI domain. Eliminates the pattern of separate approval UIs per module and gives approvers one place to review, approve, reject, delegate, and escalate.

## Non-Negotiables

### 1. Module Identity

- **Module name**: `ipai_platform_approval_inbox`
- **Extends**: `ipai_platform_approvals` (base approval engine)
- **Depends**: `mail`, `hr`, `ipai_platform_approvals`
- **Naming**: All models use `ipai.approval.*` namespace

### 2. Domain-Agnostic

- **Rule**: The inbox MUST work for any approval domain — expense, invoice, close, tax, travel, procurement, or any future domain.
- **No hardcoded domains**: Domain registration is via a mixin/registry pattern, not conditional logic.
- **Connector pattern**: Each domain module registers its approval types with the inbox. The inbox never imports domain modules directly.

### 3. Single Unified Queue

- **Rule**: There MUST be exactly ONE approval UI for all domains.
- **No separate views**: Approvers do not navigate to different menus for expense vs invoice vs travel approvals.
- **Single entry point**: Menu item "My Approvals" shows everything pending for the current user.

### 4. Delegation and Escalation

- **Delegation**: Approvers MUST be able to delegate their approval authority to another user (e.g., out-of-office).
- **Escalation**: Approvals that remain pending beyond a configurable threshold MUST auto-escalate to the next level.
- **Chain**: Delegation and escalation follow the organizational hierarchy defined in `hr.employee`.

### 5. Batch Operations

- **Rule**: Approvers MUST be able to select multiple items and approve/reject them in a single action.
- **Comment**: Batch operations require a comment/reason that applies to all selected items.
- **Constraint**: Batch operations only allowed within the same domain (cannot mix expense and invoice approvals in one batch).

### 6. Audit Trail

- **Rule**: Every approval action (approve, reject, delegate, escalate, comment) MUST be logged.
- **Fields**: Who, when, action, comment, delegated-from (if applicable).
- **Immutable**: Audit records cannot be edited or deleted.

### 7. Notification Channels

- **Primary**: Slack (via `ipai_slack_connector`)
- **Fallback**: Email (via `mail.template`)
- **In-app**: Odoo activity/chatter notifications
- **Events**: New approval request, reminder, escalation, delegation, approved, rejected

## Boundaries

### In Scope

- Unified approval inbox UI (list, Kanban, calendar views)
- Domain connector registration pattern (mixin)
- Delegation management (set delegate, date range, auto-forward)
- Escalation engine (configurable thresholds per domain)
- Batch approve/reject with comments
- Filter/sort by domain, priority, age, requester, amount
- Mobile-responsive approval interface
- Notification dispatch (Slack, email, in-app)
- Approval analytics (turnaround time, bottlenecks, delegation usage)

### Out of Scope

- Domain-specific approval logic (each domain module owns its own state machine)
- Document rendering (the inbox shows summary + link to source document)
- Payment processing (downstream of approval)
- User management / org hierarchy (owned by `hr` module)

## Success Criteria

| Metric | Target |
|--------|--------|
| Approval turnaround time | < 24 hours (P50) |
| Approver adoption rate | > 90% using inbox (vs direct module) |
| Escalation rate | < 10% of all approvals |
| Delegation coverage | 100% of planned absences have delegates |
| Batch approval usage | > 40% of approvals done in batch |

## Cost Constraints

| Component | Monthly Cost |
|-----------|--------------|
| ipai_platform_approval_inbox | $0 |
| Slack notifications | $0 (existing workspace) |
| Email notifications | $0 (Mailgun existing plan) |
| **Total** | **$0** |
