# IPAI Module Reduction Plan

**Generated:** 2026-01-12
**Total Modules Analyzed:** 109
**Target Reduction:** 109 → ~70 modules

---

## Executive Summary

The current ipai_* module set has significant redundancy and overlap. This plan:
1. Consolidates overlapping modules
2. Maps to existing Odoo CE/OCA functionality
3. Recommends deletions for truly redundant code
4. Produces a cleaner, more maintainable architecture

---

## Module Classification Legend

| Class | Description | Action |
|-------|-------------|--------|
| **A - Redundant** | Reimplements Odoo/OCA functionality | DELETE or replace with OCA |
| **B - Thin Extension** | Adds fields to existing models only | KEEP minimal |
| **C - Integration** | Bridges external systems | KEEP or simplify |
| **D - Domain Logic** | Custom business logic needed | KEEP and refactor |

---

## 1. FINANCE/ACCOUNTING MODULES (22 → 8)

### Current State: 22 modules with significant overlap

```
ipai_finance_ppm
ipai_finance_ppm_closing
ipai_finance_ppm_dashboard
ipai_finance_ppm_tdi
ipai_finance_ppm_golive
ipai_finance_ppm_umbrella
ipai_finance_bir_compliance
ipai_finance_close_automation
ipai_finance_close_seed
ipai_finance_month_end
ipai_finance_monthly_closing
ipai_finance_closing
ipai_finance_project_hybrid
ipai_month_end
ipai_month_end_closing
ipai_bir_compliance
ipai_bir_tax_compliance
ipai_tbwa_finance
ipai_expense
ipai_expense_ocr
ipai_ocr_expense
ipai_clarity_ppm_parity
```

### Reduction Plan

| Current Module | Class | Action | Replacement/Notes |
|----------------|-------|--------|-------------------|
| `ipai_finance_ppm` | D | **KEEP** | Core PPM - refactor |
| `ipai_finance_ppm_closing` | A | **MERGE** | → ipai_finance_ppm |
| `ipai_finance_ppm_dashboard` | B | **MERGE** | → ipai_finance_ppm |
| `ipai_finance_ppm_tdi` | B | **MERGE** | → ipai_finance_ppm |
| `ipai_finance_ppm_golive` | B | **DELETE** | Migration artifact |
| `ipai_finance_ppm_umbrella` | A | **DELETE** | Meta-package only |
| `ipai_finance_bir_compliance` | D | **MERGE** | → ipai_bir_compliance |
| `ipai_finance_close_automation` | A | **MERGE** | → ipai_close_orchestration |
| `ipai_finance_close_seed` | B | **KEEP** | Demo data only |
| `ipai_finance_month_end` | A | **DELETE** | Duplicate of ipai_month_end |
| `ipai_finance_monthly_closing` | A | **DELETE** | Duplicate |
| `ipai_finance_closing` | A | **DELETE** | Duplicate |
| `ipai_finance_project_hybrid` | B | **MERGE** | → ipai_finance_ppm |
| `ipai_month_end` | D | **KEEP** | Core month-end |
| `ipai_month_end_closing` | A | **DELETE** | TBWA variant, merge |
| `ipai_bir_compliance` | D | **KEEP** | Core BIR compliance |
| `ipai_bir_tax_compliance` | A | **DELETE** | Duplicate |
| `ipai_tbwa_finance` | B | **DELETE** | TBWA-specific, use config |
| `ipai_expense` | B | **KEEP** | Extends hr_expense |
| `ipai_expense_ocr` | A | **MERGE** | → ipai_ocr_core |
| `ipai_ocr_expense` | A | **DELETE** | Duplicate |
| `ipai_clarity_ppm_parity` | B | **DELETE** | Migration artifact |

### Target Architecture (8 modules)

```
ipai_finance_ppm           # Core PPM + closing + dashboard + TDI
ipai_month_end             # Month-end close orchestration
ipai_bir_compliance        # BIR tax forms + mapping
ipai_expense               # Expense extensions
ipai_ocr_core              # Unified OCR gateway
ipai_close_orchestration   # Close automation rules
ipai_finance_close_seed    # Demo/seed data
ipai_finance_project_bridge # (minimal) Project-Finance link
```

### OCA Modules to Adopt

| OCA Module | Purpose | Replaces |
|------------|---------|----------|
| `account-closing` | Period closing | Custom closing logic |
| `account-financial-reporting` | Financial reports | Custom reports |
| `mis-builder` | KPI dashboards | Custom dashboard |
| `account-reconciliation` | Reconciliation | - |
| `l10n_ph` | Philippine localization | - |

---

## 2. AI/AGENTS MODULES (55 → 25)

### Current State: 55 modules with fragmentation

Major groups:
- Core AI framework (ipai_ai_core, ipai_ai_agents, ipai_agent_core)
- AI providers (kapa, pulser)
- AI UI (ipai_aiux_chat, ipai_copilot_ui, ipai_ask_ai*)
- AI studio (ipai_ai_studio, ipai_studio_ai)
- AI sources (ipai_ai_sources_odoo, ipai_ai_connectors)

### Reduction Plan

