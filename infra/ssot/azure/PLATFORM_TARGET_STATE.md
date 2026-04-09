# Platform Target State

> **Version**: 1.5.1
> **Date**: 2026-03-11
> **Scope**: Azure-native runtime + Supabase + Databricks + Tableau Cloud consolidated target state
> **Owner**: Platform Engineering / InsightPulse AI
> **Status**: Living document -- updated per sprint

---

## Change Log

| Version | Date       | Description                                                                                         |
| ------- | ---------- | --------------------------------------------------------------------------------------------------- |
| 1.0.0   | 2026-03-07 | Initial Azure target state extracted from org restructuring                                          |
| 1.1.0   | 2026-03-08 | Added DNS target state, identity architecture, Databricks layer                                     |
| 1.2.0   | 2026-03-09 | Added Odoo 18 CE conventions, end-to-end data flow, n8n integration                                 |
| 1.3.0   | 2026-03-10 | Full Azure resource inventory (55 resources across 6 RGs), CI/CD contract, 30-day sprint            |
| 1.4.0   | 2026-03-11 | Tableau Cloud added as active analytics app surface; analytics surfaces section; SSO target updated  |
| 1.4.1   | 2026-03-11 | Analytics: 4 surfaces (Superset, Databricks, Tableau connector, Power BI). Full DO→Azure migration mandate |
| 1.5.0   | 2026-03-11 | Reconciled §2 with portal reality (57 confirmed resources). Separated current-state inventory into `resources.yaml`. Target-state aspirational resources moved to §2.3. Dual Odoo deployment exception recorded. |
| 1.5.1   | 2026-03-11 | DO runtime decommission completed: Front Door origins moved to Azure runtimes, droplet deleted, DNS section updated to Front Door canonical routing. |

---

## System Architecture Overview

```
                              ┌──────────────────────────────────┐
                              │     Azure Subscription           │
                              │     (TBWA-TaskForce-AI)          │
                              │     bc849566-...                 │
                              └──────────┬───────────────────────┘
                                         │
              ┌──────────────────────────┬┴──────────────────────────┐
              ▼                          ▼                           ▼
     ┌────────────────┐      ┌────────────────────┐      ┌──────────────────┐
     │  rg-ipai-dev   │      │  rg-ipai-shared    │      │  rg-ipai-data    │
     │  (Compute)     │      │  (Identity/Net)    │      │  (Databricks)    │
     │                │      │                    │      │                  │
     │  ca-ipai-dev   │      │  kv-ipai-shared    │      │  dbw-ipai-dev    │
     │  (Container    │      │  (Key Vault)       │      │  (Workspace)     │
     │   Apps Env)    │      │                    │      │                  │
     │                │      │  id-ipai-shared    │      │  Unity Catalog   │
     │  acr-ipai-dev  │      │  (Managed ID)      │      │  ipai_dev        │
     │  (Registry)    │      │                    │      │                  │
     └───────┬────────┘      │  fd-ipai-shared    │      └──────────────────┘
             │               │  (Front Door)      │
             │               └────────────────────┘
             │
             │   ┌────────────────────────────────────────────────┐
             │   │          pg-ipai-dev                           │
             │   │  (Azure PG Flexible Server — shared DB host)  │
             │   │                                                │
             │   │  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
             │   │  │ odoo_dev │  │ n8n_dev  │  │ supabase │    │
             │   │  │          │  │          │  │ (ai.*)   │    │
             │   │  └──────────┘  └──────────┘  └──────────┘    │
             │   └────────────────────────────────────────────────┘
             │
             ├──────────────────────────────────────────────────────┐
             │                                                      │
             ▼                                                      ▼
      DigitalOcean Runtime                                   Supabase Cloud
      (Decommissioned 2026-03-11)                            spdtwktxdalcfigzeqrz
      (no active production runtime)                         (Control Plane)
                                                             ┌──────────────────┐
                                                             │  Auth            │
                                                             │  Realtime        │
                                                             │  Edge Functions  │
                                                             │  Storage         │
                                                             │  Vault           │
                                                             │  pgvector        │
                                                             └──────────────────┘
             │
             │         Downstream Analytics & AI Surfaces
             │
             ├──────────────────────────────────────────────────────────────────┐
             │                          │              │                        │
             ▼                          ▼              ▼                        ▼
      Supabase                   srch-ipai-dev   oai-ipai-dev           Tableau Cloud
      ai.* schema                (AI Search)     (Azure OpenAI)         (Analytics App)
      (pg-ipai-dev)                                                      insightpulseai site
```

---

## 1. SSOT / SOR Doctrine

> **SSOT** = Single Source of Truth (canonical definition lives here)
> **SOR** = System of Record (operational data is mastered here)

