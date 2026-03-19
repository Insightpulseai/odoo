# Azure Self-Host Migration -- Tasks

## Status Legend

- [ ] Not started
- [x] Done

---

## WS1 -- Schema Parity

- [ ] Export cloud schema via `supabase_schema_export.sh`
- [ ] Export target schema for comparison
- [ ] Diff schemas: identify missing tables, columns, indexes, constraints
- [ ] Bootstrap missing extensions on target (pgvector, pgjwt, pg_graphql, pg_cron, pg_stat_statements)
- [ ] Bootstrap missing roles on target (anon, authenticated, authenticator, service_role, etc.)
- [ ] Bootstrap missing schemas on target (public, auth, storage, realtime, _supabase, ops, mcp_jobs, scout)
- [ ] Apply canonical migrations from `supabase/migrations/`
- [ ] Re-run schema diff -- confirm 0 missing tables, 0 missing columns
- [ ] Verify PostgREST health on target
- [ ] Verify Auth (GoTrue) health on target
- [ ] Verify Storage service health on target
- [ ] Verify Edge Functions runtime health on target
- [ ] Save evidence to `docs/evidence/*/schema_parity/`

**Gate**: `SCHEMA_PARITY: PASS`

---

## WS2 -- Table Data Migration

- [ ] Tier tables by FK dependency order (Tier 1: lookup, Tier 2: master, Tier 3: transactional)
- [ ] Export Tier 1 tables (lookup/reference) via `pg_dump --data-only`
- [ ] Import Tier 1 tables to target
- [ ] Validate Tier 1 row counts (source vs target)
- [ ] Export Tier 2 tables (master/domain)
- [ ] Import Tier 2 tables to target
- [ ] Validate Tier 2 row counts
- [ ] Export Tier 3 tables (transactional)
- [ ] Import Tier 3 tables to target
- [ ] Validate Tier 3 row counts
- [ ] Reset all sequences via `setval()` to `max(id) + 1`
- [ ] Run keyed checksum on top-10 tables by row count
- [ ] Verify constraint satisfaction (FK, unique, not-null) on target
- [ ] Save evidence to `docs/evidence/*/table_migration/`

**Gate**: Row-count parity within 1%; checksum match on critical tables

---

## WS3 -- Seed Canonicalization

- [ ] Consume seed inventory from `docs/architecture/SEED_DATA_INVENTORY.md`
- [ ] Load canonical map from `ssot/migration/seed_canonical_map.yaml`
- [ ] Resolve duplicate group 1: identify canonical source, exclude deprecated
- [ ] Resolve duplicate group 2: identify canonical source, exclude deprecated
- [ ] Resolve duplicate group 3: identify canonical source, exclude deprecated
- [ ] Resolve duplicate group 4: identify canonical source, exclude deprecated
- [ ] Resolve duplicate group 5: identify canonical source, exclude deprecated
- [ ] Resolve duplicate group 6: identify canonical source, exclude deprecated
- [ ] Replay canonical seeds only to target via `replay_canonical_seeds.py`
- [ ] Validate: zero duplicate business records per business key
- [ ] Validate: mail server seed exactly one at sequence=1
- [ ] Verify canonical map fully consumed (no unresolved entries)
- [ ] Save evidence to `docs/evidence/*/seed_canonicalization/`

**Gate**: Zero duplicates; canonical map 100% consumed

---

## WS4 -- Edge Function Deployment

- [ ] Verify deploy manifest: `ops-platform/supabase/edge-functions/deploy/manifest.yaml` (39 functions)
- [ ] SCP function directories to VM `4.193.100.31`
- [ ] Map secrets/env aliases for each function (cloud names to Key Vault refs)
- [ ] Deploy function batch 1: auth functions
- [ ] Smoke test auth functions (HTTP 200)
- [ ] Deploy function batch 2: ops/webhook functions
- [ ] Smoke test ops/webhook functions (HTTP 200)
- [ ] Deploy function batch 3: gateway functions
- [ ] Smoke test gateway functions (HTTP 200)
- [ ] Deploy function batch 4: AI/semantic functions
- [ ] Smoke test AI/semantic functions (HTTP 200)
- [ ] Deploy function batch 5: sync functions
- [ ] Smoke test sync functions (HTTP 200)
- [ ] Deploy function batch 6: utility functions
- [ ] Smoke test utility functions (HTTP 200)
- [ ] Pre-warm critical functions
- [ ] 10-minute observation: zero function errors
- [ ] Save evidence to `docs/evidence/*/edge_functions/` (HTTP status + response time per function)

**Gate**: All 39 functions return HTTP 200; zero errors in 10-minute observation

---

## WS5 -- pg_cron Migration

