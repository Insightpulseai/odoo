# ERP SaaS Clone Suite — Task Checklist

## Legend

- `[ ]` Not started
- `[~]` In progress
- `[x]` Completed
- `[!]` Blocked

---

## Phase 0: Foundation

### T0.1 Directory Structure

- [x] Create `catalog/` directory
- [x] Create `kb/parity/` directory
- [x] Create `kb/design_system/` directory
- [x] Create `tools/parity/` directory
- [x] Create `spec/erp-saas-clone-suite/` directory

### T0.2 Catalog Files

- [x] Create `catalog/best_of_breed.yaml` with clone targets
- [x] Create `catalog/equivalence_matrix.csv` with capability mapping
- [x] Create `kb/parity/rubric.json` with scoring weights
- [x] Create `kb/parity/baseline.json` with P0 baseline scores

### T0.3 Parity Tools

- [x] Implement `tools/parity/validate_spec_kit.py`
- [x] Implement `tools/parity/parity_audit.py`
- [x] Verify tools run without errors

### T0.4 CI Workflow

- [x] Create `.github/workflows/spec-and-parity.yml`
- [x] Test spec validation job
- [x] Test parity audit job
- [x] Verify artifact upload works

### T0.5 Platform Module Scaffolds

- [x] Create `addons/ipai_platform_workflow/` scaffold
- [x] Create `addons/ipai_platform_approvals/` scaffold
- [x] Create `addons/ipai_platform_audit/` scaffold
- [x] Create `addons/ipai_platform_theme/` scaffold
- [x] Verify all modules pass syntax check

---

## Phase 1: CRM Pipeline

### T1.1 Module Setup (`ipai_crm_pipeline`)

| Task | Capability ID | Owner | Status |
|------|---------------|-------|--------|
| Create module scaffold | crm.pipeline.board | - | [x] |
| Define manifest dependencies | crm.pipeline.board | - | [x] |
| Create security rules | crm.pipeline.board | - | [x] |

### T1.2 Pipeline Board Enhancement

| Task | Capability ID | Owner | Status |
|------|---------------|-------|--------|
| Inherit crm.lead model | crm.pipeline.board | - | [ ] |
| Add stage validation rules | crm.pipeline.board | - | [ ] |
| Implement quick action buttons | crm.pipeline.board | - | [ ] |
| Enhance kanban view | crm.pipeline.board | - | [ ] |
| Add stage rules indicator | crm.pipeline.board | - | [ ] |

### T1.3 Activity Timeline

| Task | Capability ID | Owner | Status |
|------|---------------|-------|--------|
| Extend mail.message display | crm.pipeline.board | - | [ ] |
| Add inline activity creation | crm.pipeline.board | - | [ ] |
| Implement @mention routing | crm.pipeline.board | - | [ ] |

### T1.4 Role Dashboards

| Task | Capability ID | Owner | Status |
|------|---------------|-------|--------|
| Pipeline by stage chart | crm.pipeline.board | - | [ ] |
| Win/loss ratio widget | crm.pipeline.board | - | [ ] |
| Activity metrics panel | crm.pipeline.board | - | [ ] |

### T1.5 Quality Gates

| Task | Capability ID | Owner | Status |
|------|---------------|-------|--------|
| Write unit tests | crm.pipeline.board | - | [ ] |
| Update parity score | crm.pipeline.board | - | [x] |
| Record demo flow | crm.pipeline.board | - | [ ] |

---

## Phase 2: Platform Primitives

### T2.1 Workflow Engine (`ipai_platform_workflow`)

| Task | Capability ID | Owner | Status |
|------|---------------|-------|--------|
| State machine model | platform.workflow | - | [ ] |
| Transition rules | platform.workflow | - | [ ] |
| Notification hooks | platform.workflow | - | [ ] |

### T2.2 Approval Chains (`ipai_platform_approvals`)

| Task | Capability ID | Owner | Status |
|------|---------------|-------|--------|
| Approver lookup | platform.approvals | - | [ ] |
| Delegation config | platform.approvals | - | [ ] |
| Escalation timer | platform.approvals | - | [ ] |

### T2.3 Audit Trail (`ipai_platform_audit`)

| Task | Capability ID | Owner | Status |
|------|---------------|-------|--------|
| Model mixin | platform.audit | - | [ ] |
| Change capture | platform.audit | - | [ ] |
| Log viewer | platform.audit | - | [ ] |

