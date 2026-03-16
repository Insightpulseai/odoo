# Tasks: Wholesale SaaS ERP on Azure

## Phase 0: Foundations & DevUx
- [ ] Define `.devcontainer/infra` (Terraform, Azure CLI, azd, PostgreSQL client).
- [ ] Define `.devcontainer/erp` (Odoo 18+, Python 3.12+, PostgreSQL client).
- [ ] Decide source-control model: GitHub + ADO Pipelines, or full ADO Repos migration.
- [ ] Initialize Azure DevOps project and configure branch policies for `main`.
- [ ] Create base Terraform modules for RG, VNet, subnets, NAT Gateway, Log Analytics, diagnostics.
- [ ] Set up remote Terraform state and env structure (`dev`, `staging`, `prod`).

## Phase 1: MVP Transactional Core
- [ ] Deploy Azure Database for PostgreSQL Flexible Server via Terraform.
- [ ] Deploy Azure Container Registry via Terraform.
- [ ] Build/push custom Odoo image to ACR.
- [ ] Deploy Azure Container Apps Environment via Terraform.
- [ ] Deploy Odoo web and worker container apps.
- [ ] Provision Azure Files and mount it for persistent Odoo filestore.
- [ ] Configure Entra ID App Registration for Odoo SSO.
- [ ] Validate Odoo multi-company security mapping and persistence behavior.

## Phase 2: Intelligence Layer
- [ ] Deploy Azure Databricks workspace via Terraform.
- [ ] Provision ADLS Gen2 for the Lakehouse.
- [ ] Create Azure Service Bus namespace, topics, and subscriptions.
- [ ] Write Odoo event publisher for `sale.order` confirmation.
- [ ] Build Databricks Lakeflow Spark Declarative Pipelines (SDP) Bronze ingestion pipeline.
- [ ] Validate event replay, idempotency, and dead-letter handling.

## Phase 3: System of Agency
- [ ] Provision Azure AI Foundry workspace.
- [ ] Deploy Azure AI Document Intelligence resource.
- [ ] Build APIM-secured Odoo integration layer.
- [ ] Create Python tool `create_vendor_bill(ocr_data)`.
- [ ] Add tracing/observability for the Foundry tool path.
- [ ] Test end-to-end OCR-to-vendor-bill flow via agent invocation.

## Phase 4: Enterprise Hardening
- [ ] Run load tests against ACA Odoo services and validate scale rules.
- [ ] Execute PostgreSQL Flexible Server failover drill.
- [ ] Implement Azure Policy to prevent unmanaged/manual resource creation.
- [ ] Add backup/restore and DR validation for DB + filestore.
- [ ] Finalize monitoring, alerts, and release promotion controls.
