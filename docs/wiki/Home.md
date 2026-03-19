# InsightPulse AI Platform

Welcome to the **ipai-platform** Azure DevOps project.

This project is the canonical control surface for planning, release governance, and execution visibility across the InsightPulse AI platform.

---

## Purpose

**ipai-platform** exists to coordinate delivery of an Azure-first platform where:

- **Odoo CE 19** is the transactional business system and system of record
- **Azure PostgreSQL** is the primary Odoo database layer
- **Databricks** is the governed intelligence and lakehouse layer
- **Microsoft Foundry / Azure AI** is the agent, copilot, and evaluation runtime
- **Supabase** is the platform/control-plane and app-backend layer for auth, metadata, workflow state, vector memory, and bounded backend services
- **n8n** is the automation and workflow orchestration layer for event-driven integration and operational flows
- **Azure DevOps** provides planning and release governance
- **GitHub** provides source control and pull request truth
- **SSOT files and runtime evidence** provide intended-state and live-state authority

This project is not a placeholder. It is the operating project for platform execution.

---

## Authority Model

The platform uses explicit truth boundaries.

| Authority | System |
|-----------|--------|
| Planned truth | Azure Boards |
| Code truth | GitHub |
| Release truth | Azure Pipelines |
| Live Azure inventory / drift truth | Azure Resource Graph |
| Agent runtime / eval truth | Microsoft Foundry |
| Intended-state truth | Repo SSOT (`ssot/`) |
| Transactional business truth | Odoo |
| Analytical intelligence truth | Databricks lakehouse |

**Key rule:** No single tool replaces all others. Planning, code, release, runtime, and transactional authority remain intentionally separated.

---

## Target Architecture

InsightPulse AI follows a **six-plane Azure-first architecture**.

| Plane | Scope |
|-------|-------|
| **Governance / Control** | Azure Boards, Azure Pipelines, policy, planning, release control |
| **Identity / Network / Security** | Entra ID, RBAC, Key Vault, managed identities, Front Door, WAF, private networking |
| **Business Systems** | Odoo CE 19, PostgreSQL, operational workflows, finance, projects, approvals |
| **Data Intelligence** | Databricks, ADLS/Delta, Unity Catalog, governed analytics, ML features, context products |
| **Agent / AI Runtime** | Foundry, copilot runtime, evaluations, tracing, bounded agent actions |
| **Experience / Domain Applications** | Public web, ops/admin surfaces, copilots, portals, dashboards, Supabase-backed app services, n8n-driven automation surfaces |

---

## What This Project Owns

**ipai-platform owns:**

- Azure Boards portfolio and execution backlog
- Release and deployment governance
- Platform architecture and operating model references
- Delivery coordination across repos and planes
- Backlog structure for:
  - Platform foundation
  - ERP parity
  - AI / copilot / agent runtime
  - Data intelligence
  - Developer experience
  - Security / compliance
  - Revenue / GTM packaging

## Core Tech Stack

- **Odoo CE 19 + OCA + thin `ipai_*` bridges** -- transactional ERP and operational workflows
- **Azure Database for PostgreSQL Flexible Server** -- Odoo database layer
- **Databricks + ADLS/Delta + Unity Catalog** -- lakehouse, analytics, and governed intelligence
- **Microsoft Foundry / Azure AI** -- agent runtime, copilots, tracing, and evaluation
- **Power BI** -- semantic consumption and reporting layer (Fabric optional)
- **Supabase** -- platform/control-plane backend for auth, metadata, workflow state, vector memory, and bounded app services
- **n8n** -- workflow automation and orchestration
- **Azure Front Door + Cloudflare DNS** -- public edge and DNS authority
- **Azure DevOps + GitHub** -- planning, code, and release governance
- **Fluent UI (React v9 default, Web Components selectively)** -- canonical design system foundation for web, platform, and agent-facing surfaces
- **`design` repo** -- shared tokens, wrappers, shell primitives, and Fluent-aligned UI contracts
- **Key Vault + Entra ID + managed identities** -- security and access control

## Boundary Notes

- **Odoo** remains the transactional system of record
- **Databricks** remains the system of intelligence
- **Foundry** remains the agent/runtime and evaluation plane
- **Supabase** is not the transactional SoR and not the lakehouse; it is the platform/control-plane and app-backend layer
- **n8n** is orchestration and automation only; it is not a system of record
- **Power BI** is the semantic consumption layer; Fabric is optional expansion, not the data-intelligence core
- **Fluent UI** is the design system foundation; the `design` repo owns tokens and shared components; application repos consume, not redefine
- **Odoo** stays native for ERP surfaces; Fluent is used selectively for embedded widgets or brand alignment, not full UI replacement

**This project does not replace:**

