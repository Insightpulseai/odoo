# `microsoft/azure-skills` — Plugin Reference

> Source: https://github.com/microsoft/azure-skills (MIT license)
> Status: Referenced, not installed as plugin. Azure MCP + Foundry MCP already wired in `.mcp.json`.

## What it provides

20 Azure skills + Azure MCP Server (200+ tools) + Foundry MCP. The Azure MCP server is already connected to this workspace — we use `mcp__azure__*` tools throughout sessions.

## Skills that fill IPAI gaps

| Skill | Gap it fills | IPAI-specific context |
|---|---|---|
| `azure-cost-optimization` | No FinOps skill | Use for Azure Sponsorship budget management ($5K credit) |
| `azure-cloud-migrate` | No migration skill | Useful for customer onboarding (migrating from other clouds) |
| `azure-rbac` | RBAC is ad-hoc in runbooks | Use for MI role assignments, customer tenant PAL linking |
| `entra-app-registration` | Entra knowledge scattered | Use for Foundry app registration, Pulser agent Entra IDs |
| `azure-diagnostics` | No diagnostic skill | Use for App Insights + ACA troubleshooting |
| `azure-compliance` | No compliance skill | Use for Purview, Defender, marketplace compliance review |

## Coexistence rule

| Context | Use | Rationale |
|---|---|---|
| Dev-time (Claude Code, VS Code, Cursor) | `microsoft/azure-skills` directly | Dev tools access Azure resources |
| Runtime agents (Pulser on ACA) | `agent-platform` gateway only | Zero-secret agents, allowlist MCP |
| IPAI-specific (Odoo, BIR, PPM) | `odoo-azure-skills` plugin | Domain-specific, not in MS plugin |

## Installation (when ready)

```bash
# Claude Code
claude plugin marketplace add microsoft/azure-skills

# Copilot CLI
/plugin marketplace add microsoft/azure-skills
```

Prereqs: Node 18+, `az login`, `azd auth login`.
