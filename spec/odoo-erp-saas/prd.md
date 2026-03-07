# PRD — Odoo ERP SaaS

## 1. Document Control

- Feature slug: `odoo-erp-saas`
- Product name: `InsightPulseAI Odoo ERP SaaS`
- Status: Draft
- Owner: InsightPulseAI
- Primary contact: business@insightpulseai.com
- SSOT bundle:
  - `spec/odoo-erp-saas/constitution.md`
  - `spec/odoo-erp-saas/prd.md`
  - `spec/odoo-erp-saas/plan.md`
  - `spec/odoo-erp-saas/tasks.md`

## 2. Executive Summary

Build a production-grade, self-hosted Odoo ERP SaaS platform that delivers Odoo Community Edition + curated OCA parity modules + thin InsightPulseAI bridge modules as a managed multi-tenant service.

The platform must provide:
- tenant lifecycle automation
- opinionated deployment/runtime management
- upgrade-safe extension patterns
- integrated observability, backups, security, and billing hooks
- AI/service bridges through external platform services rather than EE lock-in

This product is not a one-off hosted VM offer. It is a repeatable SaaS operating model for provisioning, operating, governing, and monetizing Odoo-based ERP environments.

## 3. Problem Statement

Current market options split into three weak patterns:

1. **DIY self-hosting**
   - slow to deploy
   - heavy DevOps burden
   - inconsistent security and backup posture
   - weak upgrade discipline

2. **Generic marketplace images / control-panel bundles**
   - accelerate initial install
   - but stop at infrastructure convenience
   - do not provide full tenant lifecycle, productized governance, or ERP SaaS control plane

3. **Odoo Enterprise / Odoo.sh dependency**
   - simpler operations
   - but creates vendor lock-in and reduces flexibility around infrastructure, extensions, data controls, and AI/service integrations

InsightPulseAI needs an internal and customer-facing SaaS platform that preserves:
- infrastructure sovereignty
- module composability
- OCA-first EE parity strategy
- external bridge pattern for non-module capabilities
- deterministic CI/CD and spec-governed delivery

## 4. Product Vision

Deliver an "Odoo.sh-next" style SaaS for Odoo CE + OCA, with:
- self-hosted control over infra and data
- standardized tenant provisioning
- policy-enforced runtime management
- modular ERP bundles by use case
- integrated AI/service bridges via Supabase, n8n, Azure AI, and related platform services
- zero-manual-ops bias through agent-driven and CI-driven workflows

## 5. Goals

### Business Goals
- Reduce time-to-live for a new tenant from days/weeks to under 1 hour
- Support repeatable packaging for SMEs, agencies, and enterprise deployments
- Create a monetizable ERP SaaS offer with clear plan tiers and add-on services
- Lower TCO relative to EE + Odoo.sh for customers needing flexibility and control

### Product Goals
- Provision new tenants deterministically
- Support curated app packs by vertical/use case
- Enforce secure-by-default runtime posture
- Enable upgrades with minimal custom-module drift
- Expose admin/operator controls through a unified SaaS control plane

### Technical Goals
- Odoo CE as ERP core
- OCA modules for EE parity wherever available
- `ipai_*` bridges only for external-service integration and thin glue
- Supabase as primary control plane for metadata, secrets references, audit state, orchestration state, and tenant registry
- Docker-based Odoo runtime with deterministic images
- CI/CD-first delivery with evidence-backed promotion

## 6. Non-Goals

- Rebuilding all Odoo Enterprise SaaS-only services as native Odoo addons
- Supporting arbitrary unreviewed third-party addons per tenant
- Allowing ad hoc server-level customization outside governed pipelines
- Building a marketplace image only
- Making Azure-specific infrastructure a hard dependency for all deployments

## 7. Target Users

### Primary Users
- Internal platform operators
- ERP implementation teams
- SMB and mid-market businesses adopting managed Odoo
- Agencies or multi-brand groups needing multiple governed ERP tenants

### Secondary Users
- Finance admins
- HR / Operations teams
- CRM / Sales managers
- External implementation partners under governed delivery rules

## 8. Core Value Proposition

**For customers:**
- ERP SaaS with infrastructure control and lower lock-in
- faster onboarding
- curated, production-ready module bundles
- stronger governance than ad hoc self-hosting

**For operators:**
- repeatable provisioning
- deterministic upgrades
- centralized observability
- standardized backup / restore / incident response

**For engineering:**
- spec-driven delivery
- OCA-first parity strategy
- minimal custom surface area
- externalized AI/service bridges

## 9. Product Architecture Planes

