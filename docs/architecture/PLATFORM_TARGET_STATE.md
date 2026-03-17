# InsightPulseAI — Platform Target State

**Version:** 1.4.0 | **Last Updated:** 2026-03-11 | **Owner:** Jake Tolentino
**Subscription:** Azure subscription 1 (`536d8cf6-89e1-4815-aef3-d5f2c5f4d070`) | **Primary Region:** Southeast Asia

-----

## Change Log

|Version  |Date          |Changes                                                                                                                                               |
|---------|--------------|------------------------------------------------------------------------------------------------------------------------------------------------------|
|1.0.0    |2026-03-11    |Initial Databricks target state                                                                                                                       |
|1.1.0    |2026-03-11    |DNS + infrastructure + Cloudflare transition architecture integrated                                                                                  |
|1.2.0    |2026-03-11    |Full 55-resource Azure inventory from CSV integrated                                                                                                  |
|1.3.0    |2026-03-11    |Odoo version corrected to 19 CE; `<tree>` removal enforced in CI                                                                                      |
|**1.4.0**|**2026-03-11**|**Full synthesis: all sources merged, SSOT/SOR doctrine, Databricks capabilities, DNS map, auth model, Odoo 19 CE conventions, resource cleanup plan**|

-----

## System Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      CLOUDFLARE (Authoritative DNS)                          │
│             DNS-only for mail · Proxy for apps (transition only)             │
└──────────────────────────────────┬───────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                  AZURE FRONT DOOR  ← Target public edge (provision P1)       │
│            TLS termination · WAF · Hostname routing · Origin shielding       │
└──────┬──────────────┬──────────────┬──────────────┬──────────────────────────┘
       │              │              │              │
       ▼              ▼              ▼              ▼
  ipai-odoo-dev   vm-ipai-        n8n            ipai-plane/shelf/crm-dev
  -web/cron/      supabase-dev    (Container      (Container Apps)
  worker          (SSOT)          App — target)
  (SOR)              │
       │             └──────────────────────────────────────────┐
       │                                                        │
       └─────────────────────────────────┐                      │
                                         ▼                      ▼
                               ┌─────────────────┐   ┌──────────────────────┐
                               │  dbw-ipai-dev   │   │  stipaidevlake       │
                               │  Azure Databricks◄──│  ADLS Gen2           │
                               │  rg-ipai-ai-dev │   │  Bronze/Silver/Gold  │
                               └────────┬────────┘   └──────────────────────┘
                                        │
                          ┌─────────────┼──────────────┐
                          ▼             ▼              ▼
                   Supabase          srch-ipai-dev   oai-ipai-dev
                   ai.* schema       (AI Search)     (Azure OpenAI)
                   (pg-ipai-dev)
                          │
                          ▼
         Finance Copilot · BIR Compliance · MCP Agents · Ops Console
