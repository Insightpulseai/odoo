# Wholesale SaaS ERP on Azure: Target Architecture Study

**Date**: March 2026
**Status**: Adopted
**Scope**: Target architecture, operating model, and execution roadmap for a wholesale SaaS ERP built on Azure, using Databricks, Foundry, Azure DevOps, VS Code, and Anthropic.

---

## 1. Executive Summary

### Recommendation
The target state for the Wholesale SaaS ERP must be a **Composited Azure-Native Platform** implementing a strict separation of concerns:
1. **System of Record (ERP Core)**: Containerized transactional Odoo runtime on Azure Container Apps (ACA) with Azure Database for PostgreSQL (Flexible Server).
2. **System of Intelligence (Data)**: Azure Databricks Lakehouse acting as the governed, read-optimized semantic layer and reporting engine, entirely decoupled from the transactional schema.
3. **System of Agency (AI)**: Microsoft Foundry acting as the control plane for Anthropic Claude agents, handling tool orchestration, evaluations, and runtime telemetry.

### Why this Architecture Wins
- **Isolation of Risk**: Transactional integrity is protected from analytical and AI workloads. Databricks handles heavy reads; Foundry handles non-deterministic AI execution.
- **Enterprise Governance**: Azure DevOps provides a rigid structure for planning, CI/CD, and release management, heavily reducing the compliance burden on a lean team.
- **Lean Feasibility**: By leveraging fully managed PaaS/Serverless (ACA, Databricks Serverless, Foundry), a solo developer augmented with AI agents can manage the platform without drowning in Kubernetes cluster administration or raw infrastructure ops.

### Major Tradeoffs
- **Complexity of Integration**: Requires strong eventing (Azure Event Grid/Service Bus) to synchronize the ERP transactional state with Databricks.
- **Cost Floor**: Establishing Azure Databricks, Foundry, and Azure Container Apps establishes a higher baseline consumption cost than a monolithic VM deployment.

---

## 2. Source Map

### Official Docs Used
- **Anthropic Official Docs**: `Claude Context Engineering`, `Agent SDK Overview`, `Tool Use Patterns`. *Used for structuring the non-deterministic reasoning boundaries.*
- **Azure Architecture Center**: `SaaS Tenancy Models`, `Microservices on Azure Container Apps`. *Used for computing the multitenant isolation model.*
- **Microsoft Learn / Well-Architected Framework**: `Reliability`, `Security`, `Cost Optimization`. *Used to validate the PaaS-first approach over raw VMs.*
- **Microsoft Foundry Documentation**: `Project Endpoints`, `Hosted Agents`, `Tracing & Evals`. *Used to define the AI capability layer.*
- **Databricks Architecture Guidance**: `Medallion Architecture`, `Serverless SQL`, `Unity Catalog`. *Used to define the governed data intelligence boundaries.*
- **Azure DevOps Official Docs**: `Release Pipelines`, `Boards vs GitHub Issues`, `Environments`. *Used to define the enterprise SDLC control plane.*

---

## 3. Domain Synthesis

### Anthropic
Anthropic's Claude 3.5/3.7 models require careful context engineering and safe tool boundaries. The Anthropic SDK is ideal for building deterministic agent loops. In an enterprise system, agents must not be embedded deep inside the ERP code; they should exist as distinct microservices calling the ERP via APIs.

### Azure Platform
Azure Container Apps (ACA) is the optimal PaaS for containerized workloads like Odoo, providing the scalability of K8s without the operational overhead. Azure Database for PostgreSQL Flexible Server guarantees transactional ACID compliance. Azure Entra ID and Managed Identities eliminate the need for hardcoded secrets.

### Microsoft Foundry
Foundry is a unified platform for AI model management, agent orchestration, and evaluation. It should sit parallel to the ERP, not inside it. It provides the SDKs and monitoring (tracing, evals) necessary to treat AI prompts as deployable code artifacts.

### Azure Databricks
Databricks is the intelligence layer. Operating the ERP database as a reporting engine leads to resource starvation. The Medallion architecture (Bronze -> Silver -> Gold) isolates ERP raw data, standardizes it, and serves it as governed business semantic models via Unity Catalog.

### VS Code / Engineering Workflow
The local developer loop should rely on VS Code with DevContainers. This guarantees that human and AI agents share the exact same reproducible runtime environment, eliminating "works on my machine" anti-patterns.

### Azure DevOps
Azure DevOps Boards, Repos, and Pipelines provide a unified chain of custody from Strategy -> Epic -> PR -> Release. For an enterprise SaaS ERP, Azure DevOps is superior to GitHub for strict release governance, environment approvals, and Azure-native integration. GitHub can remain the source for open-source syncs, but ADO manages the enterprise delivery.

