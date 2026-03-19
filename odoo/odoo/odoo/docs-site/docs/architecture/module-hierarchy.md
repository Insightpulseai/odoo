---
title: Module hierarchy
description: Target module structure with 60 modules across 8 layers.
---

# Module hierarchy

The target architecture consolidates from 109 modules down to 60, organized in 8 layers. Each layer has a clear responsibility boundary.

## Architecture principles

1. **Config, then OCA, then Delta.** Use built-in configuration first, OCA second, custom `ipai_*` only when needed.
2. **Thin extensions.** Prefer inheriting existing Odoo models over creating new ones.
3. **Single responsibility.** One module addresses one domain concern.
4. **Export analytics.** Heavy analytics belong in Supabase/ADLS, not Odoo.

## Layer summary

| Layer | Count | Purpose | Key modules |
|-------|-------|---------|-------------|
| **Core** | 5 | Base dependencies, workspace, branding, tenancy, feature flags | `ipai_dev_studio_base`, `ipai_workspace_core`, `ipai_ce_branding`, `ipai_tenant_core`, `ipai_module_gating` |
| **Platform** | 7 | Theme, audit, approvals, workflow, permissions, design tokens, icons | `ipai_platform_theme`, `ipai_platform_audit`, `ipai_platform_approvals`, `ipai_platform_workflow`, `ipai_platform_permissions`, `ipai_ui_brand_tokens`, `ipai_web_icons_fluent` |
| **AI / Agents** | 11 | AI framework, agents, prompts, connectors, providers, chat, control room | `ipai_ai_core`, `ipai_ai_agents`, `ipai_ai_prompts`, `ipai_ai_connectors`, `ipai_ask_ai`, `ipai_control_room`, `ipai_marketing_ai` |
| **Finance** | 7 | PPM, month-end, close orchestration, BIR compliance, expenses, OCR, seed data | `ipai_finance_ppm`, `ipai_month_end`, `ipai_close_orchestration`, `ipai_bir_compliance`, `ipai_expense`, `ipai_ocr_core` |
| **HR** | 6 | Payroll (PH), attendance, leave, appraisals, expense liquidation, planning | `ipai_hr_payroll_ph`, `ipai_hr_attendance`, `ipai_hr_leave`, `ipai_hr_appraisal` |
| **Services** | 7 | Helpdesk, approvals, planning, timesheet, field service, sign, documents | `ipai_helpdesk`, `ipai_approvals`, `ipai_planning`, `ipai_timesheet` |
| **Connectors** | 4 | Superset, Slack, n8n, data catalog | `ipai_superset_connector`, `ipai_slack_connector`, `ipai_n8n_connector`, `ipai_catalog_bridge` |
| **WorkOS** | 9 | Core framework, database, views, blocks, collab, search, canvas, templates | `ipai_workos_core`, `ipai_workos_blocks`, `ipai_workos_canvas`, `ipai_workos_collab` |

**Total: ~60 modules** (down from 109)

## Dependency graph

```
                    ipai_dev_studio_base
                            |
                    ipai_workspace_core
                            |
                    ipai_ce_branding
                     +------+------+
                     |      |      |
              ipai_ai_core  |  ipai_platform_*
                  |         |         |
         ipai_ai_agents     |   ipai_finance_ppm
              |             |         |
    ipai_control_room   ipai_ppm  ipai_month_end
              |             |         |
        ipai_ask_ai    ipai_workos_*  ipai_bir_compliance
```

## Target directory structure

```
addons/
  oca/                              # OCA modules (submodules, not tracked)
  |  account-closing/
  |  account-financial-reporting/
  |  mis-builder/
  |
  ipai/                             # IPAI custom modules
     # --- CORE LAYER ---
     ipai_dev_studio_base/          # Base dependencies (install first)
     ipai_workspace_core/           # Core workspace + routes + settings
     ipai_ce_branding/              # CE branding + portal fixes
     ipai_tenant_core/              # Multi-tenant support
     ipai_module_gating/            # Feature flags
     #
     # --- PLATFORM LAYER ---
     ipai_platform_theme/           # Base theme with variants
     ipai_platform_audit/           # Audit trail mixin
     ipai_platform_approvals/       # Approval workflow mixin
     ipai_platform_workflow/        # State machine mixin
     ipai_platform_permissions/     # RBAC mixin
     ipai_ui_brand_tokens/          # Design system tokens
     ipai_web_icons_fluent/         # Icon pack
     #
     # --- AI/AGENTS LAYER ---
     ipai_ai_core/                  # Core AI framework + sources + audit
     ipai_ai_agents/                # Agent system + UI
     ipai_ai_prompts/               # Prompt templates
     ipai_ai_connectors/            # LLM API connectors
     ipai_ask_ai/                   # Context AI assistant
     ipai_control_room/             # Agent control plane
     #
     # --- FINANCE LAYER ---
     ipai_finance_ppm/              # Core PPM (consolidated)
     ipai_month_end/                # Month-end orchestration
     ipai_close_orchestration/      # Close automation rules
     ipai_bir_compliance/           # BIR tax compliance
     ipai_expense/                  # Expense extensions
     ipai_ocr_core/                 # Unified OCR
     #
     # --- CONNECTORS LAYER ---
     ipai_superset_connector/       # Superset guest token embed
     ipai_slack_connector/          # Slack webhooks
     ipai_n8n_connector/            # n8n workflow triggers
     ipai_catalog_bridge/           # Data catalog sync
```

## OCA integration strategy

### Tier 1: must have (integrate immediately)

| OCA repo | Modules | Replaces |
|----------|---------|----------|
| `account-closing` | `account_cutoff_accrual_subscription`, `account_invoice_start_end_dates` | Custom period closing logic in `ipai_month_end` |
| `account-financial-reporting` | `account_financial_report` | Custom report generation |
| `mis-builder` | `mis_builder`, `mis_builder_budget` | Custom KPI dashboards in `ipai_finance_ppm` |

### Tier 2: should have (phase 2)

| OCA repo | Modules | Purpose |
|----------|---------|---------|
| `account-reconciliation` | `account_reconciliation_widget` | Bank reconciliation UI |
| `project` | `project_timeline`, `project_status` | Project management extensions |

### Tier 3: nice to have

| OCA repo | Modules | Purpose |
|----------|---------|---------|
| `web` | `web_widget_x2many_2d_matrix`, `web_pivot_computed_measure` | Advanced UI widgets |

## Thin extension pattern

All `ipai_*` modules extend existing Odoo models rather than creating parallel ones:

```python
# Correct: thin extension
class AccountMove(models.Model):
    _inherit = "account.move"

    finance_cluster_id = fields.Many2one('ipai.finance.cluster')
    close_status = fields.Selection([
        ('open', 'Open'),
        ('pending', 'Pending Review'),
        ('closed', 'Closed'),
    ])

    @api.depends('line_ids.balance')
    def _compute_cluster_balance(self):
        ...
```

!!! danger "Anti-pattern"
    Do not create parallel models like `ipai.account.move`. Inherit the standard `account.move` model and add fields.

## Module naming convention

```
ipai_<domain>_<feature>

Domains:
  ai        AI/ML features
  finance   Accounting and finance
  hr        Human resources
  ppm       Project portfolio management
  workos    WorkOS / knowledge base
  platform  Cross-cutting platform features
  bir       BIR tax compliance (Philippines)
```
