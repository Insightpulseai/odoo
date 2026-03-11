# Odoo.sh-Equivalent Platform — PRD

Version: 1.1.0  
Status: Active  
Last Updated: 2026-03-12

## 1. Product Goal
Implement an Odoo.sh-equivalent operating model using Azure runtime services, Supabase control-plane services, and n8n orchestration workflows.

## 2. Scope
### In scope
- Branch-to-environment lifecycle across `dev`, `staging`, `prod`, optional `preview/*`
- Build/test/deploy automation
- Staging clone + neutralization workflow
- Production backup-first promotion with rollback path
- Control-plane SSOT tables and APIs in Supabase
- n8n queue-mode orchestration

### Out of scope
- Recreating Odoo.sh UI/UX
- Using Supabase as primary Odoo runtime database
- n8n as source-of-truth datastore

## 3. Target Architecture
### Plane A: Azure runtime
- Azure Container Apps (or AKS where explicitly justified)
- Azure Database for PostgreSQL (Odoo DBs)
- Azure Cache for Redis
- Azure Front Door
- Azure Key Vault
- Azure Monitor / Log Analytics / App Insights
- Azure Blob Storage (filestore snapshots, dumps, evidence)

### Plane B: Supabase control plane (self-hosted)
- Auth, Storage, Realtime, Edge Functions
- Control-plane schemas and APIs
- Ops/admin metadata and deployment state

### Plane C: n8n automation plane (self-hosted)
- Queue mode workers
- Webhook processors (as needed)
- Deployment + backup + neutralization + notification workflows

## 4. Odoo.sh Behavior Parity Requirements
### Development parity
- Branch push triggers build, addon validation, tests, env registration.
- Dev DB supports fresh/demo/test behavior.

### Staging parity
- Staging DB restored from latest verified production backup.
- Mandatory neutralization before QA:
  - disable cron
  - block outbound mail
  - disable payment/shipping side effects
  - disable external automations
  - rewrite environment URL/secrets

### Production parity
- Protected promotion path only.
- Pre-deploy backup and filestore snapshot required.
- Post-deploy smoke tests required.
- Rollback path must remain available until verification passes.

## 5. Database and Schema Strategy
### Odoo DB naming
- Shared env model: `odoo_prod`, `odoo_staging`, `odoo_dev`
- Tenant env model: `odoo_tenant_<slug>_<env>`

### Supabase DB naming
- `platform_prod`, `platform_staging`, `platform_dev`

### n8n DB naming
- `n8n_prod`, `n8n_staging`, `n8n_dev`

### Supabase schema model
- Domain schemas: `ops`, `tenant`, `app`, `billing`, `portal`, `audit`, `integration`, `ai`, `cms`, `analytics`
- Shared-table tenancy with `tenant_id` + RLS

## 6. Control-Plane Data Contract
Minimum required tables:
- `tenant.tenants`, `tenant.workspaces`
- `app.apps`, `app.tenant_apps`
- `ops.environments`, `ops.deployments`, `ops.backups`, `ops.runtime_events`
- `billing.subscriptions`
- `audit.event_log`

Required identifiers:
- `tenant_id`, `app_id`, `environment_id`, `workspace_id` (optional), `actor_id`, `source_system`

## 7. Workflow Contract (n8n)
- Branch opened -> register env -> deploy
- Promote to staging -> restore prod backup -> neutralize -> deploy -> smoke
- Promote to prod -> preflight -> backup -> deploy -> smoke -> record
- Nightly backup verification + restore drills
- Alert routing and incident logging

## 8. Success Criteria
- Dev/staging/prod lifecycle behaves as Odoo.sh-equivalent model.
- Staging always comes from production clone + neutralization.
- Production deploys are backup-first with deterministic rollback.
- Supabase is SSOT for control-plane metadata.
- n8n executes orchestration without becoming SSOT.
