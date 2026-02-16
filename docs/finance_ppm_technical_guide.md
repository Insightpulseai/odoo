# Finance PPM — Custom Module Technical Guide

> **Odoo 19 CE** | TBWA\SMP Philippines | `erp.insightpulseai.com`
> **Branch**: `claude/deploy-finance-ppm-odoo19-LbLm4`
> **Date**: 2026-02-15

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Finance PPM Ecosystem                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │  Month-End Close  │  │ BIR Tax Filing   │   ← 2 Odoo Projects│
│  │  39 tasks / 5 ph  │  │ 50 tasks / 9 frm │                   │
│  └────────┬─────────┘  └────────┬─────────┘                    │
│           │                      │                              │
│  ┌────────▼──────────────────────▼─────────┐                   │
│  │         6-Stage Kanban Workflow          │                   │
│  │  To Do → In Prep → Review → Approval    │                   │
│  │                   → Done → Cancelled     │                   │
│  └────────┬──────────────────────┬─────────┘                   │
│           │                      │                              │
│  ┌────────▼─────────┐  ┌────────▼─────────┐                   │
│  │  ipai_finance_ppm │  │ipai_bir_tax_comp │  ← Custom Modules │
│  │  (project+acctg)  │  │ (36 eBIRForms)   │                   │
│  └────────┬─────────┘  └────────┬─────────┘                   │
│           │                      │                              │
│  ┌────────▼──────────────────────▼─────────┐                   │
│  │      ipai_enterprise_bridge             │  ← OCA Parity     │
│  │  (OAuth, IoT, MQTT, project_timeline)   │                   │
│  └────────┬──────────────────────┬─────────┘                   │
│           │                      │                              │
│  ┌────────▼─────────┐  ┌────────▼─────────┐                   │
│  │    n8n Workflows  │  │  Superset Views  │  ← Automation     │
│  │  (alerts, eFPS,   │  │  (6 SQL views)   │                   │
│  │   AI journal)     │  │                   │                   │
│  └──────────────────┘  └──────────────────┘                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Module Inventory

### Active Modules (6)

| # | Module | Version | Category | License |
|---|--------|---------|----------|---------|
| 1 | `ipai_finance_ppm` | 19.0.1.0.0 | Services/Project | LGPL-3 |
| 2 | `ipai_bir_tax_compliance` | 18.0.1.0.0 | Accounting/Localizations | AGPL-3 |
| 3 | `ipai_bir_notifications` | 19.0.1.0.0 | Accounting/Localizations | AGPL-3 |
| 4 | `ipai_bir_plane_sync` | 19.0.1.0.0 | Accounting/Localizations | AGPL-3 |
| 5 | `ipai_enterprise_bridge` | 19.0.1.0.0 | Technical | LGPL-3 |
| 6 | `ipai_finance_workflow` | 19.0.1.0.0 | Accounting/Project | AGPL-3 |

### Deprecated (Do Not Install)

| Module | Reason | Migrated To |
|--------|--------|-------------|
| `ipai_finance_tax_return` | Deprecated | `ipai_enterprise_bridge` |

---

## 1. ipai_finance_ppm

**Path**: `addons/ipai/ipai_finance_ppm/`
**Purpose**: Finance + Project + Analytic controls and import clarity for CE

### Dependencies
```
project, account, analytic, mail
```

### Models

| Model File | Extends | Purpose |
|-----------|---------|---------|
| `project_project.py` | `project.project` | Adds PPM fields (budget, forecast, variance) |
| `analytic_account.py` | `account.analytic.account` | Finance analytic linking |
| `project_task_integration.py` | `project.task` | Task-to-JE integration |

### Data Files
- `security/ir.model.access.csv` — ACL rules
- `views/ipai_finance_ppm_menus.xml` — Navigation menus
- `views/project_project_views.xml` — Project form/tree extensions
- `views/account_analytic_account_views.xml` — Analytic views
- `views/ppm_import_wizard_views.xml` — Bulk import wizard
- `data/ir_cron_ppm_sync.xml` — Scheduled sync cron

### Key Features
- Project budget/forecast/variance tracking
- Analytic account linking for cost centers
- Bulk task import wizard (CSV)
- Cron-based PPM synchronization

---

## 2. ipai_bir_tax_compliance

