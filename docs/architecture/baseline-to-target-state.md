# Baseline → Target State

> **Snapshot date:** 2026-04-17
> **Subscription:** Microsoft Azure Sponsorship (eba824fb)
> **Old sub:** DELETED (all resources gone)

---

## Current baseline (what exists right now)

### Compute — 4 ACA apps, 1 environment

| App | Image | Min replicas | Custom domain | Status |
|---|---|---|---|---|
| ipai-odoo-dev | ipai-odoo:18.0-copilot | 1 | ❌ none | ✅ HTTP 200 |
| ipai-website | ipai-website:latest | 1 | ❌ none | ✅ running |
| ipai-prismalab | prismalab:latest | 1 | ❌ none | ✅ running |
| ipai-w9studio | w9studio-landing:latest | 1 | ❌ none | ✅ running |

### Database — 1 PG Flex

| Server | SKU | Storage | HA | Private endpoint | Entra auth |
|---|---|---|---|---|---|
| pg-ipai-odoo | D4s_v3 (4 vCPU) | 128 GB | ❌ No | ❌ No | ❌ Password only |

### AI Services — 3 resources, 1 working deployment

| Resource | Kind | Working deployments | Blocked |
|---|---|---|---|
| ipai-copilot-resource | AIServices | gpt-4.1-mini only | All others (715 RTFP) |
| ipai-copilot | AIServices | Unknown | Likely same RTFP |
| docai-ipai-dev | FormRecognizer | prebuilt-invoice (tested) | None |

### Databricks — fully operational

| Component | Status |
|---|---|
| Workspace (dbw-ipai-dev, Premium) | ✅ Live |
| Unity Catalog (5 catalogs) | ✅ Live |
| Bronze tables (4) | ✅ 103 rows |
| Gold views (6) | ✅ Live |
| Genie spaces (2) | ✅ Live |
| Model serving (11 endpoints) | ✅ All READY |
| Lakehouse Federation (odoo_erp) | ✅ Live |

### Security — partial

| Component | Status |
|---|---|
| Key Vault (kv-ipai-dev-sea) | ✅ with PE |
| Managed identities (6) | ✅ plane-scoped |
| Private endpoints | ✅ KV + Search only |
| VNet | ✅ vnet-ipai-dev-sea |
| Private DNS zones (8) | ✅ Complete |
| Defender for Cloud | ❌ NOT registered |
| PG private endpoint | ❌ MISSING |

### DNS — zones created, not propagated

| Zone | Nameservers | Squarespace updated? |
|---|---|---|
| insightpulseai.com | ns1-06 through ns4-06 | ❌ PENDING |
| w9studio.net | ns1-07 through ns4-07 | ❌ PENDING |

### Monitoring — complete

| Component | Count |
|---|---|
| Log Analytics workspaces | 4 (plane-scoped) |
| App Insights | 3 (plane-scoped) |
| Action groups | 1 |
| Backup vault | 1 |

### Other

| Resource | Status |
|---|---|
| ACR (acripaiodoo) | ✅ Live |
| AI Search (srch-ipai-dev-sea) | ✅ Live + PE |
| Purview (pv-ipai-dev-sea) | ✅ Live |
| Total resources | 44 |

---

## Desired target state

### Compute — 6 ACA apps + worker/cron split

| App | Purpose | Custom domain | Tags |
|---|---|---|---|
| ipai-odoo-web | Odoo web | erp.insightpulseai.com | system=odoo, tier0 |
| ipai-odoo-worker | Odoo background jobs | (internal) | system=odoo, tier0 |
| ipai-odoo-cron | Odoo scheduled jobs | (internal) | system=odoo, tier0 |
| ipai-website | Corporate site | www.insightpulseai.com | system=web, tier1 |
| ipai-prismalab | PrismaLab | prismalab.insightpulseai.com | system=web, tier1 |
| ipai-w9studio | W9 Studio | www.w9studio.net | system=web, tier1 |

### Database — right-sized, secured

| Server | SKU | HA | Private endpoint | Entra auth | PgBouncer |
|---|---|---|---|---|---|
| pg-ipai-odoo | D2s_v3 (2 vCPU) | Zone redundant (staging/prod) | ✅ pe-ipai-dev-pg | ✅ MI-based | ✅ Enabled |

### AI Services — RTFP unblocked

| Resource | Deployments | Status |
|---|---|---|
| ipai-copilot-resource | gpt-4.1 (50), gpt-4.1-mini (10), text-embedding-3-small (120), gpt-4o-mini (10) | After RTFP ticket |
| ipai-copilot-resource | o3-pro, gpt-5.4, sora-2, gpt-image-1.5 | After RTFP ticket |
| docai-ipai-dev | prebuilt-invoice + custom TBWA models | Train on CA form + Expense Report |