| Domain                        | SSOT                | SOR                                                                                       | Notes                                                                                                                                                                              |
| ----------------------------- | ------------------- | ----------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Azure Resources**           | This document       | Azure Resource Manager                                                                    | Bicep/Terraform IaC is the deployment truth; this doc is the target state                                                                                                          |
| **DNS**                       | `subdomain-registry.yaml` | Cloudflare                                                                          | YAML-first workflow; Cloudflare is the runtime SOR                                                                                                                                 |
| **Identity**                  | Entra ID            | Entra ID                                                                                  | All human identities; Supabase Auth for external/app users                                                                                                                         |
| **Odoo Config**               | `config/` directory | Odoo database                                                                             | Config files are SSOT; running Odoo DB is SOR                                                                                                                                      |
| **Odoo Modules**              | `addons/` directory | Git (this repo)                                                                           | `addons/ipai/` tracked; `addons/oca/` submodules                                                                                                                                   |
| **OCA Baseline**              | `addons.manifest.yaml` | Git submodules                                                                         | 34 repos, tiered 0-9, validator + CI gate                                                                                                                                          |
| **Databricks**                | `databricks.yml`    | Databricks workspace                                                                      | DAB bundle is SSOT; workspace is SOR                                                                                                                                               |
| **Supabase Schema**           | Migration files     | Supabase PostgreSQL                                                                       | Append-only for `ops.*` schema                                                                                                                                                     |
| **Secrets**                   | Key Vault / Vault   | Azure Key Vault + Supabase Vault                                                          | Never in Git, never in logs                                                                                                                                                        |
| **n8n Workflows**             | `automations/n8n/`  | n8n runtime                                                                               | JSON exports committed; credentials use references                                                                                                                                 |
| **CI/CD Pipelines**           | `.github/workflows/` | GitHub Actions                                                                            | Workflow YAML is SSOT; run history is SOR                                                                                                                                          |
| **Analytics App Surface**     | Tableau Cloud       | `insightpulseai` site (`10ax.online.tableau.com`)                                          | External BI visualization and workbook delivery surface; downstream of Databricks / Supabase / Odoo exports; not SOR or SSOT                                                      |

**Hard boundary**: Databricks, n8n, Azure Front Door, and Tableau Cloud never become SSOT or SOR. They are compute/delivery/presentation surfaces that consume data mastered elsewhere.

---

## 2. Azure Resource Inventory

### 2.1 Subscription

| Field           | Value                                  |
| --------------- | -------------------------------------- |
| Name            | TBWA-TaskForce-AI                      |
| ID              | `bc849566-6392-4ecb-8fdd-ef4a7c24864d` |
| Tenant          | TBWA tenant (Entra ID)                 |
| Spending limit  | Off                                    |
| Default region  | Southeast Asia (`southeastasia`)       |

### 2.2 Current State (57 Confirmed Resources)

> **Authoritative current-state inventory**: `infra/ssot/azure/resources.yaml`
>
> The YAML file is the SSOT for what exists today. This section provides a summary only.

**Resource Groups (8 owned + 2 managed)**:

| Resource Group | Owner Domain | Resource Count | Purpose |
|---|---|---|---|
| `rg-ipai-dev` | odoo | 12 | Canonical Odoo runtime (Deployment B): web/worker/cron + PG + ACR + KV |
| `rg-ipai-shared-dev` | infra | 8 | Shared services: Front Door, WAF, Key Vault, App Insights, Log Analytics, ACR |
| `rg-ipai-ai-dev` | ai | 13 | Databricks, OpenAI, AI Search, Document Intelligence, Language, Computer Vision |
| `rg-ipai-agents-dev` | platform | 10 | Earlier Odoo deployment (A), Supabase VM, debug container |
| `rg-ipai-data-dev` | lakehouse | 1 | Shared PG Flexible Server |
| `rg-ipai-devops` | devops | 3 | Dev Center, Managed DevOps Pool |
| `rg-data-intel-ph` | ai | 2 | Azure Foundry resource + project |
| `rg-dbw-managed-ipai-dev` | lakehouse (managed) | 3 | Databricks-managed: identity, storage, access connector |
| `NetworkWatcherRG` | infra (managed) | 1 | Azure platform auto-created |
| `ai_appi-..._managed` | infra (managed) | 1 | Application Insights auto-created |

**Resource type distribution**:

| Type | Count |
|---|---|
| Container Apps | 7 |
| Container App Jobs | 3 |
| Container Apps Environments | 2 |
| Container Registries | 2 |
| PG Flexible Servers | 2 |
| Key Vaults | 2 |
| Managed Identities | 4 |
| NSGs | 4 |
| Virtual Networks | 2 |
| AI/Cognitive Services | 5 |
| Storage Accounts | 2 |
| Front Door + WAF | 2 |
| Monitoring (App Insights, Log Analytics) | 4 |
| VM + associated (disk, NIC, IP) | 4 |
| DevOps (Dev Center, Pool, Org) | 4 |
| Foundry | 2 |
| Other (LB, DNS zone, Databricks, Network Watcher, etc.) | 6 |

### 2.3 Exceptions

| ID | Title | Risk | Status | Artifact |
|---|---|---|---|---|
| EXC-001 | Dual Odoo Container App Deployments | HIGH | Unresolved | `exceptions/dual-odoo-deployment.yaml` |

**EXC-001 Summary**: Two complete Odoo deployment surfaces exist:
- **Deployment A** (`rg-ipai-agents-dev`): `odoo-web` + `odoo-init`, using shared `pg-ipai-dev` and `cripaidev`
- **Deployment B** (`rg-ipai-dev`): `ipai-odoo-dev-web/worker/cron` + jobs, using dedicated `ipai-odoo-dev-pg`, `ipaiodoodevacr`, `ipai-odoo-dev-kv`

