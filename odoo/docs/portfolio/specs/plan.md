# Odoo EE → CE/OCA SaaS Platform – Plan

## 1. Release Overview

* **v0.1 – Internal Single-Tenant Baseline**

  * Single TBWA finance tenant on Odoo 18 CE + OCA + ipai_finance_ppm.
  * Manual provisioning via scripts, minimal UI.

* **v0.2 – Multi-Tenant Control Plane (Internal use only)**

  * Platform Dashboard, Tenants List, Tenant Detail, Tenant Create Wizard.
  * Basic Keycloak + n8n integration for provisioning.

* **v1.0 – EE-Equivalent SaaS for TBWA Cluster**

  * Stable multi-tenant control plane with module bundles, infra templates, SSO, Supabase analytics, and billing overview.
  * Runbooks and AI agent flows in production.

* **v1.1+ – External Tenant Ready**

  * External-facing tenant portal improvements, better billing, optional self-signup.

---

## 2. Milestones per Release

### v0.1 – Internal Baseline

**Goals**

* Run **one production Odoo 18 CE tenant** with ipai_finance_ppm and OCA finance modules.
* Wire tenant to Supabase for Finance PPM reporting.

**Included Pages**

* `platform_dashboard` (minimal)
* `tenant_detail` (read-only, no infra actions yet)

**Dependencies**

* Base Odoo images in registry.
* Postgres deployment.
* Supabase project and finance schema.

---

### v0.2 – Multi-Tenant Control Plane

**Goals**

* Support **multiple tenants** managed from a single UI.
* Automated provisioning with n8n and GitOps (single Helm template per tenant).

**Included Pages**

* `platform_dashboard` (KPIs + operations list)
* `tenants_list`
* `tenant_detail` (Overview, Modules, Infra tabs)
* `tenant_create` (wizard)

**Dependencies**

* n8n workflows for create/pause/resume/decommission.
* GitHub Actions pipeline for Odoo image and Helm chart.
* Keycloak integration for SSO templates.

---

### v1.0 – EE-Equivalent SaaS for TBWA Cluster

**Goals**

* Provide **3–4 EE-equivalent bundles**: Finance PPM, CRM/Sales, HR/Timesheets, Retail (Scout).
* Analytics Hub with Supabase+Superset for at least 2 tenants.
* Billing & subscription overview for TBWA cluster.

**Included Pages**

* `module_catalog`
* `infra_templates`
* `analytics_hub`
* `billing_overview`
* `tenant_portal` (basic version)
* `support_center`
* `ai_console` (MVP)

**Dependencies**

* Defined ipai_* and OCA module mapping for each bundle.
* Superset dashboards for Finance PPM and Scout.
* Mattermost channels wired to alerts.
* AI agent definitions (module audit, infra upgrade planner).

---

## 3. Risks & Mitigations

| risk_id | description                                         | impact | likelihood | mitigation                                                               |
| ------- | --------------------------------------------------- | ------ | ---------- | ------------------------------------------------------------------------ |
| R1      | Odoo upgrades breaking OCA/ipai_* compatibility     | high   | medium     | Maintain staging env, pinned versions, automated smoke tests via CI      |
| R2      | Misconfigurable multi-tenancy causing data leakage  | high   | low        | Enforce DB-per-tenant, strict network policies, no cross-tenant DB users |
| R3      | n8n / GitHub Actions failures blocking provisioning | medium | medium     | Idempotent workflows, retries, runbook links from UI                     |
| R4      | Supabase sync lag or schema drift                   | medium | medium     | Use views, versioned schemas, replication monitoring                     |
| R5      | Over-reliance on AI agents for infra changes        | medium | medium     | Keep final apply steps manual/confirm-only, require human approval       |

---

## 4. Open Questions

* How strict should DB-per-tenant vs schema-per-tenant be for early TBWA rollouts?
* Do we centralize billing logic inside this platform or integrate with an external billing tool?
* Which Odoo EE features are **must-have parity** in v1 vs v1.1+?
* How much of Supabase data is read-only vs requiring write-backs from AI agents?
* Will external customers eventually require white-labeling for the control plane?
