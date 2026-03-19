# IPAI TBWA Finance - Tasks

## Completed

- [x] Create unified module structure
- [x] Implement `ph.holiday` model with workday calculation
- [x] Implement `finance.task.template` model
- [x] Implement `closing.period` model with task generation
- [x] Implement `finance.task` model with RACI workflow
- [x] Implement `bir.return` model
- [x] Implement `compliance.check` model
- [x] Add TIN field to `res.partner`
- [x] Create all view XML files (8 files)
- [x] Create security access rules
- [x] Load Philippine holidays 2025-2026 (38 holidays)
- [x] Create month-end templates (20 tasks across 4 phases)
- [x] Create BIR form templates (7 forms: 2550M, 1601C, 1601E, 2551M, 2550Q, 1604CF, 1604E, 1702)
- [x] Create overdue notification cron
- [x] Create consolidated spec bundle

## In Progress

- [ ] Commit and push unified module

## Pending

### Phase 3: Automation
- [ ] Implement email templates for notifications
- [ ] Add chatter tracking to finance.task
- [ ] Implement automated task generation action on period open
- [ ] Add smart buttons to period (task count, BIR count)

### Phase 4: Integration
- [ ] Create journal entry templates for common tasks
- [ ] Link to hr_payroll for payroll tasks
- [ ] Link to account_asset for depreciation
- [ ] Create Notion sync workflow in n8n

### Phase 5: Reporting
- [ ] Period close summary report
- [ ] BIR filing status report
- [ ] Task aging report
- [ ] Team workload report

### Phase 6: Testing
- [ ] Unit tests for holiday calculation
- [ ] Unit tests for deadline computation
- [ ] Integration tests for period lifecycle
- [ ] User acceptance testing with RIM/BOM team

## Dependencies

| Task | Depends On |
|------|------------|
| Journal entry templates | `account` module config |
| Payroll integration | `hr_payroll_account` installed |
| Depreciation automation | `account_asset_management` installed |
| Notion sync | n8n workflow deployment |

## Team Assignments

| Task Category | Primary | Backup |
|---------------|---------|--------|
| Module development | Dev Team | - |
| Template configuration | BOM | CKVC |
| User acceptance testing | RIM | BOM |
| Production deployment | IT Ops | Dev Team |
