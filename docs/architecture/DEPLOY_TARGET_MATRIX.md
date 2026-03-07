# Deploy Target Decision Matrix

> Canonical decision tree for where workloads run.
> Aligns with `ssot/azure/target-state.yaml` and `ssot/azure/service-matrix.yaml`.

## Decision Tree

```
Is it Odoo (ERP runtime)?
├── YES → Target State: Azure Container Apps (migration from DO Droplet)
│         Current: DO Droplet (docker-compose) — deploy/odoo-prod.compose.yml
│         Target:  Azure Container Apps + PostgreSQL Flexible Server
│
└── NO → Is it a serverless function?
         ├── YES → Supabase Edge Functions
         │         supabase/functions/<name>/index.ts
         │
         └── NO → Is it a web app (Next.js, React)?
                  ├── YES → Vercel
                  │         vercel.json in app directory
                  │
                  └── NO → Is it a data/AI workload?
                           ├── YES → Databricks Lakehouse (NOT in delivery path)
                           │
                           └── NO → Is it a scheduled job?
                                    ├── YES → Supabase pg_cron + Edge Function
                                    │
                                    └── NO → Azure Container Apps (platform services)
```

## Target Matrix

| Workload Type | Current Target | Target State | Config Location | CI Workflow |
|---------------|----------------|--------------|-----------------|-------------|
| **Odoo ERP** | DO Droplet (docker-compose) | Azure Container Apps | `deploy/odoo-prod.compose.yml` | `odoo-azure-deploy.yml` |
| **Edge Functions** | Supabase Edge | Supabase Edge | `supabase/config.toml` | `supabase-functions-deploy.yml` |
| **Web apps** (ops-console, web) | Vercel | Vercel | `apps/*/vercel.json` | Vercel Git integration |
| **Scheduled jobs** | Supabase pg_cron | Supabase pg_cron | `supabase/migrations/` | Migration deploy |
| **n8n workflows** | DO Droplet (container) | Azure Container Apps | `automations/n8n/` | Manual deploy |
| **Static docs** | Vercel | Vercel | `apps/docs/` | Vercel Git integration |
| **Data/AI workloads** | N/A | Databricks Lakehouse | `spec/azure-target-state/` | GitHub Actions (NOT Databricks) |
| **Platform services** | DO Droplet/App Platform | Azure Container Apps | `deploy/` | GitHub Actions |

## Platform Status

| Platform | Status | Use Case |
|----------|--------|----------|
| **Azure Container Apps** | Planned -- Target State | Odoo runtime, n8n, platform services (migration from DO) |
| **Azure PostgreSQL Flexible** | Planned -- Target State | ERP database (migration from DO-hosted PostgreSQL) |
| **DO Droplet** | Active -- Migration Source | Odoo runtime, n8n, containers (migrating to Azure) |
| **Supabase Edge** | Active | Serverless functions (81 deployed) |
| **Vercel** | Active | Web apps, static sites |
| **Databricks** | Planned | Data/AI plane (analytics, CDP, ML) -- NOT in delivery path |
| **DO App Platform** | **Deprecated** | DO NOT use. See `ssot/infra/digitalocean/policy.yaml` |

## Azure Target State

The target runtime for Odoo ERP and platform services is Azure, replacing the current DigitalOcean Droplet hosting.

### Architecture

```
Azure Front Door Premium (WAF + SSL + CDN + global routing)
    │
    ├── Azure Container Apps (Odoo CE 19 runtime)
    │       ├── odoo-web (Odoo HTTP workers)
    │       ├── odoo-cron (Odoo scheduled actions)
    │       └── n8n (automation engine)
    │
    ├── Azure Database for PostgreSQL Flexible Server
    │       ├── HA enabled
    │       ├── PostgreSQL 16
    │       └── VNet-integrated (private access only)
    │
    ├── Azure Container Registry (ACR)
    │       └── Docker images built by GitHub Actions, pushed to ACR
    │
    ├── Azure Key Vault
    │       └── Secrets, certificates, connection strings
    │
    ├── Azure Managed Identity (Entra ID)
    │       └── Passwordless auth between Container Apps and other Azure services
    │
    ├── Azure Monitor + App Insights + Log Analytics
    │       └── Metrics, traces, logs, alerting
    │
    ├── Azure Virtual Network
    │       ├── NSG rules
    │       ├── Private Link (PostgreSQL, Key Vault, ACR)
    │       └── NAT Gateway (outbound)
    │
    └── Azure Storage Account
            └── Odoo filestore, backups, attachments
```

### Migration Path (DigitalOcean to Azure)

| Component | Current (DO) | Target (Azure) |
|-----------|-------------|----------------|
| **Compute** | DO Droplet (178.128.112.214) | Azure Container Apps |
| **Database** | PostgreSQL 16 on Droplet | Azure PostgreSQL Flexible Server |
| **Container images** | DO Container Registry | Azure Container Registry (ACR) |
| **Edge/CDN** | Cloudflare (proxy) | Azure Front Door Premium |
| **Secrets** | `.env` files on Droplet | Azure Key Vault |
| **Monitoring** | Manual / basic DO metrics | Azure Monitor + App Insights |
| **Networking** | Droplet firewall | Azure VNet + NSG + Private Link |
| **File storage** | Droplet filesystem | Azure Storage Account |

### CI/CD Constraint

GitHub Actions is the sole CI/CD engine. Azure Pipelines, Azure DevOps repos, and Databricks jobs are **prohibited** from the delivery path. All container builds, tests, and deployments are orchestrated via GitHub Actions workflows that push to ACR and deploy to Container Apps.

### Three-Platform Model

```
Azure Boards (insightpulseai org)     GitHub                    Azure + Databricks
───────────────────────────────────   ─────────────────────     ─────────────────────────
Planning only                         Code + CI/CD              Runtime + Data
  - lakehouse project                   - Source control           - Container Apps
  - erp-saas project                    - GitHub Actions           - PostgreSQL Flexible
  - platform project                    - PRs + code review        - Key Vault, VNet, ACR
  - Boards + Delivery Plans             - Releases                 - Databricks Lakehouse
  - NO repos/pipelines/artifacts        - Packages                 - Unity Catalog
                                        - Security scanning        - ML Serving
```

## Why This Split

- **Odoo** needs persistent filesystem (filestore), long-running processes, and direct PostgreSQL access. Container Apps with Azure Storage and PostgreSQL Flexible provides this at scale.
- **Edge Functions** are stateless, event-driven, and benefit from Supabase's native integration (auth, database, storage).
- **Web apps** are static/SSR builds that Vercel handles optimally (CDN, preview deploys, zero-config).
- **Data/AI workloads** run on Databricks, which is purpose-built for lakehouse analytics and ML -- kept separate from the delivery pipeline.
- **DO App Platform** was deprecated because it adds cost and complexity without benefits over the target Azure + Vercel + Edge split.
