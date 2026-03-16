# Product Requirements Document (PRD): Wholesale SaaS ERP on Azure

## 1. Overview
The **InsightPulse Wholesale SaaS ERP** is an Azure-native, AI-augmented, multi-tenant enterprise resource planning platform tailored for wholesale and distribution operators. By strictly separating transaction processing (Odoo), data intelligence (Databricks), and AI orchestration (Foundry), the platform achieves enterprise-grade scale without drowning the lean operating team in infrastructure complexity.

## 2. Target Audience
- Mid-market wholesale distributors.
- Lean platform engineering teams (solo developers + AI agents).

## 3. Key Capabilities
### 3.1 Fast, Resilient Transactional Core
- Odoo 18+ hosted on Azure Container Apps.
- Modules: Sales Order Management, Purchasing, Inventory, Multi-Warehouse Routing, AP/AR Accounting.
- Strict isolation from AI/Analytical compute constraints.

### 3.2 Automated Intelligence (Lakehouse)
- Medallion architecture inside Azure Databricks (Bronze/Silver/Gold).
- Unified metrics for historical sales forecasting, inventory aging, and financial consolidation.
- Direct BI reporting from the Gold layer.

### 3.3 Azure-Native AI Capability
- Integration with Azure AI Document Intelligence for real-time extraction of emailed Purchase Orders and Vendor Bills.
- Copilot chat and reasoning agents executed via Microsoft Foundry using Anthropic models.
- Agents act identically to human users via API, complete with RBAC constraints.

### 3.4 Multi-Tenant Row-Level Security
- One unified application/database instance serving multiple wholesale tenants.
- Tenant isolation enforced via Odoo's native multi-company architecture and Azure Entra ID token claims.
- Cost-effective for SaaS economics but secure enough for enterprise trust.

## 4. Non-Functional Requirements
- **Performance**: Sub-200ms API response for transactional Odoo writes.
- **Scalability**: Azure Container Apps must scale up instantly based on HTTP queue depth or CPU pressure.
- **Security**: Zero Trust architecture. No permanent secrets; all services use Azure Managed Identities.
- **Traceability**: All prompt executions must be logged to Foundry Tracing/Evals. All infrastructure changes must be driven through Azure DevOps YAML pipelines.
