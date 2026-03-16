# Skill: Self-Hosted Data Stack — Supabase ETL + CMS + n8n + Azure Native

## Metadata

| Field | Value |
|-------|-------|
| **id** | `self-hosted-data-stack` |
| **domain** | `platform` |
| **source** | supabase/etl, supabase-cms.com, n8n.io |
| **extracted** | 2026-03-16 |
| **applies_to** | odoo, ops-platform, lakehouse, automations |
| **tags** | supabase-etl, supabase-cms, n8n, self-hosted, azure, iceberg, cdc, replication |

---

## Why This Matters

IPAI runs self-hosted on Azure (not SaaS). Every tool in the data stack must be self-hostable or Azure-native. This skill maps the complete self-hosted data stack.

## The Stack (All Self-Hosted / Azure-Native)

```
Sources                    Ingestion              Transform         Serve
────────────────────────────────────────────────────────────────────────────
Odoo PG ──────┐
              │
Supabase PG ──┤── Supabase ETL ──► ADLS Bronze ──► dbt/SDP ──► Gold
              │   (Rust, CDC)       (Parquet/      (Silver)    (marts)
n8n events ───┤                     Iceberg)                     │
              │                                                   │
External ─────┘── n8n workflows ──► Supabase ops.* ──────────────┤
  APIs             (webhooks)       (SSOT)                        │
                                                                  ▼
                                                          ┌──────────────┐
                                                          │ Superset     │
                                                          │ Tableau      │
                                                          │ Databricks   │
                                                          │ Foundry AI   │
                                                          │ Odoo reports │
                                                          └──────────────┘
```

---

## Supabase ETL (CDC Replication)

**Source**: https://github.com/supabase/etl
**License**: Apache 2.0 (open source)
**Language**: Rust

### What It Does

Sits on top of PostgreSQL logical replication. Streams changes in real-time to destinations. High-performance, fault-tolerant, type-safe.

### Supported

| Component | Details |
|-----------|---------|
| **Source** | PostgreSQL 14-18 (15+ recommended for column/row filtering) |
| **Destinations** | BigQuery (CRUD), **Apache Iceberg** (append-only) |
| **Batching** | Configurable parallelism + batch size |
| **Fault tolerance** | Built-in retry + error handling |

### IPAI Relevance

| Use Case | How |
|----------|-----|
| **Odoo PG → ADLS Iceberg** | Supabase ETL captures CDC from `ipai-odoo-dev-pg` → writes Iceberg to ADLS |
| **Supabase PG → ADLS Iceberg** | Same tool for `ops.*` tables → lakehouse Bronze |
| **Real-time** | Changes propagate immediately (not batch) |

### Why This Over Fivetran/Airbyte

| Criteria | Supabase ETL | Fivetran | Airbyte |
|----------|-------------|----------|---------|
| Self-hosted | Yes (Rust binary) | No (SaaS) | Yes (Docker) |
| Cost | Free (Apache 2.0) | $1-50K/month | Free (open-core) |
| Iceberg native | **Yes** | Via Databricks | Via connector |
| CDC quality | PG logical replication (native) | API-based polling | CDC via Debezium |
| Latency | Real-time streaming | Minutes | Minutes |
| Complexity | Low (single binary) | None (managed) | Medium (Docker stack) |

### Installation

```bash
# Add to Cargo.toml
[dependencies]
supabase-etl = "0.1"

# Or run as standalone
cargo install supabase-etl
```

### IPAI Deployment

Deploy as ACA job in `rg-ipai-dev`:
```bash
az containerapp job create \
  --name ipai-etl-odoo-bronze \
  --resource-group rg-ipai-dev \
  --environment ipai-odoo-dev-env \
  --image <acr>/supabase-etl:latest \
  --trigger-type Schedule \
  --cron-expression "*/5 * * * *"
```

---

## Supabase CMS (AI-Powered Headless CMS)

**Source**: https://www.supabase-cms.com/
**License**: Open source
**Stack**: Next.js 16 + Supabase + Prisma + shadcn/ui

### What It Does

AI-powered headless CMS with multi-tenancy, RLS security, content scheduling, SEO. Supports EditorJS, Markdown, HTML.

### IPAI Relevance

| Use Case | How |
|----------|-----|
| **Knowledge base** | Internal docs/KB for agents to search (Foundry IQ source) |
| **Documentation site** | Replace MkDocs with Supabase CMS for `docs-site/` |
| **Client portal content** | Managed content for customer-facing portals |
| **AI Auto-Blog** | Agent-generated content (blog posts, release notes) |

### Features Relevant to IPAI

| Feature | Value |
|---------|-------|
| Multi-tenant | Manage multiple sites from one dashboard |
| AI writing | Claude 3.5/GPT-4o integrated |
| SEO | Semrush keywords, meta tags, Open Graph |
| Auto-blog agent | Edge Function API for autonomous publishing |
| RLS security | Supabase Row Level Security |
| Custom domains | Per-site custom domains |

