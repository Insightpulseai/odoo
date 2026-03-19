# Seed Data Inventory & Deduplication Analysis

> Generated: 2026-03-15
> Scope: Full repository `/Users/tbwa/Documents/GitHub/Insightpulseai/odoo`
> Status: Read-only analysis — no files modified

---

## 1. Complete Inventory

### 1.1 Odoo Module Seed Data (addons/ipai/*)

These are XML/CSV data files loaded by Odoo's module installer via `__manifest__.py`.

| # | File Path | Domain | Format | Records | Type | Module |
|---|-----------|--------|--------|---------|------|--------|
| 1 | `addons/ipai/ipai_finance_close_seed/data/01_stages.xml` | Finance | XML | 6 | Seed | ipai_finance_close_seed |
| 2 | `addons/ipai/ipai_finance_close_seed/data/02_tags.xml` | Finance | XML | 41 | Seed | ipai_finance_close_seed |
| 3 | `addons/ipai/ipai_finance_close_seed/data/03_partners_employees.xml` | Finance/HR | XML | 19 | Seed | ipai_finance_close_seed |
| 4 | `addons/ipai/ipai_finance_close_seed/data/04_projects.xml` | Finance | XML | 2 | Seed | ipai_finance_close_seed |
| 5 | `addons/ipai/ipai_finance_close_seed/data/05_milestones.xml` | Finance | XML | 11 | Seed | ipai_finance_close_seed |
| 6 | `addons/ipai/ipai_finance_close_seed/data/06_tasks_month_end.xml` | Finance | XML | 39 | Seed | ipai_finance_close_seed |
| 7 | `addons/ipai/ipai_finance_close_seed/data/07_tasks_bir_tax.xml` | Finance/BIR | XML | 33 | Seed | ipai_finance_close_seed |
| 8 | `addons/ipai/ipai_finance_close_seed/data/tasks_month_end.xml` | Finance | XML | 36 | Seed | ipai_finance_close_seed |
| 9 | `addons/ipai/ipai_finance_close_seed/data/tasks_bir.xml` | Finance/BIR | XML | 27 | Seed | ipai_finance_close_seed |
| 10 | `addons/ipai/ipai_finance_workflow/data/finance_task_stages.xml` | Finance | XML | 5 | Seed | ipai_finance_workflow |
| 11 | `addons/ipai/ipai_finance_workflow/data/finance_projects.xml` | Finance | XML | 2 | Seed | ipai_finance_workflow |
| 12 | `addons/ipai/ipai_finance_workflow/data/finance_ppm_tasks.xml` | Finance | XML | 20 | Seed | ipai_finance_workflow |
| 13 | `addons/ipai/ipai_finance_workflow/data/finance_team.xml` | Finance/HR | XML | 11 | Seed | ipai_finance_workflow |
| 14 | `addons/ipai/ipai_finance_workflow/data/finance_roles.xml` | Finance | XML | 5 | Seed | ipai_finance_workflow |
| 15 | `addons/ipai/ipai_project_seed/data/project_seed.xml` | Project | XML | 2 | Seed | ipai_project_seed |
| 16 | `addons/ipai/ipai_project_seed/data/project_stage_seed.xml` | Project | XML | 4 | Seed | ipai_project_seed |
| 17 | `addons/ipai/ipai_project_seed/data/project_task_seed.xml` | Project | XML | 3 | Seed | ipai_project_seed |
| 18 | `addons/ipai/ipai_project_seed/data/project_milestone_seed.xml` | Project | XML | 2 | Seed | ipai_project_seed |
| 19 | `addons/ipai/ipai_helpdesk/data/helpdesk_stage_data.xml` | Helpdesk | XML | 6 | Seed | ipai_helpdesk |
| 20 | `addons/ipai/ipai_bir_tax_compliance/data/bir_tax_rates.xml` | BIR | XML | 1 | Reference | ipai_bir_tax_compliance |
| 21 | `addons/ipai/ipai_bir_tax_compliance/data/bir_filing_deadlines.xml` | BIR | XML | ~15 | Reference | ipai_bir_tax_compliance |
| 22 | `addons/ipai/ipai_bir_tax_compliance/data/ir_cron.xml` | BIR | XML | 2 | Config | ipai_bir_tax_compliance |
| 23 | `addons/ipai/ipai_ai_copilot/data/copilot_tools.xml` | AI | XML | 18 | Seed | ipai_ai_copilot |
| 24 | `addons/ipai/ipai_ai_copilot/data/copilot_cron.xml` | AI | XML | 1 | Config | ipai_ai_copilot |
| 25 | `addons/ipai/ipai_ai_copilot/data/mail_channel_ai.xml` | AI | XML | 1 | Seed | ipai_ai_copilot |
| 26 | `addons/ipai/ipai_ai_copilot/data/res_partner_bot.xml` | AI | XML | 1 | Seed | ipai_ai_copilot |
| 27 | `addons/ipai/ipai_workspace_core/data/copilot_tools.xml` | AI | XML | 3 | Seed | ipai_workspace_core |
| 28 | `addons/ipai/ipai_hr_expense_liquidation/data/copilot_tools.xml` | AI/Finance | XML | 4 | Seed | ipai_hr_expense_liquidation |
| 29 | `addons/ipai/ipai_ai_tools/data/ai_tools_data.xml` | AI | XML | 8 | Seed | ipai_ai_tools |
| 30 | `addons/ipai/ipai_ai_prompts/data/ai_prompt_data.xml` | AI | XML | 10 | Seed | ipai_ai_prompts |
| 31 | `addons/ipai/ipai_ai_agent_builder/data/ai_agent_data.xml` | AI | XML | 5 | Seed | ipai_ai_agent_builder |
| 32 | `addons/ipai/ipai_agent/data/tools_seed.xml` | AI | XML | 1 | Seed | ipai_agent |
| 33 | `addons/ipai/ipai_agent/data/ir_cron.xml` | AI | XML | 1 | Config | ipai_agent |
| 34 | `addons/ipai/ipai_agent/data/ir_sequence.xml` | AI | XML | 1 | Config | ipai_agent |
| 35 | `addons/ipai/ipai_agent/data/activity_types.xml` | AI | XML | 3 | Seed | ipai_agent |
| 36 | `addons/ipai/ipai_agent_skills/data/skill_categories.xml` | AI | XML | 21 | Seed | ipai_agent_skills |
| 37 | `addons/ipai/ipai_mailgun_smtp/data/ir_mail_server.xml` | Mail | XML | 1 | Config | ipai_mailgun_smtp |
| 38 | `addons/ipai/ipai_zoho_mail/data/mail_server.xml` | Mail | XML | 1 | Config | ipai_zoho_mail |
| 39 | `addons/ipai/ipai_zoho_mail/data/fetchmail_server.xml` | Mail | XML | 1 | Config | ipai_zoho_mail |
| 40 | `addons/ipai/ipai_zoho_mail/data/config_params.xml` | Mail | XML | ~3 | Config | ipai_zoho_mail |
| 41 | `addons/ipai/ipai_zoho_mail_api/data/ir_mail_server.xml` | Mail | XML | 1 | Config | ipai_zoho_mail_api |
| 42 | `addons/ipai/ipai_enterprise_bridge/data/mail_server.xml` | Mail | XML | 2 | Config | ipai_enterprise_bridge |
| 43 | `addons/ipai/ipai_enterprise_bridge/data/oauth_providers.xml` | Auth | XML | 2 | Seed | ipai_enterprise_bridge |
| 44 | `addons/ipai/ipai_enterprise_bridge/data/groups.xml` | Auth | XML | 1 | Seed | ipai_enterprise_bridge |
| 45 | `addons/ipai/ipai_enterprise_bridge/data/sequences.xml` | Platform | XML | 2 | Config | ipai_enterprise_bridge |
| 46 | `addons/ipai/ipai_enterprise_bridge/data/scheduled_actions.xml` | Platform | XML | 1 | Config | ipai_enterprise_bridge |
| 47 | `addons/ipai/ipai_enterprise_bridge/data/enterprise_bridge_data.xml` | Platform | XML | 8 | Seed | ipai_enterprise_bridge |
| 48 | `addons/ipai/ipai_enterprise_bridge/demo/demo_data.xml` | Platform | XML | ~6 | Demo | ipai_enterprise_bridge |
| 49 | `addons/ipai/ipai_vertical_retail/data/retail_product_categories.xml` | Retail | XML | 13 | Seed | ipai_vertical_retail |
| 50 | `addons/ipai/ipai_vertical_retail/data/retail_store_tags.xml` | Retail | XML | 13 | Seed | ipai_vertical_retail |
| 51 | `addons/ipai/ipai_vertical_retail/data/retail_pricelists.xml` | Retail | XML | 4 | Seed | ipai_vertical_retail |
| 52 | `addons/ipai/ipai_vertical_retail/data/retail_demo_stores.xml` | Retail | XML | 6 | Demo | ipai_vertical_retail |
| 53 | `addons/ipai/ipai_vertical_media/data/media_project_templates.xml` | Media | XML | 4 | Seed | ipai_vertical_media |
| 54 | `addons/ipai/ipai_vertical_media/data/media_campaign_stages.xml` | Media | XML | 17 | Seed | ipai_vertical_media |
| 55 | `addons/ipai/ipai_vertical_media/data/media_budget_categories.xml` | Media | XML | 13 | Seed | ipai_vertical_media |
| 56 | `addons/ipai/ipai_platform_api/data/platform_feature_data.xml` | Platform | XML | 6 | Seed | ipai_platform_api |
| 57 | `addons/ipai/ipai_website_coming_soon/data/website_page.xml` | Website | XML | 1 | Seed | ipai_website_coming_soon |
| 58 | `addons/ipai/ipai_ui_brand_tokens/data/token_defaults.xml` | UI | XML | 1 | Seed | ipai_ui_brand_tokens |
| 59 | `addons/ipai/ipai_company_scope_omc/data/company_marker.xml` | Platform | XML | ~2 | Seed | ipai_company_scope_omc |
| 60 | `addons/ipai/ipai_auth_oidc/data/auth_provider_data.xml` | Auth | XML | 2 | Seed | ipai_auth_oidc |
| 61 | `addons/ipai/ipai_ai_oca_bridge/data/ai_bridge_supabase.xml` | AI | XML | 1 | Config | ipai_ai_oca_bridge |
| 62 | `addons/ipai/ipai_ai_platform/data/config_parameters.xml` | AI | XML | 4 | Config | ipai_ai_platform |
| 63 | `addons/ipai/ipai_ai_widget/data/presets.xml` | AI | XML | 4 | Seed | ipai_ai_widget |
| 64 | `addons/ipai/ipai_finance_ppm/data/ir_cron_ppm_sync.xml` | Finance | XML | 1 | Config | ipai_finance_ppm |
| 65 | `addons/ipai/ipai_bir_notifications/data/cron_jobs.xml` | BIR | XML | 2 | Config | ipai_bir_notifications |
| 66 | `addons/ipai/ipai_bir_notifications/data/mail_templates.xml` | BIR | XML | 2 | Seed | ipai_bir_notifications |
| 67 | `addons/ipai/ipai_bir_plane_sync/data/ir_config_parameter.xml` | BIR | XML | 4 | Config | ipai_bir_plane_sync |
| 68 | `addons/ipai/ipai_ops_connector/data/ir_cron_ops_dispatch.xml` | Ops | XML | 1 | Config | ipai_ops_connector |
| 69 | `addons/ipai/ipai_pulser_connector/data/ir_cron.xml` | Ops | XML | 1 | Config | ipai_pulser_connector |
| 70 | `addons/ipai/ipai_google_workspace/data/config_params.xml` | Integration | XML | ~3 | Config | ipai_google_workspace |
| 71 | `addons/ipai/ipai_odoo_copilot/data/copilot_partner_data.xml` | AI | XML | 1 | Seed | ipai_odoo_copilot |
| 72 | `addons/ipai/ipai_odoo_copilot/data/ir_cron.xml` | AI | XML | 1 | Config | ipai_odoo_copilot |
| 73 | `addons/ipai/ipai_odoo_copilot/data/ir_actions_server.xml` | AI | XML | 1 | Config | ipai_odoo_copilot |
| 74 | `addons/ipai/ipai_odoo_copilot/data/ir_config_parameter.xml` | AI | XML | 8 | Config | ipai_odoo_copilot |
| 75 | `addons/ipai/ipai_hr_expense_liquidation/data/sequence.xml` | Finance | XML | 1 | Config | ipai_hr_expense_liquidation |
| 76 | `addons/ipai/ipai_hr_expense_liquidation/data/cron_monitoring.xml` | Finance | XML | 1 | Config | ipai_hr_expense_liquidation |

