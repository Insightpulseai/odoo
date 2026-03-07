# Azure Target State — Constitution

> Non-negotiable architectural rules for the InsightPulse AI platform.
> This document is the governance anchor for all Azure, GitHub, and Databricks decisions.

**Version:** 2.0
**Last Updated:** 2026-03-07
**Parent SSOT:** `ssot/azure/target-state.yaml`

---

## 1. Three-Platform Model

The InsightPulse AI platform operates across exactly three platforms. No additional platforms may be introduced without amending this constitution.

| Platform | Role | Scope |
|----------|------|-------|
| **Azure Boards** | Planning | Work items, backlogs, sprints, delivery plans, agent triggers |
| **GitHub** | Code + CI/CD | Repos, PRs, branch protection, Actions, Environments, Copilot/Claude agents |
| **Azure + Databricks** | Runtime + Data | Container Apps, PostgreSQL Flexible, Databricks Lakehouse, AI/ML |

---

## 2. Nine-Layer Architecture

Every service, resource, and decision must map to exactly one of these layers. Layers are ordered by dependency — lower layers must be provisioned before higher ones.

### Layer 1 — Planning (Azure Boards)

- **Services:** Azure Boards (3 projects: `lakehouse`, `erp-saas`, `platform`)
- **Capabilities:** Work items, backlogs, sprints, delivery plans, agent triggers
- **Work Item Hierarchy:** Epic > Feature > User Story > Task
- **Area Paths:**
  - `erp-saas`: Runtime / Modules / Integrations / Security / Release
  - `lakehouse`: Foundation / Pipelines / Customer360 / Marketing / ML-AI / Governance
  - `platform`: ControlPlane / BoardsAutomation / Agents / AzureRuntime / SharedServices / Observability
- **Iteration Paths:** `2026 > Q1-Q4 > Sprint 01-08+`
- **Board Columns:** Story board: New / Ready / In Progress / Blocked / In Review / Done; Task board: To Do / Doing / Review / Done
- **Swimlanes:** Expedite / Standard / Debt & Hardening
- **Tags:** odoo, oca, ipai, azure, databricks, supabase, agent, security, finops, marketing, customer360, runtime, deploy, observability
- **Naming Conventions:**
  - Epic: `[DOMAIN] Outcome`
  - Feature: `[DOMAIN] Capability`
  - Story: `As a role...`
  - Task: `Verb deliverable`
- **Custom Fields:** Primary Repo, Deployment Surface, Risk Level, Verification Required
- **GitHub Repo Mapping:**
  - ERP-SaaS: `odoo`, `odoo-modules`
  - Lakehouse: `lakehouse`
  - Platform: `platform`, `boards-automation`, `agents`, `infra`, `web`
- **Agent Flow:** Story/Task > Linked repo > Agent > Branch > PR > CI/CD > Merge > Work item auto-updated

### Layer 2 — Code (GitHub)

- **Services:** GitHub repositories, PRs, branch protection, CODEOWNERS
- **Agents:** GitHub Copilot, Claude Code, custom PR agents
- **Branch Strategy:** `main` (protected), feature branches, environment branches
- **Rules:** All code lives in GitHub. Zero repos in Azure DevOps.

### Layer 3 — CI/CD (GitHub Actions)

- **Services:** GitHub Actions workflows, GitHub Environments (dev / staging / prod)
- **Pipeline Types:** Runtime image build, module validation, secrets validation, deploy, health verify
- **Rules:** All pipelines run in GitHub Actions. Zero pipelines in Azure Pipelines. Zero pipelines in Databricks.
- **Artifacts:** Container images pushed to ACR via GitHub Actions

### Layer 4 — Runtime (Azure Compute)

- **Services:** Container Apps Environment, Container Apps, ACR, PostgreSQL Flexible Server, Storage Account
- **Workloads:** Odoo CE 19 (self-hosted), API services, background workers
- **Rules:** Container Apps is the sole compute surface. No VMs, no AKS, no App Service.

### Layer 5 — Edge / Networking

- **Services:** Front Door Premium + WAF, VNet, NSG, Private Link, NAT Gateway
- **Rules:** All public traffic enters through Front Door. Backend services are VNet-isolated. No public IPs on compute.

### Layer 6 — Secrets / Identity

- **Services:** Entra ID, Managed Identity, Key Vault, Azure Policy, Defender for Cloud
- **Rules:** Managed Identity required for all service-to-service auth. No baked secrets. No connection strings in code. Key Vault is the sole secrets store.

### Layer 7 — Observability

- **Services:** Azure Monitor, Application Insights, Log Analytics Workspace, Alerts, Diagnostic Settings
- **Rules:** Every resource must emit diagnostic logs to Log Analytics. Every Container App must have App Insights instrumented.

### Layer 8 — Integration

- **Services (optional):** Service Bus, Event Grid, Function App; Logic Apps only if needed
- **Rules:** Integration services are optional. Prefer direct HTTP between Container Apps when latency allows. Use Service Bus only for guaranteed delivery.

