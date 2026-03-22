# Developer Tooling Target State

> **Status**: Live baseline
> **Date**: 2026-03-22 (updated from approved → live baseline)

---

## One-Line Target

The target is no longer "prepare for Databricks"; it is "standardize the live `dbw-ipai-dev` workspace as the governed dev baseline, with repo-defined bundles and Azure DevOps promotion controlling what persists."

---

## 1. Identity and Org Control

| Setting | Current | Target | Action |
|---------|---------|--------|--------|
| Azure DevOps connected to Entra | Yes (Default Directory) | Keep | **Keep** |
| Restrict global PAT creation | Off | On | **Enable now** |
| Restrict full-scoped PAT creation | Off | On | **Enable now** |
| Enforce max PAT lifespan | Off | 30 days | **Enable now** |
| Leaked PAT auto-revocation | On | On | **Keep** |
| Service connections for auth | Partial | Primary auth method | **Expand** |
| PAT-centric automation | In use | Eliminated | **Phase out** |

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

## 4. VS Code Standard

| Setting | Target |
|---------|--------|
| IDE | VS Code (canonical) |
| Profile | InsightPulseAI Platform Engineering |
| Workspace model | Repo-root canonical |
| Org-root orchestration | Allowed for Claude Code / Codex |
| Multi-root workspace | Not canonical — convenience only |
| Enterprise controls | Managed profile + extension policy |
| Per-repo config | `.vscode/settings.json` + `extensions.json` |

## 5. Extension Allowlist

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

## 6. MCP Allowlist

### Tier 1 — Default

- GitHub
- Azure DevOps
- Azure AI Foundry
- Microsoft Learn
- Terraform

### Tier 2 — Install When Active

- Supabase (if still in platform scope)
- Vercel, Stripe, Entra, Fabric, Clarity (per workstream)

### Tier 3 — Do Not Default

- Generic scrape/search/DB/frontend MCPs not in the target stack

## 7. Container and Test Model

| Surface | Role |
|---------|------|
| Containers view | Odoo runtime validation, compose inspection |
| Testing view | Playwright, Python tests, Foundry eval hooks |
| AI Toolkit | Foundry integration (data-intel-ph) |

VS Code is the operator surface, not the deployment authority.

## 8. What to Avoid

- Azure DevOps extension sprawl
- PAT-centric automation
- Giant canonical multi-root workspace
- Broad MCP registry installs
- IDE-only Databricks workflows with no CLI parity
- Unresolved `${var.*}` in extension-facing configs

---

## Summary Matrix

| Surface | Target |
|---------|--------|
| Entra | Identity authority |
| Azure DevOps | Governance + promotion spine |
| Azure DevOps PATs | Heavily restricted (30-day max, no full-scope) |
| Azure DevOps auth | Service connection first |
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
| MCP | Small allowlist only |

## Highest-Priority Deltas

1. Bind local bundle default to `dev` + real workspace host — **done** (all 3 bundles)
2. Treat `dbw_ipai_dev` + `odoo_erp` as canonical current catalog model
3. Use `ipai-sql-warehouse-dev` as standard dev serving surface
4. Keep Genie empty until one curated finance/PPM space is ready
5. Prevent Databricks UI drift by making repo + Azure DevOps the authority
