# Developer Tooling Target State

> **Status**: Live baseline
> **Date**: 2026-03-22 (updated from approved → live baseline)

---

## One-Line Target

GitHub is the code and PR authority; Azure Boards and Pipelines provide work-item and deployment traceability; Databricks is the governed data/analytics backbone; Microsoft Foundry is the primary AI and agent application plane; Entra and service connections are the auth boundary.

### Platform Plane Model

```text
Databricks     = governed data / analytics backbone
Foundry        = primary AI and agent application plane
Fabric         = downstream BI / semantic consumption (Power BI)
Azure DevOps   = governance / identity / promotion spine
GitHub         = code / PR authority
```

---

## 0. Code Authority Model

GitHub is the canonical code host. Azure DevOps is the governance spine around it, not a replacement.

| Surface | Authority | Notes |
|---------|-----------|-------|
| **GitHub** | Repos, branches, pull requests | Source of truth for code |
| **Azure Boards** | Work items, epics, sprint governance | Connected via Azure Boards app for GitHub |
| **Azure Pipelines** | CI/CD, build/deploy traceability | Triggered by GitHub events |
| **Azure Test Plans** | Manual UAT, requirement traceability | Bounded acceptance surface |
| **Azure Repos** | Not used | Optional; not the target primary code host |

### Traceability Chain

Every meaningful change must link through this chain:

```text
Azure Boards work item → GitHub branch → GitHub PR (AB#<id>) → Azure Pipelines build → deployment stage
```

- PRs link to Azure Boards work items via `AB#<id>` in the PR title or description
- Azure Pipelines writes `Integrated in build` and `Integrated in release` links back to work items
- Branch policies should check for linked work items where justified
- The Azure Boards app for GitHub is the supported integration path (not ad hoc PAT-based personal auth)

### GitHub-to-Boards Integration

Install and configure the **Azure Boards app for GitHub** on the `Insightpulseai` org:

- Connects GitHub repos to Azure Boards projects
- Enables `AB#` work-item linking from commits and PRs
- Supports `fix/fixes/fixed AB#<id>` to transition work items on merge
- Provides PR insights on work items and build traceability for YAML pipelines

---

## 1. Identity, Org Control, and Authentication

### Org Settings

| Setting | Current | Target | Action |
|---------|---------|--------|--------|
| Azure DevOps connected to Entra | Yes (Default Directory) | Keep | **Keep** |
| Restrict global PAT creation | Off | On | **Enable now** |
| Restrict full-scoped PAT creation | Off | On | **Enable now** |
| Enforce max PAT lifespan | Off | 30 days | **Enable now** |
| Leaked PAT auto-revocation | On | On | **Keep** |
| Service connections for auth | Partial | Primary auth method | **Expand** |
| PAT-centric automation | In use | Eliminated | **Phase out** |

### Authentication Method by Scenario

