# Repository Structure

Last updated: 2025-11-23 05:18:19 UTC

This repository contains the **InsightPulse Odoo CE** stack: a fully self-hosted, Odoo Community Edition + OCA–based ERP for expense management and equipment booking.

The system is designed to:

- Replace **SAP Concur** for PH-focused expense & travel workflows.
- Replace **Cheqroom** for equipment catalog, bookings, and incident tracking.
- Run **only** on Odoo Community Edition + OCA modules and custom `ipai_*` addons.
- Avoid all Odoo Enterprise codepaths, IAP services, and odoo.com upsell links.
- Serve exclusively under InsightPulse domains (e.g. `erp.insightpulseai.net`).

## 2. Repository Structure

<!-- REPO_TREE_START -->
```text
.
|-- .agent
|   |-- workflows
|   `-- rules.md
|-- .claude
|   `-- settings.local.json
|-- .github
|   `-- workflows
|-- addons
|   |-- flutter_receipt_ocr
|   |-- ipai_cash_advance
|   |-- ipai_ce_cleaner
|   |-- ipai_docs
|   |-- ipai_docs_project
|   |-- ipai_equipment
|   |-- ipai_expense
|   |-- ipai_finance_monthly_closing
|   |-- ipai_finance_ppm
|   |-- ipai_ocr_expense
|   |-- ipai_ppm_monthly_close
|   `-- tbwa_spectra_integration
|-- agents
|   |-- capabilities
|   |-- knowledge
|   |-- loops
|   |-- personas
|   |-- procedures
|   |-- AGENT_SKILLS_REGISTRY.yaml
|   |-- ORCHESTRATOR.md
|   |-- PRIORITIZED_ROADMAP.md
|   |-- README.md
|   `-- odoo_reverse_mapper.yaml
|-- automations
|   `-- n8n
|-- baselines
|   `-- v0.2.1-quality-baseline-20251121.txt
|-- bin
|   |-- README.md
|   |-- finance-cli.sh
|   |-- import_bir_schedules.py
|   `-- postdeploy-finance.sh
|-- calendar
|   |-- 2026_FinanceClosing_Master.csv
|   `-- FinanceClosing_RecurringTasks.ics
|-- data
|   `-- month_end_tasks.csv
|-- deploy
|   |-- nginx
|   |-- docker-compose.yml
|   |-- monitoring_schema.sql
|   |-- monitoring_views.sql
|   `-- odoo.conf
|-- docs
|   |-- AGENTIC_CLOUD_PRD.md
|   |-- AGENT_FRAMEWORK_SESSION_REPORT.md
|   |-- APP_ICONS_README.md
|   |-- DB_TUNING.md
|   |-- DEPLOYMENT.md
|   |-- DEPLOYMENT_GUIDE.md
|   |-- ENTERPRISE_FEATURE_GAP.yaml
|   |-- FEATURE_CHEQROOM_PARITY.md
|   |-- FEATURE_CONCUR_PARITY.md
|   |-- FEATURE_WORKSPACE_PARITY.md
|   |-- HEALTH_CHECK.md
|   |-- MATTERMOST_ALERTING_SETUP.md
|   |-- N8N_CREDENTIALS_BOOTSTRAP.md
|   |-- ODOO_ARCHITECT_PERSONA.md
|   |-- ODOO_CE_DEPLOYMENT_SUMMARY.md
|   |-- ODOO_MODULE_DEPLOYMENT.md
|   |-- PRD_ipai_ppm_portfolio.md
|   |-- PROD_READINESS_GAPS.md
|   `-- SAAS_PARITY_READINESS.md
|-- mcp
|   `-- agentic-cloud.yaml
|-- notion-n8n-monthly-close
|   |-- scripts
|   |-- supabase
|   |-- workflows
|   |-- DEPLOYMENT_STATUS.md
|   |-- N8N_CLI_README.md
|   `-- WORKFLOW_CONVENTIONS.md
|-- ocr-adapter
|   |-- scripts
|   |-- test_receipts
|   |-- .gitignore
|   |-- DEPLOYMENT.md
|   |-- Dockerfile
|   |-- README.md
|   |-- docker-compose.yml
|   |-- main.py
|   |-- nginx-site.conf
|   |-- requirements.txt
|   `-- test-ocr.sh
|-- odoo
|   `-- ipai_finance_closing_seed.json
|-- scripts
|   |-- ci
|   |-- README.md
|   |-- apply-supabase-schema.sh
|   |-- backup_odoo.sh
|   |-- baseline-validation.sh
|   |-- check_project_tasks.py
|   |-- convert_csv_to_xml.py
|   |-- convert_seed_to_xml.py
|   |-- deploy-odoo-modules.sh
|   |-- deploy-to-server.sh
|   |-- deployment-checklist.sh
|   |-- gen_repo_tree.sh
|   |-- generate_2026_finance_calendar.py
|   |-- generate_2026_schedule.py
|   |-- generate_finance_dashboard.py
|   |-- healthcheck_odoo.sh
|   |-- import_month_end_tasks.py
|   |-- install-git-hooks.sh
|   |-- install_ipai_finance_ppm.sh
|   |-- pre_install_snapshot.sh
|   |-- report_ci_telemetry.sh
|   |-- run_clarity_ppm_reverse.sh
|   |-- run_odoo_migrations.sh
|   |-- validate_m1.sh
|   `-- verify_backup.sh
|-- specs
|   |-- 002-odoo-expense-equipment-mvp.prd.md
|   |-- 003-finance-ppm.prd.md
|   |-- INSTALL_SEQUENCE.md
|   |-- MODULE_SERVICE_MATRIX.md
|   |-- README.md
|   `-- tasks.md
|-- supabase
|   |-- migrations
|   `-- seed
|-- tests
|   |-- load
|   `-- regression
|-- workflows
|   `-- finance_ppm
|-- .agentignore
|-- .gitignore
|-- CHANGELOG.md
|-- CI_CD_AUTOMATION_SUMMARY.md
|-- COMPREHENSIVE_DEPLOYMENT_SUMMARY.md
|-- DEPLOYMENT_MVP.md
|-- DEPLOYMENT_STATUS.md
|-- MATTERMOST_OPEX_INTEGRATION.md
|-- OCR_PROJECT_COMPLETE.md
|-- ODOO_OCR_SETUP.md
|-- README.md
|-- TAG_LABEL_VOCABULARY.md
|-- TBWA_IPAI_MODULE_STANDARD.md
|-- bir_deadlines_2026.csv
|-- custom_module_inventory.md
|-- deploy_m1.sh.template
|-- deployment_readiness_assessment.md
|-- finance_calendar_2026.csv
|-- finance_calendar_2026.html
|-- finance_events_2026.json
|-- implementation_plan.md
|-- implementation_plan_agent.md
|-- n8n_automation_strategy.md
|-- n8n_opex_cli.sh
|-- odoo-bin
|-- odoo_ce_expert_prompt.md
|-- ph_holidays_2026.csv
|-- plan.md
|-- spec.md
|-- task.md
|-- tasks.md
|-- verify_finance_ppm.py
|-- walkthrough.md
`-- workflow_template.csv
