# D365 Finance & Operations — Documentation Surface + IPAI Delivery Skills Map

> **Scope.** Reference catalog mapping Microsoft's `fin-ops-core/fin-ops` documentation tree to IPAI's Pulser-for-Odoo displacement program, and from there to the delivery skills IPAI needs in place.
> **Date.** 2026-04-13.
> **Status.** Reference artifact. Not a how-to guide. Extends (does not replace):
> - `docs/benchmarks/d365_finance_copilot_parity_catalog.md` — 12-module Finance parity + PO parity + Copilot agent mapping
> - `ssot/benchmarks/parity_matrix.yaml` — domain-by-domain YAML rows
> - `docs/backlog/epic-0{1..4}.md` — 4 Boards backlog packs
> - `memory/feedback_d365_displacement_not_development.md`
> - `memory/feedback_d365_two_plane_doctrine.md`
> - `memory/feedback_d365_project_operations_services_erp.md`
> - `memory/feedback_odoo_module_selection_doctrine.md`
> - `memory/feedback_four_plane_architecture_doctrine.md`
> - `spec/pulser-odoo/prd.md §0` (four-plane architecture doctrine)

---

## 1. Executive summary

**`fin-ops-core/fin-ops`** is the shared platform+app documentation root for Microsoft's finance-and-operations apps family. It is **not** only Finance. Under this root Microsoft co-locates documentation for:

- **Platform / IT-Pro surface** — `dev-itpro/` sibling tree: Lifecycle Services (LCS), deployment (cloud + on-prem), data management & entities, business events, integration, system administration, upgrades, Regression Suite Automation (RSAT), Office integration, mobile, extensibility, continuous delivery.
- **App-functional surface** — `finance/`, `supply-chain/`, `human-resources/`, and project management accounting (cross-linked into `project-operations/prod-pma/`) sibling trees.
- **Intelligence / reporting surface** — analytics, financial reporting, business documents, electronic reporting, Power BI integration.

For IPAI the practical taxonomy is three concerns:

| Concern | Microsoft label | IPAI disposition |
|---|---|---|
| **Platform / IT-Pro** (LCS, environment mgmt, deployment, data mgmt, RSAT, Office integration) | `fin-ops-core/dev-itpro/*` | **Substituted** by Azure-native platform (ACA, Front Door, Key Vault, Databricks, Fabric, GitHub + Azure DevOps). Benchmark for capability, do not adopt. |
| **App-functional** (GL, AP, AR, Budget, Fixed Assets, Cost, Tax, HR, SCM) | `finance/*`, `supply-chain/*`, `human-resources/*`, `project-operations/prod-pma/*` | **Primary displacement target.** MB-310 + MB-330 functional breadth is what IPAI consultants translate to Odoo CE + OCA + thin `ipai_*`. |
| **Developer / extensibility** (X++, AOT, Chain-of-Command, models, deployable packages) | `fin-ops-core/dev-itpro/extensibility/*`, `dev-itpro/dev-tools/*` | **Explicit non-goal.** `feedback_d365_displacement_not_development.md` locks this. Skip MB-500. |

**In scope for IPAI displacement work:** platform+app functional coverage (for translation), Copilot/agent surface (for parity vs Pulser), and MS Learn MB-310/MB-330 functional cert material.

**Out of scope:** X++/AOT authoring, Dataverse dual-write internals, LCS admin as a delivery activity (benchmark only), on-premises F&O deployment patterns.

---

## 2. Documentation surface map

Tree below merges `fin-ops-core/fin-ops/` (user/functional index) with the sibling `fin-ops-core/dev-itpro/` platform tree. Every row is tagged with (a) IPAI parity target, (b) cert track classification.

### 2.1 Platform / IT-Pro surface (`fin-ops-core/dev-itpro/*`)

