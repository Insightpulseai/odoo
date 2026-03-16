# Platform Benchmark Registry

> Version: 2.0.0
> Curated benchmark sources for the InsightPulse AI platform.
> Weight: 1.0 = canonical doctrine, 0.5 = reference only, 0.0 = retired.

| Source | Weight | Influences | Must not influence |
|---|---|---|---|
| CAF / Landing Zones / Azure Architecture Center | 1.0 | Platform doctrine, operating model, landing-zone sequencing | Agent/workflow code layout |
| Microsoft Foundry SDK overview | 1.0 | agent-platform SDK choice, endpoint model, auth model | Top-level repo topology |
| Claude Code docs (best practices, workflows, teams) | 1.0 | Agent operating model, memory/rules/skills, subagents | Azure topology |
| Odoo docs / OCA docs | 1.0 | ERP/runtime/product truth | Azure platform design |
| Databricks docs | 1.0 | data-intelligence workspace, products, pipelines | ERP/runtime structure |
| Azure DevOps Boards + CLI | 1.0 | Portfolio SoR, work items, sprints, portfolio backlogs | Repo topology |
| Foundry VS Code extension guide | 0.95 | Learning path design, project onboarding | Repo topology |
| Azure DevOps MCP Server | 0.95 | Agent access to Boards/PRs/builds/tests | SSOT structure |
| Agent Framework DevUI samples | 0.9 | Local agent/workflow dev UX, sample folder shape | Enterprise platform architecture |
| Azure/azure-dev (azd) | 0.8 | Bootstrap, app deployment, template ergonomics | Landing-zone doctrine |
| Fluent UI / Fluent 2 | 0.8 | Design system and web component patterns | Backend/runtime architecture |
| Azure-Samples | 0.6 | Implementation starters and accelerators (selectively mined) | Canonical architecture |
| A2A (Google/Linux Foundation) | 0.5 | External agent-to-agent interop boundary | Internal repo/team design |
| SuperClaude Framework | 0.4 | Command packs, persona design inspiration | Canonical doctrine (not Anthropic-endorsed) |
| SAP-on-Azure Landing Zone Accelerator | 0.85 | Landing zone design areas adapted for Odoo-on-Azure | SAP-specific components (HANA, BW, Fiori) |
| Viva Goals | 0.0 | **RETIRED Dec 2025 — do not use** | Everything |

## Policy

- Sources at weight >= 0.8 may shape architecture and operating model
- Sources at weight 0.5-0.7 are implementation cookbooks only
- Sources at weight < 0.5 are optional inspiration
- No source overrides CAF, landing-zone doctrine, or the target repo architecture
- **Azure Boards replaces Viva Goals permanently** — no OKR system outside Boards

## Individual benchmark files

- [azure-devops-mcp-server.md](azure-devops-mcp-server.md)
- [foundry-vscode-guided-learning.md](foundry-vscode-guided-learning.md)
- [prepare-people-devui-foundry.md](prepare-people-devui-foundry.md)
