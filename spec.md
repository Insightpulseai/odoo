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
|-- .agent
|   |-- antigravity
|   |-- skills
|   |-- workflows
|   `-- rules.md
|-- .ai
|   `-- bugbot-rules.yml
|-- .claude
|   |-- commands
|   |-- hooks
|   |-- superclaude
|   |-- mcp-servers.json
|   |-- project_memory.db
|   |-- query_memory.py
|   |-- settings.json
|   |-- settings.local.json
|   `-- settings.web.json
|-- .continue
|   |-- prompts
|   |-- rules
|   `-- config.json
|-- .devcontainer
|   |-- backup
|   |-- scripts
|   |-- Dockerfile
|   |-- devcontainer.json
|   `-- docker-compose.yml
|-- .gemini
|   `-- tmp
|-- .githooks
|   `-- pre-commit
|-- .github
|   |-- ISSUE_TEMPLATE
|   |-- agents
|   |-- ci
|   |-- workflows
|   |-- CODEOWNERS
|   |-- STATUS_TAXONOMY.md
|   |-- copilot-instructions.md
|   `-- pull_request_template.md
|-- .insightpulse
|   |-- sync-config.yaml
|   `-- sync.yaml
|-- .lib
|   |-- bench.db
|   |-- bench.db-shm
|   |-- bench.db-wal
|   |-- bench_full.db
|   |-- bench_full.db-shm
|   |-- bench_full.db-wal
|   |-- lib.config.json
|   |-- lib.db
|   |-- lib.db-shm
|   `-- lib.db-wal
|-- .pnpm-store
|   `-- v10
|-- .supabase
|   `-- config.toml
|-- .venv
|   |-- bin
|   |-- include
|   |-- lib
|   `-- pyvenv.cfg
|-- .vscode
|   |-- README.md
|   |-- extensions.json
|   |-- ipai_workspace.code-workspace
|   |-- launch.json
|   |-- mcp-dev.code-workspace
|   |-- mcp-prod.code-workspace
|   |-- mcp.json
|   |-- settings.json
|   |-- shortcuts.json
|   `-- tasks.json
|-- _work
|   `-- OCA-ai
|-- addons
|   |-- ipai
|   |-- ipai_ai_agent_builder
|   |-- ipai_ai_rag
|   |-- ipai_ai_tools
|   |-- ipai_ask_ai
|   |-- ipai_ask_ai_chatter
|   |-- ipai_bir_data
|   |-- ipai_bir_tax_compliance
|   |-- ipai_crm_pipeline
|   |-- ipai_doc_ocr_bridge
|   |-- ipai_docflow_review
|   |-- ipai_enterprise_bridge
|   |-- ipai_finance_closing
|   |-- ipai_finance_ppm_golive
|   |-- ipai_finance_ppm_umbrella
|   |-- ipai_grid_view
|   |-- ipai_month_end
|   |-- ipai_month_end_closing
|   |-- ipai_ocr_gateway
|   |-- ipai_ops_mirror
|   |-- ipai_platform_approvals
|   |-- ipai_platform_audit
|   |-- ipai_platform_permissions
|   |-- ipai_platform_theme
|   |-- ipai_platform_workflow
|   |-- ipai_ppm_okr
|   |-- ipai_sms_gateway
|   |-- ipai_superset_connector
|   |-- ipai_tbwa_finance
|   |-- ipai_theme_tbwa
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
|   |-- oca
|   `-- test_theme_local
|-- agent-library
|   |-- _shared
|   |-- app
|   |-- ci
|   |-- dist
|   |-- evidence
|   |-- odoo
|   |-- prompts
|   |-- schemas
|   |-- scripts
|   |-- templates
|   |-- uiux
|   |-- web
|   |-- Makefile
|   `-- README.md
|-- agent-library-pack
|   |-- prompts
|   |-- router
|   |-- schemas
|   |-- scripts
|   `-- README.md
|-- agents
|   |-- capabilities
|   |-- knowledge
|   |-- loops
|   |-- personas
|   |-- policies
|   |-- procedures
|   |-- prompts
|   |-- registry
|   |-- AGENT_SKILLS_REGISTRY.yaml
|   |-- ORCHESTRATOR.md
|   |-- PRIORITIZED_ROADMAP.md
|   |-- README.md
|   |-- custom_module_auditor.md
|   |-- odoo_oca_ci_fixer.yaml
|   |-- odoo_reverse_mapper.yaml
|   `-- smart_delta_oca.yaml
|-- api
|   `-- oca-docs-brain-openapi.yaml
|-- apps
|   |-- ai-control-plane
|   |-- alpha-browser
|   |-- bi-architect
|   |-- billing-site
|   |-- chatgpt_ipai_ai_studio
|   |-- control-plane
|   |-- control-room
|   |-- control-room-api
|   |-- devops-engineer
|   |-- do-advisor-agent
|   |-- do-advisor-ui
|   |-- docs
|   |-- docs-ai-widget
|   |-- finance-ssc-expert
|   |-- ipai-chatgpt-app
|   |-- ipai-control-center-docs
|   |-- local-schema-server
|   |-- mcp-coordinator
|   |-- mobile
|   |-- multi-agent-orchestrator
|   |-- odoo-developer-agent
|   |-- odoo-frontend-shell
|   |-- odoo-saas-platform
|   |-- platform-kit
|   |-- policy-gateway
|   |-- pulser-runner
|   |-- superset-analytics
|   |-- superset-embed-api
|   |-- web
|   |-- web-backup-subscription-starter
|   `-- web-legacy-backup
|-- architecture-review
|   |-- baseline
|   |-- framework
|   |-- templates
|   `-- README.md
|-- archive
|   |-- addons
|   |-- compose
|   `-- deprecated
|-- artifacts
|   |-- docs_site
|   |-- logs
|   |-- parity
|   |-- seed_export
|   |-- seed_replace
|   |-- supabase_verify
|   |-- ce_oca_equivalents_audit.csv
|   |-- ce_oca_equivalents_audit.json
|   |-- docs_build.log
|   |-- finance_ppm_seed_audit.json
|   |-- forbidden_scan.txt
|   |-- gate_run_summary.json
|   |-- install_proof.txt
|   |-- ipai_install_upgrade_matrix.csv
|   |-- ipai_install_upgrade_matrix.json
|   |-- ipai_quality_gate.csv
|   |-- ipai_quality_gate.json
|   |-- module_audit_baseline.json
|   |-- module_audit_matrix.csv
|   |-- module_audit_matrix.json
|   `-- seed_audit.json
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
|   |-- odoo-check-gate
|   |-- odoo-tests.sh
|   `-- postdeploy-finance.sh
|-- branding
|   `-- fluentui-system-icons
|-- calendar
|   |-- 2026_FinanceClosing_Master.csv
|   `-- FinanceClosing_RecurringTasks.ics
|-- catalog
|   |-- ee_surface
|   |-- alternatives.yaml
|   |-- best_of_breed.yaml
|   |-- equivalence_matrix.csv
|   |-- equivalence_matrix_workos_notion.csv
|   |-- odoo_parity_plans.schema.json
|   |-- odoo_parity_plans.yaml
|   `-- schema.json
|-- catalogs
|   |-- locales
|   `-- sap_concur_surface_catalog.yaml
|-- ccpm
|   |-- .github
|   |-- bin
|   |-- scripts
|   |-- spec
|   |-- src
|   |-- .gitignore
|   |-- package.json
|   `-- tsconfig.json
|-- ci
|   |-- README.md
|   `-- odoo_core_addons_allowlist.txt
|-- claudedocs
|   |-- 100_PERCENT_CLI_DEPLOYMENT.md
|   |-- DEPLOYMENT_SUMMARY.md
|   |-- FINAL_DEPLOYMENT_REPORT.md
|   |-- ISSUE_RESOLUTION_REPORT.md
|   `-- bir-filing-validation-report.md
|-- clients
|   `-- flutter_receipt_ocr
|-- config
|   |-- consumers
|   |-- docflow
|   |-- ee_parity
|   |-- entrypoint.d
|   |-- finance
|   |-- install_sets
|   |-- integrations
|   |-- ipai_ai
|   |-- oca
|   |-- odoo
|   |-- parity
|   |-- sources
|   |-- tokens
|   |-- MAILGUN_INTEGRATION_COMPLETE.md
|   |-- MAILGUN_INTEGRATION_DEPLOYMENT.md
|   |-- PRODUCTION_DEPLOYMENT_SCRIPT.sh
|   |-- README_ADDONS_MANIFEST.md
|   |-- addons_manifest.oca_ipai.json
|   |-- capability_map.yaml
|   |-- extended-platform-install-order.yaml
|   |-- mailgun_integration_implementation.json
|   |-- oca-repos.yaml
|   |-- odoo-core.conf
|   |-- odoo.conf.template
|   |-- pipeline.yaml
|   |-- routing_matrix.yml
|   |-- secrets_inventory.md
|   `-- ship_set.txt
|-- contains-studio-agents
|   |-- design
|   |-- engineering
|   |-- marketing
|   |-- product
|   |-- project-management
|   |-- studio-operations
|   |-- testing
|   `-- README.md
|-- contracts
|   |-- delta
|   `-- lakehouse-executor.openapi.yaml
|-- data
|   |-- filestore
|   |-- finance_seed
|   |-- import_templates
|   |-- sessions
|   |-- templates
|   |-- IMPORT_GUIDE.md
|   |-- bir_calendar_2026.json
|   |-- bir_december_2025_seed.xml
|   |-- employee_directory.json
|   |-- month_end_closing_tasks.csv
|   |-- month_end_tasks.csv
|   |-- notion_tasks_deduplicated.json
|   |-- notion_tasks_parsed.json
|   |-- notion_tasks_with_logframe.json
|   `-- user_map.csv
|-- db
|   |-- audit
|   |-- import-templates
|   |-- migrations
|   |-- process_mining
|   |-- rls
|   |-- schema
|   |-- seeds
|   `-- DB_TARGET_ARCHITECTURE.md
|-- dbt
|   |-- dbt_project.yml
|   |-- packages.yml
|   `-- profiles.yml.example
|-- deploy
|   `-- docflow
|-- design
|   |-- components
|   |-- inputs
|   |-- tokens
|   |-- wireframe
|   |-- README.md
|   |-- schema.tokens.json
|   `-- schema.wireframe.json
|-- dev
|   |-- odoo-addons
|   |-- postgres-init
|   `-- superset
|-- docflow-agentic-finance
|   |-- agents
|   |-- archive
|   |-- artifacts
|   |-- data
|   |-- inbox
|   |-- scripts
|   |-- spec
|   |-- src
|   |-- .env
|   |-- .env.example
|   |-- .env.example.example.example
|   |-- .gitignore
|   |-- README.md
|   |-- docflow-daemon.log
|   |-- docflow-daemon.pid
|   |-- odoo.log
|   |-- odoo.pid
|   |-- pyproject.toml
|   `-- verify_smoke.sh
|-- docs
|   |-- adr
|   |-- agents
|   |-- ai
|   |-- analytics
|   |-- api
|   |-- architecture
|   |-- audits
|   |-- auth
|   |-- brand
|   |-- cicd
|   |-- claude_code
|   |-- competency
|   |-- connectors
|   |-- constitution
|   |-- control
|   |-- curation
|   |-- data-model
|   |-- databricks
|   |-- db
|   |-- deployment
|   |-- deprecated
|   |-- design-system
|   |-- diagrams
|   |-- ee-parity-gate
|   |-- ee_surface
|   |-- evidence
|   |-- github
|   |-- golive
|   |-- governance
|   |-- guides
|   |-- implementation
|   |-- incidents
|   |-- infra
|   |-- integration
|   |-- integrations
|   |-- ipai
|   |-- issues
|   |-- knowledge
|   |-- lakehouse
|   |-- llm
|   |-- llms
|   |-- memory
|   |-- migration
|   |-- module-health
|   |-- modules
|   |-- oca
|   |-- odoo
|   |-- odoo-18-handbook
|   |-- ord
|   |-- pages
|   |-- platform
|   |-- policy
|   |-- portfolio
|   |-- prd
|   |-- process
|   |-- prompts
|   |-- proofs
|   |-- rationalization
|   |-- releases
|   |-- repo
|   |-- reports
|   |-- research
|   |-- runtime
|   |-- security
|   |-- seed-data
|   |-- setup
|   |-- stack
|   |-- state_machines
|   |-- strategy
|   |-- supabase-docs-patterns
|   |-- templates
|   |-- testing
|   |-- troubleshooting
|   |-- tutorials
|   |-- wiki
|   |-- workflows
|   |-- 003-odoo-ce-custom-image-spec.md
|   |-- AGENTIC_CLOUD_PRD.md
|   |-- AGENT_FRAMEWORK_SESSION_REPORT.md
|   |-- AGENT_MEMORY_DEPLOYMENT.md
|   |-- AGENT_TROUBLESHOOTING_PLAYBOOK.md
|   |-- AIUX_SHIP_PRD.md
|   |-- AI_MODULE_NAMING_CONVENTION.md
|   |-- APP_ICONS_README.md
|   |-- AUTOMATED_TROUBLESHOOTING_GUIDE.md
|   |-- BACKLOG_COVERAGE_REPORT.json
|   |-- BACKLOG_COVERAGE_REPORT.md
|   |-- CANONICAL_ENFORCEMENT_REPORT.md
|   |-- CANONICAL_LINT.md
|   |-- CANONICAL_MAP.md
|   |-- CE_OCA_EQUIVALENTS_AUDIT.md
|   |-- CE_OCA_PROJECT_STACK.md
|   |-- CLAUDE_CODE_SETUP.md
|   |-- CODESPACES_SETUP.md
|   |-- CUSTOM_IMAGE_SUCCESS_CRITERIA.md
|   |-- DATABASE_PROMOTION_WORKFLOW.md
|   |-- DATABASE_SETUP.md
|   |-- DB_INIT_RUNBOOK.md
|   |-- DB_TUNING.md
|   |-- DELIVERABLES_MANIFEST.md
|   |-- DEPLOYMENT.md
|   |-- DEPLOYMENT_GUIDE.md
|   |-- DEPLOYMENT_INVARIANTS.md
|   |-- DEPLOYMENT_NAMING_MATRIX.md
|   |-- DEPLOYMENT_SUMMARY.md
|   |-- DEPLOY_NOTION_WORKOS.md
|   |-- DEPRECATED_DOCS.md
|   |-- DEPRECATION_PLAN.md
|   |-- DEVELOPER_TOOLS.md
|   |-- DIGITALOCEAN_EMAIL_SETUP.md
|   |-- DIGITALOCEAN_SMTP_UNBLOCK_REQUEST.md
|   |-- DIGITALOCEAN_VALIDATION_FRAMEWORK.md
|   |-- DIRECTIONAL_SYNC.md
|   |-- DNS_SETTINGS.md
|   |-- DOCKERFILE_COMPARISON.md
|   |-- DOCKER_CANONICAL_DIFF.md
|   |-- DOCKER_CD_MIGRATION_GUIDE.md
|   |-- DOCKER_SIMPLE_EXPLANATION.md
|   |-- DOCKER_SSOT_ARCHITECTURE.md
|   |-- DOCKER_VALIDATION_GUIDE.md
|   |-- DOKS_DEPLOYMENT_SUCCESS_CRITERIA.md
|   |-- DR_RUNBOOK.md
|   |-- ECOSYSTEM_GUIDE.md
|   |-- EE_IAP_TO_OCA_IPAI_MAPPING.md
|   |-- EE_TO_CE_OCA_MAPPING.md
|   |-- EMAIL_AND_OAUTH_SETUP.md
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
|   |-- GANTT_TO_ODOO_CE_MAPPING.md
|   |-- GITHUB_PAT_CODESPACES.md
|   |-- GITHUB_PAT_SCOPES.md
|   |-- GITHUB_SECRETS_SETUP.md
|   |-- GIT_AUTH_PERMANENT_FIX.md
|   |-- GIT_WORKTREE_STRATEGY.md
|   |-- GO_LIVE_CHECKLIST.md
|   |-- GO_LIVE_CHECKLIST_ODOO18_IPAI.md
|   |-- GO_LIVE_PRODUCTION_CHECKLIST.md
|   |-- GO_LIVE_RUNBOOK.md
|   |-- HEADER_CLEANUP_SUMMARY.md
|   |-- HEALTH_CHECK.md
|   |-- IMAGE_GUIDE.md
|   |-- IMPLEMENTATION_SUMMARY.md
|   |-- INDEX.md
|   |-- INDUSTRY_PACKS_OCA_DEPENDENCIES.md
|   |-- INDUSTRY_PARITY_ANALYSIS.md
|   |-- INFRASTRUCTURE_CHECKLIST.md
|   |-- INTEGRATION_BUS_DEPLOYMENT.md
|   |-- IPAI_MODULES_INDEX.md
|   |-- IPAI_MODULE_INSTALLATION_ORDER.md
|   |-- KEYCLOAK_IDENTITY_PROVIDER_DEPLOYMENT.md
|   |-- KUBERNETES_MIGRATION_SPECIFICATION.md
|   |-- LOGIN_BUTTON_FIX.md
|   |-- MAILGUN_DNS_SETUP.md
|   |-- MCP_IMPLEMENTATION_STATUS.md
|   |-- MCP_SUPABASE_INTEGRATION.md
|   |-- MIXED_CONTENT_FIX.md
|   |-- MODULE_CONSOLIDATION_GUIDE.md
|   |-- MODULE_STATUS_FINAL.md
|   |-- MODULE_STATUS_REPORT.md
|   |-- MONOREPO_STRUCTURE.md
|   |-- MVP_GO_LIVE_CHECKLIST.md
|   |-- N8N_CREDENTIALS_BOOTSTRAP.md
|   |-- NAMING_CONVENTION_EQ_APP_TOOLS.md
|   |-- OCA_CHORE_SCOPE.md
|   |-- OCA_INSTALLATION_GUIDE.md
|   |-- OCA_MIGRATION.md
|   |-- OCA_STYLE_CONTRACT.md
|   |-- OCA_TEMPLATE_INTEGRATION.md
|   |-- ODOO18_ENTERPRISE_TO_CE_OCA_MAPPING.md
|   |-- ODOO_18_CE_CHEATSHEET.md
|   |-- ODOO_18_CE_MODULE_INSTALL_ORDER.md
|   |-- ODOO_18_EE_TO_CE_OCA_PARITY.md
|   |-- ODOO_ADDONS_PATH_CONFIGURATION.md
|   |-- ODOO_APPS_CATALOG.md
|   |-- ODOO_ARCHITECT_PERSONA.md
|   |-- ODOO_CE_DEPLOYMENT_SUMMARY.md
|   |-- ODOO_CE_v0.9.0_SECURITY_AUDIT_REPORT.md
|   |-- ODOO_COPILOT_THEME_TOKEN_MAP.md
|   |-- ODOO_EXECUTION.md
|   |-- ODOO_GOLIVE_SETTINGS_INVENTORY.md
|   |-- ODOO_HTTPS_OAUTH_TROUBLESHOOTING.md
|   |-- ODOO_IMAGE_SPEC.md
|   |-- ODOO_MODULE_DEPLOYMENT.md
|   |-- ODOO_PROGRAMMATIC_CONFIG.md
|   |-- OFFICIAL_ALIGNMENT.md
|   |-- OFFICIAL_TYPOLOGY.md
|   |-- OFFLINE_TARBALL_DEPLOYMENT.md
|   |-- PRD_ipai_ppm_portfolio.md
|   |-- PRODUCTION_DATABASE_CHECKLIST.md
|   |-- PRODUCTION_DEFAULTS.md
|   |-- PRODUCTION_DEPLOYMENT_CHECKLIST.md
|   |-- PRODUCTION_HOTFIX.md
|   |-- PROD_READINESS_GAPS.md
|   |-- PROD_SNAPSHOT_MANIFEST.md
|   |-- PROGRAMMATIC_CONFIG_PLAN.md
|   |-- QUICK_REFERENCE_SSO_SETUP.md
|   |-- QUICK_START.md
|   |-- QUICK_START_CONFIGURATION.md
|   |-- RAG_ARCHITECTURE_IMPLEMENTATION_PLAN.md
|   |-- README.md
|   |-- README_MCP_STACK.md
|   |-- RELEASE_NOTES_GO_LIVE.md
|   |-- REPOSITORY_STRUCTURE.md
|   |-- REPO_SNAPSHOT.json
|   |-- REPO_TREE.contract.md
|   |-- REPO_TREE.generated.md
|   |-- SAAS_PARITY_READINESS.md
|   |-- SCHEMA_NAMESPACE_POLICY.md
|   |-- SECRETS_NAMING_AND_STORAGE.md
|   |-- SEED_DATA_ASSESSMENT.md
|   |-- SEMANTIC_VERSIONING_STRATEGY.md
|   |-- SHIP_v1.1.0_SUMMARY.md
|   |-- SITEMAP.md
|   |-- SLUG_POLICY.md
|   |-- SMTP_SETUP_SUMMARY.md
|   |-- SSO_VALIDATION_CHECKLIST.md
|   |-- STAGING.md
|   |-- SUCCESS_CRITERIA.md
|   |-- SUPERSET_INTEGRATION.md
|   |-- SUPERSET_PPM_ANALYTICS_GUIDE.md
|   |-- TAGGING_STRATEGY.md
|   |-- TBWA_THEME_DEPLOYMENT.md
|   |-- TECHNICAL_GUIDE_SUPABASE_INTEGRATION.md
|   |-- TENANT_ARCHITECTURE.md
|   |-- TESTING_ODOO_18.md
|   |-- TRACEABILITY_INDEX.yaml
|   |-- TROUBLESHOOTING.md
|   |-- UI_THEME_CONSOLIDATION_PROPOSAL.md
|   |-- VERIFIED_MEMORY.md
|   |-- WBS_LOGFRAME_MAPPING.md
|   |-- WORKOS_DEPLOYMENT_MANIFEST.md
|   |-- ZOHO_DNS_SETUP.md
|   |-- advanced-animations-guide.md
|   |-- branch-cleanup-analysis.md
|   |-- ee_parity_map.md
|   |-- llms-full.txt
|   |-- llms.txt
|   |-- notion-odoo-substitute-catalog.md
|   |-- oca_project_modules_18.csv
|   |-- odoo-apps-parity.md
|   |-- odoo_core_schema.sql
|   |-- qweb-templates-guide.md
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
|-- figma
|   |-- community
|   |-- connect
|   |-- tokens
|   `-- README.md
|-- frontend-fluent
|   `-- .env.example
|-- handbook
|   |-- compliance
|   |-- finance
|   |-- .gitbook.yaml
|   |-- README.md
|   `-- SUMMARY.md
|-- harness
|   `-- runners
|-- infra
|   |-- ai
|   |-- azure
|   |-- caddy
|   |-- ce
|   |-- ci
|   |-- ci-odoo
|   |-- cloudflare
|   |-- databricks
|   |-- deploy
|   |-- digitalocean
|   |-- dns
|   |-- do-oca-stack
|   |-- docker
|   |-- doctl
|   |-- entrypoint.d
|   |-- lakehouse
|   |-- links
|   |-- mattermost
|   |-- monitoring
|   |-- nginx
|   |-- ops-control
|   |-- platform-kit
|   |-- stack
|   |-- supabase
|   |-- superset
|   |-- terraform
|   |-- .env.example
|   |-- docker-compose.prod.yaml
|   `-- odoo.conf
|-- integrations
|   `-- apps.yml
|-- inventory
|   |-- latest -> runs/20251231T020517Z
|   `-- runs
|-- ipai-platform
|   |-- nginx
|   |-- odoo
|   |-- scripts
|   |-- secrets
|   |-- .env.example
|   |-- README.md
|   |-- compose.prod.override.external-db.yaml
|   |-- compose.prod.yaml
|   `-- compose.yaml
|-- kb
|   |-- audit
|   |-- design_system
|   |-- finance_close
|   `-- parity
|-- lib
|   |-- bin
|   |-- config
|   `-- tests
|-- logs
|   `-- odoo.log
|-- mappings
|-- mattermost
|   |-- runbooks
|   `-- webhook-templates
|-- mcp
|   |-- coordinator
|   |-- local
|   |-- n8n-mcp
|   |-- odoo-mcp
|   |-- servers
|   |-- tools
|   `-- agentic-cloud.yaml
|-- memory
|   |-- packs
|   |-- README.md
|   `-- memory_policy.yaml
|-- n8n
|   |-- workflows
|   `-- n8n_tenant_provisioning.json
|-- notion-n8n-monthly-close
|   |-- scripts
|   |-- src
|   |-- supabase
|   |-- workflows
|   |-- DEPLOYMENT_STATUS.md
|   |-- DEPLOYMENT_SUMMARY.md
|   |-- N8N_CLI_README.md
|   `-- WORKFLOW_CONVENTIONS.md
|-- oca-parity
|   |-- account-analytic
|   |-- account-budgeting
|   |-- account-consolidation
|   |-- account-financial-reporting
|   |-- account-financial-tools
|   |-- account-reconcile
|   |-- collect
|   |-- currency
|   |-- dms
|   |-- evidence
|   |-- helpdesk
|   |-- hr
|   |-- hr-holidays
|   |-- manufacture
|   |-- mis-builder
|   |-- payroll
|   |-- project
|   |-- project-reporting
|   |-- queue
|   |-- sale-workflow
|   |-- server-env
|   |-- server-tools
|   |-- server-ux
|   |-- social
|   |-- timesheet
|   |-- web
|   `-- .keep
|-- ocr-adapter
|   |-- scripts
|   |-- test_receipts
|   |-- .gitignore
|   |-- DEPLOYMENT.md
|   |-- Dockerfile
|   |-- README.md
|   |-- main.py
|   |-- nginx-site.conf
|   |-- requirements.txt
|   `-- test-ocr.sh
|-- ocr_service
|   |-- ocr.log
|   |-- ocr.pid
|   `-- server.py
|-- odoo
|   |-- compose
|   |-- ODOO_INTEGRATION_MAP.md
|   `-- ipai_finance_closing_seed.json
|-- odoo-schema-mirror
|   |-- tests
|   |-- .env.example
|   |-- export_odoo_schema.py
|   |-- generate_dbml.py
|   |-- requirements.txt
|   |-- sync_to_supabase.py
|   `-- validate_parity.py
|-- odoo19
|   |-- backups
|   |-- config
|   |-- docs
|   |-- scripts
|   |-- CANONICAL_SETUP.md
|   |-- MIGRATION_COMPLETE.md
|   |-- MIGRATION_FROM_OLD_STACK.md
|   |-- QUICK_REFERENCE.md
|   `-- compose.yaml
|-- odoo_local
|   |-- compose
|   |-- ODOO_INTEGRATION_MAP.md
|   `-- ipai_finance_closing_seed.json
|-- ops
|   |-- alerting
|   |-- backlog
|   |-- backup
|   |-- compose
|   |-- design
|   |-- github
|   |-- idp
|   |-- jobs
|   |-- observability
|   |-- pipelines
|   |-- runbooks
|   |-- secrets
|   |-- DISASTER_RECOVERY.md
|   `-- backup-production.sh
|-- osi
|   |-- osi_template.json
|   `-- osi_template.yaml
|-- out
|   |-- concur_demo
|   |-- concur_demo_odoo_map
|   |-- copilot_index
|   |-- graphs
|   |-- .gitkeep
|   |-- FLAGSHIP_REPO_RECOMMENDATION.md
|   |-- INTEGRATIONS_OPPORTUNITIES.md
|   |-- STACK_RUNBOOK.md
|   |-- TOP_REPOS.md
|   |-- UPDATED_WORK_RECOMMENDATIONS.md
|   |-- dns_audit.json
|   |-- ee_parity_matrix.md
|   |-- oca_inventory.json
|   |-- oca_inventory.md
|   |-- oca_repos_seed.txt
|   |-- repos_files.jsonl
|   |-- repos_inventory.json
|   |-- repos_names.txt
|   `-- repos_scored.json
|-- parity
|   `-- parity-matrix.yaml
|-- patches
|   `-- ipai_ce_cleaner_xmlid_fix.diff
|-- platform-kit
|   |-- cli
|   |-- docs
|   `-- reports
|-- prompts
|-- prototypes
|   |-- ipai_aiux_chat
|   |-- ipai_fluent_web_365_copilot
|   |-- ipai_theme_aiux
|   `-- README.md
|-- registry
|   |-- features
|   `-- integrations
|-- releasekit
|   |-- fastlane
|   |-- scripts
|   |-- store
|   `-- README.md
|-- reports
|   `-- parity
|-- research
|   |-- dist
|   `-- raw
|-- runtime
|   |-- docker
|   |-- down.sh
|   `-- up.sh
|-- sandbox
|   |-- dev
|   `-- workbench
|-- schemas
|   |-- gate
|   |-- parity
|   |-- feature.schema.json
|   |-- gate_report.schema.json
|   `-- integration.schema.json
|-- scripts
|   |-- aiux
|   |-- audit
|   |-- auth
|   |-- backup
|   |-- bir
|   |-- ci
|   |-- ci_gate
|   |-- codespaces
|   |-- competency
|   |-- db
|   |-- deploy
|   |-- deprecation
|   |-- design
|   |-- dev
|   |-- dns
|   |-- docker
|   |-- docs
|   |-- drive_sync
|   |-- e2e
|   |-- ee_surface
|   |-- figma
|   |-- fixes
|   |-- gates
|   |-- generate
|   |-- github
|   |-- health
|   |-- import
|   |-- infra-discovery
|   |-- integration
|   |-- integrations
|   |-- ipai-view-migration
|   |-- kb
|   |-- lakehouse
|   |-- lib
|   |-- mailgun
|   |-- memory
|   |-- month_close
|   |-- oca
|   |-- ocadev
|   |-- odoo
|   |-- odoo-automation
|   |-- odoo-kit-temp
|   |-- odoo_parity
|   |-- odooops
|   |-- ops
|   |-- parity
|   |-- plane
|   |-- policy
|   |-- ppm
|   |-- prod
|   |-- provisioners
|   |-- sandbox
|   |-- security
|   |-- seeds
|   |-- sql
|   |-- stack
|   |-- status
|   |-- supabase
|   |-- superset
|   |-- sync
|   |-- tests
|   |-- .env.example
|   |-- CONFIG_INVENTORY.txt
|   |-- FIX_OWLERROR_GUIDE.md
|   |-- README.md
|   |-- README_CONFIG_MAIL_AI_OCR.md
|   |-- README_SEED_PROJECTS.md
|   |-- activate-n8n-workflows.sh
|   |-- apply-supabase-schema.sh
|   |-- apply_config.sh
|   |-- assign_module_icons.py
|   |-- audit_email_config.py
|   |-- audit_installed_modules.py
|   |-- audit_ipai_modules.py
|   |-- audit_oca_modules.py
|   |-- auto_error_handler.sh
|   |-- backlog_scan.py
|   |-- backup_odoo.sh
|   |-- backup_verify.sh
|   |-- baseline-validation.sh
|   |-- bootstrap_apps_from_inventory.sh
|   |-- bootstrap_execution_board.sh
|   |-- bootstrap_github_issues.sh
|   |-- build_and_push_version.sh
|   |-- build_v0.10.0.sh
|   |-- build_v0.9.1.sh
|   |-- canonical_audit.py
|   |-- ce_oca_audit.py
|   |-- cf_delete_superset_dns.sh
|   |-- cf_upsert_superset_dns.sh
|   |-- check-enterprise-modules.sh
|   |-- check-generated-tokens.sh
|   |-- check-spec-kit.sh
|   |-- check-supabase-migrations.sh
|   |-- check_addon_allowlist.py
|   |-- check_go_live_manifest.py
|   |-- check_install_set_drift.sh
|   |-- check_module_status.sh
|   |-- check_odoosh_parity.py
|   |-- check_project_tasks.py
|   |-- check_secrets.sh
|   |-- check_undocumented_specs.py
|   |-- ci_local.sh
|   |-- ci_odoo_changed_modules.py
|   |-- ci_odoo_gate.py
|   |-- ci_odoo_resolve_deps.py
|   |-- ci_odoo_resolve_impacted.py
|   |-- ci_odoo_run_install_upgrade.sh
|   |-- ci_smoke_test.sh
|   |-- clean-branches.sh
|   |-- cleanup-branches.sh
|   |-- clone_missing_oca_repos.sh
|   |-- compose_vars.sh
|   |-- config_files_found.txt
|   |-- configure_base_url.py
|   |-- configure_gmail_smtp.py
|   |-- configure_gmail_smtp.sh
|   |-- configure_google_oauth.sh
|   |-- configure_mailgun_smtp.py
|   |-- configure_sendgrid_smtp.py
|   |-- configure_smtp.py
|   |-- configure_zoho_smtp.py
|   |-- convert_csv_to_xml.py
|   |-- convert_seed_to_xml.py
|   |-- copilot_ingest.py
|   |-- count_xml_seeds.py
|   |-- crawl_site.sh
|   |-- create-module-readme.sh
|   |-- create-release.sh
|   |-- create_parity_pr.sh
|   |-- db-cleanup-legacy.sh
|   |-- db_verify.sh
|   |-- delete_user_safe.sh
|   |-- deploy-bir-compliance.sh
|   |-- deploy-december-2025-bir-tasks.sh
|   |-- deploy-mailgun-mailgate.sh
|   |-- deploy-n8n-workflows.sh
|   |-- deploy-odoo-modules.sh
|   |-- deploy-otp-auth.sh
|   |-- deploy-tbwa-theme-tokens.sh
|   |-- deploy-to-server.sh
|   |-- deploy_afc_rag.sh
|   |-- deploy_complete_fix.sh
|   |-- deploy_custom_image.sh
|   |-- deploy_notion_tasks.sh
|   |-- deploy_odoo_smart.sh
|   |-- deploy_odoo_upgrade.sh
|   |-- deploy_parity_schema.sh
|   |-- deploy_prod.sh
|   |-- deploy_production.sh
|   |-- deploy_theme_to_production.sh
|   |-- deploy_vercel_prod.sh
|   |-- deploy_with_credentials.sh
|   |-- deploy_workos_prod.sh
|   |-- deployment-checklist.sh
|   |-- design-sync.sh
|   |-- diagnose_prod.sh
|   |-- diagnose_smtp.sh
|   |-- discover_digitalocean_infra.sh
|   |-- discover_docker_infra.sh
|   |-- discover_odoo_infra.py
|   |-- discover_supabase_infra.py
|   |-- discover_supabase_ui_sources.sh
|   |-- docker-desktop-audit.sh
|   |-- docker-staging-audit.sh
|   |-- docs_refresh.sh
|   |-- down.sh
|   |-- ee_replace_request.sh
|   |-- enhanced_health_check.sh
|   |-- env_vars_found.txt
|   |-- erd_dot.sql
|   |-- erp_config_cli.sh
|   |-- execute_rationalization.sh
|   |-- expense_ocr_ingest.sh
|   |-- export_architecture_diagrams.sh
|   |-- export_todo_seed.py
|   |-- extract_openai_academy_prompt_packs.py
|   |-- extract_remote_data.py
|   |-- figma-export-variables.mjs
|   |-- finance_ppm_health_check.sh
|   |-- finance_ppm_health_check.sql
|   |-- finance_ppm_restore_golden.sh
|   |-- finance_ppm_seed_audit.py
|   |-- fix-finance-ppm-schema.sh
|   |-- fix-pay-invoices-online-error.py
|   |-- fix_oauth_button.sh
|   |-- fix_oauth_button_odoo_core.sh
|   |-- fix_odoo18_views.py
|   |-- fix_permissions.sh
|   |-- fix_pos_enterprise_error.sh
|   |-- force_asset_regeneration.sh
|   |-- full_deploy_sanity.sh
|   |-- gen_addons_path.py
|   |-- gen_install_set.py
|   |-- gen_repo_tree.sh
|   |-- gen_repo_tree_fallback.sh
|   |-- generate_2026_finance_calendar.py
|   |-- generate_2026_schedule.py
|   |-- generate_erd_graphviz.py
|   |-- generate_finance_dashboard.py
|   |-- generate_go_live_checklist.py
|   |-- generate_llm_docs.py
|   |-- generate_module_docs.py
|   |-- generate_module_health_report.py
|   |-- generate_module_signatures.py
|   |-- generate_month_end_imports.py
|   |-- generate_odoo_dbml.py
|   |-- generate_odoo_template.py
|   |-- generate_release_docs.sh
|   |-- generate_repo_index.py
|   |-- generate_schema_artifacts.sh
|   |-- generate_seed_audit_artifact.py
|   |-- generate_seed_xml.py
|   |-- generate_shadow_ddl.py
|   |-- generate_spec_report.py
|   |-- go_live.sh
|   |-- go_no_go_check.sh
|   |-- healthcheck_odoo.sh
|   |-- hotfix_icon_crash.sh
|   |-- hotfix_production.sh
|   |-- html_catalog.py
|   |-- image-diff-report.sh
|   |-- image_audit.sh
|   |-- import_month_end_tasks.py
|   |-- incident_snapshot.sh
|   |-- ingest_docs_to_supabase.py
|   |-- ingest_knowledge_graph.py
|   |-- install-git-hooks.sh
|   |-- install-notion-stack.sh
|   |-- install-odoo-18-modules.sh
|   |-- install_all_ipai_modules.sh
|   |-- install_baseline.sh
|   |-- install_finance_stack.sh
|   |-- install_ipai_finance_ppm.sh
|   |-- install_module_xmlrpc.py
|   |-- install_oauth_module.py
|   |-- install_oca_modules.sh
|   |-- install_oca_parity.sh
|   |-- install_oca_project_modules.sh
|   |-- introspect_project.py
|   |-- inventory_config_keys.sh
|   |-- investigate-erp-domain.sh
|   |-- ipai_ai_seed.sh
|   |-- ipai_full_audit.py
|   |-- ipai_install_upgrade_test.sh
|   |-- ipai_quality_gate.sh
|   |-- lint.sh
|   |-- lint_odoo_entrypoint.sh
|   |-- lock_stage.sh
|   |-- map_logframe.py
|   |-- module_audit_agent.py
|   |-- n8n-gitops.sh
|   |-- new_conversation_entry.sh
|   |-- new_go_live_checklist.sh
|   |-- notify_slack.sh
|   |-- oca-bootstrap.sh
|   |-- oca-sync.sh
|   |-- oca-template-bootstrap.sh
|   |-- oca-update.sh
|   |-- oca_hydrate.sh
|   |-- odoo-18-oca-install.sh
|   |-- odoo.sh
|   |-- odoo_check_ai_ocr_params.py
|   |-- odoo_check_mail.py
|   |-- odoo_coming_soon_install.sh
|   |-- odoo_coming_soon_rollback.sh
|   |-- odoo_coming_soon_verify.sh
|   |-- odoo_config_mail_ai_ocr.py
|   |-- odoo_configure_mail.sh
|   |-- odoo_db_schema_diff.sh
|   |-- odoo_ensure_modules_installed.sh
|   |-- odoo_env_diagnose.sh
|   |-- odoo_import_project_suite.py
|   |-- odoo_install_from_manifests.sh
|   |-- odoo_install_modules.sh
|   |-- odoo_install_oca_must_have.sh
|   |-- odoo_modules_preflight.sh
|   |-- odoo_rationalization.sh
|   |-- odoo_rollback_mail_ai_ocr.py
|   |-- odoo_runtime_snapshot.sh
|   |-- odoo_seed_post_upgrade.sh
|   |-- odoo_seed_projects_and_stages.py
|   |-- odoo_smoke_close.sh
|   |-- odoo_start_fetchmail.py
|   |-- odoo_update_modules.sh
|   |-- odoo_upgrade_modules.sh
|   |-- odoo_verify_from_manifests.py
|   |-- odoo_verify_modules.py
|   |-- odoo_verify_oca_must_have.py
|   |-- package_image_tarball.sh
|   |-- parse_notion_tasks.py
|   |-- plane_bir_bootstrap.sql
|   |-- policy-check.sh
|   |-- pre_install_snapshot.sh
|   |-- prod_access_check.py
|   |-- prod_backup_dump.sh
|   |-- prod_db_guess.py
|   |-- promote.sh
|   |-- promote_oauth_users.py
|   |-- provision_tenant.sh
|   |-- recreate_odoo_prod.sh
|   |-- regen_install_sets.sh
|   |-- release_gate.sh
|   |-- replace_seed_from_excel.py
|   |-- repo_health.sh
|   |-- report_ci_telemetry.sh
|   |-- report_ee_parity.py
|   |-- report_stale_branches.sh
|   |-- rollback_seed_org.sql
|   |-- run_clarity_ppm_reverse.sh
|   |-- run_odoo_migrations.sh
|   |-- run_odoo_shell.sh
|   |-- run_project_introspection.sh
|   |-- scaffold_ipai_parity.py
|   |-- scaffold_ipai_parity.sh
|   |-- scan_ipai_modules.py
|   |-- scan_repos.sh
|   |-- schema_drift_env_check.sh
|   |-- score_repos.py
|   |-- screenshot_production.sh
|   |-- secret-scan.sh
|   |-- seed_companies_users.py
|   |-- seed_finance_close_from_xlsx.py
|   |-- seed_finance_ppm_stages.py
|   |-- seed_projects_from_xlsx.py
|   |-- setup-codespaces-pat.sh
|   |-- setup-codespaces-secrets.sh
|   |-- setup-mailgun-secrets.sh
|   |-- setup_afc_rag.sh
|   |-- setup_config_env.sh
|   |-- setup_credentials.sh
|   |-- setup_keycloak_db.sh
|   |-- simple_deploy.sh
|   |-- skill_web_session_bridge.sh
|   |-- smoke.sh
|   |-- smoke_github_app.sh
|   |-- smoke_import_odoo.sh
|   |-- smoke_odoo_container.sh
|   |-- smoke_test_odoo.sh
|   |-- smoketest.sh
|   |-- spec-kit-enforce.py
|   |-- spec_validate.sh
|   |-- ssh-tunnel-db.sh
|   |-- stack_verify.sh
|   |-- staging_down.sh
|   |-- staging_restore_and_sanitize.sh
|   |-- staging_up.sh
|   |-- start_local_odoo.sh
|   |-- supabase_delete_user.sh
|   |-- supabase_local.sh
|   |-- supabase_schema_diff.sh
|   |-- sync-fluent-tokens.sh
|   |-- sync-tokens.sh
|   |-- sync_agent_memory.py
|   |-- sync_current_state.sh
|   |-- sync_directional.py
|   |-- sync_ipai_sample_metrics_to_supabase.py
|   |-- sync_odoo_shadow.py
|   |-- tenant_automation.py
|   |-- test-mailgun.py
|   |-- test-mailgun.sh
|   |-- test_afc_rag.py
|   |-- test_auth_bootstrap.sh
|   |-- test_deploy_local.sh
|   |-- test_ee_parity.py
|   |-- test_email_flow.sh
|   |-- test_ipai_install_upgrade.py
|   |-- test_magic_link.sh
|   |-- test_mcp_jobs.sh
|   |-- test_theme_locally.sh
|   |-- union_prune_install_sets.py
|   |-- up.sh
|   |-- update_diagram_manifest.py
|   |-- update_task_phase_tags.sh
|   |-- update_tasks_after_import.py
|   |-- upgrade_theme_module.py
|   |-- validate-continue-config.sh
|   |-- validate-openapi.mjs
|   |-- validate-spec-kit.sh
|   |-- validate_ai_naming.py
|   |-- validate_capabilities.sh
|   |-- validate_catalog.mjs
|   |-- validate_ee_iap_independence.sh
|   |-- validate_ee_replacements.py
|   |-- validate_finance_ppm_data.py
|   |-- validate_ipai_doc_module_refs.py
|   |-- validate_json_schema.mjs
|   |-- validate_m1.sh
|   |-- validate_manifest.py
|   |-- validate_manifests.py
|   |-- validate_odoo19_spec.sh
|   |-- validate_odoo_parity_plans.mjs
|   |-- validate_production.sh
|   |-- validate_registries.py
|   |-- validate_repo_config.sh
|   |-- validate_repo_contract.sh
|   |-- validate_repo_layout.sh
|   |-- validate_spec_kit.py
|   |-- validate_spec_kit.sh
|   |-- validate_ssot_excel.py
|   |-- vercel_promote_previous.sh
|   |-- verify-addon-permissions.sh
|   |-- verify-addons-mounts.sh
|   |-- verify-codespaces-auth.sh
|   |-- verify-control-plane.sh
|   |-- verify-dataverse-console.sh
|   |-- verify-dns-baseline.sh
|   |-- verify-dns-enhancements.sh
|   |-- verify-https.sh
|   |-- verify-odoo-18-oca.sh
|   |-- verify-service-health.sh
|   |-- verify.sh
|   |-- verify_auth.sh
|   |-- verify_auth_setup.sh
|   |-- verify_backup.sh
|   |-- verify_cdn.sh
|   |-- verify_email_auth.sh
|   |-- verify_local.sh
|   |-- verify_login_button.sh
|   |-- verify_monitoring.sh
|   |-- verify_oca_ipai_layout.sh
|   |-- verify_phase3.py
|   |-- verify_phase5.sh
|   |-- verify_smtp.py
|   |-- verify_supabase_deploy.sh
|   |-- verify_supabase_full.sh
|   |-- verify_web_assets.sh
|   |-- web_sandbox_verify.sh
|   |-- web_session_init.sh
|   |-- whats_deployed.py
|   |-- whats_deployed.sh
|   |-- wiki_sync.sh
|   |-- worktree-setup.sh
|   |-- write_phase6_verification_summary.py
|   `-- xmlrpc_set_admin_password.py
|-- secrets
|   `-- odoo_pg_pass
|-- security
|   |-- Caddyfile.shell
|   `-- WEB_SHELL_THREAT_MODEL.md
|-- seed_export
|   |-- projects.csv
|   |-- stages.csv
|   |-- tags.csv
|   |-- tasks.csv
|   `-- users.csv
|-- seeds
|   |-- schema
|   |-- scripts
|   |-- shared
|   |-- workstreams
|   `-- README.md
|-- services
|   |-- notion-sync
|   |-- ocr
|   `-- pm_api
|-- skillpack
|   `-- manifest.json
|-- skills
|   |-- bir-tax-filing
|   |-- ci-run-validate
|   |-- expense-processing
|   |-- finance-month-end
|   |-- finance-ppm-health
|   |-- kg-entity-expand
|   |-- odoo
|   |-- odoo-module-audit
|   |-- odoo-module-scaffold
|   |-- odooops
|   |-- superset
|   |-- user
|   |-- visio-drawio-export
|   |-- web-session-command-bridge
|   |-- AGENTS.md
|   |-- README.md
|   |-- architecture_diagrams.skill.json
|   |-- registry.yaml
|   |-- superset_mcp.skill.json
|   `-- visio_drawio_export.skill.json
|-- spec
|   `-- agent
|-- specs
|   |-- 003-ai-enrichment
|   |-- agent-ready-cms
|   |-- docs
|   |-- gates
|   |-- 002-odoo-expense-equipment-mvp.prd.md
|   |-- 003-finance-ppm.prd.md
|   |-- 003-odoo-custom-image.prd.md
|   |-- INSTALL_SEQUENCE.md
|   |-- MODULE_SERVICE_MATRIX.md
|   |-- README.md
|   `-- tasks.md
|-- src
|   |-- lakehouse
|   `-- lakehouse.egg-info
|-- stack
|   `-- odoo19_stack.yaml
|-- supabase
|   |-- .temp
|   |-- functions
|   |-- migrations
|   |-- seed
|   |-- seeds
|   |-- supabase
|   |-- .preview-trigger
|   |-- .supabase-preview-config.json
|   |-- SECURITY_LINTER_REMEDIATION.md
|   |-- config.toml
|   `-- seed.sql
|-- tasks
|   `-- infra
|-- tax
|-- temp-landing-page
|   |-- app
|   |-- components
|   |-- hooks
|   |-- lib
|   |-- public
|   |-- styles
|   |-- .gitignore
|   |-- components.json
|   |-- next.config.mjs
|   |-- package.json
|   |-- postcss.config.mjs
|   |-- tsconfig.json
|   `-- vercel.json
|-- templates
|   |-- module_readme
|   |-- odoo
|   |-- odooops-console
|   `-- saas-landing
|-- tests
|   |-- api
|   |-- e2e
|   |-- load
|   |-- playwright
|   |-- regression
|   `-- sql
|-- tools
|   |-- agent-router
|   |-- audit
|   |-- backlog
|   |-- catalog
|   |-- db-inventory
|   |-- dbml
|   |-- diagramflow
|   |-- docs-crawler
|   |-- docs_catalog
|   |-- graphs
|   |-- ipai_module_gen
|   |-- model-repo-scanner
|   |-- odoo_schema
|   |-- ops-mirror-worker
|   |-- parity
|   |-- pr-gate
|   |-- routing
|   |-- seed_all.ts
|   |-- seed_doc_ocr.ts
|   |-- seed_ppm.ts
|   |-- seed_retail_intel.ts
|   `-- seed_te_cheq.ts
|-- vendor
|   |-- oca
|   |-- odoo
|   |-- oca-sync.sh
|   |-- oca.lock
|   |-- oca.lock.ce19.json
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
|   |-- n8n_scout_sync_webhook.json
|   `-- registry.yaml
|-- .agentignore
|-- .cursorignore
|-- .env
|-- .env.example
|-- .env.example.example.example
|-- .env.example.platform.example.example
|-- .env.example.platform.local.bak.20260210-194203.example.example
|-- .env.example.platform.local.bak.example.example
|-- .env.example.platform.local.bak2.example.example
|-- .env.example.production.example.example
|-- .env.platform.local
|-- .env.platform.local.bak
|-- .env.platform.local.bak.20260210-194203
|-- .env.platform.local.bak2
|-- .env.production
|-- .env.smtp.example
|-- .flake8
|-- .gitignore
|-- .gitmodules
|-- .pre-commit-config.yaml
|-- .python-version
|-- AGENTS.md
|-- ANALYTICS_ACTIVATION_SEQUENCE.md
|-- AUDIT_FIXES_APPLIED.md
|-- AUTO_HEALING_SYSTEM_SUMMARY.md
|-- AUTO_REVIEW_AND_FIX_SUMMARY.md
|-- CHANGELOG.md
|-- CI_CD_AUTOMATION_SUMMARY.md
|-- CI_CD_TROUBLESHOOTING_GUIDE.md
|-- CI_MINIMAL_SET.md
|-- CLAUDE.md
|-- CLAUDE_CODE_WEB.md
|-- CLAUDE_NEW.md
|-- COMPREHENSIVE_DEPLOYMENT_SUMMARY.md
|-- CONTRIBUTING.md
|-- CREDENTIALS_SUMMARY.md
|-- DEPLOYMENT_CHECKLIST.md
|-- DEPLOYMENT_COMPLETE.md
|-- DEPLOYMENT_MVP.md
|-- DEPLOYMENT_REPORT.md
|-- DEPLOYMENT_REPORT_FINAL.md
|-- DEPLOYMENT_RUNBOOK.md
|-- DEPLOYMENT_STATE_CURRENT.md
|-- DEPLOYMENT_STATUS.md
|-- DEPLOYMENT_VALIDATION_REPORT.md
|-- DEPLOYMENT_VERIFICATION.md
|-- DEPLOYMENT_WORKFLOW.md
|-- DEPLOY_ENTERPRISE_BRIDGE_FIX.md
|-- DEPLOY_NOW.md
|-- Dockerfile
|-- Dockerfile.v0.10.0
|-- ERP_CONFIGURATION_SUMMARY.md
|-- EXECUTE_NOW.md
|-- FINANCE_PPM_CANONICAL.md
|-- FINANCE_PPM_CE_DASHBOARD_GUIDE.md
|-- FINANCE_PPM_DASHBOARD_GUIDE.md
|-- FINANCE_PPM_IMPORT_GUIDE.md
|-- HOTFIX_OWLERROR.sh
|-- HOTFIX_SUMMARY.md
|-- IDENTITY_CHATOPS_DEPLOYMENT_SUMMARY.md
|-- INFRASTRUCTURE_PLAN.md
|-- INFRASTRUCTURE_SUMMARY.md
|-- INSIGHTPULSE_ERP_CONFIGURATION_GUIDE.md
|-- KAPA_STYLE_DOCS_ASSISTANT_IMPLEMENTATION.md
|-- LOCAL_SETUP.md
|-- MCP_QUICK_START.md
|-- Makefile
|-- Month-end Closing Task and Tax Filing ext.xlsx
|-- NOVEMBER_2025_CLOSE_TIMELINE.md
|-- NOVEMBER_2025_PPM_GO_LIVE_SUMMARY.md
|-- OCR_PROJECT_COMPLETE.md
|-- ODOO_18_VSCODE_SETUP.md
|-- ODOO_ENV_DIAGNOSTIC.md
|-- ODOO_OCR_SETUP.md
|-- PENDING_TASKS_AUTO_AUDIT.md
|-- POSTGRES_PASSWORD_SOLUTION.md
|-- PRODUCTION_DEPLOY_WORKOS.sh
|-- PROD_DEPLOY.md
|-- README.md
|-- README_BUILD.md
|-- README_PATCH.md
|-- RELEASE_v0.9.0.md
|-- REPORT.md
|-- REPO_RESTRUCTURE_PLAN.md
|-- SAFETY_MECHANISMS.md
|-- SANDBOX.md
|-- SECURITY.md
|-- STRATEGIC_PPM_ANALYTICS_SUMMARY.md
|-- TAG_LABEL_VOCABULARY.md
|-- TBWA_IPAI_MODULE_STANDARD.md
|-- VERIFY.md
|-- VSCODE_CLAUDE_CONFIGURATION_SUMMARY.md
|-- addons.manifest.json
|-- aiux_ship_manifest.yml
|-- bir_deadlines_2026.csv
|-- branch_protection.json
|-- coming-soon.html
|-- constitution.md
|-- custom_module_inventory.md
|-- deploy_m1.sh.template
|-- deploy_ppm_dashboard.sh
|-- deploy_ppm_dashboard_direct.sh
|-- deployment_readiness_assessment.md
|-- devserver.config.json
|-- docker-compose.dev.yml
|-- docker-compose.shell.yml
|-- docker-compose.yml
|-- figma-make-dev.yaml
|-- figma.config.json
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
|-- gemini.md
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
|-- ipai_open_semantics_migrations_and_functions.zip
|-- ipai_theme_tbwa_18.0.1.0.0.zip
|-- llms-full.txt
|-- llms.txt
|-- mkdocs.yml
|-- n8n_automation_strategy.md
|-- n8n_opex_cli.sh
|-- oca-aggregate.yml
|-- oca.lock.json
|-- odoo-bin
|-- odoo-bin.bash-shim.bak
|-- odoo-install-docflow.log
|-- odoo-install-final.log
|-- odoo-install-verbose.log
|-- odoo.log
|-- odoo.pid
|-- package.json
|-- parity_report.html
|-- parity_report.json
|-- parity_report_final.html
|-- parity_report_final_v2.html
|-- ph_holidays_2026.csv
|-- plan.md
|-- pnpm-lock.yaml
|-- pnpm-workspace.yaml
|-- ppm_dashboard_views.xml
|-- pyproject.toml
|-- query_memory.py
|-- requirements-dev.txt
|-- requirements-docs.txt
|-- requirements-oca.txt
|-- requirements.txt
|-- ship_v1_1_0.sh
|-- spec.md
|-- superclaude_bridge.yaml
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
