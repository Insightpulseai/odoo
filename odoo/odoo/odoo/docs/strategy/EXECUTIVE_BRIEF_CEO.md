# InsightPulseAI Platform — Executive Brief

## Summary

InsightPulseAI is building a self-hosted, governed, agent-assisted enterprise platform on Azure designed to replace high-cost enterprise SaaS dependence with an owned, extensible operating stack.

The platform uses:

- **Odoo CE 19** as the transactional system of record
- **Azure AI Foundry** as the agent and generative AI runtime
- **Azure Databricks** as the governed data intelligence backbone
- **Azure DevOps + GitHub** as the delivery and portfolio control planes

## Strategic intent

The goal is to achieve enterprise-grade operational maturity without SAP, Salesforce, or ServiceNow licensing by combining open-source foundations, Azure-native controls, and agent-assisted delivery.

## Platform structure

The platform is organized into eight planes:

- **Transactional** — Odoo ERP runtime
- **Control** — Supabase-based control and service surfaces
- **Intelligence** — Databricks, Unity Catalog, medallion pipelines
- **Agent** — Foundry, Agent Framework, MCP
- **Experience** — web apps, extensions, portals
- **Substrate** — Azure landing zones, identity, networking, WAF
- **Automation** — n8n and schedulers
- **Doctrine** — personas, skills, judges, evals, knowledge

## Strategic objectives

The current near-term execution program has seven priorities:

1. Identity baseline
2. Azure DevOps operationalization
3. Foundry runtime hardening
4. Public advisory assistant
5. Automation consolidation
6. OLTP/OLAP separation
7. Observability and security baseline

## Commercial solution direction

The current target portfolio is built around five commercial solution families:

- Customer & Identity Intelligence Fabric
- Campaign Planning / Measurement / Optimization
- Brand, Cultural & Creative Intelligence
- AI Visibility / GEO Intelligence
- Odoo Revenue & Campaign Copilot

## Operating model

The platform uses **shared management with centralized human accountability**.

- Jake is the single accountable human
- Maker agents execute build and implementation work
- Judge agents provide architecture, security, governance, FinOps, and customer-fit review
- Auto-merge is allowed for aligned work
- Human gating is reserved for destructive, RBAC, or topology-sensitive changes

## Current state

As of March 2026:

- 82 Azure resources are live
- 14 resource groups are active
- 12 Container Apps are provisioned
- 2 PostgreSQL Flexible Servers are active
- Azure Front Door + WAF is deployed
- AI Foundry hub + 2 projects exist with a deployed agent
- Databricks workspace with Unity Catalog is in place

The formal strategic objective program has not yet started execution.

## Live-state assessment

- **Engineering-live:** Yellow
- **Platform-live:** Green
- **Edge-live:** Yellow
- **Business-live:** Red

## Immediate next actions

1. Fix Docker runtime contract
2. Start identity baseline
3. Start Azure DevOps operationalization and observability/security baseline in parallel
4. Generate full Odoo whole-landscape architecture
5. Push branch, open PR, merge to main

## Decision summary

- Azure Boards replaces Viva Goals
- OCA-first is mandatory for Odoo
- Custom `ipai_*` modules remain bridge-only
- Databricks prepares governed data
- Foundry consumes governed data for agents and copilots
