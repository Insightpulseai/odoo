# IPAI Modules Index

| Module | Purpose | Depends | Models | Security | Docs Status | Install Test | Upgrade Test |
|--------|---------|---------|--------|----------|-------------|--------------|--------------|
| [ipai](../addons/ipai/ipai/README.md) | InsightPulse AI namespace for Odoo CE modules | base | 0 | ⚠️ | ✅ | ⏳ | ⏳ |
| [ipai_ask_ai](../addons/ipai/ipai_ask_ai/README.md) | AI-powered conversational assistant for Odoo | base, web, mail, ipai_platform_theme | 11 | ⚠️ | ✅ | ⏳ | ⏳ |
| [ipai_bir_tax_compliance](../addons/ipai/ipai_bir_tax_compliance/README.md) | Philippine BIR tax compliance - 36 eBIRForms support | base, mail, account | 9 | ⚠️ | ✅ | ⏳ | ⏳ |
| [ipai_close_orchestration](../addons/ipai/ipai_close_orchestration/README.md) | Close Cycle Orchestration - Cycles, Tasks, Templates, Checklists, Exceptions, Gates | base, mail | 9 | ✅ | ✅ | ⏳ | ⏳ |
| [ipai_crm_pipeline](../addons/ipai/ipai_crm_pipeline/README.md) | Salesforce-like CRM pipeline experience | crm, mail, ipai_platform_workflow, ipai_platform_theme | 0 | ⚠️ | ✅ | ⏳ | ⏳ |
| [ipai_finance_closing](../addons/ipai/ipai_finance_closing/README.md) | Month-end financial closing task template based on SAP Advanced Financial Closing | project, account | 0 | ⚠️ | ✅ | ⏳ | ⏳ |
| [ipai_finance_monthly_closing](../addons/ipai/ipai_finance_monthly_closing/README.md) | Structured month-end closing and BIR filing on top of Projects (CE/OCA-only). | project | 0 | ✅ | ✅ | ⏳ | ⏳ |
| [ipai_finance_ppm](../addons/ipai/ipai_finance_ppm/README.md) | Finance Project Portfolio Management (Notion Parity). | base, mail, project | 29 | ✅ | ✅ | ⏳ | ⏳ |
| [ipai_finance_ppm_golive](../addons/ipai/ipai_finance_ppm_golive/README.md) | Production go-live checklist for Finance PPM modules | base, project | 3 | ⚠️ | ✅ | ⏳ | ⏳ |
| [ipai_finance_ppm_umbrella](../addons/ipai/ipai_finance_ppm_umbrella/README.md) | Complete seed data for 8-employee Finance SSC with BIR compliance and month-end closing tasks | ipai_finance_ppm, project | 0 | ⚠️ | ✅ | ⏳ | ⏳ |
| [ipai_grid_view](../addons/ipai/ipai_grid_view/README.md) | Advanced grid and list view with sorting, filtering, and bulk actions | base, web, mail | 9 | ⚠️ | ✅ | ⏳ | ⏳ |
| [ipai_month_end](../addons/ipai/ipai_month_end/README.md) | SAP AFC replacement - Month-end closing automation | base, mail, account | 4 | ⚠️ | ✅ | ⏳ | ⏳ |
| [ipai_month_end_closing](../addons/ipai/ipai_month_end_closing/README.md) | SAP AFC-style month-end closing with BIR tax compliance for TBWA Finance | project, hr | 0 | ⚠️ | ✅ | ⏳ | ⏳ |
| [ipai_platform_approvals](../addons/ipai/ipai_platform_approvals/README.md) | Role-based approval chains for IPAI modules | base, mail, ipai_platform_workflow | 2 | ⚠️ | ✅ | ⏳ | ⏳ |
| [ipai_platform_audit](../addons/ipai/ipai_platform_audit/README.md) | Field-level audit trail for IPAI modules | base, mail | 8 | ⚠️ | ✅ | ⏳ | ⏳ |
| [ipai_platform_permissions](../addons/ipai/ipai_platform_permissions/README.md) | Scope-based permission and role management for IPAI modules | base, mail | 2 | ⚠️ | ✅ | ⏳ | ⏳ |
| [ipai_platform_theme](../addons/ipai/ipai_platform_theme/README.md) | Single source of truth for IPAI design tokens and branding | web | 0 | ⚠️ | ✅ | ⏳ | ⏳ |
| [ipai_platform_workflow](../addons/ipai/ipai_platform_workflow/README.md) | Generic workflow state machine for IPAI modules | base, mail | 2 | ⚠️ | ✅ | ⏳ | ⏳ |
| [ipai_ppm_a1](../addons/ipai/ipai_ppm_a1/README.md) | A1 Control Center - Workstreams, Templates, Tasks, Checks + Seed Import/Export | base, mail, project | 11 | ✅ | ✅ | ⏳ | ⏳ |
| [ipai_ppm_monthly_close](../addons/ipai/ipai_ppm_monthly_close/README.md) | Automated monthly financial close scheduling with PPM and Notion workspace parity | base, project, mail, resource | 3 | ✅ | ✅ | ⏳ | ⏳ |
| [ipai_superset_connector](../addons/ipai/ipai_superset_connector/README.md) | Apache Superset integration with managed dataset sync | base, mail, sale, account, stock, hr, project | 16 | ⚠️ | ✅ | ⏳ | ⏳ |
| [ipai_tbwa_finance](../addons/ipai/ipai_tbwa_finance/README.md) | Unified month-end closing + BIR tax compliance for TBWA Philippines | base, mail, account | 7 | ⚠️ | ✅ | ⏳ | ⏳ |
| [ipai_theme_tbwa_backend](../addons/ipai/ipai_theme_tbwa_backend/README.md) | TBWA branding skin - Black + Yellow + IBM Plex | web, ipai_platform_theme | 0 | ⚠️ | ✅ | ⏳ | ⏳ |
| [ipai_workos_affine](../addons/ipai/ipai_workos_affine/README.md) | Installs the full WorkOS AFFiNE-style suite | ipai_workos_core, ipai_workos_blocks, ipai_workos_db, ipai_workos_views, ipai_workos_collab, ipai_workos_search, ipai_workos_templates, ipai_workos_canvas, ipai_platform_permissions, ipai_platform_audit | 0 | ⚠️ | ✅ | ⏳ | ⏳ |
| [ipai_workos_blocks](../addons/ipai/ipai_workos_blocks/README.md) | Notion-style block editor for pages | base, web, ipai_workos_core | 1 | ⚠️ | ✅ | ⏳ | ⏳ |
| [ipai_workos_canvas](../addons/ipai/ipai_workos_canvas/README.md) | Edgeless canvas surface for WorkOS (AFFiNE-style) | base, web, mail | 1 | ⚠️ | ✅ | ⏳ | ⏳ |
| [ipai_workos_collab](../addons/ipai/ipai_workos_collab/README.md) | Comments, mentions, and notifications | base, mail, ipai_workos_core | 4 | ⚠️ | ✅ | ⏳ | ⏳ |
| [ipai_workos_core](../addons/ipai/ipai_workos_core/README.md) | Notion-style Work OS - Core module with workspaces, spaces, and pages | base, web, mail, ipai_platform_permissions, ipai_platform_audit | 4 | ⚠️ | ✅ | ⏳ | ⏳ |
| [ipai_workos_db](../addons/ipai/ipai_workos_db/README.md) | Notion-style databases with typed properties | base, web, ipai_workos_core | 3 | ⚠️ | ✅ | ⏳ | ⏳ |
| [ipai_workos_search](../addons/ipai/ipai_workos_search/README.md) | Global and scoped search for pages and databases | base, web, ipai_workos_core, ipai_workos_blocks, ipai_workos_db | 2 | ⚠️ | ✅ | ⏳ | ⏳ |
| [ipai_workos_templates](../addons/ipai/ipai_workos_templates/README.md) | Page and database templates | base, web, ipai_workos_core, ipai_workos_blocks, ipai_workos_db | 2 | ⚠️ | ✅ | ⏳ | ⏳ |
| [ipai_workos_views](../addons/ipai/ipai_workos_views/README.md) | Table, Kanban, and Calendar views for databases | base, web, ipai_workos_core, ipai_workos_db | 1 | ⚠️ | ✅ | ⏳ | ⏳ |