### SaaS ERP / Wholesale Domain
Wholesale requires heavy domains: Inventory, Purchasing, Sales Orders, Pricing Rules, AR/AP, and Warehouse routing. High transaction volumes mean the ERP must optimize for write-latency, entirely offloading complex margin analysis and forecasting to Databricks.

---

## 4. Target-State Architecture

### Topology
- **Control Plane**: Azure DevOps (CI/CD, Planning), Azure Entra ID (Identity), Azure Policy (Governance).
- **Data Plane / Transactional**: Azure Container Apps (Odoo web/worker containers), Azure PostgreSQL Flexible.
- **Intelligence Plane**: Azure Databricks (Medallion Lakehouse), Azure Data Lake Storage Gen2.
- **Agency Plane**: Microsoft Foundry (Agent endpoints), Azure OpenAI / Anthropic models.

### Boundaries
- **System of Record**: Odoo holds truth for Quotes, Orders, Inventory moves.
- **System of Intelligence**: Databricks holds truth for Financial Consolidation, Sales Forecasting, and historical trend analysis.
- **System of Engagement**: Dedicated Copilot UIs or Odoo native views powered by Foundry API calls.
- **Integration Layer**: Azure API Management (APIM) acting as the gateway for tenant routing; Azure Service Bus for async decoupling.

### Tenant Isolation Strategy
**Shared-DB, Separate-Schema (Row-level security + Schema boundaries).**
For a lean team, database-per-tenant is economically and operationally prohibitive. Using Odoo's native row-level multi-company isolation, backed by strict Entra ID claims, provides the highest density at the lowest operational overhead.

---

## 5. Comparative Decision Matrix

| Option | Strengths | Weaknesses | Risks | Recommended Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **1. Azure-Native Platform with Databricks + Foundry (Chosen)** | Strict boundaries; prevents ERP DB saturation; enterprise AI lifecycle; lean ops | Highest integration complexity; event-driven state sync required | Drift between ERP and Lakehouse schemas if CI/CD fails | Wholesale SaaS at scale with deep AI usage |
| **2. Monolithic ERP with Embedded Anthropic Agents** | Easy to build; zero integration latency | Transactional DB crushed by AI analytics; no trace/eval capabilities | AI hallucinations directly mutating transactional state | Rapid prototyping or internal tooling only |
| **3. Container-per-Tenant ERP + GitHub Actions** | Perfect data isolation; easy tenant deletion | Infrastructure bloat; deployment storms; expensive | Costs scale linearly with tenants; lean team will drown in ops | Highly regulated industries with data residency mandates |

---

## 6. Recommended Reference Architecture

- **Identity**: Azure Entra ID multi-tenant app registrations; Managed Identity (UMI) exclusively for resource-to-resource auth.
- **Networking**: Azure Virtual Network (VNet) injection for ACA and Databricks.
- **Edge**: Azure Front Door (WAF + CDN + Global Routing).
- **App Hosting**: Azure Container Apps (scale-to-zero for workers, dedicated profiles for heavy compute).
- **Database**: Azure Database for PostgreSQL Flexible Server.
- **Integration**: Azure Service Bus for ERP -> Databricks ETL and ERP -> Agent triggers.
- **Observability**: Azure Monitor + Application Insights + Foundry Tracing.
- **Secrets**: Azure Key Vault via Managed Identity.
- **CI/CD**: Azure DevOps YAML Pipelines using Bicep/Terraform for infrastructure.
- **Agent Runtime**: Microsoft Foundry Hosted Agents using Python SDK.
- **Document Intelligence**: Azure AI Document Intelligence for wholesale OCR (Invoices, POs).

---

## 7. Wholesale SaaS ERP Capability Map

| Capability | System Boundary | Data Ownership | AI / Agent Opportunity |
| :--- | :--- | :--- | :--- |
| **Sales Order Mgmt** | Odoo | Odoo (SoR) | Chat-to-cart, margin negotiation Copilots |
| **Inventory & Fulfillment** | Odoo | Odoo (SoR) | Optimal pick-path routing, predictive restock |
| **Procurement** | Odoo | Odoo (SoR) | Automated PO generation based on Min/Max rules |
| **Document Workflows** | Azure AI DocIntel | Odoo/Blob | Vendor bill OCR, inbound PO extraction |
| **BI & Analytics** | Databricks | Lakehouse | Natural language querying over sales history |
| **Copilot Operations** | Foundry | Foundry (State) | Cross-module reasoning, exception handling |

---

## 8. Foundry vs Databricks vs Anthropic Role Clarification

