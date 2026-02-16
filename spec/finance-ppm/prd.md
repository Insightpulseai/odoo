# Finance PPM — Product Requirements Document

> **Module**: Finance PPM (Project Portfolio Management)
> **Client**: TBWA\SMP Philippines
> **Stack**: Odoo 19 CE + OCA 19.0 + PostgreSQL 16
> **Version**: 1.2.0

---

## Overview

Finance PPM manages the month-end financial close and BIR tax filing compliance
workflow for TBWA\SMP Philippines. The system is structured as 2 Odoo projects
with 89 base tasks (39 closing + 50 BIR), 6 shared Kanban stages, and automated
alerting via n8n.

---

## Team Directory (SSOT)

> **Canonical source**: `data/seed/finance_ppm/tbwa_smp/team_directory.csv`
> **Cross-artifact parity**: roster must match CSV + import/seed scripts
> (enforced by `scripts/finance/validate_team_directory.py`)

| Code | Name | Role | Tier |
|------|------|------|------|
| CKVC | Khalil Veracruz | Finance Director | Director |
| RIM | Rey Meran | Senior Finance Manager | Senior Manager |
| BOM | Beng Manalo | Finance Manager | Manager |
| JPAL | Jinky Paladin | Finance Analyst | Analyst |
| LAS | Amor Lasaga | Finance Analyst | Analyst |
| JLI | Jerald Loterte | Finance Analyst | Analyst |
| RMQB | Sally Brillantes | Finance Analyst | Analyst |
| JAP | Jasmin Ignacio | Finance Analyst | Analyst |
| JRMO | Jhoee Oliva | Finance Analyst | Analyst |

### Invariants (enforced by CI gate)

- **Total headcount**: exactly 9
- **Tier counts**: Director=1, Senior Manager=1, Manager=1, Analyst=6
- **Uniqueness**: Code is unique; Name is unique
- **Allowed roles**: exactly {Finance Director, Senior Finance Manager, Finance Manager, Finance Analyst}
- **Allowed tiers**: exactly {Director, Senior Manager, Manager, Analyst}
- **JPAL role**: must be Finance Analyst (never Finance Supervisor)
- **Cross-artifact parity**: team_directory.csv must match EMPLOYEES dict in import scripts

### Role → Approval Mapping

| Tier | Approval Level | Workflow Stage |
|------|---------------|---------------|
| Director (CKVC) | Final approver | Pending Approval → Done |
| Senior Manager (RIM) | Senior reviewer | Under Review → Pending Approval |
| Manager (BOM) | Primary preparer (BIR) | To Do → In Preparation |
| Analyst (6 people) | Task preparers (Close) | To Do → In Preparation |

---

## Projects

### IM1: Finance PPM - Month-End Close

- **Tasks**: 39 (5 phases)
- **Phases**: I (Initial & Compliance) → II (Accruals & Amortization) → III (WIP) → IV (Final Adjustments) → V (Sign-off)
- **Deadline model**: Working Day (WD) offsets relative to period end
- **Recurring**: Monthly

### IM2: Finance PPM - BIR Tax Filing

- **Tasks**: 50 (9 BIR form types)
- **Form types**: 1601-C, 0619-E, 2550M, 2550Q, 1601-EQ, 1702Q, 1702-RT, 1604-CF, 1604-E
- **Deadline model**: Fixed BIR calendar dates (10th, 20th, 25th, etc.)
- **Recurring**: Monthly (1601-C, 0619-E, 2550M), Quarterly (2550Q, 1601-EQ, 1702Q), Annual (1702-RT, 1604-CF, 1604-E)

### Shared Workflow (6 Kanban Stages)

```
To Do → In Preparation → Under Review → Pending Approval → Done → Cancelled
```

---

## Logframe

| Level | Objective | Indicator | RAG Threshold |
|-------|-----------|-----------|---------------|
| Goal | 100% compliant + timely filing | On-time % | GREEN ≥95%, AMBER ≥80% |
| Outcome | Streamlined team coordination | Avg delay < 1 day | GREEN ≤1d, AMBER ≤3d |
| IM1 | Accurate month-end closing | % TB reconciled | GREEN ≥95%, AMBER ≥75% |
| IM2 | On-time BIR filing | Filing rate vs deadline | GREEN: 0 overdue, AMBER ≤2 |
| Outputs | JEs finalized + BIR filed | # completed tasks | Per compliance sheet |

---

## SAP Feature Parity

### SAP Financial Close Cockpit (FCC)

SAP FCC supports planning, execution, monitoring, and analysis of financial
closing tasks. Key capabilities include:

