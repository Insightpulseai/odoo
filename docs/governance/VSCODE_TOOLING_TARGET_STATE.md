# VS Code Tooling Target State

> **Status**: Approved
> **Date**: 2026-03-22
> **Profile**: InsightPulseAI Platform Engineering

---

## Target Statement

VS Code is the canonical IDE, configured through one shared InsightPulseAI profile, bootstrapped by CLI, with Azure/Container/Testing/Databricks support and a small MCP allowlist centered on GitHub, Azure DevOps, Azure AI Foundry, Microsoft Learn, Terraform, and only the platform integrations that are actually part of the architecture.

---

## Core Extension Allowlist

| Extension | ID | Purpose |
|-----------|-----|---------|
| GitHub Copilot | `github.copilot` | AI code assistance |
| GitHub Copilot Chat | `github.copilot-chat` | AI chat |
| GitHub PRs | `github.vscode-pull-request-github` | PR workflow |
| Container Tools | `ms-azuretools.vscode-docker` | Container build/debug |
| Azure Resources | `ms-azuretools.vscode-azureresourcegroups` | Azure operations |
| Azure Developer CLI | `ms-azuretools.azure-dev` | Azure dev workflow |
| Azure Account | `ms-vscode.azure-account` | Azure auth |
| Python | `ms-python.python` | Python language |
| Pylance | `ms-python.vscode-pylance` | Python analysis |
| Ruff | `charliermarsh.ruff` | Python linting/formatting |
| YAML | `redhat.vscode-yaml` | YAML support |
| Prettier | `esbenp.prettier-vscode` | JS/TS/JSON formatting |
| ESLint | `dbaeumer.vscode-eslint` | JS/TS linting |
| EditorConfig | `editorconfig.editorconfig` | Editor consistency |
| Terraform | `hashicorp.terraform` | IaC support |
| Databricks | `databricks.databricks` | Workspace productivity |
| Odoo Language Server | `odoo.odoo-language-server` | Odoo module dev |
| Git Graph | `mhutchie.git-graph` | Git visualization |

---

## MCP Server Allowlist

### Tier 1 — Default Install

| MCP Server | Architecture Plane | Why |
|------------|-------------------|-----|
| GitHub | Engineering truth | Repo/PR/issue operations |
| Azure DevOps | Governance spine | Boards/pipelines/environments |
| Azure AI Foundry | Agent/gen-AI plane | Model/agent operations |
| Microsoft Learn | Documentation | Grounded doc retrieval |
| Terraform | IaC | Infrastructure operations |

### Tier 2 — Install When Active

| MCP Server | Condition |
|------------|-----------|
| Supabase | Only if still part of active platform scope |
| Vercel | Only if Vercel deployment is active |
| Stripe | Only if payment integration is active |
| Microsoft Entra | Only for identity management tasks |
| Fabric / RTI | Only for BI-specific work |
| Clarity | Only for analytics-specific work |

### Tier 3 — Do Not Default

Generic search/scrape/data-store MCPs, ecosystem-specific frontend MCPs, and alternative DB MCPs not in the target stack.

---

## Databricks Tooling Target

| Surface | Tool | Auth |
|---------|------|------|
| Local dev | Databricks CLI | Azure CLI (user interactive) |
| IDE productivity | VS Code Databricks extension | CLI-delegated auth |
| CI/CD | `databricks bundle validate/deploy` | AzureCLI@2 + service connection |
| Unattended | Databricks CLI | OAuth M2M |

The CLI is the durable contract. The extension is convenience.

---

## Profile Bootstrap (CLI)

```bash
# Install canonical extensions
code --install-extension github.copilot
code --install-extension github.copilot-chat
code --install-extension github.vscode-pull-request-github
code --install-extension ms-azuretools.vscode-docker
code --install-extension ms-azuretools.vscode-azureresourcegroups
code --install-extension ms-azuretools.azure-dev
code --install-extension ms-vscode.azure-account
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension charliermarsh.ruff
code --install-extension redhat.vscode-yaml
code --install-extension esbenp.prettier-vscode
code --install-extension dbaeumer.vscode-eslint
code --install-extension editorconfig.editorconfig
code --install-extension hashicorp.terraform
code --install-extension databricks.databricks
code --install-extension odoo.odoo-language-server
code --install-extension mhutchie.git-graph
```

---

## Do Not Target

- Every MCP server in the registry
- Per-repo custom VS Code profiles
- Extension sprawl without an allowlist
- IDE-only Databricks workflows with no CLI parity
- Package/plugin publishing as a prerequisite for IDE setup
