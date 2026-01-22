# 📁 Repository Structure

> Auto-generated on every commit. Last update: $(date -u '+%Y-%m-%d %H:%M:%S UTC')
> Commit: 9e94d9797614ffe3b65c69c964546252e5f32874

```
.
├── .agent
│   ├── workflows
│   │   ├── deploy.md
│   │   ├── scaffold.md
│   │   └── test.md
│   └── rules.md
├── .claude
│   ├── commands
│   │   ├── dev-server.md
│   │   ├── fix-github-issue.md
│   │   ├── implement.md
│   │   ├── plan.md
│   │   ├── prototype-module.md
│   │   ├── ship.md
│   │   └── verify.md
│   ├── superclaude
│   │   └── skills
│   │       └── finance
│   ├── mcp-servers.json
│   ├── project_memory.db
│   ├── query_memory.py
│   ├── settings.json
│   └── settings.local.json
├── .continue
│   ├── prompts
│   │   ├── implement.md
│   │   ├── plan.md
│   │   ├── ship.md
│   │   └── verify.md
│   ├── rules
│   │   ├── agentic.md
│   │   ├── medallion-architecture.yaml
│   │   ├── notion-ppm.yaml
│   │   └── spec-kit.yaml
│   └── config.json
├── .devcontainer
│   ├── devcontainer.json
│   ├── post-create.sh
│   └── postCreate.sh
├── .githooks
│   └── pre-commit
├── .github
│   ├── ISSUE_TEMPLATE
│   │   ├── copilot_task.yml
│   │   ├── ee_iap_replacement.yml
│   │   ├── enterprise_replacement.yml
│   │   └── odoo_golive_task.yml
│   ├── agents
│   │   └── odoo-oca-triage.agent.md
│   ├── workflows
│   │   ├── add-to-project.yml
│   │   ├── agent-preflight.yml
│   │   ├── ai-naming-gate.yml
│   │   ├── aiux-ship-gate.yml
│   │   ├── all-green-gates.yml
│   │   ├── audit-contract.yml
│   │   ├── auth-email-ai-gate.yml
│   │   ├── auto-sitemap-tree.yml
│   │   ├── build-seeded-image.yml
│   │   ├── build-unified-image.yml
│   │   ├── canonical-gate.yml
│   │   ├── ci-web.yml
│   │   ├── ci.yml
│   │   ├── compose-topology-guard.yml
│   │   ├── control-room-ci.yml
│   │   ├── databricks-dab-ci.yml
│   │   ├── deploy-finance-ppm.yml
│   │   ├── deploy-ipai-control-center-docs.yml
│   │   ├── deploy-odoo-prod.yml
│   │   ├── deploy-production.yml
│   │   ├── deploy.yml
│   │   ├── diagrams-drawio-enforce.yml
│   │   ├── diagrams-qa.yml
│   │   ├── diagrams.yml
│   │   ├── directional-sync.yml
│   │   ├── docs-architecture-sync.yml
│   │   ├── docs-crawler-cron.yml
│   │   ├── docs-current-state-gate.yml
│   │   ├── docs-pages.yml
│   │   ├── drive-sync-verify.yml
│   │   ├── drive-sync.yml
│   │   ├── erd-docs.yml
│   │   ├── erd-graphviz.yml
│   │   ├── erd-schemaspy.yml
│   │   ├── fin-workspace-weekly-sync.yml
│   │   ├── finance-ppm-health.yml
│   │   ├── go-live-manifest-gate.yml
│   │   ├── health-check.yml
│   │   ├── icons-drift.yml
│   │   ├── infra-memory-job.yml
│   │   ├── infra-validate.yml
│   │   ├── infra_memory_job.yml
│   │   ├── insightpulse-cicd.yml
│   │   ├── ipai-ai-platform-ci.yml
│   │   ├── ipai-ai-studio-smoke.yml
│   │   ├── ipai-determinism.yml
│   │   ├── ipai-doc-drift-gate.yml
│   │   ├── ipai-dynamic-qg.yml
│   │   ├── ipai-module-matrix.yml
│   │   ├── ipai-prod-checks.yml
│   │   ├── lakehouse-smoke.yml
│   │   ├── module-catalog-drift.yml
│   │   ├── module-gating.yml
│   │   ├── modules-audit-drift.yml
│   │   ├── n8n-orchestrator.yml
│   │   ├── no-deprecated-repo-refs.yml
│   │   ├── notify-superset.yml
│   │   ├── notion-sync-ci.yml
│   │   ├── odoo-import-artifacts.yml
│   │   ├── odoo-module-install-gate.yml
│   │   ├── odoo-schema-pipeline.yml
│   │   ├── pr-installability-gate.yml
│   │   ├── prod-configure-smtp.yml
│   │   ├── prod-odoo-modules.yml
│   │   ├── project-automation.yml
│   │   ├── release-docs.yml
│   │   ├── repo-structure.yml
│   │   ├── run-odoo-cli-job.yml
│   │   ├── seed-odoo-finance.yml
│   │   ├── seeds-validate.yml
│   │   ├── spec-and-parity.yml
│   │   ├── spec-kit-enforce.yml
│   │   ├── supabase-branch-sync.yml
│   │   ├── supabase-deploy.yml
│   │   ├── superset-bump.yml
│   │   ├── superset-ci-cd.yml
│   │   ├── wiki-sync.yml
│   │   └── workflow-yaml-validate.yml
│   └── copilot-instructions.md
├── .insightpulse
│   ├── sync-config.yaml
│   └── sync.yaml
├── .vscode
│   ├── README.md
│   ├── extensions.json
│   ├── ipai_workspace.code-workspace
│   ├── launch.json
│   ├── mcp-dev.code-workspace
│   ├── mcp-prod.code-workspace
│   ├── mcp.json
│   ├── settings.json
│   ├── shortcuts.json
│   └── tasks.json
├── addons
│   ├── OCA
│   │   ├── account-financial-reporting
│   │   ├── account-financial-tools -> ../../external-src/account-financial-tools
│   │   ├── automation
│   │   ├── dms
│   │   ├── helpdesk
│   │   ├── partner-contact
│   │   ├── queue
│   │   ├── reporting-engine
│   │   ├── sale-workflow
│   │   ├── server-auth
│   │   ├── server-brand
│   │   ├── server-tools
│   │   ├── server-ux
│   │   └── web
│   ├── ipai
│   │   ├── fluent_web_365_copilot
│   │   │   ├── demo
│   │   │   ├── models
│   │   │   ├── security
│   │   │   ├── views
│   │   │   ├── README.rst
│   │   │   ├── __init__.py
│   │   │   └── __manifest__.py
│   │   ├── ipai_ai_agents_ui
│   │   │   ├── controllers
│   │   │   ├── security
│   │   │   ├── static
│   │   │   ├── tests
│   │   │   ├── ui
│   │   │   ├── views
│   │   │   ├── README.md
│   │   │   ├── __init__.py
│   │   │   └── __manifest__.py
│   │   ├── ipai_aiux_chat
│   │   │   ├── static
│   │   │   ├── views
│   │   │   ├── __init__.py
│   │   │   └── __manifest__.py
│   │   ├── ipai_chatgpt_sdk_theme
│   │   │   ├── static
│   │   │   ├── __init__.py
│   │   │   └── __manifest__.py
│   │   ├── ipai_copilot_ui
│   │   │   ├── static
│   │   │   ├── views
│   │   │   ├── __init__.py
│   │   │   └── __manifest__.py
│   │   ├── ipai_design_system_apps_sdk
│   │   │   ├── static
│   │   │   ├── README.md
│   │   │   ├── __init__.py
│   │   │   └── __manifest__.py
│   │   ├── ipai_enterprise_bridge
│   │   │   ├── controllers
│   │   │   ├── data
│   │   │   ├── demo
│   │   │   ├── models
│   │   │   ├── security
│   │   │   ├── tests
│   │   │   ├── views
│   │   │   ├── POLICY.md
│   │   │   ├── README.md
│   │   │   ├── README.rst
│   │   │   ├── __init__.py
│   │   │   ├── __manifest__.py
│   │   │   └── hooks.py
│   │   ├── ipai_finance_workflow
│   │   │   ├── data
│   │   │   ├── models
│   │   │   ├── security
│   │   │   ├── views
│   │   │   ├── __init__.py
│   │   │   └── __manifest__.py
│   │   ├── ipai_platform_theme
│   │   │   ├── static
│   │   │   ├── __init__.py
│   │   │   └── __manifest__.py
│   │   ├── ipai_theme_aiux
│   │   │   ├── static
│   │   │   ├── views
│   │   │   ├── __init__.py
│   │   │   └── __manifest__.py
│   │   ├── ipai_theme_copilot
│   │   │   ├── static
│   │   │   ├── views
│   │   │   ├── __init__.py
│   │   │   └── __manifest__.py
│   │   ├── ipai_theme_fluent2
│   │   │   ├── data
│   │   │   ├── static
│   │   │   ├── __init__.py
│   │   │   └── __manifest__.py
│   │   ├── ipai_theme_tbwa
│   │   │   ├── static
│   │   │   ├── views
│   │   │   ├── __init__.py
│   │   │   └── __manifest__.py
│   │   ├── ipai_theme_tbwa_backend
│   │   │   ├── static
│   │   │   ├── __init__.py
│   │   │   └── __manifest__.py
│   │   ├── ipai_ui_brand_tokens
│   │   │   ├── controllers
│   │   │   ├── data
│   │   │   ├── models
│   │   │   ├── security
│   │   │   ├── static
│   │   │   ├── views
│   │   │   ├── __init__.py
│   │   │   └── __manifest__.py
│   │   ├── ipai_vertical_media
│   │   │   ├── data
│   │   │   ├── models
│   │   │   ├── security
│   │   │   ├── views
│   │   │   ├── __init__.py
│   │   │   └── __manifest__.py
│   │   ├── ipai_vertical_retail
│   │   │   ├── data
│   │   │   ├── models
│   │   │   ├── security
│   │   │   ├── views
│   │   │   ├── __init__.py
│   │   │   └── __manifest__.py
│   │   ├── ipai_web_fluent2
│   │   │   ├── static
│   │   │   ├── views
│   │   │   ├── __init__.py
│   │   │   └── __manifest__.py
│   │   ├── ipai_web_icons_fluent
│   │   │   ├── static
│   │   │   ├── views
│   │   │   ├── __init__.py
│   │   │   └── __manifest__.py
│   │   ├── ipai_web_theme_tbwa
│   │   │   ├── static
│   │   │   ├── views
│   │   │   ├── __init__.py
│   │   │   └── __manifest__.py
│   │   ├── scripts
│   │   │   └── fix_odoo18_views.py
│   │   ├── .gitkeep
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_ask_ai
│   │   ├── controllers
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   ├── data
│   │   │   ├── afc_config_params.xml
│   │   │   └── ai_channel_data.xml
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── afc_rag_service.py
│   │   │   ├── ask_ai_channel.py
│   │   │   ├── ask_ai_service.py
│   │   │   └── res_config_settings.py
│   │   ├── security
│   │   │   ├── ir.model.access.csv
│   │   │   └── security.xml
│   │   ├── static
│   │   │   └── src
│   │   ├── views
│   │   │   ├── ai_settings_view.xml
│   │   │   ├── ask_ai_views.xml
│   │   │   └── res_config_settings_view.xml
│   │   ├── CHANGES.md
│   │   ├── DEPLOYMENT_CHECKLIST.md
│   │   ├── DEPLOYMENT_COMPLETE.md
│   │   ├── DEPLOYMENT_STATUS.md
│   │   ├── README.md
│   │   ├── README_AFC_RAG.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_ask_ai_chatter
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── ask_ai_request.py
│   │   │   └── mail_message.py
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_bir_tax_compliance
│   │   ├── data
│   │   │   ├── bir_filing_deadlines.xml
│   │   │   ├── bir_tax_rates.xml
│   │   │   └── ir_cron.xml
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── bir_filing_deadline.py
│   │   │   ├── bir_tax_return.py
│   │   │   ├── bir_vat.py
│   │   │   ├── bir_withholding.py
│   │   │   └── res_partner.py
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── views
│   │   │   ├── bir_dashboard_views.xml
│   │   │   ├── bir_tax_return_views.xml
│   │   │   ├── bir_vat_views.xml
│   │   │   ├── bir_withholding_views.xml
│   │   │   ├── menu.xml
│   │   │   └── res_partner_views.xml
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_crm_pipeline
│   │   ├── data
│   │   │   └── crm_stage_rules.xml
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── crm_lead.py
│   │   │   └── crm_stage.py
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── static
│   │   │   └── src
│   │   ├── views
│   │   │   ├── crm_lead_views.xml
│   │   │   └── crm_stage_views.xml
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_finance_closing
│   │   ├── data
│   │   │   ├── closing_automation.xml
│   │   │   └── closing_tasks.xml
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── DEPLOYMENT_COMPLETE.md
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_finance_ppm_golive
│   │   ├── data
│   │   │   ├── checklist_items.xml
│   │   │   └── checklist_sections.xml
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── golive_checklist.py
│   │   │   ├── golive_item.py
│   │   │   └── golive_section.py
│   │   ├── reports
│   │   │   ├── __init__.py
│   │   │   └── golive_cfo_signoff.xml
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── views
│   │   │   ├── golive_checklist_views.xml
│   │   │   ├── golive_dashboard_views.xml
│   │   │   ├── golive_item_views.xml
│   │   │   ├── golive_section_views.xml
│   │   │   └── menus.xml
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_finance_ppm_umbrella
│   │   ├── addons
│   │   │   └── ipai_finance_ppm_umbrella
│   │   ├── data
│   │   │   ├── 01_employees.xml
│   │   │   ├── 02_logframe_complete.xml
│   │   │   ├── 03_bir_schedule.xml
│   │   │   └── 04_closing_tasks.xml
│   │   ├── scripts
│   │   │   └── generate_seed_from_excel.py
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_grid_view
│   │   ├── data
│   │   │   └── demo_data.xml
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── grid_column.py
│   │   │   ├── grid_filter.py
│   │   │   └── grid_view.py
│   │   ├── security
│   │   │   ├── ir.model.access.csv
│   │   │   └── security.xml
│   │   ├── static
│   │   │   └── src
│   │   ├── views
│   │   │   ├── grid_column_views.xml
│   │   │   ├── grid_filter_views.xml
│   │   │   └── grid_view_views.xml
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_month_end
│   │   ├── data
│   │   │   ├── ir_cron.xml
│   │   │   ├── ph_holidays.xml
│   │   │   └── task_templates.xml
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── closing.py
│   │   │   ├── ph_holiday.py
│   │   │   ├── task.py
│   │   │   └── task_template.py
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── views
│   │   │   ├── closing_views.xml
│   │   │   ├── menu.xml
│   │   │   ├── ph_holiday_views.xml
│   │   │   ├── task_template_views.xml
│   │   │   └── task_views.xml
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_month_end_closing
│   │   ├── data
│   │   │   ├── project_milestone.xml
│   │   │   ├── project_project.xml
│   │   │   ├── project_tags.xml
│   │   │   ├── project_task_closing.xml
│   │   │   ├── project_task_tax.xml
│   │   │   ├── project_task_type.xml
│   │   │   └── resource_calendar_leaves.xml
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── static
│   │   │   └── description
│   │   ├── views
│   │   │   └── menus.xml
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_ocr_gateway
│   │   ├── data
│   │   │   └── ir_cron.xml
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── ipai_ocr_job.py
│   │   │   └── ipai_ocr_provider.py
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── views
│   │   │   └── ipai_ocr_views.xml
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_platform_approvals
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   └── approval_mixin.py
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── views
│   │   │   └── approval_views.xml
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_platform_audit
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   └── audit_mixin.py
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── views
│   │   │   └── audit_views.xml
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_platform_permissions
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   └── permission.py
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── views
│   │   │   └── permission_views.xml
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_platform_theme
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── res_company.py
│   │   │   └── res_config_settings.py
│   │   ├── static
│   │   │   └── src
│   │   ├── views
│   │   │   ├── assets.xml
│   │   │   ├── res_config_settings_views.xml
│   │   │   └── theme_inject.xml
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_platform_workflow
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   └── workflow_mixin.py
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── views
│   │   │   └── workflow_views.xml
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_sms_gateway
│   │   ├── controllers
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   ├── data
│   │   │   └── ir_cron.xml
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── ipai_sms_message.py
│   │   │   └── ipai_sms_provider.py
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── views
│   │   │   └── ipai_sms_views.xml
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_superset_connector
│   │   ├── data
│   │   │   ├── analytics_views.xml
│   │   │   └── superset_config.xml
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── res_config_settings.py
│   │   │   ├── superset_analytics_view.py
│   │   │   ├── superset_connection.py
│   │   │   └── superset_dataset.py
│   │   ├── security
│   │   │   ├── ir.model.access.csv
│   │   │   └── superset_security.xml
│   │   ├── views
│   │   │   ├── res_config_settings_views.xml
│   │   │   ├── superset_connection_views.xml
│   │   │   └── superset_dataset_views.xml
│   │   ├── wizards
│   │   │   ├── __init__.py
│   │   │   ├── dataset_wizard.py
│   │   │   └── dataset_wizard_views.xml
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_tbwa_finance
│   │   ├── data
│   │   │   ├── bir_form_types.xml
│   │   │   ├── compliance_checks.xml
│   │   │   ├── ir_cron.xml
│   │   │   ├── month_end_templates.xml
│   │   │   └── ph_holidays.xml
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── bir_return.py
│   │   │   ├── closing_period.py
│   │   │   ├── compliance_check.py
│   │   │   ├── finance_task.py
│   │   │   ├── finance_task_template.py
│   │   │   ├── ph_holiday.py
│   │   │   └── res_partner.py
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── views
│   │   │   ├── bir_return_views.xml
│   │   │   ├── closing_period_views.xml
│   │   │   ├── dashboard_views.xml
│   │   │   ├── finance_task_views.xml
│   │   │   ├── menu.xml
│   │   │   ├── ph_holiday_views.xml
│   │   │   └── res_partner_views.xml
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_theme_tbwa
│   │   ├── static
│   │   │   ├── description
│   │   │   └── src
│   │   ├── views
│   │   │   └── assets.xml
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_theme_tbwa_backend
│   │   ├── static
│   │   │   └── src
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── __manifest__.py
│   │   └── install.sh
│   ├── ipai_web_theme_chatgpt
│   │   ├── static
│   │   │   └── src
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_workos_affine
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_workos_blocks
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   └── block.py
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── static
│   │   │   └── src
│   │   ├── views
│   │   │   └── block_views.xml
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_workos_canvas
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   └── canvas.py
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── static
│   │   │   └── src
│   │   ├── views
│   │   │   └── canvas_views.xml
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_workos_collab
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   └── comment.py
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── views
│   │   │   └── comment_views.xml
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_workos_core
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── page.py
│   │   │   ├── space.py
│   │   │   └── workspace.py
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── static
│   │   │   └── src
│   │   ├── views
│   │   │   ├── menu_views.xml
│   │   │   ├── page_views.xml
│   │   │   ├── space_views.xml
│   │   │   └── workspace_views.xml
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_workos_db
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── database.py
│   │   │   ├── property.py
│   │   │   └── row.py
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── static
│   │   │   └── src
│   │   ├── views
│   │   │   └── database_views.xml
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_workos_search
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   └── search.py
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── views
│   │   │   └── search_views.xml
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_workos_templates
│   │   ├── data
│   │   │   └── default_templates.xml
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   └── template.py
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── views
│   │   │   └── template_views.xml
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_workos_views
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   └── view.py
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── static
│   │   │   └── src
│   │   ├── views
│   │   │   └── view_views.xml
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   └── oca
│       ├── .gitkeep
│       ├── __init__.py
│       ├── __manifest__.py
│       ├── manifest.yaml
│       ├── oca.lock.json
│       └── requirements.txt
├── agents
│   ├── capabilities
│   │   └── CAPABILITY_MATRIX.yaml
│   ├── knowledge
│   │   └── KNOWLEDGE_BASE_INDEX.yaml
│   ├── loops
│   │   └── clarity_ppm_reverse.yaml
│   ├── personas
│   │   └── odoo_architect.md
│   ├── procedures
│   │   └── EXECUTION_PROCEDURES.yaml
│   ├── prompts
│   │   └── odoo_oca_ci_fixer_system.txt
│   ├── AGENT_SKILLS_REGISTRY.yaml
│   ├── ORCHESTRATOR.md
│   ├── PRIORITIZED_ROADMAP.md
│   ├── README.md
│   ├── custom_module_auditor.md
│   ├── odoo_oca_ci_fixer.yaml
│   ├── odoo_reverse_mapper.yaml
│   └── smart_delta_oca.yaml
├── api
│   └── oca-docs-brain-openapi.yaml
├── apps
│   ├── bi-architect
│   │   ├── do
│   │   │   └── app.json
│   │   ├── APP.md
│   │   └── spec.yaml
│   ├── chatgpt_ipai_ai_studio
│   │   ├── public
│   │   │   └── widget.html
│   │   ├── src
│   │   │   └── server.js
│   │   ├── README.md
│   │   └── package.json
│   ├── control-room
│   │   ├── app
│   │   │   └── api
│   │   ├── public
│   │   │   └── assets
│   │   ├── src
│   │   │   ├── app
│   │   │   ├── assets
│   │   │   ├── components
│   │   │   ├── hooks
│   │   │   ├── lib
│   │   │   ├── theme
│   │   │   └── types
│   │   ├── .env.example
│   │   ├── FINANCE_LANDING_CHECKLIST.md
│   │   ├── PLATFORM_KIT_SPEC.md
│   │   ├── next-env.d.ts
│   │   ├── next.config.js
│   │   ├── package.json
│   │   ├── postcss.config.js
│   │   ├── tailwind.config.js
│   │   └── tsconfig.json
│   ├── control-room-api
│   │   ├── .env.example
│   │   ├── Dockerfile
│   │   ├── app.py
│   │   └── requirements.txt
│   ├── devops-engineer
│   │   ├── do
│   │   │   └── app.json
│   │   ├── APP.md
│   │   └── spec.yaml
│   ├── do-advisor-agent
│   │   ├── config
│   │   │   └── mcp-config.json
│   │   ├── prompts
│   │   │   └── unified_advisor.md
│   │   ├── tools
│   │   │   └── odoo_finance_ppm.py
│   │   └── README.md
│   ├── do-advisor-ui
│   │   ├── public
│   │   │   ├── config.js
│   │   │   └── index.html
│   │   ├── src
│   │   │   ├── assets
│   │   │   ├── components
│   │   │   ├── views
│   │   │   └── app.js
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── app-spec.yaml
│   │   └── nginx.conf
│   ├── docs-ai-widget
│   │   ├── src
│   │   │   ├── components
│   │   │   ├── embed.ts
│   │   │   └── index.ts
│   │   └── package.json
│   ├── finance-ssc-expert
│   │   ├── do
│   │   │   └── app.json
│   │   ├── APP.md
│   │   └── spec.yaml
│   ├── ipai-chatgpt-app
│   │   ├── server
│   │   │   ├── package.json
│   │   │   └── server.js
│   │   └── web
│   │       ├── src
│   │       ├── index.html
│   │       ├── package.json
│   │       ├── postcss.config.js
│   │       ├── tailwind.config.js
│   │       ├── tsconfig.json
│   │       └── vite.config.ts
│   ├── ipai-control-center-docs
│   │   ├── .vercel
│   │   │   ├── README.txt
│   │   │   └── project.json
│   │   ├── pages
│   │   │   ├── strategy
│   │   │   ├── _app.jsx
│   │   │   ├── _meta.js
│   │   │   ├── constitution.md
│   │   │   ├── index.mdx
│   │   │   ├── plan.md
│   │   │   ├── prd.md
│   │   │   └── tasks.md
│   │   ├── DEPLOYMENT.md
│   │   ├── next.config.mjs
│   │   ├── package.json
│   │   └── theme.config.jsx
│   ├── local-schema-server
│   │   ├── package.json
│   │   └── server.js
│   ├── mattermost-rag
│   │   ├── do
│   │   │   └── app.json
│   │   ├── APP.md
│   │   └── spec.yaml
│   ├── mcp-coordinator
│   │   ├── do
│   │   │   └── app.json
│   │   ├── APP.md
│   │   └── spec.yaml
│   ├── mobile
│   │   ├── src
│   │   │   ├── hooks
│   │   │   ├── lib
│   │   │   ├── screens
│   │   │   ├── store
│   │   │   └── types
│   │   ├── App.tsx
│   │   ├── README.md
│   │   ├── app.json
│   │   ├── eas.json
│   │   ├── package.json
│   │   └── tsconfig.json
│   ├── multi-agent-orchestrator
│   │   ├── do
│   │   │   └── app.json
│   │   ├── APP.md
│   │   └── spec.yaml
│   ├── odoo-developer-agent
│   │   ├── do
│   │   │   └── app.json
│   │   ├── APP.md
│   │   └── spec.yaml
│   ├── odoo-saas-platform
│   │   ├── do
│   │   │   └── app.json
│   │   ├── APP.md
│   │   └── spec.yaml
│   ├── pulser-runner
│   │   ├── .env.example
│   │   ├── app.py
│   │   ├── package.json
│   │   └── requirements.txt
│   ├── superset-analytics
│   │   ├── do
│   │   │   └── app.json
│   │   ├── APP.md
│   │   └── spec.yaml
│   ├── superset-embed-api
│   │   ├── src
│   │   │   └── index.js
│   │   ├── .env.example
│   │   ├── Dockerfile
│   │   ├── do-app-spec.yaml
│   │   └── package.json
│   └── web
│       ├── content
│       │   └── solutions
│       ├── public
│       │   └── solutions
│       ├── scripts
│       │   └── check-assets.mjs
│       ├── src
│       │   ├── app
│       │   ├── components
│       │   └── lib
│       ├── .env.example
│       ├── .gitignore
│       ├── next-env.d.ts
│       ├── next.config.js
│       ├── package.json
│       ├── postcss.config.js
│       ├── tailwind.config.js
│       └── tsconfig.json
├── archive
│   ├── addons
│   │   ├── ipai_accounting_firm_pack
│   │   │   ├── data
│   │   │   ├── models
│   │   │   ├── security
│   │   │   ├── views
│   │   │   ├── __init__.py
│   │   │   └── __manifest__.py
│   │   ├── ipai_docs
│   │   │   ├── models
│   │   │   ├── security
│   │   │   ├── tests
│   │   │   ├── views
│   │   │   ├── README.rst
│   │   │   ├── __init__.py
│   │   │   └── __manifest__.py
│   │   ├── ipai_docs_project
│   │   │   ├── data
│   │   │   ├── models
│   │   │   ├── views
│   │   │   ├── README.rst
│   │   │   ├── __init__.py
│   │   │   └── __manifest__.py
│   │   ├── ipai_finance_ap_aging
│   │   │   ├── controllers
│   │   │   ├── data
│   │   │   ├── models
│   │   │   ├── security
│   │   │   ├── static
│   │   │   ├── tests
│   │   │   ├── views
│   │   │   ├── IMPLEMENTATION_SUMMARY.md
│   │   │   ├── README.rst
│   │   │   ├── __init__.py
│   │   │   └── __manifest__.py
│   │   ├── ipai_finance_controller_dashboard
│   │   │   ├── controllers
│   │   │   ├── data
│   │   │   ├── models
│   │   │   ├── security
│   │   │   ├── static
│   │   │   ├── tests
│   │   │   ├── views
│   │   │   ├── IMPLEMENTATION_SUMMARY.md
│   │   │   ├── README.rst
│   │   │   ├── __init__.py
│   │   │   └── __manifest__.py
│   │   ├── ipai_idp
│   │   │   ├── ade
│   │   │   ├── controllers
│   │   │   ├── data
│   │   │   ├── models
│   │   │   ├── security
│   │   │   ├── services
│   │   │   ├── tests
│   │   │   ├── views
│   │   │   ├── README.md
│   │   │   ├── __init__.py
│   │   │   └── __manifest__.py
│   │   ├── ipai_marketing_agency_pack
│   │   │   ├── data
│   │   │   ├── models
│   │   │   ├── security
│   │   │   ├── views
│   │   │   ├── __init__.py
│   │   │   └── __manifest__.py
│   │   ├── ipai_ocr_expense
│   │   │   ├── models
│   │   │   ├── security
│   │   │   ├── views
│   │   │   ├── README.md
│   │   │   ├── __init__.py
│   │   │   └── __manifest__.py
│   │   ├── ipai_partner_pack
│   │   │   ├── data
│   │   │   ├── models
│   │   │   ├── security
│   │   │   ├── views
│   │   │   ├── __init__.py
│   │   │   └── __manifest__.py
│   │   ├── omc_finance_ppm
│   │   │   ├── actions
│   │   │   ├── data
│   │   │   ├── models
│   │   │   ├── security
│   │   │   ├── static
│   │   │   ├── views
│   │   │   ├── DEPLOYMENT_STRATEGY.md
│   │   │   ├── __init__.py
│   │   │   └── __manifest__.py
│   │   └── tbwa_spectra_integration
│   │       ├── data
│   │       ├── models
│   │       ├── security
│   │       ├── views
│   │       ├── wizards
│   │       ├── README.md
│   │       ├── README.rst
│   │       ├── __init__.py
│   │       └── __manifest__.py
│   └── compose
│       ├── dev-docker
│       │   ├── config
│       │   ├── ipai_finance_ppm
│       │   ├── theme_tbwa_backend
│       │   ├── .env.example
│       │   ├── Dockerfile
│       │   ├── README.md
│       │   └── docker-compose.yml
│       ├── docker
│       │   ├── hardened
│       │   ├── nginx
│       │   ├── Dockerfile.enterprise-parity
│       │   ├── Dockerfile.seeded
│       │   ├── Dockerfile.unified
│       │   ├── Dockerfile.v1.1.0-enterprise-parity
│       │   ├── build-enterprise-parity.sh
│       │   ├── docker-compose.enterprise-parity.yml
│       │   ├── docker-compose.seeded.yml
│       │   ├── docker-entrypoint.sh
│       │   ├── entrypoint.seeded.sh
│       │   ├── odoo-v1.1.0.conf
│       │   ├── odoo.conf.template
│       │   ├── odoo.seeded.conf
│       │   ├── requirements-enterprise-parity.txt
│       │   └── requirements.seeded.txt
│       ├── odooforge-sandbox
│       │   ├── .devcontainer
│       │   ├── .github
│       │   ├── addons
│       │   ├── config
│       │   ├── kit-cli
│       │   ├── reports
│       │   ├── scripts
│       │   ├── specs
│       │   ├── templates
│       │   ├── tests
│       │   ├── .gitignore
│       │   ├── .pre-commit-config.yaml
│       │   ├── AGENTS.md
│       │   ├── Dockerfile.kit
│       │   ├── README.md
│       │   ├── docker-compose.yml
│       │   ├── install-sandbox.sh
│       │   ├── requirements-dev.txt
│       │   └── requirements.txt
│       ├── docker-compose.canonical.yml
│       ├── docker-compose.docs-assistant.yml
│       ├── docker-compose.droplet.yml
│       ├── docker-compose.infra-prod.yml
│       ├── docker-compose.ipai-ops.yml
│       ├── docker-compose.mcp-local.yml
│       ├── docker-compose.ocr-adapter.yml
│       ├── docker-compose.prod.root.yml
│       ├── docker-compose.prod.v0.10.0.yml
│       ├── docker-compose.prod.v0.9.1.yml
│       ├── docker-compose.root.yml
│       ├── docker-compose.workos-deploy.yml
│       ├── docker-compose.yml
│       ├── keycloak-integration.yml
│       ├── mattermost-integration.yml
│       └── odoo-prod.compose.yml
├── artifacts
│   ├── logs
│   │   ├── ipai__install.log
│   │   ├── ipai_ask_ai__install.log
│   │   ├── ipai_bir_tax_compliance__install.log
│   │   ├── ipai_close_orchestration__install.log
│   │   ├── ipai_crm_pipeline__install.log
│   │   ├── ipai_finance_closing__install.log
│   │   ├── ipai_finance_monthly_closing__install.log
│   │   ├── ipai_finance_ppm__install.log
│   │   ├── ipai_finance_ppm_golive__install.log
│   │   ├── ipai_finance_ppm_umbrella__install.log
│   │   ├── ipai_grid_view__install.log
│   │   ├── ipai_month_end__install.log
│   │   ├── ipai_month_end_closing__install.log
│   │   ├── ipai_platform_approvals__install.log
│   │   ├── ipai_platform_audit__install.log
│   │   ├── ipai_platform_permissions__install.log
│   │   ├── ipai_platform_theme__install.log
│   │   ├── ipai_platform_workflow__install.log
│   │   ├── ipai_ppm_a1__install.log
│   │   ├── ipai_ppm_monthly_close__install.log
│   │   ├── ipai_superset_connector__install.log
│   │   ├── ipai_tbwa_finance__install.log
│   │   ├── ipai_theme_tbwa_backend__install.log
│   │   ├── ipai_workos_affine__install.log
│   │   ├── ipai_workos_blocks__install.log
│   │   ├── ipai_workos_canvas__install.log
│   │   ├── ipai_workos_collab__install.log
│   │   ├── ipai_workos_core__install.log
│   │   ├── ipai_workos_db__install.log
│   │   ├── ipai_workos_search__install.log
│   │   ├── ipai_workos_templates__install.log
│   │   └── ipai_workos_views__install.log
│   ├── seed_export
│   │   ├── 20260105_020943
│   │   │   ├── CHECKSUMS.txt
│   │   │   ├── MANIFEST.json
│   │   │   ├── projects.csv
│   │   │   ├── stages.csv
│   │   │   ├── tags.csv
│   │   │   ├── tasks.csv
│   │   │   └── users.csv
│   │   ├── latest -> 20260105_020943
│   │   └── 20260105_020943_full_export.zip
│   ├── seed_replace
│   │   ├── 20260105_023741
│   │   │   ├── CHECKSUMS.txt
│   │   │   ├── MANIFEST.json
│   │   │   ├── projects.csv
│   │   │   └── tasks.csv
│   │   ├── 20260105_023756
│   │   │   ├── CHECKSUMS.txt
│   │   │   ├── MANIFEST.json
│   │   │   ├── projects.csv
│   │   │   └── tasks.csv
│   │   ├── 20260105_023833
│   │   │   ├── CHECKSUMS.txt
│   │   │   ├── MANIFEST.json
│   │   │   ├── projects.csv
│   │   │   └── tasks.csv
│   │   ├── 20260105_023848
│   │   │   ├── CHECKSUMS.txt
│   │   │   ├── MANIFEST.json
│   │   │   ├── projects.csv
│   │   │   └── tasks.csv
│   │   ├── 20260105_023939
│   │   │   ├── CHECKSUMS.txt
│   │   │   ├── MANIFEST.json
│   │   │   ├── projects.csv
│   │   │   └── tasks.csv
│   │   ├── 20260105_023741_seed.zip
│   │   ├── 20260105_023756_seed.zip
│   │   ├── 20260105_023833_seed.zip
│   │   ├── 20260105_023848_seed.zip
│   │   └── 20260105_023939_seed.zip
│   ├── supabase_verify
│   │   └── report.json
│   ├── ce_oca_equivalents_audit.csv
│   ├── ce_oca_equivalents_audit.json
│   ├── ipai_install_upgrade_matrix.csv
│   ├── ipai_install_upgrade_matrix.json
│   ├── ipai_quality_gate.csv
│   ├── ipai_quality_gate.json
│   ├── module_audit_baseline.json
│   ├── module_audit_matrix.csv
│   └── module_audit_matrix.json
├── audit
│   ├── snapshot.json
│   └── snapshot.txt
├── automations
│   └── n8n
│       ├── workflows
│       │   ├── 01-health-check.json
│       │   ├── 02-git-operations-hub.json
│       │   ├── 03-finance-close-orchestrator.json
│       │   ├── 04-bir-compliance.json
│       │   ├── 05-github-oauth-callback.json
│       │   ├── bir_deadline_reminder.json
│       │   ├── expense_receipt_capture.json
│       │   ├── finance_closing_automation.json
│       │   ├── git_operations_hub.json
│       │   ├── invoice_ocr_to_odoo.json
│       │   ├── odoo_reverse_mapper.json
│       │   └── ppm_monthly_close_automation.json
│       ├── README_FINANCE_CLOSING.md
│       ├── bir_deadline_reminder_workflow.json
│       └── bir_overdue_nudge_workflow.json
├── baselines
│   └── v0.2.1-quality-baseline-20251121.txt
├── bin
│   ├── README.md
│   ├── ci_sync_check.sh
│   ├── copilot_drift_check.sh
│   ├── finance-cli.sh
│   ├── import_bir_schedules.py
│   ├── odoo-check-gate
│   ├── odoo-tests.sh
│   └── postdeploy-finance.sh
├── branding
│   └── fluentui-system-icons
├── calendar
│   ├── 2026_FinanceClosing_Master.csv
│   └── FinanceClosing_RecurringTasks.ics
├── catalog
│   ├── best_of_breed.yaml
│   ├── equivalence_matrix.csv
│   └── equivalence_matrix_workos_notion.csv
├── claudedocs
│   ├── 100_PERCENT_CLI_DEPLOYMENT.md
│   ├── DEPLOYMENT_SUMMARY.md
│   ├── FINAL_DEPLOYMENT_REPORT.md
│   ├── ISSUE_RESOLUTION_REPORT.md
│   └── bir-filing-validation-report.md
├── clients
│   └── flutter_receipt_ocr
│       ├── lib
│       │   ├── receipt_ocr
│       │   ├── main.dart
│       │   └── receipt_ocr.dart
│       ├── DEPLOYMENT_GUIDE.md
│       ├── README.md
│       ├── analysis_options.yaml
│       └── pubspec.yaml
├── config
│   ├── entrypoint.d
│   │   ├── 10-log-env.sh
│   │   ├── 20-render-conf.sh
│   │   └── 90-preflight.sh
│   ├── finance
│   │   └── Month-end Closing Task and Tax Filing (7).xlsx
│   ├── sources
│   │   ├── oca_repos.yaml
│   │   ├── odoo_docs.yaml
│   │   └── sap_help.yaml
│   ├── MAILGUN_INTEGRATION_COMPLETE.md
│   ├── MAILGUN_INTEGRATION_DEPLOYMENT.md
│   ├── PRODUCTION_DEPLOYMENT_SCRIPT.sh
│   ├── capability_map.yaml
│   ├── extended-platform-install-order.yaml
│   ├── mailgun_integration_implementation.json
│   ├── oca-repos.yaml
│   ├── odoo-core.conf
│   ├── odoo.conf.template
│   ├── pipeline.yaml
│   └── ship_set.txt
├── contracts
│   └── delta
│       ├── bronze_raw_pages.yaml
│       ├── gold_chunks.yaml
│       ├── gold_embeddings.yaml
│       └── silver_normalized_docs.yaml
├── data
│   ├── finance_seed
│   │   ├── 01_project.tags.csv
│   │   ├── 02_project.project.csv
│   │   ├── 03_project.task.month_end.csv
│   │   ├── 04_project.task.bir_tax.csv
│   │   ├── README.md
│   │   ├── import_all.py
│   │   ├── import_finance_seed.sh
│   │   └── update_tasks_after_import.py
│   ├── import_templates
│   │   ├── 01_project.task.type.csv
│   │   ├── 02_project.project.csv
│   │   ├── 03_project.milestone.csv
│   │   ├── 04_project.task.csv
│   │   ├── 05_project.task.dependencies.csv
│   │   ├── 06_project.task.recurrence.csv
│   │   ├── 07_mail.activity.csv
│   │   ├── README.md
│   │   └── odoo_import_headers.contract.json
│   ├── templates
│   │   └── user_assignments_template.csv
│   ├── IMPORT_GUIDE.md
│   ├── bir_calendar_2026.json
│   ├── bir_december_2025_seed.xml
│   ├── employee_directory.json
│   ├── month_end_closing_tasks.csv
│   ├── month_end_tasks.csv
│   ├── notion_tasks_deduplicated.json
│   ├── notion_tasks_parsed.json
│   ├── notion_tasks_with_logframe.json
│   └── user_map.csv
├── db
│   ├── audit
│   │   └── supabase_exposure_audit.sql
│   ├── import-templates
│   │   └── extended-platform
│   │       ├── README.md
│   │       ├── account_fiscal_year.csv
│   │       ├── auditlog_rule.csv
│   │       ├── date_range.csv
│   │       ├── date_range_type.csv
│   │       ├── dms_category.csv
│   │       ├── dms_directory.csv
│   │       ├── dms_storage.csv
│   │       ├── document_page.csv
│   │       ├── kpi_dashboard.csv
│   │       └── queue_job_channel.csv
│   ├── migrations
│   │   ├── shadow
│   │   │   ├── 001_shadow_schema_base.sql
│   │   │   └── 002_shadow_tables_generated.sql
│   │   ├── 202512070001_REORG_CREATE_DOMAIN_TABLES.sql
│   │   ├── 202512070002_REORG_COPY_DATA.sql
│   │   ├── 202512070003_REORG_CREATE_COMPAT_VIEWS.sql
│   │   ├── 202601060001_IPAI_KB_CHUNKS.sql
│   │   ├── 20260109_KG.sql
│   │   ├── 202601120001_MULTI_TENANT_PROVIDER_MODEL.sql
│   │   ├── 202601130001_SCOUT_API_SCHEMA.sql
│   │   ├── 202601130002_SCOUT_MEDALLION_TABLES.sql
│   │   ├── 202601160001_VERIFIED_MEMORY.sql
│   │   ├── 20260119_agent_memory_schema.sql
│   │   ├── 20260120_agent_coordination_schema.sql
│   │   └── 20260121_observability_schema.sql
│   ├── process_mining
│   │   ├── 001_pm_schema.sql
│   │   └── 010_p2p_etl.sql
│   ├── rls
│   │   ├── RLS_BASE_TEMPLATE.sql
│   │   └── RLS_ROLES.md
│   ├── schema
│   │   └── oca_docs_brain.dbml
│   ├── seeds
│   │   └── SEEDING_STRATEGY.md
│   └── DB_TARGET_ARCHITECTURE.md
├── deploy
│   ├── k8s
│   │   ├── namespace.yaml
│   │   ├── odoo-configmap.yaml
│   │   ├── odoo-deployment.yaml
│   │   ├── odoo-ingress.yaml
│   │   ├── odoo-secrets.yaml
│   │   ├── odoo-service.yaml
│   │   ├── postgres-service.yaml
│   │   └── postgres-statefulset.yaml
│   ├── nginx
│   │   └── erp.insightpulseai.net.conf
│   ├── runtime
│   │   ├── odoo-prod.docker_inspect.json
│   │   └── odoo-prod.image_inspect.json
│   ├── .env.production.template
│   ├── DROPLET_DEPLOYMENT.md
│   ├── PRODUCTION_SETUP.md
│   ├── README.md
│   ├── docker-compose.prod.yml
│   ├── monitoring_schema.sql
│   ├── monitoring_views.sql
│   ├── nginx_correlation_id.conf
│   ├── odoo-auto-heal.service
│   ├── odoo.canonical.conf
│   ├── odoo.conf
│   └── odoo.conf.droplet
├── docs
│   ├── adr
│   │   └── ADR-0001-clone-not-integrate.md
│   ├── api
│   │   ├── EXTENDED_PLATFORM_API.md
│   │   └── openapi.ipai_ai_platform.yaml
│   ├── architecture
│   │   ├── catalog
│   │   │   ├── COPILOT_TOOLS_SCHEMA.md
│   │   │   └── copilot_tools.openapi.json
│   │   ├── runtime_snapshot
│   │   │   ├── 20260108_013846
│   │   │   └── README.md
│   │   ├── AGENTIC_AI_ERP_ANALYTICS.md
│   │   ├── AI_MODULE_DEPRECATION_MANIFEST.md
│   │   ├── ASK_AI_CONTRACT.md
│   │   ├── AUTH_MODEL.md
│   │   ├── INSIGHTPULSEAI_TECHNICAL_ARCHITECTURE.md
│   │   ├── IPAI_AI_PLATFORM_ARCH.md
│   │   ├── IPAI_AI_PLATFORM_ERD.dbml
│   │   ├── IPAI_AI_PLATFORM_ORD.md
│   │   ├── IPAI_MODULE_REDUCTION_PLAN.md
│   │   ├── IPAI_TARGET_ARCHITECTURE.md
│   │   ├── OCR_PIPELINE.md
│   │   ├── ODOO_OFFICIAL_TO_TBWA_CANONICAL.md
│   │   ├── PROD_RUNTIME_SNAPSHOT.md
│   │   ├── README.md
│   │   ├── RUNTIME_IDENTIFIERS.md
│   │   ├── SOURCE_OF_TRUTH.md
│   │   ├── ipai_idp_architecture.drawio
│   │   ├── ipai_idp_build_deploy_custom_models.drawio
│   │   ├── ipai_idp_multi_agent_workflow.drawio
│   │   ├── ipai_idp_pdf_processing.drawio
│   │   ├── multi_tenant_architecture.md
│   │   └── runtime_identifiers.json
│   ├── audits
│   │   └── ipai_modules
│   │       ├── README.md
│   │       ├── inventory.csv
│   │       ├── inventory.json
│   │       ├── inventory.md
│   │       ├── oca_modules_vendored.txt
│   │       └── oca_overlap_map.yaml
│   ├── auth
│   │   ├── EMAIL_AUTH_SETUP.md
│   │   └── EMAIL_OTP_IMPLEMENTATION.md
│   ├── cicd
│   │   └── README.md
│   ├── claude_code
│   │   ├── IMPLEMENTATION_SUMMARY.md
│   │   ├── QUICK_REFERENCE.md
│   │   └── README.md
│   ├── connectors
│   │   └── CLAUDE_CONNECTORS.md
│   ├── data-model
│   │   ├── EXTENDED_PLATFORM_ERD.mmd
│   │   ├── EXTENDED_PLATFORM_ORM_MAP.md
│   │   ├── EXTENDED_PLATFORM_SCHEMA.dbml
│   │   ├── IPAI_AI_PLATFORM_ERD.mmd
│   │   ├── IPAI_AI_PLATFORM_SCHEMA.dbml
│   │   ├── IPAI_FINANCE_OKR_SCHEMA.dbml
│   │   ├── MULTI_TENANT_PROVIDER_SCHEMA.dbml
│   │   ├── OCA_PROJECT_DATA_MODEL.md
│   │   ├── ODOO_CANONICAL_SCHEMA.dbml
│   │   ├── ODOO_ERD.mmd
│   │   ├── ODOO_ERD.puml
│   │   ├── ODOO_MODEL_INDEX.json
│   │   ├── ODOO_MODULE_DELTAS.md
│   │   ├── ODOO_ORM_MAP.md
│   │   ├── ODOO_SHADOW_SCHEMA.sql
│   │   ├── README.md
│   │   ├── SCOUT_CES_ANALYTICS_SCHEMA.dbml
│   │   ├── SHADOW_SCHEMA_FEASIBILITY.md
│   │   ├── SUPERSET_ERD_INTEGRATION.md
│   │   └── insightpulse_canonical.dbml
│   ├── db
│   │   ├── DB_CONVENTIONS_AND_NAMING.md
│   │   ├── DB_CURRENT_INVENTORY.md
│   │   ├── DB_DOMAIN_TABLE_SPECS.md
│   │   ├── DB_ODOO_MAPPING.md
│   │   ├── DB_REORG_MIGRATION_PLAN.md
│   │   ├── DB_RLS_POLICY_TEMPLATES.md
│   │   ├── DB_TABLE_CLASSIFICATION_DRAFT.md
│   │   └── DB_TARGET_ARCHITECTURE.md
│   ├── deployment
│   │   ├── CLAUDE_CODE_CLI_PROMPT.md
│   │   ├── DEPLOYMENT_EXECUTION_GUIDE.md
│   │   ├── DEPLOYMENT_VERIFICATION_MATRIX.md
│   │   ├── MODULES_AUDIT.md
│   │   ├── OCA_CI_GUARDIAN.md
│   │   ├── PRE_FLIGHT_CHECKLIST.md
│   │   ├── README.md
│   │   └── WORKOS_DEPLOYMENT_PACKAGE.md
│   ├── design-system
│   │   ├── SHADCN_UI_DESIGN_SYSTEM_ANALYSIS.md
│   │   └── shadcn-ui-skills-catalog.json
│   ├── diagrams
│   │   ├── architecture
│   │   │   ├── README.md
│   │   │   └── manifest.json
│   │   ├── mappings
│   │   │   └── azure_to_do_supabase_odoo.yaml
│   │   ├── .gitkeep
│   │   └── ipai_platform_flow.mmd
│   ├── email
│   │   └── Mailgun_DNS.md
│   ├── evidence
│   │   ├── 20260110-0927
│   │   │   └── odooforge-sandbox
│   │   ├── 20260112-0300
│   │   │   └── erd-automation
│   │   ├── 20260112-0358
│   │   │   └── ipai_finance_okr
│   │   ├── 20260112-0649
│   │   │   └── github-setup
│   │   ├── 20260119-0840
│   │   │   └── mailgun-mailgate
│   │   ├── 20260119-1121
│   │   │   └── digitalocean-postgresql
│   │   ├── 20260120-agent-communication
│   │   │   └── IMPLEMENTATION.md
│   │   └── 20260120-mailgun
│   │       └── VERIFICATION_CHECKLIST.md
│   ├── finance-ppm
│   │   └── OCA_INSTALLATION_GUIDE.md
│   ├── golive
│   │   ├── TBWA_OMC_PH_GOLIVE_CHECKLIST.csv
│   │   └── TBWA_OMC_PH_GOLIVE_GUIDE.md
│   ├── incidents
│   │   └── templates
│   │       ├── POST_MORTEM.md
│   │       └── error_envelope.json
│   ├── infra
│   │   ├── GIT_PREFLIGHT_DEPLOYMENT_REPORT.md
│   │   ├── GIT_PREFLIGHT_INTEGRATION.md
│   │   ├── GIT_PREFLIGHT_SUMMARY.md
│   │   ├── IMPLEMENTATION_COMPLETE.md
│   │   ├── MAILGUN_INTEGRATION.md
│   │   ├── MCP_JOBS_SYSTEM.md
│   │   ├── MEMORY_INGESTION.md
│   │   ├── ODOO_SHADOW_SCHEMA.md
│   │   ├── SECRETS_MANAGEMENT.md
│   │   ├── SUPABASE_BRANCHING_INTEGRATION.md
│   │   ├── SUPABASE_ODOO_SEED_PATTERN.md
│   │   ├── VERCEL_AI_GATEWAY_INTEGRATION.md
│   │   └── VERCEL_INTEGRATIONS.md
│   ├── integration
│   │   ├── INSIGHTPULSE_ROADMAP.md
│   │   └── SLACK_INTEGRATION_SETUP.md
│   ├── integrations
│   │   ├── FOCALBOARD.md
│   │   ├── MATTERMOST.md
│   │   ├── N8N.md
│   │   ├── OCA_SUBTREE_MIGRATION.md
│   │   └── OPS_STACK.md
│   ├── ipai
│   │   ├── profiles
│   │   │   └── finance_prod.txt
│   │   ├── ARCHITECTURE.md
│   │   ├── CHANGELOG.md
│   │   ├── INSTALLATION.md
│   │   ├── MODULE_DEPRECATION_PLAN.md
│   │   ├── MODULE_EVALUATION_SUMMARY.md
│   │   ├── MODULE_NAME_CORRECTIONS.md
│   │   ├── OPERATIONS_RUNBOOK.md
│   │   ├── PROFILES.md
│   │   ├── README.md
│   │   ├── SECURITY_MODEL.md
│   │   └── module_scan.json
│   ├── knowledge
│   │   └── graph_seed.json
│   ├── llm
│   │   ├── DIGITALOCEAN_DOCKER_STACK.md
│   │   ├── GLOSSARY.md
│   │   ├── LLM_QUERY_PLAYBOOK.md
│   │   ├── MCP_INTEGRATION.md
│   │   ├── ODOO_PLATFORM.md
│   │   ├── STACK_OVERVIEW.md
│   │   ├── STACK_RELATIONSHIPS.md
│   │   ├── SUPABASE_STACK.md
│   │   └── VERCEL_STACK.md
│   ├── mailgun
│   │   ├── INBOUND_EMAIL_ROUTES.md
│   │   ├── ODOO_SMTP_SETUP.md
│   │   ├── TBWA_MAILGUN_CANONICAL.md
│   │   └── WEBHOOKS_AND_EVENTS.md
│   ├── memory
│   │   ├── CANONICAL_CONTEXT.md
│   │   ├── MEMORY_DISTILLATION.json
│   │   └── MEMORY_WRITE_INSTRUCTIONS.md
│   ├── module-health
│   │   ├── MODULES_PROD_STATUS.md
│   │   └── modules_status.json
│   ├── modules
│   │   ├── INDEX.md
│   │   ├── generation_summary.json
│   │   ├── ipai_advisor.md
│   │   ├── ipai_agent_core.md
│   │   ├── ipai_ai_agents.md
│   │   ├── ipai_ai_agents_ui.md
│   │   ├── ipai_ai_audit.md
│   │   ├── ipai_ai_connectors.md
│   │   ├── ipai_ai_copilot.md
│   │   ├── ipai_ai_core.md
│   │   ├── ipai_ai_prompts.md
│   │   ├── ipai_ai_provider_kapa.md
│   │   ├── ipai_ai_provider_pulser.md
│   │   ├── ipai_ai_sources_odoo.md
│   │   ├── ipai_ai_studio.md
│   │   ├── ipai_aiux_chat.md
│   │   ├── ipai_approvals.md
│   │   ├── ipai_ask_ai.md
│   │   ├── ipai_ask_ai_bridge.md
│   │   ├── ipai_ask_ai_chatter.md
│   │   ├── ipai_assets.md
│   │   ├── ipai_auth_oauth_internal.md
│   │   ├── ipai_bi_superset.md
│   │   ├── ipai_bir_compliance.md
│   │   ├── ipai_bir_tax_compliance.md
│   │   ├── ipai_catalog_bridge.md
│   │   ├── ipai_ce_branding.md
│   │   ├── ipai_ce_cleaner.md
│   │   ├── ipai_ces_bundle.md
│   │   ├── ipai_chatgpt_sdk_theme.md
│   │   ├── ipai_clarity_ppm_parity.md
│   │   ├── ipai_close_orchestration.md
│   │   ├── ipai_command_center.md
│   │   ├── ipai_control_room.md
│   │   ├── ipai_copilot_hub.md
│   │   ├── ipai_copilot_ui.md
│   │   ├── ipai_crm_pipeline.md
│   │   ├── ipai_custom_routes.md
│   │   ├── ipai_default_home.md
│   │   ├── ipai_design_system_apps_sdk.md
│   │   ├── ipai_dev_studio_base.md
│   │   ├── ipai_document_ai.md
│   │   ├── ipai_enterprise_bridge.md
│   │   ├── ipai_equipment.md
│   │   ├── ipai_expense.md
│   │   ├── ipai_expense_ocr.md
│   │   ├── ipai_finance_bir_compliance.md
│   │   ├── ipai_finance_close_automation.md
│   │   ├── ipai_finance_close_seed.md
│   │   ├── ipai_finance_closing.md
│   │   ├── ipai_finance_month_end.md
│   │   ├── ipai_finance_monthly_closing.md
│   │   ├── ipai_finance_ppm.md
│   │   ├── ipai_finance_ppm_closing.md
│   │   ├── ipai_finance_ppm_dashboard.md
│   │   ├── ipai_finance_ppm_golive.md
│   │   ├── ipai_finance_ppm_tdi.md
│   │   ├── ipai_finance_ppm_umbrella.md
│   │   ├── ipai_finance_project_hybrid.md
│   │   ├── ipai_focalboard_connector.md
│   │   ├── ipai_grid_view.md
│   │   ├── ipai_industry_accounting_firm.md
│   │   ├── ipai_industry_marketing_agency.md
│   │   ├── ipai_integrations.md
│   │   ├── ipai_iot_bridge.md
│   │   ├── ipai_mail_integration.md
│   │   ├── ipai_marketing_ai.md
│   │   ├── ipai_marketing_journey.md
│   │   ├── ipai_master_control.md
│   │   ├── ipai_mattermost_connector.md
│   │   ├── ipai_mcp_hub.md
│   │   ├── ipai_module_gating.md
│   │   ├── ipai_month_end.md
│   │   ├── ipai_month_end_closing.md
│   │   ├── ipai_n8n_connector.md
│   │   ├── ipai_ocr_expense.md
│   │   ├── ipai_ocr_gateway.md
│   │   ├── ipai_platform_approvals.md
│   │   ├── ipai_platform_audit.md
│   │   ├── ipai_platform_permissions.md
│   │   ├── ipai_platform_theme.md
│   │   ├── ipai_platform_workflow.md
│   │   ├── ipai_portal_fix.md
│   │   ├── ipai_ppm.md
│   │   ├── ipai_ppm_a1.md
│   │   ├── ipai_ppm_dashboard_canvas.md
│   │   ├── ipai_ppm_monthly_close.md
│   │   ├── ipai_project_gantt.md
│   │   ├── ipai_project_profitability_bridge.md
│   │   ├── ipai_project_program.md
│   │   ├── ipai_project_suite.md
│   │   ├── ipai_saas_tenant.md
│   │   ├── ipai_sample_metrics.md
│   │   ├── ipai_scout_bundle.md
│   │   ├── ipai_settings_dashboard.md
│   │   ├── ipai_skill_api.md
│   │   ├── ipai_sms_gateway.md
│   │   ├── ipai_srm.md
│   │   ├── ipai_studio_ai.md
│   │   ├── ipai_superset_connector.md
│   │   ├── ipai_superset_connector_technical_guide.md
│   │   ├── ipai_tbwa_finance.md
│   │   ├── ipai_tenant_core.md
│   │   ├── ipai_test_fixtures.md
│   │   ├── ipai_theme_aiux.md
│   │   ├── ipai_theme_copilot.md
│   │   ├── ipai_theme_fluent2.md
│   │   ├── ipai_theme_tbwa.md
│   │   ├── ipai_theme_tbwa_backend.md
│   │   ├── ipai_ui_brand_tokens.md
│   │   ├── ipai_v18_compat.md
│   │   ├── ipai_web_fluent2.md
│   │   ├── ipai_web_icons_fluent.md
│   │   ├── ipai_web_theme_chatgpt.md
│   │   ├── ipai_web_theme_tbwa.md
│   │   ├── ipai_workos_affine.md
│   │   ├── ipai_workos_blocks.md
│   │   ├── ipai_workos_canvas.md
│   │   ├── ipai_workos_collab.md
│   │   ├── ipai_workos_core.md
│   │   ├── ipai_workos_db.md
│   │   ├── ipai_workos_search.md
│   │   ├── ipai_workos_templates.md
│   │   ├── ipai_workos_views.md
│   │   └── ipai_workspace_core.md
│   ├── odoo
│   │   └── DEVELOPER_TOOLS.md
│   ├── odoo-18-handbook
│   │   ├── pages
│   │   │   ├── 01-finance-accounting.md
│   │   │   ├── 02-projects-ppm.md
│   │   │   └── 03-retail-scout-integration.md
│   │   ├── spec
│   │   │   ├── constitution.md
│   │   │   ├── plan.md
│   │   │   ├── prd.md
│   │   │   └── tasks.md
│   │   ├── ODOO_18_CE_OCA_HANDBOOK.md
│   │   └── README.md
│   ├── ops
│   │   ├── conversations
│   │   │   ├── 001 — 2025-12-31 — Initial setup.md
│   │   │   ├── 002 — 2025-12-31 — Post-commit smoke.md
│   │   │   ├── INDEX.md
│   │   │   └── index.json
│   │   ├── ANTIGRAVITY_MCP.md
│   │   ├── CONVERSATIONS_README.md
│   │   ├── EXECUTION_BOARD.md
│   │   ├── GO_LIVE_CHECKLIST.md
│   │   ├── LOCAL_DEV.md
│   │   ├── PREVENT_502.md
│   │   ├── QUICK_START.md
│   │   ├── README.md
│   │   ├── RECOVERY.md
│   │   ├── SHIP_VERIFICATION.md
│   │   ├── SUPABASE_DEPLOYMENT_VERIFICATION.md
│   │   ├── VERIFICATION_COMMANDS.md
│   │   ├── WHAT_SHIPPED.template.md
│   │   ├── drive_sync_runbook.md
│   │   └── production_redeploy_runbook.md
│   ├── ord
│   │   └── IPAI_AI_PLATFORM_ORD.md
│   ├── pages
│   │   ├── architecture.md
│   │   ├── developer-guide.md
│   │   ├── getting-started.md
│   │   ├── index.md
│   │   ├── modules.md
│   │   └── runbooks.md
│   ├── ppm
│   │   ├── architecture.md
│   │   ├── data-dictionary.md
│   │   └── runbook.md
│   ├── prd
│   │   ├── end_state
│   │   │   ├── AIUX_SHIP_v1.1.0.json
│   │   │   └── AIUX_SHIP_v1.1.0_PARAMETERIZED.json
│   │   ├── AIUX_SHIP_PRD_v1.1.0.md
│   │   ├── END_STATE_SPEC.json
│   │   ├── IPAI_SHIP_PRD_ODOO18_AIUX.md
│   │   ├── ODOO18_DO_FRESH_REDEPLOY.md
│   │   └── aiux_ship_end_state.v1.1.0.json
│   ├── proofs
│   │   └── PROD_DEPLOY_PROOF_SCHEMA.json
│   ├── rationalization
│   │   ├── EXECUTION_CHECKLIST.md
│   │   └── README.md
│   ├── releases
│   │   ├── DEPLOYMENT_PROOFS
│   │   │   ├── prod-20260109-2219
│   │   │   ├── README.md
│   │   │   ├── api_compare.json
│   │   │   ├── api_deployments.json
│   │   │   ├── api_release_latest.json
│   │   │   ├── api_workflow_run_20867798233.json
│   │   │   ├── api_workflow_runs.json
│   │   │   ├── artifacts_index.json
│   │   │   ├── deploy_run_166.json
│   │   │   ├── deploy_run_166_jobs.json
│   │   │   ├── graphql_commits_prs.json
│   │   │   └── release_tag_prod-20260106-1741.json
│   │   ├── prod-20260109-1642
│   │   │   ├── DEPLOYMENT_PROOFS
│   │   │   ├── GO_LIVE_MANIFEST.md
│   │   │   ├── WHAT_SHIPPED.json
│   │   │   └── WHAT_SHIPPED.md
│   │   ├── GO_LIVE_MANIFEST.md
│   │   ├── GO_LIVE_MANIFEST_prod-20260109-2219.md
│   │   ├── LATEST.json
│   │   ├── LATEST.md
│   │   ├── TBWA_FINOPS_INVITE_EMAIL.md
│   │   ├── TBWA_FINOPS_V1_RUNBOOK.md
│   │   ├── WHAT_DEPLOYED.json
│   │   ├── WHAT_DEPLOYED.md
│   │   ├── WHAT_DEPLOYED_prod-20260109-2219.json
│   │   ├── WHAT_DEPLOYED_prod-20260109-2219.md
│   │   ├── WHAT_SHIPPED.json
│   │   └── WHAT_SHIPPED.md
│   ├── repo
│   │   ├── GIT_STATE.prod.txt
│   │   ├── REPO_SNAPSHOT.prod.json
│   │   ├── REPO_TREE.prod.md
│   │   └── WORKOS_REPO_TREE.prod.md
│   ├── research
│   │   └── figma-design-automation
│   │       ├── automation_blueprint.md
│   │       ├── deep_report.md
│   │       ├── integration_stack.md
│   │       ├── lifecycle_map.md
│   │       ├── research_sources.md
│   │       └── skills_matrix.json
│   ├── runbooks
│   │   ├── DOCKER_DESKTOP_CLEANUP.md
│   │   ├── DOCKER_STAGING_CLEANUP.md
│   │   └── PROD_RUNBOOK_ODOO.md
│   ├── runtime
│   │   ├── ADDONS_PATH.prod.txt
│   │   ├── CONTAINER_PATH_CHECK.prod.txt
│   │   ├── HTTP_SITEMAP.prod.json
│   │   ├── IPAI_MODULE_STATUS.prod.txt
│   │   ├── MODULE_STATES.prod.csv
│   │   ├── ODOO_ACTIONS.prod.json
│   │   ├── ODOO_MENU_SITEMAP.prod.json
│   │   ├── ODOO_MODEL_SNAPSHOT.prod.json
│   │   ├── WORKOS_MODELS.prod.json
│   │   └── WORKOS_MODULES.prod.csv
│   ├── seed-data
│   │   └── EXPORT_TEMPLATES.md
│   ├── state_machines
│   │   ├── odoo
│   │   │   ├── ask_ai_chat.md
│   │   │   ├── document_upload.md
│   │   │   ├── grid_view_controller.md
│   │   │   └── superset_embed.md
│   │   ├── scout
│   │   │   ├── auth_session.md
│   │   │   ├── copilot_session.md
│   │   │   ├── offline_queue.md
│   │   │   └── realtime_subscription.md
│   │   ├── superset
│   │   │   ├── chart_query_lifecycle.md
│   │   │   ├── dashboard_filtering.md
│   │   │   └── embed_guest_token.md
│   │   └── README.md
│   ├── templates
│   │   └── ipai-ops-stack
│   │       ├── caddy
│   │       ├── docker
│   │       ├── scripts
│   │       └── README.md
│   ├── troubleshooting
│   │   ├── DBFILTER_FIX.md
│   │   └── MAGIC_LINK_500_ERROR.md
│   ├── tutorials
│   │   └── jinja2-basics
│   │       ├── examples
│   │       └── README.md
│   ├── wiki
│   │   ├── Architecture.md
│   │   ├── Configuration.md
│   │   ├── Diagrams.md
│   │   ├── Home.md
│   │   ├── Infrastructure.md
│   │   ├── Installation.md
│   │   ├── Modules-and-Features.md
│   │   ├── README.md
│   │   ├── Releases-and-Changelog.md
│   │   ├── cap-ai-agents.md
│   │   └── cap-approvals.md
│   ├── workflows
│   │   └── hire-to-retire-bpmn.html
│   ├── 003-odoo-ce-custom-image-spec.md
│   ├── AGENTIC_CLOUD_PRD.md
│   ├── AGENT_FRAMEWORK_SESSION_REPORT.md
│   ├── AGENT_MEMORY_DEPLOYMENT.md
│   ├── AGENT_TROUBLESHOOTING_PLAYBOOK.md
│   ├── AIUX_SHIP_PRD.md
│   ├── AI_MODULE_NAMING_CONVENTION.md
│   ├── APP_ICONS_README.md
│   ├── AUTOMATED_TROUBLESHOOTING_GUIDE.md
│   ├── CANONICAL_ENFORCEMENT_REPORT.md
│   ├── CANONICAL_LINT.md
│   ├── CANONICAL_MAP.md
│   ├── CE_OCA_EQUIVALENTS_AUDIT.md
│   ├── CE_OCA_PROJECT_STACK.md
│   ├── CLAUDE_CODE_SETUP.md
│   ├── CUSTOM_IMAGE_SUCCESS_CRITERIA.md
│   ├── DB_TUNING.md
│   ├── DELIVERABLES_MANIFEST.md
│   ├── DEPLOYMENT.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── DEPLOYMENT_INVARIANTS.md
│   ├── DEPLOYMENT_NAMING_MATRIX.md
│   ├── DEPLOYMENT_SUMMARY.md
│   ├── DEPLOY_NOTION_WORKOS.md
│   ├── DEVELOPER_TOOLS.md
│   ├── DIGITALOCEAN_EMAIL_SETUP.md
│   ├── DIGITALOCEAN_SMTP_UNBLOCK_REQUEST.md
│   ├── DIGITALOCEAN_VALIDATION_FRAMEWORK.md
│   ├── DIRECTIONAL_SYNC.md
│   ├── DNS_SETTINGS.md
│   ├── DOCKERFILE_COMPARISON.md
│   ├── DOCKER_CANONICAL_DIFF.md
│   ├── DOCKER_CD_MIGRATION_GUIDE.md
│   ├── DOCKER_SIMPLE_EXPLANATION.md
│   ├── DOCKER_SSOT_ARCHITECTURE.md
│   ├── DOCKER_VALIDATION_GUIDE.md
│   ├── DOKS_DEPLOYMENT_SUCCESS_CRITERIA.md
│   ├── ECOSYSTEM_GUIDE.md
│   ├── EE_IAP_TO_OCA_IPAI_MAPPING.md
│   ├── EE_TO_CE_OCA_MAPPING.md
│   ├── EMAIL_AND_OAUTH_SETUP.md
│   ├── ENTERPRISE_FEATURE_GAP.yaml
│   ├── EXECUTIVE_SUMMARY.md
│   ├── FEATURE_CHEQROOM_PARITY.md
│   ├── FEATURE_CONCUR_PARITY.md
│   ├── FEATURE_WORKSPACE_PARITY.md
│   ├── FINAL_DEPLOYMENT_GUIDE.md
│   ├── FINAL_OPERABILITY_CHECKLIST.md
│   ├── FINAL_READINESS_CHECK.md
│   ├── FINANCE_PPM_IMPLEMENTATION.md
│   ├── FIN_WORKSPACE_AUTOMATION_STATUS.md
│   ├── FIN_WORKSPACE_HARDENING_STATUS.md
│   ├── FIN_WORKSPACE_SETUP.md
│   ├── GANTT_TO_ODOO_CE_MAPPING.md
│   ├── GITHUB_SECRETS_SETUP.md
│   ├── GIT_WORKTREE_STRATEGY.md
│   ├── GO_LIVE_CHECKLIST.md
│   ├── GO_LIVE_CHECKLIST_ODOO18_IPAI.md
│   ├── GO_LIVE_PRODUCTION_CHECKLIST.md
│   ├── HEALTH_CHECK.md
│   ├── IMAGE_GUIDE.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── INDEX.md
│   ├── INDUSTRY_PACKS_OCA_DEPENDENCIES.md
│   ├── INDUSTRY_PARITY_ANALYSIS.md
│   ├── INFRASTRUCTURE_CHECKLIST.md
│   ├── IPAI_MODULES_INDEX.md
│   ├── IPAI_MODULE_INSTALLATION_ORDER.md
│   ├── KEYCLOAK_IDENTITY_PROVIDER_DEPLOYMENT.md
│   ├── KUBERNETES_MIGRATION_SPECIFICATION.md
│   ├── MAILGUN_DNS_SETUP.md
│   ├── MATTERMOST_ALERTING_SETUP.md
│   ├── MATTERMOST_CHATOPS_DEPLOYMENT.md
│   ├── MCP_IMPLEMENTATION_STATUS.md
│   ├── MCP_SUPABASE_INTEGRATION.md
│   ├── MIXED_CONTENT_FIX.md
│   ├── MODULE_CONSOLIDATION_GUIDE.md
│   ├── MODULE_STATUS_FINAL.md
│   ├── MODULE_STATUS_REPORT.md
│   ├── MONOREPO_STRUCTURE.md
│   ├── MVP_GO_LIVE_CHECKLIST.md
│   ├── N8N_CREDENTIALS_BOOTSTRAP.md
│   ├── NAMING_CONVENTION_EQ_APP_TOOLS.md
│   ├── OCA_CHORE_SCOPE.md
│   ├── OCA_INSTALLATION_GUIDE.md
│   ├── OCA_MIGRATION.md
│   ├── OCA_STYLE_CONTRACT.md
│   ├── OCA_TEMPLATE_INTEGRATION.md
│   ├── ODOO18_ENTERPRISE_TO_CE_OCA_MAPPING.md
│   ├── ODOO_18_CE_CHEATSHEET.md
│   ├── ODOO_18_CE_MODULE_INSTALL_ORDER.md
│   ├── ODOO_18_EE_TO_CE_OCA_PARITY.md
│   ├── ODOO_ADDONS_PATH_CONFIGURATION.md
│   ├── ODOO_APPS_CATALOG.md
│   ├── ODOO_ARCHITECT_PERSONA.md
│   ├── ODOO_CE_DEPLOYMENT_SUMMARY.md
│   ├── ODOO_CE_v0.9.0_SECURITY_AUDIT_REPORT.md
│   ├── ODOO_COPILOT_THEME_TOKEN_MAP.md
│   ├── ODOO_GOLIVE_SETTINGS_INVENTORY.md
│   ├── ODOO_HTTPS_OAUTH_TROUBLESHOOTING.md
│   ├── ODOO_IMAGE_SPEC.md
│   ├── ODOO_MODULE_DEPLOYMENT.md
│   ├── ODOO_PROGRAMMATIC_CONFIG.md
│   ├── OFFICIAL_ALIGNMENT.md
│   ├── OFFICIAL_TYPOLOGY.md
│   ├── OFFLINE_TARBALL_DEPLOYMENT.md
│   ├── PRD_ipai_ppm_portfolio.md
│   ├── PRODUCTION_DEFAULTS.md
│   ├── PRODUCTION_DEPLOYMENT_CHECKLIST.md
│   ├── PRODUCTION_HOTFIX.md
│   ├── PROD_READINESS_GAPS.md
│   ├── PROD_SNAPSHOT_MANIFEST.md
│   ├── PROGRAMMATIC_CONFIG_PLAN.md
│   ├── QUICK_REFERENCE_SSO_SETUP.md
│   ├── QUICK_START.md
│   ├── RAG_ARCHITECTURE_IMPLEMENTATION_PLAN.md
│   ├── README.md
│   ├── README_MCP_STACK.md
│   ├── RELEASE_NOTES_GO_LIVE.md
│   ├── REPO_SNAPSHOT.json
│   ├── REPO_TREE.contract.md
│   ├── REPO_TREE.generated.md
│   ├── SAAS_PARITY_READINESS.md
│   ├── SECRETS_NAMING_AND_STORAGE.md
│   ├── SEMANTIC_VERSIONING_STRATEGY.md
│   ├── SHIP_v1.1.0_SUMMARY.md
│   ├── SITEMAP.md
│   ├── SMTP_SETUP_SUMMARY.md
│   ├── SSO_VALIDATION_CHECKLIST.md
│   ├── STAGING.md
│   ├── SUCCESS_CRITERIA.md
│   ├── SUPERSET_INTEGRATION.md
│   ├── SUPERSET_PPM_ANALYTICS_GUIDE.md
│   ├── TAGGING_STRATEGY.md
│   ├── TBWA_THEME_DEPLOYMENT.md
│   ├── TECHNICAL_GUIDE_SUPABASE_INTEGRATION.md
│   ├── TENANT_ARCHITECTURE.md
│   ├── TESTING_ODOO_18.md
│   ├── TROUBLESHOOTING.md
│   ├── VERIFIED_MEMORY.md
│   ├── WBS_LOGFRAME_MAPPING.md
│   ├── WORKOS_DEPLOYMENT_MANIFEST.md
│   ├── ZOHO_DNS_SETUP.md
│   ├── branch-cleanup-analysis.md
│   ├── llms.txt
│   ├── notion-odoo-substitute-catalog.md
│   ├── oca_project_modules_18.csv
│   ├── odoo-apps-parity.md
│   ├── odoo_core_schema.sql
│   ├── supabase-integration.md
│   └── v0.9.1_DEPLOYMENT_GUIDE.md
├── docs-assistant
│   ├── api
│   │   ├── Dockerfile
│   │   ├── answer_engine.py
│   │   └── requirements.txt
│   ├── deploy
│   │   ├── .env.example
│   │   ├── deploy.sh
│   │   └── setup-database.sh
│   ├── mcp
│   │   └── docs_assistant.py
│   ├── web
│   │   └── docs-widget.js
│   └── DEPLOYMENT_GUIDE.md
├── engines
│   ├── _template
│   │   └── engine.yaml
│   ├── doc-ocr
│   │   └── engine.yaml
│   ├── retail-intel
│   │   └── engine.yaml
│   └── te-cheq
│       └── engine.yaml
├── external-src
│   ├── account-closing
│   ├── account-financial-reporting
│   ├── account-financial-tools
│   ├── account-invoicing
│   ├── calendar
│   ├── contract
│   ├── dms
│   ├── hr-expense
│   ├── maintenance
│   ├── project
│   ├── purchase-workflow
│   ├── reporting-engine
│   ├── server-tools
│   └── web
├── handbook
│   ├── compliance
│   │   └── bir
│   │       └── calendar.md
│   ├── finance
│   │   ├── month-end
│   │   │   └── checklist.md
│   │   └── policies
│   │       └── spending.md
│   ├── .gitbook.yaml
│   ├── README.md
│   └── SUMMARY.md
├── infra
│   ├── ai
│   │   └── provider_router
│   │       ├── README.md
│   │       ├── __init__.py
│   │       ├── requirements.txt
│   │       ├── router.py
│   │       └── test_router.py
│   ├── azure
│   │   ├── modules
│   │   │   ├── appservice.bicep
│   │   │   ├── databricks.bicep
│   │   │   ├── keyvault.bicep
│   │   │   └── storage.bicep
│   │   ├── parameters
│   │   │   ├── dev.parameters.json
│   │   │   └── prod.parameters.json
│   │   └── main.bicep
│   ├── caddy
│   │   └── Caddyfile
│   ├── ce
│   │   └── .gitkeep
│   ├── ci
│   │   ├── continue-plus
│   │   │   ├── README.md
│   │   │   ├── odoo-paths-ignore.yml
│   │   │   ├── preflight-classify.yml
│   │   │   └── spec-kit-check.yml
│   │   ├── install-test.sh
│   │   ├── structure-check.sh
│   │   └── structure_check.py
│   ├── databricks
│   │   ├── notebooks
│   │   │   ├── bronze
│   │   │   ├── gold
│   │   │   └── silver
│   │   ├── resources
│   │   │   ├── jobs.yml
│   │   │   └── schemas.yml
│   │   └── databricks.yml
│   ├── dns
│   │   └── mailgun_dns_records.md
│   ├── docker
│   │   ├── DOCKER_DESKTOP_SSOT.yaml
│   │   ├── DOCKER_STAGING_SSOT.yaml
│   │   └── odoo.conf
│   ├── doctl
│   │   └── export_state.sh
│   ├── entrypoint.d
│   │   └── .gitkeep
│   ├── lakehouse
│   │   ├── init
│   │   │   └── postgres
│   │   ├── trino
│   │   │   └── catalog
│   │   ├── .env.example
│   │   ├── README.md
│   │   └── compose.lakehouse.yml
│   ├── links
│   │   └── collab-stack.md
│   ├── mattermost
│   │   └── channel_setup.json
│   ├── stack
│   │   ├── .env.example
│   │   └── compose.stack.yml
│   ├── superset
│   │   ├── Dockerfile
│   │   ├── PRESET_PARITY_ROADMAP.md
│   │   ├── README.md
│   │   ├── do-app-spec.yaml
│   │   ├── entrypoint.sh
│   │   ├── manifest.json
│   │   ├── superset_config.py
│   │   └── virtual_datasets.sql
│   ├── .env.example
│   ├── docker-compose.prod.yaml
│   └── odoo.conf
├── inventory
│   ├── latest -> runs/20251231T020517Z
│   └── runs
│       ├── 20251231T015431Z
│       │   ├── apps."a962affc-f005-4b25-9c01-3c6b63dce52c".json
│       │   └── apps.list.json
│       ├── 20251231T015708Z
│       │   ├── apps."a962affc-f005-4b25-9c01-3c6b63dce52c".json
│       │   └── apps.list.json
│       ├── 20251231T015728Z
│       │   ├── agents.list.json
│       │   ├── apps.115a9584-75a3-4974-bb73-8f34b5cec6c9.json
│       │   ├── apps.6e33fbd8-d31d-4bf0-900e-e54642d48e3c.json
│       │   ├── apps.73af11cb-dab2-4cb1-9770-291c536531e6.json
│       │   ├── apps.7bfabd64-5b56-4222-9403-3d4cf3b23209.json
│       │   ├── apps.844b0bb2-0208-4694-bf86-12e750b7f790.json
│       │   ├── apps.9e89ce8b-e6f8-4403-af8c-8f1ca593639d.json
│       │   ├── apps.a962affc-f005-4b25-9c01-3c6b63dce52c.json
│       │   ├── apps.d77ba558-e72f-494e-a439-b27a563aeb42.json
│       │   ├── apps.de36bfbc-86a3-4293-836b-78b236bca899.json
│       │   ├── apps.list.json
│       │   ├── domains.list.json
│       │   └── droplets.list.json
│       ├── 20251231T015829Z
│       │   ├── agents.list.json
│       │   ├── apps.115a9584-75a3-4974-bb73-8f34b5cec6c9.json
│       │   ├── apps.6e33fbd8-d31d-4bf0-900e-e54642d48e3c.json
│       │   ├── apps.73af11cb-dab2-4cb1-9770-291c536531e6.json
│       │   ├── apps.7bfabd64-5b56-4222-9403-3d4cf3b23209.json
│       │   ├── apps.844b0bb2-0208-4694-bf86-12e750b7f790.json
│       │   ├── apps.9e89ce8b-e6f8-4403-af8c-8f1ca593639d.json
│       │   ├── apps.a962affc-f005-4b25-9c01-3c6b63dce52c.json
│       │   ├── apps.d77ba558-e72f-494e-a439-b27a563aeb42.json
│       │   ├── apps.de36bfbc-86a3-4293-836b-78b236bca899.json
│       │   ├── apps.list.json
│       │   ├── databases.list.json
│       │   ├── droplets.list.json
│       │   └── projects.list.json
│       ├── 20251231T015909Z
│       │   ├── agents.list.json
│       │   ├── apps.115a9584-75a3-4974-bb73-8f34b5cec6c9.json
│       │   ├── apps.6e33fbd8-d31d-4bf0-900e-e54642d48e3c.json
│       │   ├── apps.73af11cb-dab2-4cb1-9770-291c536531e6.json
│       │   ├── apps.7bfabd64-5b56-4222-9403-3d4cf3b23209.json
│       │   ├── apps.844b0bb2-0208-4694-bf86-12e750b7f790.json
│       │   ├── apps.9e89ce8b-e6f8-4403-af8c-8f1ca593639d.json
│       │   ├── apps.a962affc-f005-4b25-9c01-3c6b63dce52c.json
│       │   ├── apps.d77ba558-e72f-494e-a439-b27a563aeb42.json
│       │   ├── apps.de36bfbc-86a3-4293-836b-78b236bca899.json
│       │   ├── apps.list.json
│       │   ├── databases.list.json
│       │   ├── droplets.list.json
│       │   └── projects.list.json
│       └── 20251231T020517Z
│           ├── agents.list.json
│           ├── apps.115a9584-75a3-4974-bb73-8f34b5cec6c9.json
│           ├── apps.6e33fbd8-d31d-4bf0-900e-e54642d48e3c.json
│           ├── apps.73af11cb-dab2-4cb1-9770-291c536531e6.json
│           ├── apps.7bfabd64-5b56-4222-9403-3d4cf3b23209.json
│           ├── apps.844b0bb2-0208-4694-bf86-12e750b7f790.json
│           ├── apps.9e89ce8b-e6f8-4403-af8c-8f1ca593639d.json
│           ├── apps.a962affc-f005-4b25-9c01-3c6b63dce52c.json
│           ├── apps.d77ba558-e72f-494e-a439-b27a563aeb42.json
│           ├── apps.de36bfbc-86a3-4293-836b-78b236bca899.json
│           ├── apps.list.json
│           ├── databases.list.json
│           ├── droplets.list.json
│           └── projects.list.json
├── kb
│   ├── audit
│   │   └── AGENT_AUDIT_RULES.md
│   ├── design_system
│   │   └── tokens.yaml
│   ├── finance_close
│   │   └── sop.md
│   └── parity
│       ├── baseline.json
│       └── rubric.json
├── mattermost
│   ├── runbooks
│   │   └── .gitkeep
│   └── webhook-templates
│       └── .gitkeep
├── mcp
│   ├── coordinator
│   │   ├── app
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── main.py
│   │   │   └── routing.py
│   │   ├── infra
│   │   │   └── do
│   │   ├── DEPLOYMENT.md
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   └── requirements.txt
│   ├── local
│   │   ├── app
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── main.py
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   └── requirements.txt
│   ├── n8n-mcp
│   │   └── server.py
│   ├── odoo-mcp
│   │   ├── config.yaml
│   │   └── server.py
│   ├── servers
│   │   ├── agent-coordination-server
│   │   │   ├── src
│   │   │   ├── README.md
│   │   │   ├── package.json
│   │   │   └── tsconfig.json
│   │   ├── digitalocean-mcp-server
│   │   │   ├── src
│   │   │   ├── package.json
│   │   │   └── tsconfig.json
│   │   ├── mcp-jobs
│   │   │   ├── app
│   │   │   ├── components
│   │   │   ├── contexts
│   │   │   ├── hooks
│   │   │   ├── public
│   │   │   ├── spec
│   │   │   ├── styles
│   │   │   ├── ui
│   │   │   ├── .gitignore
│   │   │   ├── LOCKFILE_FIX_REPORT.md
│   │   │   ├── PLATFORM_KIT_SETUP.md
│   │   │   ├── README.md
│   │   │   ├── VERCEL_BUILD_FIX_SUMMARY.md
│   │   │   ├── components.json
│   │   │   ├── next.config.mjs
│   │   │   ├── package-lock.json
│   │   │   ├── package.json
│   │   │   ├── postcss.config.mjs
│   │   │   └── tsconfig.json
│   │   ├── memory-mcp-server
│   │   │   ├── src
│   │   │   ├── package.json
│   │   │   └── tsconfig.json
│   │   ├── odoo-erp-server
│   │   │   ├── src
│   │   │   ├── .env.example
│   │   │   ├── README.md
│   │   │   ├── package.json
│   │   │   └── tsconfig.json
│   │   ├── pulser-mcp-server
│   │   │   ├── src
│   │   │   ├── package.json
│   │   │   └── tsconfig.json
│   │   ├── speckit-mcp-server
│   │   │   ├── src
│   │   │   ├── package.json
│   │   │   └── tsconfig.json
│   │   ├── superset-mcp-server
│   │   │   ├── src
│   │   │   ├── package.json
│   │   │   └── tsconfig.json
│   │   ├── vercel-mcp-server
│   │   │   ├── src
│   │   │   ├── package.json
│   │   │   └── tsconfig.json
│   │   ├── odoo-erp.yaml
│   │   └── odoo-lab.yaml
│   └── agentic-cloud.yaml
├── n8n
│   ├── workflows
│   │   ├── .gitkeep
│   │   ├── deployment-notify.json
│   │   └── github-deploy-trigger.json
│   └── n8n_tenant_provisioning.json
├── notion-n8n-monthly-close
│   ├── scripts
│   │   ├── deduplicate_closing_tasks.py
│   │   ├── n8n-sync.sh
│   │   └── verify_finance_stack.sh
│   ├── src
│   │   ├── api
│   │   │   └── searchMonthlyRevenueInsights.ts
│   │   ├── components
│   │   │   └── MonthlyRevenueSearch.tsx
│   │   └── index.ts
│   ├── supabase
│   │   ├── functions
│   │   │   ├── closing-snapshot
│   │   │   ├── embed-monthly-revenue
│   │   │   └── search-monthly-revenue
│   │   └── SUPABASE_DEPLOYMENT.md
│   ├── workflows
│   │   ├── odoo
│   │   │   ├── W001_OD_MNTH_CLOSE_SYNC.json
│   │   │   ├── W002_OD_BIR_ALERTS.json
│   │   │   ├── W401_CC_EXPENSE_IMPORT.json
│   │   │   ├── W501_EQ_BOOKING_SYNC.json
│   │   │   └── W902_OD_VIEW_HEALTHCHECK.json
│   │   ├── supabase
│   │   │   └── W101_SB_CLOSE_SNAPSHOT.json
│   │   ├── ODOO_BIR_PREP.json
│   │   ├── ODOO_EXPENSE_OCR.json
│   │   ├── ODOO_KNOWLEDGE_GOV.json
│   │   ├── README.md
│   │   ├── W150_FINANCE_HEALTH_CHECK.json
│   │   └── index.yaml
│   ├── DEPLOYMENT_STATUS.md
│   ├── DEPLOYMENT_SUMMARY.md
│   ├── N8N_CLI_README.md
│   └── WORKFLOW_CONVENTIONS.md
├── oca
│   ├── .gitkeep
│   └── oca_modules.yaml
├── ocr-adapter
│   ├── scripts
│   │   ├── README.md
│   │   ├── ground_truth_example.csv
│   │   └── test-harness.py
│   ├── test_receipts
│   │   ├── receipt_CXE000000040236295.jpg
│   │   └── sample_ph_receipt.png
│   ├── .gitignore
│   ├── DEPLOYMENT.md
│   ├── Dockerfile
│   ├── README.md
│   ├── main.py
│   ├── nginx-site.conf
│   ├── requirements.txt
│   └── test-ocr.sh
├── odoo
│   ├── ODOO_INTEGRATION_MAP.md
│   └── ipai_finance_closing_seed.json
├── odoo-schema-mirror
│   ├── tests
│   │   ├── __init__.py
│   │   ├── test_export_odoo_schema.py
│   │   ├── test_generate_dbml.py
│   │   └── test_sync_to_supabase.py
│   ├── .env.example
│   ├── export_odoo_schema.py
│   ├── generate_dbml.py
│   ├── requirements.txt
│   ├── sync_to_supabase.py
│   └── validate_parity.py
├── ops
│   ├── github
│   │   ├── apply_labels.sh
│   │   └── labels.json
│   ├── jobs
│   │   └── odoo
│   │       ├── finance_stack_rollout.yaml
│   │       ├── ipai_finance_ppm_install.yaml
│   │       └── ipai_finance_ppm_upgrade.yaml
│   ├── runbooks
│   │   ├── expenses_ocr_runbook.md
│   │   ├── mailgun_domain_verification.md
│   │   ├── ocr_service.md
│   │   └── sinch_setup.md
│   ├── DISASTER_RECOVERY.md
│   └── backup-production.sh
├── ops-control
│   ├── apps
│   │   └── mcp-server
│   │       ├── src
│   │       ├── README.md
│   │       ├── package.json
│   │       └── tsconfig.json
│   ├── docs
│   │   ├── ADAPTER_GUIDE.md
│   │   ├── DEMO_MODE.md
│   │   ├── DEPLOYMENT_CHECKLIST.md
│   │   ├── DEVELOPER_GUIDE.md
│   │   ├── GITHUB_FIRST_PATTERN.md
│   │   ├── INDEX.md
│   │   └── QUICK_REFERENCE.md
│   ├── guidelines
│   │   └── Guidelines.md
│   ├── odoo_modules
│   │   ├── docs
│   │   │   └── AI_RESPONSE_SCHEMA.md
│   │   ├── ipai_ask_ai
│   │   │   ├── controllers
│   │   │   ├── data
│   │   │   ├── models
│   │   │   ├── security
│   │   │   ├── static
│   │   │   ├── views
│   │   │   ├── wizards
│   │   │   ├── __init__.py
│   │   │   └── __manifest__.py
│   │   ├── ipai_ask_ai_chatter
│   │   │   ├── static
│   │   │   ├── __init__.py
│   │   │   └── __manifest__.py
│   │   └── ipai_platform_theme
│   │       ├── static
│   │       ├── __init__.py
│   │       └── __manifest__.py
│   ├── packages
│   │   ├── core
│   │   │   ├── src
│   │   │   └── package.json
│   │   └── ui
│   │       ├── src
│   │       └── package.json
│   ├── scripts
│   │   └── validate_spec_kit.py
│   ├── spec
│   │   ├── continue-orchestrator
│   │   │   ├── constitution.md
│   │   │   ├── plan.md
│   │   │   ├── prd.md
│   │   │   └── tasks.md
│   │   ├── ops-control-room
│   │   │   ├── constitution.md
│   │   │   ├── plan.md
│   │   │   ├── prd.md
│   │   │   └── tasks.md
│   │   └── README.md
│   ├── src
│   │   ├── app
│   │   │   ├── components
│   │   │   └── App.tsx
│   │   ├── core
│   │   │   ├── execute.ts
│   │   │   ├── index.ts
│   │   │   ├── parse.ts
│   │   │   ├── runbooks.ts
│   │   │   └── types.ts
│   │   ├── styles
│   │   │   ├── fonts.css
│   │   │   ├── index.css
│   │   │   ├── tailwind.css
│   │   │   └── theme.css
│   │   └── main.tsx
│   ├── supabase
│   │   ├── functions
│   │   │   ├── ops-executor
│   │   │   └── server
│   │   ├── migrations
│   │   │   └── README.md
│   │   └── config.toml
│   ├── utils
│   │   └── supabase
│   │       └── info.tsx
│   ├── workers
│   │   ├── README.md
│   │   ├── ocr-worker.ts
│   │   └── package.json
│   ├── workflows
│   │   └── spec-kit-enforce.yml
│   ├── ACTION_PLAN.md
│   ├── ATTRIBUTIONS.md
│   ├── COMMANDS.md
│   ├── DATABASE_FIX_SUMMARY.md
│   ├── DATABASE_SETUP_FIXED.md
│   ├── DEPENDENCY_FIX.md
│   ├── DEPLOY.md
│   ├── DOCUMENTATION_INDEX.md
│   ├── ENV_GRACEFUL_FIX.md
│   ├── ENV_SETUP.md
│   ├── FIGMA_MAKE_DEPLOY.md
│   ├── FIXED.md
│   ├── FIX_DATABASE_ERRORS.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── IMPLEMENTATION_SUMMARY_JAN7.md
│   ├── MIGRATION_SETUP.md
│   ├── MIGRATION_TO_PUBLIC_SCHEMA.md
│   ├── NEXT_STEPS.md
│   ├── OCR_IMPLEMENTATION.md
│   ├── PACKAGE_JSON_FIX.md
│   ├── PARALLEL_OCR_SETUP.md
│   ├── PARALLEL_OCR_SUMMARY.md
│   ├── PHASED_IMPLEMENTATION_PLAN.md
│   ├── QUICKSTART.md
│   ├── QUICKSTART_OCR.md
│   ├── QUICK_FIX.md
│   ├── QUICK_REFERENCE.md
│   ├── README.md
│   ├── README_OCR.md
│   ├── SCHEMA_FIX_SUMMARY.md
│   ├── SCHEMA_FIX_V2_SUMMARY.md
│   ├── SECRETS_SETUP.md
│   ├── SETUP.md
│   ├── SPEC_KIT_CREATED.md
│   ├── START_HERE.md
│   ├── STATUS.md
│   ├── STRUCTURE.md
│   ├── SUPABASE_SETUP_GUIDE.md
│   ├── index.html
│   ├── package.json
│   ├── postcss.config.mjs
│   └── vite.config.ts
├── osi
│   ├── osi_template.json
│   └── osi_template.yaml
├── out
│   ├── concur_demo
│   │   └── catalog.json
│   ├── concur_demo_odoo_map
│   │   ├── mapping.csv
│   │   └── mapping.md
│   └── copilot_index
│       └── manifest.json
├── packages
│   ├── agent-core
│   │   ├── src
│   │   │   └── index.ts
│   │   └── package.json
│   ├── env-config
│   │   ├── src
│   │   │   └── index.ts
│   │   ├── package.json
│   │   └── tsconfig.json
│   ├── github-app
│   │   ├── src
│   │   │   └── server.ts
│   │   ├── .env.example
│   │   ├── package.json
│   │   └── tsconfig.json
│   ├── ipai-design-tokens
│   │   ├── src
│   │   │   ├── react
│   │   │   ├── build.ts
│   │   │   ├── material3Theme.ts
│   │   │   ├── odooTokens.ts
│   │   │   ├── tableauTokens.json
│   │   │   └── tableauTokens.ts
│   │   ├── material3-expressive.css
│   │   ├── package.json
│   │   ├── tableau.css
│   │   ├── tailwind-material3.preset.js
│   │   ├── tailwind-tableau.preset.js
│   │   ├── tailwind.preset.js
│   │   ├── tokens.css
│   │   └── tokens.scss
│   ├── saas-types
│   │   ├── prisma
│   │   │   └── schema.prisma
│   │   ├── src
│   │   │   └── index.ts
│   │   ├── package.json
│   │   └── tsconfig.json
│   └── supabase
│       └── functions
│           ├── auth-otp-request
│           └── auth-otp-verify
├── patches
│   └── ipai_ce_cleaner_xmlid_fix.diff
├── releasekit
│   ├── fastlane
│   │   ├── Appfile
│   │   ├── Fastfile
│   │   └── Gemfile
│   ├── scripts
│   │   ├── audit_android.sh
│   │   ├── audit_ios.sh
│   │   ├── build_android.sh
│   │   └── build_ios.sh
│   ├── store
│   │   ├── android
│   │   │   └── README.md
│   │   └── ios
│   │       └── README.md
│   └── README.md
├── sandbox
│   └── dev
│       ├── .claude
│       │   └── settings.local.json
│       ├── .github
│       │   └── workflows
│       ├── config
│       │   ├── .env.example
│       │   └── odoo.conf
│       ├── docs
│       │   └── runbooks
│       ├── scripts
│       │   ├── dev
│       │   └── verify.sh
│       ├── .env.example
│       ├── .gitignore
│       ├── CANONICAL_NAMING.md
│       ├── CLAUDE.md
│       ├── HOT_RELOAD_GUIDE.md
│       ├── IMPLEMENTATION_SUMMARY.md
│       ├── Makefile
│       ├── PRODUCTION_READY.md
│       ├── README.md
│       ├── REPORT.md
│       ├── docker-compose.production.yml
│       ├── docker-compose.yml
│       └── odoo.conf.production
├── scripts
│   ├── aiux
│   │   ├── verify_assets.sh
│   │   ├── verify_install.sh
│   │   └── verify_prod_health.sh
│   ├── auth
│   │   ├── confirm_user.py
│   │   └── set_password.ts
│   ├── ci
│   │   ├── audit_tree_tags.sh
│   │   ├── compare_audit_baseline.py
│   │   ├── constraints-gevent.txt
│   │   ├── deploy-ipai-modules.sh
│   │   ├── import-n8n-workflows.sh
│   │   ├── install-oca-modules.sh
│   │   ├── install_odoo_18.sh
│   │   ├── introspect_feature_inventory.py
│   │   ├── module_drift_gate.sh
│   │   ├── run_odoo_tests.sh
│   │   ├── schema_drift_check.sh
│   │   ├── verify-deployment.sh
│   │   └── wait_for_postgres.sh
│   ├── ci_gate
│   │   ├── compute_addons_roots.sh
│   │   ├── gate_modules.sh
│   │   └── module_gate.py
│   ├── deploy
│   │   ├── bootstrap_from_tag.sh
│   │   ├── deploy-prod-e2e.sh
│   │   ├── do-bootstrap-odoo-prod.sh
│   │   └── verify_prod.sh
│   ├── docs
│   │   └── sync_readme_current_state.py
│   ├── drive_sync
│   │   ├── lib
│   │   │   ├── export_doc_markdown.mjs
│   │   │   ├── google_auth.mjs
│   │   │   └── normalize_markdown.mjs
│   │   ├── README.md
│   │   ├── drive_manifest.yml
│   │   └── sync_docs.mjs
│   ├── fixes
│   │   └── fix_odoo_email_config.sh
│   ├── github
│   │   └── create_ee_replacement_issues.sh
│   ├── import
│   │   ├── import_activities.py
│   │   ├── run_import_sequence.sh
│   │   ├── validate_headers.py
│   │   ├── verify_import.py
│   │   └── verify_import.sh
│   ├── infra-discovery
│   │   ├── __init__.py
│   │   ├── discover_all.py
│   │   ├── discover_digitalocean.py
│   │   ├── discover_docker.py
│   │   ├── discover_github.py
│   │   ├── discover_odoo.py
│   │   ├── discover_supabase.py
│   │   └── discover_vercel.py
│   ├── kb
│   │   ├── seed_oca_catalog.sql
│   │   ├── seed_odoo_catalog.sql
│   │   └── seed_sap_catalog.sql
│   ├── lakehouse
│   │   ├── coverage_audit.py
│   │   ├── create_delta_tables_trino.sql
│   │   ├── mirror_gold_to_supabase.py
│   │   └── validate_contracts.py
│   ├── mailgun
│   │   ├── README.md
│   │   ├── send_test_email.sh
│   │   ├── setup_webhooks.sh
│   │   ├── test_smtp.sh
│   │   ├── verify_all.sh
│   │   ├── verify_dns.sh
│   │   └── verify_domain.sh
│   ├── odoo
│   │   ├── README_BOOTSTRAP.md
│   │   ├── bootstrap_companies.sh
│   │   ├── bootstrap_companies_min.sh
│   │   ├── company_bootstrap.py
│   │   ├── company_bootstrap_min.py
│   │   ├── company_bootstrap_xmlrpc.py
│   │   ├── diagnose_scss_error.sh
│   │   ├── fix_broken_action.sh
│   │   ├── install-ce-apps.sh
│   │   ├── install-oca-modules.sh
│   │   ├── purge_assets.sh
│   │   ├── verify-ce-apps.sh
│   │   ├── verify-full-parity.sh
│   │   └── verify-oca-modules.sh
│   ├── odoo-automation
│   │   ├── README.md
│   │   └── create_project_alias.py
│   ├── ppm
│   │   ├── deploy-databricks.sh
│   │   ├── run-dq-checks.sh
│   │   ├── setup-control-room.sh
│   │   ├── setup-notion-sync.sh
│   │   └── verify-all.sh
│   ├── prod
│   │   ├── deploy_workos.sh
│   │   └── verify_workos.sh
│   ├── seeds
│   │   ├── convert_expense_template_to_odoo.py
│   │   ├── generate_project_stack_csv.py
│   │   └── generate_project_stack_xlsx.py
│   ├── sql
│   │   └── update_phase_tags.sql
│   ├── sync
│   │   ├── docs-to-kb.js
│   │   ├── generate-sitemap.js
│   │   ├── generate-tree.js
│   │   ├── package.json
│   │   ├── schema-to-docs.js
│   │   ├── schema-to-openapi.js
│   │   ├── spec-to-prisma.js
│   │   └── sync-all.js
│   ├── FIX_OWLERROR_GUIDE.md
│   ├── README.md
│   ├── activate-n8n-workflows.sh
│   ├── apply-supabase-schema.sh
│   ├── assign_module_icons.py
│   ├── audit_email_config.py
│   ├── audit_installed_modules.py
│   ├── audit_ipai_modules.py
│   ├── audit_oca_modules.py
│   ├── auto_error_handler.sh
│   ├── backup_odoo.sh
│   ├── baseline-validation.sh
│   ├── bootstrap_apps_from_inventory.sh
│   ├── bootstrap_execution_board.sh
│   ├── bootstrap_github_issues.sh
│   ├── build_and_push_version.sh
│   ├── build_v0.10.0.sh
│   ├── build_v0.9.1.sh
│   ├── canonical_audit.py
│   ├── ce_oca_audit.py
│   ├── check-enterprise-modules.sh
│   ├── check_addon_allowlist.py
│   ├── check_go_live_manifest.py
│   ├── check_module_status.sh
│   ├── check_project_tasks.py
│   ├── check_undocumented_specs.py
│   ├── ci_local.sh
│   ├── ci_smoke_test.sh
│   ├── clean-branches.sh
│   ├── cleanup-branches.sh
│   ├── configure_base_url.py
│   ├── configure_gmail_smtp.py
│   ├── configure_gmail_smtp.sh
│   ├── configure_google_oauth.sh
│   ├── configure_mailgun_smtp.py
│   ├── configure_sendgrid_smtp.py
│   ├── configure_smtp.py
│   ├── configure_zoho_smtp.py
│   ├── convert_csv_to_xml.py
│   ├── convert_seed_to_xml.py
│   ├── copilot_ingest.py
│   ├── count_xml_seeds.py
│   ├── create-module-readme.sh
│   ├── create-release.sh
│   ├── db_verify.sh
│   ├── delete_user_safe.sh
│   ├── deploy-bir-compliance.sh
│   ├── deploy-december-2025-bir-tasks.sh
│   ├── deploy-mailgun-mailgate.sh
│   ├── deploy-n8n-workflows.sh
│   ├── deploy-odoo-modules.sh
│   ├── deploy-otp-auth.sh
│   ├── deploy-tbwa-theme-tokens.sh
│   ├── deploy-to-server.sh
│   ├── deploy_afc_rag.sh
│   ├── deploy_complete_fix.sh
│   ├── deploy_custom_image.sh
│   ├── deploy_notion_tasks.sh
│   ├── deploy_odoo_smart.sh
│   ├── deploy_odoo_upgrade.sh
│   ├── deploy_prod.sh
│   ├── deploy_with_credentials.sh
│   ├── deploy_workos_prod.sh
│   ├── deployment-checklist.sh
│   ├── diagnose_smtp.sh
│   ├── discover_digitalocean_infra.sh
│   ├── discover_docker_infra.sh
│   ├── discover_odoo_infra.py
│   ├── discover_supabase_infra.py
│   ├── docker-desktop-audit.sh
│   ├── docker-staging-audit.sh
│   ├── ee_replace_request.sh
│   ├── enhanced_health_check.sh
│   ├── erd_dot.sql
│   ├── erp_config_cli.sh
│   ├── execute_rationalization.sh
│   ├── export_todo_seed.py
│   ├── extract_remote_data.py
│   ├── finance_ppm_health_check.sh
│   ├── finance_ppm_health_check.sql
│   ├── finance_ppm_restore_golden.sh
│   ├── fix-finance-ppm-schema.sh
│   ├── fix-pay-invoices-online-error.py
│   ├── fix_oauth_button.sh
│   ├── fix_oauth_button_odoo_core.sh
│   ├── fix_odoo18_views.py
│   ├── fix_pos_enterprise_error.sh
│   ├── full_deploy_sanity.sh
│   ├── gen_addons_path.py
│   ├── gen_repo_tree.sh
│   ├── gen_repo_tree_fallback.sh
│   ├── generate_2026_finance_calendar.py
│   ├── generate_2026_schedule.py
│   ├── generate_erd_graphviz.py
│   ├── generate_finance_dashboard.py
│   ├── generate_go_live_checklist.py
│   ├── generate_llm_docs.py
│   ├── generate_module_docs.py
│   ├── generate_module_health_report.py
│   ├── generate_module_signatures.py
│   ├── generate_month_end_imports.py
│   ├── generate_odoo_dbml.py
│   ├── generate_odoo_template.py
│   ├── generate_release_docs.sh
│   ├── generate_repo_index.py
│   ├── generate_schema_artifacts.sh
│   ├── generate_seed_xml.py
│   ├── generate_shadow_ddl.py
│   ├── generate_spec_report.py
│   ├── healthcheck_odoo.sh
│   ├── hotfix_icon_crash.sh
│   ├── hotfix_production.sh
│   ├── image-diff-report.sh
│   ├── image_audit.sh
│   ├── import_month_end_tasks.py
│   ├── incident_snapshot.sh
│   ├── ingest_docs_to_supabase.py
│   ├── ingest_knowledge_graph.py
│   ├── install-git-hooks.sh
│   ├── install-notion-stack.sh
│   ├── install-odoo-18-modules.sh
│   ├── install_all_ipai_modules.sh
│   ├── install_baseline.sh
│   ├── install_finance_stack.sh
│   ├── install_ipai_finance_ppm.sh
│   ├── install_module_xmlrpc.py
│   ├── install_oauth_module.py
│   ├── install_oca_modules.sh
│   ├── install_oca_project_modules.sh
│   ├── introspect_project.py
│   ├── ipai_full_audit.py
│   ├── ipai_install_upgrade_test.sh
│   ├── ipai_quality_gate.sh
│   ├── map_logframe.py
│   ├── module_audit_agent.py
│   ├── new_conversation_entry.sh
│   ├── notify_slack.sh
│   ├── oca-bootstrap.sh
│   ├── oca-sync.sh
│   ├── oca-template-bootstrap.sh
│   ├── oca-update.sh
│   ├── oca_hydrate.sh
│   ├── odoo-18-oca-install.sh
│   ├── odoo_import_project_suite.py
│   ├── odoo_mattermost_integration.py
│   ├── odoo_rationalization.sh
│   ├── odoo_runtime_snapshot.sh
│   ├── odoo_smoke_close.sh
│   ├── odoo_update_modules.sh
│   ├── odoo_verify_modules.py
│   ├── package_image_tarball.sh
│   ├── parse_notion_tasks.py
│   ├── policy-check.sh
│   ├── pre_install_snapshot.sh
│   ├── prod_access_check.py
│   ├── prod_backup_dump.sh
│   ├── prod_db_guess.py
│   ├── promote_oauth_users.py
│   ├── provision_tenant.sh
│   ├── recreate_odoo_prod.sh
│   ├── release_gate.sh
│   ├── replace_seed_from_excel.py
│   ├── repo_health.sh
│   ├── report_ci_telemetry.sh
│   ├── report_stale_branches.sh
│   ├── run_clarity_ppm_reverse.sh
│   ├── run_odoo_migrations.sh
│   ├── run_odoo_shell.sh
│   ├── run_project_introspection.sh
│   ├── scan_ipai_modules.py
│   ├── seed_finance_close_from_xlsx.py
│   ├── seed_finance_ppm_stages.py
│   ├── setup-mailgun-secrets.sh
│   ├── setup_afc_rag.sh
│   ├── setup_keycloak_db.sh
│   ├── setup_mattermost_db.sh
│   ├── simple_deploy.sh
│   ├── smoketest.sh
│   ├── spec-kit-enforce.py
│   ├── spec_validate.sh
│   ├── stack_verify.sh
│   ├── staging_down.sh
│   ├── staging_restore_and_sanitize.sh
│   ├── staging_up.sh
│   ├── supabase_delete_user.sh
│   ├── sync-fluent-tokens.sh
│   ├── sync-tokens.sh
│   ├── sync_agent_memory.py
│   ├── sync_current_state.sh
│   ├── sync_directional.py
│   ├── sync_ipai_sample_metrics_to_supabase.py
│   ├── sync_odoo_shadow.py
│   ├── tenant_automation.py
│   ├── test-mailgun.py
│   ├── test-mailgun.sh
│   ├── test_afc_rag.py
│   ├── test_auth_bootstrap.sh
│   ├── test_deploy_local.sh
│   ├── test_email_flow.sh
│   ├── test_ipai_install_upgrade.py
│   ├── test_magic_link.sh
│   ├── update_diagram_manifest.py
│   ├── update_task_phase_tags.sh
│   ├── update_tasks_after_import.py
│   ├── validate-continue-config.sh
│   ├── validate-spec-kit.sh
│   ├── validate_ai_naming.py
│   ├── validate_ee_iap_independence.sh
│   ├── validate_ee_replacements.py
│   ├── validate_finance_ppm_data.py
│   ├── validate_ipai_doc_module_refs.py
│   ├── validate_m1.sh
│   ├── validate_manifest.py
│   ├── validate_manifests.py
│   ├── validate_production.sh
│   ├── validate_spec_kit.py
│   ├── verify-addon-permissions.sh
│   ├── verify-https.sh
│   ├── verify-odoo-18-oca.sh
│   ├── verify.sh
│   ├── verify_auth_setup.sh
│   ├── verify_backup.sh
│   ├── verify_email_auth.sh
│   ├── verify_local.sh
│   ├── verify_phase3.py
│   ├── verify_smtp.py
│   ├── verify_supabase_deploy.sh
│   ├── verify_web_assets.sh
│   ├── web_sandbox_verify.sh
│   ├── whats_deployed.py
│   ├── whats_deployed.sh
│   ├── wiki_sync.sh
│   ├── worktree-setup.sh
│   └── xmlrpc_set_admin_password.py
├── seed_export
│   ├── projects.csv
│   ├── stages.csv
│   ├── tags.csv
│   ├── tasks.csv
│   └── users.csv
├── seeds
│   ├── schema
│   │   ├── afc_tasks.schema.yaml
│   │   ├── afc_templates.schema.yaml
│   │   ├── afc_workstream.schema.yaml
│   │   ├── shared_calendars.schema.yaml
│   │   ├── stc_checks.schema.yaml
│   │   ├── stc_scenarios.schema.yaml
│   │   └── stc_workstream.schema.yaml
│   ├── scripts
│   │   ├── validate_seeds.sh
│   │   └── yaml_to_payload.py
│   ├── shared
│   │   ├── approval_policies.yaml
│   │   ├── calendars.yaml
│   │   ├── notification_profiles.yaml
│   │   ├── org_units.yaml
│   │   └── roles.yaml
│   ├── workstreams
│   │   ├── afc_financial_close
│   │   │   ├── 00_workstream.yaml
│   │   │   ├── 10_templates.yaml
│   │   │   ├── 20_tasks.yaml
│   │   │   ├── 30_checklists.yaml
│   │   │   ├── 40_kpis.yaml
│   │   │   ├── 50_roles_raci.yaml
│   │   │   └── 90_odoo_mapping.yaml
│   │   ├── project_stack
│   │   │   ├── csv
│   │   │   ├── 00_workstream.yaml
│   │   │   ├── 10_partners.yaml
│   │   │   ├── 20_analytic_accounts.yaml
│   │   │   ├── 30_products.yaml
│   │   │   ├── 40_projects.yaml
│   │   │   ├── 50_tags.yaml
│   │   │   ├── 60_stages.yaml
│   │   │   ├── 70_tasks.yaml
│   │   │   ├── 80_timesheets.yaml
│   │   │   ├── 90_odoo_mapping.yaml
│   │   │   └── project_stack_import.xlsx
│   │   └── stc_tax_compliance
│   │       ├── 00_workstream.yaml
│   │       ├── 10_worklist_types.yaml
│   │       ├── 20_compliance_checks.yaml
│   │       ├── 30_scenarios.yaml
│   │       ├── 60_localization_ph.yaml
│   │       └── 90_odoo_mapping.yaml
│   └── README.md
├── services
│   ├── notion-sync
│   │   ├── config
│   │   │   └── notion_mapping.yaml
│   │   ├── notion_sync
│   │   │   ├── __init__.py
│   │   │   ├── client.py
│   │   │   ├── config.py
│   │   │   ├── databricks_writer.py
│   │   │   ├── main.py
│   │   │   ├── models.py
│   │   │   ├── sync.py
│   │   │   └── transform.py
│   │   ├── tests
│   │   │   ├── __init__.py
│   │   │   ├── conftest.py
│   │   │   └── test_transform.py
│   │   ├── .env.example
│   │   ├── README.md
│   │   └── pyproject.toml
│   ├── ocr
│   │   ├── app
│   │   │   ├── main.py
│   │   │   └── pipeline.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── pm_api
│       ├── app
│       │   ├── __init__.py
│       │   └── main.py
│       ├── README.md
│       └── pyproject.toml
├── skillpack
│   └── manifest.json
├── skills
│   ├── bir-tax-filing
│   │   └── SKILL.md
│   ├── ci-run-validate
│   │   └── skill.yaml
│   ├── expense-processing
│   │   └── SKILL.md
│   ├── finance-month-end
│   │   └── SKILL.md
│   ├── finance-ppm-health
│   │   └── skill.yaml
│   ├── kg-entity-expand
│   │   └── skill.yaml
│   ├── odoo
│   │   ├── __init__.py
│   │   └── fetch_odoo_config_params.py
│   ├── odoo-module-audit
│   │   └── skill.yaml
│   ├── odoo-module-scaffold
│   │   └── skill.yaml
│   ├── superset
│   │   ├── __init__.py
│   │   ├── get_superset_embed_url.py
│   │   ├── get_superset_guest_token.py
│   │   └── validate_superset_health.py
│   ├── user
│   │   ├── figma-agent
│   │   │   ├── config
│   │   │   ├── examples
│   │   │   ├── templates
│   │   │   └── SKILL.md
│   │   └── supabase-schema-catalog
│   │       ├── catalog
│   │       ├── scripts
│   │       ├── AGENT_PERSONALITY.md
│   │       └── SKILL.md
│   ├── visio-drawio-export
│   │   ├── docker
│   │   │   ├── Dockerfile
│   │   │   ├── entrypoint.sh
│   │   │   └── package.json
│   │   ├── src
│   │   │   ├── convert.js
│   │   │   ├── diff.js
│   │   │   ├── export.js
│   │   │   ├── index.js
│   │   │   ├── parse.js
│   │   │   └── validate.js
│   │   ├── README.md
│   │   └── skill.yaml
│   ├── README.md
│   ├── architecture_diagrams.skill.json
│   ├── registry.yaml
│   ├── superset_mcp.skill.json
│   └── visio_drawio_export.skill.json
├── spec
│   ├── adk-control-room
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── auto-claude-framework
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── bir-tax-compliance
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── cicd-supabase-n8n
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── close-orchestration
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── continue-plus
│   │   ├── ALL_GREEN_CRITERIA.md
│   │   ├── EVALUATION_REPORT.md
│   │   ├── RUNBOOK.md
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── control-room-api
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── docs-platform-sapgrade
│   │   ├── api-contract.yaml
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── erp-saas-clone-suite
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── expense-automation
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── figma-dev-plugins-reverse
│   │   └── capabilities.md
│   ├── hire-to-retire
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── insightpulse-docs-ai
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── insightpulse-mobile
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── ipai-ai-platform
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── ipai-ai-platform-odoo18
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── ipai-control-center
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── ipai-copilot
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── ipai-month-end
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── ipai-odoo18-enterprise-patch
│   │   └── capability_map.yaml
│   ├── ipai-tbwa-finance
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── ipai_enterprise_bridge
│   │   └── ee-replacement-matrix.yaml
│   ├── kapa-plus
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── kapa-reverse
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── knowledge-graph
│   │   ├── constitution.md
│   │   ├── create-issues.sh
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── knowledge-hub
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── notion-finance-ppm-control-room
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── odoo-apps-inventory
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── odoo-ce
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── odoo-ce-enterprise-replacement
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── odoo-copilot-process-mining
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── odoo-mcp-server
│   │   ├── GAPS_ANALYSIS.md
│   │   ├── README.md
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   └── prd.md
│   ├── ops-control-room
│   │   ├── agents
│   │   │   └── figma-bridge.yaml
│   │   ├── runbooks
│   │   │   └── figma_sync_design_tokens.yaml
│   │   ├── DEPLOYMENT_INTEGRATION.md
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── parallel-control-planes
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── project-ce
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── pulser-master-control
│   │   ├── capability-registry.yaml
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── seed-bundle
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── supabase-platform-kit-observability
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── test-coverage-improvement
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── workos-notion-clone
│   │   ├── constitution.md
│   │   ├── plan.md
│   │   ├── prd.md
│   │   └── tasks.md
│   ├── constitution.md
│   ├── plan.md
│   ├── prd.md
│   └── tasks.md
├── specs
│   ├── 003-ai-enrichment
│   │   ├── DEPLOYMENT.md
│   │   ├── odoo_automation_action.py
│   │   └── spec.md
│   ├── 002-odoo-expense-equipment-mvp.prd.md
│   ├── 003-finance-ppm.prd.md
│   ├── 003-odoo-custom-image.prd.md
│   ├── INSTALL_SEQUENCE.md
│   ├── MODULE_SERVICE_MATRIX.md
│   ├── README.md
│   └── tasks.md
├── src
│   └── lakehouse
│       ├── __init__.py
│       ├── config.py
│       └── contracts.py
├── supabase
│   ├── .temp
│   │   ├── cli-latest
│   │   ├── gotrue-version
│   │   ├── pooler-url
│   │   ├── postgres-version
│   │   ├── project-ref
│   │   ├── rest-version
│   │   ├── storage-migration
│   │   └── storage-version
│   ├── functions
│   │   ├── auth-bootstrap
│   │   │   └── index.ts
│   │   ├── auth-otp-request
│   │   │   └── index.ts
│   │   ├── auth-otp-verify
│   │   │   └── index.ts
│   │   ├── catalog-sync
│   │   │   └── index.ts
│   │   ├── context-resolve
│   │   │   └── index.ts
│   │   ├── copilot-chat
│   │   │   └── index.ts
│   │   ├── cron-processor
│   │   │   └── index.ts
│   │   ├── docs-ai-ask
│   │   │   └── index.ts
│   │   ├── expense-policy-check
│   │   │   └── index.ts
│   │   ├── github-app-auth
│   │   │   └── index.ts
│   │   ├── github-mattermost-bridge
│   │   │   └── index.ts
│   │   ├── infra-memory-ingest
│   │   │   └── index.ts
│   │   ├── ipai-copilot
│   │   │   └── index.ts
│   │   ├── mcp-gateway
│   │   │   └── index.ts
│   │   ├── memory-ingest
│   │   │   └── index.ts
│   │   ├── odoo-template-export
│   │   │   └── index.ts
│   │   ├── ops-job-worker
│   │   │   └── index.ts
│   │   ├── realtime-sync
│   │   │   └── index.ts
│   │   ├── schema-changed
│   │   │   └── index.ts
│   │   ├── seed-odoo-finance
│   │   │   └── index.ts
│   │   ├── semantic-export-osi
│   │   │   └── index.ts
│   │   ├── semantic-import-osi
│   │   │   └── index.ts
│   │   ├── semantic-query
│   │   │   └── index.ts
│   │   ├── serve-erd
│   │   │   └── index.ts
│   │   ├── shadow-odoo-finance
│   │   │   └── index.ts
│   │   ├── skill-eval
│   │   │   └── index.ts
│   │   ├── sync-kb-to-schema
│   │   │   └── index.ts
│   │   ├── sync-odoo-modules
│   │   │   └── index.ts
│   │   ├── tenant-invite
│   │   │   └── index.ts
│   │   ├── three-way-match
│   │   │   └── index.ts
│   │   ├── vendor-score
│   │   │   └── index.ts
│   │   └── .env.example
│   ├── migrations
│   │   ├── 20240101000001_kb_schema.sql
│   │   ├── 20240101000002_studio_schema.sql
│   │   ├── 20240101000003_sign_schema.sql
│   │   ├── 20240101000004_booking_schema.sql
│   │   ├── 20240101000005_fsm_schema.sql
│   │   ├── 20240101000006_barcode_schema.sql
│   │   ├── 20240101000007_mobile_schema.sql
│   │   ├── 20240101000010_hr_schema.sql
│   │   ├── 20240101000011_finance_tasks_schema.sql
│   │   ├── 20240101000012_sync_events_schema.sql
│   │   ├── 20241220000001_master_control.sql
│   │   ├── 20241220000002_master_data.sql
│   │   ├── 20241221000001_control_room_api.sql
│   │   ├── 20250101_afc_canonical_schema.sql
│   │   ├── 20250101_afc_computation_triggers.sql
│   │   ├── 20250101_afc_rls_comprehensive.sql
│   │   ├── 20250101_afc_rls_fixed.sql
│   │   ├── 20250101_afc_verification_tests.sql
│   │   ├── 20250101_rls_deployment_actual_schema.sql
│   │   ├── 20250101_security_linter_remediation.sql
│   │   ├── 20251123_saas_feature_matrix.sql
│   │   ├── 20251128_semantic_query_layer.sql
│   │   ├── 202512071100_1000_CORE_SCHEMAS_AND_TENANCY.sql
│   │   ├── 202512071110_2000_ERP_FINANCE_EXPENSE_INVENTORY.sql
│   │   ├── 202512071120_2001_ERP_PROJECTS_RATES_PPM.sql
│   │   ├── 202512071130_3000_ENGINE_TE_CHEQ.sql
│   │   ├── 202512071140_3001_ENGINE_RETAIL_INTEL_SCOUT.sql
│   │   ├── 202512071150_3002_ENGINE_DOC_OCR.sql
│   │   ├── 202512071160_3003_ENGINE_PPM_FIRM.sql
│   │   ├── 202512071170_4000_AI_RAG_AND_AGENTS.sql
│   │   ├── 202512071180_5000_ANALYTICS_GOLD_PLATINUM_VIEWS.sql
│   │   ├── 202512071190_6000_SAAS_BILLING_SUBSCRIPTIONS.sql
│   │   ├── 202512071200_7000_ODOO_CE_OCA_SYNC_META.sql
│   │   ├── 202512071210_8000_RLS_POLICIES_AND_GRANTS.sql
│   │   ├── 202512071220_9000_SEEDS_REFERENCE_AND_DEMO_DATA.sql
│   │   ├── 20251219_ops_advisor_schema.sql
│   │   ├── 20251220085409_kapa_docs_copilot_hybrid_search.sql
│   │   ├── 202512201000_MULTI_ENGINE_GOVERNANCE.sql
│   │   ├── 202512201001_EXTERNAL_INTEGRATIONS.sql
│   │   ├── 202512201002_AZURE_CONTROL_CENTER.sql
│   │   ├── 202512201003_OCA_DOCS_BRAIN.sql
│   │   ├── 202512201004_SHIP_READY_DELTA.sql
│   │   ├── 20251220_001_docs_taxonomy.sql
│   │   ├── 20251220_002_docs_versioning.sql
│   │   ├── 20251220_003_docs_journeys.sql
│   │   ├── 20251220_004_kb_core.sql
│   │   ├── 20251220_005_kb_blocks.sql
│   │   ├── 20251220_006_kb_discovery.sql
│   │   ├── 20251220_007_kb_catalog.sql
│   │   ├── 20251220_agentbrain_delta.sql
│   │   ├── 20251220_capability_registry_full.sql
│   │   ├── 20251220_process_runtime_ticketing.sql
│   │   ├── 20251220_qms_lite_document_control.sql
│   │   ├── 20251220_ticketing_pipelines_clean.sql
│   │   ├── 20251222_control_room_workbench.sql
│   │   ├── 20251227_database_webhooks.sql
│   │   ├── 20251227_docs_ai_schema.sql
│   │   ├── 20251227_mcp_job_queue_cron.sql
│   │   ├── 20251227_supabase_queues_setup.sql
│   │   ├── 202601030001_docs.sql
│   │   ├── 20260106000001_kg_schema.sql
│   │   ├── 202601080001_4500_CATALOG_UNITY_SCHEMA.sql
│   │   ├── 202601080002_4501_CATALOG_SEMANTIC_LAYER.sql
│   │   ├── 202601080003_4502_OPS_ODOO_BINDINGS.sql
│   │   ├── 20260112_fix_trend_views_date_alias.sql
│   │   ├── 202601130001_IPAI_SAMPLE_METRICS.sql
│   │   ├── 20260120000001_ops_kg_infrastructure_graph.sql
│   │   ├── 20260120000002_ops_mcp_jobs_observability.sql
│   │   ├── 20260120100001_odoo_shadow_base.sql
│   │   ├── 20260120100002_odoo_shadow_tables.sql
│   │   ├── 20260120_email_otp_auth.sql
│   │   ├── 20260120_infra_schema.sql
│   │   ├── 20260120_mcp_jobs_schema.sql
│   │   ├── 20260120_skill_creator_certification.sql
│   │   ├── 20260121000000_odoo_catalogs.sql
│   │   ├── 20260121100001_odoo_data_dictionary.sql
│   │   ├── 20260121_odoo_seed_schema.sql
│   │   ├── 5001_auth_foundation.sql
│   │   ├── 5002_auth_jwt_claims.sql
│   │   ├── 5003_rls_policies.sql
│   │   ├── AFC_DEPLOYMENT_SUMMARY.md
│   │   └── RLS_DEPLOYMENT_COMPLETE.md
│   ├── seed
│   │   ├── 9000_core
│   │   │   └── 9000_core_tenants_roles_users.sql
│   │   ├── 9001_erp
│   │   │   ├── 9001_erp_finance_bir_templates.sql
│   │   │   └── 9001_erp_projects_rates_demo.sql
│   │   ├── 9002_engines
│   │   │   ├── 9002_engines_doc_ocr_sample_docs.sql
│   │   │   ├── 9002_engines_ppm_demo.sql
│   │   │   ├── 9002_engines_retail_intel_ph.sql
│   │   │   └── 9002_engines_te_cheq_demo_flows.sql
│   │   ├── 9003_ai_rag
│   │   │   ├── 9003_ai_rag_agent_registry_seed.sql
│   │   │   └── 9003_ai_rag_marketing_canvas_docs.sql
│   │   ├── 9004_analytics
│   │   │   ├── 9004_analytics_kpi_registry_seed.sql
│   │   │   └── 9004_analytics_superset_dashboard_seed.sql
│   │   ├── 9005_catalog
│   │   │   └── 9005_catalog_assets_tools.sql
│   │   ├── 9006_catalog
│   │   │   └── 9006_scout_suqi_semantic.sql
│   │   ├── 9007_skills
│   │   │   └── 9007_skills_certification_seed.sql
│   │   ├── 9008_drawio_skills
│   │   │   ├── 9008_drawio_assessment_tasks.sql
│   │   │   └── 9008_drawio_certification_seed.sql
│   │   └── 001_saas_feature_seed.sql
│   ├── seeds
│   │   ├── 001_hr_seed.sql
│   │   ├── 002_finance_seed.sql
│   │   └── 003_odoo_dict_seed.sql
│   ├── SECURITY_LINTER_REMEDIATION.md
│   └── config.toml
├── tasks
│   └── infra
│       └── AGENT_SERVICES_HARD_DELETE_CHECKLIST.md
├── templates
│   ├── module_readme
│   │   ├── CONFIGURE.rst
│   │   ├── CONTRIBUTORS.rst
│   │   ├── DESCRIPTION.rst
│   │   └── USAGE.rst
│   └── odoo
│       └── import
│           ├── README.md
│           ├── calendar_events_template.csv
│           ├── projects_template.csv
│           ├── stages_template.csv
│           └── tasks_template.csv
├── tests
│   ├── api
│   │   └── test_skill_api_contract.py
│   ├── e2e
│   │   └── playwright
│   │       ├── agent-core.spec.ts
│   │       └── playwright.config.ts
│   ├── load
│   │   └── odoo_login_and_nav.js
│   ├── playwright
│   │   └── ap_aging_print_report.spec.js
│   └── regression
│       ├── __init__.py
│       └── test_finance_ppm_install.py
├── tools
│   ├── audit
│   │   ├── db_truth.sql
│   │   ├── gen_prod_snapshot.sh
│   │   ├── gen_repo_tree.sh
│   │   ├── gen_repo_tree_prod.sh
│   │   ├── gen_runtime_sitemap.sh
│   │   ├── gen_snapshot_json.sh
│   │   ├── http_crawler.py
│   │   ├── require_audit_artifacts.sh
│   │   ├── run_audit_bundle.sh
│   │   ├── snapshot.sh
│   │   ├── verify_alignment.py
│   │   ├── verify_expected_paths.sh
│   │   └── verify_workos_install.sql
│   ├── catalog
│   │   └── databricks_org_catalog.py
│   ├── db-inventory
│   │   ├── README.md
│   │   └── inventory.py
│   ├── dbml
│   │   └── package.json
│   ├── diagramflow
│   │   ├── diagramflow
│   │   │   ├── __init__.py
│   │   │   ├── bpmn.py
│   │   │   ├── cli.py
│   │   │   ├── drawio.py
│   │   │   └── parser.py
│   │   ├── src
│   │   │   ├── cli.ts
│   │   │   ├── index.ts
│   │   │   ├── parseMermaid.ts
│   │   │   ├── remap.ts
│   │   │   ├── toBpmn.ts
│   │   │   └── toDrawio.ts
│   │   ├── README.md
│   │   ├── package.json
│   │   ├── pyproject.toml
│   │   └── tsconfig.json
│   ├── docs-crawler
│   │   ├── .env.example
│   │   ├── README.md
│   │   ├── api_ask.py
│   │   ├── config.yaml
│   │   ├── crawler.py
│   │   └── requirements.txt
│   ├── docs_catalog
│   │   ├── README.md
│   │   ├── crawl_docs.py
│   │   ├── map_to_odoo.py
│   │   └── odoo_map.yaml
│   ├── ipai_module_gen
│   │   ├── ipai_module_gen
│   │   │   ├── templates
│   │   │   ├── __init__.py
│   │   │   └── generate.py
│   │   └── pyproject.toml
│   ├── odoo_schema
│   │   ├── __init__.py
│   │   ├── export_schema.py
│   │   ├── schema_to_drawio.py
│   │   └── schema_to_pydantic.py
│   ├── parity
│   │   ├── parity_audit.py
│   │   └── validate_spec_kit.py
│   ├── seed_all.ts
│   ├── seed_doc_ocr.ts
│   ├── seed_ppm.ts
│   ├── seed_retail_intel.ts
│   └── seed_te_cheq.ts
├── vendor
│   ├── oca
│   │   ├── account-financial-reporting
│   │   ├── account-reconcile
│   │   ├── project
│   │   ├── server-tools
│   │   └── web
│   ├── oca-sync.sh
│   └── oca.lock.json
├── vercel
│   └── api
│       └── ask.py
├── workflows
│   ├── finance_ppm
│   │   ├── DEPLOYMENT.md
│   │   ├── DEPLOYMENT_SUMMARY.md
│   │   ├── FINAL_DEPLOYMENT_REPORT.md
│   │   ├── N8N_IMPORT_CHECKLIST.md
│   │   ├── bir_deadline_alert.json
│   │   ├── monthly_report.json
│   │   ├── task_escalation.json
│   │   └── verify_deployment.sh
│   ├── n8n
│   │   ├── expense-approval-workflow.json
│   │   ├── expense-ocr-workflow.json
│   │   ├── git-operations-workflow.json
│   │   ├── sync-complete.json
│   │   ├── sync-docs-changed.json
│   │   ├── sync-schema-changed.json
│   │   └── sync-spec-changed.json
│   ├── odoo
│   │   └── W403_AP_AGING_HEATMAP.json
│   ├── SHADOW_ENTERPRISE_STACK.md
│   ├── WEBHOOK_DEPLOYMENT_GUIDE.md
│   ├── n8n_bir_deadline_webhook.json
│   ├── n8n_enrichment_agent.json
│   ├── n8n_ocr_expense_webhook.json
│   └── n8n_scout_sync_webhook.json
├── .agentignore
├── .env.example
├── .env.production
├── .env.smtp.example
├── .flake8
├── .gitignore
├── .gitmodules
├── .pre-commit-config.yaml
├── ANALYTICS_ACTIVATION_SEQUENCE.md
├── AUDIT_FIXES_APPLIED.md
├── AUTO_HEALING_SYSTEM_SUMMARY.md
├── AUTO_REVIEW_AND_FIX_SUMMARY.md
├── CHANGELOG.md
├── CI_CD_AUTOMATION_SUMMARY.md
├── CI_CD_TROUBLESHOOTING_GUIDE.md
├── CI_MINIMAL_SET.md
├── CLAUDE.md
├── CLAUDE_CODE_WEB.md
├── CLAUDE_NEW.md
├── COMPREHENSIVE_DEPLOYMENT_SUMMARY.md
├── CONTRIBUTING.md
├── CREDENTIALS_SUMMARY.md
├── DEPLOYMENT_CHECKLIST.md
├── DEPLOYMENT_COMPLETE.md
├── DEPLOYMENT_MVP.md
├── DEPLOYMENT_REPORT.md
├── DEPLOYMENT_REPORT_FINAL.md
├── DEPLOYMENT_RUNBOOK.md
├── DEPLOYMENT_STATE_CURRENT.md
├── DEPLOYMENT_STATUS.md
├── DEPLOYMENT_VALIDATION_REPORT.md
├── DEPLOYMENT_VERIFICATION.md
├── DEPLOYMENT_WORKFLOW.md
├── DEPLOY_ENTERPRISE_BRIDGE_FIX.md
├── DEPLOY_NOW.md
├── Dockerfile
├── Dockerfile.v0.10.0
├── ERP_CONFIGURATION_SUMMARY.md
├── EXECUTE_NOW.md
├── FINANCE_PPM_CANONICAL.md
├── FINANCE_PPM_CE_DASHBOARD_GUIDE.md
├── FINANCE_PPM_DASHBOARD_GUIDE.md
├── FINANCE_PPM_IMPORT_GUIDE.md
├── HOTFIX_OWLERROR.sh
├── HOTFIX_SUMMARY.md
├── IDENTITY_CHATOPS_DEPLOYMENT_SUMMARY.md
├── INFRASTRUCTURE_PLAN.md
├── INFRASTRUCTURE_SUMMARY.md
├── INSIGHTPULSE_ERP_CONFIGURATION_GUIDE.md
├── KAPA_STYLE_DOCS_ASSISTANT_IMPLEMENTATION.md
├── MATTERMOST_OPEX_INTEGRATION.md
├── MCP_QUICK_START.md
├── Makefile
├── Month-end Closing Task and Tax Filing ext.xlsx
├── NOVEMBER_2025_CLOSE_TIMELINE.md
├── NOVEMBER_2025_PPM_GO_LIVE_SUMMARY.md
├── OCR_PROJECT_COMPLETE.md
├── ODOO_18_VSCODE_SETUP.md
├── ODOO_OCR_SETUP.md
├── PENDING_TASKS_AUTO_AUDIT.md
├── POSTGRES_PASSWORD_SOLUTION.md
├── PRODUCTION_DEPLOY_WORKOS.sh
├── PROD_DEPLOY.md
├── PROJECT_WRAPPER_IMPLEMENTATION.md
├── PROJECT_WRAPPER_IMPLEMENTATION_SUMMARY.md
├── README.md
├── README_BUILD.md
├── README_PATCH.md
├── RELEASE_v0.9.0.md
├── REPORT.md
├── REPO_RESTRUCTURE_PLAN.md
├── SAFETY_MECHANISMS.md
├── SANDBOX.md
├── SECURITY.md
├── SITEMAP.md
├── STRATEGIC_PPM_ANALYTICS_SUMMARY.md
├── TAG_LABEL_VOCABULARY.md
├── TBWA_IPAI_MODULE_STANDARD.md
├── TREE.md
├── VERIFY.md
├── VSCODE_CLAUDE_CONFIGURATION_SUMMARY.md
├── aiux_ship_manifest.yml
├── bir_deadlines_2026.csv
├── branch_protection.json
├── constitution.md
├── custom_module_inventory.md
├── deploy_m1.sh.template
├── deploy_ppm_dashboard.sh
├── deploy_ppm_dashboard_direct.sh
├── deployment_readiness_assessment.md
├── devserver.config.json
├── figma-make-dev.yaml
├── final_verification.sh
├── finance_calendar_2026.csv
├── finance_calendar_2026.html
├── finance_compliance_calendar_template.csv
├── finance_directory.csv
├── finance_directory_template.csv
├── finance_events_2026.json
├── finance_monthly_tasks_template.csv
├── finance_wbs.csv
├── finance_wbs_deadlines.csv
├── gemini.md
├── implementation_plan.md
├── implementation_plan_agent.md
├── import_finance_data.py
├── import_finance_directory.py
├── import_november_wbs.py
├── install_module.py
├── install_ppm_module.py
├── install_ppm_monthly_close.sh
├── ipai_ce_branding_patch_v1.2.0.zip
├── ipai_finance_ppm_directory.csv
├── ipai_open_semantics_migrations_and_functions.zip
├── ipai_theme_tbwa_18.0.1.0.0.zip
├── mkdocs.yml
├── n8n_automation_strategy.md
├── n8n_opex_cli.sh
├── oca-aggregate.yml
├── oca.lock.json
├── odoo-bin
├── odoo-ce-target.zip
├── odoo-v1.2.0-build.zip
├── odoo_ce_expert_prompt.md
├── package.json
├── parity_report.json
├── ph_holidays_2026.csv
├── plan.md
├── pnpm-lock.yaml
├── pnpm-workspace.yaml
├── ppm_dashboard_views.xml
├── pyproject.toml
├── query_memory.py
├── requirements-docs.txt
├── requirements.txt
├── ship_v1_1_0.sh
├── spec.md
├── task.md
├── tasks.md
├── turbo.json
├── update_finance_ppm.py
├── update_module.py
├── vercel.json
├── verify_deployment.py
├── verify_finance_ppm.py
├── verify_ppm_installation.sh
├── walkthrough.md
└── workflow_template.csv

1002 directories, 2851 files
```

## 📊 Stats

| Metric | Count |
|--------|-------|
| Directories | 1187 |
| Files | 3750 |
| Python files | 588 |
| XML files | 247 |
| Markdown files | 992 |
