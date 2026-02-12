# IPAI Databricks – Constitution

## Non-negotiable Principles

1. **Self-Hosted Parity, Not Vendor Clone**
   - Target *functional* parity with Databricks (data engineering, lakehouse, apps, AI governance) while remaining fully self-hosted on:
     - Supabase (Postgres + storage + Edge Functions + MCP)
     - DigitalOcean (Droplets / managed Postgres / object storage)
     - Vercel (Next.js apps, AI Gateway, Sandbox where useful)
     - Odoo CE + OCA (ERP system of record)

2. **Supabase-First Lakehouse**
   - Supabase Postgres is the primary "lakehouse brain":
     - `bronze_*` (raw/landing), `silver_*` (cleaned), `gold_*` (BI/AI-ready), `platinum_*` (ML/AI features).
     - Object storage (Supabase buckets / DO Spaces) for large binary data.
   - All access goes through:
     - RLS-enforced views
     - RPCs / Edge Functions
     - Supabase MCP server for agents.

3. **Control Plane & Secrets in Supabase**
   - Supabase is the **control plane** for:
     - Secrets (Vault)
     - Connector configs
     - Job definitions
     - Agent registrations & policies
   - No hard-coded secrets in code. All runtime access via Supabase Vault or DO secret stores.

4. **Odoo CE + OCA as ERP System of Record**
   - Odoo CE + curated OCA stack provide:
     - Finance, accounting, tax, ops, HR, project, sales.
   - IPAI Databricks treats Odoo as:
     - A governed data source (for replication)
     - A governed data sink (for write-backs) via explicit APIs/jobs.

5. **IPAI Connectors Over "Direct Fivetran"**
   - No direct Fivetran dependency.
   - Instead: IPAI Connector Framework inspired by Fivetran:
     - `ipai_connector_*` services as Edge Functions / n8n workflows.
     - Odoo, GitHub, File, Event, Database, Warehouse, Figma, n8n, MCP, Mail, etc.

6. **Databricks-Style Roles, Not Vendor Lock-in**
   - Mirror Databricks roles conceptually:
     - Platform Admin, Data Engineer, Analytics Engineer, BI Developer, AI Engineer, Operator, Auditor.
   - Implement via:
     - Postgres roles, Supabase RLS, JWT claims, Supabase Auth policies.

7. **Apps Close to Data**
   - *Apps* run on:
     - Vercel (Next.js) against Supabase (primary)
     - Optional DO app platform for heavier workloads.
   - Apps never bypass governance: all data comes via governed APIs/views.

8. **Agent Governance as First-Class Feature**
   - AI agents (Pulser, Claude, Gemini, etc.) treated like apps:
     - Registered in catalog
     - Bound to data scopes and operations
     - Logged, observable, and revocable.

9. **Spec-to-Code Discipline**
   - Every feature/change in IPAI Databricks must:
     - Ship with a Spec Kit (constitution, PRD, plan, tasks).
     - Have CI checks to enforce presence and basic validity.

10. **License Hygiene**
    - Respect Odoo, OCA, Supabase, Vercel, DO, Databricks, Fivetran, Figma licenses.
    - No copying proprietary code; only patterns/architecture.

## Guardrails

- No direct use of Databricks managed services.
- No direct Fivetran pipelines.
- No ungoverned data access paths.
- All "connector-like" behavior must be implemented via:
  - IPAI Connector Framework
  - Supabase functions / DO jobs / n8n flows.

## Architecture Pillars

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           IPAI Databricks Stack                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│   │   Apps      │  │   Agents    │  │ Dashboards  │  │   APIs      │       │
│   │  (Vercel)   │  │  (Pulser)   │  │ (Superset)  │  │  (REST)     │       │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘       │
│          │                │                │                │               │
│          └────────────────┴────────────────┴────────────────┘               │
│                                    │                                        │
│                         ┌──────────▼──────────┐                             │
│                         │   Governance Layer   │                            │
│                         │  (RLS + Auth + Audit)│                            │
│                         └──────────┬──────────┘                             │
│                                    │                                        │
│   ┌────────────────────────────────┼────────────────────────────────┐      │
│   │                    Supabase Lakehouse                           │      │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │      │
│   │  │ Bronze  │→ │ Silver  │→ │  Gold   │→ │Platinum │            │      │
│   │  │  (raw)  │  │(cleaned)│  │(analytic)│ │(ML/AI)  │            │      │
│   │  └─────────┘  └─────────┘  └─────────┘  └─────────┘            │      │
│   └────────────────────────────────┬────────────────────────────────┘      │
│                                    │                                        │
│                         ┌──────────▼──────────┐                             │
│                         │ IPAI Connector Layer │                            │
│                         │ (Edge Funcs / n8n)   │                            │
│                         └──────────┬──────────┘                             │
│                                    │                                        │
│   ┌────────────┬────────────┬──────┴──────┬────────────┬────────────┐      │
│   │   Odoo CE  │   GitHub   │    Files    │  Databases │   Events   │      │
│   └────────────┴────────────┴─────────────┴────────────┴────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Enforcement

This constitution is enforced via:
- CI spec kit validation
- Code review checklist
- Architecture decision records (ADRs)
- Quarterly compliance audits