**Subtotal: ~488 XML records across 76 data files in 35 modules.**

### 1.2 Supabase SQL Seeds (supabase/seeds/)

| # | File Path | Domain | Format | Approx Records | Type | Notes |
|---|-----------|--------|--------|----------------|------|-------|
| 1 | `supabase/seeds/001_hr_seed.sql` | HR | SQL | ~70 | Seed | Departments, job positions, employees |
| 2 | `supabase/seeds/002_finance_seed.sql` | Finance | SQL | ~40 | Seed | **DEPRECATED** — marked 2026-03-09 |
| 3 | `supabase/seeds/003_odoo_dict_seed.sql` | Platform | SQL | ~50 | Reference | Odoo data dictionary for finance PPM fields |

### 1.3 Supabase Consolidated Seeds (supabase/seed/)

| # | File Path | Domain | Format | Type |
|---|-----------|--------|--------|------|
| 1 | `supabase/seed/001_saas_feature_seed.sql` | Platform | SQL | Seed |
| 2 | `supabase/seed/9003_ai_rag/9003_ai_rag_agent_registry_seed.sql` | AI | SQL | Seed |
| 3 | `supabase/seed/9004_analytics/9004_analytics_kpi_registry_seed.sql` | Analytics | SQL | Seed |
| 4 | `supabase/seed/9004_analytics/9004_analytics_superset_dashboard_seed.sql` | Analytics | SQL | Seed |
| 5 | `supabase/seed/9007_skills/9007_skills_certification_seed.sql` | Skills | SQL | Seed |
| 6 | `supabase/seed/9008_drawio_skills/9008_drawio_certification_seed.sql` | Skills | SQL | Seed |

