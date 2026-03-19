# Close Orchestration Module - Task Checklist

## Module Implementation

- [x] Create module structure (`odoo/addons/ipai_close_orchestration/`)
- [x] Define `__manifest__.py` with dependencies
- [x] Create `__init__.py` imports

## Models

- [x] `close.task.category` - 21 task categories from TBWA process
- [x] `close.cycle` - Close cycle with period management
- [x] `close.task` - Task instances with 3-stage workflow
- [x] `close.task.template` - Reusable task definitions
- [x] `close.task.checklist` - Evidence tracking items
- [x] `close.exception` - Exception tracking with escalation
- [x] `close.approval.gate` - Approval checkpoints

## Views

- [x] `close_cycle_views.xml` - Form, tree, kanban, calendar
- [x] `close_task_views.xml` - Task views with workflow buttons
- [x] `close_exception_views.xml` - Exception management views
- [x] `menu.xml` - Navigation structure

## Security

- [x] `security/security.xml` - User groups and rules
- [x] `security/ir.model.access.csv` - Model access rights

## Data

- [x] `supabase/data/close_task_categories.xml` - 21 category records
- [x] `supabase/data/close_task_templates.xml` - 23 template records
- [x] `supabase/data/ir_cron.xml` - 4 scheduled actions

## Features

- [x] 3-stage workflow (Prep → Review → Approve)
- [x] Department routing (RIM, JPAL, BOM, CKVC, FD)
- [x] Checklist with evidence types
- [x] Exception tracking with auto-escalation
- [x] Approval gates with blocking
- [x] Due date reminders via cron
- [x] Overdue task detection
- [x] Cycle progress tracking

## Documentation

- [x] `docs/spec/close-orchestration/constitution.md`
- [x] `docs/spec/close-orchestration/prd.md`
- [x] `docs/spec/close-orchestration/plan.md`
- [x] `docs/spec/close-orchestration/tasks.md`

## Testing

- [ ] Unit tests for workflow transitions
- [ ] Test task generation from templates
- [ ] Test exception escalation
- [ ] Test gate blocking logic

## Integration

- [ ] Link to `closing.period` from ipai_tbwa_finance
- [ ] GL entry creation from tasks
- [ ] n8n webhook notifications
