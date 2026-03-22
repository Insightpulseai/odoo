# Developer Tooling Target State

> **Status**: Approved
> **Date**: 2026-03-22

---

## One-Line Target

Entra-backed Azure DevOps org, PAT-hardened, AzureCLI@2/service-connection Databricks auth, repo-root VS Code workflow, curated extension/MCP allowlist, Databricks bundles fixed to real target hosts, and Azure DevOps Boards/Pipelines as the governance and promotion spine.

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

## 3. Databricks Auth and Workspace

| Surface | Method | Config |
|---------|--------|--------|
| Local human dev | `databricks auth login --host <url>` | Interactive Azure CLI |
| Azure DevOps CI/CD | `AzureCLI@2` + service connection | `DATABRICKS_HOST` env var |
| Unattended bots | Databricks OAuth M2M | Service principal |
| GitHub Actions | OIDC / workload identity federation | Deferred |

### Fix Now — Databricks Extension State

Current (broken):
```
Target: prod
Mode: Development
Host: https://${var.workspace_host}/
```

Target (correct):
```
Target: dev
Mode: development
Host: https://adb-7405610347978231.11.azuredatabricks.net
```

### Bundle Host Resolution

Every `databricks.yml` target must resolve to a real workspace URL, not an unresolved variable. Use `.databrickscfg` profiles or environment variables to inject the host per target.

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
| Azure DevOps | Governance spine |
| Azure DevOps PATs | Heavily restricted |
| Azure DevOps auth | Service connection first |
| Databricks local auth | CLI login |
| Databricks CI auth | AzureCLI@2 |
| VS Code | Primary IDE |
| VS Code workspace model | Repo-root canonical |
| VS Code enterprise controls | Managed profile + extension policy |
| Containers | Runtime/operator surface |
| Testing | Standard test/eval surface |
| MCP | Small allowlist only |
