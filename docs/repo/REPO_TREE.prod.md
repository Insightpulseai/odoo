# Production Repo Tree

Generated: 2025-12-25T16:56:39Z
SHA: f748a4d

## addons/
```
/opt/odoo-ce/addons
├── ipai
│   ├── ipai_advisor
│   ├── ipai_assets
│   ├── ipai_bir_compliance
│   ├── ipai_ce_branding
│   ├── ipai_ce_cleaner
│   ├── ipai_clarity_ppm_parity
│   ├── ipai_close_orchestration
│   ├── ipai_custom_routes
│   ├── ipai_default_home
│   ├── ipai_dev_studio_base
│   ├── ipai_equipment
│   ├── ipai_expense
│   ├── ipai_finance_bir_compliance
│   ├── ipai_finance_month_end
│   ├── ipai_finance_monthly_closing
│   ├── ipai_finance_ppm
│   ├── ipai_finance_ppm_closing
│   ├── ipai_finance_ppm_dashboard
│   ├── ipai_finance_ppm_tdi
│   ├── ipai_finance_project_hybrid
│   ├── ipai_industry_accounting_firm
│   ├── ipai_industry_marketing_agency
│   ├── ipai_master_control
│   ├── ipai_portal_fix
│   ├── ipai_ppm
│   ├── ipai_ppm_a1
│   ├── ipai_ppm_monthly_close
│   ├── ipai_project_program
│   ├── ipai_srm
│   ├── ipai_workspace_core
│   ├── __init__.py
│   └── __manifest__.py
├── ipai_bir_tax_compliance
│   ├── data
│   ├── models
│   ├── security
│   ├── views
│   ├── __init__.py
│   └── __manifest__.py
├── ipai_close_orchestration
│   ├── data
│   ├── models
│   ├── security
│   ├── views
│   ├── __init__.py
│   └── __manifest__.py
├── ipai_crm_pipeline
│   ├── data
│   ├── models
│   ├── security
│   ├── static
│   ├── views
│   ├── __init__.py
│   └── __manifest__.py
├── ipai_finance_ppm_golive
│   ├── data
│   ├── models
│   ├── reports
│   ├── security
│   ├── views
│   ├── __init__.py
│   └── __manifest__.py
├── ipai_month_end
│   ├── data
│   ├── models
│   ├── security
│   ├── views
│   ├── __init__.py
│   └── __manifest__.py
├── ipai_platform_approvals
│   ├── models
│   ├── security
│   ├── views
│   ├── __init__.py
│   └── __manifest__.py
├── ipai_platform_audit
│   ├── models
│   ├── security
│   ├── views
│   ├── __init__.py
│   └── __manifest__.py
├── ipai_platform_permissions
│   ├── models
│   ├── security
│   ├── views
│   ├── __init__.py
│   └── __manifest__.py
├── ipai_platform_theme
│   ├── static
│   ├── views
│   ├── __init__.py
│   └── __manifest__.py
├── ipai_platform_workflow
│   ├── models
│   ├── security
│   ├── views
│   ├── __init__.py
│   └── __manifest__.py
├── ipai_ppm_a1
│   ├── data
│   ├── models
│   ├── security
│   ├── views
│   ├── wizards
│   ├── __init__.py
│   └── __manifest__.py
├── ipai_tbwa_finance
│   ├── data
│   ├── models
│   ├── security
│   ├── views
│   ├── __init__.py
│   └── __manifest__.py
├── ipai_workos_affine
│   ├── __init__.py
│   └── __manifest__.py
├── ipai_workos_blocks
│   ├── models
│   ├── security
│   ├── static
│   ├── views
│   ├── __init__.py
│   └── __manifest__.py
├── ipai_workos_canvas
│   ├── models
│   ├── security
│   ├── static
│   ├── views
│   ├── __init__.py
│   └── __manifest__.py
├── ipai_workos_collab
│   ├── models
│   ├── security
│   ├── views
│   ├── __init__.py
│   └── __manifest__.py
├── ipai_workos_core
│   ├── models
│   ├── security
│   ├── static
│   ├── views
│   ├── __init__.py
│   └── __manifest__.py
├── ipai_workos_db
│   ├── models
│   ├── security
│   ├── static
│   ├── views
│   ├── __init__.py
│   └── __manifest__.py
├── ipai_workos_search
│   ├── models
│   ├── security
│   ├── views
│   ├── __init__.py
│   └── __manifest__.py
├── ipai_workos_templates
│   ├── data
│   ├── models
│   ├── security
│   ├── views
│   ├── __init__.py
│   └── __manifest__.py
├── ipai_workos_views
│   ├── models
│   ├── security
│   ├── static
│   ├── views
│   ├── __init__.py
│   └── __manifest__.py
└── oca
    ├── __init__.py
    ├── __manifest__.py
    ├── manifest.yaml
    └── requirements.txt
```

