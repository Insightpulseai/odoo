# Platform Architecture — InsightPulse AI

> Complete 9-layer reference architecture for the three-platform model.
> This document is the canonical architecture reference for all teams.

**Version:** 1.0
**Last Updated:** 2026-03-07
**Constitution:** `spec/azure-target-state/constitution.md`
**PRD:** `spec/azure-target-state/prd.md`

---

## 1. Three-Platform Model

InsightPulse AI operates across three platforms with strict role separation:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        THREE-PLATFORM MODEL                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────────────┐  │
│   │  AZURE BOARDS   │   │     GITHUB      │   │   AZURE + DATABRICKS   │  │
│   │   (Planning)    │   │  (Code + CI/CD) │   │   (Runtime + Data)     │  │
│   ├─────────────────┤   ├─────────────────┤   ├─────────────────────────┤  │
│   │ Work items      │──>│ Repositories    │──>│ Container Apps (Odoo)  │  │
│   │ Backlogs        │   │ Pull requests   │   │ PostgreSQL Flexible    │  │
│   │ Sprints         │   │ Branch protect  │   │ ACR                    │  │
│   │ Delivery plans  │   │ GitHub Actions  │   │ Key Vault              │  │
│   │ Agent triggers  │   │ Environments    │   │ Front Door + WAF       │  │
│   │                 │   │ Copilot/Claude  │   │ VNet + NSG             │  │
│   │ 3 projects:     │   │                 │   │ Monitor + App Insights │  │
│   │  - lakehouse    │   │                 │   │ Entra ID               │  │
│   │  - erp-saas     │   │                 │   │ Databricks Lakehouse   │  │
│   │  - platform     │   │                 │   │                        │  │
│   └────────┬────────┘   └────────┬────────┘   └────────────┬───────────┘  │
│            │                     │                          │              │
│            └─────────────────────┴──────────────────────────┘              │
│                          Bidirectional linking                              │
│                    (Work item <-> PR <-> Deploy)                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Rules:**
- Azure Boards is planning only (no repos, no pipelines, no artifacts, no wiki)
- GitHub is the sole code host and CI/CD engine
- Azure cloud services provide runtime compute and data processing
- Databricks is the data/AI plane, never CI/CD

---

## 2. Nine-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 9: DATA / AI                                              │
│  Databricks Lakehouse, Unity Catalog, MLflow, AI Search          │
├─────────────────────────────────────────────────────────────────┤
│  Layer 8: INTEGRATION                                            │
│  Service Bus, Event Grid, Function App (optional)                │
├─────────────────────────────────────────────────────────────────┤
│  Layer 7: OBSERVABILITY                                          │
│  Monitor, App Insights, Log Analytics, Alerts                    │
├─────────────────────────────────────────────────────────────────┤
│  Layer 6: SECRETS / IDENTITY                                     │
│  Entra ID, Managed Identity, Key Vault, Azure Policy, Defender   │
├─────────────────────────────────────────────────────────────────┤
│  Layer 5: EDGE / NETWORKING                                      │
│  Front Door Premium + WAF, VNet, NSG, Private Link, NAT Gateway  │
├─────────────────────────────────────────────────────────────────┤
│  Layer 4: RUNTIME                                                │
│  Container Apps, ACR, PostgreSQL Flexible, Storage Account       │
├─────────────────────────────────────────────────────────────────┤
│  Layer 3: CI/CD                                                  │
│  GitHub Actions (build, test, scan, deploy), Environments        │
├─────────────────────────────────────────────────────────────────┤
│  Layer 2: CODE                                                   │
│  GitHub Repos, PRs, Branch Protection, CODEOWNERS                │
├─────────────────────────────────────────────────────────────────┤
│  Layer 1: PLANNING                                               │
│  Azure Boards (lakehouse, erp-saas, platform)                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Primary Delivery Flow

End-to-end path from planning to production:

```
┌──────────────┐    ┌──────────┐    ┌────────────────┐    ┌─────┐    ┌─────────────────┐
│ Azure Boards │───>│  GitHub   │───>│ GitHub Actions  │───>│ ACR │───>│ Container Apps  │
│ (work item)  │    │ (branch) │    │ (build + test)  │    │     │    │ (Odoo CE 19)    │
└──────────────┘    └──────────┘    └────────────────┘    └─────┘    └────────┬────────┘
       │                  │                                                     │
       │                  │                                            ┌────────▼────────┐
       │                  │                                            │   PostgreSQL     │
       │                  │                                            │   Flexible       │
       └──────────────────┴──── auto-update on merge ──────────────────┘   Server         │
                                                                       └─────────────────┘
```

