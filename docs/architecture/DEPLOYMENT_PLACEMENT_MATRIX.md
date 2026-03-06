# Deployment Placement Matrix

> Where each workload type deploys and why. Use this to make placement decisions.

## Platform Matrix

| Platform | Workload Type | Strengths | Constraints | Examples |
|----------|--------------|-----------|-------------|----------|
| **Databricks Apps** | Data-plane apps | Close to data, UC governed, Spark access | Data team only, no public access | Control Room, DQ Dashboard, Connector Monitor, Analyst Notebooks |
| **Azure Container Apps** | Agent runtime, async workers | Scalable, event-driven, containerized | Requires container packaging | OCR Service, Agent Service, Webhook Receivers, Async Processors |
| **Vercel** | Customer-facing web | Edge CDN, Next.js native, auto-deploy | Static/SSR only, no long-running | insightpulseai.com, Ops Console, Marketing Site |
| **Odoo (DigitalOcean)** | Transactional workflow, ERP | System of truth, business logic | Single server, not horizontally scalable | ERP, Expense, PPM, Close Control, Accounting |
| **DO App Platform** | Specialized agents | Cost-optimized, always-on, managed | Limited compute, no GPU | DevOps Engineer, BI Architect, Finance SSC Expert |
| **Supabase** | External integrations | Edge Functions, Realtime, pgvector | Not for primary OLTP | Task Bus, n8n Bridge, Semantic Search, Auth Bridge |

## Decision Framework

When placing a new workload, ask:

1. **Does it need direct data access (Spark/Unity Catalog)?** → Databricks Apps
2. **Is it customer-facing web?** → Vercel
3. **Is it transactional ERP workflow?** → Odoo
4. **Is it an async worker or webhook handler?** → Azure Container Apps
5. **Is it a specialized AI agent?** → DO App Platform
6. **Is it an integration bridge or edge function?** → Supabase

## Anti-Patterns

| Don't Do This | Do This Instead |
|---------------|----------------|
| Deploy web apps on Databricks | Use Vercel for web |
| Run ERP logic in Azure Container Apps | Keep in Odoo |
| Put analytics dashboards on Vercel | Use Superset or Databricks Apps |
| Run data pipelines on DO Droplet | Use Databricks |
| Store transactional data in Supabase | Use Odoo PostgreSQL |
| Deploy CI/CD on Azure DevOps | Use GitHub Actions |
