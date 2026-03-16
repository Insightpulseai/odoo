# Tasks: Wholesale SaaS ERP on Azure

## Phase 0: Foundations & DevUx

- [ ] Define `.devcontainer` for `infra` (Terraform, Azure CLI).
- [ ] Define `.devcontainer` for `erp` (Odoo 18+, Python 3.12+, PostgreSQL client).
- [ ] Initialize Azure DevOps project and configure Branch Policies (main must pass PR).
- [ ] Create base Terraform modules for Azure VNet, NAT Gateway, and Log Analytics.
- [ ] Configure GitHub-to-Azure DevOps sync (if needed) or migrate completely to ADO Repos.

## Phase 1: MVP Transactional Core

- [ ] Deploy Azure Database for PostgreSQL Flexible Server via Terraform.
- [ ] Deploy Azure Container Apps Environment via Terraform.
- [ ] Push Odoo custom `Dockerfile` to Azure Container Registry.
- [ ] Deploy Odoo standard container (web) and worker container (background jobs).
- [ ] Mount Azure Files to Odoo ACA for persistent filestore.
- [ ] Configure Entra ID App Registration for Odoo SSO.
- [ ] Validate Odoo multi-company row-level security mapping.

## Phase 2: Intelligence Layer

- [ ] Deploy Azure Databricks workspace via Terraform.
- [ ] Provision ADLS Gen2 for the Databricks Lakehouse.
- [ ] Create Azure Service Bus namespace and topics for Odoo event emission.
- [ ] Write Odoo server action/webhook to broadcast `sale.order` confirmation to Service Bus.
- [ ] Build Databricks Delta Live Table (DLT) pipeline to ingest from Service Bus (Bronze).

## Phase 3: System of Agency

- [ ] Provision Microsoft Foundry (Azure AI Foundry) workspace.
- [ ] Deploy Azure AI Document Intelligence resource.
- [ ] Build Odoo API integration layer in APIM (securing Odoo endpoints).
- [ ] Create Python tool for Foundry: `create_vendor_bill(ocr_data)`.
- [ ] Test Anthropic Copilot Agent invoking `create_vendor_bill` through Foundry tracing.

## Phase 4: Enterprise Hardening

- [ ] Run load tests on Odoo ACA instances to validate auto-scaling behavior.
- [ ] Execute a manual failover drill for Azure PostgreSQL Flexible.
- [ ] Implement Azure Policy to restrict manual resource creation outside of Azure DevOps.
