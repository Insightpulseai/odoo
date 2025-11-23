# Repository Structure

Last updated: 2025-11-23 05:18:19 UTC

```
.
├── .github
│   ├── workflows
│   │   ├── ci-odoo-ce.yml
│   │   ├── ci-odoo-oca.yml
│   │   ├── health-check.yml
│   │   ├── odoo-parity-tests.yml
├── .gitignore
├── OCR_PROJECT_COMPLETE.md
├── ODOO_OCR_SETUP.md
├── README.md
├── TAG_LABEL_VOCABULARY.md
├── addons
│   ├── flutter_receipt_ocr
│   │   ├── DEPLOYMENT_GUIDE.md
│   │   ├── README.md
│   │   ├── analysis_options.yaml
│   │   ├── lib
│   │   │   ├── main.dart
│   │   │   ├── receipt_ocr
│   │   │   ├── receipt_ocr.dart
│   │   │   │   ├── config.dart
│   │   │   │   ├── ocr_api_client.dart
│   │   │   │   ├── parsed_receipt.dart
│   │   │   │   ├── receipt_ocr_sheet.dart
│   │   ├── pubspec.yaml
│   ├── ipai_ce_cleaner
│   │   ├── __init__.py
│   │   ├── __manifest__.py
│   │   ├── static
│   │   │   ├── src
│   │   │   │   ├── css
│   │   │   │   │   ├── ipai_ce_cleaner.css
│   │   ├── views
│   │   │   ├── ipai_ce_cleaner_assets.xml
│   │   │   ├── ipai_ce_cleaner_views.xml
│   ├── ipai_docs
│   │   ├── tests
│   │   │   ├── __init__.py
│   │   │   ├── test_workspace_visibility.py
│   ├── ipai_equipment
│   │   ├── __init__.py
│   │   ├── __manifest__.py
│   │   ├── data
│   │   │   ├── ipai_equipment_cron.xml
│   │   │   ├── ipai_equipment_sequences.xml
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── equipment.py
│   │   ├── security
│   │   │   ├── ir.model.access.csv
│   │   ├── tests
│   │   │   ├── __init__.py
│   │   │   ├── test_booking_cron.py
│   │   │   ├── test_equipment_flow.py
│   │   ├── views
│   │   │   ├── ipai_equipment_menus.xml
│   │   │   ├── ipai_equipment_views.xml
│   ├── ipai_expense
│   │   ├── __init__.py
│   │   ├── __manifest__.py
│   │   ├── data
│   │   │   ├── ipai_expense_categories.xml
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── expense.py
│   │   ├── security
│   │   │   ├── ipai_expense_security.xml
│   │   │   ├── ir.model.access.csv
│   │   ├── tests
│   │   │   ├── __init__.py
│   │   │   ├── test_business_flow.py
│   │   │   ├── test_expense_ocr.py
│   │   ├── views
│   │   │   ├── ipai_expense_menus.xml
│   │   │   ├── ipai_expense_views.xml
│   ├── ipai_finance_monthly_closing
│   │   ├── __init__.py
│   │   ├── __manifest__.py
│   │   ├── data
│   │   │   ├── project_templates.xml
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── project_task.py
│   │   ├── security
│   │   │   ├── ir.model.access.csv
│   │   ├── views
│   │   │   ├── project_task_views.xml
│   ├── ipai_ocr_expense
│   │   ├── __init__.py
│   │   ├── __manifest__.py
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── hr_expense_ocr.py
│   │   │   ├── ocr_expense_log.py
│   │   │   ├── res_config_settings.py
│   │   ├── security
│   │   │   ├── ir.model.access.csv
│   │   ├── views
│   │   │   ├── ipai_ocr_expense_views.xml
│   │   │   ├── ipai_ocr_settings_views.xml
│   │   │   ├── ocr_expense_log_views.xml
│   ├── ipai_ppm_monthly_close
│   │   ├── INSTALL_NOVEMBER_2025.md
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── __manifest__.py
│   │   ├── data
│   │   │   ├── ppm_close_cron.xml
│   │   │   ├── ppm_close_template_data_REAL.xml
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── ppm_close_task.py
│   │   │   ├── ppm_close_template.py
│   │   │   ├── ppm_monthly_close.py
│   │   ├── security
│   │   │   ├── ir.model.access.csv
│   │   ├── tests
│   │   │   ├── __init__.py
│   │   │   ├── test_monthly_close.py
│   │   ├── views
│   │   │   ├── ppm_close_menu.xml
│   │   │   ├── ppm_close_task_views.xml
│   │   │   ├── ppm_close_template_views.xml
│   │   │   ├── ppm_monthly_close_views.xml
│   │   ├── wizards
│   │   │   ├── __init__.py
│   ├── tbwa_spectra_integration
│   │   ├── README.md
│   │   ├── __init__.py
│   │   ├── __manifest__.py
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   ├── approval_matrix.py
│   │   │   ├── hr_expense_advance.py
│   │   │   ├── hr_expense_sheet.py
│   │   │   ├── spectra_export.py
│   │   │   ├── spectra_mapping.py
├── agents
│   ├── AGENT_SKILLS_REGISTRY.yaml
│   ├── ORCHESTRATOR.md
│   ├── PRIORITIZED_ROADMAP.md
│   ├── README.md
│   ├── capabilities
│   │   ├── CAPABILITY_MATRIX.yaml
│   ├── knowledge
│   │   ├── KNOWLEDGE_BASE_INDEX.yaml
│   ├── loops
│   │   ├── clarity_ppm_reverse.yaml
│   ├── odoo_oca_ci_fixer.yaml
│   ├── odoo_reverse_mapper.yaml
│   ├── procedures
│   │   ├── EXECUTION_PROCEDURES.yaml
│   ├── prompts
│   │   ├── odoo_oca_ci_fixer_system.txt
├── automations
│   ├── n8n
│   │   ├── workflows
│   │   │   ├── odoo_reverse_mapper.json
│   │   │   ├── ppm_monthly_close_automation.json
├── baselines
│   ├── v0.2.1-quality-baseline-20251121.txt
├── bin
│   ├── odoo-tests.sh
├── data
│   ├── month_end_tasks.csv
├── deploy
│   ├── docker-compose.yml
│   ├── nginx
│   │   ├── erp.insightpulseai.net.conf
│   ├── odoo.conf
├── deploy_m1.sh.template
├── docs
│   ├── AGENT_FRAMEWORK_SESSION_REPORT.md
│   ├── DEPLOYMENT.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── ENTERPRISE_FEATURE_GAP.yaml
│   ├── FEATURE_CHEQROOM_PARITY.md
│   ├── FEATURE_CONCUR_PARITY.md
│   ├── FEATURE_WORKSPACE_PARITY.md
│   ├── HEALTH_CHECK.md
│   ├── ODOO_MODULE_DEPLOYMENT.md
│   ├── PRD_ipai_ppm_portfolio.md
│   ├── SAAS_PARITY_READINESS.md
│   ├── TESTING_ODOO_18.md
│   ├── deployment
│   │   ├── OCA_CI_GUARDIAN.md
│   │   ├── README.md
├── notion-n8n-monthly-close
│   ├── DEPLOYMENT_STATUS.md
│   ├── N8N_CLI_README.md
│   ├── WORKFLOW_CONVENTIONS.md
│   ├── scripts
│   │   ├── n8n-sync.sh
│   │   ├── verify_finance_stack.sh
│   ├── workflows
│   │   ├── ODOO_BIR_PREP.json
│   │   ├── ODOO_EXPENSE_OCR.json
│   │   ├── ODOO_KNOWLEDGE_GOV.json
│   │   ├── README.md
│   │   ├── W150_FINANCE_HEALTH_CHECK.json
│   │   ├── index.yaml
│   │   ├── odoo
│   │   │   ├── W001_OD_MNTH_CLOSE_SYNC.json
│   │   │   ├── W002_OD_BIR_ALERTS.json
│   │   │   ├── W401_CC_EXPENSE_IMPORT.json
│   │   │   ├── W501_EQ_BOOKING_SYNC.json
│   │   ├── supabase
│   │   │   ├── W101_SB_CLOSE_SNAPSHOT.json
├── ocr-adapter
│   ├── .gitignore
│   ├── DEPLOYMENT.md
│   ├── Dockerfile
│   ├── README.md
│   ├── docker-compose.yml
│   ├── main.py
│   ├── nginx-site.conf
│   ├── requirements.txt
│   ├── scripts
│   │   ├── README.md
│   │   ├── ground_truth_example.csv
│   │   ├── test-harness.py
│   ├── test-ocr.sh
├── plan.md
├── scripts
│   ├── README.md
│   ├── apply-supabase-schema.sh
│   ├── backup_odoo.sh
│   ├── baseline-validation.sh
│   ├── check_project_tasks.py
│   ├── ci
│   │   ├── run_odoo_tests.sh
│   ├── deploy-odoo-modules.sh
│   ├── deploy-to-server.sh
│   ├── deployment-checklist.sh
│   ├── gen_repo_tree.sh
│   ├── gen_repo_tree_fallback.sh
│   ├── import_month_end_tasks.py
│   ├── install-git-hooks.sh
│   ├── run_clarity_ppm_reverse.sh
│   ├── validate_m1.sh
├── spec.md
├── specs
│   ├── 002-odoo-expense-equipment-mvp.prd.md
│   ├── INSTALL_SEQUENCE.md
│   ├── MODULE_SERVICE_MATRIX.md
│   ├── README.md
│   ├── tasks.md
├── supabase
│   ├── migrations
│   │   ├── 20251123_saas_feature_matrix.sql
│   ├── seed
│   │   ├── 001_saas_feature_seed.sql
├── tasks.md
```
