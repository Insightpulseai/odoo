# Implementation Plan: Wholesale SaaS ERP on Azure

> **Architecture model:** Six-plane Azure-first
> **Operational core:** Odoo CE 19 (SoR) + Databricks (SoI) + Foundry (Agent Runtime)

## Phase 0: Foundations & DevUx

**Objective**: Establish the six-plane landing zone and CI/CD automation.

1. Author `.devcontainer` specifications for Odoo, Infra, and AI agent workloads.
2. Initialize Azure DevOps organization, project, and Board hierarchies.
3. Deploy Azure Landing Zones (VNets, Identity, Log Analytics, APIM) via Bicep modules (`infra/azure/modules/`) deployed through Azure Pipelines.
4. Codify truth-authority model in `ssot/architecture/platform-boundaries.yaml`.
5. Establish GitHub as code truth, Azure Pipelines as release truth.

## Phase 1: MVP Transactional Core

**Objective**: Deploy the mission-critical Odoo CE 19 System of Record.

1. Provision Azure Database for PostgreSQL Flexible Server.
2. Provision Azure Container Apps environment and deploy Odoo web/worker services.
3. Configure Azure Front Door for global edge routing and WAF.
4. Establish Azure Entra ID single sign-on for Odoo.
   - **Identity bootstrap status (2026-03-18):** Native tenant admins created (`admin@`, `emergency-admin@ceoinsightpulseai.onmicrosoft.com`), Global Admin + MFA assigned. `insightpulseai.com` verified and set as default domain. M365 Business Premium not yet redeemed (zero SKUs). Security Defaults temporarily disabled for bootstrap — re-enable after MFA enrollment.
5. Create initial Wholesale Tenant (Company) to validate database-per-tenant isolation.
6. Configure OCA-first module baseline (CE + OCA as primary EE parity vehicle).

## Phase 2: Intelligence Layer

**Objective**: Establish the canonical data intelligence core.

1. Deploy Azure Databricks Workspace via Bicep (canonical, not optional). Terraform retained for Cloudflare DNS only.
2. Provision ADLS Gen2 for the Lakehouse with medallion layout (bronze/silver/gold).
3. Configure Unity Catalog for governance and lineage tracking.
4. Configure Azure Service Bus or Event Hubs to stream transactional state changes from Odoo.
5. Build the Lakeflow Spark Declarative Pipelines (SDP) ingestion pipeline (Odoo Bronze -> Silver -> Gold).
6. Verify reporting queries execute against the Lakehouse, not PostgreSQL.

## Phase 3: Agent Runtime & Document Workflows

**Objective**: Establish the agent factory and hosted runtime via Microsoft Foundry.

1. Initialize Microsoft Foundry workspace side-by-side with Azure OpenAI.
2. Route inbound vendor emails to Azure AI Document Intelligence for OCR parsing.
3. Author Anthropic Agent tools inside Foundry to securely read/write Odoo POs via APIM-governed REST API.
4. Establish Foundry Tracing to monitor agent execution, hallucinations, and tool failures.
5. Configure evaluation pipelines for agent quality monitoring.
6. All agent-to-Odoo calls routed through APIM (governed ingress/egress boundary).

## Phase 4: Enterprise Hardening

**Objective**: Prepare for production SaaS scale.

1. Conduct Azure Well-Architected Review across the deployed infrastructure.
2. Finalize Disaster Recovery (DR) testing (e.g., PostgreSQL point-in-time restore, APIM failover).
3. Lock down environment gates in Azure DevOps.
4. Implement and validate automated tenant promotion (shared → stamped deployment).
5. Configure Azure Resource Graph queries for live inventory drift detection.
6. Verify all six planes are observable and governed per truth-authority model.
