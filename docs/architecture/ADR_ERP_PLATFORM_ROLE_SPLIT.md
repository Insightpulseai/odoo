# ADR: ERP Platform Role Split — Odoo SoR, Databricks SoI, Foundry Agent Runtime

> **Status**: Accepted
> **Date**: 2026-03-17
> **Deciders**: CEO
> **Source**: `docs/research/wholesale-saas-erp-azure-architecture-study.md`

---

## Context

The platform needs clear ownership boundaries between transactional ERP, analytics/intelligence,
and agent operations to avoid "everything tries to do everything" failure modes.

## Decision

Adopt a three-plane architecture:

| Plane | Platform | Owns | Must NOT own |
|-------|----------|------|--------------|
| **SoR** (transactional) | Odoo CE 19 | Orders, invoices, inventory, purchasing, accounting, master data | Analytics lake, agent orchestration |
| **SoI** (intelligence) | Azure Databricks + Unity Catalog | Lakehouse (medallion), data products, context datasets, analytics | ERP transactions |
| **Agent runtime** | Microsoft Foundry Agent Service | Agent hosting, tracing, evaluation, publish, monitoring | Data engineering, ERP posting |

### Tenancy model

Database-per-tenant is the recommended SaaS isolation model. It aligns with Odoo's
multi-database hosting pattern and `dbfilter` routing.

- **Default**: DB-per-tenant, shared Odoo runtime farm
- **Enterprise tier**: deployment-per-tenant ("stamp")
- **Growth model**: hybrid (shared default, stamp on upgrade)

### Agent boundary rule

Agents recommend; Odoo commits. No agent may post to ledger, create orders, or mutate
inventory without an Odoo-side guardrail (approval workflow or validation gate).

### Integration spine

- **Azure API Management**: tool gateway for agents + external API governance
- **Azure Service Bus**: durable cross-system messaging (queues + topics)
- **Azure Event Grid**: reactive event fan-out
- **Anthropic Agent SDK + MCP**: agent implementation patterns + tool connectivity standard

### DevOps coexistence

| System | Role |
|--------|------|
| Azure DevOps Boards | Portfolio / control SoR (epics, features, stories) |
| GitHub | Source-control and PR truth |
| Azure Pipelines | Governed deployment path (approvals/checks for prod) |

## Consequences

- All new modules/features must identify which plane owns the capability
- Cross-plane features require a contract doc (`docs/contracts/`)
- Agents require Foundry trace + eval gates before publish promotion
- Databricks produces "context products" (gold datasets) for agents — not raw ERP data
- Supabase role narrows to self-hosted VM exception; not a control plane

## Alternatives considered

| Alternative | Why rejected |
|-------------|-------------|
| Odoo does everything (ERP + analytics + agents) | Odoo is not an analytics platform or agent runtime |
| Databricks as transactional core | Medallion is analytics optimization, not OLTP |
| Ad-hoc agent hosting (no Foundry) | Untraced agents are un-debuggable in production |
| Supabase as control plane | Foundry + APIM + Service Bus is the managed-service path |

---

*Accepted 2026-03-17.*
