# Deployment Target Matrix

> Canonical reference for where each workload type deploys and why.

| Platform | Workload Type | CI Trigger | Why Here | Examples |
|----------|--------------|------------|----------|----------|
| **GitHub Actions** | CI/CD orchestration | Push/PR/schedule | Canonical CI/CD engine | Lint, test, build, deploy triggers |
| **DigitalOcean Droplet** | Core services (consolidated) | GitHub Actions → SSH | Cost-optimized, self-hosted | Odoo ERP, n8n, OCR Service, Auth |
| **DigitalOcean App Platform** | Specialized agents | GitHub Actions → DO API | Always-on, managed | DevOps Engineer, BI Architect, Finance SSC |
| **Databricks (Azure)** | Data platform workloads | DABs / GitHub Actions | Unity Catalog, Spark compute | Connectors, DLT pipelines, Gold marts, ML |
| **Vercel** | Customer-facing web | GitHub push (auto) | Edge CDN, Next.js native | insightpulseai.com, ops console |
| **Supabase** | External integrations | GitHub Actions / n8n | Edge Functions, Realtime | Task bus, n8n bridge, pgvector search |
| **Azure DevOps** | Program overlay ONLY | N/A (not CI/CD) | Enterprise program mgmt | Boards (if retained), executive dashboards |

## Key Rules

1. **No duplicate CI/CD**: GitHub Actions is the sole CI/CD engine
2. **Azure DevOps is NOT a deployment target**: It's a program management overlay only
3. **Databricks deployment**: Via DABs (Databricks Asset Bundles), triggered by GitHub Actions or manual
4. **DigitalOcean**: Consolidated on single droplet (178.128.112.214) for cost optimization
5. **Vercel**: Auto-deploys from GitHub, no manual pipeline needed