### Layer 9 — Data / AI (Databricks)

- **Services:** Databricks Lakehouse (Unity Catalog, Delta Lake, MLflow, Feature Store)
- **Capabilities:** Analytics, CDP/Customer 360, ML models, AI assistants
- **Rules:** Databricks is the data/AI plane only. It never participates in CI/CD. It never hosts application runtime. Data flows from runtime (Layer 4) into Databricks, not the reverse.

---

## 3. Non-Negotiable Rules

### 3.1 GitHub is the sole CI/CD engine

- All build, test, scan, and deploy pipelines run in GitHub Actions
- Azure Pipelines are prohibited
- Databricks Jobs are not CI/CD — they are data workloads

### 3.2 Azure DevOps = Boards ONLY

The following Azure DevOps services are **permanently prohibited**:

| Service | Status | Reason |
|---------|--------|--------|
| Azure Repos | PROHIBITED | GitHub is sole code host |
| Azure Pipelines | PROHIBITED | GitHub Actions is sole CI/CD |
| Azure Artifacts | PROHIBITED | ACR + GitHub Packages |
| Azure Test Plans | PROHIBITED | GitHub Actions + pytest/jest |
| Azure Wiki | PROHIBITED | In-repo spec kits + docs/ |

### 3.3 Odoo CE 19 is self-hosted

- **Required qualifier:** "self-hosted CE 19"
- **Prohibited terms:** "Odoo SaaS", "Odoo.sh", "Odoo Enterprise", "Odoo Online"
- Odoo runs on Container Apps (Azure) or DigitalOcean — never on Odoo's own hosting

### 3.4 Managed Identity required

- No service may authenticate using baked credentials
- All Azure service-to-service communication uses Managed Identity
- Key Vault stores external secrets (third-party API keys, Odoo admin password)
- Connection strings are never committed to source control

### 3.5 Container Apps is primary compute

- No VMs for application workloads
- No AKS (unnecessary complexity)
- No App Service (Container Apps is preferred)
- Container Apps Environment with VNet integration

### 3.6 Databricks is data plane only

- Databricks handles: analytics, ML, Customer 360, data pipelines
- Databricks never handles: CI/CD, application hosting, API serving
- Data flows: Runtime > Event Grid/Service Bus > Databricks (one-way ingest)

---

## 4. Prohibited Services

These Azure services must never be provisioned:

| Service | Reason |
|---------|--------|
| Azure Pipelines | GitHub Actions is sole CI/CD |
| Azure Repos | GitHub is sole code host |
| Azure Artifacts | ACR + GitHub Packages |
| Azure Test Plans | In-pipeline testing |
| Azure Wiki | In-repo docs |
| Azure DevOps Feeds | npm/PyPI via GitHub |
| AKS | Container Apps preferred |
| App Service | Container Apps preferred |
| Azure VMs (for app workloads) | Container Apps preferred |
| Azure Static Web Apps | Vercel or Container Apps |
| Azure Cognitive Services (legacy) | Use Azure AI Services or Databricks ML |

---

## 5. Azure Boards — Three-Project Structure

### Organization: `insightpulseai`

| Project | Domain | Scope |
|---------|--------|-------|
| `lakehouse` | Data/AI | Databricks, marketing intelligence, customer 360, data pipelines, ML/AI, BI |
| `erp-saas` | ERP | Odoo runtime, OCA/IPAI modules, tenant/release, ERP integrations, environment hardening |
| `platform` | Infrastructure | Supabase control plane, Azure runtime services, boards automation, agents, shared auth/config/observability |

### PR and Agent Flow

```
Story/Task (Azure Boards)
    └─> Linked GitHub Repo
        └─> Agent creates branch
            └─> PR opened
                └─> GitHub Actions CI/CD
                    └─> Merge to main
                        └─> Work item auto-updated (Done)
```

---

## 6. Cross-Reference Table

| Artifact | Path | Purpose |
|----------|------|---------|
| Target State SSOT | `ssot/azure/target-state.yaml` | Canonical platform capability matrix |
| Service Matrix | `ssot/azure/service-matrix.yaml` | Machine-readable service inventory |
| DNS Migration Plan | `ssot/azure/dns-migration-plan.yaml` | DNS record state machine |
| Platform Architecture | `docs/architecture/PLATFORM_ARCHITECTURE.md` | 9-layer reference architecture |
| Copilot Spec | `spec/odoo-copilot-azure/` | Microsoft Agent Framework integration |
| PRD | `spec/azure-target-state/prd.md` | Product requirements |
| Plan | `spec/azure-target-state/plan.md` | Phased rollout plan |
| Tasks | `spec/azure-target-state/tasks.md` | Implementation checklist |

---

## 7. Amendment Process

This constitution may only be amended by:

1. Creating a PR with changes to this file
2. Updating `ssot/azure/target-state.yaml` to reflect the change
3. Updating `docs/architecture/PLATFORM_ARCHITECTURE.md` if architectural layers change
4. Approval from platform owner

**This constitution is binding for all contributors, human and AI.**
