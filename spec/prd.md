# Odoo EE → CE/OCA SaaS Platform – PRD

## 0. Assumptions

* Target version is **Odoo 18 CE**, with future minor upgrades handled via standard OCA practices.
* Single **primary organization** (TBWA\SMP cluster) with potential sub-tenants (agencies, studios, entities) sharing the same control plane.
* Each tenant gets either **own Postgres DB** or **own schema**; decision configurable but defaults to **DB per tenant**.
* Existing InsightPulseAI stack (Supabase, n8n, Mattermost, Keycloak, agents) is already running or can be provisioned.
* ipai_* custom modules for Finance, PPM, BIR, retail, AI orchestration already exist or will be built incrementally.
* Devs use **Codex CLI + Claude Code** as the default coding workflow; runtime access controlled via environment and secrets, not via raw prompts.

---

## 1. App Snapshot

* **Platforms**

  * Web app (control plane) – React/Next.js (or similar) admin UI.
  * Odoo CE web UI – per-tenant workspaces accessed via subdomains.
* **User Roles**

  * **Platform Owner** – manages infra, global settings, images, OCA catalog.
  * **Platform Operator / DevOps** – runs upgrades, handles incidents, uses AI agents.
  * **Tenant Admin (Agency Admin)** – manages their tenant workspace, users, module bundles, billing info.
  * **Workspace Admin** – config within a tenant's Odoo instance (apps, security, local settings).
  * **End User** – uses Odoo modules (finance, CRM, HR, etc.).
  * **Finance Owner** – sees billing/subscription and access to Superset dashboards.
* **Core Flows**

  * Create and configure a **new tenant workspace** from a pre-defined bundle (e.g., Finance PPM).
  * Attach **Keycloak realm/clients** and SSO to each tenant workspace.
  * Configure **OCA/ipai_* module bundles** per tenant and apply them via deployment.
  * Setup **Supabase/Superset integration** for tenant analytics (e.g., Scout, Finance PPM dashboards).
  * Manage **billing and subscription status** for each tenant.
  * Monitor **health, logs, and backups** across all tenants.

---

## 2. Page Inventory

| page_id            | page_name                         | route / screen_key         | roles                                      | main_goal                                                 |
| ------------------ | --------------------------------- | -------------------------- | ------------------------------------------ | --------------------------------------------------------- |
| platform_dashboard | Platform Overview                 | `/`                        | platform_owner, platform_operator          | High-level view of tenants, health, and queued operations |
| tenants_list       | Tenants                           | `/tenants`                 | platform_owner, platform_operator          | List and manage all tenants                               |
| tenant_detail      | Tenant Detail                     | `/tenants/[tenant_id]`     | platform_owner, platform_operator          | Configure specific tenant (status, modules, infra, SSO)   |
| tenant_create      | Create Tenant Wizard              | `/tenants/new`             | platform_owner                             | Guided tenant workspace creation                          |
| module_catalog     | Module & Bundles Catalog          | `/catalog`                 | platform_owner, platform_operator          | Manage OCA/ipai_* module bundles and presets              |
| infra_templates    | Infra Templates & Images          | `/infra/templates`         | platform_owner, platform_operator          | Manage base Docker images, Helm charts, env presets       |
| sso_config         | SSO & Identity Integrations       | `/integrations/sso`        | platform_owner, platform_operator          | Configure Keycloak realms/clients per tenant              |
| automation_center  | Automation & Workflows (n8n)      | `/integrations/automation` | platform_owner, platform_operator          | View and manage n8n workflows related to tenants          |
| analytics_hub      | Analytics & Supabase/Superset Hub | `/integrations/analytics`  | platform_owner, platform_operator, finance | Link tenants to Supabase schemas and Superset dashboards  |
| billing_overview   | Billing & Subscriptions           | `/billing`                 | platform_owner, finance_owner              | Overview of plans, usage, and invoices                    |
| tenant_portal      | Tenant Self-Service Portal        | `/portal`                  | tenant_admin                               | Tenant admin view of their workspace(s) and subscriptions |
| support_center     | Support & Runbooks                | `/support`                 | all authenticated                          | Docs, runbooks, status links, Mattermost channels         |
| ai_console         | AI & Agents Console               | `/ai-console`              | platform_owner, platform_operator          | Launch and monitor AI flows against platform/tenants      |
| settings_platform  | Platform Settings                 | `/settings`                | platform_owner                             | Global configuration and secrets indirection              |