Architectural signal points to Deployment B as the intended canonical surface (matches `odoo-runtime.yaml` 3-role spec), but canonical status is formally UNKNOWN until resolved.

### 2.4 Naming Convention Deviations

Target convention: `{type}-ipai-{env}` (e.g., `fd-ipai-dev`, `acr-ipai-dev`)

| Actual Name | Expected Convention | Decision |
|---|---|---|
| `ipai-fd-dev` | `fd-ipai-dev` | Accepted (D-002) |
| `ipaiDevWafPolicy` | `waf-ipai-dev` | Accepted (D-002) |
| `cripaidev` | `acr-ipai-dev` | Accepted (D-002) |
| `ipaiodoodevacr` | `acr-ipai-odoo-dev` | Accepted (D-002) |
| Databricks-managed resources | N/A | Do not normalize (managed) |

Rename is deferred to a future pass. Current names documented as-is in `resources.yaml`.

### 2.5 Target-State Resources (Not Yet Deployed)

These resources are planned but do **not exist** in the portal. They represent the target architecture.

**Planned Resource Group: `rg-ipai-network`** (Hub-Spoke Networking)

| Resource | Type | Purpose |
|---|---|---|
| `vnet-ipai-hub` | Virtual Network | Hub network |
| `vnet-ipai-spoke-dev` | Virtual Network | Spoke for dev workloads |
| `peer-hub-spoke-dev` / `peer-spoke-dev-hub` | VNet Peering | Hub-spoke connectivity |
| `bastion-ipai-dev` | Azure Bastion | Secure VM access |
| `nsg-ipai-spoke-dev` | NSG | Spoke firewall rules |

**Planned Resource Group: `rg-ipai-monitoring`** (Observability)

| Resource | Type | Purpose |
|---|---|---|
| `grafana-ipai-dev` | Managed Grafana | Dashboards + alerting |
| `prom-ipai-dev` | Azure Monitor (Prometheus) | Metrics collection |
| `ag-ipai-dev` | Action Group | Alert routing |
| Metric alerts (CPU, error rate, PG connections) | Metric Alert | Threshold alerting |

**Planned Resource Group: `rg-ipai-backup`** (DR)

| Resource | Type | Purpose |
|---|---|---|
| `rsv-ipai-dev` | Recovery Services Vault | Backup vault |
| `policy-daily-30d` / `policy-weekly-90d` | Backup Policy | Retention policies |
| `st-ipai-backup` | Storage Account (Cool) | Long-term backup storage |
| `lock-ipai-backup` | Resource Lock | Prevent accidental deletion |

**Planned Data Platform Resources** (evaluate before provisioning)

| Resource | Type | Status |
|---|---|---|
| `adf-ipai-dev` | Data Factory | Evaluate: ADF vs Databricks Autoloader for CDC |
| `evh-ipai-dev` | Event Hub | Evaluate: needed for real-time CDC? |
| `cosmos-ipai-dev` | Cosmos DB | Evaluate: needed, or PG JSONB sufficient? |
| `synapse-ipai-dev` | Synapse Analytics | Evaluate: decommission if Databricks SQL covers use cases |
| `ml-ipai-dev` | ML Workspace | Evaluate: consolidate MLflow to Databricks? |
| `purview-ipai-dev` | Microsoft Purview | Planned: provision when Unity Catalog lineage ready |

### 2.6 Reconciliation

Full reconciliation report: `RESOURCE_RECONCILIATION_REPORT.md`

| Metric | Count |
|---|---|
| Portal confirmed resources | 57 |
| Previously documented (resources.yaml v1.0) | ~17 |
| Newly documented | 40 |
| Managed/auto-created | 8 |
| Target-state aspirational (not deployed) | ~31 |
| Naming deviations (non-managed) | 4 |
| Unresolved exceptions | 1 |

---

## 3. DNS Target State

### Primary Domain: `insightpulseai.com`

