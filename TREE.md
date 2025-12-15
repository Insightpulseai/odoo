# 📁 Repository Structure

> Auto-generated on every commit. Last update: $(date -u '+%Y-%m-%d %H:%M:%S UTC')
> Commit: d88beaacdc750aa57340945c31d1319002314bc1

```
.
├── .agent
│   ├── workflows
│   │   ├── deploy.md
│   │   ├── scaffold.md
│   │   └── test.md
│   └── rules.md
├── .claude
│   ├── project_memory.db
│   ├── query_memory.py
│   └── settings.local.json
├── .github
│   ├── workflows
│   │   ├── auto-sitemap-tree.yml
│   │   ├── ci-odoo-ce.yml
│   │   ├── ci-odoo-oca.yml
│   │   └── health-check.yml
│   └── copilot-instructions.md
├── addons
│   ├── flutter_receipt_ocr
│   │   ├── lib
│   │   │   ├── receipt_ocr
│   │   │   ├── main.dart
│   │   │   └── receipt_ocr.dart
│   │   ├── DEPLOYMENT_GUIDE.md
│   │   ├── README.md
│   │   ├── analysis_options.yaml
│   │   └── pubspec.yaml
│   ├── ipai_bir_compliance
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   └── account_move.py
│   │   ├── reports
│   │   │   └── bir_2307_report.xml
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── wizards
│   │   │   ├── __init__.py
│   │   │   ├── bir_dat_file_wizard.py
│   │   │   └── bir_dat_file_wizard_view.xml
│   │   ├── README.rst
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_ce_cleaner
│   │   ├── static
│   │   │   └── src
│   │   ├── views
│   │   │   ├── ipai_ce_cleaner_assets.xml
│   │   │   └── ipai_ce_cleaner_views.xml
│   │   ├── README.rst
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_clarity_ppm_parity
│   │   ├── data
│   │   │   ├── bir_schedule_2025_2026.xml
│   │   │   ├── clarity_data.xml
│   │   │   └── demo_data.xml
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── project_checklist.py
│   │   │   ├── project_milestone.py
│   │   │   ├── project_phase.py
│   │   │   ├── project_project.py
│   │   │   └── project_task.py
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── views
│   │   │   ├── project_menu.xml
│   │   │   ├── project_milestone_views.xml
│   │   │   ├── project_phase_views.xml
│   │   │   ├── project_project_views.xml
│   │   │   └── project_task_views.xml
│   │   ├── IMPLEMENTATION_SUMMARY.md
│   │   ├── QUICK_START.md
│   │   ├── README.rst
│   │   ├── STATUS.md
│   │   ├── TEST_REPORT.md
│   │   ├── __init__.py
│   │   ├── __manifest__.py
│   │   └── install.sh
│   ├── ipai_docs
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── ipai_doc.py
│   │   │   └── ipai_doc_tag.py
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── tests
│   │   │   ├── __init__.py
│   │   │   └── test_workspace_visibility.py
│   │   ├── views
│   │   │   ├── ipai_doc_tag_views.xml
│   │   │   ├── ipai_doc_views.xml
│   │   │   └── menu.xml
│   │   ├── README.rst
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_docs_project
│   │   ├── data
│   │   │   └── workspace_seed.xml
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── doc.py
│   │   │   ├── project.py
│   │   │   └── task.py
│   │   ├── views
│   │   │   ├── project_views.xml
│   │   │   └── task_views.xml
│   │   ├── README.rst
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_equipment
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   └── equipment.py
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── tests
│   │   │   ├── __init__.py
│   │   │   └── test_equipment_lifecycle.py
│   │   ├── views
│   │   │   ├── ipai_equipment_menus.xml
│   │   │   └── ipai_equipment_views.xml
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_expense
│   │   ├── data
│   │   │   └── ipai_expense_categories.xml
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   └── expense.py
│   │   ├── security
│   │   │   ├── ipai_expense_security.xml
│   │   │   └── ir.model.access.csv
│   │   ├── tests
│   │   │   ├── __init__.py
│   │   │   └── test_expense_validation.py
│   │   ├── views
│   │   │   ├── ipai_expense_menus.xml
│   │   │   └── ipai_expense_views.xml
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_finance_ap_aging
│   │   ├── controllers
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   ├── data
│   │   │   └── ap_aging_cron.xml
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   └── account_move_line.py
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── static
│   │   │   └── src
│   │   ├── tests
│   │   │   ├── __init__.py
│   │   │   └── test_ap_aging.py
│   │   ├── views
│   │   │   ├── ap_aging_menu.xml
│   │   │   └── ap_aging_views.xml
│   │   ├── IMPLEMENTATION_SUMMARY.md
│   │   ├── README.rst
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_finance_controller_dashboard
│   │   ├── controllers
│   │   │   ├── __init__.py
│   │   │   └── main.py
│   │   ├── data
│   │   │   └── controller_dashboard_cron.xml
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   └── finance_controller_kpi.py
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── static
│   │   │   └── src
│   │   ├── tests
│   │   │   ├── __init__.py
│   │   │   └── test_controller_kpi.py
│   │   ├── views
│   │   │   ├── controller_dashboard_menu.xml
│   │   │   └── controller_dashboard_views.xml
│   │   ├── IMPLEMENTATION_SUMMARY.md
│   │   ├── README.rst
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_finance_monthly_closing
│   │   ├── data
│   │   │   └── project_templates.xml
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   └── project_task.py
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── views
│   │   │   └── project_task_views.xml
│   │   ├── README.rst
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_finance_ppm
│   │   ├── controllers
│   │   │   ├── __init__.py
│   │   │   └── ppm_dashboard.py
│   │   ├── data
│   │   │   ├── bir_schedule_seed.xml
│   │   │   ├── finance_bir_schedule_2026_full.xml
│   │   │   ├── finance_bir_schedule_seed.xml
│   │   │   ├── finance_cron.xml
│   │   │   └── finance_logframe_seed.xml
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── bir_schedule.py
│   │   │   ├── finance_bir_deadline.py
│   │   │   ├── finance_person.py
│   │   │   ├── finance_ppm.py
│   │   │   ├── finance_task.py
│   │   │   ├── ppm_dashboard.py
│   │   │   └── project_task.py
│   │   ├── scripts
│   │   │   └── generate_bir_seeds.py
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── static
│   │   │   ├── lib
│   │   │   └── src
│   │   ├── views
│   │   │   ├── bir_schedule_views.xml
│   │   │   ├── finance_bir_deadline_views.xml
│   │   │   ├── finance_person_views.xml
│   │   │   ├── finance_ppm_views.xml
│   │   │   ├── finance_task_views.xml
│   │   │   ├── menus.xml
│   │   │   ├── ppm_dashboard_template.xml
│   │   │   ├── ppm_dashboard_views.xml
│   │   │   └── project_task_views.xml
│   │   ├── README.md
│   │   ├── README.rst
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_finance_ppm_dashboard
│   │   ├── static
│   │   │   ├── lib
│   │   │   └── src
│   │   ├── views
│   │   │   └── ipai_finance_ppm_dashboard_views.xml
│   │   ├── README.rst
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_finance_ppm_tdi
│   │   ├── data
│   │   │   ├── bir_calendar_seed.xml
│   │   │   ├── finance_team_seed.xml
│   │   │   ├── logframe_kpi_seed.xml
│   │   │   ├── month_end_tasks_notion_import.xml
│   │   │   ├── month_end_tasks_seed.xml
│   │   │   └── ph_holiday_calendar_seed.xml
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── finance_ppm_bir_calendar.py
│   │   │   ├── finance_ppm_logframe.py
│   │   │   ├── finance_ppm_ph_holiday.py
│   │   │   └── finance_ppm_tdi_audit.py
│   │   ├── security
│   │   │   ├── ir.model.access.csv
│   │   │   └── security_groups.xml
│   │   ├── static
│   │   │   └── description
│   │   ├── views
│   │   │   ├── finance_ppm_tdi_audit_views.xml
│   │   │   └── menu.xml
│   │   ├── wizard
│   │   │   ├── __init__.py
│   │   │   ├── finance_ppm_import_wizard.py
│   │   │   └── finance_ppm_import_wizard_views.xml
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── __manifest__.py
│   │   └── hooks.py
│   ├── ipai_idp
│   │   ├── ade
│   │   │   ├── core
│   │   │   ├── pipelines
│   │   │   └── __init__.py
│   │   ├── controllers
│   │   │   ├── __init__.py
│   │   │   ├── health_controller.py
│   │   │   └── idp_api_controller.py
│   │   ├── data
│   │   │   └── idp_model_versions_data.xml
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── idp_ade_trace.py
│   │   │   ├── idp_document.py
│   │   │   ├── idp_document_ocr.py
│   │   │   ├── idp_extraction.py
│   │   │   ├── idp_llm_gateway.py
│   │   │   ├── idp_model_version.py
│   │   │   ├── idp_review.py
│   │   │   ├── idp_validation_rule.py
│   │   │   └── res_config_settings.py
│   │   ├── security
│   │   │   ├── idp_groups.xml
│   │   │   ├── idp_record_rules.xml
│   │   │   └── ir.model.access.csv
│   │   ├── services
│   │   │   ├── __init__.py
│   │   │   ├── idp_service_extractor.py
│   │   │   ├── idp_service_health.py
│   │   │   ├── idp_service_ocr.py
│   │   │   ├── idp_service_parser.py
│   │   │   └── idp_service_validator.py
│   │   ├── tests
│   │   │   ├── __init__.py
│   │   │   ├── test_document_flow.py
│   │   │   ├── test_extraction.py
│   │   │   ├── test_health.py
│   │   │   ├── test_http_endpoints.py
│   │   │   ├── test_parsers.py
│   │   │   ├── test_security.py
│   │   │   └── test_validation.py
│   │   ├── views
│   │   │   ├── idp_document_views.xml
│   │   │   ├── idp_extraction_views.xml
│   │   │   ├── idp_menus.xml
│   │   │   ├── idp_model_version_views.xml
│   │   │   ├── idp_review_views.xml
│   │   │   └── res_config_settings_views.xml
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_ocr_expense
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── hr_expense_ocr.py
│   │   │   ├── ocr_expense_log.py
│   │   │   └── res_config_settings.py
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── views
│   │   │   ├── ipai_ocr_expense_views.xml
│   │   │   ├── ipai_ocr_settings_views.xml
│   │   │   └── ocr_expense_log_views.xml
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_portal_fix
│   │   ├── controllers
│   │   │   ├── __init__.py
│   │   │   └── portal.py
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── ir_http.py
│   │   │   └── ir_qweb.py
│   │   ├── views
│   │   │   └── portal_templates.xml
│   │   ├── DEPLOYMENT_VERIFICATION.md
│   │   ├── README.md
│   │   ├── README.rst
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_ppm_monthly_close
│   │   ├── data
│   │   │   ├── ppm_close_cron.xml
│   │   │   └── ppm_close_template_data_REAL.xml
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── ppm_close_task.py
│   │   │   ├── ppm_close_template.py
│   │   │   └── ppm_monthly_close.py
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── tests
│   │   │   ├── __init__.py
│   │   │   └── test_monthly_close.py
│   │   ├── views
│   │   │   ├── ppm_close_menu.xml
│   │   │   ├── ppm_close_task_views.xml
│   │   │   ├── ppm_close_template_views.xml
│   │   │   └── ppm_monthly_close_views.xml
│   │   ├── wizards
│   │   │   └── __init__.py
│   │   ├── INSTALL_NOVEMBER_2025.md
│   │   ├── README.md
│   │   ├── README.rst
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   └── tbwa_spectra_integration
│       ├── data
│       │   ├── approval_matrix_data.xml
│       │   ├── export_templates_data.xml
│       │   ├── spectra_mapping_data.xml
│       │   ├── tbwa_cron.xml
│       │   └── users_data.xml
│       ├── models
│       │   ├── __init__.py
│       │   ├── approval_matrix.py
│       │   ├── hr_expense_advance.py
│       │   ├── hr_expense_sheet.py
│       │   ├── spectra_export.py
│       │   └── spectra_mapping.py
│       ├── security
│       │   ├── ir.model.access.csv
│       │   └── tbwa_security.xml
│       ├── views
│       │   ├── approval_matrix_views.xml
│       │   ├── hr_expense_advance_views.xml
│       │   ├── spectra_export_views.xml
│       │   ├── spectra_mapping_views.xml
│       │   └── tbwa_menu.xml
│       ├── wizards
│       │   ├── __init__.py
│       │   ├── spectra_export_wizard.py
│       │   └── spectra_export_wizard_views.xml
│       ├── README.md
│       ├── README.rst
│       ├── __init__.py
│       └── __manifest__.py
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
│   ├── odoo_oca_ci_fixer.yaml
│   ├── odoo_reverse_mapper.yaml
│   └── smart_delta_oca.yaml
├── apps
│   ├── do-advisor-agent
│   │   ├── config
│   │   │   └── mcp-config.json
│   │   ├── prompts
│   │   │   └── unified_advisor.md
│   │   ├── tools
│   │   │   └── odoo_finance_ppm.py
│   │   └── README.md
│   └── do-advisor-ui
│       ├── public
│       │   ├── config.js
│       │   └── index.html
│       ├── src
│       │   ├── assets
│       │   ├── components
│       │   ├── views
│       │   └── app.js
│       ├── Dockerfile
│       ├── README.md
│       ├── app-spec.yaml
│       └── nginx.conf
├── automations
│   └── n8n
│       └── workflows
│           ├── odoo_reverse_mapper.json
│           └── ppm_monthly_close_automation.json
├── baselines
│   └── v0.2.1-quality-baseline-20251121.txt
├── bin
│   ├── README.md
│   ├── finance-cli.sh
│   ├── import_bir_schedules.py
│   ├── odoo-tests.sh
│   └── postdeploy-finance.sh
├── calendar
│   ├── 2026_FinanceClosing_Master.csv
│   └── FinanceClosing_RecurringTasks.ics
├── data
│   ├── bir_calendar_2026.json
│   ├── employee_directory.json
│   ├── month_end_tasks.csv
│   ├── notion_tasks_deduplicated.json
│   ├── notion_tasks_parsed.json
│   └── notion_tasks_with_logframe.json
├── db
│   ├── migrations
│   │   ├── 202512070001_REORG_CREATE_DOMAIN_TABLES.sql
│   │   ├── 202512070002_REORG_COPY_DATA.sql
│   │   └── 202512070003_REORG_CREATE_COMPAT_VIEWS.sql
│   ├── rls
│   │   ├── RLS_BASE_TEMPLATE.sql
│   │   └── RLS_ROLES.md
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
│   ├── .env.production.template
│   ├── README.md
│   ├── docker-compose.prod.v0.10.0.yml
│   ├── docker-compose.prod.v0.9.1.yml
│   ├── docker-compose.prod.yml
│   ├── docker-compose.yml
│   ├── keycloak-integration.yml
│   ├── mattermost-integration.yml
│   ├── monitoring_schema.sql
│   ├── monitoring_views.sql
│   ├── odoo-auto-heal.service
│   └── odoo.conf
├── dev-docker
│   ├── config
│   │   └── odoo.conf
│   ├── ipai_finance_ppm
│   │   ├── data
│   │   │   └── finance_ppm_data.xml
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── finance_canvas.py
│   │   │   └── finance_ppm_task.py
│   │   ├── security
│   │   │   └── ir.model.access.csv
│   │   ├── static
│   │   │   └── description
│   │   ├── tests
│   │   │   ├── __init__.py
│   │   │   └── test_finance_canvas.py
│   │   ├── views
│   │   │   ├── finance_canvas_views.xml
│   │   │   └── finance_ppm_task_views.xml
│   │   ├── README.rst
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── theme_tbwa_backend
│   │   ├── static
│   │   │   └── src
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── .env.example
│   ├── Dockerfile
│   ├── README.md
│   └── docker-compose.yml
├── docker
│   ├── nginx
│   │   ├── ssl
│   │   │   ├── .gitkeep
│   │   │   └── README.md
│   │   └── nginx.conf
│   ├── Dockerfile.enterprise-parity
│   ├── Dockerfile.v1.1.0-enterprise-parity
│   ├── build-enterprise-parity.sh
│   ├── docker-compose.enterprise-parity.yml
│   ├── odoo-v1.1.0.conf
│   └── requirements-enterprise-parity.txt
├── docs
│   ├── architecture
│   │   ├── INSIGHTPULSEAI_TECHNICAL_ARCHITECTURE.md
│   │   ├── README.md
│   │   ├── ipai_idp_architecture.drawio
│   │   ├── ipai_idp_build_deploy_custom_models.drawio
│   │   ├── ipai_idp_multi_agent_workflow.drawio
│   │   └── ipai_idp_pdf_processing.drawio
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
│   │   ├── OCA_CI_GUARDIAN.md
│   │   └── README.md
│   ├── diagrams
│   │   └── architecture
│   │       ├── README.md
│   │       └── manifest.json
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
│   ├── 003-odoo-ce-custom-image-spec.md
│   ├── AGENTIC_CLOUD_PRD.md
│   ├── AGENT_FRAMEWORK_SESSION_REPORT.md
│   ├── APP_ICONS_README.md
│   ├── AUTOMATED_TROUBLESHOOTING_GUIDE.md
│   ├── CUSTOM_IMAGE_SUCCESS_CRITERIA.md
│   ├── DB_TUNING.md
│   ├── DEPLOYMENT.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── DEPLOYMENT_NAMING_MATRIX.md
│   ├── DIGITALOCEAN_VALIDATION_FRAMEWORK.md
│   ├── DOCKERFILE_COMPARISON.md
│   ├── DOCKER_CD_MIGRATION_GUIDE.md
│   ├── DOCKER_VALIDATION_GUIDE.md
│   ├── DOKS_DEPLOYMENT_SUCCESS_CRITERIA.md
│   ├── ENTERPRISE_FEATURE_GAP.yaml
│   ├── EXECUTIVE_SUMMARY.md
│   ├── FEATURE_CHEQROOM_PARITY.md
│   ├── FEATURE_CONCUR_PARITY.md
│   ├── FEATURE_WORKSPACE_PARITY.md
│   ├── FINAL_DEPLOYMENT_GUIDE.md
│   ├── FINAL_OPERABILITY_CHECKLIST.md
│   ├── FINANCE_PPM_IMPLEMENTATION.md
│   ├── HEALTH_CHECK.md
│   ├── IMAGE_GUIDE.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── INDUSTRY_PARITY_ANALYSIS.md
│   ├── KEYCLOAK_IDENTITY_PROVIDER_DEPLOYMENT.md
│   ├── KUBERNETES_MIGRATION_SPECIFICATION.md
│   ├── MATTERMOST_ALERTING_SETUP.md
│   ├── MATTERMOST_CHATOPS_DEPLOYMENT.md
│   ├── MCP_IMPLEMENTATION_STATUS.md
│   ├── MIXED_CONTENT_FIX.md
│   ├── MVP_GO_LIVE_CHECKLIST.md
│   ├── N8N_CREDENTIALS_BOOTSTRAP.md
│   ├── OCA_MIGRATION.md
│   ├── ODOO18_ENTERPRISE_TO_CE_OCA_MAPPING.md
│   ├── ODOO_18_CE_CHEATSHEET.md
│   ├── ODOO_18_EE_TO_CE_OCA_PARITY.md
│   ├── ODOO_ARCHITECT_PERSONA.md
│   ├── ODOO_CE_DEPLOYMENT_SUMMARY.md
│   ├── ODOO_CE_v0.9.0_SECURITY_AUDIT_REPORT.md
│   ├── ODOO_HTTPS_OAUTH_TROUBLESHOOTING.md
│   ├── ODOO_MODULE_DEPLOYMENT.md
│   ├── OFFLINE_TARBALL_DEPLOYMENT.md
│   ├── PRD_ipai_ppm_portfolio.md
│   ├── PROD_READINESS_GAPS.md
│   ├── QUICK_REFERENCE_SSO_SETUP.md
│   ├── README.md
│   ├── README_MCP_STACK.md
│   ├── SAAS_PARITY_READINESS.md
│   ├── SECRETS_NAMING_AND_STORAGE.md
│   ├── SEMANTIC_VERSIONING_STRATEGY.md
│   ├── SSO_VALIDATION_CHECKLIST.md
│   ├── SUPERSET_PPM_ANALYTICS_GUIDE.md
│   ├── TESTING_ODOO_18.md
│   ├── WBS_LOGFRAME_MAPPING.md
│   ├── branch-cleanup-analysis.md
│   └── v0.9.1_DEPLOYMENT_GUIDE.md
├── docs-assistant
│   ├── api
│   │   ├── Dockerfile
│   │   ├── answer_engine.py
│   │   └── requirements.txt
│   ├── deploy
│   │   ├── .env.example
│   │   ├── deploy.sh
│   │   ├── docker-compose.yml
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
│   ├── servers
│   │   ├── odoo-erp.yaml
│   │   └── odoo-lab.yaml
│   └── agentic-cloud.yaml
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
│   └── .gitkeep
├── oca-addons
│   ├── mis-builder
│   ├── project
│   ├── purchase-workflow
│   ├── reporting-engine
│   ├── server-ux
│   └── oca-addons-extra.tar.gz
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
│   ├── docker-compose.yml
│   ├── main.py
│   ├── nginx-site.conf
│   ├── requirements.txt
│   └── test-ocr.sh
├── odoo
│   ├── ODOO_INTEGRATION_MAP.md
│   └── ipai_finance_closing_seed.json
├── scripts
│   ├── ci
│   │   ├── constraints-gevent.txt
│   │   ├── install_odoo_18.sh
│   │   ├── run_odoo_tests.sh
│   │   └── wait_for_postgres.sh
│   ├── README.md
│   ├── apply-supabase-schema.sh
│   ├── auto_error_handler.sh
│   ├── backup_odoo.sh
│   ├── baseline-validation.sh
│   ├── build_and_push_version.sh
│   ├── build_v0.10.0.sh
│   ├── build_v0.9.1.sh
│   ├── check_project_tasks.py
│   ├── cleanup-branches.sh
│   ├── convert_csv_to_xml.py
│   ├── convert_seed_to_xml.py
│   ├── deploy-odoo-modules.sh
│   ├── deploy-to-server.sh
│   ├── deploy_custom_image.sh
│   ├── deploy_notion_tasks.sh
│   ├── deploy_prod.sh
│   ├── deployment-checklist.sh
│   ├── enhanced_health_check.sh
│   ├── erp_config_cli.sh
│   ├── full_deploy_sanity.sh
│   ├── gen_repo_tree.sh
│   ├── gen_repo_tree_fallback.sh
│   ├── generate_2026_finance_calendar.py
│   ├── generate_2026_schedule.py
│   ├── generate_finance_dashboard.py
│   ├── generate_seed_xml.py
│   ├── healthcheck_odoo.sh
│   ├── import_month_end_tasks.py
│   ├── install-git-hooks.sh
│   ├── install_ipai_finance_ppm.sh
│   ├── install_module_xmlrpc.py
│   ├── map_logframe.py
│   ├── odoo_mattermost_integration.py
│   ├── package_image_tarball.sh
│   ├── parse_notion_tasks.py
│   ├── pre_install_snapshot.sh
│   ├── report_ci_telemetry.sh
│   ├── run_clarity_ppm_reverse.sh
│   ├── run_odoo_migrations.sh
│   ├── setup_keycloak_db.sh
│   ├── setup_mattermost_db.sh
│   ├── simple_deploy.sh
│   ├── smoketest.sh
│   ├── test_deploy_local.sh
│   ├── update_diagram_manifest.py
│   ├── validate_m1.sh
│   ├── verify-https.sh
│   ├── verify_backup.sh
│   └── verify_phase3.py
├── skills
│   ├── architecture_diagrams.skill.json
│   └── superset_mcp.skill.json
├── spec
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
├── supabase
│   ├── migrations
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
│   │   └── 202512071220_9000_SEEDS_REFERENCE_AND_DEMO_DATA.sql
│   └── seed
│       ├── 9000_core
│       │   └── 9000_core_tenants_roles_users.sql
│       ├── 9001_erp
│       │   ├── 9001_erp_finance_bir_templates.sql
│       │   └── 9001_erp_projects_rates_demo.sql
│       ├── 9002_engines
│       │   ├── 9002_engines_doc_ocr_sample_docs.sql
│       │   ├── 9002_engines_ppm_demo.sql
│       │   ├── 9002_engines_retail_intel_ph.sql
│       │   └── 9002_engines_te_cheq_demo_flows.sql
│       ├── 9003_ai_rag
│       │   ├── 9003_ai_rag_agent_registry_seed.sql
│       │   └── 9003_ai_rag_marketing_canvas_docs.sql
│       ├── 9004_analytics
│       │   ├── 9004_analytics_kpi_registry_seed.sql
│       │   └── 9004_analytics_superset_dashboard_seed.sql
│       └── 001_saas_feature_seed.sql
├── tests
│   ├── load
│   │   └── odoo_login_and_nav.js
│   ├── playwright
│   │   └── ap_aging_print_report.spec.js
│   └── regression
│       ├── __init__.py
│       └── test_finance_ppm_install.py
├── tools
│   ├── seed_all.ts
│   ├── seed_doc_ocr.ts
│   ├── seed_ppm.ts
│   ├── seed_retail_intel.ts
│   └── seed_te_cheq.ts
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
├── .flake8
├── .gitignore
├── .gitmodules
├── .pre-commit-config.yaml
├── ANALYTICS_ACTIVATION_SEQUENCE.md
├── AUDIT_FIXES_APPLIED.md
├── AUTO_HEALING_SYSTEM_SUMMARY.md
├── CHANGELOG.md
├── CI_CD_AUTOMATION_SUMMARY.md
├── CI_CD_TROUBLESHOOTING_GUIDE.md
├── CLAUDE.md
├── CLAUDE_NEW.md
├── COMPREHENSIVE_DEPLOYMENT_SUMMARY.md
├── DEPLOYMENT_MVP.md
├── DEPLOYMENT_STATUS.md
├── DEPLOYMENT_VALIDATION_REPORT.md
├── DEPLOYMENT_VERIFICATION.md
├── DEPLOYMENT_WORKFLOW.md
├── Dockerfile
├── Dockerfile.v0.10.0
├── ERP_CONFIGURATION_SUMMARY.md
├── EXECUTE_NOW.md
├── FINANCE_PPM_CE_DASHBOARD_GUIDE.md
├── FINANCE_PPM_DASHBOARD_GUIDE.md
├── FINANCE_PPM_IMPORT_GUIDE.md
├── IDENTITY_CHATOPS_DEPLOYMENT_SUMMARY.md
├── INSIGHTPULSE_ERP_CONFIGURATION_GUIDE.md
├── KAPA_STYLE_DOCS_ASSISTANT_IMPLEMENTATION.md
├── MATTERMOST_OPEX_INTEGRATION.md
├── MCP_QUICK_START.md
├── NOVEMBER_2025_CLOSE_TIMELINE.md
├── NOVEMBER_2025_PPM_GO_LIVE_SUMMARY.md
├── OCR_PROJECT_COMPLETE.md
├── ODOO_18_VSCODE_SETUP.md
├── ODOO_OCR_SETUP.md
├── POSTGRES_PASSWORD_SOLUTION.md
├── PROJECT_WRAPPER_IMPLEMENTATION.md
├── PROJECT_WRAPPER_IMPLEMENTATION_SUMMARY.md
├── README.md
├── RELEASE_v0.9.0.md
├── SITEMAP.md
├── STRATEGIC_PPM_ANALYTICS_SUMMARY.md
├── TAG_LABEL_VOCABULARY.md
├── TBWA_IPAI_MODULE_STANDARD.md
├── TREE.md
├── VSCODE_CLAUDE_CONFIGURATION_SUMMARY.md
├── bir_deadlines_2026.csv
├── constitution.md
├── custom_module_inventory.md
├── deploy_m1.sh.template
├── deploy_ppm_dashboard.sh
├── deploy_ppm_dashboard_direct.sh
├── deployment_readiness_assessment.md
├── docker-compose.mcp-local.yml
├── docker-compose.prod.yml
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
├── implementation_plan.md
├── implementation_plan_agent.md
├── import_finance_data.py
├── import_finance_directory.py
├── import_november_wbs.py
├── install_module.py
├── install_ppm_module.py
├── install_ppm_monthly_close.sh
├── ipai_finance_ppm_directory.csv
├── n8n_automation_strategy.md
├── n8n_opex_cli.sh
├── odoo-bin
├── odoo-ce-target.zip
├── odoo_ce_expert_prompt.md
├── ph_holidays_2026.csv
├── plan.md
├── ppm_dashboard_views.xml
├── query_memory.py
├── requirements.txt
├── spec.md
├── task.md
├── tasks.md
├── update_finance_ppm.py
├── update_module.py
├── verify_deployment.py
├── verify_finance_ppm.py
├── verify_ppm_installation.sh
├── walkthrough.md
└── workflow_template.csv

258 directories, 772 files
```

## 📊 Stats

| Metric | Count |
|--------|-------|
| Directories | 274 |
| Files | 828 |
| Python files | 204 |
| XML files | 102 |
| Markdown files | 204 |
