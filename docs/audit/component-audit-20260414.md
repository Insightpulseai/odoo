# IPAI Comprehensive Component Audit — 2026-04-14

**Scope:** Every canonical component plane at state-of-day. Live queries against Azure Resource Graph, Entra, ADO Boards, GitHub, local repo.

**Baseline:** D365 Finance parity Wave-01 in flight (R1 week 0); 3 decision gates active (Apr 27 / Jun 15 / Aug 11); R4 GA target 2026-12-15.

---

## 1. Azure Resource Plane — 30 resources in `eba824fb-332d-4623-9dfb-2c9f7ee83f4e`

| Type | Count | Notes |
|---|---|---|
| `storage/storageaccounts` | 4 | ADLS + app storage |
| `managedidentity/userassignedidentities` | 3 | runtime, build, agent |
| `operationalinsights/workspaces` | 2 | dev + stg |
| **`insights/actiongroups`** | **2** | ✅ NEW today (`ag-ipai-dev-sea`) |
| `app/managedenvironments` | 2 | dev ACA env v1 + v2 |
| `app/containerapps` | 2 | `ipai-copilot-gateway`, `ipai-prismalab-gateway` |
| `servicebus/namespaces` | 1 | — |
| **`search/searchservices`** | **1** | ✅ NEW today (`srch-ipai-dev-sea`) |
| **`purview/accounts`** | **1** | ✅ NEW today (`pv-ipai-dev-sea`) |
| `network/virtualnetworks` | 1 | `vnet-ipai-dev-sea` |
| `network/networksecuritygroups` | 1 | — |
| `keyvault/vaults` | 1 | `kv-ipai-dev-sea` |
| `insights/components` | 1 | App Insights |
| `eventhub/namespaces` | 1 | Purview-managed |
| `dbforpostgresql/flexibleservers` | 1 | `pg-ipai-odoo` (GP) |
| `databricks/workspaces` | 1 | `dbw-ipai-dev` |
| `databricks/accessconnectors` | 1 | MI for Databricks |
| `containerregistry/registries` | 1 | `acripaidev` |
| `app/jobs` | 1 | `ipai-build-agent` |
| `app/managedenvironments/managedcertificates` | 1 | — |
| `network/networkwatchers` | 1 | — |

**Gap vs R3 target (62):** +32 needed. Next tranche: T4 private DNS (8) + T5 private endpoints (8) + T6 extra Log Analytics/DCR (4) = path to 51. Remaining 11 at R3 W8-W9 (Front Door Premium, ACA internal, KV replicas, backup vaults).

---

## 2. Entra Identity Plane

### 2.1 App Registrations — 21 total

| Category | App | Status | Risk |
|---|---|---|---|
| 🔴 **Deprecated** | `ipai-n8n-entra` | active | **DELETE** — n8n fully deprecated 2026-04-07 |
| ⚠️ **Audit** | `Diva Goals API`, `Diva Goals Web` | active | non-canonical; verify purpose |
| ⚠️ **Audit** | `InsightPulse AI - Tableau Cloud`, `ipai-tableau-sso` | active | Tableau not in canonical stack |
| ✅ IPAI-owned | `IPAI Platform Admin CLI` | active | internal tooling |
| ✅ IPAI-owned | `InsightPulseAI Azure DevOps Automation` | active | service principal for ADO |
| ✅ IPAI-owned | `ipai-github-oidc` | active | OIDC federation (GHA removed — re-scope to Azure Pipelines) |
| ✅ IPAI-owned | `ipai-copilot-gateway` | active | ACA runtime |
| ✅ IPAI-owned | `IPAI PG MCP Server` | active | MCP server for PG |
| ✅ IPAI-owned | `InsightPulseAI Odoo Login` | active | Odoo SSO (old) |
| ✅ IPAI-owned | `InsightPulse AI - Odoo Login` | active | Odoo SSO (new) — consolidate? |
| ✅ IPAI-owned | `InsightPulse AI - Odoo ERP` | active | Odoo API app |
| ✅ IPAI-owned | `ipai-copilot-resource-...-AgentIdentityBlueprint` | active | Foundry agent blueprint |
| 🆕 Teams apps | `ipai-ap-invoice-teams-dev` | active | #528 (AP/AR) Teams surface |
| 🆕 Teams apps | `ipai-doc-intel-teams-dev` | active | Document Intelligence Teams |
| 🆕 Teams apps | `ipai-tax-guru-teams-dev` | active | TaxPulse Teams |
| 🆕 Teams apps | `ipai-finance-close-teams-dev` | active | #615 close cycle |
| 🆕 Teams apps | `ipai-pulser-teams-dev` | active | Pulser main Teams |
| 🆕 Teams apps | `ipai-bank-recon-teams-dev` | active | #532 bank recon |
| ✅ Federated | `GitHub Enterprise Cloud SAML SSO` | cert 3/30/2028 | only app with cert tracked |
| ✅ 3rd party | `Zoho`, `Zoho Mail Admin` | active | canonical (SMTP) |

