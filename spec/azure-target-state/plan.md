# Azure Target State — Implementation Plan

> Phased rollout plan for the InsightPulse AI three-platform architecture.
> Each phase has clear entry criteria, deliverables, and exit criteria.

**Version:** 2.0
**Last Updated:** 2026-03-07
**Parent SSOT:** `ssot/azure/target-state.yaml`
**Constitution:** `spec/azure-target-state/constitution.md`
**PRD:** `spec/azure-target-state/prd.md`

---

## Phase 0 — IaC Foundation

**Goal:** Establish infrastructure-as-code baseline with Bicep. All subsequent phases depend on this foundation.

**Entry Criteria:** Azure subscription active, GitHub repo provisioned, Entra ID tenant configured.

### Deliverables

1. **Bicep Module Library**
   - Resource Group module
   - VNet + NSG + subnet module
   - Key Vault module (with Managed Identity access policies)
   - ACR module (Basic SKU)
   - Managed Identity module (system-assigned + user-assigned)
   - Storage Account module (Standard LRS)

2. **GitHub Actions IaC Pipeline**
   - `infra-validate.yml` — Bicep lint + what-if on PR
   - `infra-deploy.yml` — Bicep deploy on merge to main
   - GitHub Environments: `dev`, `staging`, `prod` with approval gates

3. **Environment Structure**
   - Resource group naming: `rg-ipai-{env}` (dev, staging, prod)
   - Tagging standard: `environment`, `project`, `owner`, `cost-center`
   - Key Vault per environment with Managed Identity access

4. **Secrets Bootstrap**
   - GitHub Actions secrets for Azure service principal (OIDC preferred)
   - Key Vault seeded with: Odoo admin password, PostgreSQL password, external API keys
   - Zero secrets in source control (gitleaks enforced)

**Exit Criteria:**
- `az deployment group what-if` succeeds for all modules
- Key Vault accessible via Managed Identity from GitHub Actions
- ACR created and GitHub Actions can push images
- VNet provisioned with Container Apps subnet and PostgreSQL subnet

---

## Phase 1 — Runtime

**Goal:** Odoo CE 19 running on Container Apps with PostgreSQL Flexible Server, accessible via ACR image.

**Entry Criteria:** Phase 0 complete (VNet, ACR, Key Vault, Managed Identity provisioned).

### Deliverables

1. **Container Apps Environment**
   - Bicep module for Container Apps Environment with VNet integration
   - Log Analytics Workspace connected
   - Internal-only ingress (no public IP — Front Door handles external traffic in Phase 2)

2. **Container Apps — Odoo CE 19**
   - Bicep module for Container App
   - Image source: ACR (built by GitHub Actions)
   - Environment variables from Key Vault references
   - Health probes: liveness (`/web/health`), readiness (`/web/health`)
   - Min replicas: 1, Max replicas: 3
   - CPU: 1.0, Memory: 2.0Gi

3. **PostgreSQL Flexible Server**
   - Bicep module for PostgreSQL Flexible Server
   - SKU: Burstable B1ms (cost-minimized)
   - VNet integration (delegated subnet)
   - Entra ID authentication (Managed Identity)
   - Database: `odoo` (single database, `list_db=False`)
   - Automated backups: 7-day retention

4. **Storage Account**
   - Blob container for Odoo filestore
   - Blob container for database backups
   - Private endpoint (VNet)

5. **GitHub Actions Deploy Pipeline**
   - Build Odoo CE 19 Docker image
   - Push to ACR
   - Update Container Apps revision
   - Run health check post-deploy

**Exit Criteria:**
- Odoo CE 19 responds on Container Apps internal endpoint
- `/web/health` returns 200
- PostgreSQL reachable from Container App via VNet
- GitHub Actions can build and deploy end-to-end
- Storage Account accessible for filestore

---

## Phase 2 — Edge + Security

**Goal:** Production-grade external access with WAF, SSL, and identity controls.

**Entry Criteria:** Phase 1 complete (Container Apps + PostgreSQL running).

### Deliverables

1. **Front Door Premium**
   - Bicep module for Front Door profile
   - Origin group pointing to Container Apps Environment
   - Custom domain: `erp.insightpulseai.com` (with managed certificate)
   - WAF policy: OWASP 3.2 ruleset, bot protection, rate limiting
   - Health probes to `/web/health`

2. **Entra ID Integration**
   - App registration for Odoo SSO
   - RBAC role assignments for Container Apps management
   - Conditional Access policies (MFA for admin roles)

3. **Azure Policy**
   - Deny public IP on Container Apps
   - Require Managed Identity on all resources
   - Require Key Vault for secrets
   - Require diagnostic settings on all resources
   - Deny prohibited services (VMs, AKS, App Service for workloads)

4. **Network Hardening**
   - NSG rules: deny all inbound except Front Door
   - Private endpoints for PostgreSQL, Key Vault, Storage Account
   - NAT Gateway for deterministic outbound IP (if third-party allowlisting needed)

5. **Defender for Cloud**
   - Enable for Container Apps, PostgreSQL, Key Vault
   - Security alerts to Log Analytics

**Exit Criteria:**
- `erp.insightpulseai.com` resolves through Front Door with valid SSL
- WAF blocks OWASP test payloads
- No resource has a public IP except Front Door
- Azure Policy audit shows zero violations
- Entra ID SSO functional for Odoo

---

## Phase 3 — Observability

**Goal:** Full-stack monitoring, alerting, and diagnostics for all runtime services.

