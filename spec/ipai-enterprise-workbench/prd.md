# PRD — IPAI Enterprise Workbench for Odoo CE (18/19)

## 1) Problem Statement
We need a self-hosted, CE-first enterprise workbench delivering enterprise-class workflow parity without Odoo Enterprise/IAP. It must unify:
- Odoo CE (core operations)
- OCA (feature parity)
- IPAI modules (vertical workflows + minimal bridge)
- Superset BI (analytics)
- Supabase + n8n + MCP (automation backbone)
- Token-driven design system (UI/UX parity and rebranding readiness)
- GitHub Pages docs as canonical documentation surface

## 2) Goals
### 2.1 Primary Goal
Deliver a production-ready "Enterprise Workbench" stack that installs, configures, validates, and deploys reproducibly.

### 2.2 Required Outcomes (Acceptance Criteria)
1) **Odoo 18 CE** with OCA Project modules configured; Finance PPM stages aligned to canonical 6-stage workflow.
2) **Seed generation** from workbook is deterministic, includes `task_code`, stage mapping, and passes validation.
3) **Superset** runs and connects to analytics sources (Odoo read-only and/or replicated schemas) and exposes Finance PPM dashboards.
4) **Supabase + n8n + MCP** enable automation: reminders, escalations, approvals, data sync; with auditable run logs.
5) **IPAI design system modules** provide theme/token parity across Odoo + web surfaces; future TBWA branding is token-driven.
6) Documentation links and references are updated to the canonical base: `https://jgtolentino.github.io/odoo-ce/`.

## 3) Non-Goals
- Running Odoo's primary transactional database on Supabase.
- Re-implementing all Enterprise-only apps; parity is bounded to targeted workflows and ROI.
- UI-driven admin steps as the primary configuration mechanism (must be scripted/exportable).

## 4) Users
- Finance Ops: month-end close, BIR deadlines, approvals and auditability.
- Operations/Admin: deterministic deployments, upgrades, compliance gates.
- Analyst/BI: stable datasets, drift-controlled models, reproducible dashboards.
- Agentic DevOps: MCP tools for audits, seed regen, deploy verification.

## 5) Functional Requirements

### 5.1 Odoo CE + OCA + IPAI
- Install CE base apps as required by vertical bundles.
- Install OCA Project suite modules needed for stage management and templates.
- Configure Finance PPM stages (importable via XML and CSV templates).

**Canonical Finance PPM workflow:**
| Seq | Stage | Fold | State | Description |
|---:|---|---|---|---|
| 10 | To Do | false | draft | Not started |
| 20 | In Preparation | false | open | Data gathering |
| 30 | Under Review | false | open | Supervisor review |
| 40 | Pending Approval | false | pending | FD sign-off |
| 50 | Done | true | done | Closing stage |
| 60 | Cancelled | true | cancelled | Cancel stage |

### 5.2 Superset BI
- Superset runs as a service with:
  - dedicated metadata DB
  - datasets connecting to analytics views
- Must include starter dashboards:
  - Finance PPM stage/state progress
  - deadlines calendar and SLAs
  - exception lists (overdue / blocked)
  - audit trail lens (run logs, approvals, escalations)

### 5.3 Supabase + n8n + MCP Automation Backbone
- Supabase ops schema (runs/run_events/artifacts) stores:
  - automation run traces
  - artifacts (CSV exports, validation reports)
  - status transitions
- n8n runs:
  - scheduled reminders and escalations
  - inbound/outbound integrations (Mail, Slack/Mattermost, Drive)
  - data sync from Odoo to analytics schemas (where applicable)
- MCP provides tool endpoints:
  - seed generation + validation
  - repo health + drift checks
  - environment doctor
  - OCA aggregation verification

### 5.4 Design System Modules
- Introduce `ipai_design_system*` modules as token adapters:
  - SSOT `tokens.json`
  - OWL theme adapter for Odoo
  - web adapter for Workbench UI surfaces
  - future Mattermost branding overlay adapter

### 5.5 Documentation
- Must publish docs under: `https://jgtolentino.github.io/odoo-ce/`
- Any internal references to alternative docs bases must be removed or redirected.

## 6) EE/IAP Upsell Replacement Scope
- Remove enterprise upsell surfaces (UI and links).
- Replace EE-only capabilities via:
  - OCA modules where possible
  - OSS services + integration (Superset, OCR service, DMS/CMS)
  - minimal IPAI glue under `ipai_enterprise_bridge` when unavoidable
- All replacements require:
  - mapping doc (EE feature → CE/OCA/IPAI replacement)
  - scripted config
  - verification tests

## 7) Success Metrics
- CI stays green with all drift gates.
- Finance PPM validation passes (0 errors/warnings) against workbook-derived rules.
- Superset dashboards load successfully and match expected metrics.
- Supabase+n8n automation runs produce auditable events.
- Design system tokens apply consistently across surfaces.

## 8) Milestones
- M1: Workspace (Odoo + Superset + optional n8n) reproducible locally
- M2: Finance PPM canonicalization (workbook → seed + validation)
- M3: Superset dashboards (datasets + starter dashboards)
- M4: Supabase+n8n+MCP automation end-to-end
- M5: Design system modules (tokens + adapters)
- M6: Odoo 19 readiness (compat matrix + upgrade playbook + gates)

