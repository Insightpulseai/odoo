# Plan – InsightPulseAI Odoo 18 CE/OCA Implementation Handbook

**Product:** Documentation handbook
**Version:** 1.0.0
**Last Updated:** 2025-12-07

---

## Release Roadmap

### v0.1 – Finance-Only Handbook

**Goal:** Complete finance documentation for TE-Cheq go-live

**Scope:**
- Finance workspace pages (all 9 pages)
- Supabase schema documentation for `finance.*`, `expense.*`
- n8n workflow blueprints for expense approval
- Integration call-outs for TE-Cheq engine

**Dependencies:**
- [ ] `finance.*` Supabase schema finalized
- [ ] `ipai_expense` module deployed
- [ ] `wf_expense_*` n8n workflows active

**Milestones:**
| Milestone | Description | Target |
|-----------|-------------|--------|
| M0.1.1 | Finance Overview + COA pages | Week 1 |
| M0.1.2 | Invoicing + Vendor Bills pages | Week 2 |
| M0.1.3 | Expenses + TE-Cheq pages | Week 3 |
| M0.1.4 | Month-end + Reconciliation pages | Week 4 |
| M0.1.5 | Finance UAT checklist | Week 4 |

---

### v0.2 – Projects/Timesheets + Basic HR

**Goal:** Add PPM and HR documentation for Phase 2 go-live

**Scope:**
- Projects & PPM workspace (all 8 pages)
- HR & People Ops workspace (all 6 pages)
- Supabase schema documentation for `projects.*`, `rates.*`, `hr.*`
- n8n workflow blueprints for timesheet approval

**Dependencies:**
- [ ] `ipai_ppm_portfolio` module deployed
- [ ] `projects.*` Supabase schema finalized
- [ ] `wf_timesheet_*` n8n workflows active
- [ ] OCA `hr_timesheet_sheet` configured

**Milestones:**
| Milestone | Description | Target |
|-----------|-------------|--------|
| M0.2.1 | PPM Overview + Hierarchy pages | Week 5 |
| M0.2.2 | WBS + Timesheets pages | Week 6 |
| M0.2.3 | Budget + Rate Cards pages | Week 7 |
| M0.2.4 | HR Overview + Employees pages | Week 8 |
| M0.2.5 | Time Off + Attendance pages | Week 9 |
| M0.2.6 | PPM + HR UAT checklists | Week 9 |

---

### v0.3 – Retail & Scout Integration

**Goal:** Document Scout data pipeline and SariCoach

**Scope:**
- Retail & Scout workspace (all 6 pages)
- Medallion architecture documentation
- SariCoach AI coaching patterns
- Superset dashboard guides

**Dependencies:**
- [ ] Scout bronze/silver/gold schemas deployed
- [ ] `wf_scout_*` n8n workflows active
- [ ] SariCoach agent configured
- [ ] Superset dashboards created

**Milestones:**
| Milestone | Description | Target |
|-----------|-------------|--------|
| M0.3.1 | POS Configuration page | Week 10 |
| M0.3.2 | Scout Pipeline + Medallion pages | Week 11 |
| M0.3.3 | SariCoach AI documentation | Week 12 |
| M0.3.4 | Retail analytics dashboards | Week 12 |

---

### v1.0 – Full TBWA Finance Workspace Coverage

**Goal:** Complete handbook for production go-live

**Scope:**
- Equipment workspace (all 5 pages)
- Sales/CRM workspace (all 4 pages)
- AI Workbench documentation (all 5 pages)
- Integrations documentation (all 5 pages)
- DevOps documentation (all 7 pages)
- Developer Guide (all 5 pages)

**Dependencies:**
- [ ] All ipai_* modules deployed
- [ ] All Supabase schemas finalized
- [ ] All n8n workflows active
- [ ] All AI agents configured
- [ ] Production infrastructure stable

**Milestones:**
| Milestone | Description | Target |
|-----------|-------------|--------|
| M1.0.1 | Equipment workspace | Week 13 |
| M1.0.2 | Sales/CRM workspace | Week 14 |
| M1.0.3 | AI Workbench documentation | Week 15 |
| M1.0.4 | Integrations documentation | Week 16 |
| M1.0.5 | DevOps documentation | Week 17 |
| M1.0.6 | Developer Guide | Week 18 |
| M1.0.7 | Full handbook review | Week 19 |
| M1.0.8 | Production go-live | Week 20 |

---