| Area | One-liner | IPAI parity target | Cert track |
|---|---|---|---|
| Lifecycle Services (LCS) | Tenant, project, environment, build, deployment, servicing portal | **Out of scope** — substitute: Azure subscription + RG model + Azure DevOps pipelines + GitHub Actions. Benchmark only. See `memory/azure_rg_normalization.md`. | platform ops |
| Cloud deployment | Tier-1/2/3/4 cloud env provisioning via LCS | Azure-native: ACA envs `ipai-odoo-dev-env-v2` + Bicep stamp + Azure DevOps deploy lane | platform ops |
| On-premises deployment | Self-hosted F&O boxes | **Out of scope** — IPAI is Azure-native | platform ops |
| Upgrade / One Version | Cloud-driven feature updates | Odoo 18 CE + OCA submodule pins + `oca-port` CLI; Azure Pipelines `odoo-deploy.yml`. See `agents/skills/oca-module-porter/`. | platform ops |
| Data management (`data-entities/*`) | Data entities, DIXF, import/export, Package API | **CE + OCA + bridge**: Odoo XML-RPC/JSON-RPC + OCA `server-tools/base_import_*` + `ipai_ops_api`. Databricks Bronze/Silver for analytics. | platform ops |
| Database movement operations | Copy prod→sandbox, point-in-time restore, refresh | **Substituted** — Azure Database for PG Flexible Server + pg_dump/pg_restore workflows. See Epic 03 + `memory/project_azure_pg_migration_state.md`. | platform ops |
| Business events | Emit business events to Azure Event Grid / Service Bus | **Parity via** Odoo automated-action → Logic Apps → Service Bus; `ipai_ops_api` emits. Memory: `project_azure_eventing_state.md`. | platform ops |
| Integration (OData, Service endpoints, Power Platform) | Inbound/outbound integration patterns | **Parity via** Odoo JSON-RPC/XML-RPC + M365 Agent SDK bridge (`agent-platform/services/m365-bot-proxy/`) + MCP (`mcp/servers/`). Dual-write = **explicit non-goal**. | platform ops |
| Sysadmin (users, security roles, workflow, number sequences) | Tenant-level admin | **CE native** security + `ir.rule` + `res.groups` + OCA `server-auth/*` + `ipai_auth_oidc` (Entra ID). Workflow = Odoo Studio-free server actions + OCA `base_tier_validation`. | platform ops + MB-310 admin items |
| Office integration (Excel add-in, export to Excel) | Read/write Odoo data from Excel | **Partial substitute** — Power BI + Excel via Fabric mirror (`fcipaidev`); no native "Excel add-in for posting journals." Channel = Slack/Teams/Systray. | platform ops |
| Mobile platform | F&O mobile app + workspace designer | **Substituted** — iOS wrapper `web/mobile/` (docs/skills/ios-native-wrapper.md), Slack, Teams, Odoo web PWA. | platform ops |
| Regression Suite Automation (RSAT) | Task-recorder-driven UAT playback | **CE equivalent**: Odoo `odoo.tests.HttpCase` + Playwright (`mcp/playwright`) + pytest; Epic 01 §UAT. See `.claude/skills/ci-validate.sh`, `agents/skills/odoo-test-authoring/`. | platform ops |
| Performance / troubleshooting | SQL perf, telemetry, LCS traces | **Substituted** — App Insights + Log Analytics + Azure Monitor; `agents/skills/odoo-log-triage/`, `agents/skills/azure-observability-ops/`. | platform ops |
| Dev tools (Visual Studio + X++) | X++ IDE, compiler, CIL generation | **OUT OF SCOPE** — non-goal. IPAI writes Python/XML/OWL in VS Code devcontainer. | **MB-500 — skip** |
| Extensibility (models, Chain-of-Command, deployable packages) | X++ extension model | **OUT OF SCOPE** — non-goal. Odoo extension = `_inherit` on models, OWL JS overrides, QWeb XML overrides. See `.claude/rules/odoo19-coding.md`. | **MB-500 — skip** |
| Continuous delivery | Build/release pipelines in Azure DevOps via LCS | **Substituted** — GitHub Actions CI + Azure DevOps deploy (per `ssot/governance/platform-authority-split.yaml`). Epic 04. | platform ops |

### 2.2 App-functional surface (`fin-ops-core/fin-ops/*` and cross-linked apps)

