# Executive Summary — InsightPulseAI Platform

## What we are building

A self-hosted, governed, agent-assisted enterprise platform on Azure where:

- **Odoo CE 18** is the transactional system of record for ERP, finance, HR, and operations
- **Azure AI Foundry** is the agent and generative AI runtime
- **Azure Databricks** is the governed data intelligence backbone
- **Azure DevOps + GitHub** are the delivery and portfolio control planes

## Why

Replace expensive enterprise SaaS dependence with a self-hosted, cost-disciplined platform we own, govern, and extend through agents, while targeting enterprise-grade operational maturity.

## Platform planes

| Plane | Repo | Runtime |
|---|---|---|
| Transactional | `odoo` | Odoo CE + OCA + thin `ipai_*` bridges on Azure Container Apps + PostgreSQL |
| Control | `platform` | Supabase + ops console + service catalog |
| Intelligence | `data-intelligence` | Databricks + Unity Catalog + medallion pipelines |
| Agent | `agent-platform` | Azure AI Foundry + Agent Framework + MCP |
| Experience | `web` | Next.js portals, browser extensions, marketing site |
| Substrate | `infra` | Azure landing zones, Front Door, Key Vault, identity |
| Automation | `automations` | n8n workflows, schedulers, job runners |
| Doctrine | `agents` | Personas, skills, judges, knowledge, evals |

## Strategic objectives

| # | Objective | Target |
|---|---|---|
| 1 | Identity baseline: Entra ID, MFA, named accounts | Apr 2026 |
| 2 | Azure DevOps operationalization: YAML pipelines, WIF | Apr 2026 |
| 3 | Foundry runtime hardening: production-ready agents | Apr 2026 |
| 4 | Public advisory assistant: zero browser-side secrets | May 2026 |
| 5 | Automation consolidation: 100% inventory, 70% dedup | May 2026 |
| 6 | OLTP/OLAP separation: CDC, medallion, BI publication | May 2026 |
| 7 | Observability and security baseline: App Insights, Defender | Apr 2026 |

## Target solution portfolio

| Solution family | Plane | Inspiration |
|---|---|---|
| Customer & Identity Intelligence Fabric | `data-intelligence` | Smartly.io + Databricks |
| Campaign Planning / Measurement / Optimization | `data-intelligence` | Smartly.io |
| Brand, Cultural & Creative Intelligence | `data-intelligence` + `agent-platform` | Quilt.AI + LIONS |
| AI Visibility / GEO Intelligence | `data-intelligence` | dataintelligence.ro + Quilt.AI |
| Odoo Revenue & Campaign Copilot | `odoo` | Odoo Copilot + Foundry |

## Operating model

**Shared management with centralized human accountability**

- **Jake** is the single accountable human: executive sponsor, architect, governance owner, final approver
- **Maker agents** build: `chief-architect`, `azure-platform`, `odoo-runtime`, `foundry-agent`, `data-intelligence`, `release-ops`
- **Judge agents** review: architecture, security, governance, FinOps, customer-value, TBWA-fit
- **Auto-merge** is allowed for aligned, green work
- **Human gates** apply only to destructive, RBAC, or topology-sensitive changes

## Current state — March 2026

- **82 Azure resources** across **14 resource groups**
- **12 Container Apps** provisioned
- **2 PostgreSQL Flexible Servers** active
- **Azure Front Door + WAF** deployed
- **AI Foundry hub + 2 projects** with deployed agent
- **Databricks workspace** with Unity Catalog
- All 7 strategic objectives are **not yet started**

## Live-state gates

| Gate | Status |
|---|---|
| Engineering-live | Yellow — Docker context drift |
| Platform-live | Green — Azure resources confirmed |
| Edge-live | Yellow — Front Door health unverified |
| Business-live | Red — end-to-end workflow evidence absent |

## Key decisions

- **No Viva Goals** — Azure Boards is the portfolio system of record
- **No SAP / Salesforce / ServiceNow licensing** — capability is built on open source + Azure
- **OCA-first for Odoo** — custom `ipai_*` modules only for bridge behavior
- **Spec-driven SDLC** — spec → maker → judge → pipeline → evidence → monitor
- **Databricks prepares governed data; Foundry consumes it** — complementary, not competing

## Immediate next steps

1. Fix the Docker runtime contract to clear the engineering-live gate
2. Start **OBJ-001** identity baseline
3. Start **OBJ-002** and **OBJ-007** in parallel
4. Generate the full **Odoo Whole-Landscape** target architecture
5. Push branch, create PR, and merge to main

---

*SSOT: `ssot/governance/unified_strategy.yaml` | Org topology: `ssot/repo/org_topology.yaml` | Landing zone: `ssot/azure/landing_zone.yaml`*
