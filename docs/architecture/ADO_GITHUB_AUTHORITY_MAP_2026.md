# ADO / GitHub Authority Map 2026

> **SSOT**: `ssot/governance/ado_github_authority_map.yaml`
> **Related**: `ssot/governance/azdo-execution-hierarchy.yaml`, `infra/ssot/github/desired-end-state.yaml`
> **Date**: 2026-03-23

---

## 1. Single ADO Project

**`ipai-platform`** is the sole Azure DevOps project for InsightPulse AI. All Boards work items, pipelines, and artifacts live here. There is no second project.

## 2. GitHub Repos as Code Authority

GitHub is the code authority. Azure DevOps is the work-tracking and pipeline authority. The 11 canonical repos under `github.com/Insightpulseai`:

| # | GitHub Repo | Area Path in ADO | Purpose |
|---|-------------|------------------|---------|
| 1 | `odoo` | `ipai-platform\ERP` | Odoo CE 19 + IPAI addons + OCA |
| 2 | `agents` | `ipai-platform\Agents` | Agent skills, evals, knowledge base |
| 3 | `data-intelligence` | `ipai-platform\Data` | Databricks lakehouse, ETL, BI |
| 4 | `agent-platform` | `ipai-platform\Agents\Runtime` | Agent orchestration runtime |
| 5 | `infra` | `ipai-platform\Infra` | Shared IaC (Bicep, Terraform) |
| 6 | `design` | `ipai-platform\Design` | Design tokens, component library |
| 7 | `platform` | `ipai-platform\Platform` | Control-plane services |
| 8 | `web` | `ipai-platform\Web` | Web apps, ops console |
| 9 | `docs` | `ipai-platform\Docs` | Documentation site |
| 10 | `mobile` | `ipai-platform\Mobile` | iOS/Android apps |
| 11 | `mcp` | `ipai-platform\MCP` | MCP server implementations |

## 3. PR to Work Item Linkage

Every PR that closes or advances a work item must include `AB#<id>` in the PR description or commit message. Azure DevOps auto-links the PR to the work item.

**Pattern**: `AB#12345` in PR body or commit message.

**CI enforcement**: The `planning-index-ssot-check.yml` workflow validates that merged PRs on `main` reference an `AB#` tag when touching `addons/`, `agents/`, or `infra/` paths.

## 4. Area Path to Repo Mapping

```
ipai-platform (root)
  \ERP           -> odoo
  \Agents        -> agents
  \Agents\Runtime -> agent-platform
  \Data          -> data-intelligence
  \Infra         -> infra
  \Design        -> design
  \Platform      -> platform
  \Web           -> web
  \Docs          -> docs
  \Mobile        -> mobile
  \MCP           -> mcp
```

Each area path maps 1:1 to a GitHub repo. Cross-repo work items use the parent area path (`ipai-platform`) and tag both repos.

## 5. Rules

1. **One project**: All work lives in `ipai-platform`. Do not create additional ADO projects.
2. **GitHub is code truth**: Never store source code in ADO repos. ADO repos are disabled.
3. **AB# linkage is mandatory**: PRs without `AB#` tags are flagged by CI.
4. **Area paths match repos**: Do not create area paths that do not correspond to a repo.
5. **Pipelines reference GitHub**: ADO pipelines use GitHub service connections, not ADO repos.

---

*Machine-readable version: `ssot/governance/ado_github_authority_map.yaml`*