| Area | One-liner | IPAI parity target | Cert track |
|---|---|---|---|
| Finance → General Ledger | CoA, dimensions, periods, journals | CE `account` + OCA `account-financial-tools/*`, `account-financial-reporting/*`, `account-consolidation` (hydration P1) | MB-310 |
| Finance → Accounts Payable | Vendor master, 3-way match, capture | CE `purchase`+`stock`+`account` + OCA `account-invoicing/*`, `purchase-workflow/*` + Foundry DI pipeline (`project_invoice_pipeline.md`) + `ipai_document_intelligence` | MB-310 |
| Finance → Accounts Receivable | Customer master, billing, subscription, credit, collections, dunning | CE `sale`+`account`+`account_followup` + OCA `contract`, `credit-control` (hydration P1) | MB-310 |
| Finance → Budgeting | Budget planning, control, position forecasting | CE `account_budget` + OCA `mis-builder/mis_builder_budget`; `ipai_position_forecast` bridge P2 | MB-310 |
| Finance → Cash & Bank | Bank master, statement import, reconciliation, cash-flow forecast | CE `account` + OCA `account-reconcile/*` + `ipai_bank_recon` (D365 Financial Reconciliation peer) | MB-310 |
| Finance → Cost accounting | Cost elements, overhead absorption, allocation | CE `analytic` + OCA `account-analytic/*`; **thin vs D365** — P2 `ipai_cost_allocation` | MB-310 |
| Finance → Fixed assets + Asset leasing | Asset master, depreciation books, IFRS 16 leases | CE `account_asset` + OCA `account-financial-tools/account_asset_*`; **IFRS 16 leasing is gap (P1 multinationals)** — `ipai_asset_leasing_ifrs16` | MB-310 |
| Finance → Tax | Tax codes, jurisdictional calc, e-invoicing | **IPAI advantage (PH-deep):** `ipai_ph_tax_config`, `ipai_bir_tax_compliance`, `ipai_bir_returns`, `ipai_bir_2307`, `ipai_bir_2307_automation`, `ipai_bir_slsp`, `ipai_tax_intelligence`, `ipai_tax_review`, TaxPulse-PH-Pack | MB-310 + PH overlay |
| Finance → Expense management | Expense capture, categories, policy, approvals | CE `hr_expense` + `ipai_expense_ops` + `ipai_hr_expense_liquidation` + Foundry DI | MB-310 |
| Finance → Subscription billing | Recurring, milestone, usage-based | CE `sale_subscription` + OCA `contract` | MB-310 |
| Finance → Consolidation & elimination | Multi-entity consolidation | OCA `account-consolidation` (hydration P1) | MB-310 |
| Finance → Public sector | Fund accounting, encumbrances, grants | **P3** — document as known non-parity | MB-310 (public-sector flavor) |
| Finance → Globalization / regional | Country localization layer | PH IPAI-advantage; non-PH P3 | MB-310 + flavor |
| Project management accounting (cross-linked to `project-operations/prod-pma/`) | Project accounting, WBS, rev-rec, project invoicing | Odoo `project`+`sale_timesheet`+`analytic` + OCA `project/*`, `timesheet/*`, `mis_builder_budget`; `ipai_finance_ppm_seed` (ipai_finance_ppm DEPRECATED 2026-04-11) | MB-310 (PMA topics) |
| Human Resources → Personnel, leave, benefits, learning | HR master, absences, benefits, LMS | CE `hr`+`hr_holidays`+`hr_attendance` + OCA `hr/*`. **Not primary IPAI sell.** | **out of scope for MB-310/330** (HR = MB-910 flavor) |
| Human Resources → US payroll | Country payroll engine | **P3** — substitute per-country partner payroll modules | N/A |
| Supply Chain → Product information management (PIM) | Product master, variants, categories | CE `product`+variants + OCA `product-attribute/*` | MB-330 |
| Supply Chain → Inventory management | On-hand, movements, valuation | CE `stock` + OCA `stock-logistics-*/` | MB-330 |
| Supply Chain → Master planning | MPS/MRP | CE `mrp`+`purchase_stock` MRP modules + OCA `manufacture/*` | MB-330 |
| Supply Chain → Procurement & sourcing | PO, vendor scoring, sourcing events | CE `purchase` + OCA `purchase-workflow/*` | MB-330 |
| Supply Chain → Production control | Shop floor, routing, BOM explosion | CE `mrp` + OCA `manufacture/*` | MB-330 |
| Supply Chain → Sales & marketing | CRM-lite, quotes, campaigns | CE `crm`+`sale` + OCA `crm/*` | MB-330 |
| Supply Chain → Transportation management | Load planning, carrier rating, routing | CE + OCA thin; **P3** | MB-330 |
| Supply Chain → Warehouse management (+ WMS mobile app) | Put-away, picking, waves, mobile scanning | CE `stock` WMS + OCA `wms/*` + barcode. Mobile = Odoo Barcode app / OCA. | MB-330 |
| Supply Chain → Asset management | EAM, work orders, preventive | OCA `maintenance/*` | MB-330 (asset mgmt) |
| Intelligence → Analytics & Power BI | Analytical workspaces, BYOD, entity store | **Substituted** — Fabric Mirroring (live, `fcipaidev`) + Databricks Gold marts + Power BI. Memory: `project_fabric_finance_ppm.md`, `project_data_lane_architecture.md`. | platform ops |
| Intelligence → Business documents | Templated PDF/Word outputs | CE QWeb + OCA `reporting-engine/report_xlsx`, `report_py3o` | functional / platform ops |
| Intelligence → Financial reporting (Management Reporter-style) | Row/column P&L, BS, TB | OCA `account-financial-reporting/account_financial_report` + `mis_builder` | MB-310 |
| Intelligence → Electronic reporting (ER) | Declarative regulatory format engine | **Thin substitute** — `ipai_bir_*` per-form Python. No declarative engine outside BIR (P3 for non-PH). | MB-310 (regulatory flavor) |
| Finance insights (ML) | Payment predictions, cash-flow ML, vendor prediction | **Gap.** Target home = Databricks Gold + Foundry agent. P2. | MB-310 preview items |
| Copilot in F&O / Copilot Studio agents | Financial Reconciliation, Collections in Outlook, Supplier Comms, Time & Expense | **Pulser catalog:** `ipai_finance_reconcile_agent`, `pulser_ar_collections`, `ipai_procurement_comms_agent`, `ipai_expense_agent`. Surfaces: `ipai_odoo_copilot` + `ipai_mail_plugin_bridge` + `agent-platform/services/m365-bot-proxy/` | MB-310 + Foundry/Agent cert |

---

## 3. Delivery skills map

