# ipai_month_end Implementation Tasks

## Phase 1: Core Models

### Task Template Model
- [ ] Create ipai.month.end.task.template model
- [ ] Add phase selection field (I, II, III, IV)
- [ ] Add RACI user fields
- [ ] Add prep_day_offset field
- [ ] Add depends_on_ids M2M field
- [ ] Add odoo_model and oca_module fields

### Closing Model
- [ ] Create ipai.month.end.closing model
- [ ] Add period_date field
- [ ] Add last_workday computed field
- [ ] Add state field (draft, in_progress, closed)
- [ ] Add task_ids O2M relation
- [ ] Add progress computed field

### Task Model
- [ ] Create ipai.month.end.task model
- [ ] Inherit mail.thread, mail.activity.mixin
- [ ] Add closing_id M2O relation
- [ ] Add template_id M2O relation
- [ ] Add RACI user fields
- [ ] Add due date fields
- [ ] Add state computed field

### Holiday Model
- [ ] Create ipai.ph.holiday model
- [ ] Add date and name fields
- [ ] Add holiday type field
- [ ] Import 2024-2025 holidays

## Phase 2: Workflow Engine

### Workday Calculation
- [ ] Create _get_workday_offset() method
- [ ] Create _is_workday() method
- [ ] Test with various offsets
- [ ] Handle edge cases (year boundary)

### Task Generation
- [ ] Create generation wizard
- [ ] Calculate due dates from templates
- [ ] Assign RACI from templates
- [ ] Validate dependencies

### State Machine
- [ ] Implement prep_done action
- [ ] Implement review_done action
- [ ] Implement approve_done action
- [ ] Add state computed field
- [ ] Add timestamp fields

## Phase 3: Views & UX

### Tree Views
- [ ] Create template list view
- [ ] Create closing list view
- [ ] Create task list view with grouping
- [ ] Add filters and group_by

### Form Views
- [ ] Create template form view
- [ ] Create closing form view
- [ ] Create task form view with buttons
- [ ] Add chatter widget

### Kanban View
- [ ] Create task Kanban view
- [ ] Group by state
- [ ] Add drag-and-drop (if applicable)

### Dashboard
- [ ] Create closing dashboard action
- [ ] Add progress bar widget
- [ ] Add overdue count widget
- [ ] Add phase completion chart

## Phase 4: Notifications

### Mail Integration
- [ ] Enable mail.thread on task model
- [ ] Track state changes
- [ ] Enable follower notifications

### Overdue Alerts
- [ ] Create _cron_send_overdue_notifications()
- [ ] Create ir.cron record
- [ ] Test daily execution
- [ ] Add email template

### Activity Scheduling
- [ ] Schedule activity on assignment
- [ ] Mark done on task completion
- [ ] Create escalation activity

## Phase 5: Data & Testing

### Template Library
- [ ] Create Phase I templates (10 tasks)
- [ ] Create Phase II templates (8 tasks)
- [ ] Create Phase III templates (6 tasks)
- [ ] Create Phase IV templates (12 tasks)

### Holiday Data
- [ ] Import 2024 PH holidays
- [ ] Import 2025 PH holidays
- [ ] Verify with official DOLE calendar

### Testing
- [ ] Unit tests for workday calculation
- [ ] Integration tests for workflow
- [ ] End-to-end test for full cycle
- [ ] Performance test with 100+ tasks

## Phase 6: Documentation

### User Guide
- [ ] Template management
- [ ] Closing period creation
- [ ] Task execution workflow
- [ ] Dashboard usage

### Admin Guide
- [ ] Installation
- [ ] Configuration
- [ ] Cron job setup
- [ ] Troubleshooting

### Migration Guide
- [ ] Export SAP AFC templates
- [ ] Map to ipai templates
- [ ] Parallel run procedure
- [ ] Cutover checklist
