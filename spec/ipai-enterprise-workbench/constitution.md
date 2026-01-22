# Constitution — IPAI Enterprise Workbench

## 1. Purpose
Build and operate a self-hosted enterprise workbench for Odoo CE (18 now, 19-ready) delivering enterprise-class workflow parity using **CE + OCA + IPAI**, integrated with **Superset BI**, **Supabase + n8n + MCP** automation, and a token-driven **IPAI design system**.

## 2. Non-Negotiable Constraints
1) **No Odoo Enterprise modules**.  
2) **No IAP dependencies** (no odoo.com upsells, no paid IAP services).  
3) **OCA-first**: prefer upstream OCA modules; IPAI code only for glue/bridge or vertical workflows.  
4) **Deterministic artifacts**: generated docs/seeds must be versioned and drift-gated in CI.  
5) **CLI-first operations**: all setup, testing, and deployment must be fully automatable with scripts/CI.  
6) **Docs canonical URL**: `https://jgtolentino.github.io/odoo-ce/` is the authoritative docs base.

## 3. Core Principles
### 3.1 CE=EE Parity Strategy
- Replace EE-only functionality via:
  1) OCA modules
  2) OSS external services (Superset, Mattermost, OCR service, etc.)
  3) Minimal IPAI bridge glue (`ipai_enterprise_bridge`)
- Any feature parity claim must be backed by:
  - module mapping
  - config steps (scripted)
  - verification tests

### 3.2 Separation of Concerns
- **Odoo DB** remains authoritative for ERP transactions.
- **Superset** consumes analytics views or replicated warehouse schemas (read-only access).
- **Supabase** is the integration backbone: ops queue/event sourcing, automation state, realtime.
- **n8n** executes workflows; MCP exposes tools to agents.

### 3.3 Design System Single Source of Truth
- Maintain a single SSOT `tokens.json` for design tokens.
- Odoo OWL theme module(s) must consume tokens (thin adapter).
- Web surfaces (Workbench UI) must consume the same tokens (thin adapter).
- Branding overlays (Mattermost/TBWA) must be token-driven, not hard-coded.

## 4. Security Baseline
- Least privilege DB roles: read-only for Superset; constrained service roles for automation.
- Secrets never committed; env-only via CI/runner secret stores.
- All automation writes an auditable event trail (Supabase ops schema recommended).

## 5. Release Gates (CI Must Enforce)
- **No EE/IAP** gate: fail if enterprise dependencies/links are reintroduced.
- **Seed drift** gate: workbook → seed regen must yield zero diff.
- **Data-model drift** gate: DBML/ERD/ORM maps must match generator outputs.
- **Spec kit enforcement**: required 4 files exist for each spec bundle.
- **Repo structure**: canonical tree files are auto-generated and must match.

## 6. Definition of Done
A release is "Done" when:
- Odoo CE + OCA + IPAI modules install cleanly and pass validations.
- Finance PPM workflow matches canonical stage/state mapping and validates against workbook.
- Superset connects to analytics sources and dashboards render without errors.
- Supabase+n8n+MCP automation path functions end-to-end with audit trails.
- Docs are updated and published under GitHub Pages base URL.