**Assumption:** IPAI delivery pods work Odoo-first; D365 F&O familiarity is for **translation and displacement conversations**, not implementation. Every role below requires the operating doctrine (`CLAUDE.md`, `feedback_d365_displacement_not_development.md`, `feedback_four_plane_architecture_doctrine.md`) as baseline.

Columns:
- **Core skills** — what the role must ship.
- **D365 familiarity required** — what F&O concepts they translate FROM (benchmark-level, not implement-level).
- **Odoo / OCA skills required** — primary hands-on surface.
- **MS Learn modules to consume** — cite training paths (not generic "learn D365").
- **Certifications** — target certs. MB-500 is explicitly excluded everywhere.
- **Existing IPAI skill files** — `.claude/skills/*` and `agents/skills/*` reusable content.

### 3.1 Solution Architect

| Dimension | Content |
|---|---|
| Core skills | Displacement strategy, parity-gap framing, four-plane architecture defense, WAF reviews (Azure + GitHub), cross-repo contract authoring |
| D365 familiarity | F&O implementation lifecycle, LCS concepts, One Version policy, Dataverse dual-write *as non-goal rationale*, Copilot agent install modes |
| Odoo/OCA skills | CE module taxonomy, OCA repo topology, `addons/ipai/_template/` gating, custom-module introspection doctrine |
| MS Learn paths | `learn.microsoft.com/training/paths/explore-fin-ops-apps-dynamics-365-capabilities`, `.../architect-dynamics-365-solutions`, `.../implement-dynamics-365-solutions-success-by-design` |
| Certs | MB-310 (pass), MB-330 (familiarity), AZ-305, SC-100 (nice-to-have) |
| Existing IPAI skills | `agents/skills/pulser-d365-migration/`, `agents/skills/caf-adoption-planning/`, `agents/skills/caf-cloud-native-design/`, `agents/skills/saas-deployment-stamp-design/`, `agents/skills/service-matrix-truth/`, `.claude/skills/waf-grounding.md`, `agents/skills/azure-well-architected/`, `agents/skills/github-well-architected/` |

### 3.2 Finance Functional Consultant

| Dimension | Content |
|---|---|
| Core skills | Chart of accounts design, financial dimensions → analytic plans translation, period/close orchestration, AP/AR workflows, bank recon rules, fixed-asset books, BIR compliance authoring |
| D365 familiarity | GL + dimension framework, AP 3-way match, AR credit & collections workflow, Budget planning stages, Asset leasing (IFRS 16), Cost accounting dimensions, Tax calc service |
| Odoo/OCA skills | CE `account`, OCA `account-financial-tools`, `account-financial-reporting`, `account-reconcile`, `account-invoicing`, `credit-control`, `contract`, `mis-builder`; `ipai_finance_close`, `ipai_bank_recon`, `ipai_bir_*` stack |
| MS Learn paths | `training/paths/get-started-finance-dynamics-365-finance`, `.../configure-manage-accounts-payable-dynamics-365-finance`, `.../configure-manage-accounts-receivable-credit-collections-dynamics-365-finance`, `.../configure-manage-cash-bank-management-dynamics-365-finance`, `.../configure-manage-fixed-assets-dynamics-365-finance`, `.../configure-manage-general-ledger-dynamics-365-finance`, `.../configure-manage-tax-dynamics-365-finance` |
| Certs | **MB-310 (required)** |
| Existing IPAI skills | `agents/skills/finance-month-end/SKILL.md`, `agents/skills/bir/`, `agents/skills/bir_tax/`, `agents/skills/bir-tax-filing/`, `agents/skills/expense-processing/`, `agents/skills/tax_advisory_diva.skill.json`, `agents/skills/bir_workflow_diva.skill.json`, `agents/skills/tax_evidence_collection.skill.json` |

### 3.3 Project Services Consultant

| Dimension | Content |
|---|---|
| Core skills | Services delivery setup (opportunity→project→resource→time→invoice), rate cards, T&M + fixed-fee + milestone billing, WBS, revenue recognition patterns, timesheet discipline |
| D365 familiarity | Project Operations "Integrated with ERP" shape (primary benchmark), project price lists, resourcing, forecasts and budgets, WBS, project invoicing |
| Odoo/OCA skills | CE `project`, `sale_timesheet`, `hr_timesheet`, `analytic`; OCA `project/*` (`project_timeline`, `project_task_wbs`, `project_parent`, `project_task_stage_state`, `project_pivot`), `timesheet/*`, `sale-workflow/sale_timesheet_*`, `mis_builder_budget`; `ipai_finance_ppm_seed` |
| MS Learn paths | `training/paths/project-operations-dynamics-365` family, modules under `dynamics-365/project-operations/prod-pma/` (project management accounting reading) |
| Certs | **MB-310 (required — PMA topics)**, optional MB-300 historical |
| Existing IPAI skills | `agents/skills/project_finance/SKILL.md`, `agents/skills/finance-ppm-health/`, `agents/skills/portfolio-manager/`, `agents/skills/product-manager/` |

### 3.4 Odoo Implementation Engineer