```

-----

## 1. SSOT / SOR Doctrine

|Layer                     |System                      |Azure Resource                                                                        |Role                                                                          |
|--------------------------|----------------------------|--------------------------------------------------------------------------------------|------------------------------------------------------------------------------|
|**System of Record (SOR)**|**Odoo 19 CE**              |`ipai-odoo-dev-web/cron/worker` (Container Apps, `rg-ipai-dev`)                       |ERP transactions, ledger, invoices, tax filings, stock                        |
|**System of Truth (SSOT)**|Supabase                    |`vm-ipai-supabase-dev` + `pg-ipai-dev` (PG Flex, `rg-ipai-data-dev`)                  |Control plane, identity, orchestration state, governance, analytics-ready data|
|**Intelligence Layer**    |Azure Databricks            |`dbw-ipai-dev` (`rg-ipai-ai-dev`)                                                     |ML, feature store, serving endpoints, Gold KPIs                               |
|**Orchestration**         |n8n                         |Target: Container App (`cae-ipai-dev` or `ipai-odoo-dev-env`)                         |Workflow automation, connector glue, retry logic                              |
|**AI Services**           |Azure Cognitive             |`oai-ipai-dev` (OpenAI), `vision-ipai-dev`, `lang-ipai-dev`, `docai-ipai-dev`         |GPT-4, OCR, NLP, Document Intelligence                                        |
|**Search**                |Azure AI Search             |`srch-ipai-dev` (`rg-ipai-ai-dev`)                                                    |Semantic search over Delta Lake + Supabase                                    |
|**AI Foundry**            |Azure AI Foundry            |`data-intel-ph-resource` (`rg-data-intel-ph`, East US 2)                              |AI evaluation, fine-tuning, experiment workspace                              |
|**Public Edge**           |Azure Front Door            |Not yet provisioned — P1                                                               |TLS termination, WAF, hostname routing                                        |
|**DNS**                   |Cloudflare                  |`insightpulseai.com` (authoritative)                                                  |All DNS; mail DNS-only; app records proxy during transition                   |
|**Identity**              |Microsoft Entra ID          |`id-ipai-agents-dev`, `id-ipai-aca-dev`, `id-ipai-databricks-dev`, `dbmanagedidentity`|Workforce SSO + service Managed Identities                                    |
|**Secrets**               |Azure Key Vault             |`kv-ipai-dev` (platform), `ipai-odoo-dev-kv` (Odoo)                                   |All secrets — never in git or env vars                                        |
|**Observability**         |App Insights + Log Analytics|`appi-ipai-dev`, `law-ipai-dev` (`rg-ipai-shared-dev`)                                |Unified telemetry, structured logs                                            |
|**CI/CD**                 |Azure DevOps                |`insightpulseai` org + `ipai-build-pool` (Managed DevOps Pool)                        |Pipeline execution for all services                                           |

**Hard boundary:** Databricks, n8n, and Azure Front Door never become SSOT or SOR. They read from Odoo/Supabase and publish only *derived artifacts* back to Supabase `ai.*`.

-----

## 2. Azure Resource Inventory (55 Resources)

### Resource Group Summary

|Resource Group           |Purpose                                                                       |Count|
|-------------------------|------------------------------------------------------------------------------|-----|
|`rg-ipai-dev`            |Core platform — Odoo 19 CE, Plane, Shelf, CRM (Container Apps) + PG + KV + ACR|12   |
|`rg-ipai-ai-dev`         |AI/ML — Databricks, OpenAI, Search, Vision, Language, DocAI, VNet, NSGs, ADLS |13   |
|`rg-ipai-agents-dev`     |Agent runtime — Supabase VM, CAE, Managed Identity, LB, Networking            |9    |
|`rg-ipai-shared-dev`     |Shared — App Insights, Log Analytics, ACR, Key Vault, Managed Identity        |6    |
|`rg-ipai-devops`         |CI/CD — Dev Center, Managed DevOps Pool, Project                              |3    |
|`rg-dbw-managed-ipai-dev`|Databricks managed — Unity Catalog connector, Managed Identity, Storage       |3    |
|`rg-ipai-data-dev`       |Data — `pg-ipai-dev` (Supabase Postgres PG Flex)                              |1    |
|`rg-data-intel-ph`       |AI Foundry — `data-intel-ph-resource` (East US 2)                             |2    |

### Container Apps — Core Platform (`rg-ipai-dev`)

|Resource              |Type                      |Role                         |Status  |
|----------------------|--------------------------|-----------------------------|--------|
|`ipai-odoo-dev-web`   |Container App             |Odoo 19 CE web frontend (SOR)|Active  |
|`ipai-odoo-dev-cron`  |Container App             |Odoo scheduled jobs          |Active  |
|`ipai-odoo-dev-worker`|Container App             |Odoo async workers           |Active  |
|`ipai-odoo-dev-wave1` |Container App Job         |Odoo migration/wave job      |Active  |
|`ipai-odoo-install`   |Container App Job         |Odoo init job                |Active  |
|`ipai-plane-dev`      |Container App             |Plane project management     |Active  |
|`ipai-shelf-dev`      |Container App             |Shelf.nu asset tracker       |Active  |
|`ipai-crm-dev`        |Container App             |Atomic CRM                   |Active  |
|`ipai-odoo-dev-env`   |Container Apps Environment|Shared CAE for Odoo stack    |Active  |

### Agent Runtime (`rg-ipai-agents-dev`)

|Resource              |Type                      |Role                              |Action    |
|----------------------|--------------------------|----------------------------------|----------|
|`vm-ipai-supabase-dev`|Virtual Machine           |Self-hosted Supabase (SSOT)       |Keep      |
|`cae-ipai-dev`        |Container Apps Environment|Agent + n8n runtime target        |Keep      |
|`odoo-web`            |Container App             |Duplicate of `ipai-odoo-dev-web`  |**Retire**|
|`odoo-init`           |Container App Job         |Duplicate init job                |**Retire**|
|`debug-odoo-ep`       |Container Instance        |Debug artifact                    |**Retire**|

### Databases

|Resource          |Type          |RG                |Role                   |Status |
|------------------|--------------|------------------|-----------------------|-------|
|`pg-ipai-dev`     |PG Flex Server|`rg-ipai-data-dev`|Supabase SSOT Postgres |Active |
|`ipai-odoo-dev-pg`|PG Flex Server|`rg-ipai-dev`     |Odoo 19 CE SOR Postgres|Active |

### AI / ML Stack

|Resource                |Type                 |Location |Role                                        |
|------------------------|---------------------|---------|--------------------------------------------|
|`dbw-ipai-dev`          |Azure Databricks     |SEA      |Intelligence layer — Delta Lake, ML, serving|
|`oai-ipai-dev`          |Azure OpenAI         |East US  |GPT-4o, text-embedding-3-large              |
|`vision-ipai-dev`       |Computer Vision      |SEA      |Image analysis, document pre-processing     |
|`lang-ipai-dev`         |Language             |SEA      |NLP, sentiment, entity extraction           |
|`docai-ipai-dev`        |Document Intelligence|SEA      |Invoice/receipt OCR — BIR compliance        |
|`srch-ipai-dev`         |AI Search            |SEA      |Semantic search across Delta + Supabase     |
|`stipaidevlake`         |Storage (ADLS Gen2)  |SEA      |Databricks Delta Lake — Bronze/Silver/Gold  |
|`data-intel-ph-resource`|AI Foundry + Project |East US 2|Model evaluation, fine-tuning workspace     |

### Security & Identity

|Resource                        |Type                |RG                       |Scope                      |
|--------------------------------|--------------------|-------------------------|---------------------------|
|`kv-ipai-dev`                   |Key Vault           |`rg-ipai-shared-dev`     |Platform-wide secrets      |
|`ipai-odoo-dev-kv`              |Key Vault           |`rg-ipai-dev`            |Odoo 19 CE scoped secrets  |
|`id-ipai-agents-dev`            |Managed Identity    |`rg-ipai-shared-dev`     |Agent workloads            |
|`id-ipai-aca-dev`               |Managed Identity    |`rg-ipai-agents-dev`     |Container Apps             |
|`id-ipai-databricks-dev`        |Managed Identity    |`rg-ipai-ai-dev`         |Databricks service identity|
|`dbmanagedidentity`             |Managed Identity    |`rg-dbw-managed-ipai-dev`|Databricks managed         |
|`unity-catalog-access-connector`|Databricks Connector|`rg-dbw-managed-ipai-dev`|Unity Catalog ADLS access  |

### CI/CD & Shared Services

|Resource                                 |Type                |RG                  |Role                                            |
|-----------------------------------------|--------------------|--------------------|------------------------------------------------|
|`insightpulseai`                         |Azure DevOps org    |VS Online RG        |All pipelines                                   |
|`ipai-build-pool`                        |Managed DevOps Pool |`rg-ipai-devops`    |Self-hosted build agents                        |
|`ipai-devcenter`                         |Dev Center          |`rg-ipai-devops`    |Dev environment management                      |
|`cripaidev`                              |Container Registry  |`rg-ipai-shared-dev`|Shared platform images (target primary)         |
|`ipaiodoodevacr`                         |Container Registry  |`rg-ipai-dev`       |Odoo-specific images (consolidate to `cripaidev`)|
|`appi-ipai-dev`                          |Application Insights|`rg-ipai-shared-dev`|Telemetry                                       |
|`law-ipai-dev`                           |Log Analytics       |`rg-ipai-shared-dev`|Unified logs                                    |
|`privatelink.postgres.database.azure.com`|Private DNS Zone    |`rg-ipai-ai-dev`    |Private PG connectivity for both servers        |

-----

## 3. DNS Target State

### Current Split-Origin Architecture (Transition)

```
Cloudflare DNS
├── Legacy origin: 178.128.112.214 (DigitalOcean — DEPRECATED 2026-03-15)
└── Azure origin:  4.193.100.31   (Azure VM — supabase, n8n-azure)
```

### Target Architecture

```
Cloudflare DNS (authoritative, DNS-only for mail)
    └── Azure Front Door (public edge)
            └── Azure Container Apps / VM origins