**Path**: `addons/ipai_bir_tax_compliance/`
**Purpose**: Philippine BIR tax compliance — 36 eBIRForms support
**Application**: Yes (standalone app)

### Dependencies
```
base, mail, account, project
```

### Models

| Model File | Model Name | Purpose |
|-----------|-----------|---------|
| `bir_tax_return.py` | `bir.tax_return` | Tax return tracking (main record) |
| | `bir.tax_return.line` | Line items per return |
| `bir_vat.py` | `bir.vat.return` | VAT return records |
| | `bir.vat.line` | VAT line items (input/output) |
| `bir_withholding.py` | `bir.withholding.return` | Withholding tax returns |
| | `bir.withholding.line` | Withholding line items |
| `bir_filing_deadline.py` | `bir.filing.deadline` | Filing deadline tracking |
| `res_partner.py` | `res.partner` (ext.) | TIN validation on partners |

### Data Files
- `data/bir_tax_rates.xml` — BIR withholding tax rate tables
- `data/bir_filing_deadlines.xml` — Annual filing calendar
- `data/ir_cron.xml` — Deadline check cron jobs
- `views/bir_tax_return_views.xml` — Tax return forms
- `views/bir_vat_views.xml` — VAT return forms
- `views/bir_withholding_views.xml` — Withholding forms
- `views/bir_dashboard_views.xml` — Compliance dashboard
- `views/res_partner_views.xml` — TIN field on partners

### BIR Form Coverage (9 types in Finance PPM)

| Form | Frequency | Model | .dat Export |
|------|-----------|-------|-------------|
| 1601-C | Monthly | `bir.withholding.return` | Yes |
| 0619-E | Monthly | `bir.withholding.return` | Yes |
| 2550M | Monthly | `bir.vat.return` | Yes |
| 2550Q | Quarterly | `bir.vat.return` | Yes + SLSP |
| 1601-EQ | Quarterly | `bir.withholding.return` | Yes + QAP |
| 1702Q | Quarterly | `bir.tax_return` | No |
| 1702-RT | Annual | `bir.tax_return` | No |
| 1604-CF | Annual | `bir.alphalist` | Yes + Alphalist |
| 1604-E | Annual | `bir.alphalist` | Yes + SAWT |

---

## 3. ipai_bir_notifications

**Path**: `addons/ipai/ipai_bir_notifications/`
**Purpose**: Email digest and urgent alerts for BIR tax filing deadlines

### Dependencies
```
base, mail, ipai_bir_tax_compliance
```

### Models

| Model File | Model Name | Purpose |
|-----------|-----------|---------|
| `bir_alert.py` | `bir.alert` | Alert records with cooldown logic |

### Alert Logic
- **Daily digest**: Sent at configured time via cron
- **Urgent alerts**: Triggered when deadline ≤3 days away
- **Cooldown**: 4-hour minimum between urgent alerts
- **Channel**: Zoho Mail SMTP (per deprecated Mailgun replacement)

---

## 4. ipai_bir_plane_sync

**Path**: `addons/ipai/ipai_bir_plane_sync/`
**Purpose**: Bidirectional sync between BIR deadlines and Plane project management

### Dependencies
```
base, ipai_bir_tax_compliance
```

### External Dependencies
```python
pip install requests
```

### Models

| Model File | Extends | Purpose |
|-----------|---------|---------|
| `bir_filing_deadline.py` | `bir.filing.deadline` | Adds Plane issue sync fields |

### Integration Points
- Syncs `bir.filing.deadline` ↔ Plane issues
- OKR tracking for compliance metrics
- Webhook support for real-time updates

---

## 5. ipai_enterprise_bridge

**Path**: `addons/ipai/ipai_enterprise_bridge/`
**Purpose**: Replace Odoo Enterprise/IAP features with CE+OCA alternatives

### Dependencies
```
base, base_setup, mail, auth_oauth, fetchmail, web,
hr_expense, maintenance, project
```

### External Dependencies
```python
pip install requests paho-mqtt
```

### Models (15 files)