| Dimension | Content |
|---|---|
| Core skills | CE module config, OCA adoption, `ipai_*` thin-bridge authoring (with `MODULE_INTROSPECTION.md` + `TECHNICAL_GUIDE.md`), `_inherit` patterns, OWL JS, QWeb, ACL/rules, test authoring |
| D365 familiarity | "What F&O form this replaces" conversational fluency — not X++ |
| Odoo/OCA skills | CE 18 internals, OCA submodule discipline, pre-commit tooling, oca-port for series migrations, devcontainer workflow |
| MS Learn paths | Light — mainly concept-mapping via `fin-ops-core/fin-ops/` doc reads; no MS implementation training for this role |
| Certs | **None required.** (MB-500 explicitly skipped per doctrine.) |
| Existing IPAI skills | `.claude/rules/odoo19-coding.md`, `.claude/rules/oca-governance.md`, `agents/skills/oca-module-porter/`, `agents/skills/oca-development-standards/`, `agents/skills/odoo-module-scaffold/`, `agents/skills/odoo-module-scaffolding/`, `agents/skills/odoo-orm-model-extension/`, `agents/skills/odoo-view-customization/`, `agents/skills/odoo-webclient-owl-extension/`, `agents/skills/odoo-security-acl-rules/`, `agents/skills/odoo-test-authoring/`, `agents/skills/odoo-upgrade-safe-extension/`, `.claude/skills/odoo-oca-governance/`, `addons/ipai/_template/` |

### 3.5 Data Platform Engineer

| Dimension | Content |
|---|---|
| Core skills | Fabric mirroring, Databricks medallion (Bronze→Silver→Gold), Unity Catalog governance, Power BI semantic modeling, Odoo PG replication hygiene |
| D365 familiarity | BYOD, Entity store, ADLS export, Finance analytical workspaces — all **benchmark only** (IPAI uses Fabric mirror, not BYOD) |
| Odoo/OCA skills | Odoo PG schema literacy (for Silver models), `ipai_data_intelligence` surface |
| MS Learn paths | `training/paths/get-started-fabric`, `.../implement-data-lakehouse-microsoft-fabric`, `.../get-started-power-bi`, `.../design-data-model-power-bi`, Databricks Academy (non-MS) + `learn.microsoft.com/training/paths/administer-microsoft-azure-databricks` |
| Certs | **DP-600 (Fabric Analytics Engineer)**, optional DP-700 (Fabric Data Engineer), Databricks Data Engineer Associate |
| Existing IPAI skills | `agents/skills/databricks-mlops-architecture/`, `agents/skills/databricks-compute-jobs-ops/`, `agents/skills/databricks-identity-sql-ops/`, `agents/skills/databricks-model-serving-production-readiness/`, `agents/skills/databricks-pipeline-production-readiness/`, `agents/skills/databricks-agent-production-readiness/`, `agents/skills/azure-pg-ha-dr/` |

### 3.6 AI / Agent Engineer

| Dimension | Content |
|---|---|
| Core skills | Microsoft Agent Framework patterns, Foundry agent authoring (SDK 2.x — `azure-ai-projects>=2.0.0`, MI RBAC, keyless), MCP tool authoring, Pulser skill registration, policy-gated action execution |
| D365 familiarity | Copilot Finance agent catalog (Reconciliation, Collections, Expense, Supplier Comms), Copilot Studio install modes, Copilot-in-Excel/Outlook surfaces |
| Odoo/OCA skills | `ipai_odoo_copilot` systray, `ipai_ai_copilot`, `ipai_ask_ai_azure`, `ipai_mail_plugin_bridge`, `ipai_copilot_actions`, `ipai_enterprise_bridge` |
| MS Learn paths | `training/paths/get-started-ai-agent-development`, `.../build-ai-agents-azure-ai-foundry`, `.../microsoft-agents-sdk`, Agent Framework repo reading (`reference_release_manager_assistant_adoption.md`), Copilot Studio training paths |
| Certs | AI-102 (Azure AI Engineer), optional AI-900 (skip if AI-102) |
| Existing IPAI skills | `agents/skills/agent-framework-core/`, `agents/skills/agent-orchestration-taskbus/`, `agents/skills/agent-pattern-selection/`, `agents/skills/autonomous-agent-fit-assessment/`, `agents/skills/azure-foundry/`, `agents/skills/foundry-agent-runtime-promotion/`, `agents/skills/foundry-mcp-auth-design/`, `agents/skills/foundry-remote-mcp-registration/`, `agents/skills/foundry-model-selection/`, `agents/skills/foundry-model-routing/`, `agents/skills/claude-foundry-runtime-integration/`, `agents/skills/claude-mcp-integration/`, `agents/skills/m365-agents-channel-delivery/`, `agents/skills/copilot-sdk-dev-assistant/`, `agents/skills/pulser/`, `agents/skills/pulser-d365-migration/` |

### 3.7 DevOps / Release Engineer