| Subdomain       | Type  | Target                                  | Purpose                    | State    |
| --------------- | ----- | --------------------------------------- | -------------------------- | -------- |
| `@` (apex)      | CNAME | `ipai-fd-dev-ep-fnh4e8d6gtdhc8ax.z03.azurefd.net` | Root domain                | Active   |
| `www`           | CNAME | `ipai-fd-dev-ep-fnh4e8d6gtdhc8ax.z03.azurefd.net` | WWW redirect               | Active   |
| `erp`           | CNAME | `ipai-fd-dev-ep-fnh4e8d6gtdhc8ax.z03.azurefd.net` | Odoo ERP                   | Active   |
| `n8n`           | CNAME | `ipai-fd-dev-ep-fnh4e8d6gtdhc8ax.z03.azurefd.net` | n8n automation             | Active   |
| `auth`          | CNAME | `ipai-fd-dev-ep-fnh4e8d6gtdhc8ax.z03.azurefd.net` | Auth service               | Active   |
| `superset`      | CNAME | `ipai-fd-dev-ep-fnh4e8d6gtdhc8ax.z03.azurefd.net` | Apache Superset            | Active   |
| `mcp`           | CNAME | `ipai-fd-dev-ep-fnh4e8d6gtdhc8ax.z03.azurefd.net` | MCP coordinator            | Active   |
| `plane`         | CNAME | `ipai-fd-dev-ep-fnh4e8d6gtdhc8ax.z03.azurefd.net` | Plane project mgmt         | Active   |
| `shelf`         | CNAME | `ipai-fd-dev-ep-fnh4e8d6gtdhc8ax.z03.azurefd.net` | Shelf service              | Active   |
| `crm`           | CNAME | `ipai-fd-dev-ep-fnh4e8d6gtdhc8ax.z03.azurefd.net` | CRM service                | Active   |
| `ops`           | CNAME | `ipai-fd-dev-ep-fnh4e8d6gtdhc8ax.z03.azurefd.net` | Ops console                | Active   |
| `ocr`           | CNAME | `ipai-fd-dev-ep-fnh4e8d6gtdhc8ax.z03.azurefd.net` | OCR service                | Active   |
| `api`           | CNAME | `fd-ipai-shared.azurefd.net`            | API gateway (Front Door)   | Planned  |
| `app`           | CNAME | `fd-ipai-shared.azurefd.net`            | App frontend (Front Door)  | Planned  |
| `data`          | CNAME | `dbw-ipai-dev.azuredatabricks.net`      | Databricks workspace       | Planned  |
| `mail`          | CNAME | `mailgun.org`                           | Mailgun verification       | Active   |
| `email.mg`      | CNAME | `mailgun.org`                           | Mailgun DKIM               | Active   |
| `agent`         | CNAME | `*.agents.do-ai.run`                    | AI agent                   | Active   |

### DNS Migration Path

```
Phase 1 (Done):     DNS cut to Azure Front Door (canonical subdomains on AFD)
Phase 2 (Done):     Remaining DO-backed origins moved to Azure runtimes
Phase 3 (Done):     DO droplet decommissioned (snapshot complete, droplet deleted)
```

### Deprecated Domains (Never Use)

| Domain               | Status      | Replacement           |
| -------------------- | ----------- | --------------------- |
| `insightpulseai.net` | Deprecated  | `insightpulseai.com`  |
| `*.insightpulseai.net` | Deprecated | `*.insightpulseai.com` |

---

## 4. Identity & Auth Architecture

### Target Identity Stack

```
                    ┌─────────────────┐
                    │   Entra ID      │
                    │   (Primary IdP) │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────────┐
        │ Keycloak │  │ Supabase │  │ Azure AD B2C │
        │ (Bridge) │  │  Auth    │  │ (Future)     │
        └────┬─────┘  └────┬─────┘  └──────────────┘
             │              │
    ┌────────┼────────┐     │
    ▼        ▼        ▼     ▼
  Odoo    Plane    Superset  Apps
  n8n     Shelf    CRM       Edge Functions
```

**Target**: Entra ID as primary identity provider for admin surfaces -- Odoo, n8n, Plane, Shelf, CRM, Superset, Databricks. Tableau Cloud uses connector-based auth (not SSO).

### Identity Mapping

| Surface       | Current Auth     | Target Auth              | Protocol  |
| ------------- | ---------------- | ------------------------ | --------- |
| Odoo 18       | Local DB         | Entra ID via Keycloak    | OIDC      |
| n8n           | Local DB         | Entra ID via Keycloak    | OIDC      |
| Superset      | Local DB         | Entra ID via Keycloak    | OIDC      |
| Databricks    | Entra ID         | Entra ID (no change)     | SAML/OIDC |
| Tableau Cloud | Tableau Identity | Connector credentials    | N/A       |
| Plane         | Local DB         | Entra ID via Keycloak    | OIDC      |
| Supabase      | Supabase Auth    | Supabase Auth + Entra ID | OIDC      |
| GitHub        | GitHub Identity  | GitHub + Entra ID SSO    | SAML      |
| Azure Portal  | Entra ID         | Entra ID (no change)     | Native    |

### Service Accounts / Managed Identities

| Identity              | Type              | Scope                              | Credential Store    |
| --------------------- | ----------------- | ---------------------------------- | ------------------- |
| `id-ipai-shared`      | Managed Identity  | ACR pull, Key Vault read, PG auth  | Azure (no creds)    |
| `sp-ipai-ci`          | Service Principal | GitHub Actions OIDC federation     | Federated (no secret) |
| `odoo-sa`             | PG role           | Odoo database access               | Key Vault           |
| `n8n-sa`              | PG role           | n8n database access                | Key Vault           |
| `supabase-sa`         | PG role           | Supabase schema access             | Supabase Vault      |

---

## 5. Databricks Intelligence Layer

### Workspace Configuration

| Setting              | Value                                              |
| -------------------- | -------------------------------------------------- |
| Workspace            | `dbw-ipai-dev`                                     |
| Region               | Southeast Asia                                     |
| Unity Catalog        | `ipai_dev`                                         |
| Default cluster      | Single-node, Standard_DS3_v2, auto-terminate 30min |
| Storage (ADLS Gen2)  | `st-ipai-lake-dev`                                 |