## Dependency Graph

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DOCUMENTATION DEPENDENCIES                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  SUPABASE SCHEMAS                 N8N WORKFLOWS                         │
│  ┌─────────────────┐              ┌─────────────────┐                  │
│  │ finance.*       │──────────────│ wf_expense_*    │                  │
│  │ expense.*       │              │ wf_invoice_*    │                  │
│  └────────┬────────┘              └────────┬────────┘                  │
│           │                                │                            │
│           ▼                                ▼                            │
│  ┌─────────────────────────────────────────────────────┐               │
│  │              v0.1 FINANCE HANDBOOK                   │               │
│  └─────────────────────────────────────────────────────┘               │
│                                                                         │
│  ┌─────────────────┐              ┌─────────────────┐                  │
│  │ projects.*      │──────────────│ wf_timesheet_*  │                  │
│  │ rates.*         │              │ wf_project_*    │                  │
│  └────────┬────────┘              └────────┬────────┘                  │
│           │                                │                            │
│           ▼                                ▼                            │
│  ┌─────────────────────────────────────────────────────┐               │
│  │           v0.2 PPM + HR HANDBOOK                     │               │
│  └─────────────────────────────────────────────────────┘               │
│                                                                         │
│  ┌─────────────────┐              ┌─────────────────┐                  │
│  │ scout_*.*       │──────────────│ wf_scout_*      │                  │
│  │ saricoach.*     │              │ wf_saricoach_*  │                  │
│  └────────┬────────┘              └────────┬────────┘                  │
│           │                                │                            │
│           ▼                                ▼                            │
│  ┌─────────────────────────────────────────────────────┐               │
│  │           v0.3 RETAIL HANDBOOK                       │               │
│  └─────────────────────────────────────────────────────┘               │
│                                                                         │
│  ┌─────────────────┐              ┌─────────────────┐                  │
│  │ All schemas     │              │ All workflows   │                  │
│  │ complete        │              │ complete        │                  │
│  └────────┬────────┘              └────────┬────────┘                  │
│           │                                │                            │
│           ▼                                ▼                            │
│  ┌─────────────────────────────────────────────────────┐               │
│  │             v1.0 FULL HANDBOOK                       │               │
│  └─────────────────────────────────────────────────────┘               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Quality Gates Per Release

### v0.1 Quality Gate

- [ ] All 9 finance pages complete
- [ ] Schema references verified against `finance.*`, `expense.*`
- [ ] n8n workflow IDs match actual workflows
- [ ] Code examples tested on Odoo 18 CE
- [ ] Finance SME review completed
- [ ] UAT checklist validated

### v0.2 Quality Gate

- [ ] All 14 PPM + HR pages complete
- [ ] Schema references verified against `projects.*`, `rates.*`, `hr.*`
- [ ] n8n workflow IDs match actual workflows
- [ ] PPM SME review completed
- [ ] HR SME review completed

### v0.3 Quality Gate

- [ ] All 6 retail pages complete
- [ ] Medallion architecture documented accurately
- [ ] SariCoach prompts reviewed
- [ ] Superset dashboard links verified
- [ ] Retail SME review completed

### v1.0 Quality Gate

- [ ] All 55+ pages complete
- [ ] Full handbook navigation tested
- [ ] RAG indexing complete
- [ ] All AI agents can query handbook
- [ ] Documentation Lead sign-off
- [ ] Executive review completed

---

## Resource Allocation

| Role | v0.1 | v0.2 | v0.3 | v1.0 |
|------|------|------|------|------|
| Documentation Lead | 40% | 40% | 30% | 50% |
| Finance SME | 60% | 10% | 5% | 5% |
| PPM SME | 5% | 50% | 5% | 10% |
| HR SME | 5% | 30% | 5% | 5% |
| Retail SME | 5% | 5% | 50% | 10% |
| Platform Developer | 20% | 20% | 30% | 30% |
| DevOps Engineer | 10% | 10% | 10% | 30% |

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Schema changes after documentation | HIGH | Version lock schemas before doc sprint |
| n8n workflow naming inconsistency | MEDIUM | Establish naming convention upfront |
| SME availability | MEDIUM | Schedule reviews in advance |
| Scope creep | HIGH | Strict adherence to page inventory |
| RAG indexing issues | MEDIUM | Test chunking strategy early |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Page completion rate | 100% per release | Pages completed / planned |
| SME approval rate | 100% | Pages approved / submitted |
| RAG query accuracy | >85% | Relevant results / total queries |
| User satisfaction | >4.0/5 | Post-release survey |
| Time to answer | <30s | Agent response time |