### Why Consider

Currently IPAI uses MkDocs for docs. Supabase CMS adds:
- AI-assisted content creation
- Multi-tenant site management
- Supabase-native (same stack as ops-platform)
- Edge Function auto-blog agent

### Decision

**Not a priority for R0-R3.** Evaluate for R4+ when docs/KB platform needs upgrade. Current MkDocs is sufficient.

---

## n8n ↔ Odoo Integration (Self-Hosted)

**Source**: https://n8n.io/integrations/odoo/
**Deployment**: Self-hosted Docker on ACA (`n8n.insightpulseai.com`)

### Already Documented

Full integration documented in `skills/integration/n8n-odoo-supabase-etl/SKILL.md`. Key points:

| Capability | Status |
|-----------|--------|
| XML-RPC to Odoo | **Active** (31+ workflows) |
| Supabase bridge | **Active** (HTTP POST to REST API) |
| Built-in Odoo node | Available (not yet migrated from HTTP nodes) |
| Webhook triggers | **Active** |
| Cron scheduling | **Active** |

---

## Complete Self-Hosted Data Stack (Azure-Native)

| Layer | Tool | Hosting | Status |
|-------|------|---------|--------|
| **ERP (SOR)** | Odoo CE 19 | ACA (`ipai-odoo-dev-web`) | **Running** |
| **Control Plane (SSOT)** | Supabase | Azure VM (`vm-ipai-supabase-dev`) | **Running** |
| **Workflow Engine** | n8n | ACA (behind AFD) | **Running** |
| **CDC Replication** | Supabase ETL | ACA job (planned) | **Planned** |
| **Data Lake** | ADLS Gen2 | Azure Storage | **Planned** |
| **Lake Format** | Apache Iceberg (or Parquet) | On ADLS | **Planned** |
| **Transform** | dbt / Lakeflow SDP | Databricks (`dbw-ipai-dev`) | **Planned** |
| **BI** | Apache Superset | ACA (`ipai-superset-dev`) | **Running** |
| **BI (External)** | Tableau Cloud | SaaS connector | **Planned** |
| **AI** | Azure Foundry | Azure AI | **Staging** |
| **Edge/TLS** | Azure Front Door | AFD (`ipai-fd-dev`) | **Running** |
| **DNS** | Cloudflare | SaaS (DNS-only mode) | **Running** |
| **Secrets** | Azure Key Vault | `ipai-odoo-dev-kv` | **Running** |
| **Identity** | Keycloak → Entra | ACA (`ipai-auth-dev`) | **Running** (transitional) |
| **Container Registry** | Azure ACR | `ipaiodoodevacr` | **Running** |
| **Database** | Azure PG Flexible | `ipai-odoo-dev-pg` | **Running** |
| **Lakehouse Compute** | Databricks | `dbw-ipai-dev` (Premium) | **Running** (no data flowing) |
| **CMS** | Supabase CMS (candidate) | Would run on Supabase | **Evaluate R4+** |
| **Mail** | Zoho SMTP + Mailpit | External + ACA sidecar | **Running** |
| **OCR** | Azure Doc Intelligence + PaddleOCR | ACA (`ipai-ocr-dev`) | **Running** |
| **Search** | Azure AI Search | `srch-ipai-dev` | **Provisioned** |

### What's Self-Hosted vs SaaS

| Self-Hosted (Azure) | SaaS (External) |
|--------------------|-----------------|
| Odoo (ACA) | Cloudflare (DNS) |
| Supabase (VM) | Zoho (SMTP) |
| n8n (ACA) | Tableau Cloud (BI) |
| Superset (ACA) | GitHub (SCM) |
| PaddleOCR (ACA) | Stripe/PayPal (payments) |
| Keycloak (ACA) | DragonPay/GCash (PH payments) |
| Mailpit (compose) | |
| All Azure services | |

**Zero vendor lock-in on core data path.** Every component from source (Odoo PG) through transform (Databricks/dbt) to serve (Superset/Foundry) runs on Azure or self-hosted open source.

---

## The Missing Piece: Supabase ETL for CDC

The gap between "data in Odoo PG" and "data in lakehouse" is the CDC layer. Options:

| Option | Effort | Latency | Cost |
|--------|--------|---------|------|
| **Supabase ETL** (Rust, Iceberg-native) | Medium | Real-time | Free |
| **n8n scheduled queries** (current) | Low | Minutes | Free |
| **Lakeflow Connect** (Databricks) | Low | Minutes | DBU cost |
| **Airbyte** (Docker) | Medium | Minutes | Free (open-core) |

**Recommendation**: Start with **Lakeflow Connect** (already have Databricks workspace). Add **Supabase ETL** when real-time CDC is needed or when Iceberg format is adopted.