**Step-by-step:**

1. **Plan:** Work item created in Azure Boards (Story or Task in one of 3 projects)
2. **Code:** Developer or agent creates feature branch in linked GitHub repo
3. **Review:** PR opened with `AB#<work-item-id>` in description
4. **CI:** GitHub Actions runs: lint > test > scan > build Docker image
5. **Publish:** Image pushed to ACR with commit SHA tag
6. **Deploy:** Container Apps pulls new image, creates revision
7. **Verify:** Health check confirms `/web/health` returns 200
8. **Close:** Work item auto-updated to Done on merge

---

## 4. Parallel Data Platform Flow

Data and analytics run independently from the delivery pipeline:

```
┌──────────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌──────────────┐
│     Sources      │    │    Databricks     │    │  Intelligence   │    │  Dashboards  │
│                  │───>│    Lakehouse      │───>│     Layer       │───>│              │
├──────────────────┤    ├──────────────────┤    ├─────────────────┤    ├──────────────┤
│ Odoo CE 19       │    │ Bronze (raw)     │    │ Customer 360    │    │ Superset     │
│ (PostgreSQL)     │    │ Silver (clean)   │    │ Marketing Intel │    │ PowerBI      │
│                  │    │ Gold (business)  │    │ ML Models       │    │ Embedded     │
│ n8n webhooks     │    │ Platinum (ML)    │    │ AI Assistants   │    │ dashboards   │
│                  │    │                  │    │                 │    │              │
│ External APIs    │    │ Unity Catalog    │    │ MLflow Registry │    │ Odoo iframes │
│ IoT / sensors    │    │ Delta Lake       │    │ Feature Store   │    │              │
└──────────────────┘    └──────────────────┘    └─────────────────┘    └──────────────┘
```

**Data flow is one-directional:** Runtime (Layer 4) emits events into Databricks (Layer 9). Databricks never writes back to the runtime database.

---

## 5. Azure Boards — Three-Project Structure

```
Organization: insightpulseai
│
├── Project: lakehouse ──────────────────────────────────────────────
│   │  Scope: Databricks, marketing intelligence, customer 360,
│   │         data pipelines, ML/AI, BI
│   │
│   ├── Area: Foundation        (workspace, unity catalog, networking)
│   ├── Area: Pipelines         (ingestion, transformation, scheduling)
│   ├── Area: Customer360       (unified customer view, CDP)
│   ├── Area: Marketing         (campaign analytics, attribution)
│   ├── Area: ML-AI             (model training, serving, RAG)
│   └── Area: Governance        (data quality, lineage, access control)
│
│   Linked repos: lakehouse
│
├── Project: erp-saas ───────────────────────────────────────────────
│   │  Scope: Odoo runtime, OCA/IPAI modules, tenant/release,
│   │         ERP integrations, environment hardening
│   │
│   ├── Area: Runtime           (Container Apps, PostgreSQL, ACR)
│   ├── Area: Modules           (OCA modules, ipai_* custom modules)
│   ├── Area: Integrations      (n8n, Slack, Supabase, external APIs)
│   ├── Area: Security          (Entra ID, MFA, RBAC, audit)
│   └── Area: Release           (versioning, deployment, rollback)
│
│   Linked repos: odoo, odoo-modules
│
└── Project: platform ──────────────────────────────────────────────
    │  Scope: Supabase control plane, Azure runtime services,
    │         boards automation, agents, shared auth/config/observability
    │
    ├── Area: ControlPlane      (Supabase, Edge Functions, Vault)
    ├── Area: BoardsAutomation  (work item automation, sync hooks)
    ├── Area: Agents            (Claude, Copilot, custom agents)
    ├── Area: AzureRuntime      (Container Apps env, VNet, Front Door)
    ├── Area: SharedServices    (Key Vault, Storage, shared config)
    └── Area: Observability     (Monitor, App Insights, Log Analytics)

    Linked repos: platform, boards-automation, agents, infra, web
```

### Work Item Hierarchy

