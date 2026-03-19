# Odoo.sh-Equivalent Platform — Tasks

Last Updated: 2026-03-12

## Spec and SSOT
- [x] Define runtime/control/orchestration plane doctrine.
- [x] Define env model (`prod`, `staging`, `dev`, optional `preview/*`).
- [x] Define DB naming contract for Odoo/Supabase/n8n.
- [x] Define Supabase schema-per-domain + RLS tenancy model.

## Azure Runtime Tasks
- [x] Ensure `odoo_staging` and `odoo_prod` exist on canonical Odoo PG server.
- [x] Add idempotent script to enforce Odoo stage/prod DB existence.
- [ ] Provision staging ACA app set (`ipai-odoo-staging-*`) and wire `DB_NAME=odoo_staging`.
- [ ] Provision prod ACA app set (`ipai-odoo-prod-*`) and wire `DB_NAME=odoo_prod`.
- [ ] Validate Front Door host routing for `erp`, `erp-staging`, `erp-dev`.

## Supabase Control-Plane Tasks
- [ ] Create/validate `tenant.tenants`, `tenant.workspaces`.
- [ ] Create/validate `app.apps`, `app.tenant_apps`.
- [ ] Create/validate `ops.environments`, `ops.deployments`, `ops.backups`, `ops.runtime_events`.
- [ ] Create/validate `billing.subscriptions` and `audit.event_log`.
- [ ] Apply tenant RLS policies based on JWT `tenant_id`.

## n8n Orchestration Tasks
- [ ] Enable queue mode and worker topology for production.
- [ ] Configure webhook URL/proxy settings for reverse proxy.
- [ ] Implement branch-open deploy workflow.
- [ ] Implement prod->staging clone + neutralization workflow.
- [ ] Implement prod promotion workflow with preflight/backup/smoke.
- [ ] Implement backup verification + restore drill workflows.

## Promotion and Reliability Tasks
- [ ] Enforce deploy gate sequence: CI -> backup -> deploy -> smoke -> record.
- [ ] Capture rollback procedure and validation evidence per release.
- [ ] Verify retention windows satisfy daily/weekly/monthly policy.

## Tenant Expansion Tasks (Optional)
- [ ] Add tenant-isolated Odoo DB naming rollout (`odoo_tenant_<slug>_<env>`).
- [ ] Add tenant-aware workflow input/audit context in n8n.
- [ ] Validate cross-tenant isolation tests in control-plane APIs.
