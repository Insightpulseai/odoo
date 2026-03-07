# Azure Target State — Task Checklist

> Complete implementation checklist across all phases.
> Each task maps to a deliverable in `plan.md`.

**Version:** 2.0
**Last Updated:** 2026-03-07
**Plan:** `spec/azure-target-state/plan.md`

---

## Phase 0 — IaC Foundation

### Bicep Module Library

- [ ] Create `infra/bicep/modules/resource-group.bicep`
- [ ] Create `infra/bicep/modules/vnet.bicep` (VNet + subnets + NSGs)
- [ ] Create `infra/bicep/modules/key-vault.bicep` (with Managed Identity access policies)
- [ ] Create `infra/bicep/modules/acr.bicep` (Basic SKU)
- [ ] Create `infra/bicep/modules/managed-identity.bicep` (system-assigned + user-assigned)
- [ ] Create `infra/bicep/modules/storage-account.bicep` (Standard LRS)
- [ ] Create `infra/bicep/main.bicep` (orchestrator for all modules)
- [ ] Create `infra/bicep/parameters/dev.bicepparam`
- [ ] Create `infra/bicep/parameters/staging.bicepparam`
- [ ] Create `infra/bicep/parameters/prod.bicepparam`

### GitHub Actions IaC Pipeline

- [ ] Create `.github/workflows/infra-validate.yml` (Bicep lint + what-if on PR)
- [ ] Create `.github/workflows/infra-deploy.yml` (Bicep deploy on merge)
- [ ] Configure GitHub Environment: `dev` (auto-approve)
- [ ] Configure GitHub Environment: `staging` (manual approve)
- [ ] Configure GitHub Environment: `prod` (manual approve + 2 reviewers)

### Environment Structure

- [ ] Define resource group naming convention: `rg-ipai-{env}`
- [ ] Define tagging standard in Bicep parameters
- [ ] Create Key Vault per environment
- [ ] Verify Managed Identity can access Key Vault

### Secrets Bootstrap

- [ ] Configure GitHub OIDC for Azure (federated credentials)
- [ ] Seed Key Vault with Odoo admin password
- [ ] Seed Key Vault with PostgreSQL admin password
- [ ] Seed Key Vault with external API keys (Mailgun, Slack, etc.)
- [ ] Add gitleaks to CI pipeline (`.github/workflows/security-scan.yml`)
- [ ] Verify zero secrets in source control

### Phase 0 Verification

- [ ] `az deployment group what-if` succeeds for dev environment
- [ ] GitHub Actions can authenticate to Azure via OIDC
- [ ] ACR created and accessible from GitHub Actions
- [ ] VNet provisioned with correct subnet configuration

---

## Phase 1 — Runtime

### Container Apps Environment

- [ ] Create `infra/bicep/modules/container-apps-env.bicep`
- [ ] VNet integration (delegated subnet)
- [ ] Log Analytics Workspace connection
- [ ] Internal-only ingress configuration

### Container Apps — Odoo CE 19

- [ ] Create `infra/bicep/modules/container-app.bicep`
- [ ] Create `docker/Dockerfile.azure` (Odoo CE 19 for Container Apps)
- [ ] Configure environment variables from Key Vault references
- [ ] Configure health probes (liveness + readiness on `/web/health`)
- [ ] Set scaling rules (min: 1, max: 3)
- [ ] Set resource limits (CPU: 1.0, Memory: 2.0Gi)

### PostgreSQL Flexible Server

- [ ] Create `infra/bicep/modules/postgresql-flexible.bicep`
- [ ] Configure Burstable B1ms SKU
- [ ] VNet integration (delegated subnet)
- [ ] Enable Entra ID authentication
- [ ] Create database `odoo`
- [ ] Configure automated backups (7-day retention)
- [ ] Test Managed Identity connection from Container App

### Storage Account

- [ ] Create blob container `odoo-filestore`
- [ ] Create blob container `odoo-backups`
- [ ] Configure private endpoint
- [ ] Mount as volume in Container App

### GitHub Actions Deploy Pipeline

- [ ] Create `.github/workflows/build-odoo-image.yml`
- [ ] Create `.github/workflows/deploy-container-app.yml`
- [ ] Create `.github/workflows/health-verify.yml`
- [ ] End-to-end test: push > build > deploy > health check

### Phase 1 Verification

- [ ] Odoo CE 19 responds on Container Apps internal endpoint
- [ ] `/web/health` returns 200
- [ ] PostgreSQL reachable from Container App via VNet
- [ ] GitHub Actions build-deploy pipeline succeeds
- [ ] Storage Account accessible for filestore
- [ ] `odoo.conf` has `list_db=False` and `db_name=odoo`

