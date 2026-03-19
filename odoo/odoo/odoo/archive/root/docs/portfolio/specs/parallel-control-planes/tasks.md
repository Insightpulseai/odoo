# Tasks — Parallel Control Planes

## Completed

- [x] Create ipai_ppm_a1 module structure
- [x] Create ipai_close_orchestration module structure
- [x] Implement A1 role configuration model
- [x] Implement A1 workstream model
- [x] Implement A1 template model with steps
- [x] Implement A1 tasklist with task generation
- [x] Implement A1 check/STC model
- [x] Implement A1 seed export/import
- [x] Implement close category model
- [x] Implement close template model
- [x] Implement close cycle model
- [x] Implement close task with workflow
- [x] Implement close exception with escalation
- [x] Implement close approval gate
- [x] Add security groups and record rules
- [x] Create views for all models
- [x] Create menu structure
- [x] Add cron jobs for automation
- [x] Add webhook event triggers
- [x] Create smoke test script
- [x] Validate Python and XML syntax

## Pending

- [ ] Add module README.rst files
- [ ] Add demo data for testing
- [ ] Add i18n translation placeholders
- [ ] Create seed validation script
- [ ] Add API documentation
- [ ] Integration test with actual database

## Acceptance Criteria

1. **Module Installation**
   - Both modules install without errors
   - Dependencies resolved correctly
   - Demo data loads (if provided)

2. **Workflow Functionality**
   - Tasks can transition through all states
   - Checklist items block progression when incomplete
   - Exceptions prevent task submission
   - Gates block cycle closure

3. **Automation**
   - Cron jobs execute without errors
   - Webhooks fire on state changes
   - Role resolver maps codes to users

4. **Multi-Company**
   - Records scoped to company
   - Record rules enforced
   - Cross-company access blocked