- GitHub repos
- Odoo operational records
- Databricks data products
- Runtime evidence in platform-specific systems

---

## Desired End State

This project reaches its desired state when all of the following are true.

### 1. Boards is trustworthy

- Epics have clear scope and descriptions
- Issues are parented correctly
- Stale/test/orphan items are removed
- States reflect reality
- Major workstreams are linked to specs, repos, and delivery evidence

### 2. Repos and pipelines are operational

- Connected codebases are active
- PR validation is running
- Deployment stages exist and are visible
- Commits and PRs reference `AB#...` work items

### 3. Wiki explains the platform clearly

- Architecture
- Repo boundaries
- Release model
- Environment model
- Planning model
- Go-live and rollback references

### 4. Core runtime is stable

- Odoo on Azure is healthy
- Identity/security baseline is in place
- Observability is active
- PostgreSQL ownership is unambiguous
- Front Door / DNS / edge model is governed

### 5. Strategic lanes are active

- ERP parity work is tracked
- Databricks lakehouse is active
- Foundry / copilot work is bounded and governed
- Expense / OCR / finance PPM work is modeled
- Odoo Projects to Azure Boards integration is bounded and documented

### 6. Go-live readiness is evidence-based

- Release flow exists
- Rollback path exists
- Backup / restore path exists
- Readiness can be demonstrated from evidence, not assumptions

---

## Delivery Principles

### Boards-first planning

All material platform work should exist in Azure Boards as Epic, Issue, or Task.

### Repo-first implementation

Implementation happens in the owning repo, not in Azure DevOps Repos by default.

### Evidence-backed progress

Work item status should reflect real implementation evidence, not intention.

### Bounded integration

Cross-system writes must be governed. No analytics or agent layer may silently override transactional authority.

### Odoo-wins execution rule

Where Odoo Projects syncs to Azure Boards:

- Azure Boards remains planning truth
- Odoo remains execution truth
- Synced operational fields are bounded
- Conflict resolution favors Odoo for execution fields

---

## Active Workstream Categories

| Category | Key Areas |
|----------|-----------|
| **Platform Foundation** | Identity baseline, Azure DevOps operationalization, observability, Key Vault, Zero Trust |
| **ERP / Odoo** | Runtime stabilization, OCA parity, finance PPM, expense automation, approvals, OCR |
| **AI / Copilot / Agents** | Odoo Copilot, Foundry integration, bounded actions, guided learning, agent registry |
| **Data Intelligence** | Databricks activation, Unity Catalog, OLTP/OLAP separation, lakehouse data products |
| **Developer Experience** | Devcontainer parity, VS Code workspace, contract checks, release ergonomics |
| **Revenue / GTM** | Solution packaging, demo assets, communications, commercialization lanes |

---

## Key Project Rules

1. Azure Boards is the planning truth
2. GitHub is the code truth
3. Azure Pipelines is the release truth
4. Odoo is the transactional system of record
5. Databricks is the intelligence plane
6. Foundry is the agent runtime plane
7. Fabric / Power Platform / portal templates may inform implementation, but do not silently become canonical architecture
8. Bicep is the canonical Azure IaC path
9. Managed identity is preferred over static credentials wherever possible

---

## Wiki Pages

- [Architecture Overview](Architecture-Overview)
- [Authority Model](Authority-Model)
- [Environment Map](Environment-Map)
- [Repo Ownership Map](Repo-Ownership-Map)
- [Azure Boards Operating Model](Azure-Boards-Operating-Model)
- [Pipeline and Release Model](Pipeline-and-Release-Model)
- [Identity and Access Model](Identity-and-Access-Model)
- [Databricks and Lakehouse Model](Databricks-and-Lakehouse-Model)
- [Odoo Runtime and Parity Model](Odoo-Runtime-and-Parity-Model)
- [Go-Live Checklist](Go-Live-Checklist)
- [Rollback and Recovery](Rollback-and-Recovery)
- [Finance PPM Operating Model](Finance-PPM-Operating-Model)

---

## Quick Start for Team Members

1. Review the authority model above
2. Open Azure Boards and find your work item
3. Verify the owning repo and spec bundle
4. Implement in GitHub with `AB#...` linkage
5. Use Azure Pipelines for governed deployment
6. Update status only when evidence exists

---

## Project Summary

**ipai-platform** is the canonical Azure DevOps project for InsightPulse AI. It provides the planning and release spine for an Azure-first platform where Odoo is the business system of record, Databricks is the governed intelligence layer, Foundry is the agent/runtime layer, Supabase provides platform/control-plane backend capabilities, and n8n provides workflow automation and orchestration.

The goal is a clean, evidence-backed, production-ready delivery model — not a placeholder project, and not a duplicate of runtime truth elsewhere.
