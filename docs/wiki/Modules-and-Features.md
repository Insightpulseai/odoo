# Modules & Features

High-level catalog of IPAI + OCA modules deployed in `odoo-ce`.

## Module Statistics

| Category | Count |
|----------|-------|
| **IPAI Custom Modules** | 87 |
| **OCA Repositories** | 12 |

---

## Core IPAI Modules

### Platform & Workspace

| Module | Description |
|--------|-------------|
| `ipai_workos_core` | Work OS core models and services |
| `ipai_workspace_core` | Core workspace functionality |
| `ipai_dev_studio_base` | Base dependencies for IPAI development |
| `ipai_ce_branding` | CE branding layer |
| `ipai_control_room` | Control room dashboard |
| `ipai_command_center` | Command center for operations |

### AI & Agents

| Module | Description |
|--------|-------------|
| `ipai_ai_core` | AI core framework |
| `ipai_ai_agents` | Agent system |
| `ipai_ai_agents_ui` | Agent system UI |
| `ipai_ai_prompts` | Prompt management |
| `ipai_ai_studio` | AI Studio interface |
| `ipai_ai_audit` | AI audit and compliance |
| `ipai_copilot_ui` | M365 Copilot-inspired assistant UI for Odoo 18 |
| `ipai_ask_ai` | Ask AI assistant |
| `ipai_ask_ai_chatter` | AI in chatter interface |
| `ipai_aiux_chat` | AI UX chat component |

### AI Providers & Connectors

| Module | Description |
|--------|-------------|
| `ipai_ai_connectors` | AI service connectors |
| `ipai_ai_provider_kapa` | Kapa AI provider |
| `ipai_ai_provider_pulser` | Pulser AI provider |
| `ipai_ai_sources_odoo` | Odoo data as AI source |
| `ipai_document_ai` | Document AI processing |

### Finance & PPM

| Module | Description |
|--------|-------------|
| `ipai_finance_ppm` | Finance PPM core |
| `ipai_finance_okr` | OKR + PMBOK + WBS finance governance |
| `ipai_finance_bir_compliance` | BIR tax compliance (Philippines) |
| `ipai_finance_month_end` | Month-end close workflows |
| `ipai_ppm` | Project Portfolio Management |
| `ipai_ppm_monthly_close` | Monthly close for PPM |
| `ipai_expense` | Expense management |
| `ipai_expense_ocr` | OCR for expense receipts |
| `ipai_bir_compliance` | BIR compliance automation |
| `ipai_close_orchestration` | Close orchestration workflows |

### Theme & UI

| Module | Description |
|--------|-------------|
| `ipai_theme_custom` | Configurable theme layer for client brands |
| `ipai_theme_tbwa_backend` | TBWA backend theme |
| `ipai_ui_brand_tokens` | Brand design tokens |
| `ipai_design_system_apps_sdk` | Design system SDK |
| `ipai_chatgpt_sdk_theme` | ChatGPT SDK theme styling |
| `ipai_assets` | Shared assets |

### Platform Features

| Module | Description |
|--------|-------------|
| `ipai_approvals` | Approval workflows |
| `ipai_advisor` | Advisor functionality |
| `ipai_agent_core` | Core agent framework |
| `ipai_catalog_bridge` | Catalog bridge integration |
| `ipai_custom_routes` | Custom API routes |
| `ipai_default_home` | Default home page |
| `ipai_equipment` | Equipment management |
| `ipai_auth_oauth_internal` | Internal OAuth authentication |

### Industry Modules

| Module | Description |
|--------|-------------|
| `ipai_industry_marketing_agency` | Marketing agency extensions |
| `ipai_industry_accounting_firm` | Accounting firm extensions |

### Integration Connectors

| Module | Description |
|--------|-------------|
| `ipai_n8n_connector` | n8n workflow integration |
| `ipai_mattermost_connector` | Mattermost chat integration |
| `ipai_superset_connector` | Superset BI integration |

---

## OCA Module Stacks

Community modules from the Odoo Community Association:

### Accounting

- `account_financial_*` - Financial reporting
- `account_invoice_*` - Invoice management
- `account_reconciliation_*` - Bank reconciliation

### Sales & CRM

- `sale_*` - Sales extensions
- `crm_*` - CRM enhancements

### HR & Payroll

- `hr_*` - HR management
- `payroll_*` - Payroll processing

---

## Module Dependency Hierarchy

```
ipai_dev_studio_base           # Base dependencies (install first)
    └── ipai_workspace_core    # Core workspace functionality
        └── ipai_ce_branding   # CE branding layer
            ├── ipai_ai_core   # AI core framework
            │   ├── ipai_ai_agents     # Agent system
            │   └── ipai_ai_prompts    # Prompt management
            ├── ipai_finance_ppm       # Finance PPM
            │   └── ipai_finance_month_end
            └── [other modules]
```

---

## Module Naming Convention

| Domain | Prefix Pattern | Examples |
|--------|---------------|----------|
| AI/Agents | `ipai_ai_*`, `ipai_agent_*` | `ipai_ai_agents`, `ipai_ai_core` |
| Finance | `ipai_finance_*` | `ipai_finance_ppm`, `ipai_finance_okr` |
| Platform | `ipai_platform_*` | `ipai_platform_workflow`, `ipai_platform_audit` |
| Workspace | `ipai_workspace_*` | `ipai_workspace_core` |
| Studio | `ipai_dev_studio_*`, `ipai_studio_*` | `ipai_dev_studio_base` |
| Industry | `ipai_industry_*` | `ipai_industry_marketing_agency` |
| Theme/UI | `ipai_theme_*`, `ipai_ui_*` | `ipai_theme_custom` |
| Integrations | `ipai_*_connector` | `ipai_n8n_connector` |

---

## Full Module List

All 87 IPAI modules in `addons/ipai/`:

```
ipai_advisor                    ipai_agent_core
ipai_ai_agents                  ipai_ai_agents_ui
ipai_ai_audit                   ipai_ai_connectors
ipai_ai_core                    ipai_ai_prompts
ipai_ai_provider_kapa           ipai_ai_provider_pulser
ipai_ai_sources_odoo            ipai_ai_studio
ipai_aiux_chat                  ipai_approvals
ipai_ask_ai                     ipai_ask_ai_chatter
ipai_assets                     ipai_auth_oauth_internal
ipai_bir_compliance             ipai_catalog_bridge
ipai_ce_branding                ipai_ce_cleaner
ipai_chatgpt_sdk_theme          ipai_clarity_ppm_parity
ipai_close_orchestration        ipai_command_center
ipai_control_room               ipai_copilot_ui
ipai_custom_routes              ipai_default_home
ipai_design_system_apps_sdk     ipai_dev_studio_base
ipai_document_ai                ipai_equipment
ipai_expense                    ipai_expense_ocr
ipai_finance_bir_compliance     ipai_finance_month_end
ipai_finance_okr                ipai_finance_ppm
... (87 total)
```

See **Releases & Changelog** for when each module was introduced or changed.
