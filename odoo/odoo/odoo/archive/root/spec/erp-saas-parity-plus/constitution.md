# ERP SaaS Parity Plus Constitution

## 1. Core Principles

1. **Odoo/OCA is the ERP Engine**: Use Odoo Community Edition and curated OCA modules for all core transaction logic and basic UIs.
2. **Supabase is the Control Plane**: Supabase manages identity, integrations, metering, observational data, and acts as the secure API/webhook gateway.
3. **No Enterprise Replacements**: "Parity" means matching Odoo Enterprise or SaaS ERP value via composability (n8n, Supabase, Vercel), not by trying to copy proprietary modules verbatim.
4. **Agentic Ops Over Manual Labor**: Rather than building every missing UI screen, empower AI Agents (via GraphRAG and MCP) to assist with complex tasks (like period closes or issue triaging).
5. **Observability is Mandatory**: A system is not "SaaS grade" until deployments, errors, integration jobs, and dead letters are centrally visible and alerted upon (Slack).

## 2. Technical Constraints

- `ipai_*` modules exist _only_ as connectors or compat overlays. Business logic belongs in CE/OCA or external services.
- The `ops.*` Supabase schema is the exclusive integration backbone. Do not bypass it for webhooks or background jobs.
- Vercel apps map 1:1 with Next.js monorepo folders in `apps/*`.

## 3. The 7 Layers of Parity

1. **ERP Feature Parity**: Match transactions via CE+OCA.
2. **Identity & Tenant Model**: Supabase SSO + Tenant Isolation.
3. **Integration Bus**: webhook -> queue -> worker -> external.
4. **Observability**: Centralized logs, ops console, Slack alerts.
5. **Change Management**: CI/CD drift checks, stages, deterministic builds.
6. **Billing & Entitlements**: Stripe + Metering on Supabase.
7. **Agentic "Plus"**: GraphRAG, AI-assisted transactions, incident remediation.