| Model File | Purpose |
|-----------|---------|
| `enterprise_bridge.py` | Core bridge config (`ipai.enterprise.bridge.config`) |
| `iot_device.py` | IoT device management (CE alternative) |
| `iot_mqtt_bridge.py` | MQTT-based IoT communication |
| `ai_mixin.py` | AI capability mixin for all models |
| `ipai_close_checklist.py` | Month-end close checklist |
| `ipai_policy.py` | Policy enforcement framework |
| `ipai_job.py` | Background job processing |
| `res_config_settings.py` | Settings page integration |
| `account_move.py` | Journal entry extensions |
| `project_task_integration.py` | Project task PPM fields |
| `hr_expense_integration.py` | Expense workflow (CE) |
| `maintenance_equipment_integration.py` | Equipment tracking |
| `product_template.py` | Product barcode extensions |
| `purchase_order.py` | Purchase order integration |

### Enterprise Feature Mappings

| Enterprise Feature | Bridge Mode | OCA Alternative |
|-------------------|-------------|----------------|
| Planning (Gantt) | OCA | `project_timeline` |
| Approvals | OCA | `purchase_requisition` |
| Studio | Custom | `ipai_enterprise_bridge` |
| IoT | Custom | `iot_mqtt_bridge.py` |
| Helpdesk | OCA | `helpdesk_mgmt` |
| Marketing Automation | n8n | n8n workflows |

---

## 6. ipai_finance_workflow

**Path**: `addons/ipai/ipai_finance_workflow/`
**Purpose**: Shared finance stages + projects for Month-End Close and BIR workflows

### Dependencies
```
project, mail, hr, ipai_workspace_core
```

### Models

| Model File | Purpose |
|-----------|---------|
| `finance_role.py` | Finance team role definitions |
| `project_task.py` | Task extensions for finance workflow |

### Data Seeds
- `data/finance_roles.xml` — Director, Senior Manager, Supervisor, Accountant
- `data/finance_task_stages.xml` — 5 stages: Preparation → Review → Approval → Execute → Closed
- `data/finance_projects.xml` — 2 projects: Month-End Close (IM1), BIR Returns (IM2)
- `data/finance_team.xml` — Team member assignments
- `data/finance_ppm_tasks.xml` — Base task templates

---

## Installation Order

```bash
# 1. Prerequisites
pip install requests paho-mqtt

# 2. Install in dependency order
python3 scripts/install_module_xmlrpc.py --modules "ipai_enterprise_bridge"
python3 scripts/install_module_xmlrpc.py --modules "ipai_finance_workflow"
python3 scripts/install_module_xmlrpc.py --modules "ipai_finance_ppm"
python3 scripts/install_module_xmlrpc.py --modules "ipai_bir_tax_compliance"
python3 scripts/install_module_xmlrpc.py --modules "ipai_bir_notifications"
python3 scripts/install_module_xmlrpc.py --modules "ipai_bir_plane_sync"

# 3. Install OCA Gantt bridge (Bridge Gap 1)
bash scripts/install_oca_gantt_bridge.sh "$ODOO_ADMIN_PASSWORD"

# 4. Seed Finance PPM data
python3 scripts/seed_finance_ppm_stages_odoo19.py "$ODOO_ADMIN_PASSWORD"
python3 scripts/bulk_import_tasks_odoo19.py "$ODOO_ADMIN_PASSWORD"

# 5. Verify
bash scripts/test_finance_ppm_odoo19.sh "$ODOO_ADMIN_PASSWORD"
```

---

## Dependency Graph

```
                    ┌──────────────┐
                    │     base     │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
     ┌────────▼──┐  ┌──────▼─────┐  ┌──▼────────────┐
     │  project   │  │  account   │  │  mail / hr     │
     └────┬───────┘  └──────┬─────┘  └──┬────────────┘
          │                 │            │
     ┌────▼─────────────────▼────────────▼──┐
     │      ipai_enterprise_bridge          │
     │   (OAuth, IoT, MQTT, EE parity)     │
     └────┬──────────────────────┬──────────┘
          │                      │
     ┌────▼───────────┐    ┌────▼────────────────┐
     │ipai_workspace  │    │ipai_finance_workflow │
     │    _core       │    │(stages, roles, team) │
     └────────────────┘    └────┬────────────────┘
                                │
               ┌────────────────┼──────────────────┐
               │                │                   │
     ┌─────────▼──────┐ ┌──────▼─────────┐ ┌──────▼──────────────┐
     │ipai_finance_ppm│ │ipai_bir_tax    │ │ OCA project_timeline│
     │(budget/analytic)│ │ _compliance    │ │ (Gantt/timeline)    │
     └────────────────┘ │(36 eBIRForms)  │ └─────────────────────┘
                        └──────┬─────────┘
                               │
                  ┌────────────┼────────────┐
                  │                         │
        ┌─────────▼──────────┐   ┌──────────▼─────────┐
        │ipai_bir_notifications│  │ipai_bir_plane_sync │
        │(email alerts)       │  │(Plane.so OKR sync)  │
        └────────────────────┘   └────────────────────┘
```

