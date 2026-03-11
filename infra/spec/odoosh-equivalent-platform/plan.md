# Odoo.sh-Equivalent Platform — Implementation Plan

Version: 1.1.0  
Status: Active  
Last Updated: 2026-03-12

## Phase 1: Foundation Contracts
1. Finalize this spec bundle (constitution/prd/plan/tasks).
2. Publish DB naming and schema contract into SSOT.
3. Enforce runtime/control-plane DB separation in docs and deployment scripts.

## Phase 2: Azure Runtime Completion
1. Ensure Odoo environment DBs exist (`odoo_dev`, `odoo_staging`, `odoo_prod`).
2. Align ACA env vars (`DB_NAME`) for stage/prod app sets when deployed.
3. Confirm Front Door routes and hostname mapping per environment.
4. Harden backup storage and retention policy (daily/weekly/monthly).

## Phase 3: Supabase Control Plane
1. Implement or validate required schemas: `ops`, `tenant`, `app`, `billing`, `portal`, `audit`, `integration`, `ai`, `cms`, `analytics`.
2. Implement core tables (`ops.environments`, `ops.deployments`, `ops.backups`, `ops.runtime_events`, etc.).
3. Apply tenant-aware RLS policies (`tenant_id` claim model).
4. Expose control-plane APIs/edge hooks for deploy lifecycle events.

## Phase 4: n8n Orchestration
1. Enable queue mode with Redis-backed workers.
2. Configure reverse-proxy-safe webhook URL settings.
3. Implement canonical workflows:
   - branch-open deploy
   - staging clone + neutralize
   - prod promotion + smoke + rollback trigger
   - backup verify + restore drill
   - notification/incident fanout

## Phase 5: Promotion and Evidence
1. Gate promotion with CI + backup + smoke + approval checks.
2. Persist all deployment/backup events in Supabase ops tables.
3. Store evidence artifacts in canonical evidence paths.
4. Add rollback validation notes per release wave.

## Phase 6: Tenant Isolation Expansion (Optional)
1. Introduce `odoo_tenant_<slug>_<env>` for isolated ERP tenants.
2. Keep Supabase shared multi-tenant with `tenant_id` + RLS.
3. Ensure n8n workflows include tenant context and audit scope.