The product decomposes into five planes. The runtime stack (Odoo + PG + Docker) is **commodity**. The operations plane and control plane are **the real product**.

### Product Flow

```
Commercial plan
      │
      ▼
Tenant/runtime profile (Control Plane)
      │
      ▼
Governed infrastructure (Infrastructure Plane)
      │
      ▼
Odoo runtime (Runtime Plane)
      │
      ▼
Ops automation (Operations Plane)
```

### Plane Responsibilities

| Plane | Responsibilities | Azure Services |
|-------|-----------------|----------------|
| **Runtime** | Odoo CE + OCA + PG + Nginx + Docker | Container Apps, ACR |
| **Control** | Tenant registry, plan catalog, module packs, deployment metadata, audit | Supabase (Edge Functions, Vault) |
| **Operations** | Backups, patching, SSL, health checks, upgrades, scaling, evidence packs | Key Vault, Monitor, Log Analytics |
| **Infrastructure** | Compute, storage, networking, ingress, secrets | Container Apps, PG Flexible, Front Door, VNet |
| **Commercial** | Plan tiers, entitlements, billing events, SLA mapping, add-ons | Supabase + billing provider |

### Competitive Positioning (Copy / Adapt / Skip)

What to learn from the Websoft9/marketplace model — and what to surpass:

| Capability | Marketplace Model (Websoft9) | Our Model | Decision |
|------------|------------------------------|-----------|----------|
| Runtime separation from ops | Yes — control panel over Docker | Yes — Supabase control plane | **Copy** the principle |
| Governed operator model | Partial — cPanel-style | Full — CI/CD + evidence-backed | **Adapt** — make it deterministic |
| Tiered plan packaging | Yes — startup/growth/enterprise | Yes — with add-on marketplace | **Copy** |
| Automated backup/SSL/patching | Yes — as Day-2 ops | Yes — as first-class product features | **Copy** |
| Custom module support | Yes — unrestricted | Yes — but governed (OCA-first + curated packs) | **Adapt** — add governance |
| Multi-app expansion on shared infra | Yes — Websoft9 hosts many apps | No — Odoo-specific platform | **Skip** |
| Full infrastructure control | Yes — root/SSH access | Yes — but through governed pipelines, not raw access | **Adapt** |
| Marketplace image as identity | Yes — "deploy in 10 minutes" | No — SaaS operating model, not an image | **Skip** |
| VM-first architecture | Yes — Azure VMs | No — Container Apps-first | **Skip** for end state |
| Broad SLA/DR claims | Yes — in marketing | No — only what evidence actually supports | **Skip** |

---

## 10. Product Scope

### 10.1 In Scope

#### A. Tenant Provisioning
- create tenant records
- assign plan / region / environment
- generate runtime config
- provision database, filestore, domain routing, and secrets references
- initialize baseline modules and demo/seed policy as configured

#### B. SaaS Control Plane
- tenant registry
- plan catalog
- module pack catalog
- environment and deployment metadata
- health status and runtime evidence
- backup / restore status
- upgrade eligibility / drift status
- operator actions log

#### C. Runtime Platform
- custom Odoo Docker image strategy
- reverse proxy / TLS / domain routing
- worker sizing profiles
- scheduled jobs / backups / maintenance hooks
- standardized storage and filestore handling

#### D. ERP App Distribution
- curated app packs by domain:
  - Finance
  - CRM / Sales
  - Inventory / Purchase
  - Project / Services
  - HR
  - Helpdesk / Field Service
  - Website / Portal

#### E. Governance & Security
- tenant isolation
- environment separation
- RBAC for operator/admin roles
- audit logging
- backup policies
- secret-reference-only config posture
- upgrade gate checks

#### F. Integrations / Bridges
- Supabase control-plane integration
- email / SMTP integration
- SSO hooks
- webhook/event hooks
- optional bridge connectors to Azure AI, n8n, document processing, OCR, and analytics services

#### G. Commercial Packaging
- plan tiers
- metered or packaged add-ons
- tenant limits by plan
- support/SLA class mapping

### 10.2 Out of Scope
- free-form customer shell access by default
- unmanaged plugin ecosystem
- arbitrary per-tenant infra topology outside supported templates
- replacing all external AI/document/voice services with native Odoo code

## 11. Functional Requirements

### FR-1 Tenant Lifecycle
The system must support create, suspend, resume, upgrade-plan, downgrade-plan, archive, and delete lifecycle states for each tenant.

### FR-2 Provisioning Automation
The system must provision a new tenant from a predefined service template with deterministic configuration and idempotent execution.

### FR-3 Module Pack Installation
The platform must support operator-approved module packs and install order enforcement.

