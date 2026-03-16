# Constitution: Wholesale SaaS ERP on Azure

> **Version:** 1.0.0
> **Scope:** Architecture constraints, boundaries, and required standards for the ERP platform.

## 1. Core Platform Boundaries
- **Transactional System of Record**: Odoo running on Azure Container Apps (ACA) with Azure Database for PostgreSQL Flexible Server. Odoo exclusively handles immediate business logic (Sales, Inventory, Purchasing) and is the ultimate truth for active transactions.
- **Intelligence System**: Azure Databricks with Unity Catalog. Analytical workloads, forecasting, and lakehouse storage must never execute within the Odoo PostgreSQL instance. Data must be replicated asynchronously to the Lakehouse.
- **Agentic System**: Microsoft Foundry. All non-deterministic LLM operations, complex reasoning loops, and prompt evaluations belong in Foundry. AI agents must operate as independent microservices consuming Odoo via APIs; they must never directly mutate Odoo transactional data without strict API guardrails.

## 2. Engineering & Developer Experience
- **Reproducibility**: All local engineering (human and AI agent) must occur inside VS Code `.devcontainer` environments. This guarantees identical toolchains (Azure CLI, Databricks CLI, Terraform).
- **Control Plane**: Azure DevOps (Boards, Repos, Pipelines) is the unchallenged Single Source of Truth for planning, CI/CD, and release gating. No deployments bypass Azure Pipelines.

## 3. Tenancy and Isolation
- **Row-Level Security**: The ERP maintains a shared-database, separate-schema (or row-level multi-company) tenancy model to keep infrastructure costs and operational overhead feasible for a lean team.
- **Identity**: Azure Entra ID manages all authentication, RBAC, and B2B identities.

## 4. Integration
- **Gateway**: Azure API Management (APIM) is the front door for all cross-tenant routing and API protection.
- **Eventing**: Azure Service Bus triggers asynchronous cross-boundary workflows (e.g., Odoo -> Databricks, Odoo -> AI Agents).
