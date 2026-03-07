# Approval Inbox — Implementation Plan

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                   ipai_platform_approval_inbox                       │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                 Approval Inbox UI                            │   │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │   │
│   │  │ List     │  │ Kanban   │  │ Calendar │  │ Dashboard│   │   │
│   │  │ View     │  │ View     │  │ View     │  │ View     │   │   │
│   │  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │   │
│   └─────────────────────────────────────────────────────────────┘   │
│         │                                                            │
│         ▼                                                            │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │              Connector Registry                              │   │
│   │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │   │
│   │  │ Expense │ │ Invoice │ │ Close   │ │ Travel  │ ...       │   │
│   │  │Connector│ │Connector│ │Connector│ │Connector│          │   │
│   │  └─────────┘ └─────────┘ └─────────┘ └─────────┘          │   │
│   └─────────────────────────────────────────────────────────────┘   │
│         │                   │                   │                    │
│         ▼                   ▼                   ▼                    │
│   ┌──────────┐      ┌──────────┐      ┌──────────────────┐         │
│   │Delegation│      │Escalation│      │ Notification     │         │
│   │ Engine   │      │ Engine   │      │ Dispatcher       │         │
│   └──────────┘      └──────────┘      │ ┌─────┐┌──────┐ │         │
│                                        │ │Slack││Email │ │         │
│                                        │ └─────┘└──────┘ │         │
│                                        └──────────────────┘         │
└──────────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
  │ hr_expense   │   │ account.move │   │ ipai_close_  │
  │ (CE native)  │   │ (CE native)  │   │ orchestration│
  └──────────────┘   └──────────────┘   └──────────────┘
```

## Module Structure

```
addons/ipai/ipai_platform_approval_inbox/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── approval_connector.py       # ipai.approval.connector (abstract mixin)
│   ├── approval_item.py            # ipai.approval.item (transient aggregator)
│   ├── approval_log.py             # ipai.approval.log (audit trail)
│   ├── delegation.py               # ipai.approval.delegation
│   ├── escalation_rule.py          # ipai.approval.escalation_rule
│   └── notification_preference.py  # ipai.approval.notification_pref
├── views/
│   ├── approval_inbox_views.xml    # List, Kanban, Calendar views
│   ├── approval_dashboard.xml      # Analytics dashboard
│   ├── delegation_views.xml        # Delegation management
│   ├── escalation_rule_views.xml   # Escalation configuration
│   ├── notification_pref_views.xml # User notification preferences
│   └── menu.xml                    # Menu items
├── security/
│   ├── ir.model.access.csv
│   └── approval_security.xml
├── data/
│   ├── escalation_rules_data.xml   # Default escalation thresholds
│   ├── mail_template_data.xml      # Email templates
│   ├── cron_data.xml               # Escalation check cron
│   └── slack_template_data.xml     # Slack message templates
├── wizards/
│   ├── __init__.py
│   ├── batch_approve.py            # Batch approve wizard
│   ├── batch_reject.py             # Batch reject wizard
│   ├── set_delegation.py           # Set delegation wizard
│   └── wizard_views.xml
├── reports/
│   ├── approval_turnaround.xml
│   ├── bottleneck_analysis.xml
│   └── escalation_report.xml
├── static/
│   ├── description/
│   │   └── icon.png
│   └── src/
│       ├── js/
│       │   └── approval_inbox.js   # Client-side batch select, swipe
│       └── xml/
│           └── approval_templates.xml
└── tests/
    ├── __init__.py
    ├── test_connector_registry.py
    ├── test_delegation.py
    ├── test_escalation.py
    ├── test_batch_operations.py
    └── test_notification.py
```

## Milestones

### Phase 1: Generic Approval Model + Inbox UI (Week 1-2)

**Goal**: Unified inbox view aggregating approvals from all registered domain connectors.

- [ ] Create `ipai.approval.connector` abstract model (mixin interface)
- [ ] Create `ipai.approval.item` transient model (aggregated view)
- [ ] Create `ipai.approval.log` model (immutable audit trail)
- [ ] Build inbox list view with domain badges, priority, age indicators
- [ ] Build inbox Kanban view grouped by domain
- [ ] Implement single-item approve/reject with comment
- [ ] Implement filter/sort by domain, priority, age, requester, amount
- [ ] Add "My Approvals" menu item with badge count
- [ ] Security groups: approval_user, approval_admin
- [ ] Create default connector for `hr_expense` (CE native) as reference implementation

**Verification:**
```bash
docker compose exec -T web odoo -d odoo -i ipai_platform_approval_inbox --stop-after-init
# Verify connector registry
docker compose exec -T web odoo shell -d odoo -c "
connectors = env['ipai.approval.connector']._get_registered_connectors()
print(f'{len(connectors)} connectors registered')
"
```

### Phase 2: Domain Connectors (Week 3-4)

**Goal**: Connect expense, invoice, and close orchestration domains to the inbox.

- [ ] Implement expense connector (`ipai_finance_tne_control` integration)
  - Travel request approvals
  - Cash advance approvals
  - Expense report approvals
- [ ] Implement close connector (`ipai_close_orchestration` integration)
  - Review stage approvals
  - Approval gate approvals
- [ ] Implement invoice connector (accounts payable integration)
  - Vendor invoice approvals
- [ ] Implement BIR filing connector (`ipai_finance_bir_compliance` integration)
  - BIR return filing approvals
- [ ] Each connector provides: domain name, icon, color, summary fields
- [ ] Test cross-domain inbox population

**Verification:**
```bash
docker compose exec -T web odoo -d odoo -u ipai_platform_approval_inbox --stop-after-init
# Verify all connectors
docker compose exec -T web odoo shell -d odoo -c "
for c in env['ipai.approval.connector']._get_registered_connectors():
    print(f'  {c.get_approval_domain()}: registered')