### Medallion Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Bronze     │     │   Silver     │     │    Gold      │     │  Platinum    │
│              │ ──► │              │ ──► │              │ ──► │              │
│  Raw ingest  │     │  Cleaned +   │     │  Business    │     │  ML features │
│  JSON/CSV    │     │  normalized  │     │  aggregates  │     │  + serving   │
│              │     │  typed       │     │  star schema │     │              │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
     ▲                                                               │
     │                                                               ▼
  Sources:                                                     Consumers:
  - Odoo PG (CDC)                                             - Superset
  - Supabase (webhooks)                                       - Tableau Cloud
  - n8n (event stream)                                        - Databricks Dashboards
  - External APIs                                             - AI Search index
  - File uploads                                              - Azure OpenAI (RAG)
```

### Unity Catalog Schema

| Catalog     | Schema       | Purpose                              |
| ----------- | ------------ | ------------------------------------ |
| `ipai_dev`  | `bronze`     | Raw ingested data                    |
| `ipai_dev`  | `silver`     | Cleaned, typed, deduplicated         |
| `ipai_dev`  | `gold`       | Business aggregates, star schema     |
| `ipai_dev`  | `platinum`   | ML features, model inputs/outputs    |
| `ipai_dev`  | `sandbox`    | Ad-hoc exploration (auto-expire 7d)  |

### Databricks Apps (Planned)

| App                    | Purpose                          | Status   |
| ---------------------- | -------------------------------- | -------- |
| `scout-dashboard`      | Brand intelligence dashboard     | Active   |
| `juicer-analytics`     | Content analytics                | Active   |
| `retail-advisor`       | Retail AI recommendations        | Active   |
| `insights-dashboard`   | Executive insights               | Active   |
| `finance-analytics`    | Financial reporting              | Planned  |
| `hr-analytics`         | HR metrics and workforce         | Planned  |
| `ops-monitor`          | Operational monitoring           | Planned  |
| `compliance-tracker`   | BIR compliance tracking          | Planned  |

---

## 6. Odoo 18 CE Development Conventions

### Module Structure

```
addons/ipai/ipai_<domain>_<feature>/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── <model_name>.py
├── views/
│   └── <model_name>_views.xml
├── security/
│   ├── ir.model.access.csv
│   └── security.xml
├── data/
│   └── <data_files>.xml
├── wizards/                    # (optional)
├── reports/                    # (optional)
├── static/                     # (optional)
│   └── description/
│       └── icon.png
└── tests/
    ├── __init__.py
    └── test_<feature>.py
```

### Manifest Convention

```python
{
    "name": "IPAI <Domain> <Feature>",
    "version": "19.0.1.0.0",
    "category": "<Odoo Category>",
    "summary": "<One-line description>",
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.com",
    "license": "LGPL-3",
    "depends": ["base"],           # Minimal dependencies
    "data": [],
    "installable": True,
    "application": False,          # True only for top-level apps
    "auto_install": False,
}
```

### Database Naming

| Environment | Database   | Purpose               |
| ----------- | ---------- | --------------------- |
| Production  | `odoo`     | Production ERP        |
| Development | `odoo_dev` | Local development     |
| Testing     | `test_*`   | Disposable test DBs   |

**Never use** `odoo_core`, `odoo_db`, `postgres`, or any other database names.

### Key Scripts

| Script                                    | Purpose                        |
| ----------------------------------------- | ------------------------------ |
| `scripts/odoo/install_module.sh`          | Install/update a module        |
| `scripts/odoo/run_tests.sh`              | Run module tests               |
| `scripts/odoo/backup_db.sh`              | Backup database                |
| `scripts/odoo/restore_db.sh`             | Restore database               |
| `scripts/odoo/validate_addons_manifest.py`| Validate addons manifest       |

---

## 7. End-to-End Data Flow

```
┌─────────────┐    ┌──────────┐    ┌──────────────┐    ┌────────────┐
│  Odoo 18    │    │   n8n    │    │  Databricks  │    │  Consumers │
│  (Source)   │───►│ (ETL)   │───►│  (Lakehouse) │───►│            │
│             │    │          │    │              │    │  Superset  │
│  Invoices   │    │  Extract │    │  Bronze →    │    │  Tableau   │
│  Payments   │    │  Transform│   │  Silver →    │    │  Dashboards│
│  HR records │    │  Load    │    │  Gold        │    │  AI Search │
│  Inventory  │    │          │    │              │    │  Reports   │
└──────┬──────┘    └──────────┘    └──────┬───────┘    └────────────┘
       │                                   │
       │                                   │
       ▼                                   ▼