---

## 3. Page Specs

### 3.1 `platform_dashboard` – Platform Overview

* Route: `/`
* Roles: platform_owner, platform_operator
* Layout zones:

  * `header`: logo, global nav, user menu, environment (dev/stage/prod) indicator
  * `main_content`: summary KPIs, health tiles, recent events
  * `right_sidebar`: active maintenance windows, AI suggestions

**Components**

| component_id             | name                       | type     | props / inputs                         | state / data used                           | behaviors                                                                          |
| ------------------------ | -------------------------- | -------- | -------------------------------------- | ------------------------------------------- | ---------------------------------------------------------------------------------- |
| kpi_tenant_counts        | Tenants KPIs               | card_row | counts: {total, active, paused, error} | `/api/platform/kpi/tenants`                 | clicking a card filters tenants_list by status                                     |
| kpi_resource_usage       | Resource Usage             | card_row | metrics: CPU, RAM, storage, nodes      | `/api/platform/kpi/resources`               | click → navigate to infra_templates or DO metrics page                             |
| tenants_health_table     | Tenant Health Table        | table    | tenants[], filters                     | `/api/tenants?include_health=true&limit=20` | row click → tenant_detail; severity badge colors based on health                   |
| operations_timeline      | Recent Operations Timeline | list     | events[]                               | `/api/operations/recent`                    | entry click → opens operation_detail drawer                                        |
| ai_recommendations_panel | AI Recommendations         | panel    | suggestions[]                          | `/api/ai/platform-suggestions`              | click on suggestion triggers relevant flow (e.g., open PR template or create task) |

**Modals / Drawers**

* `operation_detail_drawer`

  * Opens from operations_timeline row click.
  * Shows operation logs, status, links to DO, n8n, GitHub actions.
  * Actions: re-run operation, open in n8n, view logs.

**Navigation**

* To `tenants_list` via KPIs and quick links.
* To `ai_console` via AI Recommendations.
* To `billing_overview` via top bar or KPI detail.

---

### 3.2 `tenants_list` – Tenants

* Route: `/tenants`
* Roles: platform_owner, platform_operator
* Layout zones:

  * `header`: title, search, filters, "Create tenant" button
  * `main_content`: table/grid of tenants with status, key metrics

**Components**

| component_id         | name            | type   | props / inputs                     | state / data used                   | behaviors                                                |
| -------------------- | --------------- | ------ | ---------------------------------- | ----------------------------------- | -------------------------------------------------------- |
| tenants_filters_bar  | Tenants Filters | form   | status, plan, region, agency group | local filter state                  | on_change → refetch tenants table                        |
| tenants_search_input | Search          | input  | query                              | local query state                   | debounce → refetch                                       |
| tenants_table        | Tenants Table   | table  | tenants[], sort, pagination        | `/api/tenants` with filters + query | row click → tenant_detail; badge click filters by status |
| create_tenant_button | "Create Tenant" | button | label, route                       | none                                | click → navigate to tenant_create                        |

**Modals / Drawers**

* None (v1); creation happens via tenant_create page.

**Navigation**

* To `tenant_detail` via row click.
* To `tenant_create` via primary button.

---

### 3.3 `tenant_detail` – Tenant Detail