```
Epic: [DOMAIN] Outcome
  │
  └── Feature: [DOMAIN] Capability
       │
       └── User Story: As a <role>, I want <capability> so that <value>
            │
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

---

## 6. Networking Architecture

```
                        Internet
                           │
                   ┌───────▼───────┐
                   │  Front Door   │
                   │  Premium      │
                   │  + WAF Policy │
                   └───────┬───────┘
                           │ Private Link
              ┌────────────▼────────────┐
              │         VNet            │
              │   (10.0.0.0/16)         │
              │                         │
              │  ┌───────────────────┐  │
              │  │ Subnet: apps      │  │
              │  │ (10.0.1.0/24)     │  │
              │  │                   │  │       ┌─────────────┐
              │  │  Container Apps   │  │       │  Key Vault  │
              │  │  Environment      │◄─┼──────>│  (Private   │
              │  │  ┌─────────────┐  │  │  MI   │   Endpoint) │
              │  │  │ Odoo CE 19  │  │  │       └─────────────┘
              │  │  │ (rev N)     │  │  │
              │  │  └──────┬──────┘  │  │       ┌─────────────┐
              │  │         │         │  │       │  Storage    │
              │  └─────────┼─────────┘  │       │  Account    │
              │            │            │       │  (Private   │
              │  ┌─────────▼─────────┐  │       │   Endpoint) │
              │  │ Subnet: db        │  │       └─────────────┘
              │  │ (10.0.2.0/24)     │  │
              │  │                   │  │       ┌─────────────┐
              │  │  PostgreSQL       │  │       │  ACR        │
              │  │  Flexible Server  │  │       │  (Private   │
              │  │  (Burstable B1ms) │  │       │   Endpoint) │
              │  └───────────────────┘  │       └─────────────┘
              │                         │
              │  ┌───────────────────┐  │
              │  │ Subnet: dbx       │  │
              │  │ (10.0.3.0/24)     │  │
              │  │                   │  │
              │  │  Databricks       │  │
              │  │  (VNet injection) │  │
              │  └───────────────────┘  │
              │                         │
              └─────────┬───────────────┘
                        │
                ┌───────▼───────┐
                │  NAT Gateway  │  (optional — outbound static IP)
                └───────────────┘
```

---

## 7. Repo Structure Recommendation

```
insightpulseai/
│
├── odoo/                          # Odoo CE 19 monorepo (ERP-SaaS)
│   ├── addons/ipai/               # IPAI custom modules
│   ├── addons/oca/                # OCA community modules
│   ├── docker/                    # Dockerfiles
│   ├── infra/bicep/               # Azure IaC (Bicep modules)
│   ├── spec/azure-target-state/   # This spec bundle
│   ├── ssot/azure/                # Azure SSOT files
│   └── .github/workflows/        # CI/CD pipelines
│
├── odoo-modules/                  # Standalone module repo (optional)
│
├── lakehouse/                     # Databricks pipelines + notebooks
│   ├── pipelines/
│   ├── notebooks/
│   ├── models/
│   └── tests/
│
├── platform/                      # Shared platform services
│   ├── supabase/
│   ├── functions/
│   └── config/
│
├── boards-automation/             # Azure Boards automation
│   ├── hooks/
│   ├── sync/
│   └── .github/workflows/
│
├── agents/                        # AI agent services
│   ├── claude-agent/
│   ├── copilot-agent/
│   └── board-agent/
│
├── infra/                         # Cross-cutting infrastructure
│   ├── bicep/
│   ├── terraform/
│   └── scripts/
│
└── web/                           # Web frontend
    ├── apps/
    └── packages/