┌──────────────┐                    ┌──────────────┐
│  PostgreSQL  │                    │  ADLS Gen2   │
│  (pg-ipai)   │                    │  (st-ipai-   │
│              │                    │   lake-dev)  │
│  Odoo tables │                    │  Parquet/    │
│  n8n tables  │                    │  Delta Lake  │
│  Supabase    │                    │              │
└──────────────┘                    └──────────────┘
```

### Data Flow Rules

1. **Odoo is SOR** for all ERP transactional data (invoices, payments, HR, inventory)
2. **n8n orchestrates** ETL -- never direct DB-to-DB copies
3. **Databricks is the compute layer** -- all transformations happen here
4. **ADLS Gen2 is the storage layer** -- all lakehouse data lands here
5. **Consumers read from Gold** -- never from Bronze or Silver
6. **Supabase is the control plane** -- auth, realtime, edge functions
7. **PostgreSQL (pg-ipai-dev)** hosts Odoo, n8n, and Supabase schemas on one server

### CDC (Change Data Capture) Pattern

```python
# n8n webhook receives Odoo model changes
# Triggered by ir.actions.server on write/create/unlink

# Odoo → n8n webhook → Databricks (Autoloader)
# Flow: model.write() → server action → HTTP POST → n8n → ADLS Bronze → Autoloader
```

---

## 8. n8n Integration

### Workflow Categories

| Category          | Count | Purpose                              |
| ----------------- | ----- | ------------------------------------ |
| GitHub Events     | 5     | PR/issue/push → Odoo tasks          |
| Odoo Sync         | 8     | ERP data → Lakehouse                |
| Slack Alerts      | 4     | CI/deploy/error notifications        |
| Scheduled Jobs    | 6     | Daily/weekly/monthly automation      |
| AI Pipelines      | 3     | Claude/GPT orchestration             |
| Compliance        | 2     | BIR report generation                |

### n8n → Odoo Integration

```javascript
// n8n HTTP Request node → Odoo JSON-RPC
{
  "method": "POST",
  "url": "{{ $env.ODOO_URL }}/jsonrpc",
  "body": {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "service": "object",
      "method": "execute_kw",
      "args": [
        "{{ $env.ODOO_DB }}",
        "{{ $env.ODOO_UID }}",
        "{{ $env.ODOO_PASSWORD }}",
        "project.task",
        "create",
        [{ "name": "{{ $json.title }}", "description": "{{ $json.body }}" }]
      ]
    }
  }
}
```

### n8n Credential References (Mandatory)

All n8n workflows must use credential references, never literal values:

```javascript
// Correct
"{{ $credentials.odoo_jsonrpc.url }}"
"{{ $credentials.odoo_jsonrpc.password }}"

// Wrong -- never do this
"http://erp.insightpulseai.com"
"admin_password_here"
```

---

## 9. Analytics App Surfaces

### Surface Inventory

| Surface                | Type                     | Status        | SOR/SSOT | Notes                                                        |
| ---------------------- | ------------------------ | ------------- | -------- | ------------------------------------------------------------ |
| Databricks Dashboards  | Embedded BI              | Target        | No       | Unity Catalog-native; Genie for NL queries                   |
| Tableau Cloud          | External BI platform     | **Active**    | No       | `insightpulseai` site on `10ax.online.tableau.com`           |
| Superset               | Self-hosted BI           | **Migrate**   | No       | Currently on DO droplet; migrate to Azure Container Apps     |
| Power BI               | Azure-native BI          | **Active**    | No       | Connector to Databricks SQL Warehouse + Azure PG             |

### Tableau Cloud Classification

| Field              | Value                                                                     |
| ------------------ | ------------------------------------------------------------------------- |
| Site               | `insightpulseai`                                                          |
| URL                | `https://10ax.online.tableau.com/#/site/insightpulseai/home`              |
| Classification     | Analytics app / BI consumption surface                                    |
| Offering           | Managed enterprise service (Tableau Cloud license)                        |
| Data Integration   | Connectors (Databricks SQL Warehouse, Supabase PG, Odoo exports/extracts) |
| Auth Model         | Connector credentials only — not SSO, not Entra ID                        |
| SOR                | No                                                                        |
| SSOT               | No                                                                        |
| Presentation Layer | Yes                                                                       |

**Rule**: Tableau Cloud is a managed enterprise analytics application. It consumes data via connectors (Databricks SQL Warehouse, Supabase PG, Odoo file exports) — not via SSO or identity federation. It is a presentation/consumption surface only — never a system of record or source of truth. Workbook definitions and data-source metadata should be inventoried and versioned where possible, but the authoritative data always lives upstream in the lakehouse or operational databases.

### Power BI Classification

| Field              | Value                                                                     |
| ------------------ | ------------------------------------------------------------------------- |
| Type               | Azure-native BI / connector-based analytics                               |
| Data Integration   | Connectors (Databricks SQL Warehouse, Azure PG Flexible Server)           |
| Auth Model         | Entra ID (native Azure SSO)                                               |
| SOR                | No                                                                        |
| SSOT               | No                                                                        |
| Presentation Layer | Yes                                                                       |

**Rule**: Power BI is an Azure-native analytics surface. It connects to Databricks SQL Warehouse and Azure PG via built-in connectors. Unlike Tableau Cloud, Power BI authenticates via Entra ID natively. Like all analytics surfaces, it is a presentation/consumption layer only — never a system of record.

### Analytics Data Flow

```
  Odoo (SOR)  ──►  Databricks Gold  ──►  Tableau Cloud (presentation, connector auth)
                        │
  Supabase    ──►───────┤──────────────►  Databricks Dashboards (presentation)
                        │
  n8n exports ──►───────┤──────────────►  Superset (presentation, migrating to ACA)
                        │
  Azure PG    ──►───────┘──────────────►  Power BI (presentation, Entra ID auth)
```