* Route: `/tenants/[tenant_id]`
* Roles: platform_owner, platform_operator
* Layout zones:

  * `header`: tenant name, status chip, actions (Pause, Resume, Decommission)
  * `tabs`: Overview, Modules, Infra, SSO, Analytics, Billing, Logs
  * `main_content`: tab-specific content

**Components**

| component_id           | name            | type       | props / inputs                                   | state / data used             | behaviors                                                |
| ---------------------- | --------------- | ---------- | ------------------------------------------------ | ----------------------------- | -------------------------------------------------------- |
| tenant_status_badge    | Tenant Status   | badge      | status                                           | part of tenant object         | click (optional)→ open change-status modal               |
| tenant_action_buttons  | Tenant Actions  | button_row | actions: pause, resume, rebuild, open odoo_url   | tenant state                  | triggers /api/tenants/[id]/ops                           |
| tenant_tabs            | Tenant Tabs     | tabs       | active_tab                                       | URL param or local state      | change tab → updates route query                         |
| tenant_overview_panel  | Overview        | panel      | tenant core fields, k8s namespace, DB info, URLs | `/api/tenants/[id]`           | links to infra, SSO, analytics tabs                      |
| tenant_modules_table   | Modules/Bundles | table      | modules[], presets[]                             | `/api/tenants/[id]/modules`   | toggle module state, apply presets, create PR suggestion |
| tenant_infra_panel     | Infra Panel     | panel      | nodes, pods, image versions                      | `/api/tenants/[id]/infra`     | click image version → proposal to upgrade (opens modal)  |
| tenant_sso_panel       | SSO Panel       | panel      | keycloak realm, client ids, redirect URIs        | `/api/tenants/[id]/sso`       | open in Keycloak admin, test login                       |
| tenant_analytics_panel | Analytics Panel | panel      | Supabase schema, Superset dashboard links        | `/api/tenants/[id]/analytics` | open Superset dashboard, test ETL job                    |
| tenant_billing_panel   | Billing Panel   | panel      | plan, usage metrics, next invoice date           | `/api/tenants/[id]/billing`   | adjust plan, open invoice (future)                       |
| tenant_logs_viewer     | Logs & Events   | viewer     | logs[], filters                                  | `/api/tenants/[id]/logs`      | filter by severity, open in DO/n8n                       |

**Modals / Drawers**

* `tenant_status_change_modal`

  * Pause/Resume/Decommission with impacts explained.
* `apply_bundle_modal`

  * Choose OCA/ipai_* bundle → generate GitHub PR / GitOps job.
* `image_upgrade_modal`

  * Select target Odoo/OS image → schedule rollout via GitHub Actions + Helm.

**Navigation**

* To **Odoo workspace** (tenant-specific URL).
* To `automation_center` for workflows referencing this tenant.
* To `analytics_hub` filtered by this tenant.

---

### 3.4 `tenant_create` – Create Tenant Wizard

* Route: `/tenants/new`
* Roles: platform_owner
* Layout zones:

  * `header`: wizard title, progress
  * `main_content`: stepper form (Identity → Plan → Bundle → Infra → SSO → Review)

**Components (examples)**

| component_id         | name            | type  | props / inputs                         | state / data used                      | behaviors                                                    |
| -------------------- | --------------- | ----- | -------------------------------------- | -------------------------------------- | ------------------------------------------------------------ |
| tenant_identity_step | Identity Step   | form  | tenant_name, slug, agency_group        | local wizard state                     | validate uniqueness                                          |
| tenant_plan_step     | Plan Step       | form  | plan_options                           | static config                          | selects billing profile                                      |
| tenant_bundle_step   | Bundle Step     | form  | module_bundles[]                       | `/api/catalog/bundles`                 | chooses OCA/ipai_ bundles                                    |
| tenant_infra_step    | Infra Step      | form  | region, DB strategy, HA level          | DO regions, templates                  | writes infra spec to be applied                              |
| tenant_sso_step      | SSO Step        | form  | Keycloak realm template, redirect URIs | `/api/integrations/keycloak/templates` | preview config                                               |
| tenant_review_step   | Review & Create | panel | aggregated wizard state                | local wizard state                     | on submit → POST `/api/tenants` and schedule infra workflows |