---

## Phase 2 — Edge + Security

### Front Door Premium

- [ ] Create `infra/bicep/modules/front-door.bicep`
- [ ] Configure origin group pointing to Container Apps
- [ ] Add custom domain `erp.insightpulseai.com`
- [ ] Configure managed SSL certificate
- [ ] Create WAF policy (OWASP 3.2 ruleset)
- [ ] Enable bot protection
- [ ] Configure rate limiting rules
- [ ] Set up health probes to `/web/health`

### Entra ID Integration

- [ ] Create app registration for Odoo SSO
- [ ] Configure RBAC role assignments for Container Apps
- [ ] Set up Conditional Access policies (MFA for admins)
- [ ] Test SSO login flow

### Azure Policy

- [ ] Create policy: deny public IP on Container Apps
- [ ] Create policy: require Managed Identity on all resources
- [ ] Create policy: require Key Vault for secrets
- [ ] Create policy: require diagnostic settings
- [ ] Create policy: deny prohibited services (VMs, AKS, App Service)
- [ ] Assign policies to subscription/resource group
- [ ] Run compliance scan

### Network Hardening

- [ ] Configure NSG: deny all inbound except Front Door service tag
- [ ] Create private endpoints for PostgreSQL
- [ ] Create private endpoints for Key Vault
- [ ] Create private endpoints for Storage Account
- [ ] Provision NAT Gateway (if outbound IP allowlisting needed)

### Defender for Cloud

- [ ] Enable Defender for Container Apps
- [ ] Enable Defender for PostgreSQL
- [ ] Enable Defender for Key Vault
- [ ] Configure security alerts to Log Analytics

### Phase 2 Verification

- [ ] `erp.insightpulseai.com` resolves through Front Door
- [ ] SSL certificate valid and auto-renewing
- [ ] WAF blocks OWASP test payloads (SQLi, XSS)
- [ ] No resource has public IP except Front Door
- [ ] Azure Policy compliance: zero violations
- [ ] Entra ID SSO works for Odoo login

---

## Phase 3 — Observability

### Application Insights

- [ ] Create App Insights resource linked to Log Analytics
- [ ] Instrument Odoo Container App
- [ ] Configure custom metrics (request latency, error rate, sessions)
- [ ] Set up availability tests (synthetic monitoring from 3+ regions)

### Log Analytics Workspace

- [ ] Configure diagnostic settings on Container Apps
- [ ] Configure diagnostic settings on PostgreSQL
- [ ] Configure diagnostic settings on Front Door
- [ ] Configure diagnostic settings on Key Vault
- [ ] Configure diagnostic settings on VNet/NSG
- [ ] Create custom KQL queries for Odoo logs
- [ ] Set retention to 30 days

### Azure Monitor Alerts

- [ ] Alert: Odoo health check failure (> 2 consecutive)
- [ ] Alert: PostgreSQL CPU > 80% for 5 minutes
- [ ] Alert: Container App restart count > 3 in 10 minutes
- [ ] Alert: Front Door 5xx rate > 5%
- [ ] Alert: Key Vault access denied events
- [ ] Alert: Storage Account throttling
- [ ] Configure action group (email + Slack webhook)

### Dashboards

- [ ] Create Azure Portal dashboard: runtime health overview
- [ ] Create workbook: Odoo performance metrics
- [ ] Create workbook: infrastructure cost tracking

### Phase 3 Verification

- [ ] All resources emit logs to Log Analytics
- [ ] Simulate failure: verify alert fires within 5 minutes
- [ ] Dashboards display live metrics
- [ ] Availability test reports uptime from external probe

---

## Phase 4 — Agent Layer

### Azure Boards Project Setup

- [ ] Create project `lakehouse` in `insightpulseai` organization
- [ ] Create project `erp-saas` in `insightpulseai` organization
- [ ] Create project `platform` in `insightpulseai` organization
- [ ] Configure area paths for `erp-saas`: Runtime, Modules, Integrations, Security, Release
- [ ] Configure area paths for `lakehouse`: Foundation, Pipelines, Customer360, Marketing, ML-AI, Governance
- [ ] Configure area paths for `platform`: ControlPlane, BoardsAutomation, Agents, AzureRuntime, SharedServices, Observability
- [ ] Configure iteration paths: `2026 > Q1 > Sprint 01-04`, repeat for Q2-Q4
- [ ] Configure Story board columns: New / Ready / In Progress / Blocked / In Review / Done
- [ ] Configure Task board columns: To Do / Doing / Review / Done
- [ ] Add swimlanes: Expedite / Standard / Debt & Hardening
- [ ] Add custom field: Primary Repo (string)
- [ ] Add custom field: Deployment Surface (single select)
- [ ] Add custom field: Risk Level (single select)
- [ ] Add custom field: Verification Required (boolean)
- [ ] Create tag set: odoo, oca, ipai, azure, databricks, supabase, agent, security, finops, marketing, customer360, runtime, deploy, observability

