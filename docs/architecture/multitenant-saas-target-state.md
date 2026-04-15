# Multitenant SaaS Target State

> **Locked:** 2026-04-15
> **Authority:** this file (Azure SaaS multitenant pattern adoption)
> **Source:** [Microsoft Learn — Azure SaaS multitenant solution architecture](https://learn.microsoft.com/en-us/azure/architecture/guide/saas-multitenant-solution-architecture/) + [Multitenant solution checklist](https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/checklist)
> **Doctrine:** Build for partner-integration day one. Every IPAI service must be partner-listable in [Azure Partner Solutions](https://learn.microsoft.com/en-us/azure/partner-solutions/partners).

---

## Why this matters now

Per the user instruction `2026-04-15`: **"should be building service we'll later be integrated as a partner."**

Translation: every IPAI surface (Odoo+Pulser, PrismaLab, W9 booking, data-intelligence) must be architected so that:

1. **Tenant isolation** is a first-class concern (not bolted on later)
2. **Identity boundary** per tenant uses Entra workload identities + per-tenant Azure roles
3. **Data isolation** uses one of the three approved patterns (per-tenant DB / shared-DB-per-schema / shared-DB-shared-schema)
4. **Networking** supports per-tenant private endpoints and VNet integration where required
5. **Billing / metering** can carry tenant ID through to consumption metrics
6. **Onboarding** is automatable via Bicep + Azure Pipelines

This is the contract we'll need before any of these services can be listed in Azure Marketplace or co-sold via Partner Center.

---

## Tenant model decisions (locked)

### 1. Tenant isolation strategy per surface

| Surface | Isolation pattern | Rationale |
|---|---|---|
| **Odoo / Pulser ERP** | Shared DB, **schema-per-tenant** + Odoo `res.company` per tenant | Odoo native multi-company already supports this; PG schema split via `ops.platform_*` already in place |
| **PrismaLab tools** | Shared DB, shared schema, **tenant_id column** | Anonymous-first usage; tenant_id attached when user authenticates |
| **W9 booking** | Per-tenant single-instance for now | Single brand surface; multi-tenant is future when offering booking-as-a-service |
| **Data intelligence (PH)** | Shared DB, **shared schema, tenant_id column** + Databricks Unity Catalog isolation | Lakehouse already has UC governance; per-tenant catalogs/schemas |

### 2. Identity per tenant

```
Entra Tenant: insightpulseai.com (single, today)
  ↓
Per-business Entra app registrations (W9, PrismaLab consumers, etc.)
  ↓
Per-tenant managed identities for service-to-service auth
  ↓
Per-tenant Key Vault references for tenant-scoped secrets
```

Doctrine: **No password-based auth for service workloads.** Per [`infra/azure/tags/main.bicep`](../../infra/azure/tags/main.bicep) `managed_by: bicep` and per `.claude/rules/security-baseline.md`.

### 3. Routing per tenant

Route through 1 shared Azure Front Door per [`docs/architecture/domain-and-web-bom-target-state.md`](./domain-and-web-bom-target-state.md):

```
Tenant URL pattern:
  <tenant>.insightpulseai.com   (or custom domain via AFD)
       ↓
  Front Door rules → ACA app (with tenant header injected)
       ↓
  ACA app reads tenant context from header, applies tenant policy
```

### 4. Configuration per tenant

| Item | Where it lives |
|---|---|
| Tenant config (limits, features, branding) | `ops.tenants` table in PG (one row per tenant) |
| Per-tenant secrets | Key Vault with tenant-scoped naming (`<tenant>-<secret-name>`) |
| Per-tenant Foundry context | Foundry project per tenant when scale demands; until then, single project + tenant_id metadata on agent runs |
| Per-tenant feature flags | `ops.feature_flags` table joined on tenant_id |

### 5. Data classification per tenant

Per [`ssot/azure/tagging-standard.yaml`](../../ssot/azure/tagging-standard.yaml) `data_classification` values, every tenant carries a per-tenant default classification:

```
public:        anonymous PrismaLab usage
internal:      single-tenant IPAI/W9 ops
restricted:    customer pilots
confidential:  named-customer multi-tenant
```

### 6. Metering / billing per tenant

| Cost driver | Metering pattern |
|---|---|
| Foundry tokens | App Insights custom metric per agent run, tagged with tenant_id |
| ACA compute | ACA built-in cost allocation by `cost_center` tag (mandatory per tagging standard) |
| Postgres storage | Schema-level allocation calculation (per-tenant schema sizes) |
| Databricks compute | Unity Catalog per-tenant cluster tagging |
| AI Search | Index-level usage attribution |

All tenant-tagged metrics flow into Power BI / Fabric for FinOps reporting.

---

## Multitenant checklist (Microsoft pattern → IPAI status)

| Microsoft checklist item | IPAI position | Status |
|---|---|---|
| Choose your tenancy model | Schema-per-tenant for ERP; shared+tenant_id for products | ✅ locked |
| Define tenant lifecycle | Onboarding → trial → paid → churned states in `ops.tenants` | ⏸ schema not yet defined |
| Identity isolation | Entra app reg per tenant where customer-facing | ⏸ no per-tenant apps yet |
| Network isolation | AFD + WAF per surface; per-tenant PE for restricted | ⏸ AFD shared exists, per-tenant PE pending |
| Data isolation | PG schema split + UC catalog isolation | ⏸ partial |
| Cost allocation | Mandatory tags per tagging-standard | ✅ contract live |
| Throttling and quotas | Per-tenant rate limit in API gateway | ⏸ not yet |
| Incident isolation | Per-tenant monitoring in App Insights | ⏸ shared today |
| Onboarding automation | Bicep + Azure Pipelines tenant provisioning | ⏸ no automation yet |
| Offboarding / data export | GDPR-style export per tenant | ⏸ not yet |
| Custom domains per tenant | AFD custom domain binding | ⏸ supported, not yet wired |
| Feature flags per tenant | `ops.feature_flags` joined on tenant_id | ⏸ table not defined |
| Per-tenant audit | `ops.audit_log` with tenant_id | ⏸ not started |
| Compliance posture | BIR-PH per tenant where applicable | ⏸ defined per surface |

---

## Build sequence (doctrine-aligned)

### Phase 1 — Tenant model schema (next 14 days)
- Define `ops.tenants` table (id, name, status, plan, created_at, branding_json, compliance_scope)
- Define `ops.feature_flags` (tenant_id FK + flag name + value)
- Define `ops.audit_log` with tenant_id
- Bicep tenant onboarding module (creates Entra app reg + per-tenant secrets + initial schema rows)

### Phase 2 — Per-tenant routing (30 days)
- AFD route rule template per tenant
- Tenant header injection at edge
- ACA middleware to read tenant context
- Per-tenant rate limiting

### Phase 3 — Per-tenant data + observability (60 days)
- Per-tenant Postgres schema for ERP customers
- Per-tenant App Insights filter + dashboards
- Per-tenant Foundry context (project per tenant when warranted)

### Phase 4 — Marketplace + Partner readiness (90 days)
- Consumption metering wired to Azure Marketplace metered billing API
- Co-sell motion documented per Partner Center requirements
- IPAI surfaces listable in Azure Partner Solutions catalog

---

## Anti-pattern guard

**Do not:**
- Build single-tenant first then "add multi-tenant later" — it's much harder to retrofit isolation
- Use Postgres `database` per tenant — operational cost explodes
- Use Foundry resource per tenant — quota and cost explosion
- Skip metering "for now" — Marketplace listing requires it from start

**Do:**
- Start with shared infra + tenant_id discriminator (cheapest, most flexible)
- Promote to per-tenant resources only when justified by data classification or scale
- Always tag every resource with a tenant_id when ANY workload is tenant-aware
- Always carry tenant_id through the full request path (header → middleware → DB → telemetry)

---

## References

- [Architectural approaches for the deployment and configuration of multitenant solutions on Azure](https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/approaches/deployment-configuration)
- [SaaS multitenant solution architecture](https://learn.microsoft.com/en-us/azure/architecture/guide/saas-multitenant-solution-architecture/)
- [Multitenant solution checklist](https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/checklist)
- [Azure Partner Solutions](https://learn.microsoft.com/en-us/azure/partner-solutions/partners)
- [Common Data Model — schema creation](https://learn.microsoft.com/en-us/common-data-model/creating-schemas)

---

*Last updated: 2026-04-15*