### 2.2 Enterprise Applications — 11 total (from earlier screenshot)
- 1 Unmanaged (no owner)
- 0 Conditional Access policies
- 0 Access reviews
- 0 Sign-in log exports
- Only 1 of 11 tracks cert expiry

### 2.3 Agent Identities (Preview) — 2
- 1 Active, 1 Unmanaged
- 1 Blueprint: `ipai-copilot-resource-...-AgentIdentityBlueprint`
- 0 Custom collections

### 2.4 Missing registrations (gap)
`release-manager-aca`, `m365-bot-proxy`, `odoo-mcp-server`, `foundry-agents-sp` (both), `azure-devops-service-connection` (MI-based), `pulser-orchestrator`.

**SSOT to create:** `ssot/identity/entra-registry.yaml` — doesn't exist.

---

## 3. Odoo Module Plane — 56 IPAI + 28 OCA

### 3.1 Finance parity modules (D365 Finance surfaces)
| Module | Status | D365 feature | ADO |
|---|---|---|---|
| `ipai_finance_gl` | ✅ shipped | GL + financial foundation | #527 Done |
| `ipai_finance_close` | ✅ existing | Period close cycle | #615 |
| `ipai_finance_ppm` | ✅ existing | OKR portfolio mgmt | #536 (PO) |
| `ipai_ar_collections` | 🟡 scaffolded today | Collections | #533 |
| `ipai_expense_ops` | ✅ existing | Expense mgmt | #529 |
| `ipai_bank_recon` | ✅ existing | Bank recon (paired with recon_agent) | #532 |
| **`ipai_finance_ap_ar`** | 🆕 **scaffolded this session** (21 files) | AP/AR parity | #528 |
| **`ipai_finance_fpa`** | 🔄 in flight | FP&A + Copilot | #614 |
| **`ipai_finance_cash`** | 🔄 in flight | Cash mgmt + forecasting | #529 + #616 |
| **`ipai_finance_tax`** | 🔄 in flight | Tax management (unified) | Epic #6 |

### 3.2 BIR/Tax modules
`ipai_bir_2307`, `ipai_bir_2307_automation`, `ipai_bir_compliance`, `ipai_bir_returns`, `ipai_bir_slsp`, `ipai_bir_tax_compliance` — 6 modules; eBIRForms/eFPS/ePAY in motion; eAFS gate 2026-08-11.

### 3.3 Copilot/AI modules
`ipai_odoo_copilot` (shipped w/ Claude Sonnet + multi-turn), `ipai_ai_copilot`, `ipai_ai_platform`, `ipai_copilot_actions`, `ipai_ai_channel_actions`, `ipai_ask_ai_azure`, `ipai_document_intelligence`, `ipai_document_extraction`, `ipai_data_intelligence`, `ipai_ai_widget` (DEPRECATED per CLAUDE.md — global patches replaced by native Odoo 18 Ask AI).

### 3.4 Integration modules
`ipai_aca_proxy`, `ipai_agent`, `ipai_auth_oidc`, `ipai_enterprise_bridge`.

### 3.5 Branch/Tenant modules
`ipai_branch_profile`.

### 3.6 Compliance modules
`ipai_compliance_approval`, `ipai_compliance_evidence`, `ipai_compliance_graph`.

### 3.7 OCA Baseline — 28 repos hydrated
Need to verify list matches `ssot/odoo/oca-baseline.yaml`.

---

## 4. ADO Boards — Execution plane

| Category | Count | State |
|---|---|---|
| **Epics open** | 37 | 5 Doing / 32 To Do |
| **Wave-01 Issues active** | 30+ | 3 shipped but mis-stated (cleanup today) |
| **Iterations** | 5 | R1 Foundation (active), R2, R3, R4, Backlog |
| **Canonical path** | `ipai-platform\R1-Foundation-30d` | confirmed 2026-04-14 |

