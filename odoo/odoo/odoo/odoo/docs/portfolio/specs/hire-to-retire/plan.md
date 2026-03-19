# Hire-to-Retire Implementation Plan

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Odoo 18 CE + OCA                          │
├─────────────────────────────────────────────────────────────┤
│  HR Module (Co-Owner)          │  Payroll Module (FSS)      │
│  ├── Employee Master           │  ├── Payroll Runs          │
│  ├── Recruitment               │  ├── Salary Computation    │
│  ├── Time Off (Leave)          │  ├── Final Pay Calc        │
│  ├── Clearance Workflow        │  └── Tax/Deductions        │
│  └── COE Generation            │                            │
├─────────────────────────────────────────────────────────────┤
│  Supabase (External Sync)      │  Control Room (Dashboard)  │
│  ├── Real-time status          │  ├── SLA monitoring        │
│  ├── Approval notifications    │  ├── Overdue alerts        │
│  └── Mobile access             │  └── Process analytics     │
└─────────────────────────────────────────────────────────────┘
```

## Milestones

### Phase 1: Foundation (Week 1-2)
- [ ] Configure Odoo HR module
- [ ] Set up employee master data fields
- [ ] Configure leave types (VL, SL, etc.)
- [ ] Create PH holiday calendar
- [ ] Set up payroll structure

### Phase 2: Clearance Workflow (Week 3)
- [ ] Create clearance checklist model
- [ ] Implement parallel clearance routing
- [ ] Add clearance signature capture
- [ ] Build clearance completion trigger

### Phase 3: Final Pay (Week 4)
- [ ] Create final pay calculation wizard
- [ ] Implement leave credit conversion
- [ ] Add deduction handling
- [ ] Build approval workflow
- [ ] Set up payment execution

### Phase 4: COE & Compliance (Week 5)
- [ ] Create COE template
- [ ] Implement 3-day SLA tracking
- [ ] Add DOLE compliance reports
- [ ] Set up SLA breach alerts

### Phase 5: Integration (Week 6)
- [ ] Sync to Supabase for mobile access
- [ ] Build Control Room dashboard
- [ ] Configure n8n workflows for notifications
- [ ] End-to-end testing

## Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| HR Module | Odoo 18 CE + OCA | Full employee lifecycle |
| Leave Management | OCA hr_holidays extensions | Conversion support |
| Payroll | Odoo Payroll + localization | PH tax compliance |
| Workflow | Odoo Approvals + mail.activity | Built-in audit trail |
| SLA Tracking | Custom + Superset | Real-time dashboards |

## Risks

| Risk | Mitigation |
|------|------------|
| DOLE compliance gaps | Legal review of all calculations |
| Late clearance collection | Automated reminders + escalation |
| Incorrect leave balance | HR verification gate |
| Tax computation errors | Finance review before release |