## deploy/
```
/opt/odoo-ce/deploy
├── k8s
│   ├── namespace.yaml
│   ├── odoo-configmap.yaml
│   ├── odoo-deployment.yaml
│   ├── odoo-ingress.yaml
│   ├── odoo-secrets.yaml
│   ├── odoo-service.yaml
│   ├── postgres-service.yaml
│   └── postgres-statefulset.yaml
├── nginx
│   └── erp.insightpulseai.net.conf
├── README.md
├── docker-compose.prod.v0.10.0.yml
├── docker-compose.prod.v0.9.1.yml
├── docker-compose.prod.yml
├── docker-compose.workos-deploy.yml
├── docker-compose.yml
├── keycloak-integration.yml
├── mattermost-integration.yml
├── monitoring_schema.sql
├── monitoring_views.sql
├── odoo-auto-heal.service
└── odoo.conf
```

## tools/
```
/opt/odoo-ce/tools
├── audit
│   ├── db_truth.sql
│   ├── gen_prod_snapshot.sh
│   ├── gen_repo_tree.sh
│   ├── gen_repo_tree_prod.sh
│   ├── gen_runtime_sitemap.sh
│   ├── gen_snapshot_json.sh
│   ├── http_crawler.py
│   ├── require_audit_artifacts.sh
│   ├── run_audit_bundle.sh
│   ├── snapshot.sh
│   ├── verify_alignment.py
│   ├── verify_expected_paths.sh
│   └── verify_workos_install.sql
├── catalog
│   └── databricks_org_catalog.py
├── db-inventory
│   ├── README.md
│   └── inventory.py
├── docs-crawler
│   ├── README.md
│   ├── api_ask.py
│   ├── config.yaml
│   ├── crawler.py
│   └── requirements.txt
├── docs_catalog
│   ├── README.md
│   ├── crawl_docs.py
│   ├── map_to_odoo.py
│   └── odoo_map.yaml
├── parity
│   ├── parity_audit.py
│   └── validate_spec_kit.py
├── seed_all.ts
├── seed_doc_ocr.ts
├── seed_ppm.ts
├── seed_retail_intel.ts
└── seed_te_cheq.ts
```

## catalog/
```
/opt/odoo-ce/catalog
├── best_of_breed.yaml
├── equivalence_matrix.csv
└── equivalence_matrix_workos_notion.csv
```

