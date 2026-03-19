# InsightPulse Odoo CE – Project Spec

Repo: https://github.com/jgtolentino/odoo
Owner: InsightPulseAI – ERP Platform Team
Status: Active

## 1. Overview

This repository contains the **InsightPulse Odoo CE** stack: a fully self-hosted, Odoo Community Edition + OCA–based ERP for expense management and equipment booking.

The system is designed to:

- Replace **SAP Concur** for PH-focused expense & travel workflows.
- Replace **Cheqroom** for equipment catalog, bookings, and incident tracking.
- Run **only** on Odoo Community Edition + OCA modules and custom `ipai_*` addons.
- Avoid all Odoo Enterprise codepaths, IAP services, and odoo.com upsell links.
- Serve exclusively under InsightPulse domains (e.g. `erp.insightpulseai.com`).

## 2. Repository Structure

<!-- REPO_TREE_START -->
```text
.
AGENTS.md
ANALYTICS_ACTIVATION_SEQUENCE.md
AUDIT_FIXES_APPLIED.md
AUTO_HEALING_SYSTEM_SUMMARY.md
AUTO_REVIEW_AND_FIX_SUMMARY.md
CHANGELOG.md
CI_CD_AUTOMATION_SUMMARY.md
CI_CD_TROUBLESHOOTING_GUIDE.md
CI_MINIMAL_SET.md
CLAUDE.md
CLAUDE_CODE_WEB.md
CLAUDE_NEW.md
COMPREHENSIVE_DEPLOYMENT_SUMMARY.md
CONTRIBUTING.md
CREDENTIALS_SUMMARY.md
DEPLOYMENT_CHECKLIST.md
DEPLOYMENT_COMPLETE.md
DEPLOYMENT_MVP.md
DEPLOYMENT_REPORT.md
DEPLOYMENT_REPORT_FINAL.md
DEPLOYMENT_RUNBOOK.md
DEPLOYMENT_STATE_CURRENT.md
DEPLOYMENT_STATUS.md
DEPLOYMENT_VALIDATION_REPORT.md
DEPLOYMENT_VERIFICATION.md
DEPLOYMENT_WORKFLOW.md
DEPLOY_ENTERPRISE_BRIDGE_FIX.md
DEPLOY_NOW.md
Dockerfile
Dockerfile.v0.10.0
ERP_CONFIGURATION_SUMMARY.md
EXECUTE_NOW.md
FINANCE_PPM_CANONICAL.md
FINANCE_PPM_CE_DASHBOARD_GUIDE.md
FINANCE_PPM_DASHBOARD_GUIDE.md
FINANCE_PPM_IMPORT_GUIDE.md
HOTFIX_OWLERROR.sh
HOTFIX_SUMMARY.md
HYBRID_SETUP.md
IDENTITY_CHATOPS_DEPLOYMENT_SUMMARY.md
INFRASTRUCTURE_PLAN.md
INFRASTRUCTURE_SUMMARY.md
INSIGHTPULSE_ERP_CONFIGURATION_GUIDE.md
KAPA_STYLE_DOCS_ASSISTANT_IMPLEMENTATION.md
LOCAL_SETUP.md
MCP_QUICK_START.md
Makefile
Month-end Closing Task and Tax Filing ext.xlsx
NOVEMBER_2025_CLOSE_TIMELINE.md
NOVEMBER_2025_PPM_GO_LIVE_SUMMARY.md
OCR_PROJECT_COMPLETE.md
ODOO_18_VSCODE_SETUP.md
ODOO_ENV_DIAGNOSTIC.md
ODOO_OCR_SETUP.md
PENDING_TASKS_AUTO_AUDIT.md
POSTGRES_PASSWORD_SOLUTION.md
PRODUCTION_DEPLOY_WORKOS.sh
PROD_DEPLOY.md
README.md
README_BUILD.md
README_PATCH.md
RELEASE_v0.9.0.md
REPORT.md
REPO_RESTRUCTURE_PLAN.md
SAFETY_MECHANISMS.md
SANDBOX.md
SECURITY.md
STRATEGIC_PPM_ANALYTICS_SUMMARY.md
TAG_LABEL_VOCABULARY.md
TBWA_IPAI_MODULE_STANDARD.md
VERIFY.md
VSCODE_CLAUDE_CONFIGURATION_SUMMARY.md
_work
|-- OCA-ai
addons
addons.manifest.json
|-- _deprecated
|-- ipai
|-- ipai_ai_agent_builder
|-- ipai_ai_rag
|-- ipai_ai_tools
|-- ipai_ask_ai
|-- ipai_ask_ai_chatter
|-- ipai_bir_data
|-- ipai_bir_tax_compliance
|-- ipai_crm_pipeline
|-- ipai_doc_ocr_bridge
|-- ipai_docflow_review
|-- ipai_enterprise_bridge
|-- ipai_finance_closing
|-- ipai_finance_ppm_golive
|-- ipai_finance_ppm_umbrella
|-- ipai_grid_view
|-- ipai_month_end
|-- ipai_month_end_closing
|-- ipai_ocr_gateway
|-- ipai_ops_mirror
|-- ipai_platform_approvals
|-- ipai_platform_audit
|-- ipai_platform_permissions
|-- ipai_platform_theme
|-- ipai_platform_workflow
|-- ipai_ppm_okr
|-- ipai_sms_gateway
|-- ipai_superset_connector
|-- ipai_tbwa_finance
|-- ipai_theme_tbwa
|-- ipai_theme_tbwa_backend
|-- ipai_web_theme_chatgpt
|-- ipai_workos_affine
|-- ipai_workos_blocks
|-- ipai_workos_canvas
|-- ipai_workos_collab
|-- ipai_workos_core
|-- ipai_workos_db
|-- ipai_workos_search
|-- ipai_workos_templates
|-- ipai_workos_views
agent-library
agent-library-pack
|-- README.md
|-- prompts
|-- router
|-- schemas
|-- scripts
|-- Makefile
|-- README.md
|-- _shared
|-- app
|-- ci
|-- odoo
|-- prompts
|-- schemas
|-- scripts
|-- templates
|-- uiux
|-- web
agents
|-- AGENT_SKILLS_REGISTRY.yaml
|-- ORCHESTRATOR.md
|-- PRIORITIZED_ROADMAP.md
|-- README.md
|-- capabilities
|-- custom_module_auditor.md
|-- knowledge
|-- loops
|-- odoo_oca_ci_fixer.yaml
|-- odoo_reverse_mapper.yaml
|-- personas
|-- policies
|-- procedures
|-- prompts
|-- registry
|-- smart_delta_oca.yaml
aiux_ship_manifest.yml
api
|-- oca-docs-brain-openapi.yaml
architecture-review
|-- README.md
|-- baseline
|-- framework
|-- templates
archive
|-- addons
|-- compose
|-- deprecated
artifacts
|-- audit
|-- ce_oca_equivalents_audit.csv
|-- ce_oca_equivalents_audit.json
|-- docs_site
|-- finance_ppm_seed_audit.json
|-- forbidden_scan.txt
|-- gate_run_summary.json
|-- install_proof.txt
|-- ipai_install_upgrade_matrix.csv
|-- ipai_install_upgrade_matrix.json
|-- ipai_quality_gate.csv
|-- ipai_quality_gate.json
|-- logs
|-- module_audit_baseline.json
|-- module_audit_matrix.csv
|-- module_audit_matrix.json
|-- parity
|-- seed_audit.json
|-- seed_export
|-- seed_replace
|-- supabase_verify
audit
|-- snapshot.json
|-- snapshot.txt
automations
|-- n8n
baselines
|-- v0.2.1-quality-baseline-20251121.txt
bin
|-- README.md
|-- ci_sync_check.sh
|-- copilot_drift_check.sh
|-- finance-cli.sh
|-- import_bir_schedules.py
|-- odoo-check-gate
|-- odoo-tests.sh
|-- postdeploy-finance.sh
bir_deadlines_2026.csv
branch_protection.json
branding
|-- fluentui-system-icons
calendar
|-- 2026_FinanceClosing_Master.csv
|-- FinanceClosing_RecurringTasks.ics
catalog
|-- alternatives.yaml
|-- best_of_breed.yaml
|-- ee_surface
|-- equivalence_matrix.csv
|-- equivalence_matrix_workos_notion.csv
|-- odoo_parity_plans.schema.json
|-- odoo_parity_plans.yaml
|-- schema.json
catalogs
|-- locales
|-- sap_concur_surface_catalog.yaml
ccpm
|-- bin
|-- package.json
|-- scripts
|-- spec
|-- src
|-- tsconfig.json
ci
|-- README.md
|-- odoo_core_addons_allowlist.txt
claudedocs
|-- 100_PERCENT_CLI_DEPLOYMENT.md
|-- DEPLOYMENT_SUMMARY.md
|-- FINAL_DEPLOYMENT_REPORT.md
|-- ISSUE_RESOLUTION_REPORT.md
|-- bir-filing-validation-report.md
clients
|-- flutter_receipt_ocr
coming-soon.html
config
|-- MAILGUN_INTEGRATION_COMPLETE.md
|-- MAILGUN_INTEGRATION_DEPLOYMENT.md
|-- PRODUCTION_DEPLOYMENT_SCRIPT.sh
|-- README_ADDONS_MANIFEST.md
|-- addons_manifest.oca_ipai.json
|-- capability_map.yaml
|-- consumers
|-- docflow
|-- ee_parity
|-- entrypoint.d
|-- extended-platform-install-order.yaml
|-- finance
|-- install_sets
|-- integrations
|-- ipai_ai
|-- mailgun_integration_implementation.json
|-- oca
|-- oca-repos.yaml
|-- odoo
|-- odoo-core.conf
|-- odoo.conf.template
|-- odoo.dev.conf
|-- odoo.prod.conf
|-- odoo.staging.conf
|-- parity
|-- pipeline.yaml
|-- routing_matrix.yml
|-- secrets_inventory.md
|-- ship_set.txt
|-- sources
|-- tokens
constitution.md
contains-studio-agents
|-- README.md
|-- design
|-- engineering
|-- marketing
|-- product
|-- project-management
|-- studio-operations
|-- testing
contracts
|-- delta
|-- lakehouse-executor.openapi.yaml
custom_module_inventory.md
data
|-- IMPORT_GUIDE.md
|-- bir_calendar_2026.json
|-- bir_december_2025_seed.xml
|-- employee_directory.json
|-- finance_seed
|-- import_templates
|-- month_end_closing_tasks.csv
|-- month_end_tasks.csv
|-- notion_tasks_deduplicated.json
|-- notion_tasks_parsed.json
|-- notion_tasks_with_logframe.json
|-- templates
|-- user_map.csv
db
|-- DB_TARGET_ARCHITECTURE.md
|-- audit
|-- import-templates
|-- migrations
|-- process_mining
|-- rls
|-- schema
|-- seeds
dbt
|-- dbt_project.yml
|-- profiles.yml.example
deploy_m1.sh.template
deploy_ppm_dashboard.sh
deploy_ppm_dashboard_direct.sh
deployment_readiness_assessment.md
design
design-tokens
|-- tokens.json
|-- README.md
|-- components
|-- inputs
|-- schema.tokens.json
|-- schema.wireframe.json
|-- tokens
|-- wireframe
dev
|-- odoo-addons
|-- postgres-init
|-- superset
devserver.config.json
docflow-agentic-finance
|-- README.md
|-- agents
|-- data
|-- docflow-daemon.pid
|-- odoo.pid
|-- pyproject.toml
|-- scripts
|-- spec
|-- src
|-- verify_smoke.sh
docker-compose.dev.yml
docker-compose.shell.yml
docker-compose.yml
docs
docs-assistant
|-- DEPLOYMENT_GUIDE.md
|-- api
|-- deploy
|-- mcp
|-- web
|-- 003-odoo-ce-custom-image-spec.md
|-- AGENTIC_CLOUD_PRD.md
|-- AGENT_FRAMEWORK_SESSION_REPORT.md
|-- AGENT_MEMORY_DEPLOYMENT.md
|-- AGENT_TROUBLESHOOTING_PLAYBOOK.md
|-- AIUX_SHIP_PRD.md
|-- AI_MODULE_NAMING_CONVENTION.md
|-- APP_ICONS_README.md
|-- AUTOMATED_TROUBLESHOOTING_GUIDE.md
|-- BACKLOG_COVERAGE_REPORT.json
|-- BACKLOG_COVERAGE_REPORT.md
|-- CANONICAL_ENFORCEMENT_REPORT.md
|-- CANONICAL_LINT.md
|-- CANONICAL_MAP.md
|-- CE_OCA_EQUIVALENTS_AUDIT.md
|-- CE_OCA_PROJECT_STACK.md
|-- CLAUDE_CODE_SETUP.md
|-- CODESPACES_SETUP.md
|-- CUSTOM_IMAGE_SUCCESS_CRITERIA.md
|-- DATABASE_PROMOTION_WORKFLOW.md
|-- DATABASE_SETUP.md
|-- DB_INIT_RUNBOOK.md
|-- DB_TUNING.md
|-- DELIVERABLES_MANIFEST.md
|-- DEPLOYMENT.md
|-- DEPLOYMENT_GUIDE.md
|-- DEPLOYMENT_INVARIANTS.md
|-- DEPLOYMENT_NAMING_MATRIX.md
|-- DEPLOYMENT_SUMMARY.md
|-- DEPLOY_NOTION_WORKOS.md
|-- DEPRECATED_DOCS.md
|-- DEPRECATION_PLAN.md
|-- DEVELOPER_TOOLS.md
|-- DIGITALOCEAN_EMAIL_SETUP.md
|-- DIGITALOCEAN_SMTP_UNBLOCK_REQUEST.md
|-- DIGITALOCEAN_VALIDATION_FRAMEWORK.md
|-- DIRECTIONAL_SYNC.md
|-- DNS_SETTINGS.md
|-- DOCKERFILE_COMPARISON.md
|-- DOCKER_CANONICAL_DIFF.md
|-- DOCKER_CD_MIGRATION_GUIDE.md
|-- DOCKER_SIMPLE_EXPLANATION.md
|-- DOCKER_SSOT_ARCHITECTURE.md
|-- DOCKER_VALIDATION_GUIDE.md
|-- DOKS_DEPLOYMENT_SUCCESS_CRITERIA.md
|-- DR_RUNBOOK.md
|-- ECOSYSTEM_GUIDE.md
|-- EE_IAP_TO_OCA_IPAI_MAPPING.md
|-- EE_TO_CE_OCA_MAPPING.md
|-- EMAIL_AND_OAUTH_SETUP.md
|-- ENTERPRISE_FEATURE_GAP.yaml
|-- EXECUTIVE_SUMMARY.md
|-- FEATURE_CHEQROOM_PARITY.md
|-- FEATURE_CONCUR_PARITY.md
|-- FEATURE_WORKSPACE_PARITY.md
|-- FINAL_DEPLOYMENT_GUIDE.md
|-- FINAL_OPERABILITY_CHECKLIST.md
|-- FINAL_READINESS_CHECK.md
|-- FINANCE_PPM_IMPLEMENTATION.md
|-- FIN_WORKSPACE_AUTOMATION_STATUS.md
|-- FIN_WORKSPACE_HARDENING_STATUS.md
|-- FIN_WORKSPACE_SETUP.md
|-- GANTT_TO_ODOO_CE_MAPPING.md
|-- GITHUB_PAT_CODESPACES.md
|-- GITHUB_PAT_SCOPES.md
|-- GITHUB_SECRETS_SETUP.md
|-- GIT_AUTH_PERMANENT_FIX.md
|-- GIT_WORKTREE_STRATEGY.md
|-- GO_LIVE_CHECKLIST.md
|-- GO_LIVE_CHECKLIST_ODOO18_IPAI.md
|-- GO_LIVE_PRODUCTION_CHECKLIST.md
|-- GO_LIVE_RUNBOOK.md
|-- HEADER_CLEANUP_SUMMARY.md
|-- HEALTH_CHECK.md
|-- IMAGE_GUIDE.md
|-- IMPLEMENTATION_SUMMARY.md
|-- INDEX.md
|-- INDUSTRY_PACKS_OCA_DEPENDENCIES.md
|-- INDUSTRY_PARITY_ANALYSIS.md
|-- INFRASTRUCTURE_CHECKLIST.md
|-- INTEGRATION_BUS_DEPLOYMENT.md
|-- IPAI_MODULES_INDEX.md
|-- IPAI_MODULE_INSTALLATION_ORDER.md
|-- KEYCLOAK_IDENTITY_PROVIDER_DEPLOYMENT.md
|-- KUBERNETES_MIGRATION_SPECIFICATION.md
|-- LOGIN_BUTTON_FIX.md
|-- MAILGUN_DNS_SETUP.md
|-- MCP_IMPLEMENTATION_STATUS.md
|-- MCP_SUPABASE_INTEGRATION.md
|-- MIXED_CONTENT_FIX.md
|-- MODULE_CONSOLIDATION_GUIDE.md
|-- MODULE_STATUS_FINAL.md
|-- MODULE_STATUS_REPORT.md
|-- MONOREPO_STRUCTURE.md
|-- MVP_GO_LIVE_CHECKLIST.md
|-- N8N_CREDENTIALS_BOOTSTRAP.md
|-- NAMING.md
|-- NAMING_CONVENTION_EQ_APP_TOOLS.md
|-- OCA_CHORE_SCOPE.md
|-- OCA_INSTALLATION_GUIDE.md
|-- OCA_MIGRATION.md
|-- OCA_STYLE_CONTRACT.md
|-- OCA_TEMPLATE_INTEGRATION.md
|-- ODOO18_ENTERPRISE_TO_CE_OCA_MAPPING.md
|-- ODOO_18_CE_CHEATSHEET.md
|-- ODOO_18_CE_MODULE_INSTALL_ORDER.md
|-- ODOO_18_EE_TO_CE_OCA_PARITY.md
|-- ODOO_ADDONS_PATH_CONFIGURATION.md
|-- ODOO_APPS_CATALOG.md
|-- ODOO_ARCHITECT_PERSONA.md
|-- ODOO_CE_DEPLOYMENT_SUMMARY.md
|-- ODOO_CE_v0.9.0_SECURITY_AUDIT_REPORT.md
|-- ODOO_COPILOT_THEME_TOKEN_MAP.md
|-- ODOO_EXECUTION.md
|-- ODOO_GOLIVE_SETTINGS_INVENTORY.md
|-- ODOO_HTTPS_OAUTH_TROUBLESHOOTING.md
|-- ODOO_IMAGE_SPEC.md
|-- ODOO_MODULE_DEPLOYMENT.md
|-- ODOO_PROGRAMMATIC_CONFIG.md
|-- OFFICIAL_ALIGNMENT.md
|-- OFFICIAL_TYPOLOGY.md
|-- OFFLINE_TARBALL_DEPLOYMENT.md
|-- PRD_ipai_ppm_portfolio.md
|-- PRODUCTION_DATABASE_CHECKLIST.md
|-- PRODUCTION_DEFAULTS.md
|-- PRODUCTION_DEPLOYMENT_CHECKLIST.md
|-- PRODUCTION_HOTFIX.md
|-- PROD_READINESS_GAPS.md
|-- PROD_SNAPSHOT_MANIFEST.md
|-- PROGRAMMATIC_CONFIG_PLAN.md
|-- QUICK_REFERENCE_SSO_SETUP.md
|-- QUICK_START.md
|-- QUICK_START_CONFIGURATION.md
|-- RAG_ARCHITECTURE_IMPLEMENTATION_PLAN.md
|-- README.md
|-- README_MCP_STACK.md
|-- RELEASE_NOTES_GO_LIVE.md
|-- REPOSITORY_STRUCTURE.md
|-- REPO_SNAPSHOT.json
|-- REPO_TREE.contract.md
|-- REPO_TREE.generated.md
|-- SAAS_PARITY_READINESS.md
|-- SCHEMA_NAMESPACE_POLICY.md
|-- SECRETS_NAMING_AND_STORAGE.md
|-- SEED_DATA_ASSESSMENT.md
|-- SEMANTIC_VERSIONING_STRATEGY.md
|-- SHIP_v1.1.0_SUMMARY.md
|-- SITEMAP.md
|-- SLUG_POLICY.md
|-- SMTP_SETUP_SUMMARY.md
|-- SSO_VALIDATION_CHECKLIST.md
|-- STAGING.md
|-- SUCCESS_CRITERIA.md
|-- SUPERSET_INTEGRATION.md
|-- SUPERSET_PPM_ANALYTICS_GUIDE.md
|-- TAGGING_STRATEGY.md
|-- TBWA_THEME_DEPLOYMENT.md
|-- TECHNICAL_GUIDE_SUPABASE_INTEGRATION.md
|-- TENANT_ARCHITECTURE.md
|-- TESTING_ODOO_18.md
|-- TRACEABILITY_INDEX.yaml
|-- TROUBLESHOOTING.md
|-- UI_THEME_CONSOLIDATION_PROPOSAL.md
|-- VERIFIED_MEMORY.md
|-- WBS_LOGFRAME_MAPPING.md
|-- WORKOS_DEPLOYMENT_MANIFEST.md
|-- ZOHO_DNS_SETUP.md
|-- adr
|-- advanced-animations-guide.md
|-- agents
|-- ai
|-- analytics
|-- api
|-- arch
|-- audits
|-- auth
|-- branch-cleanup-analysis.md
|-- brand
|-- cicd
|-- claude_code
|-- competency
|-- connectors
|-- constitution
|-- control
|-- curation
|-- data-model
|-- databricks
|-- db
|-- deployment
|-- deprecated
|-- design-system
|-- development
|-- diagrams
|-- ee-parity-gate
|-- ee_parity_map.md
|-- evidence
|-- github
|-- golive
|-- governance
|-- guides
|-- implementation
|-- incidents
|-- infra
|-- integration
|-- integrations
|-- ipai
|-- issues
|-- knowledge
|-- lakehouse
|-- llm
|-- llms
|-- llms-full.txt
|-- llms.txt
|-- memory
|-- migration
|-- module-health
|-- modules
|-- notion-odoo-substitute-catalog.md
|-- oca
|-- oca_project_modules_18.csv
|-- odoo
|-- odoo-18-handbook
|-- odoo-apps-parity.md
|-- odoo_core_schema.sql
|-- odooops-sh
|-- okr
|-- ord
|-- pages
|-- platform
|-- policy
|-- portfolio
|-- prd
|-- process
|-- prompts
|-- proofs
|-- qweb-templates-guide.md
|-- rationalization
|-- releases
|-- repo
|-- research
|-- runbooks
|-- runtime
|-- security
|-- seed-data
|-- setup
|-- stack
|-- state_machines
|-- strategy
|-- supabase-docs-patterns
|-- supabase-integration.md
|-- superset
|-- templates
|-- testing
|-- troubleshooting
|-- tutorials
|-- v0.9.1_DEPLOYMENT_GUIDE.md
|-- wiki
|-- workflows
engines
|-- _template
|-- doc-ocr
|-- retail-intel
|-- te-cheq
external-src
|-- account-closing
|-- account-financial-reporting
|-- account-financial-tools
|-- account-invoicing
|-- calendar
|-- contract
|-- dms
|-- hr-expense
|-- maintenance
|-- project
|-- purchase-workflow
|-- reporting-engine
|-- server-tools
|-- web
figma
figma-make-dev.yaml
figma.config.json
|-- README.md
|-- community
|-- connect
|-- tokens
final_verification.sh
finance_calendar_2026.csv
finance_calendar_2026.html
finance_compliance_calendar_template.csv
finance_directory.csv
finance_directory_template.csv
finance_events_2026.json
finance_monthly_tasks_template.csv
finance_wbs.csv
finance_wbs_deadlines.csv
frontend-fluent
gemini.md
handbook
|-- README.md
|-- SUMMARY.md
|-- compliance
|-- finance
harness
|-- runners
implementation_plan.md
implementation_plan_agent.md
import_finance_data.py
import_finance_directory.py
import_november_wbs.py
infra
|-- ai
|-- azure
|-- caddy
|-- ce
|-- ci
|-- ci-odoo
|-- cloudflare
|-- databricks
|-- deploy
|-- digitalocean
|-- dns
|-- do-oca-stack
|-- docker
|-- docker-compose.prod.yaml
|-- doctl
|-- entrypoint.d
|-- lakehouse
|-- links
|-- mattermost
|-- monitoring
|-- nginx
|-- odoo
|-- odoo.conf
|-- ops-control
|-- platform-kit
|-- secrets
|-- stack
|-- supabase
|-- superset
|-- terraform
install_module.py
install_ppm_module.py
install_ppm_monthly_close.sh
integrations
|-- apps.yml
inventory
|-- latest
|-- runs
ipai-platform
|-- README.md
|-- compose.prod.override.external-db.yaml
|-- compose.prod.yaml
|-- compose.yaml
|-- nginx
|-- odoo
|-- scripts
ipai_ce_branding_patch_v1.2.0.zip
ipai_finance_ppm_directory.csv
ipai_open_semantics_migrations_and_functions.zip
ipai_theme_tbwa_18.0.1.0.0.zip
kb
|-- audit
|-- design_system
|-- finance_close
|-- parity
llms-full.txt
llms.txt
mattermost
|-- runbooks
|-- webhook-templates
mcp
|-- agentic-cloud.yaml
|-- coordinator
|-- local
|-- n8n-mcp
|-- odoo-mcp
|-- servers
|-- tools
memory
|-- README.md
|-- memory_policy.yaml
|-- packs
mkdocs.yml
n8n
|-- n8n_tenant_provisioning.json
|-- workflows
n8n_automation_strategy.md
n8n_opex_cli.sh
notion-n8n-monthly-close
|-- DEPLOYMENT_STATUS.md
|-- DEPLOYMENT_SUMMARY.md
|-- N8N_CLI_README.md
|-- WORKFLOW_CONVENTIONS.md
|-- scripts
|-- src
|-- supabase
|-- workflows
oca-aggregate.yml
oca.lock.json
ocr-adapter
|-- DEPLOYMENT.md
|-- Dockerfile
|-- README.md
|-- main.py
|-- nginx-site.conf
|-- requirements.txt
|-- scripts
|-- test-ocr.sh
|-- test_receipts
ocr_service
|-- ocr.pid
|-- server.py
odoo
odoo-bin
odoo-schema-mirror
|-- export_odoo_schema.py
|-- generate_dbml.py
|-- requirements.txt
|-- sync_to_supabase.py
|-- tests
|-- validate_parity.py
odoo.code-workspace
odoo.pid
|-- ODOO_INTEGRATION_MAP.md
|-- compose
|-- ipai_finance_closing_seed.json
odoo19
|-- CANONICAL_SETUP.md
|-- MIGRATION_COMPLETE.md
|-- MIGRATION_FROM_OLD_STACK.md
|-- QUICK_REFERENCE.md
|-- backups
|-- compose.yaml
|-- config
|-- docs
|-- scripts
odoo_local
|-- ODOO_INTEGRATION_MAP.md
|-- compose
|-- ipai_finance_closing_seed.json
ops
|-- DISASTER_RECOVERY.md
|-- alerting
|-- backlog
|-- backup
|-- backup-production.sh
|-- compose
|-- design
|-- github
|-- idp
|-- jobs
|-- observability
|-- pipelines
|-- runbooks
|-- secrets
osi
|-- osi_template.json
|-- osi_template.yaml
out
|-- FLAGSHIP_REPO_RECOMMENDATION.md
|-- INTEGRATIONS_OPPORTUNITIES.md
|-- STACK_RUNBOOK.md
|-- TOP_REPOS.md
|-- UPDATED_WORK_RECOMMENDATIONS.md
|-- concur_demo
|-- concur_demo_odoo_map
|-- copilot_index
|-- dns_audit.json
|-- ee_parity_matrix.md
|-- oca_inventory.json
|-- oca_inventory.md
|-- oca_repos_seed.txt
|-- repos_files.jsonl
|-- repos_inventory.json
|-- repos_names.txt
|-- repos_scored.json
package.json
parity
|-- ee_only
|-- parity-matrix.yaml
parity_report.html
parity_report.json
parity_report_final.html
parity_report_final_v2.html
patches
|-- ipai_ce_cleaner_xmlid_fix.diff
ph_holidays_2026.csv
pkgs
|-- agent-core
|-- agentic-codebase-crawler
|-- config
|-- echarts-react
|-- echarts-themes
|-- github-app
|-- ipai-ai-sdk
|-- ipai-ai-sdk-python
|-- ipai-design-tokens
|-- saas-types
|-- supabase
plan.md
platform
platform-kit
|-- cli
|-- docs
|-- reports
|-- db
pnpm-lock.yaml
pnpm-workspace.yaml
ppm_dashboard_views.xml
prototypes
|-- README.md
|-- ipai_aiux_chat
|-- ipai_fluent_web_365_copilot
|-- ipai_theme_aiux
pyproject.toml
query_memory.py
registry
|-- features
|-- integrations
releasekit
|-- README.md
|-- fastlane
|-- scripts
|-- store
reports
|-- parity
requirements-dev.txt
requirements-docs.txt
requirements-oca.txt
requirements.txt
runtime
|-- docker
|-- down.sh
|-- up.sh
sandbox
|-- dev
|-- workbench
schemas
|-- feature.schema.json
|-- gate_report.schema.json
|-- integration.schema.json
|-- parity
scripts
|-- CONFIG_INVENTORY.txt
|-- FIX_OWLERROR_GUIDE.md
|-- README.md
|-- README_CONFIG_MAIL_AI_OCR.md
|-- README_SEED_PROJECTS.md
|-- activate-n8n-workflows.sh
|-- agentic
|-- aiux
|-- apply-supabase-schema.sh
|-- apply_config.sh
|-- assign_module_icons.py
|-- audit
|-- audit_email_config.py
|-- audit_installed_modules.py
|-- audit_ipai_modules.py
|-- audit_oca_modules.py
|-- auth
|-- auto_error_handler.sh
|-- backlog_scan.py
|-- backup
|-- backup_odoo.sh
|-- backup_verify.sh
|-- baseline-validation.sh
|-- bir
|-- bootstrap_apps_from_inventory.sh
|-- bootstrap_execution_board.sh
|-- bootstrap_github_issues.sh
|-- bootstrap_ssot_dns_odoo_supabase.sh
|-- build_and_push_version.sh
|-- build_v0.10.0.sh
|-- build_v0.9.1.sh
|-- canonical_audit.py
|-- ce_oca_audit.py
|-- cf
|-- cf_delete_superset_dns.sh
|-- cf_upsert_superset_dns.sh
|-- check-enterprise-modules.sh
|-- check-generated-tokens.sh
|-- check-spec-kit.sh
|-- check-supabase-migrations.sh
|-- check_addon_allowlist.py
|-- check_go_live_manifest.py
|-- check_install_set_drift.sh
|-- check_module_status.sh
|-- check_odoosh_parity.py
|-- check_project_tasks.py
|-- check_secrets.sh
|-- check_undocumented_specs.py
|-- chore_repo.sh
|-- ci
|-- ci_gate
|-- ci_local.sh
|-- ci_odoo_changed_modules.py
|-- ci_odoo_gate.py
|-- ci_odoo_resolve_deps.py
|-- ci_odoo_resolve_impacted.py
|-- ci_odoo_run_install_upgrade.sh
|-- ci_smoke_test.sh
|-- clean-branches.sh
|-- cleanup-branches.sh
|-- clone_missing_oca_repos.sh
|-- cloudflare-dns-audit.sh
|-- cloudflare-enable-proxy.sh
|-- codespaces
|-- competency
|-- compose_vars.sh
|-- config_files_found.txt
|-- configure_base_url.py
|-- configure_gmail_smtp.py
|-- configure_gmail_smtp.sh
|-- configure_google_oauth.sh
|-- configure_mailgun_smtp.py
|-- configure_sendgrid_smtp.py
|-- configure_smtp.py
|-- configure_zoho_smtp.py
|-- convert_csv_to_xml.py
|-- convert_seed_to_xml.py
|-- copilot_ingest.py
|-- count_xml_seeds.py
|-- crawl_site.sh
|-- create-module-readme.sh
|-- create-release.sh
|-- create_parity_pr.sh
|-- db
|-- db-cleanup-legacy.sh
|-- db_verify.sh
|-- delete_user_safe.sh
|-- deploy
|-- deploy-bir-compliance.sh
|-- deploy-december-2025-bir-tasks.sh
|-- deploy-mailgun-mailgate.sh
|-- deploy-n8n-workflows.sh
|-- deploy-odoo-modules.sh
|-- deploy-otp-auth.sh
|-- deploy-tbwa-theme-tokens.sh
|-- deploy-to-server.sh
|-- deploy_afc_rag.sh
|-- deploy_complete_fix.sh
|-- deploy_custom_image.sh
|-- deploy_notion_tasks.sh
|-- deploy_odoo_smart.sh
|-- deploy_odoo_upgrade.sh
|-- deploy_parity_schema.sh
|-- deploy_prod.sh
|-- deploy_production.sh
|-- deploy_theme_to_production.sh
|-- deploy_vercel_prod.sh
|-- deploy_with_credentials.sh
|-- deploy_workos_prod.sh
|-- deployment-checklist.sh
|-- deprecation
|-- design
|-- design-sync.sh
|-- dev
|-- devcontainer_up.sh
|-- diagnose_prod.sh
|-- diagnose_smtp.sh
|-- discover_digitalocean_infra.sh
|-- discover_docker_infra.sh
|-- discover_odoo_infra.py
|-- discover_supabase_infra.py
|-- discover_supabase_ui_sources.sh
|-- dns
|-- docker
|-- docker-desktop-audit.sh
|-- docker-staging-audit.sh
|-- docs
|-- docs_refresh.sh
|-- down.sh
|-- drive_sync
|-- ee_replace_request.sh
|-- ee_surface
|-- enhanced_health_check.sh
|-- erd_dot.sql
|-- erp_config_cli.sh
|-- execute_rationalization.sh
|-- expense_ocr_ingest.sh
|-- export_architecture_diagrams.sh
|-- export_todo_seed.py
|-- extract_openai_academy_prompt_packs.py
|-- extract_remote_data.py
|-- figma
|-- figma-export-variables.mjs
|-- finance_ppm_health_check.sh
|-- finance_ppm_health_check.sql
|-- finance_ppm_restore_golden.sh
|-- finance_ppm_seed_audit.py
|-- fix-finance-ppm-schema.sh
|-- fix-pay-invoices-online-error.py
|-- fix_claude_code_bash_patterns.py
|-- fix_oauth_button.sh
|-- fix_oauth_button_odoo_core.sh
|-- fix_odoo18_views.py
|-- fix_permissions.sh
|-- fix_pos_enterprise_error.sh
|-- fixes
|-- force_asset_regeneration.sh
|-- full_deploy_sanity.sh
|-- gates
|-- gen_addons_path.py
|-- gen_addons_path.sh
|-- gen_install_set.py
|-- gen_odoo_editions_parity_seed.py
|-- gen_repo_tree.sh
|-- gen_repo_tree_fallback.sh
|-- generate
|-- generate-dns-artifacts.sh
|-- generate_2026_finance_calendar.py
|-- generate_2026_schedule.py
|-- generate_erd_graphviz.py
|-- generate_finance_dashboard.py
|-- generate_go_live_checklist.py
|-- generate_llm_docs.py
|-- generate_module_docs.py
|-- generate_module_health_report.py
|-- generate_module_signatures.py
|-- generate_month_end_imports.py
|-- generate_odoo_dbml.py
|-- generate_odoo_template.py
|-- generate_release_docs.sh
|-- generate_repo_index.py
|-- generate_schema_artifacts.sh
|-- generate_seed_audit_artifact.py
|-- generate_seed_xml.py
|-- generate_shadow_ddl.py
|-- generate_spec_report.py
|-- github
|-- go_live.sh
|-- go_no_go_check.sh
|-- health
|-- healthcheck_odoo.sh
|-- hotfix_icon_crash.sh
|-- hotfix_production.sh
|-- html_catalog.py
|-- image-diff-report.sh
|-- image_audit.sh
|-- import
|-- import_month_end_tasks.py
|-- incident_snapshot.sh
|-- infra-discovery
|-- ingest_docs_to_supabase.py
|-- ingest_knowledge_graph.py
|-- install-git-hooks.sh
|-- install-notion-stack.sh
|-- install-odoo-18-modules.sh
|-- install_all_ipai_modules.sh
|-- install_baseline.sh
|-- install_finance_stack.sh
|-- install_ipai_finance_ppm.sh
|-- install_module_xmlrpc.py
|-- install_oauth_module.py
|-- install_oca_modules.sh
|-- install_oca_parity.sh
|-- install_oca_project_modules.sh
|-- integration
|-- integrations
|-- introspect_project.py
|-- inventory_config_keys.sh
|-- investigate-erp-domain.sh
|-- ipai-view-migration
|-- ipai_ai_seed.sh
|-- ipai_full_audit.py
|-- ipai_install_upgrade_test.sh
|-- ipai_quality_gate.sh
|-- kb
|-- lakehouse
|-- lib
|-- lint.sh
|-- lint_all.sh
|-- lint_odoo_entrypoint.sh
|-- lock_stage.sh
|-- mailgun
|-- map_logframe.py
|-- memory
|-- module_audit_agent.py
|-- month_close
|-- n8n-gitops.sh
|-- new_conversation_entry.sh
|-- new_go_live_checklist.sh
|-- notify_slack.sh
|-- oca
|-- oca-bootstrap.sh
|-- oca-sync.sh
|-- oca-template-bootstrap.sh
|-- oca-update.sh
|-- oca_hydrate.sh
|-- ocadev
|-- odoo
|-- odoo-18-oca-install.sh
|-- odoo-automation
|-- odoo.sh
|-- odoo_check_ai_ocr_params.py
|-- odoo_check_mail.py
|-- odoo_coming_soon_install.sh
|-- odoo_coming_soon_rollback.sh
|-- odoo_coming_soon_verify.sh
|-- odoo_config_mail_ai_ocr.py
|-- odoo_configure_mail.sh
|-- odoo_db_schema_diff.sh
|-- odoo_ensure_modules_installed.sh
|-- odoo_env_diagnose.sh
|-- odoo_import_project_suite.py
|-- odoo_install_from_manifests.sh
|-- odoo_install_modules.sh
|-- odoo_install_oca_must_have.sh
|-- odoo_modules_preflight.sh
|-- odoo_parity
|-- odoo_rationalization.sh
|-- odoo_rollback_mail_ai_ocr.py
|-- odoo_runtime_snapshot.sh
|-- odoo_seed_post_upgrade.sh
|-- odoo_seed_projects_and_stages.py
|-- odoo_smoke_close.sh
|-- odoo_start_fetchmail.py
|-- odoo_update_modules.sh
|-- odoo_upgrade_modules.sh
|-- odoo_verify_from_manifests.py
|-- odoo_verify_modules.py
|-- odoo_verify_oca_must_have.py
|-- odooops
|-- ops
|-- package_image_tarball.sh
|-- parity
|-- parity_seed_sanity_check.py
|-- parse_notion_tasks.py
|-- plane
|-- plane_bir_bootstrap.sql
|-- policy
|-- policy-check.sh
|-- ppm
|-- pre_install_snapshot.sh
|-- prod
|-- prod_access_check.py
|-- prod_backup_dump.sh
|-- prod_db_guess.py
|-- promote.sh
|-- promote_oauth_users.py
|-- provision_tenant.sh
|-- provisioners
|-- recreate_odoo_prod.sh
|-- refactor
|-- regen_install_sets.sh
|-- release_gate.sh
|-- replace_seed_from_excel.py
|-- repo_health.sh
|-- report_ci_telemetry.sh
|-- report_ee_parity.py
|-- report_stale_branches.sh
|-- run_clarity_ppm_reverse.sh
|-- run_odoo_migrations.sh
|-- run_odoo_shell.sh
|-- run_project_introspection.sh
|-- sandbox
|-- scaffold_ipai_parity.py
|-- scaffold_ipai_parity.sh
|-- scan_ipai_modules.py
|-- scan_repos.sh
|-- schema_drift_env_check.sh
|-- score_repos.py
|-- screenshot_production.sh
|-- secret-scan.sh
|-- secrets
|-- security
|-- seed_companies_users.py
|-- seed_finance_close_from_xlsx.py
|-- seed_finance_ppm_stages.py
|-- seed_projects_from_xlsx.py
|-- seeds
|-- setup-codespaces-pat.sh
|-- setup-codespaces-secrets.sh
|-- setup-mailgun-secrets.sh
|-- setup_afc_rag.sh
|-- setup_config_env.sh
|-- setup_credentials.sh
|-- setup_keycloak_db.sh
|-- simple_deploy.sh
|-- skill_web_session_bridge.sh
|-- smoke.sh
|-- smoke_github_app.sh
|-- smoke_import_odoo.sh
|-- smoke_odoo_container.sh
|-- smoke_test_odoo.sh
|-- smoketest.sh
|-- spec-kit-enforce.py
|-- spec_validate.sh
|-- speckit-scaffold.sh
|-- sql
|-- ssh-tunnel-db.sh
|-- stack
|-- stack_verify.sh
|-- staging_down.sh
|-- staging_restore_and_sanitize.sh
|-- staging_up.sh
|-- start_local_odoo.sh
|-- status
|-- supabase
|-- supabase_delete_user.sh
|-- supabase_local.sh
|-- supabase_schema_diff.sh
|-- superset
|-- superset_db_connect.sh
|-- superset_db_setup.py
|-- sync
|-- sync-fluent-tokens.sh
|-- sync-tokens.sh
|-- sync_agent_memory.py
|-- sync_current_state.sh
|-- sync_directional.py
|-- sync_ipai_sample_metrics_to_supabase.py
|-- sync_odoo_shadow.py
|-- tenant_automation.py
|-- test-mailgun.py
|-- test-mailgun.sh
|-- test_afc_rag.py
|-- test_auth_bootstrap.sh
|-- test_deploy_local.sh
|-- test_ee_parity.py
|-- test_email_flow.sh
|-- test_ipai_install_upgrade.py
|-- test_magic_link.sh
|-- test_mcp_jobs.sh
|-- test_theme_locally.sh
|-- tests
|-- union_prune_install_sets.py
|-- up.sh
|-- update_diagram_manifest.py
|-- update_task_phase_tags.sh
|-- update_tasks_after_import.py
|-- upgrade_theme_module.py
|-- validate-continue-config.sh
|-- validate-openapi.mjs
|-- validate-spec-kit.sh
|-- validate_ai_naming.py
|-- validate_capabilities.sh
|-- validate_catalog.mjs
|-- validate_ee_iap_independence.sh
|-- validate_ee_replacements.py
|-- validate_finance_ppm_data.py
|-- validate_ipai_doc_module_refs.py
|-- validate_json_schema.mjs
|-- validate_m1.sh
|-- validate_manifest.py
|-- validate_manifests.py
|-- validate_no_deprecated_installed.sh
|-- validate_odoo19_spec.sh
|-- validate_odoo_parity_plans.mjs
|-- validate_production.sh
|-- validate_registries.py
|-- validate_repo_config.sh
|-- validate_repo_contract.sh
|-- validate_repo_layout.sh
|-- validate_spec_kit.py
|-- validate_spec_kit.sh
|-- validate_spec_kit_odooops.sh
|-- validate_ssot_excel.py
|-- vercel_promote_previous.sh
|-- verify-addon-permissions.sh
|-- verify-addons-mounts.sh
|-- verify-codespaces-auth.sh
|-- verify-control-plane.sh
|-- verify-dataverse-console.sh
|-- verify-dns-baseline.sh
|-- verify-dns-enhancements.sh
|-- verify-https.sh
|-- verify-odoo-18-oca.sh
|-- verify-service-health.sh
|-- verify-workspace-dns.sh
|-- verify.sh
|-- verify_auth.sh
|-- verify_auth_setup.sh
|-- verify_backup.sh
|-- verify_cdn.sh
|-- verify_email_auth.sh
|-- verify_generated_odoo_artifacts.sh
|-- verify_local.sh
|-- verify_login_button.sh
|-- verify_monitoring.sh
|-- verify_oca_ipai_layout.sh
|-- verify_phase3.py
|-- verify_phase5.sh
|-- verify_smtp.py
|-- verify_supabase_deploy.sh
|-- verify_supabase_full.sh
|-- verify_web_assets.sh
|-- web_sandbox_verify.sh
|-- web_session_init.sh
|-- whats_deployed.py
|-- whats_deployed.sh
|-- wiki_sync.sh
|-- worktree-setup.sh
|-- write_phase6_verification_summary.py
|-- xmlrpc_set_admin_password.py
security
|-- Caddyfile.shell
|-- WEB_SHELL_THREAT_MODEL.md
seed_export
|-- projects.csv
|-- stages.csv
|-- tags.csv
|-- tasks.csv
|-- users.csv
seeds
|-- README.md
|-- schema
|-- scripts
|-- shared
|-- workstreams
services
|-- notion-sync
|-- ocr
|-- pm_api
ship_v1_1_0.sh
skillpack
|-- manifest.json
skills
|-- AGENTS.md
|-- README.md
|-- architecture_diagrams.skill.json
|-- bir-tax-filing
|-- ci-run-validate
|-- expense-processing
|-- finance-month-end
|-- finance-ppm-health
|-- kg-entity-expand
|-- odoo
|-- odoo-module-audit
|-- odoo-module-scaffold
|-- odooops
|-- registry.yaml
|-- superset
|-- superset_mcp.skill.json
|-- user
|-- visio-drawio-export
|-- visio_drawio_export.skill.json
|-- web-session-command-bridge
spec
spec.md
|-- agent
|-- cloudflare-security
|-- composer-bugbot
|-- github-well-architected
|-- infra-well-architected
|-- odoo-ee-parity-seed
|-- odoo-sh-clone
|-- odoo-supabase-deployment
|-- odooops-sh
|-- parity
|-- refactor-automation
|-- repo-chores
specs
|-- 002-odoo-expense-equipment-mvp.prd.md
|-- 003-ai-enrichment
|-- 003-finance-ppm.prd.md
|-- 003-odoo-custom-image.prd.md
|-- INSTALL_SEQUENCE.md
|-- MODULE_SERVICE_MATRIX.md
|-- README.md
|-- agent-ready-cms
|-- docs
|-- gates
|-- tasks.md
src
|-- lakehouse
stack
|-- odoo19_stack.yaml
supabase
|-- SECURITY_LINTER_REMEDIATION.md
|-- config.toml
|-- functions
|-- migrations
|-- seed
|-- seed.sql
|-- seeds
|-- supabase
superclaude_bridge.yaml
task.md
tasks
tasks.md
|-- infra
temp-landing-page
templates
|-- module_readme
|-- odoo
|-- odooops-console
|-- saas-landing
tests
|-- api
|-- e2e
|-- load
|-- playwright
|-- regression
|-- sql
tools
|-- agent-router
|-- audit
|-- backlog
|-- catalog
|-- db-inventory
|-- dbml
|-- diagramflow
|-- docs-crawler
|-- docs_catalog
|-- graphs
|-- ipai_module_gen
|-- model-repo-scanner
|-- odoo_schema
|-- ops-mirror-worker
|-- parity
|-- pr-gate
|-- routing
|-- seed_all.ts
|-- seed_doc_ocr.ts
|-- seed_ppm.ts
|-- seed_retail_intel.ts
|-- seed_te_cheq.ts
turbo.json
update_finance_ppm.py
update_module.py
vendor
|-- oca
|-- oca-sync.sh
|-- oca.lock
|-- oca.lock.ce19.json
|-- oca.lock.json
vercel
vercel.json
|-- api
verify_deployment.py
verify_finance_ppm.py
verify_ppm_installation.sh
walkthrough.md
web
|-- ai-control-plane
|-- alpha-browser
|-- bi-architect
|-- billing-site
|-- chatgpt_ipai_ai_studio
|-- control-plane
|-- control-room
|-- control-room-api
|-- devops-engineer
|-- do-advisor-agent
|-- do-advisor-ui
|-- docs
|-- docs-ai-widget
|-- finance-ssc-expert
|-- ipai-chatgpt-app
|-- ipai-control-center-docs
|-- local-schema-server
|-- mcp-coordinator
|-- mobile
|-- multi-agent-orchestrator
|-- odoo-developer-agent
|-- odoo-frontend-shell
|-- odoo-saas-platform
|-- odooops-dashboard
|-- platform-kit
|-- policy-gateway
|-- pulser-runner
|-- superset-analytics
|-- superset-embed-api
|-- web
|-- web-backup-subscription-starter
|-- web-legacy-backup
workflow_template.csv
workflows
|-- SHADOW_ENTERPRISE_STACK.md
|-- WEBHOOK_DEPLOYMENT_GUIDE.md
|-- finance_ppm
|-- n8n
|-- n8n_bir_deadline_webhook.json
|-- n8n_enrichment_agent.json
|-- n8n_ocr_expense_webhook.json
|-- n8n_scout_sync_webhook.json
|-- odoo
|-- registry.yaml
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
- `erp.insightpulseai.com` is the canonical entry point for all users.
- CI/CD fails if Enterprise/IAP traces are introduced.

## 7. Dependencies & Integrations

- PostgreSQL (single instance for MVP).
- Nginx (or equivalent) reverse proxy and SSL termination.
- Optional: centralized logging/monitoring stack (to be defined in a later PRD).

## 8. Roadmap Link

Implementation details and milestones are tracked in:

- [plan.md](plan.md) – phases and milestones.
- [tasks.md](tasks.md) – actionable task checklist.
