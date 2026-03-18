# Azure Startup Knowledge Base

> Knowledge base for the azure-startup-advisor agent.
> Maps Azure Developer CLI (azd) patterns to the InsightPulseAI architecture.
> Source: Microsoft Learn docs + spec/azure-target-state/ spec bundle.

---

## Canonical Role of This Document

This document is a **reference knowledge base**, NOT a source of truth. It provides patterns, mappings, and decision guidance for the azure-startup-advisor agent.

**Authoritative sources that override this document:**
- `spec/azure-target-state/constitution.md` — principles and constraints
- `spec/azure-target-state/plan.md` — phased rollout plan
- `spec/azure-target-state/tasks.md` — task breakdown and acceptance criteria
- `ssot/azure/resources.yaml` — canonical resource inventory
- `infra/azure/azure.yaml` — service-to-resource mapping (azd manifest)

If this document conflicts with any of the above, the above wins. This file may lag behind spec changes.

---

## Sections

| # | Section | Purpose |
|---|---------|---------|
| 1 | azd Template Pattern → InsightPulseAI Mapping | Directory structure mapping |
| 2 | azd Commands → InsightPulseAI Equivalents | Command translation table |
| 3 | Phase-to-azd Mapping | Phase-specific deployment commands |
| 4 | Naming Convention Reference | Resource naming patterns |
| 5 | OIDC Authentication Flow | CI/CD auth architecture |
| 6 | Evidence Generation Pattern | Evidence path and format |
| 7 | Resource State Classification | SSOT source field values |
| 8 | Current Platform Baseline | Deployed resource summary |
| 9 | Key Bicep Module Patterns | IaC template patterns |
| 10 | Startup Advisor Decision Tree | Phase progression logic |
| 11 | azd-Compatible azure.yaml (Target) | Service manifest target |
| 12 | Build 2026 Relevance | Upcoming Azure features |
| 13 | Decision Matrix | Compute platform selection guidance |

---

## 1. azd Template Pattern → InsightPulseAI Mapping

### Standard azd Structure

```
project/
├── azure.yaml          # Service-to-resource mapping
├── infra/              # Bicep or Terraform IaC
│   ├── main.bicep      # Entry point
│   └── modules/        # Reusable modules
├── .azure/             # Environment configs
├── src/                # Application source
├── .github/            # CI/CD workflows
└── .devcontainer/      # Dev container config
```

### InsightPulseAI Equivalent

```
odoo/
├── infra/azure/azure.yaml       # Service-to-resource mapping (azd-compatible)
├── infra/azure/                 # Bicep IaC
│   ├── main.bicep               # Existing: Notion PPM control room
│   ├── platform/main.bicep      # Target: Phase 0 landing zone
│   ├── agents/main.bicep        # Target: Phase 1 Container Apps
│   ├── data/main.bicep          # Target: Phase 2 Databricks
│   └── modules/                 # Shared modules
├── ssot/azure/resources.yaml    # SSOT inventory (replaces .azure/)
├── addons/ipai/                 # Odoo modules (app source)
├── mcp/servers/                 # MCP tool servers (app source)
├── supabase/functions/          # Edge Functions (app source)
├── .github/workflows/           # CI/CD (azd-compatible)
│   ├── odoo-azure-deploy.yml
│   └── odoo-azure-upgrade-evidence.yml
└── .devcontainer/               # Dev container
```

---

## 2. azd Commands → InsightPulseAI Equivalents

| azd Command | InsightPulseAI Equivalent | Notes |
|-------------|--------------------------|-------|
| `azd init` | `spec/azure-target-state/` spec bundle | Defines architecture before provisioning |
| `azd auth login` | `az login --use-device-code` or OIDC in CI | P3: Managed identity for service auth |
| `azd provision` | `az deployment sub create --template-file infra/azure/platform/main.bicep` | Phase-specific Bicep deployment |
| `azd deploy` | `.github/workflows/odoo-azure-deploy.yml` | ACR build + Container App revision |
| `azd up` | Phase-specific bootstrap scripts | Provision + deploy in one shot |
| `azd env` | `ssot/azure/resources.yaml` + `.env` files | SSOT is the env registry |
| `azd monitor` | Azure Monitor + Log Analytics + App Insights | P7: Observability non-negotiable |
| `azd pipeline config` | `.github/workflows/` + OIDC setup | Federated credentials, no secrets |

