# 📁 Repository Structure

> Auto-generated on every commit. Last update: $(date -u '+%Y-%m-%d %H:%M:%S UTC')
> Commit: 314f2583abf65c629a116ee4b824b4a9a5359799

```
.
├── .agent
│   ├── workflows
│   │   ├── deploy.md
│   │   ├── scaffold.md
│   │   └── test.md
│   └── rules.md
├── .claude
│   └── settings.local.json
├── .github
│   └── workflows
│       ├── auto-sitemap-tree.yml
│       ├── ci-odoo-ce.yml
│       ├── ci-odoo-oca.yml
│       └── health-check.yml
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
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_ce_cleaner
│   │   ├── static
│   │   │   └── src
│   │   ├── views
│   │   │   ├── ipai_ce_cleaner_assets.xml
│   │   │   └── ipai_ce_cleaner_views.xml
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_clarity_ppm_parity
│   │   ├── data
│   │   │   └── clarity_data.xml
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
│   │   │   └── project_project_views.xml
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
│   │   │   ├── finance_person_views.xml
│   │   │   ├── finance_ppm_views.xml
│   │   │   ├── finance_task_views.xml
│   │   │   ├── menus.xml
│   │   │   ├── ppm_dashboard_template.xml
│   │   │   ├── ppm_dashboard_views.xml
│   │   │   └── project_task_views.xml
│   │   ├── README.md
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_finance_ppm_dashboard
│   │   ├── static
│   │   │   ├── lib
│   │   │   └── src
│   │   ├── views
│   │   │   └── ipai_finance_ppm_dashboard_views.xml
│   │   ├── __init__.py
│   │   └── __manifest__.py
│   ├── ipai_portal_fix
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── ir_http.py
│   │   │   └── ir_qweb.py
│   │   ├── views
│   │   │   └── portal_templates.xml
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
│   └── odoo_reverse_mapper.yaml
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
│   └── month_end_tasks.csv
├── deploy
│   ├── nginx
│   │   └── erp.insightpulseai.net.conf
│   ├── README.md
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
├── docs
│   ├── deployment
│   │   ├── OCA_CI_GUARDIAN.md
│   │   └── README.md
│   ├── diagrams
│   │   └── architecture
│   │       ├── README.md
│   │       └── manifest.json
│   ├── AGENTIC_CLOUD_PRD.md
│   ├── AGENT_FRAMEWORK_SESSION_REPORT.md
│   ├── APP_ICONS_README.md
│   ├── AUTOMATED_TROUBLESHOOTING_GUIDE.md
│   ├── DB_TUNING.md
│   ├── DEPLOYMENT.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── DOCKER_CD_MIGRATION_GUIDE.md
│   ├── DOCKER_VALIDATION_GUIDE.md
│   ├── ENTERPRISE_FEATURE_GAP.yaml
│   ├── FEATURE_CHEQROOM_PARITY.md
│   ├── FEATURE_CONCUR_PARITY.md
│   ├── FEATURE_WORKSPACE_PARITY.md
│   ├── FINAL_OPERABILITY_CHECKLIST.md
│   ├── FINANCE_PPM_IMPLEMENTATION.md
│   ├── HEALTH_CHECK.md
│   ├── IMAGE_GUIDE.md
│   ├── KEYCLOAK_IDENTITY_PROVIDER_DEPLOYMENT.md
│   ├── KUBERNETES_MIGRATION_SPECIFICATION.md
│   ├── MATTERMOST_ALERTING_SETUP.md
│   ├── MATTERMOST_CHATOPS_DEPLOYMENT.md
│   ├── N8N_CREDENTIALS_BOOTSTRAP.md
│   ├── OCA_MIGRATION.md
│   ├── ODOO18_ENTERPRISE_TO_CE_OCA_MAPPING.md
│   ├── ODOO_ARCHITECT_PERSONA.md
│   ├── ODOO_CE_DEPLOYMENT_SUMMARY.md
│   ├── ODOO_MODULE_DEPLOYMENT.md
│   ├── PRD_ipai_ppm_portfolio.md
│   ├── PROD_READINESS_GAPS.md
│   ├── SAAS_PARITY_READINESS.md
│   └── TESTING_ODOO_18.md
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
│   └── agentic-cloud.yaml
├── notion-n8n-monthly-close
│   ├── scripts
│   │   ├── n8n-sync.sh
│   │   └── verify_finance_stack.sh
│   ├── supabase
│   │   ├── functions
│   │   │   └── closing-snapshot
│   │   └── SUPABASE_DEPLOYMENT.md
│   ├── workflows
│   │   ├── odoo
│   │   │   ├── W001_OD_MNTH_CLOSE_SYNC.json
│   │   │   ├── W002_OD_BIR_ALERTS.json
│   │   │   ├── W401_CC_EXPENSE_IMPORT.json
│   │   │   └── W501_EQ_BOOKING_SYNC.json
│   │   ├── supabase
│   │   │   └── W101_SB_CLOSE_SNAPSHOT.json
│   │   ├── ODOO_BIR_PREP.json
│   │   ├── ODOO_EXPENSE_OCR.json
│   │   ├── ODOO_KNOWLEDGE_GOV.json
│   │   ├── README.md
│   │   ├── W150_FINANCE_HEALTH_CHECK.json
│   │   └── index.yaml
│   ├── DEPLOYMENT_STATUS.md
│   ├── N8N_CLI_README.md
│   └── WORKFLOW_CONVENTIONS.md
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
│   ├── check_project_tasks.py
│   ├── convert_csv_to_xml.py
│   ├── convert_seed_to_xml.py
│   ├── deploy-odoo-modules.sh
│   ├── deploy-to-server.sh
│   ├── deployment-checklist.sh
│   ├── enhanced_health_check.sh
│   ├── erp_config_cli.sh
│   ├── gen_repo_tree.sh
│   ├── gen_repo_tree_fallback.sh
│   ├── generate_2026_finance_calendar.py
│   ├── generate_2026_schedule.py
│   ├── generate_finance_dashboard.py
│   ├── healthcheck_odoo.sh
│   ├── import_month_end_tasks.py
│   ├── install-git-hooks.sh
│   ├── install_ipai_finance_ppm.sh
│   ├── odoo_mattermost_integration.py
│   ├── pre_install_snapshot.sh
│   ├── report_ci_telemetry.sh
│   ├── run_clarity_ppm_reverse.sh
│   ├── run_odoo_migrations.sh
│   ├── setup_keycloak_db.sh
│   ├── setup_mattermost_db.sh
│   ├── update_diagram_manifest.py
│   ├── validate_m1.sh
│   └── verify_backup.sh
├── skills
│   ├── architecture_diagrams.skill.json
│   └── superset_mcp.skill.json
├── specs
│   ├── 002-odoo-expense-equipment-mvp.prd.md
│   ├── 003-finance-ppm.prd.md
│   ├── INSTALL_SEQUENCE.md
│   ├── MODULE_SERVICE_MATRIX.md
│   ├── README.md
│   └── tasks.md
├── supabase
│   ├── migrations
│   │   └── 20251123_saas_feature_matrix.sql
│   └── seed
│       └── 001_saas_feature_seed.sql
├── tests
│   ├── load
│   │   └── odoo_login_and_nav.js
│   └── regression
│       ├── __init__.py
│       └── test_finance_ppm_install.py
├── workflows
│   └── finance_ppm
│       ├── DEPLOYMENT.md
│       ├── DEPLOYMENT_SUMMARY.md
│       ├── FINAL_DEPLOYMENT_REPORT.md
│       ├── N8N_IMPORT_CHECKLIST.md
│       ├── bir_deadline_alert.json
│       ├── monthly_report.json
│       ├── task_escalation.json
│       └── verify_deployment.sh
├── .agentignore
├── .env.example
├── .gitignore
├── .gitmodules
├── .pre-commit-config.yaml
├── AUTO_HEALING_SYSTEM_SUMMARY.md
├── CHANGELOG.md
├── CI_CD_AUTOMATION_SUMMARY.md
├── CI_CD_TROUBLESHOOTING_GUIDE.md
├── CLAUDE.md
├── CLAUDE_NEW.md
├── COMPREHENSIVE_DEPLOYMENT_SUMMARY.md
├── DEPLOYMENT_MVP.md
├── DEPLOYMENT_STATUS.md
├── Dockerfile
├── ERP_CONFIGURATION_SUMMARY.md
├── FINANCE_PPM_CE_DASHBOARD_GUIDE.md
├── FINANCE_PPM_DASHBOARD_GUIDE.md
├── FINANCE_PPM_IMPORT_GUIDE.md
├── IDENTITY_CHATOPS_DEPLOYMENT_SUMMARY.md
├── INSIGHTPULSE_ERP_CONFIGURATION_GUIDE.md
├── KAPA_STYLE_DOCS_ASSISTANT_IMPLEMENTATION.md
├── MATTERMOST_OPEX_INTEGRATION.md
├── NOVEMBER_2025_CLOSE_TIMELINE.md
├── NOVEMBER_2025_PPM_GO_LIVE_SUMMARY.md
├── OCR_PROJECT_COMPLETE.md
├── ODOO_18_VSCODE_SETUP.md
├── ODOO_OCR_SETUP.md
├── POSTGRES_PASSWORD_SOLUTION.md
├── PROJECT_WRAPPER_IMPLEMENTATION.md
├── PROJECT_WRAPPER_IMPLEMENTATION_SUMMARY.md
├── README.md
├── SITEMAP.md
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
├── final_verification.sh
├── finance_calendar_2026.csv
├── finance_calendar_2026.html
├── finance_compliance_calendar_template.csv
├── finance_directory_template.csv
├── finance_events_2026.json
├── finance_monthly_tasks_template.csv
├── finance_wbs.csv
├── finance_wbs_deadlines.csv
├── implementation_plan.md
├── implementation_plan_agent.md
├── import_finance_data.py
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

158 directories, 428 files
```

## 📊 Stats

| Metric | Count |
|--------|-------|
| Directories | 169 |
| Files | 461 |
| Python files | 105 |
| XML files | 52 |
| Markdown files | 120 |
