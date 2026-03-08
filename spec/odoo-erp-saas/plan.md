# Plan — Odoo ERP SaaS

> Implementation plan for the InsightPulseAI Odoo ERP SaaS platform.

---

## Phase 1: Internal Platform (Foundation)

### 1.1 Docker Image Pipeline

- Create deterministic Odoo CE 19 Docker image
- Pin Odoo CE version, Python 3.12, PostgreSQL 16 client
- Include OCA module layer (locked submodule pins)
- Include `ipai_*` bridge modules
- CI pipeline: build → test → tag with SHA → push to registry
- Registry: Azure Container Registry or GitHub Container Registry

### 1.2 Tenant Provisioning Engine

- Supabase control plane tables:
  - `tenants` — registry with lifecycle state
  - `plans` — plan catalog with entitlements
  - `module_packs` — curated module bundles
  - `deployments` — runtime metadata per tenant
- Provisioning script/Edge Function:
  - Create PostgreSQL database for tenant
  - Initialize Odoo with base + selected module pack
  - Configure domain/subdomain routing
  - Store secrets references in Vault
  - Run post-provision health check

### 1.3 Runtime Platform

- Docker Compose for single-node deployment
- Nginx reverse proxy with per-tenant routing
- TLS via Let's Encrypt (certbot or Caddy)
- Worker sizing profiles (small, medium, large)
- Cron container for scheduled Odoo jobs
- Backup container with pg_dump + filestore archive

### 1.4 Observability

- Tenant health endpoint: `/web/health` per tenant
- Backup freshness monitoring via control plane
- Deployment version tracking
- Log aggregation to Application Insights or Log Analytics

### 1.5 Upgrade Governance

- Pre-flight check script:
  - Compare installed module versions vs target
  - Detect schema drift
  - Verify backup freshness < 24h
  - Validate module compatibility matrix
- Post-deploy evidence capture
- Rollback procedure (restore from pre-upgrade backup)

---

### 1.6 ERP Entity Model (Company / Branch)

> Workstream: WS-ERP-ENTITY-01

Extend the existing `core` + `saas` schemas with Odoo company/branch semantics.
Does NOT create new tenant tables — uses `core.tenant` and `core.app_user` as foundation.

- Uses existing: `core.tenant` (workspace), `core.app_user` (user identity), `saas.accounts` (billing)
- New tables in `erp` schema:
  - `erp.companies` — Odoo `res.company` mirror, FK to `core.tenant` + `core.company`
  - `erp.branches` — optional subdivision under a company
  - `erp.company_memberships` — user ↔ company access (FK to `core.app_user`)
  - `erp.branch_memberships` — user ↔ branch access (FK to `core.app_user`)
- `erp.v_entity_hierarchy` — unified view joining core.tenant + saas.accounts + erp.companies + erp.branches
- Every transactional table must carry `tenant_id` + `company_id` (NOT NULL), `branch_id` (nullable)
- Shared master data tables carry `tenant_id`, with optional `company_id`/`branch_id`
- Classify all existing platform tables into shared vs scoped categories

### 1.7 Active Context & RLS (Company/Branch Scoping)

> Workstream: WS-RLS-CTX-01

Implement row-level security that respects Odoo's parent-company/branch narrowing.

- JWT claims must include `tenant_id`, `company_id`, `branch_id`, `role`
- Supabase `auth.jwt()` extraction for RLS policies
- Company-level RLS: user can read/write when they have membership in `tenant_id` (via core.tenant_membership) + `company_id` (via erp.company_memberships)
- Branch narrowing: if `branch_id` is populated on a row, user must either:
  - Have that branch in their `erp.branch_memberships`, OR
  - Have parent-company admin role (inherits all branch access)
- Selecting a company implies visibility of all its branches
- Selecting a branch narrows scope to that branch only
- Create reusable RLS policy templates for:
  - `rls_org_company_branch_read` — standard read policy
  - `rls_org_company_branch_write` — standard write policy
  - `rls_shared_master_read` — for shared master data (org-wide)

---

## Phase 2: Managed Multi-Tenant SaaS

### 2.1 Tenant Templates

- Predefined tenant templates per vertical:
  - Finance-first (accounting, invoicing, expenses)
  - CRM-first (leads, pipeline, email integration)
  - Inventory-first (warehouse, purchasing, MRP)
  - Services-first (project, timesheet, helpdesk)
- Template = plan + module pack + worker profile + backup policy

### 2.2 Operator Console

- Web-based admin surface (Next.js or Odoo admin module)
- Tenant list with status, plan, health, backup freshness
- Actions: provision, suspend, resume, upgrade, restore, archive
- Audit log viewer
- Deployment evidence viewer

### 2.3 Plan Entitlements

- Enforce per-plan limits:
  - Max users
  - Max workers
  - Storage quota
  - Backup frequency
  - Available module packs
- Entitlement checks at provisioning and plan change

### 2.4 Billing Integration

- Billing event emission (tenant created, plan changed, add-on activated)
- Integration hooks for Stripe or custom billing engine
- Usage metering for add-ons (storage, API calls)
- Plan-level SLA mapping

---

## Phase 3: Self-Service SaaS

### 3.1 Customer Portal

- Self-service sign-up flow
- Plan selection and payment
- Add-on activation
- Basic admin: users, domains, API keys

### 3.2 Add-On Marketplace

- Curated add-on catalog (AI assistant, OCR, analytics, multi-company)
- One-click activation with plan compatibility checks
- Metered billing for usage-based add-ons

### 3.3 Advanced Operations

- Sandbox/staging environments per tenant
- SSO configuration (SAML/OIDC)
- Custom domain management
- HA/multi-region options for enterprise tier

---

## Dependencies

```
Phase 1.1 (Docker) ← foundation for everything
  ├── Phase 1.2 (Provisioning) ← needs images
  ├── Phase 1.3 (Runtime) ← needs images
  └── Phase 1.5 (Upgrades) ← needs image versioning

Phase 1.2 (Provisioning) + 1.3 (Runtime)
  └── Phase 2.1 (Templates) ← needs working provisioning

Phase 2.2 (Console) ← needs Phase 1 complete
Phase 2.3 (Entitlements) ← needs plan catalog
Phase 2.4 (Billing) ← needs entitlements

Phase 3 ← needs Phase 2 complete
```

---

## Technology Decisions

| Component | Choice | Rationale |
|-----------|--------|-----------|
| ERP Core | Odoo CE 19 | CE-only policy, no EE lock-in |
| Parity Modules | OCA | Community-vetted, maintained |
| Container Runtime | Docker (Container Apps target) | Deterministic, portable |
| Control Plane | Supabase | Existing platform, Edge Functions, Vault |
| Image Registry | ACR or GHCR | Azure-native or GitHub-native |
| Reverse Proxy | Nginx or Caddy | Proven, auto-TLS capable |
| Operator Console | Next.js (web repo) | Shared with other web surfaces |
| Billing | Stripe (or custom) | Open question, decide in Phase 2 |
