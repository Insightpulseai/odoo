# IPAI TBWA Finance - Implementation Plan

## Architecture Decisions

### AD-1: Unified Module
**Decision**: Combine month-end and BIR compliance into single `ipai_tbwa_finance` module.

**Rationale**:
- Same team (RIM prep, BOM review)
- Same RACI workflow pattern
- Shared Philippine holiday calendar
- BIR deadlines ARE part of month-end
- One install, one dependency set

### AD-2: Task Type Discrimination
**Decision**: Use `task_type` field on unified `finance.task` model.

**Rationale**:
- Simpler than inheritance
- Easy filtering for views
- Shared workflow logic
- Consistent reporting

### AD-3: Template-Based Generation
**Decision**: Tasks generated from templates, not hard-coded.

**Rationale**:
- Easy to add/modify tasks
- Frequency filtering (monthly/quarterly/annual)
- OCA module reference for future automation
- Customer-configurable

## Implementation Phases

### Phase 1: Core Models ✓
- [x] `ph.holiday` - Holiday calendar with workday calculation
- [x] `finance.task.template` - Task templates
- [x] `closing.period` - Period management
- [x] `finance.task` - Task instances with RACI workflow
- [x] `compliance.check` - Pre-close validation
- [x] `bir.return` - BIR filing documents

### Phase 2: Views & Data ✓
- [x] Kanban/tree/form views for all models
- [x] Dashboard action
- [x] Holiday data (2025-2026)
- [x] Month-end templates (20 tasks)
- [x] BIR form templates (7 forms)
- [x] Security access rules

### Phase 3: Automation (Pending)
- [ ] Cron for overdue notifications
- [ ] Automated task generation on period open
- [ ] Email templates for notifications
- [ ] Chatter integration for workflow

### Phase 4: Integration (Future)
- [ ] Connect to `account` for journal entry creation
- [ ] Connect to `hr_payroll` for payroll tasks
- [ ] Connect to OCA modules (asset, cutoff, etc.)
- [ ] Notion sync via n8n workflow

## File Structure

```
addons/ipai_tbwa_finance/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── ph_holiday.py           # Holiday calendar
│   ├── res_partner.py          # TIN field extension
│   ├── finance_task_template.py # Task templates
│   ├── closing_period.py       # Period management
│   ├── finance_task.py         # Task instances
│   ├── bir_return.py           # BIR filing docs
│   └── compliance_check.py     # Pre-close checks
├── views/
│   ├── ph_holiday_views.xml
│   ├── finance_task_template_views.xml
│   ├── closing_period_views.xml
│   ├── finance_task_views.xml
│   ├── bir_return_views.xml
│   ├── compliance_check_views.xml
│   ├── dashboard_views.xml
│   └── menuitems.xml
├── security/
│   └── ir.model.access.csv
└── data/
    ├── ph_holidays.xml          # 2025-2026 holidays
    ├── month_end_templates.xml  # 20 month-end tasks
    ├── bir_form_types.xml       # BIR form templates
    ├── compliance_checks.xml    # Sequences
    └── ir_cron.xml              # Scheduled actions
```

## Testing Strategy

### Unit Tests
- Holiday workday calculation
- Task deadline computation
- Period state transitions
- RACI workflow enforcement

### Integration Tests
- Full period lifecycle (open → generate → close)
- BIR return computation from invoices
- Compliance check blocking

### User Acceptance
- RIM team task workflow
- BOM review workflow
- FD period close workflow

## Dependencies

| Module | Purpose | Source |
|--------|---------|--------|
| base | Core models | Odoo |
| mail | Chatter, notifications | Odoo |
| account | Journal entries | Odoo |
| hr_payroll_account | Payroll integration | OCA |
| account_asset_management | Depreciation | OCA |
| account_cutoff_accrual_order_base | Accruals | OCA |

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Holiday calendar incomplete | Wrong deadlines | Pre-load 2 years, allow CRUD |
| OCA modules not installed | Manual tasks | Graceful degradation, info field |
| Period opened without tasks | Missing work | Auto-generate on open |
| Concurrent period edits | Data conflicts | Period locking |