### 1.4 Supabase YAML Workstream Seeds (supabase/seeds/workstreams/)

| # | Workstream | Files | Domain | Type |
|---|------------|-------|--------|------|
| 1 | `afc_financial_close/` | 7 YAML files (00-90) | Finance | Seed — templates, tasks, checklists, KPIs, RACI, Odoo mapping |
| 2 | `project_stack/` | 9 YAML files + 8 CSVs + 1 XLSX | Project | Seed — partners, analytic accounts, products, projects, tags, stages, tasks, timesheets |
| 3 | `stc_tax_compliance/` | 6 YAML files | BIR | Seed — worklist types, compliance checks, scenarios, PH localization |

### 1.5 CSV/JSON Data Files (supabase/data/)

| # | File Path | Domain | Format | Records | Type |
|---|-----------|--------|--------|---------|------|
| 1 | `supabase/data/finance_seed/01_project.tags.csv` | Finance | CSV | 36 | Seed |
| 2 | `supabase/data/finance_seed/02_project.project.csv` | Finance | CSV | 2 | Seed |
| 3 | `supabase/data/finance_seed/03_project.task.month_end.csv` | Finance | CSV | 36 | Seed |
| 4 | `supabase/data/finance_seed/04_project.task.bir_tax.csv` | Finance | CSV | 33 | Seed |
| 5 | `supabase/data/finance_seed/05_expense_categories.csv` | Finance | CSV | 18 | Seed |
| 6 | `supabase/data/finance_seed/06_approval_thresholds.csv` | Finance | CSV | 11 | Reference |
| 7 | `supabase/data/month_end_closing_tasks.csv` | Finance | CSV | 37 | Seed |
| 8 | `supabase/data/month_end_tasks.csv` | Finance | CSV | 36 | Seed |
| 9 | `supabase/data/bir_december_2025_seed.xml` | BIR | XML | 10 | Seed |
| 10 | `supabase/data/bir_calendar_2026.json` | BIR | JSON | ~50 | Reference |
| 11 | `supabase/data/employee_directory.json` | HR | JSON | ~10 | Reference |
| 12 | `supabase/data/user_map.csv` | HR | CSV | ~10 | Reference |
| 13 | `supabase/data/seed/finance_ppm/tbwa_smp/*.csv` | Finance | CSV | 6 files | Seed |

