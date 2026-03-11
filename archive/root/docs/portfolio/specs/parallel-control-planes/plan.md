# Implementation Plan — Parallel Control Planes

## Phase 1: Module Structure ✅

- [x] Create `addons/ipai_ppm_a1/` module skeleton
- [x] Create `addons/ipai_close_orchestration/` module skeleton
- [x] Define manifest files with dependencies
- [x] Set up security groups and record rules

## Phase 2: A1 Control Center Models ✅

- [x] `a1.role` - Role configuration with resolver
- [x] `a1.workstream` - Organizational units
- [x] `a1.template` - Task templates with steps
- [x] `a1.template.step` - Step definitions
- [x] `a1.template.checklist` - Checklist templates
- [x] `a1.task` - Task instances
- [x] `a1.task.checklist` - Checklist items
- [x] `a1.tasklist` - Period runs
- [x] `a1.check` - STC scenarios
- [x] `a1.export.run` - Seed export/import

## Phase 3: Close Orchestration Models ✅

- [x] `close.task.category` - Task categories
- [x] `close.task.template` - Task templates
- [x] `close.cycle` - Close cycles
- [x] `close.task` - Close tasks
- [x] `close.task.checklist` - Task checklists
- [x] `close.exception` - Exception tracking
- [x] `close.approval.gate` - Approval gates
- [x] `close.approval.gate.template` - Gate templates

## Phase 4: Views and Menus ✅

- [x] A1 views (workstream, template, task, tasklist, check)
- [x] Close views (cycle, task, exception, gate)
- [x] Menu structure for both modules
- [x] Kanban views for tasks

## Phase 5: Automation ✅

- [x] Task generation from templates
- [x] Workflow state transitions
- [x] Cron: Due date reminders
- [x] Cron: Exception auto-escalation
- [x] Cron: Gate status checks
- [x] Webhook triggers for state changes

## Phase 6: Testing ✅

- [x] Smoke test script
- [x] Python syntax validation
- [x] XML validity checks

## Phase 7: Documentation ✅

- [x] Spec bundle (constitution, prd, plan, tasks)
- [x] Module README files (pending)

## Future Enhancements

- [ ] Seed YAML parser with schema validation
- [ ] n8n workflow templates
- [ ] Superset dashboard integration
- [ ] PDF export for close cycles
- [ ] API endpoints for external systems
