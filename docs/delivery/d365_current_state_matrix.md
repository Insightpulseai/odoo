# IPAI Current State vs D365 F&O Documentation Ladder

> **Purpose.** Honest status snapshot. Maps IPAI's current Azure estate and repo state to the D365 F&O doc taxonomy, so delivery planning and SoW conversations start from a verifiable position instead of aspirational messaging.
>
> **Companion to:** `d365_fin_ops_surface_and_skills_catalog.md` (skills) and `../benchmarks/d365_finance_copilot_parity_catalog.md` (parity).
>
> **Last updated:** 2026-04-14
> **Status authority:** Azure Resource Graph (subs `eba824fb-…` sponsored + `536d8cf6-…` workload), Insightpulseai/odoo GitHub repo, `ssot/benchmarks/parity_matrix.yaml`.

---

## Canonical status label

Use this sentence anywhere the program state is quoted (proposals, SoWs, specs, boards):

> **Azure-native dev/staging substrate established for Pulser/Odoo, including Odoo runtime, PostgreSQL, Databricks, storage, identities, and observability. Functional finance/project-operations parity, production release posture, and go-live readiness remain in progress.**

One-line version:

> Azure substrate: yes. Functional F&O-equivalent operating system: not yet. Go-live-ready agentic ERP/project-ops platform: not yet.

---

## Plane maturity (current)

| Plane | Status | Evidence | Gap |
|---|---|---|---|
| **Transaction (Odoo+OCA)** | Partial | `ca-ipai-odoo-web-dev`, `ipai-odoo-dev-web` (workload sub, Running), `init-db`, `pg-ipai-odoo-dev`, `pg-ipai-odoo` (PG Flex), `acripaiodoo` (ACR) | No production runtime; functional hydration at ~35-45% EE parity (per CLAUDE.md); OCA modules partially hydrated (consolidation/credit-control/contract not confirmed) |
| **Data intelligence (Databricks+Fabric)** | Partial-strong | `dbw-ipai-dev`, `unity-catalog-access-connector`, `stdevipai`, `stlkipaidev`, Fabric `fcipaidev` (per memory) | No Power BI semantic layer deployed; no curated gold-layer datasets for finance/PPM; no extract-from-Odoo pipeline evidence |
| **Agent (Foundry+MAF)** | Partial | `ipai-copilot-resource` (Foundry, East US 2 per memory `reference_foundry_resource_correction.md`), `ipai-prismalab-gateway` (RAG gateway live), `ipai-bot-proxy-dev`, `ipai-odoo-mcp` | 0 Foundry deployments; Agent 365 prep not live; named Pulser sub-agents (`financial_reconciliation_agent`, `collections_agent`, `expense_agent`) not all built per `parity_matrix.yaml` |
| **Delivery (GitHub+Azure)** | Partial | GitHub `Insightpulseai/odoo`, 12+ workflows, Azure DevOps `insightpulseai/ipai-platform`, spec bundles in `spec/`, doctrine branch ready to push | AI-led SDLC posture documented but not fully wired; `Pulser Release Ops` (per PRD §0.7) not yet built; no preview-env-per-PR; `project_azdo_project_state.md` shows 11/12 pipelines failing |
| **Security & observability** | Baseline | `kv-ipai-dev-sea`, `appi-ipai-dev`, `log-ipai-dev-sea`, `la-ipai-stg`, `id-ipai-dev`, `id-ipai-stg`, `dbmanagedidentity`, `workers-vnet`, `workers-sg` | WAF review evidence not captured; no per-tenant KV scope for future TBWA\SMP; agent governance (approval bands, audit) exists as doctrine, not enforced at runtime |
| **Functional ERP parity** | Early | `ipai_bank_recon` + 14 `ipai_*` modules inventoried; 10 OCA repos present | Per `ssot/benchmarks/parity_matrix.yaml`: ~55-65% Finance parity, ~70% PO parity; P0 gaps are AR/Collections, Services.ProfitabilityCockpit |
| **Go-live readiness** | Early | `GO_LIVE_ACCELERATION_PLAN.md` + `GO_LIVE_RUNBOOK.md` drafted | No cutover rehearsal; no UAT suite runnable in CI; no first-close review evidence; hypercare model drafted not exercised |

---

## D365 F&O doc taxonomy → IPAI status matrix

### A. Platform / implementation lifecycle

| D365 section | IPAI equivalent | Current status | Next gap |
|---|---|---|---|
| **Implementation guide** | `docs/delivery/GO_LIVE_ACCELERATION_PLAN.md`, `docs/tenants/TENANCY_MODEL.md` | **Partial** | Convert to formal implementation playbook per tenant |
| **Cloud deployment (LCS)** | Azure Container Apps (dev+staging), ACR, Bicep modules in `infra/azure/modules/` | **Partial** | Production ACA + AFD not deployed; Key Vault boundary per tenant not defined |
| **Environment mgmt** | `odoo_dev` / `odoo_staging` / `odoo` DB convention per CLAUDE.md; `docs/tenants/TENANCY_MODEL.md` | **Partial** | Env refresh/sanitization policy not written; prod DB doesn't exist |
| **Upgrades/updates/hotfixes** | Odoo + OCA submodule pinning via `.gitmodules` | **Partial** | No formal upgrade playbook; no OCA version lock evidence |
| **Continuous delivery** | GitHub Actions + Azure DevOps per `ssot/governance/platform-authority-split.yaml` | **Partial** | 11/12 AzDO pipelines failing (per memory); release gate not enforced |
| **Prepare for go-live** | `GO_LIVE_RUNBOOK.md` | **Early** | No readiness checklist enforcement; no dress-rehearsal evidence |