### 1.6 Root-Level and Standalone Seed Files

| # | File Path | Domain | Format | Type |
|---|-----------|--------|--------|------|
| 1 | `ipai_finance_closing_seed.json` | BIR | JSON | Seed — BIR form schedules |
| 2 | `docs/kb/graph_seed.json` | Platform | JSON | Reference — knowledge graph |
| 3 | `scripts/odoo/seed_prod_users.py` | HR/Auth | Python | Seed script — companies + users |
| 4 | `scripts/benchmark/seed_personas.py` | Testing | Python | Demo — benchmark personas |
| 5 | `scripts/finance_ppm_seed_audit.py` | Finance | Python | Audit script (not seed data) |

### 1.7 Python Post-Init Hooks Creating Records

| # | File Path | Domain | Records Created | Type |
|---|-----------|--------|-----------------|------|
| 1 | `addons/ipai/ipai_system_config/hooks.py` | Mail/Config | `ir.config_parameter` + `ir.mail_server` (SSOT SMTP) | Config |
| 2 | `addons/ipai/ipai_enterprise_bridge/hooks.py` | Platform | `ir.config_parameter` (7 defaults) | Config |
| 3 | `addons/ipai/ipai_website_coming_soon/hooks.py` | Website | Website page setup | Config |

### 1.8 ops-platform Copies (Exact Duplicates of supabase/)

| # | File Path | Duplicate Of |
|---|-----------|-------------|
| 1 | `ops-platform/supabase/seeds/001_hr_seed.sql` | `supabase/seeds/001_hr_seed.sql` (identical) |
| 2 | `ops-platform/supabase/seeds/002_finance_seed.sql` | `supabase/seeds/002_finance_seed.sql` (pre-deprecation copy) |
| 3 | `ops-platform/supabase/seeds/003_odoo_dict_seed.sql` | `supabase/seeds/003_odoo_dict_seed.sql` (identical) |
| 4 | `ops-platform/supabase/seed/001_saas_feature_seed.sql` | `supabase/seed/001_saas_feature_seed.sql` |
| 5 | `ops-platform/supabase/seed/9003_ai_rag/*` | `supabase/seed/9003_ai_rag/*` |
| 6 | `ops-platform/supabase/seed/9004_analytics/*` | `supabase/seed/9004_analytics/*` |
| 7 | `ops-platform/supabase/seed/9007_skills/*` | `supabase/seed/9007_skills/*` |
| 8 | `ops-platform/supabase/seed/9008_drawio_skills/*` | `supabase/seed/9008_drawio_skills/*` |

### 1.9 Nested `odoo/` Directory Copies (Exact Duplicates)