```

### Hostname Migration Map

|Hostname                          |Current               |Action                           |Target Origin                |Priority|
|----------------------------------|----------------------|---------------------------------|-----------------------------|--------|
|`erp`                             |`178.128.112.214` DO  |DEPRECATED (2026-03-15)          |AFD → `ipai-odoo-dev-web`    |P1      |
|`mcp`                             |`178.128.112.214` DO  |DEPRECATED (2026-03-15)          |AFD → MCP Container App      |P1      |
|`auth`                            |`178.128.112.214` DO  |DEPRECATED (2026-03-15)          |AFD → Entra ID gateway       |P1      |
|`n8n`                             |`178.128.112.214` DO  |DEPRECATED (2026-03-15)          |AFD → n8n Container App      |P1      |
|`supabase`                        |`4.193.100.31` Azure  |**Wire to AFD**                  |AFD → `vm-ipai-supabase-dev` |P2      |
|`n8n-azure`                       |`4.193.100.31` Azure  |**Rename to `n8n`** post-migration|Merge with n8n above         |P2      |
|`plane`                           |`178.128.112.214` DO  |DEPRECATED (2026-03-15)          |AFD → `ipai-plane-dev`       |P2      |
|`crm`                             |`178.128.112.214` DO  |DEPRECATED (2026-03-15)          |AFD → `ipai-crm-dev`         |P2      |
|`ocr`                             |`178.128.112.214` DO  |DEPRECATED (2026-03-15)          |AFD → `docai-ipai-dev`       |P2      |
|`www` / `@`                       |`178.128.112.214` DO  |DEPRECATED (2026-03-15)          |AFD → landing page           |P2      |
|`shelf`                           |`178.128.112.214` DO  |Retire — deprecated 2026-03-11   |AFD → `ipai-shelf-dev`       |P3      |
|`superset`                        |`178.128.112.214` DO  |DEPRECATED (2026-03-15)          |Databricks Dashboards + Genie|P3      |
|`mail`, MX, SPF, DKIM, DMARC     |Zoho SMTP              |**Keep DNS-only — never touch**  |No change                    |—       |
|`mg` (`mg.insightpulseai.com`)    |Mailgun                |Deprecated — Zoho SMTP canonical |No change (remove when safe) |—       |

-----

## 4. Identity & Auth Architecture

|Surface              |Provider           |Resource                          |Notes                                                     |
|---------------------|-------------------|----------------------------------|----------------------------------------------------------|
|Databricks           |Entra ID SSO       |`id-ipai-databricks-dev`          |Primary workforce identity                                |
|Container Apps       |Managed Identity   |`id-ipai-aca-dev`                 |No human credentials                                      |
|Agent workloads      |Managed Identity   |`id-ipai-agents-dev`              |Scoped least-privilege                                    |
|Odoo 19 CE           |Odoo-native RBAC   |—                                 |Entra ID LDAP sync planned; `ipai-odoo-dev-kv` for secrets|
|Supabase app surfaces|Supabase Auth + RLS|`pg-ipai-dev`                     |JWT claims: `org_id`, `company_id`, `role`                |
|All secrets          |Azure Key Vault    |`kv-ipai-dev` + `ipai-odoo-dev-kv`|Never in git, env vars, or container specs                |

-----

## 5. Databricks Intelligence Layer (`dbw-ipai-dev`)

### Pillar Capabilities

|Pillar          |Tools                                             |Use                                                |
|----------------|--------------------------------------------------|---------------------------------------------------|
|SQL & Analytics |SQL Editor, Queries, Dashboards, Genie            |Finance self-serve, KPI dashboards, BIR queries    |
|Data Engineering|DLT Pipelines, Jobs, Runs, Data Ingestion         |Bronze to Silver to Gold, Odoo CDC, Supabase feeds |
|AI / ML         |Experiments, Features, Models, Serving, Agents    |Finance Copilot, anomaly detection, BIR classifiers|
|Marketplace     |Fivetran, dbt Cloud, Tableau/Power BI, MCP Servers|Odoo sync, transforms, BI, Claude agent access     |

### Serving Endpoint Routing (11 endpoints — all Ready)

|Use Case                                  |Primary                                  |Fallback                                |
|------------------------------------------|-----------------------------------------|----------------------------------------|
|Finance Copilot (interactive)             |`databricks-llama-4-maverick`            |`databricks-meta-llama-3-3-70b-instruct`|
|Batch classification (BIR, reconciliation)|`databricks-meta-llama-3-1-8b-instruct`  |`databricks-gemma-2-12b`                |
|Semantic embeddings                       |`databricks-bge-large-en`                |`databricks-gte-large-en`               |
|Document OCR pipeline                     |`docai-ipai-dev` then Databricks         |`vision-ipai-dev`                       |
|Long-form reasoning                       |`databricks-meta-llama-3-1-405b-instruct`|—                                       |

### Delta Lake Schema (`stipaidevlake` ADLS Gen2)

|Schema             |Contents                                                                 |Owner              |
|-------------------|-------------------------------------------------------------------------|-------------------|
|`bronze.odoo_*`    |Raw from `ipai-odoo-dev-pg` — append-only, `source_run_id`, `ingested_at`|ETL pipeline       |
|`bronze.supabase_*`|Supabase CDC from `pg-ipai-dev`                                          |ETL pipeline       |
|`silver.odoo_*`    |dbt-typed, validated Odoo entities                                       |dbt + Unity Catalog|
|`silver.finance_*` |Finance-domain cleansed tables                                           |dbt                |
|`gold.finance_kpis`|AR aging, cash position, P&L rollups                                     |dbt                |
|`gold.bir_*`       |BIR VAT, WHT, income tax compliance tables                               |dbt                |
|`ai.embeddings`    |Vectors — `oai-ipai-dev` + `bge-large-en`                                |Feature pipeline   |
|`ai.features`      |Feature Store registered features                                        |Feature Store      |

### Databricks to Supabase Publish Path

|Payload           |Mechanism                 |Supabase Target       |
|------------------|--------------------------|----------------------|
|Gold KPI snapshots|Edge Function HTTP POST   |`ai.kpi_snapshots`    |
|Feature vectors   |pgvector upsert           |`ai.embeddings`       |
|Inference results |Edge Function queue worker|`ai.inference_results`|
|Job run events    |Webhook                   |`ops.run_events`      |

-----

## 6. Odoo 19 CE — Development Conventions

**These are enforced as CI gate failures — not guidelines.**

|Rule             |Correct                                                        |Forbidden                                     |
|-----------------|---------------------------------------------------------------|----------------------------------------------|
|View tag         |`<list>`                                                       |`<tree>` — removed in Odoo 19, runtime error  |
|Action view_mode |`view_mode="list,form"`                                        |`"tree,form"` — invalid in 19                 |
|Module selection |OCA-first — evaluate all OCA modules before custom code        |Custom-first                                  |
|Deprecated APIs  |`_cr`, `_context`, `_uid`, `osv` all removed                   |Do not use                                    |
|Deployment target|`ipai-odoo-dev-web/cron/worker` (Container Apps, `rg-ipai-dev`)|DO droplet (legacy)                           |
|Database         |`ipai-odoo-dev-pg` (Azure PG Flex, SEA)                        |`odoo-db-sgp1` (DO, legacy)                   |
|Local sandbox    |`~/Documents/GitHub/odoo-ce/sandbox/dev`                       |—                                             |
|Repo             |`github.com/InsightPulseAI/odoo`                               |—                                             |

-----

## 7. End-to-End Data Flow

```
Odoo 19 CE  (ipai-odoo-dev-pg + Container Apps — SOR)
    │ XML-RPC / Webhooks → n8n (Container App)
    │ + Fivetran Partner Connect
    ▼
