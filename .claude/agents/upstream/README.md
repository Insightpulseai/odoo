# Upstream Copilot Agents (Version-Pinned)

Source: [github/awesome-copilot/agents](https://github.com/github/awesome-copilot/tree/main/agents)

Version-pinned copies of upstream `awesome-copilot` custom agents that fit the
IPAI stack and doctrine. Committed in-repo per Engineering Execution Doctrine
("reuse upstream for commodity capability; configure for compositional
concerns; build only the thinnest `ipai_*` layer for business-specific
deltas").

## Why pinned copies, not live install

VS Code one-click install fetches from `main` branch — prompts drift without
our review. These copies are reviewed-at-commit and replayable. Refresh by
re-running the download snippet and committing the diff.

## Inventory

| Agent | Stack fit | Doctrine anchor |
|---|---|---|
| `azure-principal-architect` | Azure Well-Architected | Invariant #11 (SaaS Workload Doc) |
| `azure-saas-architect` | Multitenant Azure | Pulser/W9/Prismalab tenant model |
| `azure-verified-modules-bicep` | AVM Bicep | `azure-bicep-troubleshooting` skill upstream companion |
| `azure-verified-modules-terraform` | AVM Terraform | `terraform-specialist` subagent upstream |
| `azure-iac-generator` | IaC hub | Gap: partial IaC coverage across 63 live resources |
| `azure-iac-exporter` | Resource → IaC | Same gap |
| `azure-policy-analyzer` | Compliance | `ssot/governance/` |
| `azure-logic-apps-expert` | Logic Apps | Replaced deprecated n8n (2026-04-07) |
| `mcp-m365-agent-expert` | MCP on M365 | Matches commit `3e2cc9837` (m365 declarative agent scaffold) |
| `declarative-agents-architect` | Declarative agents | Three-protocol model — Agent365 SDK leg |
| `agent-governance-reviewer` | Agent safety | 3-tier defense doctrine (CLAUDE.md) |
| `defender-scout-kql` | Defender XDR KQL | CI/CD authority matrix uses Defender for DevOps |
| `kusto-assistant` | KQL for Azure Data Explorer | 4× `log-ipai-*-sea` Log Analytics workspaces |
| `context-architect` | Multi-file planning | Complements `speckit.plan` |
| `expert-react-frontend-engineer` | React/Vite | `ipai-website`, `ipai-prismalab`, `ipai-w9studio` |
| `adr-generator` | ADRs | Feeds `docs/architecture/` decisions |

## Not imported (and why)

- **PRD Chat Mode / Implementation Plan Mode** — duplicate `speckit.specify` / `speckit.plan`.
- **Gem Planner/Orchestrator/Implementer/Researcher, Blueprint Mode** — duplicate `superpowers:*` + `speckit.*`.
- **Critical Thinking / Devils Advocate / Mentor** — duplicate `socratic-mentor` subagent.
- **GitHub Actions Expert** — contradicts CLAUDE.md (Azure Pipelines is sole deploy authority; GHA scoped-exception only).
- **Linux distro experts, Laravel/Drupal/Clojure/C++/MAUI/.NET/AEM** — stack mismatch (ACA containers only; no Laravel/Drupal/etc.).
- **Launchdarkly / Amplitude / Apify / JFrog / Atlassian / Dynatrace / Elasticsearch** — not in vendor list.

## Refresh procedure

```bash
cd .claude/agents/upstream
BASE=https://raw.githubusercontent.com/github/awesome-copilot/main/agents
for f in *.agent.md; do curl -sSL -o "$f" "$BASE/$f"; done
git diff --stat
# Review diff, commit if acceptable
```