| # | File Path | Duplicate Of |
|---|-----------|-------------|
| 1 | `odoo/ipai_finance_closing_seed.json` | `ipai_finance_closing_seed.json` (identical) |
| 2 | `odoo/addons/ipai/ipai_agent/data/tools_seed.xml` | `addons/ipai/ipai_agent/data/tools_seed.xml` |
| 3 | `odoo/docs/kb/graph_seed.json` | `docs/kb/graph_seed.json` |
| 4 | `odoo/supabase/seeds/002_finance_seed.sql` | `supabase/seeds/002_finance_seed.sql` |

### 1.10 Archive Directory (Inactive but Present)

| # | File Path | Domain | Notes |
|---|-----------|--------|-------|
| 1 | `archive/addons/omc_finance_ppm/data/logframe_seed.xml` | Finance | Legacy PPM seed (pre-ipai naming) |
| 2 | `archive/addons/omc_finance_ppm/data/ppm_seed_finance_wbs_2025_2026.xml` | Finance | Legacy WBS seed |
| 3 | `archive/addons/omc_finance_ppm/data/ppm_seed_users.xml` | Finance/HR | Legacy user seed |
| 4 | `archive/addons/omc_finance_ppm/data/ppm_seed_schema.json` | Finance | Legacy schema definition |
| 5 | `archive/addons/ipai_docs_project/data/workspace_seed.xml` | Docs | Legacy workspace seed |
| 6 | `archive/root/scripts/seed_*.py` (18 files) | Various | Legacy seed scripts |
| 7 | `archive/root/scripts/kb/seed_*.sql` (3 files) | KB | Duplicate of `agents/scripts/kb/` |

### 1.11 Platform Tools (TypeScript Seed Scripts)

| # | File Path | Domain | Format | Type |
|---|-----------|--------|--------|------|
| 1 | `platform/tools/seed_all.ts` | Platform | TS | Orchestrator |
| 2 | `platform/tools/seed_ppm.ts` | Finance | TS | Seed script for Supabase |
| 3 | `platform/tools/seed_te_cheq.ts` | QA | TS | Seed script for Supabase |
| 4 | `platform/tools/seed_retail_intel.ts` | Retail | TS | Seed script for Supabase |
| 5 | `platform/tools/seed_doc_ocr.ts` | Documents | TS | Seed script for Supabase |

### 1.12 KB Agent Seeds

| # | File Path | Domain | Format | Type |
|---|-----------|--------|--------|------|
| 1 | `agents/scripts/kb/seed_odoo_catalog.sql` | KB | SQL | Reference — Odoo docs catalog |
| 2 | `agents/scripts/kb/seed_sap_catalog.sql` | KB | SQL | Reference — SAP docs catalog |
| 3 | `agents/scripts/kb/seed_oca_catalog.sql` | KB | SQL | Reference — OCA docs catalog |

---

## 2. Duplicate Detection Results

### 2.1 CRITICAL: Finance Month-End Close Tasks (Triple Duplication)

**Severity: HIGH** — Three separate sources seed the same month-end closing tasks into `project.task`:

| Source | Location | Records | Stage Model | Project Name |
|--------|----------|---------|-------------|-------------|
| A | `ipai_finance_close_seed/data/06_tasks_month_end.xml` | 39 tasks | `stage_todo` etc. (6 stages) | "Finance PPM - Month-End Close" |
| B | `ipai_finance_close_seed/data/tasks_month_end.xml` | 36 tasks | `ipai_stage_preparation` etc. | `project_month_end_template` |
| C | `ipai_finance_workflow/data/finance_ppm_tasks.xml` | 20 tasks (ME01-ME08 + BIR01-BIR12) | `fin_stage_prep` etc. (5 stages) | "FIN - Month-End Close" |

**Analysis**: All three seed the same real-world finance closing tasks (payroll, tax provisions, rent, accruals, etc.) but with:
- Different XML IDs (`task_me_01` vs `task_close_01_process_and_record_payroll_fi` vs `fin_ppm_me_payroll_personnel`)
- Different stage references (3 different stage sets)
- Different project references (3 different project records)
- Different field sets (C has `finance_workflow_type`, `preparer_id`, `reviewer_id`, `approver_id`)

### 2.2 CRITICAL: Finance Project Stages (Triple Duplication)

| Source | Location | Records | Stage Names |
|--------|----------|---------|-------------|
| A | `ipai_finance_close_seed/data/01_stages.xml` | 6 | To Do, In Preparation, Under Review, Pending Approval, Done, Cancelled |
| B | `ipai_finance_workflow/data/finance_task_stages.xml` | 5 | Preparation, Review, Approval, Execute/File/Pay, Closed/Archived |
| C | `ipai_project_seed/data/project_stage_seed.xml` | 4 | Backlog, In Progress, Review, Done |

All seed `project.task.type` records. Source A and B are finance-specific (near duplicates with different naming). Source C is generic project stages.

