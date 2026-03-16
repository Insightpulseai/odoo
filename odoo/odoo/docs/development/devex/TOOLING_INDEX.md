# Developer Tooling Index

> SSOT: [`ssot/devex/tooling_inventory.yaml`](../../../ssot/devex/tooling_inventory.yaml)
> Validator: `scripts/ci/check_tooling_inventory.py`
> CI guard: `.github/workflows/tooling-inventory-check.yml`

This document is the human-readable index of standardized developer tooling
for the `Insightpulseai/odoo` repository. Edit the SSOT YAML, not this file.

---

## VS Code Extensions

| ID | Name | Status | Purpose |
|----|------|--------|---------|
| `ms-vscode-remote.remote-containers` | Dev Containers | **required** | Standardized devcontainer workflow |
| `GitHub.vscode-pull-request-github` | GitHub PRs & Issues | **required** | In-editor PR review and issue triage |
| `ms-python.python` | Python | **required** | Odoo development, linting, testing |
| `ms-python.vscode-pylance` | Pylance | **required** | Type checking and IntelliSense |
| `redhat.vscode-yaml` | YAML | **required** | SSOT YAML schema validation |
| `editorconfig.editorconfig` | EditorConfig | **required** | Consistent formatting rules |
| `dbaeumer.vscode-eslint` | ESLint | recommended | JS/TS linting (MCP servers, apps) |
| `mhutchie.git-graph` | Git Graph | recommended | Branch/merge visualization |
| `dotjoshjohnson.xml` | XML Tools | optional | Odoo view XML editing |
| `ms-edgedevtools.vscode-edge-devtools` | Edge Tools | optional | Browser debugging (when needed) |
| `*.odoo-snippets` | Odoo Snippets packs | **avoid** | Inconsistent patterns across contributors |

## Docker Desktop Extensions

| Name | Status | Purpose |
|------|--------|---------|
| Logs Explorer | **required** | Container log triage without ID guessing |
| Resource Usage | **required** | Memory/CPU spike detection |
| Aqua Trivy | recommended | Image vulnerability scanning |
| Copacetic | optional | Patch images from scanner results |
| Remote Docker | optional | SSH tunnel to remote Docker hosts |
| Docker MCP Toolkit (Deprecated) | **avoid** | Deprecated; native integration exists |

## MCP Servers

| ID | Source | Status | Integration Surface | Approval Required |
|----|--------|--------|---------------------|-------------------|
| `github-mcp` | external | **active** | GitHub repo/PR/issues/actions | no |
| `supabase-mcp` | external | **active** | Supabase DB/Auth/Edge/Vault | no |
| `context7-mcp` | external | **active** | Library docs injection | no |
| `playwright-mcp` | external | **active** | E2E testing + regression | no |
| `sentry-mcp` | external | **active** | Error tracking/alerting | no |
| `netdata-mcp` | external | **active** | Server observability | no |
| `markitdown-mcp` | external | **active** | Document-to-Markdown conversion | no |
| `chrome-devtools-mcp` | external | **active** | Frontend perf/debug | no |
| `vercel-mcp` | external | planned | Vercel deployments | yes |
| `terraform-mcp` | external | planned | IaC enforcement (Cloudflare) | yes |
| `figma-mcp` | external | planned | Design token sync | yes |
| `stripe-mcp` | external | planned | Payment processing | yes |
| `docker-mcp-toolkit-deprecated` | external | **rejected** | Docker Hub (deprecated toolkit) | no |

### What we explicitly avoid

- **Docker MCP Toolkit**: Deprecated upstream. Docker Desktop ships native MCP integration.
- **Random Odoo Snippets packs**: No repo-wide standard; creates inconsistent patterns.
- **Any MCP server not listed above**: Must be proposed via PR to `ssot/devex/tooling_inventory.yaml` before adoption.

---

*Last updated: 2026-03-02*