### FR-4 Plan Enforcement
The platform must enforce plan-based quotas and feature entitlements.

### FR-5 Runtime Health
The platform must capture tenant runtime health, deployment version, backup freshness, and critical alerts.

### FR-6 Backup & Restore
The platform must run scheduled backups and support operator-initiated restore workflows with auditability.

### FR-7 Upgrade Governance
The platform must evaluate module/runtime drift before any upgrade or promotion.

### FR-8 Domain & Access Management
The platform must support tenant domains/subdomains, TLS, and optional SSO integration.

### FR-9 Billing Hooks
The platform must expose billing-relevant events and plan metadata for subscription lifecycle handling.

### FR-10 Operator Console
The platform must provide a unified operator-facing admin surface for tenant status, actions, logs, and evidence.

### FR-11 Observability
The platform must emit logs, metrics, deployment evidence, and backup evidence into a central control-plane record.

### FR-12 Extension Policy
The platform must enforce OCA-first parity and restrict `ipai_*` modules to bridge/meta responsibilities.

## 12. Non-Functional Requirements

### NFR-1 Availability
- baseline target: 99.9% for production plans
- higher tiers may target 99.95% with HA options

### NFR-2 Security
- secret values never committed to repo
- encrypted at rest and in transit
- least-privilege service credentials
- auditable operator actions

### NFR-3 Performance
- page responsiveness and worker sizing must meet agreed plan SLOs
- background jobs must be isolated from interactive workloads where required

### NFR-4 Scalability
- vertical scaling supported by plan profile
- future horizontal/read-replica/HA patterns must remain possible without tenant redesign

### NFR-5 Maintainability
- deterministic image builds
- upgrade playbooks
- CI-enforced validation
- evidence packs for releases and restores

### NFR-6 Portability
- default reference deployment may target Azure or DigitalOcean, but product architecture must remain cloud-portable

## 13. Product Packaging

### Plan A — Starter
- small team / single entity
- baseline module bundle
- standard backup window
- community/standard support tier

### Plan B — Growth
- larger user counts
- more workers/resources
- daily backups
- business-hours support
- selected integrations

### Plan C — Enterprise
- advanced sizing
- stronger SLA
- restore priority
- SSO / advanced controls
- premium support and integration options

### Add-Ons
- extra storage
- advanced analytics
- OCR / document processing bridge
- AI assistant bridge
- multi-company pack
- sandbox / staging environment
- premium support

## 14. Key User Flows

### Flow 1: New Tenant Launch
Operator selects plan + region + app pack → system provisions tenant → baseline modules install → health checks pass → domain/TLS activate → tenant marked live.

### Flow 2: Plan Upgrade
Operator changes entitlement profile → infra/runtime checks run → new limits/resources apply → billing event emitted → audit record stored.

### Flow 3: Safe Upgrade
Operator selects approved release target → preflight checks validate drift/backups/module compatibility → deployment executes → post-deploy evidence stored.

### Flow 4: Incident Restore
Operator chooses restore point → recovery workflow executes → health validation completes → incident timeline and evidence retained.

## 15. Success Metrics

### Business Metrics
- time to first live tenant
- monthly recurring revenue
- gross margin by plan
- support hours per tenant
- churn / expansion rate

### Product Metrics
- tenant provisioning success rate
- median provisioning time
- backup freshness compliance
- restore success rate
- upgrade success rate
- number of manual operator interventions per tenant/month

### Engineering Metrics
- image build reproducibility
- drift detection coverage
- failed deploy rollback time
- module compatibility pass rate

## 16. Risks

- OCA parity gaps for some EE-adjacent capabilities
- custom-module sprawl if bridge policy is not enforced
- tenant-specific exceptions eroding standardization
- billing/support complexity across plan tiers
- HA architecture increasing operational cost and product complexity

## 17. Open Questions

- single-db-per-tenant vs grouped tenancy strategy for lower tiers
- canonical billing engine/provider
- default cloud reference architecture for v1 GA
- operator console implementation surface: Odoo admin, external web app, or hybrid
- whether customer-facing self-service provisioning is included in v1 or deferred

## 18. Launch Recommendation

### Phase 1 — Internal Platform
- single-tenant managed deployments
- standardized image
- core control-plane registry
- backups / observability / upgrade gates

### Phase 2 — Managed Multi-Tenant SaaS
- repeatable tenant templates
- operator console
- plan entitlements
- billing hooks

### Phase 3 — Self-Service SaaS
- guided onboarding
- customer admin portal
- add-on marketplace
- advanced compliance / HA tiers
