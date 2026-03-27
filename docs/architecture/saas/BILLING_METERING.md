# SaaS Billing & Metering Design Authority

> Declares the per-tenant billing and metering architecture for Azure SaaS Workload compliance.
> Implementation is **deferred** — this document establishes the design authority and constraints.
>
> SaaS authority: https://learn.microsoft.com/en-us/azure/architecture/guide/saas/plan-journey-saas
> Cross-references:
>   - `docs/architecture/target-platform-architecture.md` (SaaS Readiness Gate)
>   - `docs/architecture/microsoft_collection_alignment.md` §7 (billing/cost management gap)
>   - `ssot/governance/platform-strategy-2026.yaml` (billing_metering_status)
>   - `docs/architecture/reliability_operating_model.md` §9 (SaaS incident model)

---

## 1. What Is Metered

| Meter | Unit | Applies To |
|-------|------|-----------|
| ERP transactions | API calls or document count per period | Odoo workload |
| AI agent invocations | Request count per period | Foundry agents |
| Document processing | Pages processed per period | Document Intelligence |
| Data storage | GB stored per period | Databricks / ADLS |
| Compute time | vCPU-hours per period | ACA container apps |

These are the **candidate meters**. Final meter selection depends on pricing model (per-seat, usage-based, or hybrid). The decision is deferred until the first external tenant is onboarded.

---

## 2. Meter Source of Truth

| Component | Authority |
|-----------|----------|
| ERP usage | Odoo `ir.logging` + custom usage model (`ipai.tenant.usage`) |
| Agent usage | Application Insights custom metrics + Foundry telemetry |
| Document processing | Document Intelligence API response metadata |
| Storage | Azure Cost Management API or Storage Analytics |
| Compute | Azure Monitor container metrics |

All meter data flows into a **usage events table** for aggregation. The table does not exist yet — schema is defined below as a target.

---

## 3. Tenant Identity Key

| Field | Value |
|-------|-------|
| Tenant identifier | `tenant_id` (UUID, assigned at onboarding) |
| Source of truth | Entra ID (target) / Keycloak (transitional) |
| Propagation | HTTP header `X-Tenant-Id` or JWT claim `tenant_id` |
| Constraint | Every metered event MUST include `tenant_id` |

---

## 4. Usage Event Schema (Target)

```yaml
# Target schema — not yet implemented
usage_event:
  event_id: uuid
  tenant_id: uuid
  meter_type: enum(erp_tx, agent_invoke, doc_page, storage_gb, compute_vcpu_hr)
  quantity: decimal
  timestamp: iso8601
  source_service: string
  correlation_id: string  # traces back to App Insights
```

**Schema authority**: This document. Implementation will be a Supabase migration or Odoo model, depending on where the usage aggregation service runs.

---

## 5. Aggregation Boundary

- Usage events are collected **per-request** (fine-grained)
- Aggregation to billing periods happens in the **aggregation service** (not at collection time)
- Billing period: **calendar month** (aligned with Azure billing cycle)
- Aggregation output: one row per tenant per meter per period

---

## 6. Reconciliation Authority

| Reconciliation | Owner | Mechanism |
|---------------|-------|-----------|
| Usage events vs Azure Cost Management | Platform lead | Monthly comparison (manual until automated) |
| Aggregated usage vs invoice | Finance lead | Month-end close process |
| Tenant disputes | Platform lead + finance lead | Evidence from usage events + App Insights traces |

---

## 7. Chargeback / Showback Policy

| Mode | Description | Status |
|------|------------|--------|
| **Showback** (current) | Internal cost visibility per workload/resource group | Active via Azure Cost Management |
| **Chargeback** (target) | Per-tenant invoicing based on metered usage | Deferred — requires external tenant onboarding |

Showback is sufficient for the current single-operator model. Chargeback requires:
- Usage aggregation service operational
- Pricing model defined
- Billing integration (Stripe, manual invoice, or Azure Marketplace)

---

## 8. Implementation Status

| Component | Status |
|-----------|--------|
| Meter definition | `partial` — candidate meters identified, not finalized |
| Usage event schema | `not_started` — target schema defined, not implemented |
| Collection instrumentation | `not_started` |
| Aggregation service | `not_started` |
| Reconciliation process | `not_started` |
| Chargeback integration | `not_started` |
| Showback (Azure Cost Mgmt) | `complete` — active for internal use |

**Trigger for implementation**: First external tenant onboarding or formal SaaS assessment.

---

*Last updated: 2026-03-21*
