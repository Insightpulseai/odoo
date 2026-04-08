# Tenancy Model

> Canonical tenant isolation policy for the InsightPulse AI platform.
> SSOT: `ssot/architecture/tenancy_model.yaml`

---

## Tenant Identifier Contract

| Identifier | Scope | Example |
|------------|-------|---------|
| `customer_tenant_id` | Business tenant — maps to a customer org / Odoo company | `cust_abc123` |
| `entra_tenant_id` | Microsoft Entra directory — identity plane only | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `workspace_id` | Creative / Studio workspace boundary | `ws_studio_001` |
| `environment_id` | Deployment environment (dev / staging / prod) | `env_dev` |
| `instance_id` | Runtime instance of a service within an environment | `ipai-odoo-dev-web` |

**Rule:** `customer_tenant_id != entra_tenant_id`. Never overload `tenant_id` as a generic catch-all. Every API, schema, and config must use the explicit identifier that matches its scope.

---

## Isolation Planes

### 1. Public Surfaces (No Tenant Data)

| Surface | Examples | Tenant Awareness |
|---------|----------|-----------------|
| Marketing landing pages | `insightpulseai.com`, SaaS landing | None |
| Public documentation | Docs portal | None |
| Public assistant (advisory) | Landing page chat | None |

**Rule:** Public surfaces never receive, store, or route tenant-specific data. No `customer_tenant_id` in request context.

### 2. Multitenant Control Plane

| Surface | Examples | Isolation |
|---------|----------|-----------|
| Diva Copilot orchestration | Mode routing, goal tracking | Logical — `customer_tenant_id` scopes queries |
| Platform metadata | Agent registry, skill catalog | Shared catalog, tenant-scoped bindings |
| Governance / observability | Audit logs, traces, metrics | Tenant-tagged but centrally stored |

**Rule:** Control plane is logically multitenant. All queries, logs, and state must include `customer_tenant_id`. Cross-tenant data leakage is a P0 security defect.

### 3. Tenant-Isolated Execution Plane

| Surface | Examples | Isolation |
|---------|----------|-----------|
| Odoo ERP runtime | Transactional records, invoices, partners | Company-scoped (Odoo `res.company`) |
| Odoo Copilot | ERP assistant, action execution | Per-company, per-user |
| Document Intelligence | OCR extraction, record mapping | Per-document, per-company |
| Genie analytics | Governed Q&A over lakehouse | Per-tenant semantic layer |

**Rule:** Execution plane is tenant-isolated. Odoo enforces via `res.company` and record rules. Copilot enforces via company-scoped conversation access. No cross-company data in a single response.

### 4. Tenant-Isolated Creative Workspace

| Surface | Examples | Isolation |
|---------|----------|-----------|
| W9 Studio | Brand presets, media assets, campaigns | Per-workspace (`workspace_id`) |
| Studio Copilot | Creative finishing, export | Per-workspace |

**Rule:** Creative workspaces are isolated by `workspace_id`. Brand presets, asset libraries, and generation history do not leak across workspaces.

---

## Cross-Plane Rules

1. **Public -> Control Plane:** Requires authentication. No tenant data flows without auth.
2. **Control Plane -> Execution Plane:** `customer_tenant_id` must be propagated in every request.
3. **Execution Plane -> Creative Workspace:** `workspace_id` must be validated against `customer_tenant_id`.
4. **Never:** Route tenant data through public surfaces. Merge tenant contexts in a single response. Use `entra_tenant_id` as a business tenant key.

---

## Current State

| Plane | Status |
|-------|--------|
| Public surfaces | Implemented — no tenant data |
| Multitenant control plane | Partial — Diva modes exist, no formal multi-customer isolation yet |
| Tenant-isolated execution | Single-company only (Odoo company scoping active, multi-tenant not tested) |
| Tenant-isolated creative | Not implemented — W9 Studio is in design |

Multi-customer tenancy is a future milestone. Current runtime is single-company. The model above is the target architecture.

---

## SSOT References

- Machine-readable: `ssot/architecture/tenancy_model.yaml`
- Assistant surfaces: `../agents/ASSISTANT_SURFACES.md`
- Identity: `ssot/identity/entra_target_state.yaml`

---

*Last updated: 2026-03-24*
