# IPAI Target Module Architecture

**Generated:** 2026-01-12
**Target Module Count:** 60 (down from 109)

---

## Architecture Principles

1. **Config → OCA → Delta**: Use built-in config first, OCA second, custom only when needed
2. **Thin Extensions**: Prefer extending existing models over creating new ones
3. **Single Responsibility**: One module = one domain concern
4. **Export Analytics**: Heavy analytics belong in Supabase/Superset, not Odoo

---

## Target Module Hierarchy

```
odoo-ce/addons/
├── oca/                           # OCA modules (submodules, not tracked)
│   ├── account-closing/
│   ├── account-financial-reporting/
│   ├── mis-builder/
│   └── ...
│
├── ipai/                          # IPAI custom modules
│   │
│   ├── # ═══ CORE LAYER ═══
│   ├── ipai_dev_studio_base/      # Base dependencies (install first)
│   ├── ipai_workspace_core/       # Core workspace + routes + settings
│   ├── ipai_ce_branding/          # CE branding + portal fixes
│   ├── ipai_tenant_core/          # Multi-tenant support
│   ├── ipai_module_gating/        # Feature flags
│   │
│   ├── # ═══ PLATFORM LAYER ═══
│   ├── ipai_platform_theme/       # Base theme with variants
│   ├── ipai_platform_audit/       # Audit trail mixin
│   ├── ipai_platform_approvals/   # Approval workflow mixin
│   ├── ipai_platform_workflow/    # State machine mixin
│   ├── ipai_platform_permissions/ # RBAC mixin
│   ├── ipai_ui_brand_tokens/      # Design system tokens
│   ├── ipai_web_icons_fluent/     # Icon pack
│   │
│   ├── # ═══ AI/AGENTS LAYER ═══
│   ├── ipai_ai_core/              # Core AI framework + sources + audit
│   ├── ipai_ai_agents/            # Agent system + UI
│   ├── ipai_ai_prompts/           # Prompt templates
│   ├── ipai_ai_connectors/        # LLM API connectors
│   ├── ipai_ai_provider_kapa/     # Kapa+ provider
│   ├── ipai_ai_provider_pulser/   # Pulser provider
│   ├── ipai_aiux_chat/            # Chat interface
│   ├── ipai_ask_ai/               # Context AI assistant
│   ├── ipai_ask_ai_chatter/       # Chatter integration
│   ├── ipai_control_room/         # Agent control plane
│   ├── ipai_marketing_ai/         # Marketing-specific AI
│   │
│   ├── # ═══ FINANCE LAYER ═══
│   ├── ipai_finance_ppm/          # Core PPM (consolidated)
│   │   ├── models/
│   │   │   ├── ppm_cluster.py     # Finance clusters
│   │   │   ├── ppm_close.py       # Close tasks (from ppm_closing)
│   │   │   └── ppm_dashboard.py   # Dashboard (from ppm_dashboard)
│   │   └── views/
│   ├── ipai_month_end/            # Month-end orchestration
│   ├── ipai_close_orchestration/  # Close automation rules
│   ├── ipai_bir_compliance/       # BIR tax compliance
│   ├── ipai_expense/              # Expense extensions
│   ├── ipai_ocr_core/             # Unified OCR (consolidated)
│   ├── ipai_finance_close_seed/   # Demo/seed data
│   │
│   ├── # ═══ PPM/PROJECT LAYER ═══
│   ├── ipai_ppm/                  # General PPM (non-finance)
│   ├── ipai_ppm_a1/               # A1-specific extensions
│   ├── ipai_ppm_dashboard_canvas/ # Dashboard canvas
│   ├── ipai_project_suite/        # Project extensions
│   ├── ipai_project_program/      # Program management
│   │
│   ├── # ═══ WORKOS LAYER ═══
│   ├── ipai_workos_core/          # Core framework
│   ├── ipai_workos_db/            # Database layer
│   ├── ipai_workos_views/         # View components
│   ├── ipai_workos_blocks/        # Block system
│   ├── ipai_workos_collab/        # Real-time collab
│   ├── ipai_workos_search/        # Search engine
│   ├── ipai_workos_canvas/        # Canvas/whiteboard
│   ├── ipai_workos_affine/        # Affine integration
│   ├── ipai_workos_templates/     # Page templates
│   │
│   ├── # ═══ INTEGRATIONS LAYER ═══
│   ├── ipai_superset_connector/   # Superset guest token embed
│   ├── ipai_mattermost_connector/ # Mattermost webhooks
│   ├── ipai_n8n_connector/        # n8n workflow triggers
│   ├── ipai_catalog_bridge/       # Data catalog sync
│   │
│   ├── # ═══ INDUSTRY LAYER ═══
│   ├── ipai_industry_marketing_agency/ # Marketing agency vertical
│   ├── ipai_industry_accounting_firm/  # Accounting firm vertical
│   │
│   ├── # ═══ MISC ═══
│   ├── ipai_auth_oauth_internal/  # OAuth extension
│   ├── ipai_srm/                  # Supplier management
│   ├── ipai_equipment/            # Equipment tracking
│   └── ipai_test_fixtures/        # Test data
```

