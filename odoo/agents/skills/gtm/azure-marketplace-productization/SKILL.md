# Skill: Azure Marketplace Offer Productization

source: learn.microsoft.com/partner-center/marketplace-offers + research
extracted: 2026-03-15
applies-to: web, ops-platform, infra, .github

## Context (as of Sep 2025)
Azure Marketplace + AppSource unified into single Microsoft Marketplace.
6M+ monthly visitors. MACC alignment is primary enterprise buying driver.

## Recommended offer type: SaaS (primary)
- Runs in IPAI tenant (Azure SEA)
- Customer accesses via web (ops-console)
- Microsoft handles billing, tax, invoicing
- Supports flat rate + per-user + custom meters

## Revenue unlock chain (do in order)
1. Partner Center account → MPN ID
2. Transactable SaaS offer (live)
3. Co-sell Ready (one-pager + pitch deck)
4. Azure IP Co-sell Eligible ($100K ACR + tech validation + RAD)
5. MACC Eligible (enterprise close unlock)
6. Marketplace Rewards (7× sales multiplier)

## Pricing architecture (IPAI)

| Plan | Billing | Includes |
|------|---------|----------|
| Starter | Flat monthly | Odoo CE + 5 users + base connectors |
| Growth | Flat + per-user | + OCA modules + Superset/AI/BI dashboards |
| Enterprise | Flat + meters | + Agents runtime + BIR compliance + pipelines |
| Private Offer | Negotiated | Custom modules, SLA, data residency |

## Metered dimensions (Enterprise tier)
- `ai_inference_calls`: per 1,000 agent LLM calls
- `documents_processed`: per document (OCR/PaddleOCR)
- `active_integrations`: per connected data source/month
- `bir_reports_generated`: per BIR compliance report

## Technical integration (SSOT-compliant)

```
Marketplace webhook
  → Supabase Edge Function (ops-platform/functions/marketplace-webhook/)
  → ops.marketplace_subscriptions (RLS by tenant)
  → ops.metering_events (append-only, emit to Metering API)
  → n8n: provision/deprovision Odoo tenant workflow
  → Odoo: billing reference artifacts (SOR)
```

## APIs to implement

### SaaS Fulfillment API v2
```
POST /resolve          → convert marketplace token → subscription
GET  /subscriptions    → list active subscriptions
POST /subscriptions/{id}/activate   → activate after setup
DELETE /subscriptions/{id}          → handle cancellation
```

### Metering Service API
```
POST /usageEvent       → emit consumption events (PAYG meters)
POST /usageEventBatch  → batch emit (high-volume)
```

### Webhooks received
- Subscribed / Unsubscribed / Suspended / Reinstated / Renewed
- PlanChanged / QuantityChanged

## SaaS Accelerator
- Repo: `github.com/Azure/Commercial-Marketplace-SaaS-Accelerator`
- Use as scaffold only — replace .NET webhook receiver with Supabase Edge Function
- Subscription state lands in `ops.marketplace_subscriptions`, not a separate app

## Private offer motion (enterprise close)
- Create via Partner Center → Private offers dashboard
- Time-bound: up to 3 years
- Multiparty (MPO): add local Microsoft reseller for PH market
- MACC-eligible: 100% of sale counts toward customer's Azure commitment
- Process: get customer Azure billing account ID → create offer → email link

## Reference architecture diagram (required for co-sell)
Must show IPAI primarily platformed on Azure (SEA region):
- Azure Container Apps (Odoo web/worker/cron)
- Azure Database for PostgreSQL Flexible Server
- Azure Data Lake Storage (stipaidevlake)
- Azure Databricks (dbw-ipai-dev)
- Supabase on Azure VM (control plane)
- Azure Front Door (CDN + WAF + TLS)
- Azure Key Vault (secrets)
- Azure OpenAI (oai-ipai-dev)

## Revenue share
Microsoft takes 3% of SaaS transactions. 97% to publisher.

## IPAI advantage
Existing Azure footprint (Sub `536d8cf6`, SEA, ACA + PG Flex + Databricks)
already satisfies "primarily platformed on Azure" for IP Co-sell validation.
Reference architecture diagram ≈ existing infra diagram.

## Fastest path to first revenue
Minimal Viable Offer: one plan, flat monthly, SaaS Fulfillment API via Edge Function.
Target existing client (TBWA\SMP) as first private offer.
One $50K+ deal = half the $100K ACR threshold toward MACC eligibility.

## Don'ts
- Never submit "Contact Me" listing as primary — not transactable, not MACC-eligible
- Never hardcode subscription state in app — all in `ops.marketplace_subscriptions`
- Never process webhook outside Edge Function (X-MS-Signature verification required)
- Never estimate timelines for the user