### 2.3 CRITICAL: Finance Projects (Double Duplication)

| Source | Location | Projects |
|--------|----------|----------|
| A | `ipai_finance_close_seed/data/04_projects.xml` | "Finance PPM - Month-End Close" + "Finance PPM - BIR Tax Filing" |
| B | `ipai_finance_workflow/data/finance_projects.xml` | "FIN - Month-End Close" + "FIN - BIR Returns" |

Both seed 2 `project.project` records for the same real-world projects (month-end close + BIR tax filing) with different names and different stage references.

### 2.4 CRITICAL: BIR Tax Tasks (Triple Duplication)

| Source | Location | Records |
|--------|----------|---------|
| A | `ipai_finance_close_seed/data/07_tasks_bir_tax.xml` | 33 tasks |
| B | `ipai_finance_close_seed/data/tasks_bir.xml` | 27 tasks |
| C | `supabase/data/bir_december_2025_seed.xml` | 10 tasks |

Sources A and B are within the same module with overlapping BIR task data. Source C is a period-specific seed for December 2025.

### 2.5 HIGH: Mail Server Configuration (Quadruple Duplication)

Four modules seed `ir.mail_server` records:

| Source | Module | Server Name | Host | Status |
|--------|--------|-------------|------|--------|
| A | `ipai_mailgun_smtp` | "Mailgun SMTP (mg.insightpulseai.com)" | smtp.mailgun.org:2525 | **DEPRECATED** (Mailgun is deprecated per CLAUDE.md) |
| B | `ipai_zoho_mail` | "Zoho SMTP (Prod)" | smtppro.zoho.com:587 | Active — canonical |
| C | `ipai_zoho_mail_api` | "Zoho Mail API" | mail.zoho.com:465 | Active — API-based |
| D | `ipai_enterprise_bridge` | "Zoho Mail SMTP" | smtp.zoho.com:587 | Inactive (active=False) |
| E | `ipai_system_config` (hook) | "SSOT SMTP" | From env vars | Active — env-driven |

All five create `ir.mail_server` records. If all modules are installed, up to 5 mail servers would exist with `sequence=1`, causing unpredictable mail routing.

### 2.6 HIGH: Supabase Seeds — Exact Copies (ops-platform/ mirror)

The `ops-platform/supabase/` directory contains exact copies of files in `supabase/`:
- `seeds/001_hr_seed.sql` — **identical**
- `seeds/003_odoo_dict_seed.sql` — **identical**
- `seeds/002_finance_seed.sql` — identical except supabase/ copy has deprecation header
- All `seed/` subdirectories — copies

### 2.7 HIGH: Nested odoo/ Directory

The `odoo/` directory at repo root is an older snapshot of the entire repo, containing stale copies of:
- `odoo/ipai_finance_closing_seed.json` (identical to root)
- `odoo/addons/ipai/...` (stale module copies)
- `odoo/supabase/seeds/...` (stale seed copies)

### 2.8 MEDIUM: Finance Seed CSV vs XML vs YAML (Semantic Triplication)

The same finance closing data exists in three formats for different consumption targets:

| Format | Location | Target |
|--------|----------|--------|
| XML | `addons/ipai/ipai_finance_close_seed/data/*.xml` | Odoo module installer |
| CSV | `supabase/data/finance_seed/*.csv` | Odoo XML-RPC import script |
| YAML | `supabase/seeds/workstreams/afc_financial_close/*.yaml` | Supabase/platform seed |

All three encode the same month-end closing task definitions. The YAML version is the most structured (includes SAP AFC codes, RACI, due offsets). The XML version is the most Odoo-native. The CSV version is the most import-friendly.

### 2.9 MEDIUM: Copilot Tools Spread Across Modules

Three modules seed `ipai.copilot.tool` records:
- `ipai_ai_copilot/data/copilot_tools.xml` — 18 tools (primary)
- `ipai_hr_expense_liquidation/data/copilot_tools.xml` — 4 tools (domain-specific)
- `ipai_workspace_core/data/copilot_tools.xml` — 3 tools (domain-specific)

**Not a true duplicate** — this is the correct Odoo pattern (each module registers its own tools). Noted for completeness.

### 2.10 MEDIUM: HR/Employee Data (Cross-System Duplication)

| Source | Location | Target System | Records |
|--------|----------|---------------|---------|
| A | `supabase/seeds/001_hr_seed.sql` | Supabase (custom HR tables) | ~70 |
| B | `ipai_finance_close_seed/data/03_partners_employees.xml` | Odoo (`res.partner`) | 19 |
| C | `ipai_finance_workflow/data/finance_team.xml` | Odoo (`res.users`) | 11 |
| D | `supabase/data/employee_directory.json` | Reference | ~10 |
| E | `scripts/odoo/seed_prod_users.py` | Odoo (`res.company`, `res.users`) | ~7 |

