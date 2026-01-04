# InsightPulse Odoo CE – Project Spec

Repo: https://github.com/jgtolentino/odoo-ce
Owner: InsightPulseAI – ERP Platform Team
Status: Active

## 1. Overview

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
|   |-- commands
|   |-- superclaude
|   |-- project_memory.db
|   |-- query_memory.py
|   |-- settings.json
|   `-- settings.local.json
|-- .continue
|   |-- prompts
|   |-- rules
|   `-- config.json
|-- .githooks
|   `-- pre-commit
|-- .github
|   |-- workflows
|   `-- copilot-instructions.md
|-- .insightpulse
|   |-- sync-config.yaml
|   `-- sync.yaml
|-- addons
|   |-- ipai
|   |-- ipai_ask_ai
|   |-- ipai_ask_ai_chatter
|   |-- ipai_bir_tax_compliance
|   |-- ipai_crm_pipeline
|   |-- ipai_finance_closing
|   |-- ipai_finance_ppm_golive
|   |-- ipai_finance_ppm_umbrella
|   |-- ipai_grid_view
|   |-- ipai_month_end
|   |-- ipai_month_end_closing
|   |-- ipai_ocr_gateway
|   |-- ipai_platform_approvals
|   |-- ipai_platform_audit
|   |-- ipai_platform_permissions
|   |-- ipai_platform_theme
|   |-- ipai_platform_workflow
|   |-- ipai_sms_gateway
|   |-- ipai_superset_connector
|   |-- ipai_tbwa_finance
|   |-- ipai_theme_tbwa_backend
|   |-- ipai_web_theme_chatgpt
|   |-- ipai_workos_affine
|   |-- ipai_workos_blocks
|   |-- ipai_workos_canvas
|   |-- ipai_workos_collab
|   |-- ipai_workos_core
|   |-- ipai_workos_db
|   |-- ipai_workos_search
|   |-- ipai_workos_templates
|   |-- ipai_workos_views
|   `-- oca
|-- agents
|   |-- capabilities
|   |-- knowledge
|   |-- loops
|   |-- personas
|   |-- procedures
|   |-- prompts
|   |-- AGENT_SKILLS_REGISTRY.yaml
|   |-- ORCHESTRATOR.md
|   |-- PRIORITIZED_ROADMAP.md
|   |-- README.md
|   |-- odoo_oca_ci_fixer.yaml
|   |-- odoo_reverse_mapper.yaml
|   `-- smart_delta_oca.yaml
|-- api
|   `-- oca-docs-brain-openapi.yaml
|-- apps
|   |-- bi-architect
|   |-- chatgpt_ipai_ai_studio
|   |-- control-room
|   |-- control-room-api
|   |-- devops-engineer
|   |-- do-advisor-agent
|   |-- do-advisor-ui
|   |-- docs-ai-widget
|   |-- finance-ssc-expert
|   |-- ipai-chatgpt-app
|   |-- ipai-control-center-docs
|   |-- mattermost-rag
|   |-- mcp-coordinator
|   |-- mobile
|   |-- multi-agent-orchestrator
|   |-- odoo-developer-agent
|   |-- odoo-saas-platform
|   |-- pulser-runner
|   `-- superset-analytics
|-- archive
|   `-- addons
|-- artifacts
|   |-- logs
|   |-- ce_oca_equivalents_audit.csv
|   |-- ce_oca_equivalents_audit.json
|   |-- ipai_install_upgrade_matrix.csv
|   |-- ipai_install_upgrade_matrix.json
|   |-- ipai_quality_gate.csv
|   |-- ipai_quality_gate.json
|   |-- module_audit_baseline.json
|   |-- module_audit_matrix.csv
|   `-- module_audit_matrix.json
|-- audit
|   |-- snapshot.json
|   `-- snapshot.txt
|-- automations
|   `-- n8n
|-- baselines
|   `-- v0.2.1-quality-baseline-20251121.txt
|-- bin
|   |-- README.md
|   |-- ci_sync_check.sh
|   |-- copilot_drift_check.sh
|   |-- finance-cli.sh
|   |-- import_bir_schedules.py
|   |-- odoo-tests.sh
|   `-- postdeploy-finance.sh
|-- branding
|   `-- fluentui-system-icons
|-- calendar
|   |-- 2026_FinanceClosing_Master.csv
|   `-- FinanceClosing_RecurringTasks.ics
|-- catalog
|   |-- best_of_breed.yaml
|   |-- equivalence_matrix.csv
|   `-- equivalence_matrix_workos_notion.csv
|-- claudedocs
|   |-- 100_PERCENT_CLI_DEPLOYMENT.md
|   |-- DEPLOYMENT_SUMMARY.md
|   |-- FINAL_DEPLOYMENT_REPORT.md
|   |-- ISSUE_RESOLUTION_REPORT.md
|   |-- bir-deadline-reminder-system.sql
|   |-- bir-filing-lead-time-corrections.sql
|   |-- bir-filing-validation-report.md
|   `-- bir-okr-scoring-functions.sql
|-- clients
|   `-- flutter_receipt_ocr
|-- config
|   |-- entrypoint.d
|   |-- finance
|   |-- sources
|   |-- capability_map.yaml
|   |-- odoo.conf.template
|   `-- pipeline.yaml
|-- contracts
|   `-- delta
|-- data
|   |-- import_templates
|   |-- IMPORT_GUIDE.md
|   |-- bir_calendar_2026.json
|   |-- bir_december_2025_seed.xml
|   |-- employee_directory.json
|   |-- month_end_closing_tasks.csv
|   |-- month_end_closing_tasks.sql
|   |-- month_end_tasks.csv
|   |-- notion_tasks_deduplicated.json
|   |-- notion_tasks_parsed.json
|   `-- notion_tasks_with_logframe.json
|-- db
|   |-- migrations
|   |-- rls
|   |-- schema
|   |-- seeds
|   `-- DB_TARGET_ARCHITECTURE.md
|-- deploy
|   |-- k8s
|   |-- nginx
|   |-- .env.production.template
|   |-- README.md
|   |-- docker-compose.prod.v0.10.0.yml
|   |-- docker-compose.prod.v0.9.1.yml
|   |-- docker-compose.prod.yml
|   |-- docker-compose.workos-deploy.yml
|   |-- docker-compose.yml
|   |-- keycloak-integration.yml
|   |-- mattermost-integration.yml
|   |-- monitoring_schema.sql
|   |-- monitoring_views.sql
|   |-- odoo-auto-heal.service
|   `-- odoo.conf
|-- dev-docker
|   |-- config
|   |-- ipai_finance_ppm
|   |-- theme_tbwa_backend
|   |-- .env.example
|   |-- Dockerfile
|   |-- README.md
|   `-- docker-compose.yml
|-- docker
|   |-- hardened
|   |-- nginx
|   |-- Dockerfile.enterprise-parity
|   |-- Dockerfile.seeded
|   |-- Dockerfile.unified
|   |-- Dockerfile.v1.1.0-enterprise-parity
|   |-- build-enterprise-parity.sh
|   |-- docker-compose.enterprise-parity.yml
|   |-- docker-compose.seeded.yml
|   |-- docker-entrypoint.sh
|   |-- entrypoint.seeded.sh
|   |-- odoo-v1.1.0.conf
|   |-- odoo.conf.template
|   |-- odoo.seeded.conf
|   |-- requirements-enterprise-parity.txt
|   `-- requirements.seeded.txt
|-- docs
|   |-- adr
|   |-- architecture
|   |-- data-model
|   |-- db
|   |-- deployment
|   |-- diagrams
|   |-- finance-ppm
|   |-- ipai
|   |-- modules
|   |-- odoo
|   |-- odoo-18-handbook
|   |-- ops
|   |-- ppm
|   |-- repo
|   |-- runtime
|   |-- workflows
|   |-- 003-odoo-ce-custom-image-spec.md
|   |-- AGENTIC_CLOUD_PRD.md
|   |-- AGENT_FRAMEWORK_SESSION_REPORT.md
|   |-- APP_ICONS_README.md
|   |-- AUTOMATED_TROUBLESHOOTING_GUIDE.md
|   |-- CE_OCA_EQUIVALENTS_AUDIT.md
|   |-- CUSTOM_IMAGE_SUCCESS_CRITERIA.md
|   |-- DB_TUNING.md
|   |-- DELIVERABLES_MANIFEST.md
|   |-- DEPLOYMENT.md
|   |-- DEPLOYMENT_GUIDE.md
|   |-- DEPLOYMENT_NAMING_MATRIX.md
|   |-- DEPLOY_NOTION_WORKOS.md
|   |-- DEVELOPER_TOOLS.md
|   |-- DIGITALOCEAN_SMTP_UNBLOCK_REQUEST.md
|   |-- DIGITALOCEAN_VALIDATION_FRAMEWORK.md
|   |-- DIRECTIONAL_SYNC.md
|   |-- DOCKERFILE_COMPARISON.md
|   |-- DOCKER_CD_MIGRATION_GUIDE.md
|   |-- DOCKER_VALIDATION_GUIDE.md
|   |-- DOKS_DEPLOYMENT_SUCCESS_CRITERIA.md
|   |-- ECOSYSTEM_GUIDE.md
|   |-- ENTERPRISE_FEATURE_GAP.yaml
|   |-- EXECUTIVE_SUMMARY.md
|   |-- FEATURE_CHEQROOM_PARITY.md
|   |-- FEATURE_CONCUR_PARITY.md
|   |-- FEATURE_WORKSPACE_PARITY.md
|   |-- FINAL_DEPLOYMENT_GUIDE.md
|   |-- FINAL_OPERABILITY_CHECKLIST.md
|   |-- FINAL_READINESS_CHECK.md
|   |-- FINANCE_PPM_IMPLEMENTATION.md
|   |-- FIN_WORKSPACE_AUTOMATION_STATUS.md
|   |-- FIN_WORKSPACE_HARDENING_STATUS.md
|   |-- FIN_WORKSPACE_SETUP.md
|   |-- GITHUB_SECRETS_SETUP.md
|   |-- GIT_WORKTREE_STRATEGY.md
|   |-- GO_LIVE_CHECKLIST.md
|   |-- HEALTH_CHECK.md
|   |-- IMAGE_GUIDE.md
|   |-- IMPLEMENTATION_SUMMARY.md
|   |-- INDUSTRY_PACKS_OCA_DEPENDENCIES.md
|   |-- INDUSTRY_PARITY_ANALYSIS.md
|   |-- IPAI_MODULES_INDEX.md
|   |-- KEYCLOAK_IDENTITY_PROVIDER_DEPLOYMENT.md
|   |-- KUBERNETES_MIGRATION_SPECIFICATION.md
|   |-- MATTERMOST_ALERTING_SETUP.md
|   |-- MATTERMOST_CHATOPS_DEPLOYMENT.md
|   |-- MCP_IMPLEMENTATION_STATUS.md
|   |-- MCP_SUPABASE_INTEGRATION.md
|   |-- MIXED_CONTENT_FIX.md
|   |-- MODULE_STATUS_FINAL.md
|   |-- MODULE_STATUS_REPORT.md
|   |-- MONOREPO_STRUCTURE.md
|   |-- MVP_GO_LIVE_CHECKLIST.md
|   |-- N8N_CREDENTIALS_BOOTSTRAP.md
|   |-- NAMING_CONVENTION_EQ_APP_TOOLS.md
|   |-- OCA_MIGRATION.md
|   |-- ODOO18_ENTERPRISE_TO_CE_OCA_MAPPING.md
|   |-- ODOO_18_CE_CHEATSHEET.md
|   |-- ODOO_18_EE_TO_CE_OCA_PARITY.md
|   |-- ODOO_ADDONS_PATH_CONFIGURATION.md
|   |-- ODOO_APPS_CATALOG.md
|   |-- ODOO_ARCHITECT_PERSONA.md
|   |-- ODOO_CE_DEPLOYMENT_SUMMARY.md
|   |-- ODOO_CE_v0.9.0_SECURITY_AUDIT_REPORT.md
|   |-- ODOO_HTTPS_OAUTH_TROUBLESHOOTING.md
|   |-- ODOO_IMAGE_SPEC.md
|   |-- ODOO_MODULE_DEPLOYMENT.md
|   |-- ODOO_PROGRAMMATIC_CONFIG.md
|   |-- OFFLINE_TARBALL_DEPLOYMENT.md
|   |-- PRD_ipai_ppm_portfolio.md
|   |-- PROD_READINESS_GAPS.md
|   |-- PROD_SNAPSHOT_MANIFEST.md
|   |-- QUICK_REFERENCE_SSO_SETUP.md
|   |-- RAG_ARCHITECTURE_IMPLEMENTATION_PLAN.md
|   |-- README.md
|   |-- README_MCP_STACK.md
|   |-- REPO_SNAPSHOT.json
|   |-- REPO_TREE.contract.md
|   |-- REPO_TREE.generated.md
|   |-- SAAS_PARITY_READINESS.md
|   |-- SECRETS_NAMING_AND_STORAGE.md
|   |-- SEMANTIC_VERSIONING_STRATEGY.md
|   |-- SITEMAP.md
|   |-- SMTP_SETUP_SUMMARY.md
|   |-- SSO_VALIDATION_CHECKLIST.md
|   |-- SUPERSET_PPM_ANALYTICS_GUIDE.md
|   |-- TAGGING_STRATEGY.md
|   |-- TESTING_ODOO_18.md
|   |-- WBS_LOGFRAME_MAPPING.md
|   |-- WORKOS_DEPLOYMENT_MANIFEST.md
|   |-- ZOHO_DNS_SETUP.md
|   |-- branch-cleanup-analysis.md
|   |-- odoo-apps-parity.md
|   |-- odoo_core_schema.sql
|   |-- supabase-integration.md
|   `-- v0.9.1_DEPLOYMENT_GUIDE.md
|-- docs-assistant
|   |-- api
|   |-- deploy
|   |-- mcp
|   |-- web
|   `-- DEPLOYMENT_GUIDE.md
|-- engines
|   |-- _template
|   |-- doc-ocr
|   |-- retail-intel
|   `-- te-cheq
|-- external-src
|   |-- account-closing
|   |-- account-financial-reporting
|   |-- account-financial-tools
|   |-- account-invoicing
|   |-- calendar
|   |-- contract
|   |-- dms
|   |-- hr-expense
|   |-- maintenance
|   |-- project
|   |-- purchase-workflow
|   |-- reporting-engine
|   |-- server-tools
|   `-- web
|-- infra
|   |-- azure
|   |-- ce
|   |-- ci
|   |-- databricks
|   |-- docker
|   |-- doctl
|   |-- entrypoint.d
|   |-- lakehouse
|   `-- superset
|-- inventory
|   |-- latest -> runs/20251231T020517Z
|   `-- runs
|-- kb
|   |-- audit
|   |-- design_system
|   |-- finance_close
|   `-- parity
|-- mattermost
|   |-- runbooks
|   `-- webhook-templates
|-- mcp
|   |-- coordinator
|   |-- local
|   |-- servers
|   `-- agentic-cloud.yaml
|-- n8n
|   `-- workflows
|-- notion-n8n-monthly-close
|   |-- scripts
|   |-- src
|   |-- supabase
|   |-- workflows
|   |-- DEPLOYMENT_STATUS.md
|   |-- DEPLOYMENT_SUMMARY.md
|   |-- N8N_CLI_README.md
|   `-- WORKFLOW_CONVENTIONS.md
|-- oca
|   `-- .gitkeep
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
|   |-- ODOO_INTEGRATION_MAP.md
|   `-- ipai_finance_closing_seed.json
|-- ops
|   |-- github
|   |-- DISASTER_RECOVERY.md
|   `-- backup-production.sh
|-- out
|   |-- concur_demo
|   |-- concur_demo_odoo_map
|   `-- copilot_index
|-- patches
|   `-- ipai_ce_cleaner_xmlid_fix.diff
|-- releasekit
|   |-- fastlane
|   |-- scripts
|   |-- store
|   `-- README.md
|-- scripts
|   |-- ci
|   |-- import
|   |-- kb
|   |-- lakehouse
|   |-- odoo
|   |-- ppm
|   |-- prod
|   |-- sync
|   |-- FIX_OWLERROR_GUIDE.md
|   |-- README.md
|   |-- activate-n8n-workflows.sh
|   |-- apply-supabase-schema.sh
|   |-- assign_module_icons.py
|   |-- auto_error_handler.sh
|   |-- backup_odoo.sh
|   |-- baseline-validation.sh
|   |-- bootstrap_apps_from_inventory.sh
|   |-- build_and_push_version.sh
|   |-- build_v0.10.0.sh
|   |-- build_v0.9.1.sh
|   |-- ce_oca_audit.py
|   |-- check-enterprise-modules.sh
|   |-- check_module_status.sh
|   |-- check_project_tasks.py
|   |-- ci_local.sh
|   |-- ci_smoke_test.sh
|   |-- cleanup-branches.sh
|   |-- cleanup-duplicate-dec2025-tasks.sql
|   |-- cleanup_duplicate_users.sql
|   |-- configure_gmail_smtp.py
|   |-- configure_zoho_smtp.py
|   |-- convert_csv_to_xml.py
|   |-- convert_seed_to_xml.py
|   |-- copilot_ingest.py
|   |-- create-module-readme.sh
|   |-- create-release.sh
|   |-- deploy-bir-compliance.sh
|   |-- deploy-december-2025-bir-tasks.sh
|   |-- deploy-n8n-workflows.sh
|   |-- deploy-odoo-modules.sh
|   |-- deploy-to-server.sh
|   |-- deploy_afc_rag.sh
|   |-- deploy_custom_image.sh
|   |-- deploy_notion_tasks.sh
|   |-- deploy_odoo_smart.sh
|   |-- deploy_odoo_upgrade.sh
|   |-- deploy_prod.sh
|   |-- deploy_workos_prod.sh
|   |-- deployment-checklist.sh
|   |-- enhanced_health_check.sh
|   |-- erp_config_cli.sh
|   |-- finance_ppm_health_check.sh
|   |-- finance_ppm_health_check.sql
|   |-- finance_ppm_restore_golden.sh
|   |-- fix-finance-ppm-schema.sh
|   |-- fix-pay-invoices-online-error.py
|   |-- fix_home_manual.sql
|   |-- fix_home_page.sql
|   |-- full_deploy_sanity.sh
|   |-- gen_repo_tree.sh
|   |-- gen_repo_tree_fallback.sh
|   |-- generate_2026_finance_calendar.py
|   |-- generate_2026_schedule.py
|   |-- generate_finance_dashboard.py
|   |-- generate_module_docs.py
|   |-- generate_odoo_dbml.py
|   |-- generate_seed_xml.py
|   |-- healthcheck_odoo.sh
|   |-- image-diff-report.sh
|   |-- image_audit.sh
|   |-- import_month_end_tasks.py
|   |-- insert-december-2025-tasks.sql
|   |-- insert-december-2025-tasks.sql.bak
|   |-- install-git-hooks.sh
|   |-- install_all_ipai_modules.sh
|   |-- install_ipai_finance_ppm.sh
|   |-- install_module_xmlrpc.py
|   |-- introspect_project.py
|   |-- ipai_full_audit.py
|   |-- ipai_install_upgrade_test.sh
|   |-- ipai_quality_gate.sh
|   |-- map_logframe.py
|   |-- module_audit_agent.py
|   |-- new_conversation_entry.sh
|   |-- notify_slack.sh
|   |-- oca-bootstrap.sh
|   |-- oca-sync.sh
|   |-- oca-update.sh
|   |-- odoo_mattermost_integration.py
|   |-- odoo_smoke_close.sh
|   |-- package_image_tarball.sh
|   |-- parse_notion_tasks.py
|   |-- policy-check.sh
|   |-- pre_install_snapshot.sh
|   |-- release_gate.sh
|   |-- repo_health.sh
|   |-- report_ci_telemetry.sh
|   |-- run_clarity_ppm_reverse.sh
|   |-- run_odoo_migrations.sh
|   |-- run_project_introspection.sh
|   |-- scan_ipai_modules.py
|   |-- seed_finance_close_from_xlsx.py
|   |-- setup_afc_rag.sh
|   |-- setup_keycloak_db.sh
|   |-- setup_mattermost_db.sh
|   |-- simple_deploy.sh
|   |-- smoketest.sh
|   |-- spec-kit-enforce.py
|   |-- spec_validate.sh
|   |-- sync-tokens.sh
|   |-- sync_current_state.sh
|   |-- sync_directional.py
|   |-- test_afc_rag.py
|   |-- test_deploy_local.sh
|   |-- update_diagram_manifest.py
|   |-- validate-continue-config.sh
|   |-- validate-spec-kit.sh
|   |-- validate_m1.sh
|   |-- validate_manifests.py
|   |-- verify-https.sh
|   |-- verify.sh
|   |-- verify_backup.sh
|   |-- verify_phase3.py
|   `-- worktree-setup.sh
|-- seeds
|   |-- schema
|   |-- scripts
|   |-- shared
|   |-- workstreams
|   `-- README.md
|-- services
|   `-- notion-sync
|-- skillpack
|   `-- manifest.json
|-- skills
|   |-- visio-drawio-export
|   |-- architecture_diagrams.skill.json
|   |-- superset_mcp.skill.json
|   `-- visio_drawio_export.skill.json
|-- spec
|   |-- adk-control-room
|   |-- bir-tax-compliance
|   |-- close-orchestration
|   |-- continue-plus
|   |-- control-room-api
|   |-- docs-platform-sapgrade
|   |-- erp-saas-clone-suite
|   |-- expense-automation
|   |-- hire-to-retire
|   |-- insightpulse-docs-ai
|   |-- insightpulse-mobile
|   |-- ipai-control-center
|   |-- ipai-copilot
|   |-- ipai-month-end
|   |-- ipai-tbwa-finance
|   |-- knowledge-hub
|   |-- notion-finance-ppm-control-room
|   |-- odoo-apps-inventory
|   |-- odoo-ce
|   |-- odoo-mcp-server
|   |-- parallel-control-planes
|   |-- pulser-master-control
|   |-- seed-bundle
|   |-- workos-notion-clone
|   |-- constitution.md
|   |-- plan.md
|   |-- prd.md
|   `-- tasks.md
|-- specs
|   |-- 003-ai-enrichment
|   |-- 002-odoo-expense-equipment-mvp.prd.md
|   |-- 003-finance-ppm.prd.md
|   |-- 003-odoo-custom-image.prd.md
|   |-- INSTALL_SEQUENCE.md
|   |-- MODULE_SERVICE_MATRIX.md
|   |-- README.md
|   `-- tasks.md
|-- src
|   `-- lakehouse
|-- supabase
|   |-- functions
|   |-- migrations
|   |-- seed
|   |-- seeds
|   |-- SECURITY_LINTER_REMEDIATION.md
|   `-- config.toml
|-- tasks
|   `-- infra
|-- templates
|   `-- module_readme
|-- tests
|   |-- load
|   |-- playwright
|   `-- regression
|-- tools
|   |-- audit
|   |-- catalog
|   |-- db-inventory
|   |-- docs-crawler
|   |-- docs_catalog
|   |-- parity
|   |-- seed_all.ts
|   |-- seed_doc_ocr.ts
|   |-- seed_ppm.ts
|   |-- seed_retail_intel.ts
|   `-- seed_te_cheq.ts
|-- vendor
|   |-- oca
|   |-- oca-sync.sh
|   |-- oca.lock
|   `-- oca.lock.json
|-- vercel
|   `-- api
|-- workflows
|   |-- finance_ppm
|   |-- n8n
|   |-- odoo
|   |-- SHADOW_ENTERPRISE_STACK.md
|   |-- WEBHOOK_DEPLOYMENT_GUIDE.md
|   |-- n8n_bir_deadline_webhook.json
|   |-- n8n_enrichment_agent.json
|   |-- n8n_ocr_expense_webhook.json
|   `-- n8n_scout_sync_webhook.json
|-- .agentignore
|-- .env.example
|-- .env.production
|-- .flake8
|-- .gitignore
|-- .gitmodules
|-- .pre-commit-config.yaml
|-- ANALYTICS_ACTIVATION_SEQUENCE.md
|-- AUDIT_FIXES_APPLIED.md
|-- AUTO_HEALING_SYSTEM_SUMMARY.md
|-- CHANGELOG.md
|-- CI_CD_AUTOMATION_SUMMARY.md
|-- CI_CD_TROUBLESHOOTING_GUIDE.md
|-- CLAUDE.md
|-- CLAUDE_NEW.md
|-- COMPREHENSIVE_DEPLOYMENT_SUMMARY.md
|-- CONTRIBUTING.md
|-- DEPLOYMENT_MVP.md
|-- DEPLOYMENT_REPORT.md
|-- DEPLOYMENT_REPORT_FINAL.md
|-- DEPLOYMENT_RUNBOOK.md
|-- DEPLOYMENT_STATUS.md
|-- DEPLOYMENT_VALIDATION_REPORT.md
|-- DEPLOYMENT_VERIFICATION.md
|-- DEPLOYMENT_WORKFLOW.md
|-- Dockerfile
|-- Dockerfile.v0.10.0
|-- ERP_CONFIGURATION_SUMMARY.md
|-- EXECUTE_NOW.md
|-- FINANCE_PPM_CANONICAL.md
|-- FINANCE_PPM_CE_DASHBOARD_GUIDE.md
|-- FINANCE_PPM_DASHBOARD_GUIDE.md
|-- FINANCE_PPM_IMPORT_GUIDE.md
|-- HOTFIX_OWLERROR.sh
|-- IDENTITY_CHATOPS_DEPLOYMENT_SUMMARY.md
|-- INFRASTRUCTURE_PLAN.md
|-- INSIGHTPULSE_ERP_CONFIGURATION_GUIDE.md
|-- KAPA_STYLE_DOCS_ASSISTANT_IMPLEMENTATION.md
|-- MATTERMOST_OPEX_INTEGRATION.md
|-- MCP_QUICK_START.md
|-- NOVEMBER_2025_CLOSE_TIMELINE.md
|-- NOVEMBER_2025_PPM_GO_LIVE_SUMMARY.md
|-- OCR_PROJECT_COMPLETE.md
|-- ODOO_18_VSCODE_SETUP.md
|-- ODOO_OCR_SETUP.md
|-- POSTGRES_PASSWORD_SOLUTION.md
|-- PRODUCTION_DEPLOY_WORKOS.sh
|-- PROD_DEPLOY.md
|-- PROJECT_WRAPPER_IMPLEMENTATION.md
|-- PROJECT_WRAPPER_IMPLEMENTATION_SUMMARY.md
|-- README.md
|-- README_BUILD.md
|-- README_PATCH.md
|-- RELEASE_v0.9.0.md
|-- REPO_RESTRUCTURE_PLAN.md
|-- SAFETY_MECHANISMS.md
|-- SECURITY.md
|-- SITEMAP.md
|-- STRATEGIC_PPM_ANALYTICS_SUMMARY.md
|-- TAG_LABEL_VOCABULARY.md
|-- TBWA_IPAI_MODULE_STANDARD.md
|-- TREE.md
|-- VERIFY.md
|-- VSCODE_CLAUDE_CONFIGURATION_SUMMARY.md
|-- bir_deadlines_2026.csv
|-- branch_protection.json
|-- constitution.md
|-- custom_module_inventory.md
|-- deploy_m1.sh.template
|-- deploy_ppm_dashboard.sh
|-- deploy_ppm_dashboard_direct.sh
|-- deployment_readiness_assessment.md
|-- docker-compose.mcp-local.yml
|-- docker-compose.prod.yml
|-- docker-compose.yml
|-- final_verification.sh
|-- finance_calendar_2026.csv
|-- finance_calendar_2026.html
|-- finance_compliance_calendar_template.csv
|-- finance_directory.csv
|-- finance_directory_template.csv
|-- finance_events_2026.json
|-- finance_monthly_tasks_template.csv
|-- finance_wbs.csv
|-- finance_wbs_deadlines.csv
|-- implementation_plan.md
|-- implementation_plan_agent.md
|-- import_finance_data.py
|-- import_finance_directory.py
|-- import_november_wbs.py
|-- install_module.py
|-- install_ppm_module.py
|-- install_ppm_monthly_close.sh
|-- ipai_ce_branding_patch_v1.2.0.zip
|-- ipai_finance_ppm_directory.csv
|-- n8n_automation_strategy.md
|-- n8n_opex_cli.sh
|-- oca.lock.json
|-- odoo-bin
|-- odoo-ce-target.zip
|-- odoo-v1.2.0-build.zip
|-- odoo_ce_expert_prompt.md
|-- package.json
|-- parity_report.json
|-- ph_holidays_2026.csv
|-- plan.md
|-- pnpm-workspace.yaml
|-- ppm_dashboard_views.xml
|-- query_memory.py
|-- requirements.txt
|-- spec.md
|-- task.md
|-- tasks.md
|-- turbo.json
|-- update_finance_ppm.py
|-- update_module.py
|-- vercel.json
|-- verify_deployment.py
|-- verify_finance_ppm.py
|-- verify_ppm_installation.sh
|-- walkthrough.md
`-- workflow_template.csv
```
<!-- REPO_TREE_END -->