**Modals / Drawers**

* `confirm_create_tenant_modal` – confirm operations, show estimated time and steps.

**Navigation**

* On success: redirect to `tenant_detail` for new tenant.

---

### 3.5 `module_catalog` – Module & Bundles Catalog

* Route: `/catalog`
* Roles: platform_owner, platform_operator
* Purpose: define **EE-equivalent bundles** (Finance PPM, HR, CRM, etc.) out of CE/OCA/ipai_ modules.

**Key Components**

| component_id        | name          | type  | props / inputs                            | data used                          | behaviors                                     |
| ------------------- | ------------- | ----- | ----------------------------------------- | ---------------------------------- | --------------------------------------------- |
| module_list         | Module List   | list  | modules[], filters (OCA repo, ipai, core) | `/api/catalog/modules`             | inspect module metadata, dependencies         |
| bundle_list         | Bundle List   | list  | bundles[]                                 | `/api/catalog/bundles`             | click → bundle_detail                         |
| bundle_detail_panel | Bundle Detail | panel | bundle modules, description, tags         | `/api/catalog/bundles/[bundle_id]` | create PR to modify bundle, assign to tenants |

(Other pages follow similar pattern; for brevity, not all tables are expanded.)

---

## 4. Component Library Summary

| component_id        | appears_on                                   | reusable | config knobs                        |
| ------------------- | -------------------------------------------- | -------- | ----------------------------------- |
| kpi_tenant_counts   | platform_dashboard                           | yes      | labels, metrics source              |
| tenants_table       | platform_dashboard, tenants_list             | yes      | columns, filter config, actions     |
| tenant_status_badge | tenants_list, tenant_detail                  | yes      | status mapping, click behavior      |
| stepper_wizard      | tenant_create, sso_config (later)            | yes      | steps array, validation mode        |
| integration_panel   | analytics_hub, automation_center, sso_config | yes      | integration type, status, actions   |
| logs_viewer         | tenant_detail, platform_dashboard            | yes      | log source, filters, link templates |

---

## 5. Data Model & API Contracts

### 5.1 Core Entities

**Tenant**

* Fields: `id`, `slug`, `name`, `agency_group`, `status` (active/paused/error/decommissioned), `plan_id`, `db_name`, `db_host`, `k8s_namespace`, `odoo_url`, `created_at`, `updated_at`.

**ModuleBundle**

* Fields: `id`, `name`, `code`, `description`, `type` (finance_ppm, crm, hr, retail, etc.), `modules` (array of module names), `version`, `created_at`, `updated_at`.

**TenantModuleState**

* Fields: `id`, `tenant_id`, `module_name`, `source` (core/oca/ipai), `state` (installed/removed/pending), `last_operation_id`.

**InfraTemplate**

* Fields: `id`, `name`, `k8s_chart`, `docker_image_odoo`, `docker_image_pg`, `size_profile`, `env_defaults`, `version`.

**SSOConfig**

* Fields: `id`, `tenant_id`, `keycloak_realm`, `keycloak_client_id`, `redirect_uris`, `status`.

**AnalyticsConfig**

* Fields: `id`, `tenant_id`, `supabase_project`, `schema_name`, `sync_mode`, `superset_dashboard_url`.

**BillingSubscription**

* Fields: `id`, `tenant_id`, `plan_id`, `status`, `current_period_start`, `current_period_end`, `next_invoice_date`, `pricing_model`.

**OperationLog**

* Fields: `id`, `tenant_id`, `type`, `status`, `payload`, `logs_url`, `started_at`, `finished_at`, `trigger_source` (UI/n8n/AI).

---

### 5.2 APIs (examples)