Different systems, but the same organizational data (finance team members) is encoded in 5 different files.

### 2.11 LOW: Month-End Tasks in CSV (supabase/data/)

Two CSV files with very similar content:
- `supabase/data/month_end_closing_tasks.csv` (38 lines)
- `supabase/data/month_end_tasks.csv` (37 lines)

Both contain month-end closing tasks with Owner/Reviewer/Approver columns. Near-duplicate content.

---

## 3. Canonical Source Recommendation

### Per-Domain SSOT Assignment

| Domain | Canonical Source | Format | Rationale |
|--------|-----------------|--------|-----------|
| **Finance Stages** | `ipai_finance_workflow/data/finance_task_stages.xml` | XML | Has `finance_stage_code` for programmatic access; 5-stage lifecycle is cleaner than 6 |
| **Finance Projects** | `ipai_finance_workflow/data/finance_projects.xml` | XML | Richer descriptions, explicit stage refs |
| **Finance Month-End Tasks** | `ipai_finance_workflow/data/finance_ppm_tasks.xml` | XML | Has preparer/reviewer/approver assignments + structured fields |
| **Finance BIR Tasks** | `ipai_finance_close_seed/data/07_tasks_bir_tax.xml` | XML | Most complete (33 tasks vs 27) |
| **Finance Team/Users** | `ipai_finance_workflow/data/finance_team.xml` | XML | References Odoo `res.users` properly |
| **Finance CSV Import** | `supabase/data/finance_seed/*.csv` | CSV | For XML-RPC bulk import scenarios |
| **Finance YAML (cross-system)** | `supabase/seeds/workstreams/afc_financial_close/` | YAML | For Supabase platform integration |
| **Mail Server** | `ipai_zoho_mail/data/mail_server.xml` | XML | Canonical per SSOT rules (Zoho SMTP) |
| **Project Stages (generic)** | `ipai_project_seed/data/project_stage_seed.xml` | XML | For non-finance projects |
| **BIR Reference Data** | `ipai_bir_tax_compliance/data/` | XML | Filing deadlines, tax rates |
| **HR Supabase** | `supabase/seeds/001_hr_seed.sql` | SQL | For Supabase HR tables only |
| **Odoo Users** | `scripts/odoo/seed_prod_users.py` | Python | For production user setup |
| **KB Catalogs** | `agents/scripts/kb/seed_*.sql` | SQL | For knowledge base |

---

## 4. Consolidation Actions

### 4.1 Delete (Safe to Remove)

| Action | File(s) | Reason |
|--------|---------|--------|
| **DELETE** | `ops-platform/supabase/seeds/001_hr_seed.sql` | Exact copy of `supabase/seeds/001_hr_seed.sql` |
| **DELETE** | `ops-platform/supabase/seeds/002_finance_seed.sql` | Stale copy (missing deprecation header) |
| **DELETE** | `ops-platform/supabase/seeds/003_odoo_dict_seed.sql` | Exact copy of `supabase/seeds/003_odoo_dict_seed.sql` |
| **DELETE** | `ops-platform/supabase/seed/` (all) | Exact copies of `supabase/seed/` |
| **DELETE** | `odoo/ipai_finance_closing_seed.json` | Exact copy of root `ipai_finance_closing_seed.json` |
| **DELETE** | `odoo/supabase/seeds/002_finance_seed.sql` | Stale copy |
| **DELETE** | `odoo/addons/ipai/ipai_agent/data/tools_seed.xml` | Stale copy of active module |
| **DELETE** | `odoo/docs/kb/graph_seed.json` | Stale copy |
| **DELETE** | `supabase/data/month_end_tasks.csv` | Near-duplicate of `month_end_closing_tasks.csv` |
| **DELETE** | `addons/ipai/ipai_mailgun_smtp/` (entire module) | Mailgun is deprecated; module seeds a deprecated mail server |

### 4.2 Merge (Consolidate Into Canonical Source)

| Action | Source (Remove) | Target (Keep) | Notes |
|--------|-----------------|---------------|-------|
| **MERGE** | `ipai_finance_close_seed/data/06_tasks_month_end.xml` | `ipai_finance_workflow/data/finance_ppm_tasks.xml` | Merge any missing task details into the workflow module |
| **MERGE** | `ipai_finance_close_seed/data/tasks_month_end.xml` | `ipai_finance_workflow/data/finance_ppm_tasks.xml` | Same as above — older format |
| **MERGE** | `ipai_finance_close_seed/data/01_stages.xml` | `ipai_finance_workflow/data/finance_task_stages.xml` | Keep the 5-stage workflow lifecycle |
| **MERGE** | `ipai_finance_close_seed/data/04_projects.xml` | `ipai_finance_workflow/data/finance_projects.xml` | Keep the richer project definitions |
| **MERGE** | `ipai_finance_close_seed/data/tasks_bir.xml` | `ipai_finance_close_seed/data/07_tasks_bir_tax.xml` | Deduplicate within same module |
| **MERGE** | `ipai_enterprise_bridge/data/mail_server.xml` | `ipai_zoho_mail/data/mail_server.xml` | Remove inactive duplicate from bridge |

