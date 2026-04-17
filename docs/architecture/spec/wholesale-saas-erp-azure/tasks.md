# Tasks: Wholesale SaaS ERP on Azure

## Phase 0: Foundations & DevUx

- [x] Define `.devcontainer/infra` (Terraform, Azure CLI, azd, PostgreSQL client).
- [x] Define `.devcontainer/erp` (Odoo CE 19, Python 3.12+, PostgreSQL client).
- [x] Decide source-control model: GitHub + ADO Pipelines, or full ADO Repos migration. (Decided: GitHub + ADO Pipelines)
- [x] Initialize Azure DevOps project and configure branch policies for `main`.
- [x] Codify six-plane architecture model in `ssot/architecture/platform-boundaries.yaml`.
- [x] Codify data flows in `ssot/architecture/data-flows.yaml`.
- [x] Document truth-authority model (Boards/GitHub/Pipelines/Resource Graph/Foundry/repo SSOT).
- [x] Create base Bicep modules for VNet, subnets, Log Analytics, Azure Files, diagnostics (`infra/azure/modules/`). Terraform retained for Cloudflare DNS only.
- [x] Create environment parameter files (`dev`, `prod`) for Bicep deployments (`infra/azure/parameters/`).
- [x] Create CI/CD pipeline for Bicep deployments (`.azure/pipelines/ci-cd.yml`).

## Phase 1: MVP Transactional Core

- [x] Deploy Azure Database for PostgreSQL Flexible Server (`ipai-odoo-dev-pg` in `rg-ipai-dev` — active).
- [x] Deploy Azure Container Registry (`cripaidev` in `rg-ipai-shared-dev` — active).
- [ ] Build/push custom Odoo CE 19 image to ACR.
- [x] Deploy Azure Container Apps Environment (`ipai-odoo-dev-env` in `rg-ipai-dev` — active).
- [x] Deploy Odoo web and worker container apps (`ipai-odoo-dev-web`, `-worker`, `-cron` — active).
- [x] Codify Azure Files Bicep module (`infra/azure/modules/azure-files.bicep`). Deployment pending.
- [ ] Deploy Azure Files and mount to ACA for persistent Odoo filestore.
- [x] Create Front Door dev parameter file (`infra/azure/parameters/front-door-dev.parameters.json`) with real ACA FQDNs.
- [ ] Deploy Front Door dev configuration and validate routing.
- [x] Configure Entra ID App Registration for Odoo SSO. App `3605a67d-7135-44a0-8640-03a9b4225923`, 15 roles, secrets in `ipai-odoo-dev-kv`. Blocked: M365 Business Premium for Conditional Access P1.
- [ ] Validate database-per-tenant isolation model.
- [ ] Configure OCA-first module baseline (56-module target, 7 known gaps).
- [x] Retire duplicate resources: `odoo-web` deleted from `rg-ipai-agents-dev` (2026-03-18). `odoo-init` not found.
- [ ] Re-enable Security Defaults after MFA enrollment for both native admins.

## Phase 2: Intelligence Layer

- [ ] Deploy Azure Databricks workspace via Bicep (canonical, not optional).
- [ ] Provision ADLS Gen2 for the Lakehouse with medallion layout.
- [ ] Configure Unity Catalog for governance and lineage.
- [ ] Create Azure Service Bus namespace, topics, and subscriptions.
- [ ] Write Odoo event publisher for `sale.order` confirmation.
- [ ] Build Databricks Lakeflow SDP Bronze ingestion pipeline.
- [ ] Build Silver normalization pipeline (dedup, type casting, schema validation).
- [ ] Build Gold curation pipeline (business logic, aggregation, feature engineering).
- [ ] Validate event replay, idempotency, and dead-letter handling.

## Phase 3: Agent Runtime

- [ ] Provision Microsoft Foundry workspace.
- [ ] Deploy Azure AI Document Intelligence resource.
- [ ] Build APIM-secured Odoo integration layer.
- [ ] Create Python tool `create_vendor_bill(ocr_data)`.
- [ ] Configure Foundry tracing for all agent tool executions.
- [ ] Set up evaluation pipelines for agent quality monitoring.
- [ ] Test end-to-end OCR-to-vendor-bill flow via agent invocation.

## Phase 4: Enterprise Hardening

- [ ] Run load tests against ACA Odoo services and validate scale rules.
- [ ] Execute PostgreSQL Flexible Server failover drill.
- [ ] Implement Azure Policy to prevent unmanaged/manual resource creation.
- [ ] Add backup/restore and DR validation for DB + filestore.
- [ ] Implement automated tenant promotion (shared -> stamped deployment).
- [ ] Configure Azure Resource Graph drift detection queries.
- [ ] Finalize monitoring, alerts, and release promotion controls.
- [ ] Verify all six planes are observable per truth-authority model.
