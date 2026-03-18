# Odoo EE → CE/OCA SaaS Platform – Constitution

## 1. Project Summary

* Build a **self-hosted, Odoo 18 CE + OCA–based SaaS** that delivers **Odoo Enterprise–level features** without EE code or licenses.
* Provide a **multi-tenant control plane** to spin up, configure, and monitor Odoo CE/OCA workspaces for agencies and internal business units.
* Enforce **Config → OCA → Delta custom** philosophy with strict OCA compliance and clean separation of ipai_* custom modules.
* Integrate the full InsightPulseAI stack: **DigitalOcean (Droplets/DOKS), Postgres, Supabase, n8n, Keycloak, Mattermost, Superset, Pulser/Codex/Claude agents** for automation and AI assistance.
* Target TBWA\SMP and related entities initially, but keep the architecture SaaS-ready for external clients.

## 2. Constraints & Guardrails

* **Odoo License Compliance**

  * No Enterprise modules, no EE code in repo; use **Odoo 18 CE** + vetted **OCA** modules only.
  * All custom code lives under **ipai_*** (and optional tbwa_*) addons; clearly marked as "Delta" layer.
* **Architecture & Tech Stack**

  * Hosting: **DigitalOcean** (Droplets and/or DOKS Kubernetes).
  * Core App DB: **PostgreSQL** (Odoo primary DB per tenant).
  * Analytics / Data Platform: **Supabase Postgres** as central data warehouse (read-only from Odoo).
  * Workflow Automation: **n8n** (self-hosted) for cron-style jobs, cross-system orchestrations, and webhooks.
  * Identity & SSO: **Keycloak** as IdP (SAML/OIDC) for tenants and internal users.
  * Messaging / Collaboration: **Mattermost** for notifications, AI assistants, and operational channels.
  * BI & Dashboards: **Superset / similar BI** on top of Supabase.
  * AI & Agents: **Pulser**, **Codex CLI**, **Claude Code CLI**, self-hosted Claude endpoint for codegen/ops; AI agents run **outside** Odoo runtime.
  * CI/CD: **GitHub Actions** is the canonical pipeline for images, migrations, and tests.
* **Security & Isolation**

  * Strict **tenant isolation** at DB level (schema or database per tenant) + network rules.
  * Access to production DBs via **Codex/agents only through approved paths**, never via raw model prompts.
* **Non-goals (for v1)**

  * No marketplace for third-party apps; only curated ipai_*/OCA catalog.
  * No generic public "self-signup + credit card" SaaS at launch; tenants are provisioned manually or via internal checklist.
  * No attempts to fully reimplement Odoo Online billing; use simpler subscription and billing models.

## 3. Success Criteria

* **Functional**

  * Can create a new tenant workspace (Odoo CE/OCA instance) via the control plane in **≤ 15 minutes** end-to-end (including DNS + SSL + Keycloak).
  * At least **3 canonical "EE parity" bundles** (Finance PPM, HR/Timesheets, CRM/Sales) are available as one-click module presets.
  * Each tenant has working SSO via Keycloak and can access their isolated Odoo workspace and Superset dashboards.
* **Operational**

  * All changes flow through **GitHub PRs** with green CI (OCA compliance, tests, lint) before deployment.
  * Standard **n8n workflows** exist for nightly backups, health checks, and log aggregation.
* **Data & Analytics**

  * Supabase receives **near-real-time replicated data** from at least one production tenant and powers at least one TBWA-grade dashboard (Scout, Finance PPM, etc.).
* **AI & Automation**

  * At least **one agent flow** (e.g., "Odoo module audit", "Finance PPM health check") runs end-to-end via Pulser/Codex against this platform.