## spec/
```
/opt/odoo-ce/spec
├── adk-control-room
│   ├── constitution.md
│   ├── plan.md
│   ├── prd.md
│   └── tasks.md
├── bir-tax-compliance
│   ├── constitution.md
│   ├── plan.md
│   ├── prd.md
│   └── tasks.md
├── close-orchestration
│   ├── constitution.md
│   ├── plan.md
│   ├── prd.md
│   └── tasks.md
├── continue-plus
│   ├── ALL_GREEN_CRITERIA.md
│   ├── EVALUATION_REPORT.md
│   ├── RUNBOOK.md
│   ├── constitution.md
│   ├── plan.md
│   ├── prd.md
│   └── tasks.md
├── control-room-api
│   ├── constitution.md
│   ├── plan.md
│   ├── prd.md
│   └── tasks.md
├── docs-platform-sapgrade
│   ├── api-contract.yaml
│   ├── constitution.md
│   ├── plan.md
│   ├── prd.md
│   └── tasks.md
├── erp-saas-clone-suite
│   ├── constitution.md
│   ├── plan.md
│   ├── prd.md
│   └── tasks.md
├── expense-automation
│   ├── constitution.md
│   ├── plan.md
│   ├── prd.md
│   └── tasks.md
├── hire-to-retire
│   ├── constitution.md
│   ├── plan.md
│   ├── prd.md
│   └── tasks.md
├── insightpulse-mobile
│   ├── constitution.md
│   ├── plan.md
│   ├── prd.md
│   └── tasks.md
├── ipai-control-center
│   ├── constitution.md
│   ├── plan.md
│   ├── prd.md
│   └── tasks.md
├── ipai-month-end
│   ├── constitution.md
│   ├── plan.md
│   ├── prd.md
│   └── tasks.md
├── ipai-tbwa-finance
│   ├── constitution.md
│   ├── plan.md
│   ├── prd.md
│   └── tasks.md
├── knowledge-hub
│   ├── constitution.md
│   ├── plan.md
│   ├── prd.md
│   └── tasks.md
├── notion-finance-ppm-control-room
│   ├── constitution.md
│   ├── plan.md
│   ├── prd.md
│   └── tasks.md
├── odoo-apps-inventory
│   ├── constitution.md
│   ├── plan.md
│   ├── prd.md
│   └── tasks.md
├── parallel-control-planes
│   ├── constitution.md
│   ├── plan.md
│   ├── prd.md
│   └── tasks.md
├── pulser-master-control
│   ├── capability-registry.yaml
│   ├── constitution.md
│   ├── plan.md
│   ├── prd.md
│   └── tasks.md
├── seed-bundle
│   ├── constitution.md
│   ├── plan.md
│   ├── prd.md
│   └── tasks.md
├── workos-notion-clone
│   ├── constitution.md
│   ├── plan.md
│   ├── prd.md
│   └── tasks.md
├── constitution.md
├── plan.md
├── prd.md
└── tasks.md
```

## kb/
```
/opt/odoo-ce/kb
├── audit
│   └── AGENT_AUDIT_RULES.md
├── design_system
│   └── tokens.yaml
└── parity
    ├── baseline.json
    └── rubric.json
```