```

---

## 8. Service Inventory

### Mandatory Services (13)

| Service | Layer | Resource Name Pattern | SKU |
|---------|-------|-----------------------|-----|
| Container Apps Environment | 4 - Runtime | `cae-ipai-{env}` | Consumption |
| Container Apps | 4 - Runtime | `ca-ipai-odoo-{env}` | Consumption |
| ACR | 4 - Runtime | `acripai{env}` | Basic |
| PostgreSQL Flexible | 4 - Runtime | `psql-ipai-{env}` | Burstable B1ms |
| Storage Account | 4 - Runtime | `stipai{env}` | Standard LRS |
| Front Door Premium | 5 - Edge | `afd-ipai` | Premium |
| VNet | 5 - Edge | `vnet-ipai-{env}` | Standard |
| Key Vault | 6 - Secrets | `kv-ipai-{env}` | Standard |
| Managed Identity | 6 - Identity | `id-ipai-{env}` | System-assigned |
| Entra ID | 6 - Identity | (tenant-level) | Free |
| Azure Monitor | 7 - Observability | (subscription-level) | Pay-as-you-go |
| Application Insights | 7 - Observability | `appi-ipai-{env}` | Pay-as-you-go |
| Log Analytics | 7 - Observability | `log-ipai-{env}` | Pay-as-you-go |

### Optional Strong Services (6)

| Service | Layer | When Needed |
|---------|-------|-------------|
| Service Bus | 8 - Integration | Multi-service guaranteed delivery |
| Event Grid | 8 - Integration | Databricks ingest triggers |
| Function App | 8 - Integration | Lightweight webhook handlers |
| API Management | 5 - Edge | External API exposure |
| NAT Gateway | 5 - Edge | Outbound IP allowlisting |
| Azure Policy | 6 - Governance | Production compliance |

### Optional Data/AI Services (4)

| Service | Layer | When Needed |
|---------|-------|-------------|
| Databricks Workspace | 9 - Data/AI | Analytics, Customer 360, ML |
| ML Workspace | 9 - Data/AI | Model training and registry |
| Azure AI Services | 9 - Data/AI | Document intelligence, NLP |
| Azure AI Search | 9 - Data/AI | Vector search, RAG |

### Azure Boards (Planning Layer)

| Project | Scope |
|---------|-------|
| `lakehouse` | Data/AI: Databricks, marketing intelligence, customer 360, data pipelines, ML/AI, BI |
| `erp-saas` | ERP: Odoo runtime, OCA/IPAI modules, tenant/release, integrations, hardening |
| `platform` | Infrastructure: Supabase control plane, Azure runtime, boards automation, agents, shared services |

---

## 9. Prohibited Services

These services must never be provisioned (see constitution):

| Service | Reason | Alternative |
|---------|--------|-------------|
| Azure Pipelines | GitHub Actions is sole CI/CD | GitHub Actions |
| Azure Repos | GitHub is sole code host | GitHub |
| Azure Artifacts | ACR + GitHub Packages | ACR, npm |
| Azure Test Plans | In-pipeline testing | GitHub Actions + pytest/jest |
| Azure Wiki | In-repo documentation | spec/ + docs/ |
| AKS | Over-engineered | Container Apps |
| App Service | Container Apps preferred | Container Apps |
| Azure VMs (workloads) | Container Apps preferred | Container Apps |
| Static Web Apps | Vercel preferred | Vercel, Container Apps |

---

## 10. ERP Positioning

| Attribute | Value |
|-----------|-------|
| Product | Odoo CE 19 |
| Qualifier | Self-hosted Community Edition |
| Hosting | Azure Container Apps (primary) or DigitalOcean (legacy) |
| Database | PostgreSQL Flexible Server (Azure) or PostgreSQL 16 (DO) |
| Module Philosophy | Config > OCA > Delta (`ipai_*`) |
| License | LGPL-3.0 |

**Prohibited terms:** "Odoo SaaS", "Odoo.sh", "Odoo Enterprise", "Odoo Online"

---

## 11. Cross-References

| Document | Path | Purpose |
|----------|------|---------|
| Constitution | `spec/azure-target-state/constitution.md` | Non-negotiable architectural rules |
| PRD | `spec/azure-target-state/prd.md` | Product requirements |
| Plan | `spec/azure-target-state/plan.md` | Phased rollout plan |
| Tasks | `spec/azure-target-state/tasks.md` | Implementation checklist |
| Target State SSOT | `ssot/azure/target-state.yaml` | Canonical platform capability matrix |
| Service Matrix SSOT | `ssot/azure/service-matrix.yaml` | Machine-readable service inventory |
| DNS Migration SSOT | `ssot/azure/dns-migration-plan.yaml` | DNS record state machine |
| Copilot Spec | `spec/odoo-copilot-azure/` | Microsoft Agent Framework integration |
| SSOT Boundaries | `docs/architecture/SSOT_BOUNDARIES.md` | Platform boundary definitions |
| Deploy Target Matrix | `docs/architecture/DEPLOY_TARGET_MATRIX.md` | Service-to-target mapping |
| Environments | `docs/architecture/ENVIRONMENTS.md` | Environment definitions |