### 4.1 Wave-01 Benchmark Epics (the 3 bundles)
- #523 D365 Finance Parity — 8 active Issues under (5 orig + 3 added today)
- #524 Finance Agents Parity — 5 active (1 done #532 v0)
- #525 D365 Project Operations Parity — 7 active (4 orig + 3 added today)

### 4.2 PH Pack Epics (gated for R2+ execution)
#373–#383 + #480 — 11 Epics, all To Do, execution starts post-R2 Finance proof.

### 4.3 OBJ Epics (legacy baseline)
#1 Identity (Doing), #2 ERP Parity (Doing), #3 Foundry Runtime (Doing), #4 Data OLTP/OLAP, #5 DevEx, #6 Security/Compliance/BIR, #7 Revenue (Doing).

### 4.4 Hardening/Proving/Codifying (hardening bundle)
#341 Production Agent Runtime Hardening (deferred), #502 Hardening, #503 Proving, #504 Codifying.

### 4.5 Other
#63 Odoo 18 Go-Live (Doing), #106 Schema Governance (Doing), #181 ipai_odoo_copilot (Done), #238–#244 Operating models (Odoo/AI Platform/Data Intel/SDK/Governance), #358 Financial Reports Intelligence, #521 Azure Pipelines Governance.

---

## 5. GitHub Plane

### 5.1 Open Issues — 36 (per earlier review)
- P0 hardening: #719 break-glass, #720 crit deps, #721 Fabric-vs-DBX trial
- P1 proving: #722 cost tagging, #723 SLOs, #724 canary rollout, #733 Partner Center
- P2 codifying: #726–#730 (evals, cost, SLO gates)
- Wave-02 Finance: #687–#690 (expense_ops, ppm_bridge, finance_close, taxpulse_bridge)
- Wave-03 Azure: #644 PIM, #649 WAF Review, #663 RBAC, #664 Bicep IaC
- Wave-04 Marketplace: #656–#662
- Deprecated: SAP benchmark set (`priority:deferred`)

### 5.2 Open PRs — 6
| # | Topic | Action |
|---|---|---|
| #749 | R3 gap closers (today) | merge after T2/T3 verified — ✅ all 3 live |
| #746 | BOM R3 trajectory doc | merge now |
| #737 | capability-coverage matrix | merge now |
| #736 | Partner Center runbook | merge after #733 |
| #735 | CI noise fix + staging | review — post-doctrine |
| #703 | Copilot DI + PPM sourcing | 4d old, 2/4 tasks |