---

## 3. Phase-to-azd Mapping

### Phase 0: Landing Zone (azd init equivalent)

```bash
# What azd would do:
azd init --template azure-container-apps

# What InsightPulseAI does:
az deployment sub create \
  --location southeastasia \
  --template-file infra/azure/platform/main.bicep \
  --parameters environment=dev
```

**Resources**: RGs, Key Vault (RBAC), Log Analytics, Managed IDs, VNet, NSGs

### Phase 1: Container Apps (azd provision equivalent)

```bash
# What azd would do:
azd provision

# What InsightPulseAI does:
az deployment group create \
  --resource-group rg-ipai-agents-dev \
  --template-file infra/azure/agents/main.bicep \
  --parameters environment=dev
```

**Resources**: ACR, Container Apps Environment, health-check app, Dapr components

### Phase 2: Databricks (data plane)

```bash
# Databricks managed via Bicep, not azd
az deployment group create \
  --resource-group rg-ipai-ai-dev \
  --template-file infra/azure/data/main.bicep \
  --parameters environment=dev
```

**Resources**: Unity Catalog, medallion schema, access connectors

### Phase 3: Foundry (AI orchestration)

```bash
# Foundry Agent Service via Azure AI SDK
az ai project create --name proj-ipai-dev \
  --resource-group rg-ipai-agents-dev \
  --hub hub-ipai-dev
```

### Phase 4: Production Hardening

```bash
# WAF, DDoS, budget alerts
az deployment group create \
  --resource-group rg-ipai-platform-dev \
  --template-file infra/azure/platform/hardening.bicep
```

---

## 4. Naming Convention Reference

```
{type}-ipai-{env}

Examples:
  rg-ipai-platform-dev       # Resource group
  kv-ipai-platform-dev       # Key Vault
  law-ipai-dev               # Log Analytics Workspace
  id-ipai-aca-dev            # Managed Identity (Container Apps)
  cae-ipai-dev               # Container Apps Environment
  ca-healthcheck-ipai-dev    # Container App
  caj-agent-ipai-dev         # Container Apps Job
  cripaidev                  # Container Registry (no hyphens)
  stipaidevlake              # Storage Account (no hyphens)
  dbw-ipai-dev               # Databricks Workspace
  appi-ipai-dev              # Application Insights
```

Exceptions (platform restrictions):
- **ACR**: `{type}ipai{env}` (no hyphens allowed)
- **Storage**: `st{ipai}{env}{suffix}` (no hyphens, max 24 chars)

---

## 5. OIDC Authentication Flow

```
GitHub Actions → Azure OIDC (federated credentials)
                ↓
         Managed Identity
                ↓
    ┌───────────┼───────────┐
    ↓           ↓           ↓
  ACR Build  Container   Key Vault
             App Deploy   Access
```

**GitHub Actions Secrets Required**:
- `AZURE_SUBSCRIPTION_ID`
- `AZURE_TENANT_ID`
- `AZURE_CLIENT_ID`
- `ACR_NAME`
- `CONTAINERAPP_NAME`

**No client secrets** — OIDC workload identity federation only.

---

## 6. Evidence Generation Pattern

Every deployment produces evidence:

```
web/docs/evidence/<YYYYMMDD-HHMM+0800>/azure-<topic>/
├── logs/
│   ├── deploy.log
│   ├── verify.log
│   └── cleanup.log
└── summary.json    # { status: COMPLETE|PARTIAL|BLOCKED, ... }
```

Timezone: Asia/Manila (UTC+08:00)

---

## 7. Resource State Classification

| State | Meaning | SSOT Field |
|-------|---------|------------|
| `bicep` | Defined in IaC, deployable | `source: bicep` |
| `confirmed` | Exists in Azure, verified | `source: confirmed` |
| `pending` | Committed scope, not provisioned | `source: pending` |
| `evaluation` | Under consideration | `source: evaluation` |

---

## 8. Current Platform Baseline