* `GET /api/tenants`

  * Query: `q`, `status`, `plan`, `limit`, `offset`
  * Returns: `{ items: Tenant[], total: number }`
  * Used by: `tenants_table`, `kpi_tenant_counts`.

* `GET /api/tenants/{id}`

  * Returns: Tenant + related objects (SSOConfig, AnalyticsConfig, BillingSubscription summary).
  * Used by: `tenant_detail` panels.

* `POST /api/tenants`

  * Body: tenant create payload (identity, plan, infra template, bundle, SSO template).
  * Behavior:

    * Writes Tenant + infra specs.
    * Enqueues n8n workflow / GitOps job.
    * Returns `tenant_id` + initial operation id.

* `POST /api/tenants/{id}/operations`

  * Body: `{ type: "pause" | "resume" | "rebuild" | "module_apply" | "upgrade_image", params }`.
  * Used by: action buttons in `tenant_detail`.

* `GET /api/catalog/modules`

  * Returns: list of CE/OCA/ipai_ modules with metadata.

* `GET /api/catalog/bundles`

  * Returns: ModuleBundle list.

* `POST /api/catalog/bundles`

  * Creates/updates ipai_* bundle definition.

* `GET /api/integrations/keycloak/templates`

  * Returns sample realm/client configs for wizard.

* `GET /api/platform/kpi/tenants`

  * Returns aggregated counts and metrics for dashboard.

(Additional endpoints for analytics and billing follow the same pattern.)

---

## 6. Permissions / Roles Matrix

| role              | page_id            | view | create | edit    | delete | admin_actions                            |
| ----------------- | ------------------ | ---- | ------ | ------- | ------ | ---------------------------------------- |
| platform_owner    | platform_dashboard | yes  | n/a    | n/a     | n/a    | global operations toggle                 |
| platform_owner    | tenants_list       | yes  | yes    | yes     | yes    | create tenant, decommission              |
| platform_owner    | tenant_detail      | yes  | n/a    | yes     | yes    | pause/resume/rebuild/upgrade             |
| platform_owner    | module_catalog     | yes  | yes    | yes     | yes    | manage bundles                           |
| platform_owner    | infra_templates    | yes  | yes    | yes     | yes    | manage templates                         |
| platform_owner    | analytics_hub      | yes  | yes    | yes     | yes    | configure Supabase/Superset              |
| platform_owner    | billing_overview   | yes  | n/a    | yes     | n/a    | adjust plan, mark invoices               |
| platform_operator | platform_dashboard | yes  | n/a    | n/a     | n/a    | run ops, view logs                       |
| platform_operator | tenants_list       | yes  | no     | limited | no     | run ops, view details                    |
| platform_operator | tenant_detail      | yes  | n/a    | limited | no     | run ops but not billing changes          |
| tenant_admin      | tenant_portal      | yes  | n/a    | limited | n/a    | manage local settings, support requests  |
| finance_owner     | billing_overview   | yes  | n/a    | suggest | n/a    | propose changes; platform_owner approves |

---

## 7. Edge Cases & Constraints

* **Empty States**

  * No tenants yet → show call-to-action to create first tenant and link to docs.
  * No bundles → show explanation and recommended starting bundles (Finance PPM, CRM).

* **Loading States**

  * Use skeleton loaders for tables and cards; avoid blocking full-page spinners where possible.

* **Error Handling**

  * Surface operation failures with **logs URLs** and recommended runbook links.
  * If infra operation fails, mark tenant as `error` and encourage manual intervention.

* **Limits & Constraints**

  * Tenant count limited by cluster capacity; expose soft limit per environment.
  * Odoo version upgrades only allowed through specific, tested image tags.
  * DB access from AI agents is read-only and proxied through Codex/Edge Functions where applicable.

* **Performance**

  * Tenants list paginated (default 20 / page).
  * Logs retrieval capped by date range and count (e.g., last 7 days, max 500 events per view).