- [ ] Export all `cron.job` entries from source database
- [ ] Document each job: schedule, command, dependencies
- [ ] Map job commands to target schema/function references
- [ ] Create all `cron.job` entries on target with `active = false`
- [ ] Validate schedule count: source vs target (exact match)
- [ ] Verify no jobs are running on target
- [ ] Identify job enablement order based on dependencies
- [ ] Enable jobs in controlled order (post-cutover only)
- [ ] Verify each job executes successfully on first scheduled run
- [ ] Save evidence to `docs/evidence/*/pg_cron/`

**Gate**: Scheduler count match; all imported disabled; enablement order documented

---

## WS6 -- n8n Workflow Migration

### Import Phase

- [ ] Export workflow JSON inventory from source n8n (API + repo)
- [ ] Identify all credential references in exported workflows
- [ ] Map credentials to Azure Key Vault-backed aliases
- [ ] Rewrite webhook base URLs (cloud to self-hosted) in all workflow JSON
- [ ] Import all 47 workflows via n8n API with `active: false`
- [ ] Validate import: count matches (47), names match, all `active: false`
- [ ] Save import evidence to `docs/evidence/*/n8n_import/`

### Enablement Phase (post-cutover only)

- [ ] Smoke test Wave 1 workflows: health/control plane
- [ ] Enable Wave 1 workflows
- [ ] Monitor Wave 1 for 1 hour -- zero errors
- [ ] Smoke test Wave 2 workflows: read-only/observability
- [ ] Enable Wave 2 workflows
- [ ] Monitor Wave 2 for 1 hour -- zero errors
- [ ] Smoke test Wave 3 workflows: business automation (sync, project)
- [ ] Enable Wave 3 workflows
- [ ] Monitor Wave 3 for 1 hour -- error rate <5%
- [ ] Smoke test Wave 4 workflows: finance/BIR
- [ ] Enable Wave 4 workflows
- [ ] Monitor Wave 4 for 2 hours -- zero errors, BIR data integrity verified
- [ ] Smoke test Wave 5 workflows: write-path/deployment
- [ ] Enable Wave 5 workflows
- [ ] Monitor Wave 5 for 4 hours -- all operational, error rate <2%

**Gate (import)**: 47 workflows imported, all disabled
**Gate (enablement)**: All 5 waves enabled and stable per thresholds

---

## WS7 -- Consumer Cutover

- [ ] Review `ops-platform/supabase/cutover/consumers.yaml` -- confirm 8 consumers, priority order
- [ ] Prepare write-freeze procedure for managed Supabase
- [ ] Execute write-freeze on cloud Supabase
- [ ] Run final delta ETL (capture changes since Phase 3)
- [ ] Apply delta to self-hosted target
- [ ] Validate delta row counts
- [ ] Switch consumer 1 (highest priority per consumers.yaml)
- [ ] Health check consumer 1 -- PASS
- [ ] Switch consumer 2
- [ ] Health check consumer 2 -- PASS
- [ ] Switch consumer 3
- [ ] Health check consumer 3 -- PASS
- [ ] Switch consumer 4
- [ ] Health check consumer 4 -- PASS
- [ ] Switch consumer 5
- [ ] Health check consumer 5 -- PASS
- [ ] Switch consumer 6
- [ ] Health check consumer 6 -- PASS
- [ ] Switch consumer 7
- [ ] Health check consumer 7 -- PASS
- [ ] Switch consumer 8 (lowest priority per consumers.yaml)
- [ ] Health check consumer 8 -- PASS
- [ ] Run `CUTOVER_VERIFY` script -- all gates pass
- [ ] Save cutover evidence to `docs/evidence/*/cutover/`

**Gate**: All 8 consumers switched and healthy; `CUTOVER_VERIFY: PASS`

---

## Final Verification Checklist

- [ ] Schema parity confirmed (WS1 gate passed)
- [ ] Table data migrated and validated (WS2 gate passed)
- [ ] Seeds canonicalized and deduplicated (WS3 gate passed)
- [ ] All 39 edge functions deployed and healthy (WS4 gate passed)
- [ ] All pg_cron jobs migrated (WS5 gate passed)
- [ ] All 47 n8n workflows imported disabled (WS6 import gate passed)
- [ ] All 8 consumers switched to self-hosted (WS7 gate passed)
- [ ] All n8n workflow waves enabled and stable (WS6 enablement gate passed)
- [ ] pg_cron jobs enabled and verified (WS5 post-cutover)
- [ ] 24h observation window completed with zero critical incidents
- [ ] Databricks reconciliation confirms zero drift
- [ ] 7-day soak period started
- [ ] Cloud Supabase traffic at zero for 24h+
- [ ] 7-day soak completed with zero incidents
- [ ] Cloud Supabase project decommissioned

**Final gate**: Migration complete; all evidence committed to `docs/evidence/`
