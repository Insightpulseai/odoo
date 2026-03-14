# Azure Self-Host Migration — Tasks

## Status Legend
- [ ] Not started
- [x] Done

## Phase 1: Inventory (DONE)
- [x] Provision Azure VM (4.193.100.31)
- [x] Deploy Docker Compose (14 Supabase services + n8n)
- [x] All secrets in Azure Key Vault (28 secrets)
- [x] NSG locked (SSH + HTTP/HTTPS only)
- [x] n8n runtime-up and externally reachable

## Phase 2: Schema Migration
- [ ] Run schema export (dry-run): `gh workflow run supabase-self-host-migration.yml -f phase=schema -f mode=dry-run`
- [ ] Review schema diff output
- [ ] Verify all extensions installed (pgvector, pgjwt, pg_graphql, pg_cron)
- [ ] Run schema export (execute)
- [ ] Verify SCHEMA_PARITY: PASS

## Phase 3: Data Migration (ETL)
- [ ] Run data migration (dry-run): `gh workflow run supabase-self-host-migration.yml -f phase=data -f mode=dry-run`
- [ ] Review row count parity report
- [ ] Run data migration (execute)
- [ ] Verify DATA_PARITY: PASS (within 1% tolerance)
- [ ] Run seed scripts in order (001, 003, 9000-series)
- [ ] Skip deprecated 002_finance_seed.sql
- [ ] Verify sequences reset correctly

## Phase 4a: Edge Functions
- [ ] Run functions deploy (dry-run): `gh workflow run supabase-self-host-migration.yml -f phase=functions -f mode=dry-run`
- [ ] Review manifest (39 functions)
- [ ] Run functions deploy (execute)
- [ ] Smoke test all critical-tier functions
- [ ] Smoke test all standard-tier functions
- [ ] Document unhealthy/failing functions

## Phase 4b: n8n Workflow Migration
- [ ] Create scripts/n8n/import_workflows.sh
- [ ] Create scripts/n8n/export_credentials.sh
- [ ] Backup n8n credentials from current instance
- [ ] Run URL rewire (cloud → self-hosted) on all 47 workflow JSONs
- [ ] Import workflows via n8n API
- [ ] Verify credential references resolve
- [ ] Activate core workflows (health-check, finance, BIR)
- [ ] Smoke test health-check workflow
- [ ] Smoke test finance-close-orchestrator workflow

## Phase 5: Consumer Cutover
- [ ] Run cutover (dry-run): `gh workflow run supabase-self-host-migration.yml -f phase=cutover -f mode=dry-run`
- [ ] Review consumer rewire plan
- [ ] Rewire Edge Functions (.env on VM)
- [ ] Rewire n8n (.env on VM)
- [ ] Rewire Odoo ACA (az containerapp env set)
- [ ] Rewire GitHub Actions secrets (gh secret set)
- [ ] Update DNS records (Cloudflare → Front Door)
- [ ] Run CUTOVER_VERIFY: PASS
- [ ] Run end-to-end smoke tests (Supabase, Edge Functions, n8n, Odoo)

## Phase 6: Parallel Run + Decommission
- [ ] Run cloud and self-hosted in parallel for 7 days
- [ ] Monitor for incidents
- [ ] Decommission managed Supabase project spdtwktxdalcfigzeqrz
- [ ] Remove cloud-specific references from codebase
- [ ] Update SSOT files (service-matrix.yaml, supabase.yaml)