**Note**: This tree is auto-generated by `scripts/gen_repo_tree.sh` and enforced in CI. Any manual edits will be overwritten.

## 3. PRDs in This Repo

- [002 – InsightPulse ERP Expense & Equipment MVP](specs/002-odoo-expense-equipment-mvp.prd.md)

(Additional PRDs will be added under `specs/00x-*.prd.md` as the platform grows.)

## 4. In-Scope (Current Wave)

- Odoo CE 18 deployment (Docker/K8s friendly).
- OCA module integration for accounting, expense, and stock/maintenance.
- Custom modules:
  - `ipai_expense` – PH-specific expense + travel workflows.
  - `ipai_equipment` – Cheqroom-style equipment booking.
  - `ipai_ce_cleaner` – removal of Enterprise/IAP UI and odoo.com links.
- Reverse proxy and SSL termination via Nginx or equivalent.
- CI guardrails to enforce:
  - No Enterprise modules present/installed.
  - No `odoo.com` links or IAP references in templates/code.

## 5. Explicitly Out of Scope (MVP)

- Odoo Enterprise modules or licenses.
- Any use of Odoo IAP (SMS, email, or credits) in production.
- Full HR/payroll, manufacturing, or advanced warehouse flows.
- Multi-company consolidations and group reporting.

## 6. Success Criteria (MVP)

- Expense and travel workflows complete from creation → approval → posting, using CE/OCA only.
- Equipment booking lifecycle (reserve → checkout → check-in → incident) works end-to-end.
- UI does **not** display any Enterprise or IAP banners, menus, or upsells.
- Grep across the repo for `odoo.com` returns **no user-facing** links.
- `erp.insightpulseai.net` is the canonical entry point for all users.
- CI/CD fails if Enterprise/IAP traces are introduced.

## 7. Dependencies & Integrations

- PostgreSQL (single instance for MVP).
- Nginx (or equivalent) reverse proxy and SSL termination.
- Optional: centralized logging/monitoring stack (to be defined in a later PRD).

## 8. Roadmap Link

Implementation details and milestones are tracked in:

- [plan.md](plan.md) – phases and milestones.
- [tasks.md](tasks.md) – actionable task checklist.
