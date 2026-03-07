# Azure Target State — Product Requirements Document

> Product requirements for the InsightPulse AI three-platform architecture.
> Governs Azure runtime, GitHub CI/CD, and Azure Boards planning surface.

**Version:** 2.0
**Last Updated:** 2026-03-07
**Parent SSOT:** `ssot/azure/target-state.yaml`
**Constitution:** `spec/azure-target-state/constitution.md`

---

## 1. Users and Personas

| Persona | Role | Primary Needs |
|---------|------|---------------|
| **DevOps Engineer** | Provisions infrastructure, manages CI/CD, monitors health | IaC (Bicep), GitHub Actions, Container Apps, observability dashboards |
| **Finance Lead** | Manages Odoo ERP, month-end close, BIR compliance | Odoo CE 19 availability, backup/restore, module upgrades |
| **Data Engineer** | Builds data pipelines, analytics, ML models | Databricks Lakehouse, Unity Catalog, Delta Lake, MLflow |
| **Platform Operator** | Manages shared services, secrets, networking, identity | Key Vault, Entra ID, Managed Identity, Front Door, VNet |

---

## 2. Service Inventory

### 2.1 Mandatory Stack (13 services)

These services are required for production readiness:

| # | Service | Layer | Purpose | SKU |
|---|---------|-------|---------|-----|
| 1 | Container Apps Environment | Runtime | Compute isolation boundary | Consumption |
| 2 | Container Apps | Runtime | Odoo CE 19 + API services | Consumption |
| 3 | Azure Container Registry (ACR) | Runtime | Container image storage | Basic |
| 4 | PostgreSQL Flexible Server | Runtime | Odoo database backend | Burstable B1ms |
| 5 | Front Door Premium | Edge | Global load balancer + WAF | Premium |
| 6 | Key Vault | Secrets | Secrets, certificates, keys | Standard |
| 7 | Managed Identity | Identity | Service-to-service auth | System-assigned |
| 8 | Azure Monitor | Observability | Metrics and alerting | Pay-as-you-go |
| 9 | Application Insights | Observability | APM and distributed tracing | Pay-as-you-go |
| 10 | Log Analytics Workspace | Observability | Centralized log aggregation | Pay-as-you-go |
| 11 | Virtual Network (VNet) | Networking | Network isolation | Standard |
| 12 | Entra ID | Identity | User authentication, RBAC | Free tier |
| 13 | Storage Account | Runtime | Odoo filestore, backups, static assets | Standard LRS |

### 2.2 Optional Strong (6 services)

Recommended but not blocking for initial deployment:

| # | Service | Layer | Purpose | When Needed |
|---|---------|-------|---------|-------------|
| 14 | Service Bus | Integration | Guaranteed async messaging | Multi-service event routing |
| 15 | Event Grid | Integration | Event-driven architecture | Databricks ingest triggers |
| 16 | Function App | Integration | Lightweight event handlers | Webhook processing |
| 17 | API Management | Edge | API gateway, rate limiting | External API exposure |
| 18 | NAT Gateway | Networking | Outbound static IP | Third-party IP allowlisting |
| 19 | Azure Policy | Governance | Compliance enforcement | Production hardening |

### 2.3 Optional Data/AI (4 services)

Separate data plane — does not block ERP runtime:

| # | Service | Layer | Purpose | When Needed |
|---|---------|-------|---------|-------------|
| 20 | Databricks Workspace | Data/AI | Lakehouse analytics | Customer 360, BI |
| 21 | ML Workspace | Data/AI | Model training, registry | ML model serving |
| 22 | Azure AI Services | Data/AI | Cognitive APIs | Document intelligence, NLP |
| 23 | Azure AI Search | Data/AI | Vector search, RAG | Knowledge base search |

### 2.4 Azure Boards (planning layer — not Azure cloud)

| # | Service | Layer | Purpose |
|---|---------|-------|---------|
| 24 | Azure Boards (`lakehouse`) | Planning | Data/AI work tracking |
| 25 | Azure Boards (`erp-saas`) | Planning | ERP work tracking |
| 26 | Azure Boards (`platform`) | Planning | Infrastructure work tracking |

