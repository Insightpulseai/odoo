# Epic: Wholesale SaaS ERP Azure Implementation (Top 10 Actionable Insights)

**Description:**
This Epic tracks the top 10 actionable insights and immediate next steps derived from the Wholesale SaaS ERP Azure Architecture deep research. This establishes the composited platform across Odoo (Transactional), Databricks (Intelligence), and Microsoft Foundry (AI/Agentic).

---

## 🏗️ Phase 0: Foundations & DevUx
- [x] **1. Lock the Control Plane:** Mandate Azure DevOps as the absolute single source of truth for planning (Boards) and CI/CD (Pipelines). Transition away from fragmented issue tracking.
- [x] **2. Standardize the Dev Loop:** Publish `.devcontainer` definitions for both Odoo development and Azure Infrastructure development to guarantee AI agent and human developer determinism.
- [ ] **3. Deploy the Landing Zone:** Execute the foundational Azure Landing Zone (ALZ) Bicep/Terraform code to establish VNets, Entra ID, and Log Analytics.

## ⚡ Phase 1: MVP Transactional Core (System of Record)
- [ ] **4. Deploy the Transactional Core:** Stand up Odoo on Azure Container Apps with Azure Database for PostgreSQL (Flexible Server).
- [ ] **5. Establish the Edge/Gateway:** Configure Azure API Management (APIM) as the single global ingress point to route tenants and protect backend APIs. Ensure Azure Front Door is correctly routing traffic to APIM.
- [ ] **6. Implement Shared-Schema Multitenancy:** Configure Odoo's row-level multi-company security rules mapping to Entra ID claims (avoids the operational hazard of database-per-tenant).

## 🧠 Phase 2 & 3: Intelligence & Agency
- [ ] **7. Decouple Events:** Set up Azure Service Bus to listen for Odoo state changes (e.g., "Order Confirmed") to asynchronously trigger downstream data updates without blocking the ERP.
- [ ] **8. Initialize the Agent Factory:** Provision an Azure AI Foundry workspace to act as the centralized registry for Anthropic models and custom tool schemas.
- [ ] **9. Build the First Tool Boundary:** Create the first Foundry-hosted Python tool that allows Claude to safely query (read-only) the Odoo API through APIM.
- [ ] **10. Phase 2 Intelligence Initialization:** Initialize the Azure Databricks workspace and begin building a Lakeflow Spark Declarative Pipelines (SDP) workflow to sync Odoo events.

---

**Related Architecture Docs:**
- `docs/research/wholesale-saas-erp-azure-architecture-study.md`
- `docs/architecture/ADR_ERP_PLATFORM_ROLE_SPLIT.md`
- `docs/architecture/ADR_VSCODE_AGENTIC_ENGINEERING_MODEL.md`
- `spec/wholesale-saas-erp-azure/plan.md`
