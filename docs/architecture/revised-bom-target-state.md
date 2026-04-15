# Revised BOM Target State — Multitenant SaaS + 4 Product Planes

> **Locked:** 2026-04-15
> **Version:** 2.0.0 (revised upward from v1)
> **Authority:** [`ssot/azure/bill-of-materials.yaml`](../../ssot/azure/bill-of-materials.yaml) v2
> **Companions:**
> [`ssot/azure/tagging-standard.yaml`](../../ssot/azure/tagging-standard.yaml) v3,
> [`ssot/azure/naming-standard.yaml`](../../ssot/azure/naming-standard.yaml),
> [`docs/architecture/multitenant-saas-target-state.md`](./multitenant-saas-target-state.md),
> [`docs/architecture/domain-and-web-bom-target-state.md`](./domain-and-web-bom-target-state.md)
>
> **Microsoft refs:**
> - [SaaS multitenant solution architecture](https://learn.microsoft.com/en-us/azure/architecture/guide/saas-multitenant-solution-architecture/)
> - [Multitenant solution checklist](https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/checklist)
> - [Microsoft Advertising](https://about.ads.microsoft.com/en/get-started/achieve-your-advertising-goals)
> - [D365 Customer Insights](https://www.microsoft.com/en-us/dynamics-365/products/customer-insights)
> - [D365 Finance](https://www.microsoft.com/en-us/dynamics-365/products/finance)
> - [D365 Project Operations](https://www.microsoft.com/en-us/dynamics-365/products/project-operations)
> - [D365 Business Central](https://www.microsoft.com/en-us/dynamics-365/products/business-central)
> - [Microsoft AI for Health](https://www.microsoft.com/en-us/research/project/ai-for-health/)

---

## Why this is revised

v1 was a tight Odoo+Foundry+Databricks BOM in **one sponsorship subscription**. With Ads + Customer Insights, Finance + Project Operations + Business Central, and a research/life-sciences lane added to the capability surface, that's no longer enough.

The revised target is **a multitenant SaaS control plane with 4 product planes** — built so a future Microsoft / Azure partner integration is a wiring decision, not a rewrite.

---

## The 4 product planes

```
1. Shared SaaS control plane          ← tenancy, identity, billing, observability
2. Core operations plane              ← Odoo+Pulser (Finance + ProjectOps + BC parity)
3. Ads / customer intelligence plane  ← Ads + Customer Insights parity
4. Research / life sciences plane     ← PrismaLab + AI for Health (modest)
```

Each plane owns specific capabilities. Each tags `plane:<name>` so cost, telemetry, and policy roll up cleanly.

---

## Subscriptions (revised: 3, not 1)

| Subscription | Role | Status |
|---|---|---|
| `ipai-shared-management` | Cross-env shared services (mgmt, billing, governance) | Pending creation |
| `ipai-nonprod` | Dev + staging workloads (= current Sponsorship sub `eba824fb`) | Live |
| `ipai-prod` | Production workloads | Pending creation |

`Azure subscription 1` (`536d8cf6`) is deprecated; consolidating into the above per ADR-002.

---

## Resource groups (per env: 7, total: 18)

### Per-env pattern (apply to nonprod and prod)

```
rg-ipai-<env>-shared          # ACR refs, shared MIs, env-shared utilities
rg-ipai-<env>-network         # VNet, subnets, private DNS, PEs, NAT
rg-ipai-<env>-observability   # Log Analytics, App Insights ×4, alerts
rg-ipai-<env>-web             # web surfaces (root, ERP shell, prisma web, w9 booking)
rg-ipai-<env>-odoo-runtime    # ACA env + Odoo apps/jobs + storage
rg-ipai-<env>-agent-ai        # Foundry, AI Search, Doc Intelligence, agent storage
rg-ipai-<env>-data-intel      # Databricks, access connector, lake storage, Purview
```

### Shared-management RGs (cross-env)

```
rg-ipai-mgmt-edge             # AFD Premium + WAF policy
rg-ipai-mgmt-registry         # ACR (1 shared registry across envs)
rg-ipai-mgmt-secrets          # Shared mgmt KV
rg-ipai-mgmt-governance       # Budgets, policies, action groups
```

---

## Per-environment platform slice (target qty)

| Layer | Target qty per env |
|---|---:|
| Resource groups | 7 |
| Key Vault | 1 |
| VNet | 1 |
| Subnets | 3 (web, runtime, data/private-link) |
| Private DNS zones | 4 (postgres, search, storage, privatelink) |
| NAT gateway | 1 |
| Log Analytics workspace | 1 |
| App Insights | 4 (web, product, agent, research) |
| ACA environments | 2 (runtime + product) |
| ACA apps | 5 (odoo-app, odoo-worker, pulser-api, prisma-api, forms-api) |
| ACA jobs | 2 (odoo-init, odoo-batch) |
| PostgreSQL Flex | 1 |
| Storage accounts | 3+ (odoo, agent, lake; constrained-name per naming standard) |
| Foundry resource | 1 |
| Foundry project | 1 |
| AI Search | 1 |
| Managed identities | 3 (app/runtime, jobs/ops, data connector) |
| Databricks workspace | 1 |
| Databricks access connector | 1 |
| Purview | 0–1 (only if actively used) |
| Service Bus | 0–1 |
| Event Hubs | 0–1 |
| Redis | 0 (defer until justified) |
| Cosmos DB | 0 (defer until justified) |
| API Management | 0–1 (only when external API productization is real) |

**Per-env total:** ~38–42 resources.
**Total partner-ready (nonprod + prod + shared mgmt):** ~84–94 resources.

---

## Plane-by-plane capability map

### 1. Shared SaaS control plane

| Capability | Implementation |
|---|---|
| Tenant model | Schema-per-tenant for ERP; tenant_id column for products. Per [`multitenant-saas-target-state.md`](./multitenant-saas-target-state.md) |
| Pricing/tiering | Explicit product + tenant tiers in `ops.tenants` |
| Metering | App Insights custom metric per agent run, tagged with tenant_id |
| Isolation | Per-tenant Entra apps for customer-facing; MI-only service-to-service |
| SLO/SLA | Per tier; documented per surface |
| Noisy-neighbor control | Per-tenant rate limits, ACA scaling rules |
| Marketplace metering | Wired to Azure Marketplace metered billing API by Phase 4 |

### 2. Core operations plane (D365 Finance + ProjectOps + BC parity)

| D365 capability | IPAI implementation |
|---|---|
| Forecast-to-close | Odoo `account` + OCA `account-financial-tools` + Pulser advisory |
| Cash flow forecasting | `ipai_finance_cash` (scaffolded today) + Foundry-grounded forecasts |
| Reconciliation Agent | Pulser Recon Agent v0 (R2 Jul 14 ship target) |
| Project pricing/costing | OCA `project-reporting` + `ipai_finance_ppm` |
| Project accounting | `account.analytic.line` + OCA `account-analytic` |
| Time/expense workflows | `hr_timesheet` + `hr.expense` + `ipai_hr_expense_liquidation` |
| Resource utilization | `resource.resource` + `hr.employee` + skills mapping |
| SMB ERP backbone | Odoo CE 18 core (sales, purchase, inventory, accounting) |

### 3. Ads / customer intelligence plane (Ads + Customer Insights parity)

| Capability | IPAI implementation |
|---|---|
| Ad activation workflows | Ads/Campaign Ops APIs + orchestration via Pulser |
| Customer profile unification | data-intelligence + Odoo CRM contract layer |
| Segmentation | Pulser customer intel + Databricks ML |
| Journeys / lead handoff | Campaign/journey APIs + Odoo CRM webhook |
| Campaign analytics | Databricks + AI Search + dashboards |

**Per-env qty:** 1 App Insights + 1 MI + reuses Databricks/Search/forms. **No separate database initially.**

### 4. Research / life sciences plane (PrismaLab + AI for Health)

| Capability | IPAI implementation |
|---|---|
| Research question framing | PrismaLab "Clarify Question" tool |
| PRISMA flow + evidence synthesis | PrismaLab tools |
| Literature search | PrismaLab "Search PubMed" |
| Review type guidance | PrismaLab "Review type" |
| AI-assisted research | "Ask PrismaLab AI" — grounded retrieval over PRISMA 2020 + Cochrane + Harrer corpus |
| Optional public-health analytics | Future, behind `regulated_scope:research` tag |

**Not in default BOM** (escalation gate via `regulated_scope` tag):
- Health Data Services workspace
- FHIR service
- DICOM service
- Customer PHI platform
- Regulated clinical lakehouse

These are added **only** when an actual PHI/EHR/imaging workload is onboarded with explicit governance approval.

---

## Naming convention (per [naming-standard.yaml](../../ssot/azure/naming-standard.yaml))

```
Standard pattern:    <type>-ipai-<env>-<product>-<plane>-<region?>
Constrained names:   st<org><env><purpose><nn>  (storage)
                     cr<org><purpose>           (ACR)
```

Examples:
```
rg-ipai-prod-odoo-runtime
kv-ipai-prod-shared
appi-ipai-prod-prisma-research
aca-ipai-prod-pulser-api
acaj-ipai-prod-odoo-init
pg-ipai-prod-odoo
srch-ipai-prod-agent
dbw-ipai-prod-data
afd-ipai-prod-web
id-ipai-prod-prisma-app

stipaiprododoo01
stipaiprodagent01
stipaiprodlake01
```

---

## Tag contract (per [tagging-standard.yaml v3](../../ssot/azure/tagging-standard.yaml))

17 mandatory tags now (was 9 in v2):

```yaml
organization:        insightpulseai
environment:         nonprod | prod
product:             shared | odoo | pulser | ads | prisma | w9 | agent | data
plane:               shared | web | transaction | agent | data-intelligence | research | observability | network
workload:            edge | odoo | prisma | ads | search | foundry | databricks | forms | worker | jobs | monitoring | identity | secrets | registry
owner:               jake
cost_center:         ipai
managed_by:          bicep
source_repo:         Insightpulseai/<repo>
criticality:         low | medium | high
data_classification: public | internal | restricted | confidential
lifecycle:           experimental | active | deprecated
tenant_scope:        single-tenant | multi-tenant | platform
billing_scope:       shared | product | customer
regulated_scope:     none | research | health | clinical
backup_tier:         none | standard | critical
region:              southeastasia | eastus2 | ...
```

New in v3 (vs v2): `organization`, `workload`, `source_repo`, `tenant_scope`, `billing_scope`, `regulated_scope`, `backup_tier`, `region`.

---

## IaC repo structure

```
infra/
  azure/
    modules/
      governance/      (subscription tags, policy assignments, budgets)
      network/         (vnet, subnets, private DNS, PE, NAT)
      observability/   (LA, App Insights, alerts, action group)
      web/             (Front Door, WAF, web surfaces)
      odoo/            (ACA env, ACA app, ACA job, postgres, storage)
      agent/           (Foundry, Search, identities, storage)
      data-intelligence/ (Databricks, access connector, lake storage, Purview)
      research/        (Prisma app, research worker, research storage)
      tags/main.bicep  (canonical tag module — already exists)
    environments/
      nonprod/
      prod/
    policies/
    template-specs/

ssot/
  azure/
    bill-of-materials.yaml      ← v2 (this revision)
    naming-standard.yaml        ← new
    tagging-standard.yaml       ← v3
    rg-layout.yaml              ← derived from BOM
  foundry/
    resource-inventory.yaml
    connections.yaml
  tenants/
    tiers.yaml
    metering-contract.yaml
  research/
    regulated-scope-policy.yaml ← regulated_scope governance gate
```

---

## Delivery rule

- **Author** in Bicep
- **Validate** locally with Azure CLI (`az bicep build`, `az deployment group what-if`)
- **Promote** with Azure Pipelines only (no GHA, no Vercel)
- **No portal-only canonical changes** — all drift reconciled back into IaC

---

## SMART success criteria

### Tenancy + product

- 100% customer-facing requests resolve to tenant context before app logic
- 100% paid capabilities assignable to a product tier
- 0 known cross-tenant reads/writes in nonprod and prod
- 95%+ tenant usage meterable by product, tenant, workload

### Governance + cost

- 100% live resources carry the 17-key mandatory tag set
- 95%+ spend allocatable by `product`/`plane`/`workload`/`billing_scope`
- Monthly unallocated spend <5%
- 0 untagged production resources

### Delivery + security

- 100% infra PRs run Bicep validation + what-if
- 100% Azure-hosted workloads use MI where supported
- 0 secrets in git
- 100% prod changes flow through Azure Pipelines

### Runtime health

- All 4 canonical domains pass health checks from shared edge
- Odoo / Pulser / PrismaLab / shared API telemetry visible in App Insights
- Each major plane has ≥1 SLO defined

### Research / health lane

- 0 PHI/clinical datasets onboarded without explicit `regulated_scope` upgrade
- 100% research exports + artifacts auditable
- Default PrismaLab workloads run without Health Data Services / FHIR

---

## Lean partner-ready target

```
3 subscriptions
18 total resource groups
1 Front Door Premium + 1 WAF
1 shared ACR
3 Key Vaults (1 mgmt + 1 nonprod + 1 prod)
2 VNets (1 per env)
6 subnets
2 NAT gateways
2 PostgreSQL servers (1 per env)
2 Foundry resources (1 per env)
2 AI Search services (1 per env)
2 Databricks workspaces (1 per env)
2 lake storage accounts
4 ACA environments (2 per env)
10 ACA apps
4 ACA jobs
8 App Insights instances
2 Log Analytics workspaces
0–2 Service Bus / Event Hubs (only when streaming/async needed)
0 Redis by default
0 Cosmos DB by default
0 clinical/FHIR services by default
```

---

## What this enables

- Shared SaaS control plane → first customer onboarding without rewrite
- Tenant tiering + metering → Marketplace listing readiness
- Per-tenant `tenant_scope` tagging → cost allocation per customer
- `regulated_scope` escalation gate → safe path to PHI workloads if/when needed
- `source_repo` tag → drift reconciliation back to canonical IaC repo
- 4-plane structure → cleaner scope for partnerships (Microsoft Ads / Customer Insights / Finance / ProjectOps / BC / AI for Health)

---

*Last updated: 2026-04-15*