| Current Module | Class | Action | Notes |
|----------------|-------|--------|-------|
| `ipai_ai_core` | D | **KEEP** | Core framework |
| `ipai_agent_core` | A | **MERGE** | → ipai_ai_core |
| `ipai_ai_agents` | D | **KEEP** | Agent system |
| `ipai_ai_agents_ui` | B | **MERGE** | → ipai_ai_agents |
| `ipai_ai_audit` | B | **MERGE** | → ipai_ai_core |
| `ipai_ai_connectors` | C | **KEEP** | LLM connectors |
| `ipai_ai_prompts` | D | **KEEP** | Prompt management |
| `ipai_ai_provider_kapa` | C | **KEEP** | Kapa+ provider |
| `ipai_ai_provider_pulser` | C | **KEEP** | Pulser provider |
| `ipai_ai_sources_odoo` | B | **MERGE** | → ipai_ai_core |
| `ipai_ai_studio` | A | **DELETE** | Duplicate |
| `ipai_studio_ai` | A | **DELETE** | Duplicate |
| `ipai_aiux_chat` | B | **KEEP** | Chat UI |
| `ipai_copilot_ui` | A | **DELETE** | Use ipai_aiux_chat |
| `ipai_ask_ai` | D | **KEEP** | Decouple from PPM |
| `ipai_ask_ai_chatter` | B | **KEEP** | Chatter integration |
| `ipai_advisor` | B | **MERGE** | → ipai_ask_ai |
| `ipai_document_ai` | A | **MERGE** | → ipai_ocr_core |
| `ipai_skill_api` | B | **MERGE** | → ipai_ai_core |
| `ipai_marketing_ai` | B | **KEEP** | Marketing domain AI |
| `ipai_command_center` | B | **MERGE** | → ipai_control_room |
| `ipai_control_room` | D | **KEEP** | Agent control plane |
| `ipai_master_control` | A | **DELETE** | Use control_room |

### Target Architecture (25 modules)

```
# Core Framework
ipai_ai_core               # Core AI framework + sources + skills + audit
ipai_ai_agents             # Agent system + UI
ipai_ai_prompts            # Prompt templates

# Providers
ipai_ai_connectors         # LLM API connectors
ipai_ai_provider_kapa      # Kapa+ integration
ipai_ai_provider_pulser    # Pulser integration

# UI
ipai_aiux_chat             # Chat interface
ipai_ask_ai                # Context AI assistant (decoupled)
ipai_ask_ai_chatter        # Chatter integration

# Control
ipai_control_room          # Agent control plane + command center

# Domain
ipai_marketing_ai          # Marketing-specific AI
```

---

## 3. THEME/UI MODULES (11 → 3)

### Current State: 11 theme modules

```
ipai_theme_aiux
ipai_theme_fluent2
ipai_theme_tbwa
ipai_theme_tbwa_backend
ipai_web_fluent2
ipai_web_icons_fluent
ipai_web_theme_tbwa
ipai_web_theme_chatgpt
ipai_chatgpt_sdk_theme
ipai_platform_theme
ipai_ui_brand_tokens
```

### Reduction Plan

| Current Module | Class | Action | Notes |
|----------------|-------|--------|-------|
| `ipai_platform_theme` | B | **KEEP** | Base theme |
| `ipai_ui_brand_tokens` | B | **KEEP** | Design tokens |
| `ipai_theme_tbwa` | B | **DELETE** | Use data config |
| `ipai_theme_tbwa_backend` | B | **DELETE** | Use data config |
| `ipai_theme_aiux` | A | **DELETE** | Use platform_theme variant |
| `ipai_theme_fluent2` | A | **DELETE** | Use platform_theme variant |
| `ipai_web_fluent2` | A | **DELETE** | Merge to platform_theme |
| `ipai_web_icons_fluent` | B | **KEEP** | Icon pack only |
| `ipai_web_theme_tbwa` | A | **DELETE** | Duplicate |
| `ipai_web_theme_chatgpt` | A | **DELETE** | Use platform_theme |
| `ipai_chatgpt_sdk_theme` | A | **DELETE** | Merge to platform_theme |

### Target Architecture (3 modules)

```
ipai_platform_theme        # Base theme with variant support
ipai_ui_brand_tokens       # CSS/SCSS design tokens
ipai_web_icons_fluent      # Fluent icon pack
```

**Note:** Theme variants (TBWA, Fluent, ChatGPT) should be **data/config**, not separate modules.

---

## 4. WORKOS MODULES (9 → KEEP ALL)

These are well-designed and modular. No changes needed.

```
ipai_workos_core           # Core framework
ipai_workos_db             # Database layer
ipai_workos_views          # View components
ipai_workos_blocks         # Block system
ipai_workos_collab         # Real-time collab
ipai_workos_search         # Search engine
ipai_workos_canvas         # Canvas/whiteboard
ipai_workos_affine         # Affine integration
ipai_workos_templates      # Page templates
```

---

## 5. INTEGRATION MODULES (5 → 4)

### Current State

```
ipai_superset_connector    # Duplicate in two locations!
ipai_mattermost_connector
ipai_n8n_connector
ipai_focalboard_connector
ipai_integrations
```