### T2.4 Theme Tokens (`ipai_platform_theme`)

| Task | Capability ID | Owner | Status |
|------|---------------|-------|--------|
| SCSS variables | platform.theme | - | [ ] |
| Component mapping | platform.theme | - | [ ] |
| Theme switcher prep | platform.theme | - | [ ] |

---

## Phase 3: ITSM Incident

### T3.1 Module Setup (`ipai_itsm_incident`)

| Task | Capability ID | Owner | Status |
|------|---------------|-------|--------|
| Create module scaffold | itsm.incident.queue | - | [ ] |
| Define dependencies | itsm.incident.queue | - | [ ] |
| Create security rules | itsm.incident.queue | - | [ ] |

### T3.2 Incident Intake

| Task | Capability ID | Owner | Status |
|------|---------------|-------|--------|
| Incident model | itsm.incident.queue | - | [ ] |
| Intake form | itsm.incident.queue | - | [ ] |
| Auto-categorization | itsm.incident.queue | - | [ ] |

### T3.3 Queue Management

| Task | Capability ID | Owner | Status |
|------|---------------|-------|--------|
| Queue views | itsm.incident.queue | - | [ ] |
| Assignment rules | itsm.incident.queue | - | [ ] |
| SLA tracking | itsm.incident.queue | - | [ ] |

### T3.4 Escalation

| Task | Capability ID | Owner | Status |
|------|---------------|-------|--------|
| Escalation workflow | itsm.incident.queue | - | [ ] |
| Notification triggers | itsm.incident.queue | - | [ ] |
| Dashboard updates | itsm.incident.queue | - | [ ] |

---

## Phase 4: P1 Verticals

### T4.1 WorkOS Pages (`ipai_workos_pages`)

| Task | Capability ID | Owner | Status |
|------|---------------|-------|--------|
| Module scaffold | workos.pages.db | - | [ ] |
| Wiki pages | workos.pages.db | - | [ ] |
| Database views | workos.pages.db | - | [ ] |
| Templates | workos.pages.db | - | [ ] |

### T4.2 Assets Checkout (`ipai_assets_checkout`)

| Task | Capability ID | Owner | Status |
|------|---------------|-------|--------|
| Module scaffold | assets.checkout.reserve | - | [ ] |
| Reservation workflow | assets.checkout.reserve | - | [ ] |
| Custody tracking | assets.checkout.reserve | - | [ ] |
| Return processing | assets.checkout.reserve | - | [ ] |

### T4.3 PPM Portfolio (`ipai_ppm_portfolio`)

| Task | Capability ID | Owner | Status |
|------|---------------|-------|--------|
| Module scaffold | ppm.portfolio.lite | - | [ ] |
| Portfolio grouping | ppm.portfolio.lite | - | [ ] |
| Capacity view | ppm.portfolio.lite | - | [ ] |
| Budget summary | ppm.portfolio.lite | - | [ ] |

---

## Phase 5: Launch Prep

### T5.1 Performance

| Task | Owner | Status |
|------|-------|--------|
| Query optimization | - | [ ] |
| Caching review | - | [ ] |
| Load testing | - | [ ] |

### T5.2 Security

| Task | Owner | Status |
|------|-------|--------|
| Permission audit | - | [ ] |
| Penetration test | - | [ ] |
| Compliance check | - | [ ] |

### T5.3 Documentation

| Task | Owner | Status |
|------|-------|--------|
| User guides | - | [ ] |
| Admin docs | - | [ ] |
| API docs | - | [ ] |

### T5.4 Demo Environment

| Task | Owner | Status |
|------|-------|--------|
| Seed data scripts | - | [ ] |
| Reset automation | - | [ ] |
| Recording setup | - | [ ] |

---

## Summary

| Phase | Total | Complete | In Progress | Blocked |
|-------|-------|----------|-------------|---------|
| 0: Foundation | 17 | 17 | 0 | 0 |
| 1: CRM Pipeline | 16 | 4 | 0 | 0 |
| 2: Platform | 12 | 0 | 0 | 0 |
| 3: ITSM | 12 | 0 | 0 | 0 |
| 4: P1 Verticals | 12 | 0 | 0 | 0 |
| 5: Launch | 12 | 0 | 0 | 0 |
| **Total** | **81** | **21** | **0** | **0** |
