# Agency Agents (msitarzewski/agency-agents)

Source: [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) · MIT

Version-pinned copies of the 10 `agency-agents` personas that fill gaps left by
`github/awesome-copilot` (imported in the sibling directory `../`). Committed
in-repo per Engineering Execution Doctrine.

## Inventory

| Agent | Origin path | Fills IPAI gap |
|---|---|---|
| `mcp-builder.md` | `specialized/specialized-mcp-builder.md` | MCP server authoring — complements `mcp-m365-agent-expert` (channel side) |
| `agents-orchestrator.md` | `specialized/agents-orchestrator.md` | Supervisor-mediated orchestration (three-protocol doctrine) |
| `agentic-identity-trust.md` | `specialized/agentic-identity-trust.md` | Agent ID / Entra trust (feeds `entra-identity-governance` skill) |
| `testing-evidence-collector.md` | `testing/testing-evidence-collector.md` | Matches Operating Contract's "Evidence pack" requirement |
| `testing-reality-checker.md` | `testing/testing-reality-checker.md` | Matches "verify before commit" discipline |
| `finance-bookkeeper-controller.md` | `finance/finance-bookkeeper-controller.md` | Pulser finance copilot — month-end close |
| `finance-fpa-analyst.md` | `finance/finance-fpa-analyst.md` | Pulser Project-to-Profit cockpit |
| `finance-tax-strategist.md` | `finance/finance-tax-strategist.md` | BIR compliance domain (PH tax) |
| `compliance-auditor.md` | `specialized/compliance-auditor.md` | SOC2 / ISO 27001 — supports `cso` skill |
| `automation-governance-architect.md` | `specialized/automation-governance-architect.md` | Logic Apps governance (replaces deprecated n8n) |

## Why this subfolder (vs parent `upstream/`)

`upstream/` holds GitHub-official `awesome-copilot` agents (neutral prompt contracts).
`upstream/agency/` holds community `agency-agents` personas (strongly opinionated).
Different source, different style, different review gate — keep separated.

## Refresh procedure

```bash
cd .claude/agents/upstream/agency
BASE=https://raw.githubusercontent.com/msitarzewski/agency-agents/main
# See parent README for the source→dest mapping
```
