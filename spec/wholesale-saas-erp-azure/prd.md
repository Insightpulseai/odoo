# Product Requirements Document (PRD): Wholesale SaaS ERP on Azure

## 1. Overview

The **InsightPulse Wholesale SaaS ERP** is an Azure-native, AI-augmented, multi-tenant enterprise resource planning platform tailored for wholesale and distribution operators. It follows a **six-plane Azure-first architecture** where Odoo CE 19 serves as the transactional system of record, Azure Databricks + ADLS/Delta + Unity Catalog serves as the governed data intelligence core, and Microsoft Foundry serves as the agent factory and hosted agent runtime plane.

## 2. Target Audience

- Mid-market wholesale distributors.
- Lean platform engineering teams (solo developers + AI agents).

## 3. Key Capabilities

### 3.1 Fast, Resilient Transactional Core

- Odoo CE 19 hosted on Azure Container Apps.
- Modules: Sales Order Management, Purchasing, Inventory, Multi-Warehouse Routing, AP/AR Accounting.
- Strict isolation from AI/Analytical compute constraints.
- Module policy: CE + OCA is the primary EE parity vehicle; `ipai_*` modules are thin bridge/meta only.

### 3.2 Automated Intelligence (Lakehouse)

- Lakeflow Spark Declarative Pipelines (SDP) inside Azure Databricks.
- Unified metrics for historical sales forecasting, inventory aging, and financial consolidation.
- Direct BI reporting from the Gold layer.
- Databricks + ADLS/Delta + Unity Catalog is the canonical data intelligence core (not optional).

### 3.3 Azure-Native AI Capability

- Integration with Azure AI Document Intelligence for real-time extraction of emailed Purchase Orders and Vendor Bills.
- Copilot chat and reasoning agents executed via Microsoft Foundry using Anthropic models.
- Agents act identically to human users via APIM-governed API, complete with RBAC constraints.
- All agent operations traced and evaluated via Foundry tracing/evals pipeline.

### 3.4 Multi-Tenant Isolation

- Default: shared runtime farm + database-per-tenant to keep infrastructure costs feasible for a lean team.
- Premium/regulated: deployment stamp per tenant with dedicated database.
- Tenant isolation enforced via Odoo's native multi-company architecture and Azure Entra ID token claims.
- Automated promotion from shared to stamped deployment (no manual provisioning for tier upgrades).

## 4. Non-Functional Requirements

- **Performance**: Sub-200ms API response for transactional Odoo writes.
- **Scalability**: Azure Container Apps must scale up instantly based on HTTP queue depth or CPU pressure.
- **Security**: Zero Trust architecture. No permanent secrets; all services use Azure Managed Identities.
- **Traceability**: All prompt executions must be logged to Foundry Tracing/Evals. All infrastructure changes must be driven through Azure DevOps YAML pipelines.
- **Governance**: Six-plane architecture with explicit truth-authority model (Azure Boards = planned truth, GitHub = code truth, Azure Pipelines = release truth, Azure Resource Graph = live inventory truth, Microsoft Foundry = agent/runtime truth, repo SSOT = intended-state truth).