### Reduction Plan

| Current Module | Class | Action | Notes |
|----------------|-------|--------|-------|
| `ipai_superset_connector` (nested) | C | **DELETE** | Keep top-level only |
| `ipai_superset_connector` (top-level) | C | **KEEP** | Simplify to guest token |
| `ipai_mattermost_connector` | C | **KEEP** | ChatOps |
| `ipai_n8n_connector` | C | **KEEP** | Workflow automation |
| `ipai_focalboard_connector` | C | **DELETE** | Use native Mattermost |
| `ipai_integrations` | B | **MERGE** | → ipai_n8n_connector |

### Target Architecture (4 modules)

```
ipai_superset_connector    # Superset guest token embed
ipai_mattermost_connector  # Mattermost webhooks/chatops
ipai_n8n_connector         # n8n workflow triggers
ipai_catalog_bridge        # Data catalog sync
```

---

## 6. PLATFORM MODULES (4 → KEEP ALL)

Well-designed mixins:

```
ipai_platform_audit        # Audit trail mixin
ipai_platform_approvals    # Approval workflow mixin
ipai_platform_workflow     # State machine mixin
ipai_platform_permissions  # RBAC mixin
```

---

## 7. PPM/PROJECT MODULES (4 → 3)

### Current State

```
ipai_ppm
ipai_ppm_a1
ipai_ppm_monthly_close
ipai_ppm_dashboard_canvas
```

### Reduction Plan

| Current Module | Class | Action | Notes |
|----------------|-------|--------|-------|
| `ipai_ppm` | D | **KEEP** | Core PPM |
| `ipai_ppm_a1` | B | **KEEP** | A1 specific |
| `ipai_ppm_monthly_close` | A | **MERGE** | → ipai_month_end |
| `ipai_ppm_dashboard_canvas` | B | **KEEP** | Dashboard |

---

## 8. MISCELLANEOUS (DELETE/MERGE)

| Module | Action | Notes |
|--------|--------|-------|
| `ipai_v18_compat` | DELETE | Migration artifact |
| `ipai_ce_cleaner` | DELETE | One-time cleanup |
| `ipai_portal_fix` | MERGE | → ipai_ce_branding |
| `ipai_default_home` | MERGE | → ipai_workspace_core |
| `ipai_auth_oauth_internal` | KEEP | OAuth extension |
| `ipai_custom_routes` | MERGE | → ipai_workspace_core |
| `ipai_assets` | DELETE | Use standard assets |
| `ipai_settings_dashboard` | MERGE | → ipai_workspace_core |
| `ipai_module_gating` | KEEP | Feature flags |
| `ipai_grid_view` | DELETE | Use OCA web-view |
| `ipai_project_gantt` | DELETE | Use OCA project |
| `ipai_srm` | KEEP | Supplier management |
| `ipai_crm_pipeline` | MERGE | → OCA CRM |
| `ipai_test_fixtures` | KEEP | Test data |
| `ipai_tenant_core` | KEEP | Multi-tenant |

---

## Summary: Module Count Reduction

| Domain | Before | After | Reduction |
|--------|--------|-------|-----------|
| Finance/Accounting | 22 | 8 | -14 |
| AI/Agents | 55 | 25 | -30 |
| Theme/UI | 11 | 3 | -8 |
| WorkOS | 9 | 9 | 0 |
| Integrations | 5 | 4 | -1 |
| Platform | 4 | 4 | 0 |
| PPM/Project | 4 | 3 | -1 |
| Misc | 9 | 4 | -5 |

**TOTAL: 109 → 60 modules (-49 modules, 45% reduction)**

---

## OCA Modules to Adopt

Priority OCA repos to integrate:

| OCA Repo | Purpose | Priority |
|----------|---------|----------|
| `account-closing` | Period/year-end closing | HIGH |
| `account-financial-reporting` | Financial statements | HIGH |
| `mis-builder` | Management KPIs | HIGH |
| `account-reconciliation` | Bank reconciliation | MEDIUM |
| `project` | Project management | MEDIUM |
| `web` | UI components | LOW |
| `reporting-engine` | Report generation | LOW |

---

## Implementation Phases

### Phase 1: Quick Wins (Week 1)
- Delete duplicate location `ipai_superset_connector`
- Delete migration artifacts (`ipai_v18_compat`, `ipai_ce_cleaner`)
- Delete obvious duplicates in finance

### Phase 2: Consolidation (Week 2-3)
- Merge month-end modules → `ipai_month_end`
- Merge AI studio duplicates → `ipai_ai_core`
- Merge OCR modules → `ipai_ocr_core`

### Phase 3: Refactoring (Week 4+)
- Decouple `ipai_ask_ai` from `ipai_finance_ppm`
- Convert themes to data-driven variants
- Integrate OCA account-closing

---

## Next Steps

1. **Create GitHub issues** for each module marked DELETE/MERGE
2. **Run module dependency analysis** to identify safe deletion order
3. **Update CI** to track module count as a metric
4. **Create deprecation notices** for modules being removed
