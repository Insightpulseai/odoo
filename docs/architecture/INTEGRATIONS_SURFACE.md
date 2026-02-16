# Integration Surfaces (SSOT)

> Where each integration lives, what is authored vs generated, and how secrets are handled.

## Summary Table

| Integration | Purpose | SSOT Paths | Secrets Live In | Envs |
|---|---|---|---|---|
| Supabase | Control plane, ops schema, Edge Functions | `supabase/` | Supabase Vault / Edge secrets | dev/staging/prod |
| Vercel | Web apps (ops-console, marketing, docs) | `web/`, `infra/vercel/` | Vercel env vars (never git) | preview(staging)/prod |
| DigitalOcean | Odoo runtime, managed PG, containers | `infra/digitalocean/`, `infra/deploy/` | DO env vars / secret manager | dev/staging/prod |
| GitHub | CI/CD, policy gates, automation | `.github/` | GitHub Actions secrets (CI only) | per-environment |
| Superset | BI / dashboards / analyst surface | `infra/superset/`, `docs/architecture/SUPERSET.md` | DO env vars / secret manager (never git) | dev/staging/prod |
| n8n | Workflow automation, event routing | `automations/n8n/` | n8n runtime (not git) | dev/staging/prod |
| MCP | Agent tool routing, server manifests | `agents/mcp/` | Supabase Edge secrets / env vars | dev/staging/prod |
| Figma | Design tokens, asset pipeline | `design/figma/`, `design/tokens/` | Figma API token (CI secret) | n/a |
| Slack | Notifications, ChatOps | via `automations/` or `supabase/functions/` | Supabase Edge secrets | per-workspace |

---

## Supabase

- **SSOT**: `supabase/` (canonical Supabase CLI layout)
  - `migrations/` — SQL migrations (authored, versioned)
  - `functions/` — Edge Functions (authored)
  - `seed/` — Seed data scripts (authored)
- **Generated**: type definitions, schema cache
- **Secrets**: Supabase Vault + Edge Function secrets; never committed
- **Policy**: Supabase secrets are authoritative for Supabase code only; do not mirror into GitHub/Vercel

---

## Vercel

- **SSOT**: `web/<app>/` for source, `infra/vercel/` for config contracts
- **Generated**: `.vercel/` build artifacts (gitignored)
- **Secrets**: Vercel env vars per environment (Preview = staging, Production = prod)
- **Policy**:
  - Templates allowed for bootstrapping `web/*` apps only
  - No template-driven repo creation for `odoo/` runtime
  - Vercel should not hold `service_role` unless explicitly justified
  - Prefer Edge Function brokering for third-party API keys

---

## DigitalOcean

- **SSOT**: `infra/digitalocean/` (IaC scripts), `infra/deploy/` (production compose)
- **Generated**: Terraform state (gitignored via `**/.terraform/`, `**/terraform.tfstate*`)
- **Secrets**: DO env vars, container env, or secrets manager
- **Policy**: runtime deploys are triggered via CI/runners, not local CLI

---

## Superset (BI)

- **SSOT**: `infra/superset/` (config/provisioning templates), `docs/architecture/SUPERSET.md` (contract)
- **Generated**: exported dashboards (optional) under `infra/superset/provisioning/dashboards/`
- **Secrets**: never committed; stored as runtime env vars (DO, container env, or secrets manager)
- **Policy**: use dedicated read-only DB role; prefer analytics views over raw ERP tables

---

## n8n

- **SSOT**: `automations/n8n/workflows/` (exported workflow JSON, versioned)
- **Generated**: n8n runtime state (never committed)
- **Secrets**: n8n runtime credentials (not git); optionally brokered via Supabase Vault
- **Policy**: treat n8n as runtime tool; workflow JSON as SSOT in git

---

## MCP (Model Context Protocol)

- **SSOT**: `agents/mcp/` (server definitions, manifests, tool routing)
- **Generated**: runtime state, logs
- **Secrets**: Supabase Edge secrets for MCP gateway; env vars for server runtimes
- **Policy**: MCP servers are code; runbooks describe "how to run" in CI/runner environments

---

## Figma (Design System)

- **SSOT**: `design/figma/` (scripts, Figma Connect config), `design/tokens/` (tokens.json)
- **Generated**: `design/tokens/variables.local.json` (from Figma API export)
- **Secrets**: Figma API token (GitHub Actions secret only)
- **Policy**: tokens are SSOT; codegen converts tokens to Tailwind/CSS vars/Odoo theme vars

---

## Slack

- **SSOT**: no dedicated directory; Slack is an integration handled by:
  - `supabase/functions/` — webhook handlers
  - `automations/` — notification templates/routing rules
- **Secrets**: Slack webhook/signing secrets stored in Supabase Edge secrets
- **Policy**: Slack is a notification channel, not a platform folder

---

## GitHub

- **SSOT**: `.github/` (workflows, templates, policies, CODEOWNERS)
- **Generated**: n/a
- **Secrets**: GitHub Actions secrets (CI only); never used as application runtime secrets
- **Policy**: GitHub secrets are for CI/CD deployment plumbing, not a master vault

---

## Non-Negotiable Rules

1. **No secrets in git** — use `.env.example` patterns; real values in platform-native secret stores
2. **Each platform owns its secrets** — Supabase Vault for Supabase, Vercel env for Vercel, GitHub secrets for CI
3. **No cross-pollination** — do not mirror secrets across platforms unless explicitly required
4. **Env-scoped** — separate secret sets per environment (dev/staging/prod) in every platform
5. **`service_role` in Vercel is a footgun** — prefer Edge Function brokering