---

## 9b. Vercel Deprecation

Vercel is no longer an active deployment target for this repository.

Azure-native infrastructure (Azure Container Apps, Azure Front Door, Azure PG) is the canonical deployment surface. Any remaining Vercel integrations, preview checks, or deployment references are transitional residue and should be removed from CI contracts, documentation, and repository metadata.

| Item                              | Status         | Action                                                |
| --------------------------------- | -------------- | ----------------------------------------------------- |
| `odoo/vercel.json`                | **Removed**    | Deleted — no root-level Vercel config                  |
| `infra/ssot/integrations/vercel_hosting.yaml` | **Deprecated** | Status set to `deprecated`                  |
| `infra/ssot/integrations/vercel_agent.yaml`   | **Deprecated** | Status set to `deprecated`                  |
| `infra/ssot/integrations/vercel_ai_gateway.yaml` | **Deprecated** | Never activated; status set to `deprecated` |
| `infra/ssot/vercel/projects.yaml` | **Deprecated** | Header updated with deprecation notice                |
| `vercel-env-leak-guard.yml`       | **Disabled**   | Trigger changed to `workflow_dispatch` only            |
| `ship-on-deploy.yml`             | **Disabled**   | Was Vercel deployment_status listener; now manual-only |
| Vercel GitHub App                 | Out of scope   | May remain installed; not treated as authoritative     |

**Rule**: Do not add new `vercel.json` files, Vercel project configurations, or workflows that depend on Vercel deployment events. Do not treat Vercel preview deployments as CI gates.

---

## 10. Resources Requiring Action

| Resource                                       | Issue                                                          | Action Required                                                                                      | Priority |
| ---------------------------------------------- | -------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | -------- |
| **EXC-001: Dual Odoo Deployment**              | Two Odoo surfaces across rg-ipai-agents-dev and rg-ipai-dev   | **Resolve canonical deployment before hostname cutover**                                             | P0       |
| DO Droplet (178.128.112.214)                   | Legacy runtime removed                                          | **Completed 2026-03-11: snapshot captured, droplet deleted**                                          | Closed   |
| Supabase (`spdtwktxdalcfigzeqrz`)              | Control plane, 200+ functions with missing `search_path`       | **Run `search_path` fix; enable RLS on unprotected tables**                                          | P1       |
| `debug-odoo-ep` (Container Instances)          | Ephemeral debug container in rg-ipai-agents-dev                | **Audit: delete if no longer needed for troubleshooting**                                            | P1       |
| Dual PG Servers                                | `pg-ipai-dev` (shared) and `ipai-odoo-dev-pg` (dedicated)     | **Resolve as part of EXC-001; consolidate when canonical deployment is decided**                     | P1       |
| Dual Container Registries                      | `cripaidev` (shared) and `ipaiodoodevacr` (dedicated)          | **Resolve as part of EXC-001; consolidate when canonical deployment is decided**                     | P2       |
| Naming convention deviations                   | 4 non-managed resources deviate from `{type}-ipai-{env}`       | **Deferred: rename in a future pass after topology is locked**                                       | P3       |
| `grafana-ipai-dev` / `prom-ipai-dev`           | Planned but not yet provisioned                                | **Provision when monitoring requirements are finalized**                                              | P3       |
| Hub-spoke networking                           | Planned but not yet provisioned                                | **Provision when network isolation requirements are finalized**                                       | P3       |
| `purview-ipai-dev` (Purview)                   | Planned for data governance                                    | **Provision when Unity Catalog lineage integration is ready**                                        | P3       |
| Tableau Cloud (`insightpulseai`)               | Active BI surface, connector-only auth (decided)               | **Inventory workbooks, data sources, owners, refresh paths; document connector credentials**         | P2       |

---

## 11. CI/CD Contract

### GitHub Actions OIDC Federation

```yaml
# .github/workflows/deploy.yml
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

**No service principal secrets stored in GitHub** -- OIDC federation only.

### Pipeline Matrix

| Workflow                     | Trigger        | Target                    | Gate              |
| ---------------------------- | -------------- | ------------------------- | ----------------- |
| `ci-odoo-ce.yml`             | Push/PR        | Odoo module tests         | Must pass         |
| `ci-odoo-oca.yml`            | Push/PR        | OCA compliance            | Must pass         |
| `addons-manifest-guard.yml`  | Push/PR        | Addons manifest validation| Must pass         |
| `spec-kit-enforce.yml`       | Push/PR        | Spec bundle structure     | Must pass         |
| `build-unified-image.yml`    | Push to main   | ACR image build           | Must pass         |
| `deploy-production.yml`      | Tag `v*`       | Container Apps deploy     | Manual approval   |
| `dns-ssot-apply.yml`         | Push to main   | Cloudflare DNS            | Auto on merge     |
| `security.yml`               | Push/PR        | GitLeaks + Semgrep + Trivy| Must pass         |

### Image Build & Deploy Flow

```
Push to main
    │
    ▼