Per [Microsoft authentication guidance](https://learn.microsoft.com/en-us/azure/devops/integrate/get-started/authentication/authentication-guidance?view=azure-devops): use Microsoft Entra ID for new applications, use PATs sparingly and only when Entra ID is not available.

| Scenario | Recommended method | Do NOT use |
|----------|-------------------|------------|
| Azure Pipelines CI/CD | Service principals + managed identities | PATs |
| Azure-to-Databricks automation | `AzureCLI@2` + service connection (Entra-backed) | PATs |
| GitHub Actions → Azure DevOps | Workload identity federation (OIDC) | Long-lived PATs |
| Background services / Azure Functions | Service principals or managed identities | User-delegated tokens |
| Interactive web/desktop apps | Microsoft Entra OAuth (MSAL) | PATs |
| Local human dev (Databricks CLI) | `databricks auth login` (interactive Azure CLI) | Shared PATs |
| Personal scripts / ad hoc tasks | PATs (scoped, short-lived) | Full-scope PATs |
| Azure DevOps extensions | Azure DevOps web extension SDK | PATs |

### PAT Reduction Target

Microsoft explicitly recommends reducing PAT usage. The target policy:

- **New integrations**: Must use Entra ID (OAuth, service principals, managed identities)
- **Existing PAT integrations**: Plan migration to Entra ID auth
- **Remaining PATs**: Scoped to minimum permissions, max 30-day lifespan, never full-scope
- **Never**: Decode or read claims from authentication tokens (Azure DevOps is encrypting token payloads starting summer 2025)

### Service-to-Service Auth

All service-to-service communication must use service principals or managed identities:

- Azure Pipelines → Azure resources: service connection (Entra-backed)
- Azure Pipelines → Databricks: `AzureCLI@2` with service connection
- Azure Functions → Azure DevOps APIs: managed identity
- Odoo → Azure Key Vault: managed identity
- Do not use service accounts with interactive sign-in for automation

## 2. Azure DevOps Delivery Model

| Component | Target | Notes |
|-----------|--------|-------|
| Boards | Governance / work tracking | Epics, tasks, sprint planning |
| Pipelines | Gated promotion | dev → staging → prod |
| Service connections | Azure + Databricks auth | AzureCLI@2 pattern |
| Agent pools | `ipai-build-pool` + Azure Pipelines | Keep lean |
| Marketplace extensions | Minimal | Do not add without architecture justification |
| Project structure | Single `ipai-platform` project | Keep lean |

## 3. Databricks Auth and Live Dev Baseline

**Databricks CLI + Azure DevOps service connection + live dev workspace baseline**

### Canonical Dev Workspace

| Property | Value |
|----------|-------|
| Workspace name | `dbw-ipai-dev` |
| Workspace host | `https://adb-7405610347978231.11.azuredatabricks.net` |
| Pricing tier | Premium (+ RBAC) |
| No Public IP | Yes |
| Primary dev catalog | `dbw_ipai_dev` |
| Federated source catalog | `odoo_erp` (Lakehouse Federation → Odoo PG) |
| Domain analytics catalog | `dev_ppm` |
| Dev SQL warehouse | `ipai-sql-warehouse-dev` (serverless) |
| Genie | Enabled, zero spaces (intentional) |

### Auth Model

| Surface | Method | Config |
|---------|--------|--------|
| Local human dev | `databricks auth login --host <url>` | Interactive Azure CLI |
| Azure DevOps CI/CD | `AzureCLI@2` + service connection | `DATABRICKS_HOST` env var |
| Unattended bots | Databricks OAuth M2M | Service principal |
| GitHub Actions | OIDC / workload identity federation | Deferred |

### Bundle Defaults

Local bundle target must be `dev` with real workspace host. `prod` is reserved for gated promotion only.

```text
local bundle target = dev
mode = development
workspace_host = https://adb-7405610347978231.11.azuredatabricks.net
```

Every `databricks.yml` target must resolve to a real workspace URL, not an unresolved variable.

### Unity Catalog as Namespace Boundary

| Catalog | Role | Governance |
|---------|------|------------|
| `dbw_ipai_dev` | Platform/dev lakehouse | Primary dev workspace catalog |
| `odoo_erp` | Federated source-facing | Read-only via Lakehouse Federation |
| `dev_ppm` | Domain-oriented analytics | Finance/PPM analytical domain |
| `system` | Databricks internal | Do not modify |

Avoid ad hoc catalog sprawl. New catalogs require architecture justification.

### Serverless SQL Warehouse

`ipai-sql-warehouse-dev` is the canonical dev SQL-serving baseline for:
- Gold mart validation
- Dashboard queries
- Budget vs actual / finance PPM analytics
- Future Genie spaces

### Genie Policy

Genie is enabled but must remain empty until:
- Gold marts are stable and promoted
- Semantic naming is cleaned up
- Dashboard and warehouse contracts are stable

Create **one curated finance/PPM Genie space** as the first space, not a broad default.

## 3a. Live Workspace Discipline

Because the dev workspace already contains jobs, dashboards, workspace assets, a serverless SQL warehouse, and multiple catalogs:

- Persistent jobs must be repo-defined (bundle YAML) and promotion-controlled (Azure DevOps)
- Persistent dashboards must map to governed warehouse/catalog outputs
- Ad hoc UI-created assets should be minimized and either codified or cleaned up
- The Databricks UI is an operator/inspection surface, not the source of truth for promoted assets
- Azure DevOps = promotion and governance spine; repo bundles/SQL/code = source of truth

## 4. Microsoft Foundry — AI and Agent Plane

Per [What is Microsoft Foundry?](https://learn.microsoft.com/en-us/azure/foundry/what-is-foundry): Foundry is the unified Azure PaaS for enterprise AI operations, model builders, and app development. New investments are focused on Foundry projects in the new portal, not the older hub-based model.

### Target Position

Microsoft Foundry is the **primary AI and agent application plane**. It is not an optional overlay.

### Use Foundry for

- Agent creation and orchestration
- Tool-connected agent workflows (tool catalog)
- Model deployment, fine-tuning, and evaluation
- Tracing, monitoring, and governance of AI assets
- Publishing agents to Microsoft 365, Teams, BizChat, or containerized runtimes
- VS Code AI Toolkit / Foundry developer workflows

### Do not use Foundry for

- Data engineering, medallion transforms, or governed mart construction (Databricks)
- SQL serving or dashboard-backing queries (Databricks SQL warehouse)
- BI consumption (Power BI / Fabric)

### Foundry vs Classic

- **Target**: Foundry resources + Foundry projects in the new portal
- **Do not target**: Legacy hub-based projects (Foundry classic)
- Older hub-based projects stay in Foundry classic; new work must use the new model

### Foundry ↔ Databricks Boundary

| Plane | Owner | Examples |
|-------|-------|---------|
| Data ingestion, transforms, marts | Databricks | Bronze/silver/gold, DLT, Unity Catalog, SQL warehouse |
| AI agents, tools, evals, tracing | Foundry | Agent orchestration, tool catalog, model deployment |
| BI / semantic consumption | Fabric + Power BI | Mirroring, semantic models, reports |
| Governance / promotion | Azure DevOps | Pipelines, Boards, service connections |

Foundry **consumes** governed data outputs from Databricks. It does not replace the data platform.

### Repo Direction

Target an explicit `agent-platform` runtime plane for Foundry operational assets (evaluations, tracing, deployment contracts, agent runtime glue). Current repo mapping:

| Repo directory | Plane | Content |
|---------------|-------|---------|
| `data-intelligence/` | Databricks | Bundles, transforms, marts, serving prep |
| `agent-platform/` | Foundry runtime | Agent deployment, evals, tracing |
| `agents/` | Foundry design | Personas, skills, tool schemas, prompt contracts |
| `platform/` | Control plane | Metadata, secret refs, integration glue |

### Live Resources

| Resource | Type | Resource Group | Region |
|----------|------|---------------|--------|
| `aifoundry-ipai-dev` | AI Hub / Foundry | `rg-ipai-ai-dev` | East US 2 |
| `oai-ipai-dev` | Azure OpenAI | `rg-ipai-ai-dev` | East US |

---

## 5. VS Code Standard

| Setting | Target |
|---------|--------|
| IDE | VS Code (canonical) |
| Profile | InsightPulseAI Platform Engineering |
| Workspace model | Repo-root canonical |
| Org-root orchestration | Allowed for Claude Code / Codex |
| Multi-root workspace | Not canonical — convenience only |
| Enterprise controls | Managed profile + extension policy |
| Per-repo config | `.vscode/settings.json` + `extensions.json` |

## 6. Extension Allowlist

### Core (18 extensions)

| Extension | Purpose |
|-----------|---------|
| `github.copilot` | AI code assistance |
| `github.copilot-chat` | AI chat |
| `github.vscode-pull-request-github` | PR workflow |
| `ms-azuretools.vscode-docker` | Container tools |
| `ms-azuretools.vscode-azureresourcegroups` | Azure resources |
| `ms-azuretools.azure-dev` | Azure dev CLI |
| `ms-vscode.azure-account` | Azure auth |
| `ms-python.python` | Python |
| `ms-python.vscode-pylance` | Python analysis |
| `charliermarsh.ruff` | Python lint/format |
| `redhat.vscode-yaml` | YAML |
| `esbenp.prettier-vscode` | JS/TS/JSON format |
| `dbaeumer.vscode-eslint` | JS/TS lint |
| `editorconfig.editorconfig` | Editor consistency |
| `hashicorp.terraform` | IaC |
| `databricks.databricks` | Databricks workspace |
| `odoo.odoo-language-server` | Odoo modules |
| `mhutchie.git-graph` | Git visualization |

## 7. MCP Allowlist

### Tier 1 — Default

- GitHub
- Azure DevOps
- Microsoft Foundry
- Microsoft Learn
- Terraform

### Tier 2 — Install When Active

- Supabase (if still in platform scope)
- Vercel, Stripe, Entra, Fabric, Clarity (per workstream)

### Tier 3 — Do Not Default

- Generic scrape/search/DB/frontend MCPs not in the target stack

## 8. Container and Test Model

| Surface | Role |
|---------|------|
| Containers view | Odoo runtime validation, compose inspection |
| Testing view | Playwright, Python tests, Foundry eval hooks |
| AI Toolkit | Foundry integration (data-intel-ph) |

VS Code is the operator surface, not the deployment authority.

## 9. Azure Test Plans Target State

### Role

Azure Test Plans is a bounded acceptance-testing and requirement-traceability surface.

### Use it for

- Manual UAT and business validation
- Requirement-linked acceptance tests (requirement-based suites only)
- Release signoff evidence
- Cross-functional validation tied to backlog items

### Do not use it for

- Primary automated test authoring
- Replacing repo-native test frameworks (Playwright, pytest, Odoo `--test-enable`)
- Replacing CI test execution in Azure Pipelines

### Suite policy

Prefer requirement-based test suites when end-to-end traceability is required.
Use static or query-based suites only when traceability to backlog items is not the primary need.

### Access policy

| Access level | Role |
|-------------|------|
| Basic + Test Plans | Plan/suite/test-case authors and test managers |
| Basic | Execution and reporting users |
| Stakeholder | Feedback-only users (browser extension, no portal) |

### Runner policy

Prefer the web-based test runner for manual testing.
Do not build new dependencies on the retiring Windows Test Runner client.

### Priority acceptance packs

- Finance PPM dashboard acceptance
- Budget vs actual validation
- Odoo finance/expense acceptance
- Key cross-repo release signoff

See `docs/governance/TEST_STRATEGY_TARGET_STATE.md` for the full test strategy separating repo automation, Databricks validation, and Azure Test Plans UAT.

## 10. Odoo and AI Platform Target

| Service | Role | Boundary |
|---------|------|----------|
| **Odoo 19 CE + OCA** | Operational SoR, user-facing business workflows | Not analytics, not agent orchestration |
| **Odoo.sh** | Delivery benchmark (Git/branch/build/settings semantics) | Not the runtime destination (Azure is) |
| **Microsoft Foundry** | Primary AI and agent application plane | Not the transactional backend |
| **Document Intelligence** | OCR / extraction / classification bridge | Outputs feed Odoo workflows + Databricks analytics |
| **Databricks** | Governed analytics backbone | Not the document-ingestion engine |
| **Azure Container Apps** | Default runtime plane | Odoo.sh-aligned delivery semantics on Azure |

### Canonical architecture sentence

Odoo is the operational SoR, Odoo.sh is the delivery benchmark, Foundry is the primary AI/agent plane, Document Intelligence is the OCR/extraction bridge, Databricks is the governed analytics backbone, and Azure DevOps governs promotion across all of it.

### Do not

- Use Foundry as the transactional backend
- Use Databricks as the document-ingestion engine
- Treat Odoo.sh as the runtime target
- Replace Odoo business workflows with Foundry agents
- Collapse document extraction into Odoo or Databricks

## 11. What to Avoid

- Azure DevOps extension sprawl
- PAT-centric automation
- Giant canonical multi-root workspace
- Broad MCP registry installs
- IDE-only Databricks workflows with no CLI parity
- Unresolved `${var.*}` in extension-facing configs
- Using Databricks as the primary agent runtime plane (use Foundry)
- Building on legacy Foundry classic hub/project patterns
- Collapsing data engineering into Foundry (Databricks owns the data plane)
- Treating Foundry as an optional overlay (it is the primary AI plane)

---

## Summary Matrix

| Surface | Target |
|---------|--------|
| GitHub | Code and PR authority |
| Azure Boards | Work-item and initiative governance |
| Azure Repos | Not used (GitHub is primary) |
| Traceability | Work item → PR → build → deploy (mandatory) |
| Entra | Identity authority |
| Azure DevOps | Governance + promotion spine |
| Azure DevOps PATs | Restricted: scoped, 30-day max, no full-scope, migration to Entra planned |
| Azure DevOps auth | Entra ID first (service principals, managed identities, MSAL OAuth) |
| Service-to-service | Service principals + managed identities only (no PATs) |
| Odoo 19 CE + OCA | Operational SoR + business application surface |
| Odoo.sh | Delivery benchmark only (not runtime target) |
| Microsoft Foundry | Primary AI and agent application plane |
| Foundry project model | New portal Foundry projects (not classic hubs) |
| Document Intelligence | OCR / extraction / classification bridge |
| Fabric + Power BI | Downstream BI / semantic consumption |
| Azure Container Apps | Default runtime plane (Odoo.sh-aligned semantics) |
| Databricks workspace | `dbw-ipai-dev` (live, Premium, RBAC) |
| Databricks local auth | CLI login against real workspace host |
| Databricks CI auth | AzureCLI@2 + service connection |
| Databricks catalogs | `dbw_ipai_dev` + `odoo_erp` (federated) + `dev_ppm` |
| Databricks SQL warehouse | `ipai-sql-warehouse-dev` (serverless) |
| Databricks Genie | Enabled, zero spaces until curated |
| Databricks UI | Operator/inspection surface, not source of truth |
| VS Code | Primary IDE |
| VS Code workspace model | Repo-root canonical |
| VS Code enterprise controls | Managed profile + extension policy |
| Containers | Runtime/operator surface |
| Testing | Standard test/eval surface |
| Azure Test Plans | Bounded UAT + requirement traceability only |
| MCP | Small allowlist only |

## Compute Hosting Target

| Compute | Role | Default? |
|---------|------|----------|
| Azure Container Apps | Containerized APIs, workers, jobs, microservices, event-driven | **Default** |
| Azure App Service | Bounded web/API hosting exception | Exception only |
| App Service Environment | Single-tenant isolated App Service | Rare exception |
| App Service Managed Instance | Legacy Windows dependencies (COM, registry, MSI) | Last-resort legacy |
| AKS | Direct Kubernetes control-plane access | Not default |

Rule: Use ACA unless App Service platform features are specifically needed.

## Odoo and AI Platform Target

- Odoo remains the operational SoR and user-facing business workflow surface.
- Foundry remains the primary agent plane.
- Document Intelligence remains the document extraction/classification bridge.
- Databricks remains the governed analytics backbone.
- Odoo.sh is a delivery benchmark only, not the runtime destination.

## Highest-Priority Deltas

1. Bind local bundle default to `dev` + real workspace host — **done** (all 3 bundles)
2. Treat `dbw_ipai_dev` + `odoo_erp` as canonical current catalog model
3. Use `ipai-sql-warehouse-dev` as standard dev serving surface
4. Keep Genie empty until one curated finance/PPM space is ready
5. Prevent Databricks UI drift by making repo + Azure DevOps the authority
6. Install Azure Boards app for GitHub on `Insightpulseai` org — **enable now**
7. Require `AB#` work-item linkage on PRs for governed workstreams
8. Harden PAT policy (restrict global, restrict full-scope, 30-day max) — **enable now**

## Verification Checklist

- [ ] GitHub repos connected to Azure Boards through Azure Boards app
- [ ] PRs consistently link to Azure Boards work items via `AB#`
- [ ] Azure Pipelines writes build/release traceability back to work items
- [ ] Databricks local default target is `dev`, not `prod`
- [ ] `dbw-ipai-dev` treated as canonical dev workspace baseline
- [ ] PAT policy hardened: no new long-lived broad PAT flows
- [ ] Shared variables match live environment (`dbw_ipai_dev`, real workspace host)
- [ ] Foundry described as primary AI/agent plane, not a sidecar
- [ ] New AI work assumes Foundry projects in the new portal, not classic hubs
- [ ] Databricks remains the data/analytics plane (not collapsed into Foundry)
- [ ] AI Toolkit / Foundry workflows treated as first-class in dev-tooling target