| Dimension | Content |
|---|---|
| Core skills | Bicep authoring (stamp + modules), Azure DevOps Pipelines YAML, GitHub Actions CI, release gates, Container Apps deploy, Front Door binding, managed identity + Key Vault wiring |
| D365 familiarity | Benchmark only: deployable package → Odoo image immutability + OCA submodule pin. LCS build/release as anti-pattern reference. |
| Odoo/OCA skills | `scripts/odoo_*.sh` wrappers, devcontainer runtime, OCA submodule mgmt, pre-commit gating |
| MS Learn paths | `training/paths/build-applications-with-azure-devops`, `.../implement-ci-with-azure-pipelines`, `.../get-started-with-github-actions`, `.../design-github-enterprise-architecture`, `.../deploy-applications-azure-container-apps` |
| Certs | AZ-400 (DevOps Engineer Expert), GH-200 (GitHub Actions), optional AZ-104 |
| Existing IPAI skills | `.claude/skills/azure-bicep-troubleshooting/`, `.claude/skills/ci-validate.sh`, `agents/skills/ci-cd/`, `agents/skills/devops/`, `agents/skills/aca-app-deployment-patterns/`, `agents/skills/aca-private-networking/`, `agents/skills/azd-secure-default-deployment/`, `agents/skills/azd-environment-bootstrap/`, `agents/skills/azdo-board-ops/`, `agents/skills/azdo-work-item-ops/`, `agents/skills/azdo-project-settings/`, `agents/skills/azdo-board-normalization/`, `agents/skills/azure-cli-safe/`, `agents/skills/github-cli-safe/`, `agents/skills/odoo-ci-optimization/`, `agents/skills/odoo-ci-validation/`, `agents/skills/odoo-github-flow/`, `agents/skills/odoo-deployment/`, `agents/skills/odoo-dev-to-staging-promotion/`, `agents/skills/odoo-staging-to-production-promotion/`, `agents/skills/odoo-release-promotion/` |

### 3.8 QA / UAT Lead

| Dimension | Content |
|---|---|
| Core skills | UAT cycle design, regression automation, cutover rehearsal, test data management, evidence capture |
| D365 familiarity | Regression Suite Automation Tool (RSAT), Task recorder — **benchmark only** |
| Odoo/OCA skills | `odoo.tests.HttpCase`, pytest harness, Playwright for browser flows, disposable `test_<module>` DB discipline |
| MS Learn paths | `training/paths/getting-started-test-environments-finance-operations-apps` (concept benchmark) + generic Azure Test Plans + GitHub/Playwright-native |
| Certs | Optional ISTQB; no Microsoft cert requirement |
| Existing IPAI skills | `agents/skills/odoo-test-authoring/`, `agents/skills/odoo-test-runner-ops/`, `agents/skills/odoo-staging-validation/`, `agents/skills/odoo-dataset-neutralize-populate-ops/`, `agents/skills/odoo-dev-to-staging-promotion/`, `agents/skills/odoo-staging-to-production-promotion/`, `agents/skills/ship-readiness-gate/`, `agents/skills/skill-eval-authoring/`, `.claude/rules/testing.md` |

### 3.9 Security & Governance Lead

| Dimension | Content |
|---|---|
| Core skills | Azure WAF + GitHub WAF reviews, Entra ID posture, Key Vault RBAC, managed identity topology, secrets policy enforcement, policy-gated agent execution |
| D365 familiarity | F&O security roles → Odoo `res.groups` + `ir.rule` mapping; segregation of duties patterns |
| Odoo/OCA skills | OCA `server-auth/*` (OIDC, SAML), `ipai_auth_oidc` (Entra), record rules, multi-company security |
| MS Learn paths | `training/paths/describe-concepts-of-security-compliance-identity`, `.../implement-an-azure-information-protection-solution`, `.../secure-your-cloud-applications-in-azure`, `.../microsoft-sentinel-for-soc-analysts`, `.../azure-well-architected-security`, `.../github-well-architected-security` |
| Certs | SC-100, SC-300, AZ-500 (one of); MS-500 optional |
| Existing IPAI skills | `.claude/rules/secrets-policy.md`, `agents/skills/entra-auth-app-patterns/`, `agents/skills/entra-mcp-server/`, `agents/skills/entra-mfa-ca-hardening/`, `.claude/skills/entra-identity-governance/`, `agents/skills/azure-well-architected/`, `agents/skills/github-well-architected/`, `.claude/skills/waf-grounding.md`, `agents/skills/caf-security-baseline/`, `agents/skills/caf-governance-baseline/`, `agents/skills/saas-governance-devops-incident-design/`, `agents/skills/saas-compliance-design/`, `agents/skills/saas-identity-access-design/` |

---

## 4. Delivery skill-to-epic traceability

Load-bearing = without this role, the epic cannot complete a gate. Listed roles appear if load-bearing for **at least one feature** in that epic.