Build unified image ──► acr-ipai-dev.azurecr.io/odoo:sha-<commit>
    │
    ▼
Tag release (v*)
    │
    ▼
Manual approval gate
    │
    ▼
Deploy to Container Apps (ca-ipai-dev)
    │
    ▼
Health check ──► Rollback if unhealthy
```

---

## 12. 30-Day Sprint (2026-03-11 to 2026-04-10)

| #  | Item                                              | Owner    | Target Date | Status   |
| -- | ------------------------------------------------- | -------- | ----------- | -------- |
| 1  | Audit `plan-ipai-dev` and `pulser-poc-*` usage    | Platform | 2026-03-15  | Planned  |
| 2  | Run Supabase `search_path` fix + RLS hardening    | Platform | 2026-03-15  | Planned  |
| 3  | Configure GitHub Actions OIDC federation           | DevOps   | 2026-03-18  | Planned  |
| 4  | Build unified Docker image pipeline               | DevOps   | 2026-03-20  | Planned  |
| 5  | Deploy Odoo 18 to Container Apps (dev)             | Platform | 2026-03-22  | Planned  |
| 6  | Deploy n8n to Container Apps (dev)                 | Platform | 2026-03-24  | Planned  |
| 7  | Configure Front Door routing for api.* / app.*     | Platform | 2026-03-26  | Planned  |
| 8  | Set up Keycloak → Entra ID OIDC bridge             | Identity | 2026-03-28  | Planned  |
| 9  | Evaluate Synapse vs Databricks SQL                 | Data     | 2026-03-30  | Planned  |
| 10 | Evaluate ADF vs Autoloader for CDC                 | Data     | 2026-03-30  | Planned  |
| 11 | DO droplet migration runbook                       | Platform | 2026-04-05  | Planned  |
| 12 | Provision Grafana + Prometheus (if approved)       | Platform | 2026-04-10  | Planned  |
| 13 | Tableau Cloud workbook/data-source inventory       | Data     | 2026-03-20  | Planned  |

---

## 13. Hard Constraints

1. **No Odoo Enterprise modules** -- CE + OCA + ipai_* only
2. **No hardcoded secrets** -- Key Vault / Supabase Vault / env vars only
3. **No console-only infra changes** -- every change has a repo commit
4. **No direct DB schema edits** -- migrations only
5. **OCA modules are read-only** -- override via `ipai_*`, never patch OCA source
6. **Databricks, n8n, Azure Front Door, and Tableau Cloud never become SSOT or SOR**
7. **DNS changes are YAML-first** -- `subdomain-registry.yaml` → generator → Terraform
8. **`insightpulseai.net` is permanently deprecated** -- never reintroduce
9. **Mattermost is permanently deprecated** -- Slack only
10. **Single PG server per environment** -- no database sprawl (**currently violated**: see EXC-001)
11. **All services must support Entra ID SSO** -- no local-only auth in production

---

## 14. Verification Checklist

### Azure Resources

- [ ] All 65 confirmed resources match `infra/ssot/azure/resources.yaml`
- [ ] `id-ipai-agents-dev` managed identity has required role assignments
- [ ] `kv-ipai-dev` access policies are configured for managed identities
- [ ] `ipaiodoodevacr` / `cripaidev` are accessible from respective Container Apps Environments
- [ ] `pg-ipai-dev` (rg-ipai-data-dev) hosts expected databases
- [ ] `ipai-odoo-dev-pg` (rg-ipai-dev) hosts Odoo database for Deployment B
- [ ] `stipaidevlake` has `bronze`, `silver`, `gold`, `platinum` containers
- [ ] Dual Odoo deployment exception (EXC-001) is tracked and unresolved

### DNS

- [ ] All subdomains resolve to correct targets
- [ ] SSL certificates are valid and auto-renewing
- [ ] No references to `insightpulseai.net` in any config

### Identity

- [ ] Entra ID is configured as IdP
- [ ] Keycloak OIDC clients exist for Odoo, n8n, Superset, Plane
- [ ] Managed identity can pull from ACR without credentials
- [ ] GitHub Actions OIDC federation is configured (no stored secrets)

### Databricks

- [ ] Unity Catalog `ipai_dev` is provisioned
- [ ] Medallion schemas (`bronze`, `silver`, `gold`, `platinum`, `sandbox`) exist
- [ ] ADLS Gen2 storage is mounted and accessible
- [ ] Default cluster auto-terminates after 30 minutes

### CI/CD

- [ ] All "must pass" gates are enforced on PRs
- [ ] Image build pipeline pushes to ACR on merge to main
- [ ] Deploy pipeline requires manual approval for production
- [ ] Security scanning (GitLeaks, Semgrep, Trivy) runs on every push

### Analytics Surfaces

- [ ] Tableau Cloud `insightpulseai` site is accessible and workbooks inventoried
- [ ] Tableau data sources are documented with upstream lineage
- [ ] Superset status: **migrate to ACA** (currently on DO droplet, target: Azure Container Apps)
- [ ] Power BI workspace created and connected to Databricks SQL Warehouse + Azure PG
- [ ] Databricks Dashboards are connected to Gold layer tables

---

*Last updated: 2026-03-11 | Version 1.5.0*