### GitHub-Azure Boards Integration

- [ ] Install Azure Boards GitHub App on `insightpulseai` org
- [ ] Configure service hooks for work item state changes
- [ ] Create GitHub Action: on PR merge, update linked work item to Done
- [ ] Test bidirectional linking (work item <> PR)
- [ ] Map repos to projects: `odoo`/`odoo-modules` > `erp-saas`, `lakehouse` > `lakehouse`, `platform`/`infra`/`web` > `platform`

### Agent Framework

- [ ] Create Container App for agent service
- [ ] Implement Azure Boards API client (read assigned work items)
- [ ] Implement GitHub API client (create branch, open PR)
- [ ] Implement agent orchestration logic (work item > branch > code > PR)
- [ ] Integrate Claude/Copilot for code generation
- [ ] Add work item reference to PR description (`AB#<id>`)
- [ ] Test end-to-end: work item assignment > agent PR > CI > merge > work item done

### Agent Observability

- [ ] Instrument agent Container App with App Insights
- [ ] Add custom metrics: work items processed, PRs opened, CI pass rate
- [ ] Alert: agent failure rate > 10%
- [ ] Alert: work item queue depth > 50
- [ ] Dashboard: agent activity and performance

### Phase 4 Verification

- [ ] All 3 Azure Boards projects created with full area/iteration paths
- [ ] Work item > PR > merge > auto-update flow works
- [ ] Agent processes at least one work item autonomously
- [ ] Agent actions visible in App Insights
- [ ] Custom fields and tags visible on all boards

---

## Phase 5 — Data/AI Plane

### Databricks Workspace

- [ ] Create `infra/bicep/modules/databricks.bicep` (Premium SKU)
- [ ] Configure VNet injection
- [ ] Enable Unity Catalog
- [ ] Configure Managed Identity for data access
- [ ] Create SQL Warehouse for BI queries

### Data Ingestion

- [ ] Set up Event Grid / Service Bus bridge from Container Apps
- [ ] Create Odoo data extraction pipeline (PostgreSQL > Bronze)
- [ ] Create external API ingestion pipeline (n8n webhooks > Bronze)
- [ ] Schedule incremental ingestion (hourly for transactional, daily for dimensions)

### Medallion Architecture

- [ ] Create Bronze layer schemas (raw Odoo tables, raw API payloads)
- [ ] Create Silver layer transformations (dedup, type casting, validation)
- [ ] Create Gold layer aggregates (Customer 360, financial summaries, marketing metrics)
- [ ] Create Platinum layer features (ML features, predictions, recommendations)
- [ ] Configure Delta Lake optimization (Z-ORDER, VACUUM, OPTIMIZE)

### Intelligence Layer

- [ ] Build Customer 360 model (unified customer view across Odoo, marketing, web)
- [ ] Build marketing intelligence aggregates
- [ ] Set up MLflow model registry
- [ ] Create AI assistant RAG pipeline over gold layer

### Dashboard Integration

- [ ] Connect Superset to Databricks SQL Warehouse
- [ ] Create embedded dashboard for Odoo
- [ ] PowerBI integration for executive reporting (optional)

### Phase 5 Verification

- [ ] Databricks Workspace provisioned and accessible
- [ ] At least one pipeline runs: Odoo > Bronze > Silver
- [ ] Customer 360 gold view queryable via SQL Warehouse
- [ ] Dashboard displays live data from Databricks
- [ ] Unity Catalog shows all registered tables

---

## Cross-Phase Tasks

### Documentation

- [ ] Update `docs/architecture/PLATFORM_ARCHITECTURE.md` after each phase
- [ ] Update `ssot/azure/target-state.yaml` with actual service states
- [ ] Update `ssot/azure/service-matrix.yaml` with provisioned endpoints
- [ ] Create evidence packs in `docs/evidence/<YYYYMMDD-HHMM>/azure-target-state/`

### Security

- [ ] Run gitleaks scan before every phase completion
- [ ] Rotate all Key Vault secrets quarterly
- [ ] Review Azure Policy compliance monthly
- [ ] Defender for Cloud review monthly

### Cost Management

- [ ] Set budget alerts per resource group
- [ ] Review monthly Azure spend
- [ ] Rightsize Container Apps and PostgreSQL based on usage
- [ ] Optimize Databricks cluster auto-termination
