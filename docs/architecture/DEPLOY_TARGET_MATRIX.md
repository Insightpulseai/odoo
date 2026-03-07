# Deploy Target Decision Matrix

> Canonical decision tree for where workloads run.
> Aligns with `ssot/infra/digitalocean/policy.yaml` (App Platform deprecated).

## Decision Tree

```
Is it Odoo (ERP runtime)?
├── YES → DO Droplet (self-hosted, docker-compose)
│         deploy/odoo-prod.compose.yml
│
└── NO → Is it a serverless function?
         ├── YES → Supabase Edge Functions
         │         supabase/functions/<name>/index.ts
         │
         └── NO → Is it a web app (Next.js, React)?
                  ├── YES → Vercel
                  │         vercel.json in app directory
                  │
                  └── NO → Is it a scheduled job?
                           ├── YES → Supabase pg_cron + Edge Function
                           │
                           └── NO → DO Droplet (container)
```

## Target Matrix

| Workload Type | Deploy Target | Config Location | CI Workflow |
|---------------|---------------|-----------------|-------------|
| **Odoo ERP** | DO Droplet (docker-compose) | `deploy/odoo-prod.compose.yml` | `odoo-azure-deploy.yml` |
| **Edge Functions** | Supabase Edge | `supabase/config.toml` | `supabase-functions-deploy.yml` |
| **Web apps** (ops-console, web) | Vercel | `apps/*/vercel.json` | Vercel Git integration |
| **Scheduled jobs** | Supabase pg_cron | `supabase/migrations/` | Migration deploy |
| **n8n workflows** | DO Droplet (container) | `automations/n8n/` | Manual deploy |
| **Static docs** | Vercel | `apps/docs/` | Vercel Git integration |

## Platform Status

| Platform | Status | Use Case |
|----------|--------|----------|
| **DO Droplet** | Active | Odoo runtime, n8n, containers |
| **Supabase Edge** | Active | Serverless functions (81 deployed) |
| **Vercel** | Active | Web apps, static sites |
| **DO App Platform** | **Deprecated** | DO NOT use. See `ssot/infra/digitalocean/policy.yaml` |
| **Azure Container Apps** | Planned | Future Odoo runtime target |

## Why This Split

- **Odoo** needs persistent filesystem (filestore), long-running processes, and direct PostgreSQL access. Droplet is the only fit.
- **Edge Functions** are stateless, event-driven, and benefit from Supabase's native integration (auth, database, storage).
- **Web apps** are static/SSR builds that Vercel handles optimally (CDN, preview deploys, zero-config).
- **DO App Platform** was deprecated because it adds cost and complexity without benefits over the Droplet + Vercel + Edge split.

## Marketplace and ecosystem classification

Marketplace and ecosystem evidence indicate two different maturity patterns:

- SAP has a first-class Azure ecosystem shape, including deeper Microsoft integration surfaces and a productized Databricks-aligned data/AI path.
- Odoo appears primarily as a broad application platform with partner-packaged hosting and integration options, not as a first-class Azure workload category.

Therefore, the canonical Odoo deployment baseline must remain first-party Azure primitives plus repository-owned IaC and CI/CD, not Marketplace listings.