---

## Module Dependency Graph

```
                    ipai_dev_studio_base
                            │
                    ipai_workspace_core
                            │
                    ipai_ce_branding
                     ┌──────┼──────┐
                     │      │      │
              ipai_ai_core  │  ipai_platform_*
                  │         │         │
         ipai_ai_agents     │   ipai_finance_ppm
              │             │         │
    ipai_control_room   ipai_ppm  ipai_month_end
              │             │         │
        ipai_ask_ai    ipai_workos_*  ipai_bir_compliance
```

---

## OCA Integration Strategy

### Tier 1: Must Have (integrate immediately)

```yaml
account-closing:
  version: "18.0"
  modules:
    - account_cutoff_accrual_subscription
    - account_invoice_start_end_dates
  replaces:
    - Custom period closing logic in ipai_month_end

account-financial-reporting:
  version: "18.0"
  modules:
    - account_financial_report
  replaces:
    - Custom report generation

mis-builder:
  version: "18.0"
  modules:
    - mis_builder
    - mis_builder_budget
  replaces:
    - Custom KPI dashboards in ipai_finance_ppm_dashboard
```

### Tier 2: Should Have (integrate in Phase 2)

```yaml
account-reconciliation:
  version: "18.0"
  modules:
    - account_reconciliation_widget

project:
  version: "18.0"
  modules:
    - project_timeline
    - project_status
```

### Tier 3: Nice to Have

```yaml
web:
  version: "18.0"
  modules:
    - web_widget_x2many_2d_matrix
    - web_pivot_computed_measure
```

---

## Thin Extension Pattern

All ipai_* modules should follow this pattern where possible:

```python
# Good: Thin extension
class AccountMove(models.Model):
    _inherit = "account.move"

    # Add fields only
    finance_cluster_id = fields.Many2one('ipai.finance.cluster')
    close_status = fields.Selection([
        ('open', 'Open'),
        ('pending', 'Pending Review'),
        ('closed', 'Closed'),
    ])

    # Add computed fields
    @api.depends('line_ids.balance')
    def _compute_cluster_balance(self):
        ...

# Bad: Creating parallel models
class IpaiAccountMove(models.Model):
    _name = "ipai.account.move"  # Don't do this!
```

---

## Analytics Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        ODOO CE 18                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ account     │  │ project     │  │ hr_expense  │         │
│  │ (extended)  │  │ (extended)  │  │ (extended)  │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                 │
│  ┌──────┴────────────────┴────────────────┴──────┐         │
│  │              ipai_n8n_connector               │         │
│  └──────────────────────┬───────────────────────┘         │
└─────────────────────────┼───────────────────────────────────┘
                          │ Events (JSON)
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                       SUPABASE                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Bronze      │  │ Silver      │  │ Gold        │         │
│  │ (raw)       │→│ (cleaned)   │→│ (aggregated)│         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      SUPERSET                               │
│  ┌─────────────────────────────────────────────────┐       │
│  │  Dashboards (embedded via guest token)          │       │
│  └─────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

**Key Principle:** Odoo stores transactional data. Supabase stores analytical data. Superset visualizes.

---

## Module Naming Convention (Revised)

```
ipai_<domain>_<function>

Domains:
- ai       → AI/ML features
- finance  → Accounting/finance
- ppm      → Project portfolio management
- workos   → WorkOS/Notion clone
- platform → Cross-cutting platform features
- industry → Vertical-specific

Examples:
- ipai_ai_core           ✓ Good
- ipai_finance_ppm       ✓ Good
- ipai_workos_blocks     ✓ Good
- ipai_ipai_something    ✗ Bad (redundant prefix)
- ipai_misc              ✗ Bad (too vague)
```

---

## Migration Checklist

For each module being consolidated:

- [ ] Identify all dependent modules
- [ ] Copy models/views to target module
- [ ] Update depends in target manifest
- [ ] Run `--stop-after-init` verification
- [ ] Update tests
- [ ] Create deprecation notice in old module
- [ ] Remove old module from install scripts
- [ ] CI passes

---

## Verification Commands

```bash
# Count modules
ls -d addons/ipai/*/ | wc -l

# Check for new model definitions (should decrease)
grep -r "_name = " addons/ipai/*/models/ | wc -l

# Check for model extensions (should increase)
grep -r "_inherit = " addons/ipai/*/models/ | wc -l

# Verify no duplicate model names
grep -rh "_name = " addons/ipai/*/models/ | sort | uniq -d

# CI verification
./scripts/ci/run_odoo_tests.sh ipai_finance_ppm
```