### 5.3 CI/CD state (Azure Pipelines = sole authority)
- **GitHub Actions:** 0 workflows (deleted PR #747/#748)
- **Azure Pipelines:** 11 pipelines, 10 failing (per earlier session audit)
- **New pipeline added today:** `azure-pipelines/deploy-r3-gap-closers.yml`
- **Required check migration:** branch protection still lists deleted GHA checks — blocks merges

---

## 6. Agent Plane — Foundry + Pulser

### 6.1 Foundry
- Resource: `ipai-copilot-resource` (East US 2, cross-sub)
- SDK: `azure-ai-projects >= 2.0.0`
- Deployments: 0 (blueprint only)
- Managed Identity RBAC: live
- Sampled models: `gpt-4.1`, Claude via Responses API

### 6.2 Pulser agents
| Agent | Location | Status | D365 parity |
|---|---|---|---|
| `recon_agent` | `agents/skills/recon_agent/` | ✅ v0 shipped (18 tests) | Account Reconciliation Agent (preview) — IPAI exceeds MS |
| `project_finance` | `agents/skills/project_finance/` | scaffolded | — |
| `finance-month-end` | `agents/skills/finance-month-end/` | scaffolded | Period close |
| `bir_tax` | `agents/skills/bir_tax/` | scaffolded | PH tax |
| `research` | `agents/skills/research/` | scaffolded | PrismaLab companion |

### 6.3 Workflows
`r2r-close-workflow.py`, `bir-close-workflow.py`, `expense_liquidation_workflow.py`, `payment_reconcile_workflow.py`, `project-setup-workflow.py`.

### 6.4 Teams surface
- Adaptive Cards manifest: `agents/teams-surface/adaptive-cards-manifest.json`
- 6 Teams app regs created in Entra (bank-recon, ap-invoice, doc-intel, tax-guru, finance-close, pulser-main)

---

## 7. Data & BI Plane

### 7.1 PostgreSQL
- `pg-ipai-odoo` (General Purpose, Fabric mirroring enabled)
- Old `ipai-odoo-dev-pg` Burstable — DEPRECATED

### 7.2 Databricks
- `dbw-ipai-dev` workspace
- SQL warehouse `e7d89eabce4c330c`
- Managed access connector (MI-based)

### 7.3 Fabric
- `fcipaidev` workspace ACTIVE (do NOT pause per memory)
- Power BI Pro trial expires **2026-05-20** (36 days)
- Decision needed: Fabric vs Databricks mirror (GitHub #721 P0)

### 7.4 AI Search
- `srch-ipai-dev-sea` (basic SKU, ✅ NEW today)
- Corpus: `prismalab-rag-v1` (8 chunks, 6 sources)

### 7.5 Governance
- `pv-ipai-dev-sea` Purview ✅ NEW today
- Collections, scans, classifications: 0 configured
- Post-deploy steps: register data sources (ADLS × 3, PG, DBX, Foundry)

---

## 8. Runtime Plane — ACA

### 8.1 Container Apps
- `ipai-copilot-gateway` (public)
- `ipai-prismalab-gateway` (public + internal RAG)

### 8.2 Managed environments
- `ipai-odoo-dev-env-v2` (active)
- v1 preserved

### 8.3 Front Door
- `afd-ipai-dev` live + WAF + security headers

### 8.4 ACR
- `acripaidev`
- Images: `ipai-odoo:18.0-copilot` v18.0.6.0.0, prismalab-gateway, m365-bot-proxy

---

## 9. Platform Authority Split (doctrine)

| Function | Authority |
|---|---|
| Source control | GitHub |
| Code review/PR | GitHub |
| Issues (engineering execution) | GitHub |
| **CI/CD all lanes** | **Azure Pipelines** (sole authority per CLAUDE.md) |
| Portfolio/planning | ADO Boards |
| Test plans | ADO |
| Deploy: Odoo, Databricks, Infra, Finance modules | Azure DevOps |
| Deploy: docs/web | Azure Pipelines (GHA forbidden) |

---

## 10. Risks ranked by blast radius

1. **🔴 n8n enterprise app still active** — deprecated component may be used silently. Action: DELETE `ipai-n8n-entra`.
2. **🔴 Branch protection blocks all PRs** — required checks reference deleted workflows.
3. **🔴 Fabric trial decision (36 days)** — #721 undecided, BI continuity risk.
4. **🔴 10 of 11 Azure Pipelines failing** — staging CI blind spot.
5. **🔴 Purview 0 sources registered** — governance shell only.
6. **🟡 5 Enterprise apps without owner/CA/cert rotation** — audit tomorrow.
7. **🟡 Wave-01 pace gate 13 days out** — #528 AP/AR scaffolded today, views/tests must land before Apr 27.
8. **🟡 AI Search corpus is 8 chunks** — RAG grounding anemic; #623 target 7000+.
9. **🟡 No Entra diagnostic export to LA** — audit trail blind.
10. **🟡 Agent governance 0%** — 1 unmanaged, 0 collections, 0 blueprints policy-tagged.

---

## 11. Action-ordered plan (next 72h)

| # | Action | Where | Unblocks |
|---|---|---|---|
| 1 | Delete `ipai-n8n-entra` app reg | Entra | doctrine cleanup |
| 2 | Strip deleted GHA checks from `main` protection | GitHub → Settings | all PR merges |
| 3 | Merge PRs #749, #746, #737 | GitHub | R3 landing |
| 4 | Commit fpa/cash/tax modules when subagents complete | repo | Wave-01 #614, #529, #616 |
| 5 | Decide Fabric vs Databricks mirror | Azure portal | trial cutoff |
| 6 | Create `ssot/identity/entra-registry.yaml` | repo | identity SSOT |
| 7 | Entra CA-Apps-Baseline + diagnostic export | portal + bicep | governance |
| 8 | Register Purview data sources | portal | governance completeness |
| 9 | Assign agent owners + 3 custom collections | Entra | agent governance |
| 10 | Open Epic "Entra Identity Governance" in ADO | ADO Boards | tracking surface |

---

*Last updated: 2026-04-14 — live queries against subscription `eba824fb-332d-4623-9dfb-2c9f7ee83f4e`*
