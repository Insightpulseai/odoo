# Platform Benchmark Registry

> Version: 1.0.0
> Canonical repo: `agents`

## Purpose
This document catalogs the exact benchmark references and framework samples the platform uses as doctrine. It clarifies what each source should dictate vs. what it should explicitly *not* influence.

## Curated Benchmark Set

| Source | Weight | Use for | Do not use for |
|--------|-------:|---------|----------------|
| **CAF / Landing Zones / Azure Architecture Center** | 1.0 | Platform doctrine, operating model, landing-zone sequencing | Agent/workflow code layout |
| **Microsoft Foundry SDK overview** | 1.0 | Agent-platform SDK choice, endpoint model, auth model, multi-language support | Org-wide repo topology |
| **Microsoft Agent Framework DevUI samples** | 0.9 | Local agent/workflow dev UX, sample folder shape, DevUI-compatible structure | Enterprise platform architecture |
| **Azure/azure-dev (azd)** | 0.8 | Bootstrap, app deployment workflow, `.devcontainer` / `.vscode` / template ergonomics | Landing-zone doctrine |
| **Azure-Samples** | 0.6 | Implementation starters and accelerators, selectively mined | Canonical architecture |
| **Claude Code docs** | 1.0 | Agent operating model, memory/rules/skills, subagents, workflow discipline | Azure topology |
| **A2A** | 0.5 | External agent-to-agent interoperability boundary | Internal repo/team design |
| **Fluent UI / Fluent 2** | 0.8 | Design-system and web component/system patterns | Backend/runtime architecture |
| **Odoo docs / OCA docs** | 1.0 | ERP/runtime/product truth | Azure platform design |
| **Databricks docs** | 1.0 | Data-intelligence workspace, products, pipelines, apps | ERP/runtime structure |

---
*If a component pattern is not covered here, escalate to the `chief-architect` agent lens for derivation.*
