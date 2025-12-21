# ipai_month_end Module Constitution

## Purpose

SAP Advanced Financial Closing (AFC) replacement for Odoo 18 CE + OCA.
Target: 98% feature parity at zero licensing cost.

## Non-Negotiables

### 1. Template-Driven
- All closing tasks defined via reusable templates
- Templates grouped by phase (I, II, III, IV)
- Task dependencies enforced
- Holiday-aware scheduling (PH calendar)

### 2. RACI Workflow
- Every task has: Preparer, Reviewer, Approver
- No self-approval permitted
- Audit trail for all state changes
- Timestamps for SLA tracking

### 3. Workday Calculation
- Exclude weekends (Sat/Sun)
- Exclude Philippine holidays
- Offset days calculated from month-end close date
- Negative offsets = days before close

### 4. Notification System
- Overdue task alerts (daily cron)
- Assignment notifications
- Escalation triggers
- Integration with mail.thread

### 5. BIR Compliance (Philippines)
- Built-in Philippine tax rules
- BIR form generation support
- Audit-ready reports

## Phase Structure

| Phase | Name | Focus |
|-------|------|-------|
| I | Initial & Compliance | Tax, regulatory, opening |
| II | Accruals & Amortization | Expense recognition |
| III | WIP | Work-in-progress adjustments |
| IV | Final Adjustments & Close | Closing entries, reconciliation |

## Source of Truth

| Domain | Source | Authority |
|--------|--------|-----------|
| Task Templates | ipai.month.end.task.template | Finance Director |
| Holiday Calendar | ipai.ph.holiday | HR Ops |
| Closing Schedule | ipai.month.end.closing | Finance Director |
| Task Status | ipai.month.end.task | Task Owner |

## Quality Gates

1. All Phase I tasks complete before Phase II starts
2. All tasks reviewed before approval
3. Zero overdue tasks at month-end
4. Reconciliation differences < threshold
5. Trial balance in balance