### B. Data management

| D365 section | IPAI equivalent | Current status | Next gap |
|---|---|---|---|
| **Data entities** | Odoo models + OCA data entities (via `base_import`) | **Partial** | No canonical entity inventory for migration waves |
| **Data import/export** | `base_import`, Odoo XML-RPC / REST | **Partial** | No standard pathway contract; ad-hoc imports |
| **Database movement** | Odoo DB dump/restore scripts in `scripts/odoo/` | **Baseline** | No masking/sanitization policy; no refresh cadence |
| **Azure Data Lake integration** | ADLS Gen2 (`stlkipaidev`) + Databricks bronze/silver/gold | **Partial-strong** | Extract-from-Odoo pipeline not implemented |

### C. System administration

| D365 section | IPAI equivalent | Current status | Next gap |
|---|---|---|---|
| **User management** | `res.users` + `res.company` per tenant + Entra ID | **Partial** | Cross-tenant whitelist enforcement not validated |
| **Role-based security** | Odoo `res.groups`, `ir.rule` record rules | **Partial** | Multi-company record-rule drift-guard test not written (memory: `feedback_d365_displacement_not_development.md` + `TENANCY_MODEL.md`) |
| **Workflow system** | Odoo workflows + OCA `base_automation` | **Partial** | No cross-tenant workflow library |
| **Organizational hierarchies** | `res.company` + `hr` department tree | **Partial** | No formal hierarchy governance |
| **Number sequences** | Odoo `ir.sequence` | **Full** | — |
| **Batch processing** | Odoo `ir.cron` + `queue_job` (OCA) | **Partial** | `queue_job` hydration not confirmed |
| **Global address book** | `res.partner` | **Full** | — |

### D. Application functional domains

| D365 section | IPAI equivalent | Current status (parity_matrix.yaml) | Next gap |
|---|---|---|---|
| **General ledger** | CE `account` + OCA `account-financial-tools/reporting` | **Partial** | `account-consolidation` not hydrated |
| **Accounts payable** | CE `account,purchase` + OCA `account-invoicing,account-reconcile` + `ipai_invoice_pipeline_bridge` | **Partial** | Invoice capture + 3-way match automation not wired |
| **Accounts receivable: subscription billing** | CE `sale_subscription` + OCA `contract` | **Partial** | `contract` not hydrated |
| **Accounts receivable: collections** | OCA `credit-control` + `ipai_ar_collections_copilot` | **Gap (P0)** | `credit-control` not hydrated, module not built |
| **Budgeting** | CE `account_budget` + OCA `mis-builder` + `ipai_position_forecast` | **Partial** | Position forecasting bridge not built |
| **Cash and bank management** | CE `account` + OCA `account-reconcile` + `ipai_bank_recon` (live) | **Partial** | ML cash flow forecast = P2 |
| **Cost accounting** | CE `account_analytic` + OCA `account-analytic` + `ipai_cost_allocation` | **Gap (P2)** | Cost dimension + overhead allocation not built |
| **Fixed assets** | CE `account_asset` + `ipai_asset_leasing_ifrs16` | **Partial** | IFRS 16 lease workflow not built |
| **Financial reporting** | OCA `mis-builder, reporting-engine, account-financial-reporting` + Fabric + Power BI | **Full** (for existing reports) | Power BI semantic model for Pulser not published |
| **Globalization / PH** | `ipai_bir_*` (6 modules) + Tax Guru PH | **Full (IPAI WIN)** | No D365 equivalent |
| **Project management (ops)** | CE `project` + OCA `project/project-reporting` | **Partial (70%)** | `project_task_wbs` hydration unconfirmed |
| **Resource management** | CE `hr, hr_timesheet` + OCA `hr, timesheet, project` + `ipai_ppm_resource_bookings` | **Partial** | Resource bookings + skills matrix not composed |
| **Project profitability** | CE `project, account` + OCA `mis-builder, account-financial-reporting` + `ipai_ppm_profitability_cockpit` | **Gap (P0)** | Profitability cockpit is the primary services-client differentiator — NOT BUILT |
| **Human resources** | CE `hr` + OCA `hr/*` | **Partial** | Only expense + timesheet wired; core HR not audited |
| **Supply chain (MRP)** | CE `mrp` + OCA `manufacture` | **Early / OUT OF SCOPE unless client** | Don't build speculatively |

### E. Integration & reporting