### Foundry — project created

| Component | Status |
|---|---|
| Foundry project (proj-ipai-copilot) | ✅ Created — enables SDK 2.x + Agent Service |

### Security — hardened

| Component | Target |
|---|---|
| Defender for Cloud | ✅ Free tier enabled |
| PG private endpoint | ✅ pe-ipai-dev-pg deployed |
| KV public access | ❌ Disabled (PE-only) |
| PG firewall 0.0.0.0 | ❌ Removed |
| All resources tagged | ✅ 8 core tags per ssot/governance/tags.yaml |
| APIM GenAI gateway | ✅ Rate limiting + observability for agents |

### DNS — propagated, custom domains bound

| Hostname | ACA app | Managed cert | Status |
|---|---|---|---|
| www.insightpulseai.com | ipai-website | ✅ | Live |
| erp.insightpulseai.com | ipai-odoo-web | ✅ | Live |
| prismalab.insightpulseai.com | ipai-prismalab | ✅ | Live |
| www.w9studio.net | ipai-w9studio | ✅ | Live |
| Squarespace NS | Updated to ns1-06 / ns1-07 | — | Done |

### Databricks — gold populated, Genie certified

| Component | Target |
|---|---|
| DLT pipeline | Running (Bronze → Silver → Gold from odoo_erp federation) |
| Gold marts | 7 tables populated (not just views) |
| Genie spaces | 2 certified (Finance Ops + Compliance & Tax) |
| Databricks One Chat | Enabled (Beta preview toggle) |
| Asset Bundles | Deployed via azure-pipelines/databricks-bundles-ci.yml |

### Odoo — seeded, action-ready

| Component | Target |
|---|---|
| 10 users | Imported from people.csv with correct roles |
| 8 projects | Imported with custom fields |
| 40 milestones | Imported as tasks (x_is_milestone=true) |
| 45 tasks | Imported with assignments + stages |
| 5 kanban boards | Configured as saved filters |
| ipai_doc_intel module | Installed, API key configured |
| Pulser behavior profiles | Active (odoo_ui profile) |

### CI/CD — 3-stage promotion

| Stage | Pipeline | Gate |
|---|---|---|
| Validate | PR → bicep build + what-if + tag check | Automatic |
| Dev | Merge to main → deploy dev | No approval |
| Staging | After dev smoke → deploy staging | 1 approval |
| Prod | After staging soak → deploy prod | 2 approvals + business hours |

### Marketplace — submitted

| Item | Target |
|---|---|
| Partner Center listing | Submitted (Pulser for Odoo — Finance Ops Control Tower) |
| Demo recording | 4-minute storyboard filmed |
| TBWA pilot | Running — Khalil's team using control tower daily |

---

## Gap summary: baseline → target

| # | Gap | Effort | Priority |
|---|---|---|---|
| 1 | Update Squarespace nameservers | 5 min (you) | **P0** |
| 2 | Bind custom domains + managed certs on 4 ACA apps | 30 min | **P0** |
| 3 | Enable Defender for Cloud | 5 min | **P0** |
| 4 | Deploy PG private endpoint | 2 hrs | **P0** |
| 5 | File RTFP support ticket for Foundry | 15 min (you) | **P0** |
| 6 | Downsize PG D4s_v3 → D2s_v3 | 30 min | **P1** |
| 7 | Create Foundry project (proj-ipai-copilot) | 15 min | **P1** |
| 8 | Split Odoo into web + worker + cron | 2 hrs | **P1** |
| 9 | Import Odoo seed data (13 tasks per spec-kit) | 4 hrs | **P1** |
| 10 | Install ipai_doc_intel + configure API key | 30 min | **P1** |
| 11 | Create 3-stage infra-promote.yml pipeline | 1 day | **P1** |
| 12 | Create ADO environments (dev/staging/prod) | 30 min | **P1** |
| 13 | Enable Databricks One Chat | 5 min | **P1** |
| 14 | Tag all 44 resources with 8 core tags | 2 hrs | **P1** |
| 15 | Run DLT pipeline (populate gold from federation) | 2 hrs | **P1** |
| 16 | Deploy APIM GenAI gateway | 4 hrs | **P2** |
| 17 | Train custom DocAI model on TBWA forms | 1 day | **P2** |
| 18 | Record demo | 30 min | **P2** |
| 19 | Submit marketplace listing | 1 hr | **P2** |

**Total estimated effort: ~5 days to reach full target state from current baseline.**

---

*Last updated: 2026-04-17*