**Entry Criteria:** Phase 2 complete (Front Door + security controls active).

### Deliverables

1. **Application Insights**
   - Instrumentation on Odoo Container App
   - Custom metrics: request latency, error rate, active sessions
   - Availability tests (synthetic monitoring)

2. **Log Analytics Workspace**
   - Diagnostic settings on: Container Apps, PostgreSQL, Front Door, Key Vault, VNet
   - Custom KQL queries for Odoo-specific logs
   - Retention: 30 days (cost-optimized)

3. **Azure Monitor Alerts**
   - Odoo health check failure (> 2 consecutive failures)
   - PostgreSQL CPU > 80% for 5 minutes
   - Container App restart count > 3 in 10 minutes
   - Front Door 5xx error rate > 5%
   - Key Vault access denied events
   - Storage Account throttling

4. **Dashboards**
   - Azure Portal dashboard: runtime health overview
   - Workbook: Odoo performance (response time, error rate, throughput)
   - Workbook: Infrastructure cost tracking

5. **Diagnostic Settings**
   - All resources emit logs to Log Analytics
   - Container Apps: console logs, system logs
   - PostgreSQL: query performance, connection logs
   - Front Door: access logs, WAF logs

**Exit Criteria:**
- All resources emit diagnostic logs to Log Analytics
- Alert rules fire correctly on simulated failures
- Dashboards display live metrics
- Availability test confirms uptime from external probe

---

## Phase 4 — Agent Layer

**Goal:** Establish the agent framework for automated work item processing, PR generation, and CI/CD orchestration triggered from Azure Boards.

**Entry Criteria:** Phase 3 complete (observability in place for monitoring agent actions).

### Deliverables

1. **Azure Boards Project Setup**
   - Create 3 projects in `insightpulseai` organization: `lakehouse`, `erp-saas`, `platform`
   - Configure area paths per constitution (Runtime/Modules/Integrations/Security/Release for erp-saas, etc.)
   - Configure iteration paths: `2026 > Q1-Q4 > Sprint 01-08+`
   - Board columns: Story board (New/Ready/In Progress/Blocked/In Review/Done), Task board (To Do/Doing/Review/Done)
   - Swimlanes: Expedite / Standard / Debt & Hardening
   - Custom fields: Primary Repo, Deployment Surface, Risk Level, Verification Required
   - Tags baseline: odoo, oca, ipai, azure, databricks, supabase, agent, security, finops

2. **GitHub-Azure Boards Integration**
   - Service hooks: Work item state changes trigger GitHub webhook
   - GitHub Actions: PR merge updates linked work item to Done
   - Bidirectional link: Work item contains PR URL, PR description contains work item ID

3. **Agent Framework**
   - Container App for agent service (Python/Node.js)
   - Agent reads assigned work items from Azure Boards API
   - Agent creates branch in linked GitHub repo
   - Agent generates code changes (via Claude/Copilot)
   - Agent opens PR with work item reference
   - GitHub Actions runs CI; on merge, work item auto-closes

4. **Agent Observability**
   - App Insights instrumentation on agent Container App
   - Custom metrics: work items processed, PRs opened, CI pass rate
   - Alerts: agent failure rate > 10%, work item queue depth > 50

**Exit Criteria:**
- All 3 Azure Boards projects created with full configuration
- Work item > PR > merge > work item update flow works end-to-end
- Agent can process at least one work item type autonomously
- Agent actions visible in App Insights

---

## Phase 5 — Data/AI Plane

**Goal:** Connect Databricks Lakehouse for analytics and intelligence. This phase is optional and does not block ERP runtime.

**Entry Criteria:** Phase 1 complete (runtime operational). Phases 2-4 recommended but not required.

### Deliverables

1. **Databricks Workspace**
   - Bicep module for Databricks Workspace (Premium SKU)
   - VNet injection into existing VNet
   - Unity Catalog configured
   - Managed Identity for data access

2. **Data Ingestion**
   - Event Grid / Service Bus bridge from Container Apps to Databricks
   - Odoo data extraction (PostgreSQL > Bronze layer)
   - External API ingestion (n8n webhook payloads)

3. **Medallion Architecture**
   - Bronze: raw ingestion (Odoo tables, API payloads, webhook events)
   - Silver: cleaned, deduplicated, typed
   - Gold: business aggregates (Customer 360, financial summaries, marketing metrics)
   - Platinum: ML features, predictions, recommendations

4. **Intelligence Layer**
   - Customer 360 model
   - Marketing intelligence dashboards
   - ML model registry (MLflow)
   - AI assistant integration (RAG over gold layer)

5. **Dashboard Integration**
   - Superset connected to Databricks SQL Warehouse
   - Embedded dashboards in Odoo (via iframe or API)
   - PowerBI integration (optional, for executive reporting)

**Exit Criteria:**
- Databricks Workspace provisioned and accessible
- At least one data pipeline running (Odoo > Bronze > Silver)
- Customer 360 gold view queryable
- Dashboard showing live data from Databricks

---

## Phase Dependencies

```
Phase 0 (IaC Foundation)
    │
    ▼
Phase 1 (Runtime) ──────────────────────────► Phase 5 (Data/AI)
    │                                              [optional, non-blocking]
    ▼
Phase 2 (Edge + Security)
    │
    ▼
Phase 3 (Observability)
    │
    ▼
Phase 4 (Agent Layer)
```

Phases 0-4 are sequential. Phase 5 can start after Phase 1 and runs in parallel.
