# Constitution: Wholesale SaaS ERP on Azure

> **Version:** 2.0.0
> **Scope:** Architecture constraints, boundaries, and required standards for the ERP platform.
> **Architecture model:** Six-plane Azure-first

## 1. Architecture Model

The platform follows a **six-plane Azure-first architecture**:

| # | Plane | Scope |
| --- | --- | --- |
| 1 | Governance / Control | Planning, code, release, policy enforcement |
| 2 | Identity / Network / Security | Authentication, edge routing, secrets, API governance |
| 3 | Business Systems | Transactional ERP and workflow automation |
| 4 | Data Intelligence | Governed lakehouse, ML, feature store, BI serving |
| 5 | Agent / AI Runtime | Agent factory, model hosting, tracing, evaluations |
| 6 | Experience / Domain Applications | User-facing surfaces consuming platform services |

Within this model, three systems form the **operational core**:

- **Odoo CE 19** (Business Systems plane) — System of Record for all active transactions.
- **Azure Databricks + ADLS/Delta + Unity Catalog** (Data Intelligence plane) — Canonical system of intelligence. Not optional.
- **Microsoft Foundry** (Agent / AI Runtime plane) — Agent runtime, tracing, evaluations, and monitoring.

## 2. Core Platform Boundaries

- **Transactional System of Record**: Odoo CE 19 running on Azure Container Apps (ACA) with Azure Database for PostgreSQL Flexible Server. Odoo exclusively handles immediate business logic (Sales, Inventory, Purchasing, Accounting, BIR compliance) and is the ultimate truth for active transactions.
- **Intelligence System**: Azure Databricks with Unity Catalog. Analytical workloads, forecasting, and lakehouse storage must never execute within the Odoo PostgreSQL instance. Data must be replicated asynchronously to the lakehouse. Databricks is canonical — not optional or "only for complex transforms."
- **Agentic System**: Microsoft Foundry. All non-deterministic LLM operations, complex reasoning loops, prompt evaluations, and agent tracing belong in Foundry. AI agents must operate as independent microservices consuming Odoo via APIM-governed APIs; they must never directly mutate Odoo transactional data without strict API guardrails.
- **API Gateway**: Azure API Management is the governed ingress/egress and policy boundary. APIM is **not** the system of record. APIM is **not** the agent runtime. It is the governed front door for all cross-tenant routing and API protection.

## 3. Truth Authorities

Plane membership is architectural placement. Truth authority is a separate operational model.

| Authority | System |
| --- | --- |
| Planned truth | Azure Boards |
| Code truth | GitHub |
| Release truth | Azure Pipelines |
| Live inventory truth | Azure Resource Graph |
| Agent/runtime truth | Microsoft Foundry |
| Intended-state truth | Repo SSOT (`ssot/`) |

No plane table may be used as a substitute for this truth-authority model.

## 4. Engineering & Developer Experience

- **Reproducibility**: All local engineering (human and AI agent) must occur inside VS Code `.devcontainer` environments. This guarantees identical toolchains (Azure CLI, Databricks CLI, Terraform).
- **Control Plane**: Azure DevOps (Boards, Pipelines) is the unchallenged planning and release surface. GitHub is the code truth. No deployments bypass Azure Pipelines.

## 5. Tenancy and Isolation

- **Default**: Shared runtime farm + database-per-tenant. Each tenant gets a dedicated PostgreSQL database within a shared ACA environment.
- **Premium/Regulated**: Deployment stamp per tenant with dedicated database.
- **Migration**: Promotion from shared to stamped deployment **must be fully automated**. No manual infrastructure provisioning for tenant tier upgrades.
- **Identity**: Azure Entra ID manages all authentication, RBAC, and B2B identities.

## 6. Integration

- **Gateway**: Azure API Management is the governed front door for all cross-tenant routing and API protection.
- **Eventing**: Azure Service Bus triggers asynchronous cross-boundary workflows (e.g., Odoo -> Databricks, Odoo -> AI Agents).
- **Edge**: Azure Front Door for TLS termination, WAF, and hostname routing.

## 7. Module Policy

- **OCA-first**: CE + OCA is the primary EE parity vehicle.
- **`ipai_*` modules**: Thin bridge/meta/integration glue only. Not a general business capability or EE parity lane.
- **Never**: Modify OCA source, copy OCA files into `addons/ipai/`, or create `ipai_*` replacements for standard business modules.