| Platform | Best For | Must Avoid | Interoperation |
| :--- | :--- | :--- | :--- |
| **Anthropic (Model)** | Complex reasoning, document parsing, coding. | Storing data, raw DB execution. | Hosted in Azure / called via API. |
| **Microsoft Foundry** | Orchestrating models, prompt management, tracing, enterprise RBAC. | Executing heavy data transformations. | Orchestrates Anthropic models; provides API to Odoo. |
| **Azure Databricks** | Massive analytical processing, ML training, unified SQL/governance. | Transactional state mutation (OLTP). | Feeds analytics context to Foundry agents. |

---

## 9. Azure DevOps and VS Code Operating Model

- **Planning**: Azure Boards (Epics -> Features -> PBIs/Tasks).
- **Repo Strategy**: Monorepo or strictly bounded multi-repo (e.g., `infra`, `erp`, `intelligence`, `agents`).
- **Environments**: Dev -> UAT -> Prod. Gated by ADO Environment Approvals.
- **Dev Workflow**: VS Code + `.devcontainer`. The container installs tooling (az cli, databricks cli, terraform, odoo reqs).
- **Agentic Engineering**: AI Agents operate locally inside the devcontainer, or via GitHub/ADO Pull Requests to review code against the Constitution.

---

## 10. Risks, Anti-patterns, and Failure Modes

- **Anti-pattern**: Over-centralizing AI inside the transactional ERP. Causes compute saturation and makes upgrading the ERP impossible.
- **Anti-pattern**: Using Databricks as the transactional core. Parquet/Delta lakes are not meant for single-row ACID OLTP updates.
- **Risk**: Tool sprawl. Trying to use GitHub Projects, Azure Boards, and physical whiteboards simultaneously. *Mitigation: Azure Boards is the absolute SSOT.*
- **Risk**: Governance too heavy. Trying to implement full ITIL change-management. *Mitigation: Automate controls inside Azure DevOps YAML pipelines.*

---

## 11. Phased Roadmap

### Phase 0: Foundations
- **Objective**: Establish Azure Landing Zones, Entra ID, Azure DevOps, and VS Code DevContainers.
- **Exit Criteria**: Fully automated ALZ deployment via CI/CD.

### Phase 1: MVP Transactional ERP
- **Objective**: Deploy Odoo to ACA with PostgreSQL.
- **Exit Criteria**: Wholesalers can create inventory, sales orders, and invoices securely backing to a shared-schema DB.

### Phase 2: Intelligence & Analytics
- **Objective**: Establish Databricks Lakehouse. Set up ETL from Odoo Postgres -> Bronze -> Silver -> Gold.
- **Exit Criteria**: Dashboards operational with unified governed metrics.

### Phase 3: Copilots and AI Factory
- **Objective**: Deploy Microsoft Foundry. Integrate Document Intelligence for OCR and Anthropic agents for complex workflows.
- **Exit Criteria**: Odoo users can parse inbound PDFs into POs via AI pipelines.

### Phase 4: Enterprise Scale
- **Objective**: Multi-tenant hardening, global edge replication, DR testing.
- **Exit Criteria**: Platform is resilient to regional failure and compliant with enterprise SLA.

---

## 12. Final Recommendation & Action List

### Recommendation
Adopt the **Composited Azure-Native Platform**. Keep Odoo strictly bounded to OLTP, Databricks strictly bounded to OLAP, and Foundry strictly bounded to AI Orchestration. Drive all engineering via Azure DevOps + VS Code DevContainers.

### Build Now / Defer / Avoid
| Category | Decision | Justification |
| :--- | :--- | :--- |
| **Azure DevContainers** | BUILD NOW | Prevents environment drift for the solo developer + agents. |
| **Azure DevOps Pipelines** | BUILD NOW | CI/CD automation is life support for a lean team. |
| **Databricks Lakehouse** | DEFER | Build the transactional ERP first. Lakehouse requires active data gravity. |
| **Database-per-Tenant** | AVOID | Will crush a solo developer with operational and migration complexity. |
| **Embedded Custom LLM code** | AVOID | Push all AI integration through Foundry SDKs. |

### Top 10 Action List
1. Lock Azure DevOps as the SSOT for planning and CI/CD.
2. Publish DevContainer definitions for Odoo and Infra development.
3. Deploy Azure Landing Zone foundational Bicep/Terraform.
4. Establish Azure API Management as the perimeter gateway.
5. Deploy Odoo onto Azure Container Apps.
6. Configure Azure PostgreSQL Flexible with connection pooling.
7. Setup Azure Service Bus for decoupling outbound ERP events.
8. Initialize Azure Databricks workspace (deferred to Phase 2).
9. Initialize Microsoft Foundry workspace.
10. Map out Entra ID App Roles for multi-tenant isolation.
