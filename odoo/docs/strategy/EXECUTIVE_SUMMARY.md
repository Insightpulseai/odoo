# Executive Summary — InsightPulse AI Platform

## What we are building

A self-hosted, governed, agent-assisted enterprise platform on Azure where:

- **Odoo CE 19** is the transactional system of record (ERP, finance, HR, operations)
- **Azure AI Foundry** is the agent and generative AI runtime
- **Azure Databricks** is the governed data intelligence backbone
- **Azure DevOps + GitHub** are the delivery and portfolio control planes

## Why

Replace expensive enterprise SaaS (SAP, Salesforce, ServiceNow) with a self-hosted, cost-minimized stack that we own, govern, and extend through agents — while matching or exceeding enterprise operational maturity.

## Platform planes (8)

| Plane | Repo | Runtime |
|---|---|---|
| Transactional | `odoo` | Odoo CE + OCA + ipai bridges on Azure Container Apps + PostgreSQL |
| Control | `platform` | Supabase + ops console + service catalog |
| Intelligence | `data-intelligence` | Databricks + Unity Catalog + medallion pipelines |
| Agent | `agent-platform` | Azure AI Foundry + Agent Framework + MCP |
| Experience | `web` | Next.js portals, browser extensions, marketing site |
| Substrate | `infra` | Azure landing zones, Front Door, Key Vault, identity |
| Automation | `automations` | n8n workflows, schedulers, job runners |
| Doctrine | `agents` | Personas, skills, judges, knowledge, evals |

## Strategic objectives (7, sequenced)

| # | Objective | Target |
|---|---|---|
| 1 | Identity baseline (Entra ID, MFA, named accounts) | Apr 2026 |
| 2 | Azure DevOps operationalization (YAML pipelines, WIF) | Apr 2026 |
| 3 | Foundry runtime hardening (production-ready agents) | Apr 2026 |
| 4 | Public advisory assistant (zero browser-side secrets) | May 2026 |
| 5 | Automation consolidation (100% inventory, 70% dedup) | May 2026 |
| 6 | OLTP/OLAP separation (CDC, medallion, BI publication) | May 2026 |
| 7 | Observability + security baseline (App Insights, Defender) | Apr 2026 |

## Target solution portfolio (5 commercial families)

| Solution | Plane | Inspiration |
|---|---|---|
| Customer & Identity Intelligence Fabric | data-intelligence | Smartly.io + Databricks |
| Campaign Planning/Measurement/Optimization | data-intelligence | Smartly.io |
| Brand, Cultural & Creative Intelligence | data-intelligence + agent-platform | Quilt.AI + LIONS |
| AI Visibility / GEO Intelligence | data-intelligence | dataintelligence.ro + Quilt.AI |
| Odoo Revenue & Campaign Copilot | odoo | Odoo Copilot + Foundry |

## Operating model

**Shared management with centralized human accountability.**

- One human (Jake) = executive sponsor, architect, governance owner, final approver
- Maker agents = build (chief-architect, azure-platform, odoo-runtime, foundry-agent, data-intelligence, release-ops)
- Judge agents = review (architecture, security, governance, finops, customer-value, tbwa-fit)
- Auto-merge for aligned work; human gate only for destructive/RBAC/topology changes

## Current state (Mar 2026)

- **82 Azure resources** live across 14 resource groups
- **12 Container Apps** provisioned (Odoo web/worker/cron + 8 services)
- **2 PostgreSQL Flexible Servers** active
- **Azure Front Door + WAF** deployed
- **AI Foundry hub + 2 projects** with deployed agent
- **Databricks workspace** with Unity Catalog
- All 7 strategic objectives: **not yet started**

## Live-state gates

| Gate | Status |
|---|---|
| Engineering-live (local dev works) | Yellow — Docker context drift |
| Platform-live (Azure resources exist) | Green — 82 resources confirmed |
| Edge-live (Front Door reaches origin) | Yellow — health unverified |
| Business-live (end-to-end workflow) | Red — no evidence yet |

## Key decisions

- **No Viva Goals** (retired Dec 2025) — Azure Boards is portfolio SoR
- **No SAP/Salesforce licensing** — build equivalent on open-source + Azure
- **OCA-first** for Odoo modules — custom ipai_* only for bridges
- **Spec-driven SDLC** — spec → maker → judge → pipeline → evidence → monitor
- **Databricks prepares data, Foundry consumes it** — sequential, not competing

## What's next

1. Fix Docker runtime contract (engineering-live gate)
2. Start OBJ-001 (identity baseline)
3. Start OBJ-002 + OBJ-007 in parallel (AzDo + observability)
4. Generate the full Odoo Whole-Landscape architecture (spec bundle ready)
5. Push branch, create PR, merge to main

---

*SSOT: `ssot/governance/unified_strategy.yaml` | Org topology: `ssot/repo/org_topology.yaml` | Landing zone: `ssot/azure/landing_zone.yaml`*