- **Task Scheduler**: Dependency-aware scheduling with Gantt/timeline view
  and critical-path designation on tasks (FCC add-on)
  [SAP Fiori Apps Library: Manage Financial Close]
- **Closing Cockpit**: Centralized dashboard for close status, bottleneck
  identification, and SLA tracking
  [SAP Help Portal: Financial Close Cockpit]
- **Integration**: Automated journal posting with validation rules,
  intercompany reconciliation, and balance carryforward

### SAP Tax Compliance

SAP Tax Compliance emphasizes hit processing with status/task management
and automation support, including ML acceleration for tax determination:

- **Tax Filing Management**: Form preparation, validation, and electronic
  submission workflows with status tracking
  [SAP Help Portal: Tax Compliance for S/4HANA]
- **Compliance Calendar**: Jurisdiction-aware deadline tracking with
  escalation and notification rules

### Odoo 19 Bridge Implementation

| SAP Feature | Odoo 19 Bridge | Status |
|-------------|---------------|--------|
| Gantt / Critical Path | OCA `project_timeline` + `project_task_dependency` | `install_oca_gantt_bridge.sh` |
| Tax Form Generation | Odoo 19 PH localization + `ipai_bir_tax_compliance` | `n8n_bir_form_generation.json` |
| e-Filing Automation | n8n → eFPS / eBIRForms / eAFS | `n8n_bir_efiling_automation.json` |
| AI Journal Posting | Claude API validation → `account.move` draft | `n8n_ai_journal_posting.json` |
| Compliance Dashboard | Superset (11 SQL views including logframe KPIs) | `dashboard_queries_odoo19.sql` |

### Sources

- SAP Fiori Apps Library — Manage Financial Close: `https://fioriappslibrary.hana.ondemand.com/`
- SAP Help Portal — Financial Close Cockpit: `https://help.sap.com/docs/portfolio-category/ACCOUNTING_AND_FINANCIAL_CLOSE`
- SAP Help Portal — Tax Compliance: `https://help.sap.com/docs/SAP_ASSURANCE_AND_COMPLIANCE_SOFTWARE_FOR_SAP_S_4HANA_-_SAP_TAX_COMPLIANCE_FOR_SAP_S_4HANA`

---

## Seed Data SSOT

### Canonical Root

```
data/seed/finance_ppm/tbwa_smp/
├── team_directory.csv     # 9 employees with Code, Name, Email, Role, Tier
├── projects.csv           # 2 projects (Month-End Close + BIR Tax Filing)
├── tags.csv               # 33 tags (phases + BIR forms + categories)
├── tasks_month_end.csv    # 39 closing tasks (5 phases)
├── tasks_bir_tax.csv      # 50 BIR tasks (9 form types)
└── logframe.csv           # Logframe matrix (Goal → Activities)
```

### Archive Policy

- **No deletes**: superseded seed variants are moved to `data/archive/finance_ppm/tbwa_smp/<YYYYMMDD>/`
- **Provenance**: every archived set includes a `MANIFEST.md` with original path, date, reason, and canonical replacement
- **CI enforcement**: `scripts/finance/validate_seed_ssot.py` fails PRs if duplicate seed data exists outside archive

### Import Scripts

All import/seed scripts reference the canonical root via:
```python
SEED_ROOT = "data/seed/finance_ppm/tbwa_smp"
```

---

## Automation

### n8n Workflows (4)

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| Recurrent Alerts | Cron 9AM/5PM PHT | Due/overdue/handover Slack alerts |
| BIR Form Generation | Weekly + Webhook | Generate .dat files via Odoo 19 PH |
| BIR e-Filing | Webhook | eFPS/eBIRForms/eAFS packaging |
| AI Journal Posting | Weekday 6AM + Webhook | Claude API JE validation → draft |

### Superset Dashboard (11 views)

Views 1-6: Operational (task summary, funnel, workload, timeline, tax calendar, team)
Views 7-11: Logframe KPIs (goal, outcome, IM1, IM2, outputs) with RAG status

---

## Quality Gates

| Gate | Script | Trigger |
|------|--------|---------|
| Team directory drift | `scripts/finance/validate_team_directory.py` | PR touching roster/spec/import |
| Seed SSOT enforcement | `scripts/finance/validate_seed_ssot.py` | PR touching data/seed, data/archive, scripts |
| Finance PPM data | `scripts/validate_finance_ppm_data.py` | Existing gate |
| Deployment test | `scripts/test_finance_ppm_odoo19.sh` | Post-deploy |
