# Tasks — Odoo ERP SaaS

> Work breakdown for the InsightPulseAI Odoo ERP SaaS platform.

---

## Phase 1: Internal Platform

### Docker Image Pipeline
- [ ] **1.1.1** Create base Odoo CE 19 Dockerfile (Python 3.12, PG 16 client)
- [ ] **1.1.2** Add OCA module layer with locked submodule pins
- [ ] **1.1.3** Add ipai_* bridge modules layer
- [ ] **1.1.4** Create CI workflow: build → test → tag → push
- [ ] **1.1.5** Set up container registry (ACR or GHCR)
- [ ] **1.1.6** Create image version manifest

### Tenant Provisioning Engine
- [ ] **1.2.1** Create Supabase migration: `tenants` table
- [ ] **1.2.2** Create Supabase migration: `plans` table with entitlements schema
- [ ] **1.2.3** Create Supabase migration: `module_packs` table
- [ ] **1.2.4** Create Supabase migration: `deployments` table
- [ ] **1.2.5** Build provisioning Edge Function: create tenant
- [ ] **1.2.6** Build provisioning script: create PG database
- [ ] **1.2.7** Build provisioning script: initialize Odoo with module pack
- [ ] **1.2.8** Build provisioning script: configure domain routing
- [ ] **1.2.9** Build provisioning script: store secrets in Vault
- [ ] **1.2.10** Build post-provision health check

### Runtime Platform
- [ ] **1.3.1** Create Docker Compose for single-node deployment
- [ ] **1.3.2** Configure Nginx reverse proxy with per-tenant routing
- [ ] **1.3.3** Set up TLS automation (Let's Encrypt)
- [ ] **1.3.4** Define worker sizing profiles (small/medium/large)
- [ ] **1.3.5** Create cron container for scheduled Odoo jobs
- [ ] **1.3.6** Create backup container (pg_dump + filestore)
- [ ] **1.3.7** Create backup schedule configuration

### Observability
- [ ] **1.4.1** Implement tenant health endpoint monitoring
- [ ] **1.4.2** Build backup freshness monitoring
- [ ] **1.4.3** Build deployment version tracking
- [ ] **1.4.4** Configure log aggregation

### Upgrade Governance
- [ ] **1.5.1** Build pre-flight drift check script
- [ ] **1.5.2** Build module compatibility validator
- [ ] **1.5.3** Build backup verification check
- [ ] **1.5.4** Build post-deploy evidence capture
- [ ] **1.5.5** Document rollback procedure

### ERP Entity Model (Company / Branch)
- [ ] **1.6.1** Create Supabase migration: `tenant.organizations` table
- [ ] **1.6.2** Create Supabase migration: `tenant.memberships` table (user ↔ org)
- [ ] **1.6.3** Create Supabase migration: `erp.companies` table (mirrors `res.company`)
- [ ] **1.6.4** Create Supabase migration: `erp.branches` table (optional subdivision)
- [ ] **1.6.5** Create Supabase migration: `erp.company_memberships` table
- [ ] **1.6.6** Create Supabase migration: `erp.branch_memberships` table
- [ ] **1.6.7** Classify existing platform tables: shared master vs company-scoped
- [ ] **1.6.8** Add `organization_id`, `company_id`, `branch_id` columns to scoped tables
- [ ] **1.6.9** Document entity model in `docs/architecture/TENANCY_MODEL.md`

### Active Context & RLS
- [ ] **1.7.1** Define JWT active-context contract (`org_id`, `company_id`, `branch_id`, `role`)
- [ ] **1.7.2** Create RLS policy template: `rls_org_company_branch_read`
- [ ] **1.7.3** Create RLS policy template: `rls_org_company_branch_write`
- [ ] **1.7.4** Create RLS policy template: `rls_shared_master_read`
- [ ] **1.7.5** Apply company-level RLS to transactional tables
- [ ] **1.7.6** Apply branch-narrowing RLS (branch membership OR parent-company admin)
- [ ] **1.7.7** Test: parent company sees all branch data
- [ ] **1.7.8** Test: branch selection narrows scope to that branch only
- [ ] **1.7.9** Test: subsidiaries as separate companies have isolated data

---

## Phase 2: Managed Multi-Tenant SaaS

### Tenant Templates
- [ ] **2.1.1** Define Finance-first template (plan + modules + profile)
- [ ] **2.1.2** Define CRM-first template
- [ ] **2.1.3** Define Inventory-first template
- [ ] **2.1.4** Define Services-first template
- [ ] **2.1.5** Build template instantiation automation

### Operator Console
- [ ] **2.2.1** Design operator console UI (wireframes)
- [ ] **2.2.2** Build tenant list view with health/status
- [ ] **2.2.3** Build tenant actions (provision, suspend, resume, upgrade, restore)
- [ ] **2.2.4** Build audit log viewer
- [ ] **2.2.5** Build deployment evidence viewer
- [ ] **2.2.6** Integrate with Supabase control plane API

### Plan Entitlements
- [ ] **2.3.1** Define Starter plan limits
- [ ] **2.3.2** Define Growth plan limits
- [ ] **2.3.3** Define Enterprise plan limits
- [ ] **2.3.4** Build entitlement enforcement middleware
- [ ] **2.3.5** Build plan upgrade/downgrade workflow

### Billing Integration
- [ ] **2.4.1** Select billing provider (Stripe or custom)
- [ ] **2.4.2** Build billing event emission
- [ ] **2.4.3** Build usage metering for add-ons
- [ ] **2.4.4** Build subscription lifecycle hooks

---

## Phase 3: Self-Service SaaS

### Customer Portal
- [ ] **3.1.1** Build sign-up flow
- [ ] **3.1.2** Build plan selection + payment
- [ ] **3.1.3** Build add-on activation UI
- [ ] **3.1.4** Build customer admin (users, domains, API keys)

### Add-On Marketplace
- [ ] **3.2.1** Build add-on catalog
- [ ] **3.2.2** Build one-click activation with compatibility checks
- [ ] **3.2.3** Build metered billing for usage-based add-ons

### Advanced Operations
- [ ] **3.3.1** Build sandbox/staging environment provisioning
- [ ] **3.3.2** Build SSO configuration (SAML/OIDC)
- [ ] **3.3.3** Build custom domain management
- [ ] **3.3.4** Design HA/multi-region architecture