| Epic | Architect | Finance | Project | Odoo Eng | Data Eng | AI Eng | DevOps | QA | Sec |
|---|---|---|---|---|---|---|---|---|---|
| E1 Migration / UAT / Go-Live | ✅ | ✅ | ✅ (if services deal) | ✅ | ✅ (cutover data) | — | ✅ | ✅ | ✅ |
| E2 Architecture / Dev / Hardening | ✅ | — | — | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| E3 Azure PostgreSQL Foundation | ✅ | — | — | ✅ (consumer side) | ✅ | — | ✅ | ✅ | ✅ |
| E4 Azure Pipelines / GitHub Delivery | ✅ | — | — | ✅ (consumer side) | — | ✅ (agent deploy lanes) | ✅ | ✅ | ✅ |

Cross-reference paths for each epic: `docs/backlog/epic-01-migration-uat-golive.md`, `...epic-02-architecture-dev-hardening.md`, `...epic-03-azure-postgresql-foundation.md`, `...epic-04-azure-pipelines-github.md`.

---

## 5. Skill gap analysis

Baseline inventory read from:
- `.claude/skills/` — 11 skill dirs + 5 standalone `.md` files (Azure/Bicep/Foundry/OCA/Entra/WAF leaning).
- `agents/skills/` — 180+ dirs spanning Azure, Databricks, Foundry, Odoo, SaaS/tenant design, RL training patterns, project-finance / finance / BIR.

Coverage is strong on: Odoo engineering, OCA porting, Foundry/agent runtime, Azure WAF/CAF, Databricks production-readiness, Entra identity, BIR tax. Coverage is thin on: **D365 translation fluency**, cost accounting, IFRS 16 leasing, position forecasting, RSAT-equivalent automation harness, Copilot Finance agent parity decision aids.

**Top-10 gaps (priority-ordered):**

| # | Gap skill | What it produces | Priority | Rationale |
|---|---|---|---|---|
| 1 | `d365-fno-translation-playbook` | Per-F&O-form → Odoo surface → OCA module decision matrix (consultant-facing) | **P0** | Displacement conversations fail without this. `pulser-d365-migration` is a starting seed, not a full playbook. |
| 2 | `ipai-finance-reconciliation-agent-build` | Buildable recipe for wrapping `ipai_bank_recon` as a Pulser/Foundry agent with policy gates | **P0** | Peers Financial Reconciliation (D365 preview); P1 in `reference_d365_agent_parity_matrix.md`. |
| 3 | `copilot-finance-parity-conversation` | Quote/position script distinguishing Plane A (ERP license) from Plane B (Copilot seats) | **P0** | `feedback_d365_two_plane_doctrine.md` insists quoting must be two-plane. |
| 4 | `ipai-ar-collections-copilot-build` | Builds collections_agent: `account_followup` + credit-control + Outlook surface via `ipai_mail_plugin_bridge` | **P0** | `ssot/benchmarks/parity_matrix.yaml` Finance.AR.Collections = status `gap`, priority P0. |
| 5 | `oca-hydration-verify-pack` | Confirms OCA repos (`account-consolidation`, `contract`, `credit-control`, `account-analytic`, `project_task_wbs`) are hydrated in `addons/oca/` per `.claude/rules/ssot-platform.md` §Rule 10 | **P1** | Multiple parity rows blocked on "verify hydration." |
| 6 | `foundry-di-to-odoo-3way-match` | Automated 3-way match wiring: Foundry DI → `ipai_document_intelligence` → `purchase`+`stock`+`account.move` reconciliation | **P1** | Pipeline is live; match wiring is the parity P1. |
| 7 | `ifrs16-asset-leasing-odoo` | Thin `ipai_asset_leasing_ifrs16` bridge spec (ROU asset + liability + unwind) | **P1** | Multinational prospects hard-gate on this. |
| 8 | `electronic-reporting-non-ph-assessment` | Per-jurisdiction go/no-go framework for non-PH e-invoicing/regulatory outputs | **P1** | Globalization Studio is a D365 breadth advantage; IPAI needs a decision lens, not 40 clones. |
| 9 | `rsat-equivalent-regression-harness` | Playwright + Odoo `HttpCase` pattern library for recording and replaying UAT flows | **P2** | `E1` UAT gate needs an RSAT analog; `odoo-test-authoring` is close but not UAT-flow-centric. |
| 10 | `position-forecasting-bridge` | `ipai_position_forecast` spec: headcount × rate × period against `mis_builder_budget` | **P2** | Budgeting parity row in `parity_matrix.yaml` marks this gap. |

(Gap skill names follow the `.claude/skills/<name>/SKILL.md` convention; see `.claude/skills/librarian-indexer/` for skill-authoring process.)

---

## 6. Learning paths to commission

### 6.1 Microsoft Learn — functional (required)

- MB-310 study guide: `aka.ms/mb310-StudyGuide`
- MB-310 modules (all 8 functional areas): General Ledger, AP, AR + Credit & Collections, Cash & Bank, Fixed Assets, Tax, Expense, Budget
- MB-330 study guide: `aka.ms/mb330-StudyGuide`
- MB-330 modules: Product Information Management, Inventory & Asset, SCM processes, WMS + TMS, Master Planning
- Project Operations reading: `learn.microsoft.com/en-us/dynamics365/project-operations/prod-pma/` — project management accounting subtree (functional consultant benchmark for PO "Integrated with ERP" shape)