| D365 section | IPAI equivalent | Current status | Next gap |
|---|---|---|---|
| **Service endpoints (OData)** | Odoo XML-RPC + REST + `ipai-odoo-mcp` (ACA app) | **Partial** | MCP tool catalog not published |
| **Power Platform integration / dual-write** | **OUT OF SCOPE** per doctrine | — | Do not build |
| **Office integration** | M365 Agent SDK via `ipai-bot-proxy-dev` (ACA) + Teams surface | **Partial** | Outlook Copilot channel not wired |
| **Business events** | OCA `queue_job` + webhooks | **Early** | No event bus pattern adopted |
| **Azure Data Lake export** | Databricks + Unity Catalog | **Partial-strong** | Extract-from-Odoo not implemented |
| **Electronic reporting (non-PH)** | `ipai_bir_*` for PH; nothing for EU/US | **P1 assessment pending** | Per `d365_fin_ops_surface_and_skills_catalog.md` gap #8 |
| **Financial reporting / Power BI** | Fabric + Power BI canonical | **Partial-strong** | No published semantic model |

### F. Platform operations

| D365 section | IPAI equivalent | Current status | Next gap |
|---|---|---|---|
| **Task recorder / RSAT** | Odoo tours + Playwright | **Early (P2)** | Regression harness not wired (gap #9 in skills catalog) |
| **Performance tuning** | Odoo profiling + PG tuning + ACA scaling | **Baseline** | No load test / benchmark baseline per `epic-02` S7.3 |
| **Troubleshooting** | Application Insights + Log Analytics | **Baseline** | No canonical runbook per incident class |
| **Business documents / print mgmt** | Odoo QWeb reports + `reporting-engine` | **Full** | — |

---

## Where IPAI is NOT yet on the D365 ladder

1. **Functional application completion** — the domain-by-domain parity matrix shows ~55-70% for the flagship domains; AR/Collections is P0 gap; Profitability Cockpit P0 gap.
2. **Production runtime** — dev + staging only; no `odoo` prod DB; no production AFD routing for prod runtime; no production Key Vault separate from dev.
3. **Cutover / go-live evidence** — runbook exists, rehearsal doesn't. First-close review model not exercised.
4. **Agent governance runtime** — capability matrix (read/recommend/draft/act) + approval bands exist as doctrine in PRD §0.3, not enforced at runtime.
5. **Pulser Release Ops** — §0.7 of PRD locks the adaptation, but the adapted service is not built.
6. **OCA hydration audit** — `consolidation`, `credit-control`, `contract`, `account-analytic`, `field-service`, `edi`, `l10n-*` status uncertain. Gap #5 in skills catalog.
7. **Power BI semantic model** — no published canonical model backing executive dashboards.
8. **Per-tenant onboarding smoke** — tenancy model written, smoke test + record-rule drift guard not wired.

---

## D365 ladder progression — where we go next

Mapped to the 4 backlog epics in `docs/backlog/`:

| D365 ladder rung | Next IPAI milestone | Epic | Horizon |
|---|---|---|---|
| Implementation lifecycle baseline | Run through `epic-01 migration/UAT/go-live` Feature 1 + 2 (migration strategy + data framework) | E1 | P0 |
| Development and administration | Run `epic-02` Features 1 + 2 + 3 (arch, dev tools, Odoo AOT-equivalents) — scaffold via `addons/ipai/_template/` | E2 | P0 |
| Functional parity hardening | Hydrate missing OCA repos (Gap #5); build `ipai_ar_collections_copilot` (Gap #2); build profitability cockpit | parity_matrix | P0 |
| Data foundation completion | Odoo → bronze extract pipeline; gold layer for finance/PPM; Power BI semantic model | E1 + E2 | P1 |
| Prepare for go-live | UAT library (E1 Feature 3); cutover rehearsal (E1 Story 4.2); first-close rehearsal | E1 | P1 |
| Agent governance runtime | Enforce read/recommend/draft/act capability matrix + approval bands; agent-aware go-live (E1 Story 5.2) | E1 + `feedback_four_plane_architecture_doctrine.md` | P1 |
| Production release posture | Production env; Key Vault per tenant; AFD routing for prod; first-client cutover | E3 + E4 | P1 |
| Pulser Release Ops build | Adapt `microsoft/release-manager-assistant` per PRD §0.7; GitHub-first, Odoo-aware | E4 | P2 |

---

## Anchors

- **Parity (domain):** `ssot/benchmarks/parity_matrix.yaml`
- **Parity (narrative):** `../benchmarks/d365_finance_copilot_parity_catalog.md`
- **Skills (delivery team):** `./d365_fin_ops_surface_and_skills_catalog.md`
- **Tenancy:** `../tenants/TENANCY_MODEL.md`
- **PRD doctrine:** `../../spec/pulser-odoo/prd.md` §0
- **CLAUDE.md:** `Odoo extension and customization doctrine`
- **Backlog:** `../backlog/` (4 epics, 80 stories)

## Changelog

- 2026-04-14 Initial honest-status matrix. Next refresh: when any epic feature transitions P0→done, or when OCA hydration audit completes (gap #5).