## docs/
```
/opt/odoo-ce/docs
├── adr
│   └── ADR-0001-clone-not-integrate.md
├── architecture
│   ├── INSIGHTPULSEAI_TECHNICAL_ARCHITECTURE.md
│   ├── README.md
│   ├── ipai_idp_architecture.drawio
│   ├── ipai_idp_build_deploy_custom_models.drawio
│   ├── ipai_idp_multi_agent_workflow.drawio
│   └── ipai_idp_pdf_processing.drawio
├── db
│   ├── DB_CONVENTIONS_AND_NAMING.md
│   ├── DB_CURRENT_INVENTORY.md
│   ├── DB_DOMAIN_TABLE_SPECS.md
│   ├── DB_ODOO_MAPPING.md
│   ├── DB_REORG_MIGRATION_PLAN.md
│   ├── DB_RLS_POLICY_TEMPLATES.md
│   ├── DB_TABLE_CLASSIFICATION_DRAFT.md
│   └── DB_TARGET_ARCHITECTURE.md
├── deployment
│   ├── CLAUDE_CODE_CLI_PROMPT.md
│   ├── DEPLOYMENT_EXECUTION_GUIDE.md
│   ├── DEPLOYMENT_VERIFICATION_MATRIX.md
│   ├── OCA_CI_GUARDIAN.md
│   ├── PRE_FLIGHT_CHECKLIST.md
│   ├── README.md
│   └── WORKOS_DEPLOYMENT_PACKAGE.md
├── diagrams
│   └── architecture
├── finance-ppm
│   └── OCA_INSTALLATION_GUIDE.md
├── odoo-18-handbook
│   ├── pages
│   ├── spec
│   ├── ODOO_18_CE_OCA_HANDBOOK.md
│   └── README.md
├── ppm
│   ├── architecture.md
│   ├── data-dictionary.md
│   └── runbook.md
├── repo
│   ├── GIT_STATE.prod.txt
│   ├── REPO_SNAPSHOT.prod.json
│   ├── REPO_TREE.prod.md
│   └── WORKOS_REPO_TREE.prod.md
├── runtime
│   ├── ADDONS_PATH.prod.txt
│   ├── CONTAINER_PATH_CHECK.prod.txt
│   ├── HTTP_SITEMAP.prod.json
│   ├── MODULE_STATES.prod.csv
│   ├── ODOO_MENU_SITEMAP.prod.json
│   ├── ODOO_MODEL_SNAPSHOT.prod.json
│   ├── WORKOS_MODELS.prod.json
│   └── WORKOS_MODULES.prod.csv
├── workflows
│   └── hire-to-retire-bpmn.html
├── 003-odoo-ce-custom-image-spec.md
├── AGENTIC_CLOUD_PRD.md
├── AGENT_FRAMEWORK_SESSION_REPORT.md
├── APP_ICONS_README.md
├── AUTOMATED_TROUBLESHOOTING_GUIDE.md
├── CUSTOM_IMAGE_SUCCESS_CRITERIA.md
├── DB_TUNING.md
├── DELIVERABLES_MANIFEST.md
├── DEPLOYMENT.md
├── DEPLOYMENT_GUIDE.md
├── DEPLOYMENT_NAMING_MATRIX.md
├── DEPLOY_NOTION_WORKOS.md
├── DIGITALOCEAN_VALIDATION_FRAMEWORK.md
├── DOCKERFILE_COMPARISON.md
├── DOCKER_CD_MIGRATION_GUIDE.md
├── DOCKER_VALIDATION_GUIDE.md
├── DOKS_DEPLOYMENT_SUCCESS_CRITERIA.md
├── ECOSYSTEM_GUIDE.md
├── ENTERPRISE_FEATURE_GAP.yaml
├── EXECUTIVE_SUMMARY.md
├── FEATURE_CHEQROOM_PARITY.md
├── FEATURE_CONCUR_PARITY.md
├── FEATURE_WORKSPACE_PARITY.md
├── FINAL_DEPLOYMENT_GUIDE.md
├── FINAL_OPERABILITY_CHECKLIST.md
├── FINAL_READINESS_CHECK.md
├── FINANCE_PPM_IMPLEMENTATION.md
├── GITHUB_SECRETS_SETUP.md
├── GIT_WORKTREE_STRATEGY.md
├── GO_LIVE_CHECKLIST.md
├── HEALTH_CHECK.md
├── IMAGE_GUIDE.md
├── IMPLEMENTATION_SUMMARY.md
├── INDUSTRY_PACKS_OCA_DEPENDENCIES.md
├── INDUSTRY_PARITY_ANALYSIS.md
├── KEYCLOAK_IDENTITY_PROVIDER_DEPLOYMENT.md
├── KUBERNETES_MIGRATION_SPECIFICATION.md
├── MATTERMOST_ALERTING_SETUP.md
├── MATTERMOST_CHATOPS_DEPLOYMENT.md
├── MCP_IMPLEMENTATION_STATUS.md
├── MIXED_CONTENT_FIX.md
├── MVP_GO_LIVE_CHECKLIST.md
├── N8N_CREDENTIALS_BOOTSTRAP.md
├── OCA_MIGRATION.md
├── ODOO18_ENTERPRISE_TO_CE_OCA_MAPPING.md
├── ODOO_18_CE_CHEATSHEET.md
├── ODOO_18_EE_TO_CE_OCA_PARITY.md
├── ODOO_APPS_CATALOG.md
├── ODOO_ARCHITECT_PERSONA.md
├── ODOO_CE_DEPLOYMENT_SUMMARY.md
├── ODOO_CE_v0.9.0_SECURITY_AUDIT_REPORT.md
├── ODOO_HTTPS_OAUTH_TROUBLESHOOTING.md
├── ODOO_IMAGE_SPEC.md
├── ODOO_MODULE_DEPLOYMENT.md
├── OFFLINE_TARBALL_DEPLOYMENT.md
├── PRD_ipai_ppm_portfolio.md
├── PROD_READINESS_GAPS.md
├── PROD_SNAPSHOT_MANIFEST.md
├── QUICK_REFERENCE_SSO_SETUP.md
├── RAG_ARCHITECTURE_IMPLEMENTATION_PLAN.md
├── README.md
├── README_MCP_STACK.md
├── REPO_SNAPSHOT.json
├── REPO_TREE.contract.md
├── REPO_TREE.generated.md
├── SAAS_PARITY_READINESS.md
├── SECRETS_NAMING_AND_STORAGE.md
├── SEMANTIC_VERSIONING_STRATEGY.md
├── SITEMAP.md
├── SSO_VALIDATION_CHECKLIST.md
├── SUPERSET_PPM_ANALYTICS_GUIDE.md
├── TAGGING_STRATEGY.md
├── TESTING_ODOO_18.md
├── WBS_LOGFRAME_MAPPING.md
├── WORKOS_DEPLOYMENT_MANIFEST.md
├── branch-cleanup-analysis.md
├── odoo-apps-parity.md
├── supabase-integration.md
└── v0.9.1_DEPLOYMENT_GUIDE.md
```