### 6.2 Azure + Data + AI

- `learn.microsoft.com/training/paths/azure-well-architected-framework`
- `learn.microsoft.com/training/paths/microsoft-cloud-adoption-framework-for-azure`
- `learn.microsoft.com/training/paths/implement-azure-security-compliance`
- `learn.microsoft.com/training/paths/deploy-applications-azure-container-apps`
- `learn.microsoft.com/training/paths/implement-data-lakehouse-microsoft-fabric`
- `learn.microsoft.com/training/paths/administer-microsoft-azure-databricks`
- `learn.microsoft.com/training/paths/get-started-power-bi`
- `learn.microsoft.com/training/paths/build-ai-agents-azure-ai-foundry`
- `learn.microsoft.com/training/paths/microsoft-agents-sdk` (M365 Agents SDK)

### 6.3 GitHub + DevOps

- `learn.microsoft.com/training/paths/github-actions`
- `learn.microsoft.com/training/paths/design-github-enterprise-architecture`
- GitHub Well-Architected Framework (authoritative for `agents/skills/github-well-architected/`)
- `learn.microsoft.com/training/paths/build-applications-with-azure-devops`
- `learn.microsoft.com/training/paths/implement-ci-with-azure-pipelines`

### 6.4 Certifications to commission

| Role count | Cert | Priority |
|---|---|---|
| All Finance consultants | MB-310 | **Required** |
| SCM consultants (if SCM pods form) | MB-330 | **Required** |
| Data Platform | DP-600 | **Required** |
| AI / Agent Eng | AI-102 | **Required** |
| DevOps | AZ-400 | **Required** |
| Security Lead | one of SC-100 / SC-300 / AZ-500 | **Required** |
| Architect | MB-310 + AZ-305 + SC-100 | **Recommended** |

### 6.5 WAF review trainings (recurring)

- Azure WAF self-assessment for every workload: `learn.microsoft.com/assessments/azure-architecture-review/`
- GitHub WAF review: per `agents/skills/github-well-architected/`
- SaaS WAF overlay: per `agents/skills/azure-well-architected/` + `agents/skills/saas-*-design/` cluster

---

## 7. Explicit non-goals

1. **X++ / AOT / Chain-of-Command authoring.** IPAI writes Odoo Python (`models/`), OWL JS (`static/src/js/`), and QWeb XML (`views/`). Do not cross-train engineers on X++ runtime, CIL generation, or deployable package construction. `memory/feedback_d365_displacement_not_development.md` locks this. Per `CLAUDE.md` and `.claude/rules/odoo19-coding.md`, Odoo extension is `_inherit` + override, never fork.

2. **MB-500 Finance & Operations Developer Associate.** Skip entirely. Displaces D365, does not author in D365. Consultants certify MB-310 (+ MB-330 where SCM in scope); engineers do not certify to MB-500.

3. **LCS admin as delivery activity.** LCS concepts are benchmark material only. IPAI deploys via Azure DevOps Pipelines + GitHub Actions against ACA (`ssot/governance/platform-authority-split.yaml`). Do not invest in LCS environment lifecycle, build automation, or servicing training.

4. **Dataverse / dual-write internals.** Explicit non-goal per §3.12 of the parity catalog. Odoo is system-of-record; analytics export uses Fabric Mirroring + Databricks. Do not train engineers on Dataverse tables, virtual entities, or Power Platform Map translations.

5. **F&O on-premises.** Out of scope — IPAI is Azure-native per `CLAUDE.md` deprecations (DigitalOcean, on-prem nginx edge). Benchmark only if a prospect raises sovereignty; substitute = Azure sovereign/private-link ACA.

6. **Excel add-in parity as a product.** Per `memory/feedback_d365_two_plane_doctrine.md`, Copilot-in-Excel is a *channel*, not a product. IPAI substitutes channels: Odoo systray (`ipai_odoo_copilot`), Slack (Pulser), Teams / M365 bridge (`agent-platform/services/m365-bot-proxy/`). Do not build an Excel add-in unless a prospect hard-gates on it.

7. **F&O public-sector functionality.** Fund accounting, appropriations, grants — document as known non-parity (P3). Do not invest delivery learning budget here until a sector deal materializes.

8. **Globalization Studio non-PH breadth.** 40+ locales in D365 Globalization Studio is out of IPAI's near-term scope. PH (BIR) depth is the IPAI advantage; other locales get `l10n_*` + OCA assessments per gap skill #8 above.

---

*Generated 2026-04-13. Extends `docs/benchmarks/d365_finance_copilot_parity_catalog.md` and `ssot/benchmarks/parity_matrix.yaml`. All doctrine references live in `memory/` and `spec/pulser-odoo/prd.md §0`.*
