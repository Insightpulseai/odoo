# Odoo.sh-Equivalent Platform — Constitution

Version: 1.1.0  
Status: Active  
Last Updated: 2026-03-12

## Purpose
Define non-negotiable operating rules for an Odoo.sh-equivalent model on Azure + self-hosted Supabase + self-hosted n8n.

## Core Doctrine
- Azure hosts Odoo runtime plane: app runtime, ingress, Odoo PostgreSQL, Redis, secrets, monitoring, backups.
- Self-hosted Supabase hosts control plane: SSOT metadata, APIs, auth, storage, realtime, edge functions.
- Self-hosted n8n hosts orchestration plane: deploy/clone/neutralize/backup-verify/alerts.
- Git + CI/CD replace Odoo.sh UI workflows for branch/build/promotion.

## Non-Negotiables
1. Reproduce Odoo.sh behavior, not Odoo.sh infrastructure.
2. Runtime and control-plane databases are separated.
3. Odoo transactional runtime never depends on Supabase database lifecycle.
4. Staging must be production-clone + neutralization before testing.
5. Production deploys are backup-first and rollback-capable.
6. Control-plane truth must live in repo + Supabase ops tables; n8n is executor, not SSOT.
7. No secrets in git-tracked config; secret references only.
8. All operations must be CLI/API executable; UI is convenience only.

## Environment Tiers
- `prod`: protected, promotion-only, strongest controls.
- `staging`: restored from prod clone, side effects neutralized.
- `dev`: fresh/shared development data for build/test loops.
- `preview/<branch>`: optional ephemeral branch environments.

## Database Contract
- Odoo runtime DB names (required): `odoo_prod`, `odoo_staging`, `odoo_dev`.
- Tenant-isolated Odoo pattern (optional): `odoo_tenant_<slug>_<env>`.
- Supabase control-plane DB names: `platform_prod`, `platform_staging`, `platform_dev`.
- n8n metadata DB names: `n8n_prod`, `n8n_staging`, `n8n_dev`.

## Supabase Multi-Tenant Contract
- Shared database, shared schemas, `tenant_id` + RLS enforcement.
- Schema-per-domain, not schema-per-tenant.
- Required domain schemas: `ops`, `tenant`, `app`, `billing`, `portal`, `audit`, `integration`, `ai`, `cms`, `analytics`.

## Governance
- Changes to plane boundaries, DB separation, or tier behaviors require constitution amendment.
- Spec artifacts in this bundle are authoritative for Odoo.sh-equivalent operating model.