---

## 3. System Architecture

### 3.1 Primary Delivery Flow

```
┌──────────────┐    ┌──────────┐    ┌────────────────┐    ┌─────┐    ┌─────────────────┐
│ Azure Boards │───>│  GitHub   │───>│ GitHub Actions  │───>│ ACR │───>│ Container Apps  │
│ (3 projects) │    │ (repos)  │    │ (CI/CD)         │    │     │    │ (Odoo CE 19)    │
└──────────────┘    └──────────┘    └────────────────┘    └─────┘    └────────┬────────┘
                                                                               │
                                                                     ┌────────▼────────┐
                                                                     │   PostgreSQL     │
                                                                     │   Flexible       │
                                                                     └─────────────────┘
```

**Flow:**
1. Work item created in Azure Boards (one of 3 projects)
2. Agent/developer creates branch in linked GitHub repo
3. PR opened, GitHub Actions runs CI pipeline (lint, test, scan, build)
4. On merge: container image built and pushed to ACR
5. Container Apps pulls new image, runs health checks
6. Work item auto-updated to Done

### 3.2 Parallel Data Platform Flow

```
┌──────────────┐    ┌──────────────┐    ┌───────────────┐    ┌────────────┐
│   Sources    │───>│  Databricks  │───>│ Intelligence  │───>│ Dashboards │
│              │    │  Lakehouse   │    │   Layer       │    │            │
├──────────────┤    ├──────────────┤    ├───────────────┤    ├────────────┤
│ Odoo CE 19   │    │ Bronze       │    │ Customer 360  │    │ Superset   │
│ n8n webhooks │    │ Silver       │    │ Marketing     │    │ PowerBI    │
│ External APIs│    │ Gold         │    │ ML models     │    │ Embedded   │
│ IoT/sensors  │    │ Platinum     │    │ AI assistants │    │ dashboards │
└──────────────┘    └──────────────┘    └───────────────┘    └────────────┘
```

**Flow:**
1. Data sources (Odoo, APIs, webhooks) emit events
2. Event Grid / Service Bus routes to Databricks ingestion
3. Databricks processes through medallion layers (Bronze > Silver > Gold > Platinum)
4. Intelligence layer produces Customer 360, ML predictions, AI features
5. Dashboards consume gold/platinum views for visualization

### 3.3 Azure Boards 3-Project Structure

```
Organization: insightpulseai
│
├── Project: lakehouse
│   ├── Area: Foundation
│   ├── Area: Pipelines
│   ├── Area: Customer360
│   ├── Area: Marketing
│   ├── Area: ML-AI
│   └── Area: Governance
│   Repos: lakehouse
│
├── Project: erp-saas
│   ├── Area: Runtime
│   ├── Area: Modules
│   ├── Area: Integrations
│   ├── Area: Security
│   └── Area: Release
│   Repos: odoo, odoo-modules
│
└── Project: platform
    ├── Area: ControlPlane
    ├── Area: BoardsAutomation
    ├── Area: Agents
    ├── Area: AzureRuntime
    ├── Area: SharedServices
    └── Area: Observability
    Repos: platform, boards-automation, agents, infra, web
```

---

## 4. CI Pipeline Types

| Pipeline | Trigger | Steps | Artifact |
|----------|---------|-------|----------|
| **Runtime Image Build** | Push to `main` | Checkout > Build Docker image > Push to ACR > Deploy to Container Apps | Container image in ACR |
| **Module Validation** | PR to `main` | Checkout > Lint (flake8, black, isort) > Unit tests > OCA compliance | Test report |
| **Secrets Validation** | PR to `main` | Scan for hardcoded secrets (gitleaks) > Verify .env patterns | Pass/fail gate |
| **Deploy** | Merge to `main` (auto) or manual | Pull image from ACR > Update Container Apps revision > Health check | Running revision |
| **Health Verify** | Post-deploy (auto) | HTTP health check > DB connectivity > Module list verification | Health report |

---

## 5. Networking Architecture