## .github/
```
/opt/odoo-ce/.github
├── workflows
│   ├── agent-preflight.yml
│   ├── all-green-gates.yml
│   ├── audit-contract.yml
│   ├── auto-sitemap-tree.yml
│   ├── build-seeded-image.yml
│   ├── build-unified-image.yml
│   ├── ci-odoo-ce.yml
│   ├── ci-odoo-oca.yml
│   ├── control-room-ci.yml
│   ├── databricks-dab-ci.yml
│   ├── deploy-finance-ppm.yml
│   ├── deploy-ipai-control-center-docs.yml
│   ├── deploy-production.yml
│   ├── diagrams-qa.yml
│   ├── docs-crawler-cron.yml
│   ├── health-check.yml
│   ├── infra-validate.yml
│   ├── lakehouse-smoke.yml
│   ├── notion-sync-ci.yml
│   ├── production-ready.yml
│   ├── repo-structure.yml
│   ├── seeds-validate.yml
│   ├── spec-and-parity.yml
│   ├── spec-kit-enforce.yml
│   ├── spec-validate.yml
│   ├── superset-bump.yml
│   ├── sync-master.yml
│   └── verify-gates.yml
└── copilot-instructions.md
```

## IPAI Modules
```
ipai_bir_tax_compliance
ipai_close_orchestration
ipai_crm_pipeline
ipai_finance_ppm_golive
ipai_month_end
ipai_platform_approvals
ipai_platform_audit
ipai_platform_permissions
ipai_platform_theme
ipai_platform_workflow
ipai_ppm_a1
ipai_tbwa_finance
ipai_workos_affine
ipai_workos_blocks
ipai_workos_canvas
ipai_workos_collab
ipai_workos_core
ipai_workos_db
ipai_workos_search
ipai_workos_templates
ipai_workos_views
```