| Component | Location | Status |
|-----------|----------|--------|
| Databricks workspace | `dbw-ipai-dev` in `rg-ipai-ai-dev` | confirmed |
| ADLS Gen2 | `stipaidevlake` with medallion containers | confirmed |
| Key Vault | `kv-ipai-dev` in `rg-ipai-shared-dev` | bicep |
| Azure OpenAI | `oai-ipai-dev` (S0) | confirmed |
| VNet | `vnet-ipai-databricks` (10.10.0.0/16) | confirmed |
| Container Apps | Not yet provisioned | pending (Phase 1) |
| ACR | Not yet provisioned | pending (Phase 1) |
| Foundry | Not yet provisioned | pending (Phase 3) |

---

## 9. Key Bicep Module Patterns

Existing modules follow this pattern:

```bicep
// Module: infra/azure/modules/{resource}.bicep
targetScope = 'resourceGroup'

@description('Resource name')
param name string

@description('Location')
param location string = resourceGroup().location

@description('Tags')
param tags object = {}

resource myResource 'Microsoft.{Provider}/{Type}@{API-version}' = {
  name: name
  location: location
  tags: tags
  properties: {
    // ...
  }
}

output id string = myResource.id
output name string = myResource.name
```

---

## 10. Startup Advisor Decision Tree

```
User asks: "What should I deploy next?"
  ↓
Read ssot/azure/resources.yaml
  ↓
Count: confirmed vs pending resources
  ↓
  ├── Phase 0 incomplete? → Deploy landing zone (RGs, KV, LAW, IDs)
  ├── Phase 0 done, Phase 1 missing? → Deploy Container Apps (ACR, CAE, apps)
  ├── Phase 1 done, Phase 2 missing? → Consolidate Databricks (Unity, medallion)
  ├── Phase 2 done, Phase 3 missing? → Set up Foundry (project, agents)
  └── Phase 3 done? → Production hardening (WAF, DDoS, budgets)
```

---

## 11. azd-Compatible azure.yaml (Target)

```yaml
# infra/azure/azure.yaml
name: insightpulseai-platform
metadata:
  template: insightpulseai/odoo@latest

services:
  odoo:
    project: ./addons/ipai
    language: python
    host: containerapp
    docker:
      path: ./docker/Dockerfile

  mcp-plane:
    project: ./mcp/servers/plane
    language: ts
    host: containerapp

  edge-functions:
    project: ./supabase/functions
    language: ts
    host: function    # Supabase-hosted, not Azure

pipeline:
  provider: github

infra:
  provider: bicep
  path: ./infra/azure
  module: ./infra/azure/platform/main.bicep
```

---

## 12. Build 2026 Relevance

Microsoft Build 2026 (June 2-3, San Francisco):
- Azure Developer CLI v2 with enhanced template authoring
- Foundry Agent Service GA
- Container Apps dynamic sessions
- Copilot Studio agent integration with Azure resources

Track these for InsightPulseAI roadmap alignment:
- Foundry GA → unblocks Phase 3
- Container Apps sessions → potential for Odoo shell access
- Copilot Studio → potential for VS Code extension integration

---

## 13. Decision Matrix — Compute Platform Selection

| Factor | Container Apps | App Service | VM (IaaS) |
|--------|---------------|-------------|-----------|
| **Use when** | Microservices, event-driven, scale-to-zero workloads | Monolithic web apps, PaaS-managed runtime | Legacy apps requiring OS-level control |
| **Avoid when** | Persistent connections required (WebSockets >30min) | Need fine-grained container orchestration | Cost optimization is priority |
| **InsightPulseAI fit** | MCP servers, agent jobs, health-check apps | Odoo web (if not containerized) | Never — violates P4 (Container Apps over AKS/VM) |
| **Scaling** | Event-driven, scale-to-zero, consumption billing | Auto-scale rules, always-on minimum | Manual or VMSS |
| **Secrets** | Key Vault refs via managed identity | Key Vault refs or App Settings | Key Vault refs or OS env vars |
| **Networking** | VNet integration, internal ingress | VNet integration, private endpoints | Full VNet control |
| **Cost model** | Pay-per-request (consumption) or dedicated | Always-on plan tiers | Always-on VM billing |

**Default choice for InsightPulseAI**: Container Apps (per P4). Only escalate to App Service if Container Apps lacks a required feature. Never use VMs unless explicitly justified in a spec amendment.
