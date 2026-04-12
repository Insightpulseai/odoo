# Azure Platform Overview

> Canonical reference for the InsightPulseAI six-plane Azure architecture.

## Purpose

This document describes the platform's logical architecture at the **overview** level. It maps every canonical runtime service to one of six planes, defines truth-plane ownership, and separates implementation targets from benchmark references.

## Diagram

![Azure Platform Overview](diagrams/azure-platform-overview.png)

**Source:** [`azure-platform-overview.drawio`](diagrams/azure-platform-overview.drawio) (editable in [app.diagrams.net](https://app.diagrams.net))

## Six-Plane Model

| # | Plane | Purpose | Key Services |
|---|-------|---------|--------------|
| 1 | **Governance / Control** | Planning, code, release, inventory, intended-state | Azure Boards, GitHub, Azure Pipelines, Resource Graph, Repo SSOT |
| 2 | **Identity / Network / Security** | AuthN/AuthZ, edge routing, secrets, networking | Cloudflare DNS, Azure Front Door/WAF, Entra ID, Key Vault, Managed Identities, VNet |
| 3 | **Business Systems** | Transactional core, automation, project management | Odoo CE 18 (ACA), PostgreSQL Flexible Server, n8n (ACA), Plane (ACA), Superset (ACA) |
| 4 | **Data Intelligence** | Governed data products, analytics, BI | Databricks, ADLS/Delta Lake, Unity Catalog, Microsoft Fabric |
| 5 | **Agent / AI Runtime** | Agent hosting, document processing, orchestration | Microsoft Foundry, Document Intelligence, Logic Apps, Azure Functions |
| 6 | **Experience / Domain Apps** | User-facing surfaces, APIs, browser tools | Odoo UI, Domain Workbenches, FastAPI/JSON-RPC, web/ apps |

## Truth Authorities (6 canonical)

Six governance-level truth authorities. No authority may silently replace another.

| Truth Authority | Authoritative System | What It Owns |
|-----------------|---------------------|--------------|
| Planned truth | Azure Boards | Epics, features, OKRs, sprint plans |
| Code truth | GitHub | Source code, PRs, branch state |
| Release truth | Azure Pipelines | Build/deploy status, promotion gates |
| Live inventory truth | Azure Resource Graph | Actual Azure resource state, drift detection |
| Agent/runtime/eval truth | Microsoft Foundry | Agent definitions, tool catalog, evals, traces |
| Intended-state truth | Repo SSOT | `ssot/` YAML files, architecture docs, contracts |

### Domain Systems / Evidence Artifacts

These are operational systems of record or evidence artifacts — not governance-level truth authorities.

| System | Role | Classification |
|--------|------|----------------|
| Odoo | Transactional system of record | Domain system |
| Databricks + Fabric | Analytical system of record | Domain system |
| Document Intelligence | Extraction pipeline | Domain system |
| Runtime Evidence | Audit trail | Evidence artifact |
| Architecture diagrams | Generated renders | Evidence artifact |
| Validation outputs | CI evidence | Evidence artifact |

## Core Runtime Services

### Edge / Controls

- **Cloudflare DNS** — authoritative DNS for `insightpulseai.com`, delegated from Spacesquare
- **Azure Front Door** (`ipai-fd-dev`) — WAF, TLS termination, routing to all ACA origins
- **Microsoft Entra ID** — target IdP (Keycloak is transitional)
- **Azure Key Vault** (`kv-ipai-dev`) — all runtime secrets via managed identity
- **Managed Identities** — workload identity federation, no stored credentials

### Business Systems

- **Odoo CE 18** — 3 ACA containers (web, worker, cron) in `rg-ipai-dev`
- **Azure PostgreSQL Flexible Server** (`ipai-odoo-dev-pg`) — Odoo transactional database
- **n8n** — ACA, automation workflows, Plane ↔ Odoo command sync
- **Plane** — ACA, project management, command surface only (not co-authoritative with Odoo)
- **Superset** — ACA, BI dashboards

### Data Intelligence

- **Databricks** (`dbw-ipai-dev`) — JDBC extract from PostgreSQL, DLT pipelines
- **ADLS / Delta Lake** — medallion architecture (bronze → silver → gold → platinum)
- **Unity Catalog** — governed data access layer
- **Microsoft Fabric** — database mirroring from PostgreSQL, BI semantic models

### Agent / AI Runtime

- **Microsoft Foundry** — agent hosting, identity lifecycle, MCP/A2A, evals
- **Document Intelligence** (`docai-ipai-dev`) — OCR, form recognition
- **Logic Apps** — cross-service orchestration
- **Azure Functions** — serverless compute for event-driven workloads

## Tenant-Context Propagation

All requests flow through Azure Front Door, which terminates TLS and routes to ACA origins. Identity context propagates via:

1. **External users** — Entra ID → OIDC token → ACA → Odoo session
2. **Agents** — Foundry managed identity → API key/OAuth2 → Odoo FastAPI
3. **Data pipelines** — Managed identity → JDBC → PostgreSQL → Databricks
4. **Secrets** — Managed identity → Key Vault → env vars (never plaintext in config)

## Scope Boundaries

### In scope (canonical implementation targets)

All services shown in the diagram — these are committed implementation targets with Azure resource backing.

### Out of scope (benchmark-only references)

The following are **reference benchmarks** used for capability mapping, not runtime dependencies:

- SAP on Azure, Concur, AvaTax
- Smartly.io, Quilt.AI, LIONS
- DataIntelligence.ro, fal.ai, Odoo.sh

These must never appear as boxes in the canonical architecture diagram.

## Rendering Contract

| Item | Value |
|------|-------|
| Source | `docs/architecture/diagrams/azure-platform-overview.drawio` |
| Render | `docs/architecture/diagrams/azure-platform-overview.png` |
| Export | `./scripts/docs/export_drawio.sh` |
| CI check | `.github/workflows/diagram-drift-check.yml` |
| Registry | `ssot/architecture/diagram_catalog.yaml` |

The `.png` is a derived artifact. Edit the `.drawio` source, run the export script, commit both.

## Next Diagram

The next artifact should be `azure-platform-high-level.drawio` — showing resource groups, environments, shared/workload boundaries, and monitoring placement. Do not create low-level deployment diagrams until the high-level layer is complete.
