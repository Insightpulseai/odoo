# Odoo EE → CE/OCA SaaS Platform – Tasks

## 1. Epics

* **EPIC-PLATFORM-BASE** – Bootstrap platform repo, base infra, CI.
* **EPIC-TENANCY-CORE** – Multi-tenant model, Tenants list/detail, create wizard.
* **EPIC-BUNDLES-EE-PARITY** – OCA/ipai_* module catalog and EE-equivalent bundles.
* **EPIC-SSO-KEYCLOAK** – Keycloak integration and SSO config per tenant.
* **EPIC-AUTOMATION-N8N** – n8n workflows for provisioning and lifecycle.
* **EPIC-ANALYTICS-SUPABASE** – Supabase/Superset analytics hub.
* **EPIC-BILLING-TBWA** – Billing overview and plan mapping for TBWA cluster.
* **EPIC-AI-CONSOLE** – AI agents console and ops integration.

---

## 2. Task Table (Issue-Ready)

| id  | title                                                                 | type    | epic                    | scope_notes                                                                                 | effort | priority |
| --- | --------------------------------------------------------------------- | ------- | ----------------------- | ------------------------------------------------------------------------------------------- | ------ | -------- |
| T1  | Init platform repo with Spec Kit and base folder layout               | chore   | EPIC-PLATFORM-BASE      | Create `spec/`, `api/`, `web/`, `infra/`, `n8n/` directories; add this Spec Kit as baseline | S      | P0       |
| T2  | Configure GitHub Actions CI pipeline                                  | infra   | EPIC-PLATFORM-BASE      | Lint, tests, Docker build for control plane; Odoo images built in separate workflow         | M      | P0       |
| T3  | Define Tenant, Bundle, InfraTemplate, SSOConfig schemas               | feature | EPIC-TENANCY-CORE       | Add core models and migrations to backend API                                               | M      | P0       |
| T4  | Implement `/api/tenants` CRUD and health endpoints                    | feature | EPIC-TENANCY-CORE       | As per PRD; include filters, pagination, health summary                                     | M      | P0       |
| T5  | Build `tenants_list` page with filters and search                     | feature | EPIC-TENANCY-CORE       | React page with table, filters bar, search input, create tenant button                      | M      | P0       |
| T6  | Build `platform_dashboard` page with KPIs and events                  | feature | EPIC-TENANCY-CORE       | KPIs cards, tenants health table, operations timeline                                       | M      | P1       |
| T7  | Implement `tenant_detail` Overview, Modules, Infra tabs               | feature | EPIC-TENANCY-CORE       | Panels and actions per PRD; stub APIs where necessary                                       | L      | P0       |
| T8  | Implement `tenant_create` multi-step wizard                           | feature | EPIC-TENANCY-CORE       | Identity, plan, bundle, infra, SSO, review; POST `/api/tenants`                             | L      | P0       |
| T9  | Catalog CE/OCA/ipai_* modules and store module metadata               | feature | EPIC-BUNDLES-EE-PARITY  | Script or config to load modules list into Module table                                     | M      | P1       |
| T10 | Define standard EE-equivalent bundles (Finance, CRM, HR)              | feature | EPIC-BUNDLES-EE-PARITY  | Create initial ModuleBundle records; tag OCA/ipai modules per bundle                        | M      | P1       |
| T11 | Implement `module_catalog` UI (modules & bundles list)                | feature | EPIC-BUNDLES-EE-PARITY  | Filterable list; bundle detail view                                                         | M      | P1       |
| T12 | Integrate Keycloak templates API (`/integrations/keycloak/templates`) | feature | EPIC-SSO-KEYCLOAK       | Provide realm/client template JSON for wizard                                               | S      | P1       |
| T13 | Build `sso_config` backend model and CRUD                             | feature | EPIC-SSO-KEYCLOAK       | Attach SSOConfig to Tenant; store realm/client IDs and redirect URIs                        | M      | P1       |
| T14 | Wire n8n workflow for tenant create/pause/resume                      | infra   | EPIC-AUTOMATION-N8N     | Create and document n8n workflow; expose webhook triggers used by backend                   | M      | P0       |
| T15 | Implement `/api/tenants/{id}/operations` to call n8n                  | feature | EPIC-AUTOMATION-N8N     | Operation types: create, pause, resume, rebuild, upgrade_image                              | M      | P0       |
| T16 | Configure Supabase project and schemas for tenant data                | infra   | EPIC-ANALYTICS-SUPABASE | Define replication approach from Odoo to Supabase                                           | L      | P1       |
| T17 | Build `analytics_hub` page                                            | feature | EPIC-ANALYTICS-SUPABASE | Show mapping of tenants → Supabase schema → Superset dashboards                             | M      | P1       |
| T18 | Implement `BillingSubscription` model and basic API                   | feature | EPIC-BILLING-TBWA       | Store plan, status, period dates for each tenant                                            | M      | P2       |
| T19 | Build `billing_overview` page                                         | feature | EPIC-BILLING-TBWA       | Show per-tenant plan, status, usage metrics                                                 | M      | P2       |
| T20 | Scaffold `ai_console` page                                            | feature | EPIC-AI-CONSOLE         | List AI flows (module audit, infra upgrade planner); basic trigger UI                       | M      | P2       |
| T21 | Add logs viewer component and backend logs endpoint                   | feature | EPIC-TENANCY-CORE       | Expose OperationLog table and logs viewer with filters                                      | M      | P1       |
| T22 | Document runbooks in `support_center`                                 | chore   | EPIC-PLATFORM-BASE      | Link to Mattermost channels, incident procedures, and n8n workflows                         | M      | P1       |

---

## 3. Labels & Conventions

* **Areas**

  * `area/api`, `area/web`, `area/infra`, `area/automation`, `area/analytics`, `area/ai`, `area/docs`.
* **Pages**

  * `page/platform_dashboard`, `page/tenants_list`, `page/tenant_detail`, `page/tenant_create`, `page/module_catalog`, etc.
* **Types**

  * `type/feature`, `type/bug`, `type/chore`, `type/infra`, `type/spike`.
* **Priority**

  * `P0`, `P1`, `P2`, `P3`.

All new issues should reference an **Epic** and at least one **page_id or core entity** from `spec/prd.md`.