"
```

### Phase 3: Delegation + Escalation Engine (Week 5-6)

**Goal**: Approvers can delegate authority; stale items auto-escalate.

- [ ] Create `ipai.approval.delegation` model
- [ ] Build delegation wizard (set delegate, date range, domain scope)
- [ ] Implement auto-forwarding of new approvals to active delegate
- [ ] "On behalf of" indicator for delegated approvals
- [ ] Delegation revocation
- [ ] Create `ipai.approval.escalation_rule` model
- [ ] Load default escalation thresholds (seed data)
- [ ] Implement escalation cron (runs every 4 hours)
- [ ] Level 1 escalation: reminder to original approver
- [ ] Level 2 escalation: reassign to escalation target
- [ ] Escalation notifications (Slack + email)
- [ ] Build batch approve/reject wizards
- [ ] Same-domain constraint for batch operations
- [ ] Batch progress indicator and result summary

**Verification:**
```bash
# Test escalation cron
docker compose exec -T web odoo shell -d odoo -c "
env['ipai.approval.escalation_rule'].sudo()._cron_check_escalations()
print('Escalation cron executed')
"
```

### Phase 4: Mobile + Slack Integration (Week 7-8)

**Goal**: Full mobile-responsive inbox; Slack actionable notifications.

- [ ] Mobile-responsive inbox CSS/layout
- [ ] Touch-friendly batch select on mobile
- [ ] Slack notification integration via `ipai_slack_connector`
- [ ] Slack actionable message buttons (Approve / Reject / View)
- [ ] Email notification templates with one-click approve link
- [ ] User notification preference model (per-channel opt-in/out)
- [ ] Build analytics dashboard: pending count, avg turnaround, escalation rate
- [ ] Approval turnaround report
- [ ] Bottleneck analysis report (users with longest queues)
- [ ] Escalation frequency report
- [ ] CSV export for all reports

**Verification:**
```bash
# Full test suite
docker compose exec -T web odoo -d odoo --test-enable --test-tags ipai_platform_approval_inbox --stop-after-init
# Health check
curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/health
```

## Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Connector pattern | Abstract model mixin | Domain modules register without inbox knowing about them |
| Inbox data model | Transient (on-the-fly aggregation) | No data duplication, always reflects real-time state |
| Audit log | Persistent model (`ipai.approval.log`) | Immutable record for compliance |
| Escalation check | Cron (every 4 hours) | Balanced between timeliness and performance |
| Batch operations | Server-side wizard | Handles large batches without browser timeout |
| Mobile UI | Responsive CSS (no separate app) | Reuse existing Odoo web client |
| Notifications | Multi-channel dispatcher | User controls which channels they receive |

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Connector aggregation slow with many domains | Inbox load time > 2s | Pagination, domain-specific caching, lazy loading |
| Delegation conflicts (original + delegate both approve) | Double-approval | Optimistic locking, first-wins pattern |
| Escalation noise | Alert fatigue | Configurable thresholds, quiet hours |
| Domain connector bugs | Items missing from inbox | Connector health check, fallback to direct module view |
| Batch operation failure mid-batch | Partial approval | Transactional per-item, report failures at end |

## Dependencies

| Dependency | Status | Impact if Delayed |
|------------|--------|-------------------|
| `ipai_platform_approvals` | Existing | Blocks all phases |
| `ipai_finance_tne_control` | See `spec/odoo-tne-control/` | Phase 2 expense connector deferred |
| `ipai_close_orchestration` | Existing | Phase 2 close connector can proceed |
| `ipai_slack_connector` | Existing | Phase 4 Slack notifications deferred |
| `ipai_finance_bir_compliance` | Existing | Phase 2 BIR connector can proceed |
