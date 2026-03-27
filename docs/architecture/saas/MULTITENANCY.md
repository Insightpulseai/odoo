# Multitenancy Model — InsightPulse AI Platform

> **Status**: Approved
> **Date**: 2026-03-22
> **Reference**: [Azure SaaS and Multitenant Solution Architecture](https://learn.microsoft.com/en-us/azure/architecture/guide/saas-multitenant-solution-architecture/)

---

## Operating Model

A B2B SaaS-style multitenant platform in which Databricks, Foundry, and selected platform services are shared across tenants, while tenant identity, data access, policy boundaries, and customer-facing experiences are isolated according to the tenancy model.

## Tenant Definition

**Tenant = customer organization / legal business entity**

A tenant represents:
- one company/customer deployment
- one managed client workspace
- one internal business unit (when platform is used internally)

A tenant is **not**:
- a single dashboard
- a single project
- a single dataset
- a single user

Users, projects, datasets, and dashboards are sub-objects **inside** a tenant.

## Tenant Isolation Boundaries

Every tenant boundary must address:

| Boundary | Description |
|----------|-------------|
| **Identity** | Tenant-scoped user identities, groups, and roles |
| **Data** | Tenant-scoped storage, tables, and query results |
| **Config** | Tenant-specific parameters, feature flags, and preferences |
| **Observability** | Tenant-attributable logs, metrics, and billing |
| **Policy / Compliance** | Tenant-specific regulatory, retention, and access policies |

## Per-Layer Shared vs Isolated Matrix

### 1. Databricks — Shared Multitenant Data Intelligence Platform

| Component | Shared | Isolated | Mechanism |
|-----------|--------|----------|-----------|
| Workspace | Shared | — | Single workspace, multi-catalog |
| Compute (clusters/serverless) | Shared | — | Job-level isolation via run_as |
| Unity Catalog | Shared registry | Tenant catalogs/schemas | `catalog_<tenant>` naming |
| Bundle framework | Shared | — | Same DAB bundles, parameterized per tenant |
| Jobs / Workflows | Shared definitions | Tenant-scoped data | Parameterized catalog/schema variables |
| Bronze storage (ADLS) | Shared account | Tenant containers/paths | `abfss://<tenant>@stipaidevlake.dfs.core.windows.net` |
| Silver/Gold tables | Shared compute | Tenant schemas | `<tenant_catalog>.silver.*`, `<tenant_catalog>.gold.*` |
| Row/column security | — | Tenant-filtered | Unity Catalog row filters + column masks |

### 2. Fabric / Power BI — Tenant-Aware BI Consumption Plane

| Component | Shared | Isolated | Mechanism |
|-----------|--------|----------|-----------|
| Semantic models | Shared pattern | Tenant-scoped data | DirectQuery with tenant-filtered SQL |
| Reports / Dashboards | Shared templates | Tenant-filtered views | RLS (Row-Level Security) in Power BI |
| Workspace | — | Per-tenant workspace | Fabric workspace per tenant |
| Copilot / AI features | Shared capacity | Tenant-scoped context | Prompt scoping via tenant identity |

### 3. Foundry — Multitenant Agent and Gen-AI Application Plane

| Component | Shared | Isolated | Mechanism |
|-----------|--------|----------|-----------|
| Agent runtime | Shared | — | Single Foundry project |
| Model deployments | Shared endpoints | — | Shared GPT-4o / Claude endpoints |
| Prompts / system instructions | Shared templates | Tenant-scoped context | Context envelope injects tenant identity |
| Tool execution | Shared dispatcher | Tenant-scoped ACL | `permitted_tools` + company scope in context envelope |
| Retrieval / RAG | Shared index infra | Tenant-filtered results | AI Search filter by tenant_id |
| Conversation history | — | Tenant-isolated | Per-tenant audit records |

### 4. Odoo ERP — Tenant-Isolated Operational System

| Component | Shared | Isolated | Mechanism |
|-----------|--------|----------|-----------|
| Odoo instance | — | Per-tenant DB | `list_db=False`, single DB per deployment |
| Modules | Shared codebase | Per-tenant config | `ir.config_parameter` per company |
| Multi-company | Shared instance | Company-scoped | Odoo native multi-company + record rules |
| API access | Shared endpoints | Tenant-scoped auth | Session/API key per company user |

### 5. Azure Platform — Shared Control Envelope with Tenant Isolation Controls

| Component | Shared | Isolated | Mechanism |
|-----------|--------|----------|-----------|
| Entra ID | Shared tenant | App-scoped roles | App registrations + conditional access |
| Key Vault | Shared vault | Tenant-prefixed secrets | `<tenant>-db-password` naming convention |
| Azure Monitor | Shared workspace | Tenant-tagged telemetry | Custom dimensions: `tenant_id` |
| Container Apps | Shared environment | — | Single ACA env, multi-route |
| Front Door | Shared profile | Tenant-scoped routes | Custom domains per tenant |
| Cost Management | Shared subscription | Tenant-tagged costs | Resource tags: `tenant=<id>` |
| CI/CD (Azure DevOps) | Shared pipelines | Environment-gated | Approval gates per tenant-affecting deploy |

## Tenancy Patterns by Maturity

### Phase 1 — Single-Tenant (Current)

```
One org, one deployment, one catalog, one DB.
Multi-company in Odoo handles internal business units.
```

### Phase 2 — Soft Multitenancy

```
Shared platform, tenant isolation via:
- Unity Catalog: separate schemas per tenant
- Power BI: RLS per tenant
- Foundry: context envelope scoping
- Odoo: multi-company record rules
```

### Phase 3 — Hard Multitenancy

```
Full tenant isolation where required:
- Separate catalogs per tenant
- Separate ADLS containers per tenant
- Separate Odoo databases per tenant
- Tenant-specific encryption keys
- Tenant-specific compliance policies
```

## Cross-Tenant Rules

1. **No cross-tenant data leakage**: A query in tenant A must never return tenant B data.
2. **Explicit sharing only**: Cross-tenant data sharing requires Delta Sharing with explicit policy.
3. **Tenant-attributable billing**: Every compute/storage cost must be attributable to a tenant.
4. **Tenant-scoped audit**: Every data access must be logged with tenant context.
5. **Tenant-independent deployment**: A platform upgrade must not require per-tenant coordination.

## Architecture Diagram Caption Set

```
1.  Ingest       = multitenant ingestion plane
2.  Process      = tenant-aware bronze/silver/gold processing
3.  Storage      = tenant-governed lakehouse storage
4.  Enrich       = tenant-aware AI/ML and gen-AI enrichment
5.  Serve        = governed tenant-aware serving layer
6.  BI           = tenant-aware semantic/reporting plane
7.  Users        = tenant-scoped AI and BI experiences
8.  Share        = cross-tenant/external sharing by explicit policy only
9.  Core         = shared multitenant Databricks execution/governance core
10. Governance   = metadata/compliance overlay across tenants
11. Platform     = shared Azure control plane
12. Tenancy      = tenant identity/data/config/policy isolation
```

---

*Reference: [Azure SaaS and Multitenant Solution Architecture](https://learn.microsoft.com/en-us/azure/architecture/guide/saas-multitenant-solution-architecture/)*