### 4.3 Deprecate (Mark but Keep for Backward Compatibility)

| Action | File | Reason |
|--------|------|--------|
| **DEPRECATE** | `supabase/seeds/002_finance_seed.sql` | Already has deprecation header; keep for Supabase-only backward compat |
| **DEPRECATE** | `ipai_finance_closing_seed.json` (root) | BIR schedule data — consider migrating to `ipai_bir_tax_compliance/data/` |
| **DEPRECATE** | `supabase/data/month_end_closing_tasks.csv` | Raw task list; canonical version is in `finance_seed/` |

### 4.4 Keep As-Is (No Action Needed)

| File | Reason |
|------|--------|
| `ipai_ai_copilot/data/copilot_tools.xml` | Correct Odoo pattern — module registers its own tools |
| `ipai_workspace_core/data/copilot_tools.xml` | Same — domain-specific tool registration |
| `ipai_hr_expense_liquidation/data/copilot_tools.xml` | Same |
| `supabase/seed/9000-9008` directories | Supabase-specific seeds, no Odoo overlap |
| `agents/scripts/kb/seed_*.sql` | KB-specific, no overlap with Odoo seeds |
| `platform/tools/seed_*.ts` | Platform engine seeds, Supabase target |
| All `ir_cron.xml`, `ir_sequence.xml` files | Configuration, not data — no duplicates |
| `archive/` directory (all) | Already archived — no action needed |

---

## 5. Risk Assessment

### 5.1 High Risk — Finance Task Consolidation

**Risk**: If both `ipai_finance_close_seed` and `ipai_finance_workflow` are installed, Odoo will create **two sets** of month-end close projects, stages, and tasks. This results in:
- Duplicate projects in the project list
- Duplicate stages cluttering the Kanban board
- ~95 duplicate tasks (39 + 36 + 20) for the same real-world work
- Confused users who don't know which project is canonical

**Mitigation**: Before merging, check which module is currently installed in production (`odoo_dev`). Remove the non-installed module's seed data. If both are installed, plan a data migration to merge records.

### 5.2 High Risk — Mail Server Conflicts

**Risk**: Up to 5 `ir.mail_server` records with `sequence=1`. Odoo picks the first active server by sequence, so having multiple at sequence 1 creates non-deterministic mail routing.

**Mitigation**:
1. Delete `ipai_mailgun_smtp` module entirely (Mailgun is deprecated)
2. Set `ipai_enterprise_bridge` mail servers to `active=False` (already done)
3. Ensure only `ipai_zoho_mail` or `ipai_system_config` hook creates the active server, not both

### 5.3 Medium Risk — ops-platform Drift

**Risk**: The `ops-platform/supabase/` directory is an exact copy today, but could drift over time if one copy is updated and the other is not.

**Mitigation**: Delete the `ops-platform/supabase/seeds/` and `ops-platform/supabase/seed/` directories. If ops-platform needs these seeds, it should reference `supabase/` via symlink or import.

### 5.4 Medium Risk — Nested `odoo/` Directory

**Risk**: The `odoo/` directory at repo root appears to be a stale copy of the entire repo. Developers or scripts could accidentally reference files from this stale copy instead of the active files.

**Mitigation**: Investigate whether any scripts or CI workflows reference `odoo/` paths. If not, remove the entire `odoo/` directory or move it to `archive/`.

### 5.5 Low Risk — CSV vs XML vs YAML Format Divergence

**Risk**: The same finance data exists in XML (for Odoo module installer), CSV (for XML-RPC import), and YAML (for Supabase platform). Over time these will diverge as changes are made to one format but not the others.

**Mitigation**: Designate one format as the single source and generate the others from it. The YAML workstream format is the most structured and could serve as the SSOT, with generation scripts producing XML and CSV.

---

## Summary Statistics

| Category | Count |
|----------|-------|
| Total seed data files (active, non-archive) | ~120 |
| Odoo module data files | 76 |
| Supabase SQL seed files | ~20 |
| YAML workstream seeds | ~22 |
| CSV data files | ~20 |
| JSON seed files | ~5 |
| Python seed scripts | ~5 |
| TypeScript seed scripts | ~5 |
| **Exact duplicate files** | **12** (ops-platform + odoo/ copies) |
| **Near/semantic duplicate groups** | **6** (finance tasks, stages, projects, BIR tasks, mail servers, HR data) |
| **Modules with conflicting seed data** | **3** (ipai_finance_close_seed, ipai_finance_workflow, ipai_project_seed) |
| **Deprecated seed files still active** | **2** (ipai_mailgun_smtp, supabase/seeds/002_finance_seed.sql) |

---

*This document is a read-only analysis. No seed files were modified.*
