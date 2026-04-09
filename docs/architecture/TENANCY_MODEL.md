# Tenancy Model

> **Status**: Approved
> **Date**: 2026-03-23
> **SSOT**: `ssot/architecture/tenancy_model.yaml`
> **Reference**: [Azure Architecture Center — Architect Multitenant Solutions](https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/overview)

---

## Doctrine

> Build a multitenant control plane, but keep the most sensitive execution planes single-tenant first.

Multitenancy is not one switch. It is a set of architectural choices per layer and per Azure component. Do not make every surface multitenant on day one.

---

## Identity Namespace Rule

Application tenant **is not** the same thing as a Microsoft Entra tenant. Never overload `tenant_id`:

| Identifier | Meaning | Scope |
|------------|---------|-------|
| `customer_tenant_id` | Application-level customer/org boundary | Product/business isolation |
| `workspace_id` | Per-customer workspace instance | Data/asset isolation within a customer |
| `entra_tenant_id` | Microsoft Entra directory ID | Identity provider boundary |

---

## Tenancy Classes

### 1. Public Surface

No tenant data, no auth, no customer state. Docs-grounded, advisory-only.

### 2. Multitenant Control Plane

Tenant-aware orchestration, provisioning, governance, and telemetry. Shared runtime with logical tenant isolation. Customer data stays in tenant-scoped data planes, never in the control plane data path.

**Requirements**: Tenant context in every request. No cross-tenant data leakage. Tenant-scoped audit trail. Shared compute acceptable.

### 3. Tenant-Isolated Execution Plane

Single-customer workspace per deployment. ERP records, approvals, finance, HR, CRM. Tenant isolation errors are the most expensive. Single-tenant first.

**Requirements**: Tenant-scoped identity, storage, retrieval, and audit. No shared data-path mixing. Add multitenant control-plane support later.

### 4. Tenant-Isolated Creative Workspace

Per-client creative environment. Media assets, prompts, brand presets, exports, approvals. Brand/data leakage risk is high. Start single-tenant per workspace.

**Requirements**: One workspace = one tenant boundary. Shared OSS toolkit can be multitenant-capable. Commercial surface starts isolated.

---

## Product Surface Assignments

| Surface | Tenancy Class | Rationale |
|---------|---------------|-----------|
| **Landing Assistant** | Public | No tenant data. Docs/pricing only. No customer data path. |
| **Diva Copilot** | Multitenant Control Plane | Best SaaS shell candidate. Orchestration above customer-specific systems. Tenant-aware now, isolated data planes behind connectors. |
| **Odoo Copilot** | Tenant-Isolated Execution | Most sensitive: ERP, finance, HR. Single-customer workspace first. |
| **Studio Copilot / W9** | Tenant-Isolated Creative | Media/brand assets. Leakage risk high. Single-tenant per workspace first. |

---

## Design Rules per Surface

### Landing Assistant
- Non-tenant-aware, non-action-capable, docs-grounded
- No Foundry tools exposed
- Public and anonymous

### Diva Copilot
- Multitenant control plane from day one
- Single-tenant or strongly isolated data planes
- Tenant context required in every API call
- Execution/data systems behind tenant-scoped connectors

### Odoo Copilot
- One customer workspace per logical tenant
- Tenant-scoped identity, storage, retrieval, audit
- Add multitenant control-plane support later
- No shared data-path mixing first

### Studio Copilot / W9 Studio
- One workspace = one tenant boundary
- Shared OSS/mediaops toolkit multitenant-capable
- W9 commercial surface starts isolated

---

## Repo Alignment

### Multitenant doctrine fit

| Repo | Why |
|------|-----|
| `platform` | Shared infrastructure and orchestration |
| `data-intelligence` | Analytics serving multiple contexts |
| `agent-platform` | Agent runtime serving multiple surfaces |
| `ugc-mediaops-kit` | OSS toolkit designed for reuse |

### Single-tenant first

| Repo | Why |
|------|-----|
| `odoo` | Customer-specific ERP data and execution |
| Customer studio workspaces | Tenant-bound creative assets |
| Tenant delivery repos | Customer-specific delivery state |

---

## Isolation Decision Matrix

| Component | Control Plane | Execution Plane | Creative Workspace |
|-----------|---------------|-----------------|-------------------|
| **Compute** | Shared + tenant context | Dedicated/strongly isolated | Dedicated per workspace |
| **Networking** | Shared VNet + NSG | Tenant-scoped NSG or dedicated | Workspace-scoped |
| **Storage** | Shared + tenant prefix | Tenant-scoped containers/accounts | Workspace-scoped containers |
| **Data** | Metadata only | Tenant-scoped DB/schema | Workspace-scoped storage |
| **Identity** | Entra + customer_tenant_id | Tenant-scoped identity | Workspace-scoped identity |
| **Governance** | Centralized audit + policy | Tenant-scoped audit trail | Workspace-scoped audit |
| **Cost** | Shared metered | Per-tenant attribution | Per-workspace attribution |

---

## What NOT to Do

- Do not make Odoo Copilot multitenant on day one — it is the most sensitive surface
- Do not overload `tenant_id` to mean Entra directory — keep `customer_tenant_id`, `workspace_id`, `entra_tenant_id` separate
- Do not assume global multitenancy — decide per component and per isolation model
- Do not mix customer data in the control plane data path
- Do not force single-tenant repos into multitenant-first doctrine

---

## Cross-References

| Document | Purpose |
|----------|---------|
| `ssot/architecture/tenancy_model.yaml` | Machine-readable SSOT |
| `docs/architecture/AI_RUNTIME_AUTHORITY.md` | Tool profiles per assistant surface |
| `ssot/agents/diva_copilot.yaml` | Tool envelope and auth policy |
| `ssot/agents/odoo_copilot_precursor.yaml` | Odoo Copilot precursor scope |

---

*Machine-readable version: `ssot/architecture/tenancy_model.yaml`*
