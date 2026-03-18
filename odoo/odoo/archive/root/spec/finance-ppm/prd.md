# Finance PPM — Product Requirements Document

> **Module**: Finance PPM (Project Portfolio Management)
> **Client**: TBWA\SMP Philippines
> **Stack**: Odoo 19 CE + OCA 19.0 + PostgreSQL 16
> **Version**: 1.3.0

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

## Parity Model: Module Replacements vs Platform Bridges

> **Authoritative map**: `spec/finance-ppm/parity_map.yaml`
> **Constitution**: `spec/finance-ppm/constitution.md`
> **Decision records**: `spec/finance-ppm/decisions/`
> **Enforced by**: `scripts/policy/validate_parity_map.py` + CI gate

### Parity Order (Non-Negotiable)

```
CE native → OCA add-on → ipai_* delta → Platform bridge
```

Each step-up requires a decision record (`spec/finance-ppm/decisions/`) explaining
why the previous layer was insufficient.

### Module Replacements (Layers 1-3)

These are **installable Odoo modules** (`ir.module.module`).

| Capability | Layer | Implementation | Notes |
|-----------|-------|---------------|-------|
| Project structure | CE | Native `project.project` + `project.task` | 2 projects, 89 tasks, 6 stages |
| Kanban workflow | CE | Native `project.task.type` stages | 6-stage workflow |
| Task assignment | CE | Native `res.users` on tasks | Team member assignment |
| Task deadlines | CE | Native `date_deadline` | WD offsets + BIR calendar |
| Task tags | CE | Native `project.tags` | 33 tags (phases + BIR forms) |
| Project milestones | CE | Native `project.milestone` | 11 logframe milestones |
| Fiscal positions | CE | Native `account.fiscal.position` | PH withholding tax |
| Task dependencies | OCA | `project_task_dependency` (19.0) | Predecessor/successor |
| Timeline view | OCA | `project_timeline` (19.0) | Timeline bar view (NOT full Gantt) |
| Stage closed | OCA | `project_stage_closed` (19.0) | Done/Cancelled distinction |
| Finance PPM controls | Delta | `ipai_finance_ppm` | Budget/forecast/variance |
| BIR tax compliance | Delta | `ipai_bir_tax_compliance` | 36 eBIRForms |
| BIR notifications | Delta | `ipai_bir_notifications` | Filing deadline alerts |
| Enterprise stubs | Delta | `ipai_enterprise_bridge` | Safe stubs only |
| Finance workflow | Delta | `ipai_finance_workflow` | Role-based stage transitions |

### Platform Bridges (Layer 4)

These are **NOT Odoo modules**. They run outside the Odoo process and substitute
platform-level services that have no module equivalent.

| Capability | Replaces | Implementation | Location |
|-----------|----------|---------------|----------|
| Recurrent alerts | EE activity scheduling | n8n → Slack | `platform/bridges/recurrent-alerts/` |
| BIR form generation | SAP Tax Compliance forms | n8n → .dat files | `platform/bridges/bir-form-generation/` |
| e-Filing automation | SAP Tax Filing integration | n8n → eFPS/eBIRForms | `platform/bridges/efiling-automation/` |
| AI journal posting | SAP Smart Journal / Odoo IAP | n8n + Claude API | `platform/bridges/ai-journal-posting/` |
| Compliance dashboard | SAP FCC Closing Cockpit | Superset + 11 SQL views | `platform/bridges/compliance-dashboard/` |

### Acknowledged Gaps (Not Available)

| Capability | SAP/EE Feature | Status |
|-----------|---------------|--------|
| Critical path analysis | SAP FCC critical-path designation | Planned; `project_timeline_critical_path` unverified for 19.0 |
| Resource leveling | SAP Planning resource leveling | Out of scope for v1 |
| Interactive Gantt | EE Gantt with drag-and-drop | Out of scope; OCA `project_timeline` is read-only timeline |

See `spec/finance-ppm/decisions/0006-critical-path-unavailable.md` for details.

---

## SAP Feature Parity (Reference)

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

### Odoo 19 Implementation Status

| SAP Feature | Odoo 19 Layer | Implementation | Status |
|-------------|--------------|---------------|--------|
| Timeline view | OCA (module) | `project_timeline` + `project_task_dependency` | Verified for 19.0 |
| Critical path | — | Not available | Unverified; see ADR-0006 |
| Tax form generation | Bridge (platform) | n8n workflow → .dat files | `platform/bridges/bir-form-generation/` |
| e-Filing | Bridge (platform) | n8n → eFPS/eBIRForms/eAFS | `platform/bridges/efiling-automation/` |
| AI journal posting | Bridge (platform) | Claude API + n8n → `account.move` draft | `platform/bridges/ai-journal-posting/` |
| Compliance dashboard | Bridge (platform) | Superset (11 SQL views) | `platform/bridges/compliance-dashboard/` |

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

## Email Notifications (v1)

> **Context**: DigitalOcean blocks outbound SMTP ports 25/465/587 on Droplets by default.
> All notification email is routed through Supabase Edge Functions (unrestricted outbound TCP)
> rather than Odoo's SMTP stack.

### Event Coverage (v1)

| Event | Trigger | Template | Recipients |
|-------|---------|----------|------------|
| `task_assigned` | `finance_task.created` emitted by Odoo | Email: assigned task with project context | All `task.user_ids` with email |
| `task_stage_changed` | `finance_task.{in_progress,submitted,approved,filed}` | Email: task moved to new stage | All `task.user_ids` with email |

### Architecture

```
Odoo project_task_integration.py
  → send_ipai_event() (webhook with assignee_emails + project_name in payload)
  → supabase/functions/webhook-ingest
  → ops.webhook_events (INSERT)
  → ops.enqueue_email_notifications() TRIGGER
  → ops.email_notification_events (pending row per recipient)
  → supabase/functions/tick (every cycle)
  → supabase/functions/email-dispatcher
  → supabase/functions/zoho-mail-bridge?action=send_email
  → Zoho Mail API → recipient inbox
```

### Retry Policy

| Attempt | Backoff | Status after |
|---------|---------|--------------|
| 1 | immediate | → 5 min retry if fail |
| 2 | +5 min | → 30 min retry if fail |
| 3 | +30 min | → dead if fail |
| 4+ | — | status=dead (no more retries) |

### Required Supabase Secrets

- `BRIDGE_SHARED_SECRET` — shared secret for `zoho-mail-bridge` auth
- `ZOHO_FROM_EMAIL` — sender address (e.g. `noreply@insightpulseai.com`)
- Zoho OAuth2 credentials already required by `zoho-mail-bridge`

---

## Quality Gates

| Gate | Script | Trigger |
|------|--------|---------|
| Team directory drift | `scripts/finance/validate_team_directory.py` | PR touching roster/spec/import |
| Seed SSOT enforcement | `scripts/finance/validate_seed_ssot.py` | PR touching data/seed, data/archive, scripts |
| Parity map enforcement | `scripts/policy/validate_parity_map.py` | PR touching spec, bridges, addons/ipai |
| Finance PPM data | `scripts/validate_finance_ppm_data.py` | Existing gate |
| Deployment test | `scripts/test_finance_ppm_odoo19.sh` | Post-deploy |