stipaidevlake ADLS Gen2 — Bronze (append-only)
    │ Databricks DLT (dbw-ipai-dev) + Unity Catalog
    ▼
Silver  (dbt-tested, schema-validated)
    │ dbt transformations
    ▼
Gold  (KPIs · BIR · Finance aggregates)
    │                            │
    ▼                            ▼
Supabase ai.*               dbw-ipai-dev
(pg-ipai-dev — SSOT)        Dashboards + Genie
    │
    ├── srch-ipai-dev  (Azure AI Search — semantic queries)
    └── oai-ipai-dev   (Azure OpenAI — embeddings + Copilot)
    │
    ▼
Finance Copilot · BIR Compliance · MCP Agents · Ops Console
```

-----

## 8. n8n Integration (Confirmed Connectors)

|Connector    |Role                                                          |
|-------------|--------------------------------------------------------------|
|Odoo         |XML-RPC pull to Bronze ingestion                              |
|Supabase     |Upsert inference results, trigger Edge Functions              |
|Postgres     |Direct DB access for low-latency ops                          |
|GitHub       |Trigger CI/CD on schema changes                               |
|HTTP Request |Databricks Jobs REST API, Serving endpoints, AFD health checks|
|Google Sheets|Finance team data entry to Delta Lake staging                  |

-----

## 9. Resources Requiring Action

|Resource                            |Issue                                              |Action                      |Priority|
|------------------------------------|---------------------------------------------------|----------------------------|--------|
|`odoo-web` (`rg-ipai-agents-dev`)   |Duplicate of `ipai-odoo-dev-web`                   |**Retire**                  |P1      |
|`odoo-init` (`rg-ipai-agents-dev`)  |Duplicate init job                                 |**Retire**                  |P1      |
|`debug-odoo-ep` (Container Instance)|Debug artifact — not ephemeral                     |**Retire**                  |P1      |
|Azure Front Door                    |Not yet provisioned — blocking all DNS migration   |**Provision**               |P1      |
|`n8n` (DO)                          |Legacy — migrate to Azure Container App            |**Migrate**                 |P1      |
|`superset` DNS + DO                 |Superseded by Databricks Dashboards + Genie        |**Evaluate retire Q2 2026** |P3      |
|`ipaiodoodevacr` vs `cripaidev`     |Two ACRs — consolidate                             |**Merge to `cripaidev`**    |P3      |
|`data-intel-ph-resource` (East US 2)|AI Foundry — verify VNet peering / private endpoint|**Review network isolation**|P2      |

-----

## 10. CI/CD Contract

**Source control:** GitHub — `InsightPulseAI/odoo`, `InsightPulseAI/databricks-pipelines`
**Runner:** Azure DevOps (`insightpulseai` org) via `ipai-build-pool` Managed DevOps Pool
**Targets:** `ipai-odoo-dev-env` (Container Apps), `dbw-ipai-dev` (Databricks). Vercel is deprecated (2026-03-11) — not an active deployment surface.

```
PR → Lint (sqlfluff · ruff · markdownlint · odoo-xml-lint [<tree> banned]) →
Unit Tests (pytest · dbt test) →
Schema Validation (RLS coverage · migration safety · Odoo 19 view conventions) →
Build + Push → cripaidev ACR →
Staging Deploy →
Integration Tests →
Production Deploy →
Smoke Tests →
Notify (Slack)
```

**Odoo 19 CE gate:** XML linter must fail any view using `<tree>` or `view_mode` containing `"tree"`. Zero tolerance — breaks production at runtime.

-----

## 11. 30-Day Sprint

|# |Action                                                                                  |Resources                                 |Due       |
|--|----------------------------------------------------------------------------------------|------------------------------------------|----------|
|1 |Provision Azure Front Door; wire `erp`, `mcp`, `auth` CNAMEs                            |AFD (new), Cloudflare                     |2026-03-18|
|2 |Retire `odoo-web`, `odoo-init`, `debug-odoo-ep` (agents-env duplicates)                 |`rg-ipai-agents-dev`                      |2026-03-20|
|3 |Migrate `erp` DNS to AFD to `ipai-odoo-dev-web`                                         |Cloudflare, AFD                           |2026-03-22|
|4 |Deploy n8n as Container App in `cae-ipai-dev`; retire DO n8n; rename `n8n-azure` to `n8n`|`cae-ipai-dev`, Cloudflare                |2026-03-22|
|5 |Configure Fivetran to `ipai-odoo-dev-pg` to `stipaidevlake` Bronze                      |`dbw-ipai-dev`, Fivetran                  |2026-03-22|
|6 |Build dbt Silver models: `account.move`, `res.partner`, `account.payment`               |`dbw-ipai-dev`, Unity Catalog             |2026-03-25|
|7 |Wire `bge-large-en` embeddings to Supabase `ai.embeddings` via Edge Function            |`dbw-ipai-dev`, `pg-ipai-dev`             |2026-03-25|
|8 |Connect `docai-ipai-dev` to BIR receipt/invoice OCR pipeline via n8n                    |`docai-ipai-dev`, n8n                     |2026-03-28|
|9 |First Gold dashboard: AR Aging, Cash Position, BIR VAT summary                          |`dbw-ipai-dev`, `law-ipai-dev`            |2026-03-31|
|10|Publish Databricks MCP Server for Claude agent access                                   |`dbw-ipai-dev`, `mcp` DNS                 |2026-03-31|
|11|Add Odoo 19 CE `<tree>` linter gate to Azure DevOps CI                                  |`ipai-build-pool`, ADO pipelines          |2026-04-07|
|12|Review `data-intel-ph-resource` network isolation (East US 2 to SEA VNet peering)       |`rg-data-intel-ph`, `vnet-ipai-databricks`|2026-04-07|
|13|Evaluate Superset retirement; migrate users to Databricks Dashboards                    |`superset` DNS, DO droplet                |2026-04-15|

-----

## 12. Hard Constraints

- No direct VM/Container IP A-records in final DNS — all traffic via Azure Front Door
- Mail DNS (`MX`, `SPF`, `DKIM`, `DMARC`, `zoho._domainkey`) always DNS-only, never proxied
- All secrets via `kv-ipai-dev` or `ipai-odoo-dev-kv` — never in git, env vars, or container specs
- Databricks must never write to `ipai-odoo-dev-pg` — Odoo owns its database
- Supabase RLS on every exposed table/view; JWT must carry `org_id`, `company_id`, `role`
- No human prod access via local accounts — Entra ID + Managed Identities only
- Odoo 19 CE: `<list>` only — `<tree>` is a runtime error; `view_mode="list,form"` only
- Production Databricks workloads via Jobs/DLT only — no interactive cluster SQL in prod
- `debug-odoo-ep` must not persist in production state

-----

## 13. Verification Checklist

### DNS & Network

- [ ] Azure Front Door provisioned with health probes for all origins
- [ ] All app hostnames CNAME to AFD (no direct VM/Container IP A-records)
- [ ] `n8n-azure` to `n8n` rename complete; DO n8n record retired
- [ ] `supabase` wired through AFD (not direct VM IP)
- [ ] Mail records (MX, SPF, DKIM, DMARC) DNS-only, untouched
- [ ] `privatelink.postgres.database.azure.com` private DNS covers both PG servers

### Infrastructure Cleanup

- [ ] `odoo-web` (agents-env) Container App retired
- [ ] `odoo-init` (agents-env) Container App Job retired
- [ ] `debug-odoo-ep` Container Instance decommissioned
- [ ] All 4 Managed Identities assigned least-privilege RBAC (no wildcard)
- [ ] Both Key Vaults — no workload uses direct env var secrets

### Odoo 19 CE

- [ ] All XML views use `<list>` — zero `<tree>` occurrences in repo
- [ ] All actions use `view_mode="list,form"` — zero `"tree"` in view_mode
- [ ] OCA module evaluation documented before any custom module authored
- [ ] Deprecated APIs (`_cr`, `_context`, `_uid`, `osv`) absent from codebase
- [ ] CI gate blocks PR if `<tree>` detected

### Databricks

- [ ] Unity Catalog access connector wired to `stipaidevlake` ADLS Gen2
- [ ] Bronze tables append-only with `ingested_at` + `source_run_id`
- [ ] Gold tables have freshness SLA defined (max staleness per table)
- [ ] `oai-ipai-dev` linked for embedding generation pipeline
- [ ] Serving endpoints authenticated via `id-ipai-databricks-dev` Managed Identity
- [ ] dbt tests pass for all Silver + Gold models in CI before production deploy

### Supabase

- [ ] RLS active on every exposed table/view in `pg-ipai-dev`
- [ ] `ops.sync_checkpoints` tracking Odoo to Bronze pipeline cursors
- [ ] `ops.run_events` receiving Databricks job events
- [ ] JWT claims (`org_id`, `company_id`, `role`) present on all auth tokens

### CI/CD

- [ ] `ipai-build-pool` Managed DevOps Pool operational for all workloads
- [ ] Odoo 19 CE `<tree>` XML linter running as required PR gate
- [ ] ACR consolidation: `ipaiodoodevacr` images migrated to `cripaidev`
- [ ] Azure DevOps pipeline gates: dbt test pass required before Delta production deploy