```
Internet
    │
    ▼
┌─────────────────────┐
│  Front Door Premium  │  (WAF, SSL termination, global routing)
│  + WAF Policy        │
└──────────┬──────────┘
           │ (Private Link)
┌──────────▼──────────┐
│       VNet           │
│  ┌─────────────┐    │
│  │ Container   │    │
│  │ Apps Env    │    │     ┌──────────────────┐
│  │  ┌────────┐ │    │     │   Key Vault      │
│  │  │ Odoo   │ │◄───┼────►│   (Managed ID)   │
│  │  │ CE 19  │ │    │     └──────────────────┘
│  │  └───┬────┘ │    │
│  └──────┼──────┘    │     ┌──────────────────┐
│         │           │     │   Storage Acct    │
│  ┌──────▼──────┐    │     │   (filestore)    │
│  │ PostgreSQL  │    │     └──────────────────┘
│  │ Flexible    │    │
│  │ (Private)   │    │
│  └─────────────┘    │
└─────────────────────┘
```

---

## 6. ERP Positioning

| Rule | Statement |
|------|-----------|
| **Canonical name** | Odoo CE 19 (self-hosted) |
| **Hosting** | Azure Container Apps or DigitalOcean droplet — never Odoo-hosted |
| **License** | Community Edition (LGPL-3.0) |
| **Module philosophy** | Config > OCA > Delta (`ipai_*`) |
| **Never use** | "Odoo SaaS", "Odoo.sh", "Odoo Enterprise", "Odoo Online" |
| **Database** | PostgreSQL Flexible Server (Azure) or PostgreSQL 16 (DO) |

---

## 7. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| CI pipeline duration (build + deploy) | < 10 minutes | GitHub Actions workflow time |
| Odoo health check response | < 500ms, 200 OK | `/web/health` endpoint |
| Infrastructure provisioning (IaC) | < 30 minutes | Bicep deployment time |
| Secrets rotation | Zero downtime | Key Vault rotation + Managed Identity |
| Container cold start | < 15 seconds | Container Apps metrics |
| Uptime (Odoo) | 99.5% | Front Door health probes |
| Zero hardcoded secrets | 0 findings | Gitleaks scan |
| Azure DevOps Boards-only | 0 repos, 0 pipelines, 0 artifacts | Azure DevOps audit |

---

## 8. Azure Boards Structure Summary

### Work Item Hierarchy

```
Epic: [DOMAIN] Outcome
  └── Feature: [DOMAIN] Capability
       └── User Story: As a <role>, I want <capability> so that <value>
            └── Task: Verb deliverable
```

### Board Configuration

| Board | Columns |
|-------|---------|
| Story Board | New > Ready > In Progress > Blocked > In Review > Done |
| Task Board | To Do > Doing > Review > Done |

### Swimlanes

| Lane | Purpose |
|------|---------|
| Expedite | Critical path / P0 items |
| Standard | Normal priority work |
| Debt & Hardening | Technical debt, security, performance |

### Tags

`odoo`, `oca`, `ipai`, `azure`, `databricks`, `supabase`, `agent`, `security`, `finops`, `marketing`, `customer360`, `runtime`, `deploy`, `observability`

### Custom Fields

| Field | Type | Purpose |
|-------|------|---------|
| Primary Repo | String | GitHub repo this work item targets |
| Deployment Surface | Single select | Container Apps / Databricks / Supabase / GitHub Pages |
| Risk Level | Single select | Low / Medium / High / Critical |
| Verification Required | Boolean | Whether deploy verification is mandatory |

---

## 9. External SSOT Dependencies

| Artifact | Path | Purpose |
|----------|------|---------|
| Target State | `ssot/azure/target-state.yaml` | Canonical platform capability matrix |
| Service Matrix | `ssot/azure/service-matrix.yaml` | Machine-readable service inventory |
| DNS Migration | `ssot/azure/dns-migration-plan.yaml` | DNS record state machine |
| Platform Architecture | `docs/architecture/PLATFORM_ARCHITECTURE.md` | 9-layer reference architecture |
| Copilot Spec | `spec/odoo-copilot-azure/` | Microsoft Agent Framework |
| Constitution | `spec/azure-target-state/constitution.md` | Non-negotiable rules |