---

## n8n Workflow Automation

### Existing Workflows (4)

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| Recurrent Alerts | `n8n_finance_ppm_workflow_odoo19.json` | Cron 9AM/5PM PHT | Due/overdue/handover alerts |
| BIR Form Generation | `n8n_bir_form_generation.json` | Weekly + Webhook | Generate .dat files via Odoo 19 PH |
| BIR e-Filing | `n8n_bir_efiling_automation.json` | Webhook | eFPS/eBIRForms/eAFS packaging |
| AI Journal Posting | `n8n_ai_journal_posting.json` | Weekday 6AM + Webhook | Claude API JE validation |

### Environment Variables Required

```bash
# Odoo connection
N8N_ODOO_URL=https://erp.insightpulseai.com
N8N_ODOO_DB=odoo
N8N_ODOO_USER=admin@insightpulseai.com
N8N_ODOO_PASSWORD=<secret>

# Slack
N8N_SLACK_CHANNEL_ID=<channel-id>
N8N_SLACK_USER_MAP={"beng.manalo@omc.com":"U12345"}

# BIR compliance
N8N_BIR_COMPANY_TIN=000-000-000-000
N8N_BIR_COMPANY_RDO=000

# AI journal posting
N8N_ANTHROPIC_API_KEY=<secret>

# Supabase (audit trail)
N8N_SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
```

---

## Superset Dashboard Views (11)

| View | Purpose |
|------|---------|
| `v_closing_task_summary` | Task status by project and stage |
| `v_tax_filing_calendar` | BIR deadline calendar (9 form types) |
| `v_stage_funnel` | Stage transition funnel |
| `v_assignee_workload` | Workload distribution per analyst |
| `v_closing_timeline` | Close cycle timeline |
| `v_finance_team` | Team directory with roles |
| `v_logframe_goal_kpi` | On-time % with RAG status (Goal) |
| `v_logframe_outcome_kpi` | Avg delay per project (Outcome) |
| `v_logframe_im1_kpi` | Monthly close reconciliation (IM1) |
| `v_logframe_im2_kpi` | BIR filing rate by form type (IM2) |
| `v_logframe_outputs_kpi` | Consolidated output counts |

---

## SAP FCC Bridge Gaps — Implementation Status

| # | Gap | SAP Feature | Odoo 19 Bridge | Status |
|---|-----|------------|-----------------|--------|
| 1 | Gantt/Critical Path | SAP FCC Task Scheduler | OCA `project_timeline` + `project_task_dependency` | `install_oca_gantt_bridge.sh` |
| 2 | Tax Form Generation | SAP Tax Compliance Forms | Odoo 19 PH l10n + `ipai_bir_tax_compliance` | `n8n_bir_form_generation.json` |
| 3 | e-Filing Automation | SAP Tax Filing Integration | n8n → eFPS/eBIRForms/eAFS | `n8n_bir_efiling_automation.json` |
| 4 | AI Journal Posting | SAP Smart Journal | Claude API + n8n → `account.move` draft | `n8n_ai_journal_posting.json` |

---

## Finance Team (SSOT)

> **Canonical source**: `data/seed/finance_ppm/tbwa_smp/team_directory.csv`
> **Validator**: `scripts/finance/validate_team_directory.py`
> **CI gate**: `.github/workflows/finance-team-directory-gate.yml`

| Code | Name | Role | Tier | Approval Level |
|------|------|------|------|---------------|
| CKVC | Khalil Veracruz | Finance Director | Director | Approver (final) |
| RIM | Rey Meran | Senior Finance Manager | Senior Manager | Reviewer (senior) |
| BOM | Beng Manalo | Finance Manager | Manager | Preparer (BIR) |
| JPAL | Jinky Paladin | Finance Analyst | Analyst | Phase III lead |
| LAS | Amor Lasaga | Finance Analyst | Analyst | Phase III-IV |
| JLI | Jerald Loterte | Finance Analyst | Analyst | Phase IV |
| RMQB | Sally Brillantes | Finance Analyst | Analyst | Phase IV |
| JAP | Jasmin Ignacio | Finance Analyst | Analyst | Phase IV |
| JRMO | Jhoee Oliva | Finance Analyst | Analyst | Phase IV |

### Roster Invariants

- **Headcount**: exactly 9
- **Tier counts**: Director=1, Senior Manager=1, Manager=1, Analyst=6
- **Uniqueness**: Code and Name are both unique
- **JPAL**: must be Finance Analyst (enforced by validator)
- **Cross-artifact parity**: CSV must match EMPLOYEES dict in `bulk_import_tasks_odoo19.py`

### How Drift Is Prevented

1. `validate_team_directory.py` checks all invariants (headcount, tiers, roles, uniqueness, JPAL)
2. `validate_seed_ssot.py` ensures no duplicate seed data exists outside canonical/archive
3. CI workflow runs both validators on PRs touching roster, spec, or import files
4. Import script EMPLOYEES dict has no fallback — fails fast if canonical data is wrong

---

## Seed Data (SSOT)

> **Canonical root**: `data/seed/finance_ppm/tbwa_smp/`
> **Archive root**: `data/archive/finance_ppm/tbwa_smp/`
> **Validator**: `scripts/finance/validate_seed_ssot.py`

### Canonical Seed Files

| File | Records | Purpose |
|------|---------|---------|
| `team_directory.csv` | 9 | Employee directory with Tier column |
| `projects.csv` | 2 | Month-End Close + BIR Tax Filing |
| `tags.csv` | 33 | Phase tags + BIR form tags |
| `tasks_month_end.csv` | 39 | 5-phase closing workflow |
| `tasks_bir_tax.csv` | 50 | 9 BIR form types |
| `logframe.csv` | 7 | Logframe matrix (Goal → Activities) |

### Adding New Seed Data

All new seed data must go to `data/seed/finance_ppm/tbwa_smp/`.
Never create seed files at `data/finance_seed/` or `artifacts/data/`.

### Archive Policy

- Superseded seed variants are moved to `data/archive/finance_ppm/tbwa_smp/<YYYYMMDD>/`
- Every archived set must include a `MANIFEST.md` with provenance
- CI fails if duplicate seed data appears outside canonical/archive

---

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `seed_finance_ppm_stages_odoo19.py` | Seeds 6 stages + 2 projects |
| `bulk_import_tasks_odoo19.py` | Imports 89 tasks (39 close + 50 BIR) |
| `seed_logframe_milestones_odoo19.py` | Seeds logframe milestones |
| `deploy_finance_ppm_odoo19.sh` | Full deployment orchestrator |
| `test_finance_ppm_odoo19.sh` | 10-point verification test suite |
| `install_oca_gantt_bridge.sh` | OCA timeline + dependency install |
| `dashboard_queries_odoo19.sql` | 11 Superset SQL views |
| `finance/validate_team_directory.py` | Team roster invariant validator |
| `finance/validate_seed_ssot.py` | Seed data SSOT enforcement |

---

## Security Model

### Access Control

| Group | Close Project | BIR Project | Journal Posting |
|-------|-------------|-------------|-----------------|
| Finance Director | Full | Full | Post (final) |
| Senior Finance Mgr | Read/Write | Read/Write | Review |
| Finance Manager | Read/Write | Read/Write | Prepare |
| Finance Analyst | Read/Write (own) | Read (own) | None |

### Approval Workflow

```
Analyst prepares → Manager reviews → Senior Manager validates → Director approves
   (In Prep)        (Under Review)    (Pending Approval)          (Done)
```

### AI Safety Guards
- Claude API validates journal entries but **never auto-posts**
- All AI-generated entries created as `account.move` in **DRAFT** state
- Finance Director (CKVC) must manually approve and post
- Full audit trail stored in Supabase

---

*Generated: 2026-02-15 | Odoo 19 CE + OCA 19.0 | TBWA\SMP Philippines*
