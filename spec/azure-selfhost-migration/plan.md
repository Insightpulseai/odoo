# Azure Self-Host Migration -- Execution Plan

> 5-phase plan matching `.github/workflows/supabase-self-host-migration.yml`.
> Constitution rules (R1--R6) apply to every phase.

---

## Phase 1 -- Inventory (Complete)

**Status**: Done

Completed via `scripts/migration/export_supabase_inventory.py` (`supabase_cloud_inventory.py`). Produced:

- Full table inventory with row counts
- Edge function manifest (88 in repo, 39 in deploy manifest)
- pg_cron job inventory
- n8n workflow inventory (~47 workflows)
- Seed data inventory with 6 duplicate groups identified
- Consumer manifest (8 consumers)

**Evidence**: `docs/evidence/*/inventory/`

---

## Phase 2 -- Schema

**Goal**: Target database schema matches source exactly.

### Steps

1. Export cloud schema (extensions, roles, schemas, DDL) via `supabase_schema_export.sh`
2. Bootstrap target extensions: pgvector, pgjwt, pg_graphql, pg_cron, pg_stat_statements
3. Bootstrap target roles: anon, authenticated, authenticator, service_role, supabase_admin, supabase_auth_admin, supabase_storage_admin, supabase_functions_admin, supabase_realtime_admin, supabase_replication_admin, supabase_read_only_user, dashboard_user, n8n
4. Bootstrap target schemas: public, auth, storage, realtime, _supabase, ops, mcp_jobs, scout
5. Apply canonical migrations from `supabase/migrations/`
6. Run schema diff: source vs target
7. Apply diffs until parity achieved
8. Verify PostgREST, Auth (GoTrue), Storage, Edge Functions service health on target

**Scripts**:
- `scripts/migration/export_supabase_inventory.py` (inventory)
- `platform/supabase/scripts/supabase_schema_export.sh` (schema diff)

**Gate**: `SCHEMA_PARITY: PASS` -- 0 missing tables, 0 missing columns, 0 missing extensions

---

## Phase 3 -- Data

**Goal**: All canonical data present on target with verified integrity.

Split into 4 parallel lanes:

### Lane A -- Table Data Copy

1. Tier tables by dependency order:
   - Tier 1: Lookup/reference tables (no FK dependencies)
   - Tier 2: Master/domain tables (res_partner, res_users, etc.)
   - Tier 3: Transactional tables (account_move, project_task, etc.)
2. Export via `pg_dump --data-only` per tier
3. Import to target preserving PK/FK insertion order
4. Reset all sequences via `setval()` to max(id) + 1
5. Validate row counts per table (source vs target, 1% tolerance)
6. Run keyed checksum on critical tables (top-10 by row count)

**Script**: `scripts/migration/migrate_tables.py`
**Gate**: Row-count parity within 1%; checksum match on critical tables

### Lane B -- Seed Canonicalization and Replay

1. Consume seed inventory from `docs/architecture/SEED_DATA_INVENTORY.md`
2. Load canonical map from `ssot/migration/seed_canonical_map.yaml`
3. For each of the 6 duplicate groups:
   - Select canonical source per map
   - Exclude deprecated/mirror sources
   - Validate canonical source data integrity
4. Replay only canonical seeds to target
5. Post-load validation: zero duplicate business records per business key
6. Verify mail server seed: exactly one at sequence=1

**Script**: `scripts/migration/replay_canonical_seeds.py`
**Gate**: Zero duplicate records per business key; canonical map fully consumed

### Lane C -- pg_cron Export and Recreate

1. Export all `cron.job` entries from source
2. Map job commands to target schema/function references
3. Create all `cron.job` entries on target with `active = false`
4. Validate schedule count: source vs target (exact match)
5. Verify no jobs are running on target until explicitly enabled

**Script**: `scripts/migration/migrate_pg_cron.py`
**Gate**: Scheduler count match; all imported disabled

### Lane D -- Storage Bucket Sync

1. List all storage buckets on source via Supabase Storage API
2. Create matching buckets on target with same policies
3. Sync all objects (files) from source to target buckets
4. Verify object counts per bucket
5. Verify auth bootstrap data via GoTrue admin API (not raw table copy)

**Script**: `scripts/migration/migrate_storage.py`
**Gate**: Bucket count match; object count match per bucket

---

## Phase 4 -- Functions

**Goal**: All 39 edge functions deployed and healthy on self-hosted Deno runtime.

### Steps

1. SCP 39 edge function directories to VM from repo
2. Deploy each function via Supabase CLI on the VM
3. Map secrets/env aliases for each function (cloud names to Key Vault names)
4. Smoke test critical-tier functions first:
   - Auth functions
   - Ops/webhook functions
   - Gateway functions
5. Smoke test standard-tier functions:
   - AI/semantic functions
   - Sync functions
   - Utility functions
6. Record HTTP status + response time for each function
7. Pre-warm critical functions to avoid cold-start issues

**Scripts**:
- `scripts/migration/migrate_edge_functions.py`
- Individual function smoke test via `curl`

**Gate**: All 39 functions return HTTP 200 on smoke test; no function errors in 10-minute observation

---

## Phase 5 -- Cutover

**Goal**: All consumers pointing to self-hosted, cloud quiesced, rollback ready.

### Steps

1. **Freeze**: Quiesce writes on managed Supabase (disable write endpoints, set read-only)
2. **Delta**: Capture final delta since Phase 3 data migration (changes during function deployment)
3. **Replay**: Apply delta to self-hosted target; verify row counts post-replay
4. **Consumer rewire**: Switch endpoints/secrets for all 8 consumers in priority order (from `consumers.yaml`):
   - Each consumer rewired individually
   - Health check after each consumer switch
   - Rollback individual consumer if health check fails
5. **Enable schedulers**: Enable pg_cron jobs in controlled order per dependency
6. **Validate**: Run `CUTOVER_VERIFY` script -- all gates must pass
7. **Monitor**: 24h observation window with alerting
8. **Decommission**: Only after 7-day soak with zero incidents

**Scripts**:
- `scripts/migration/validate_cutover.py`
- `platform/supabase/scripts/supabase_consumer_rewire.py`
- `platform/supabase/scripts/supabase_cutover_verify.sh`

**Gate**: `CUTOVER_VERIFY: PASS` + 7-day soak with zero incidents

---

## Post-Cutover -- n8n Workflow Enablement

**Separate from migration.** Enablement begins only after Phase 5 cutover is verified.

### Wave 1 -- Health / Control Plane
- Enable health-check and control-plane workflows
- Monitor for 1 hour
- Gate: Zero errors in wave 1 workflows

### Wave 2 -- Read-Only / Observability
- Enable monitoring, logging, and read-only sync workflows
- Monitor for 1 hour
- Gate: Zero errors in wave 2 workflows

### Wave 3 -- Business Automation
- Enable sync, project management, and business process workflows
- Monitor for 1 hour
- Gate: Error rate <5% in wave 3 workflows

### Wave 4 -- Finance / BIR
- Enable finance, tax compliance, and BIR reporting workflows
- Monitor for 2 hours
- Gate: Zero errors in finance workflows; BIR data integrity verified

### Wave 5 -- Write-Path / Deployment
- Enable deployment, write-path, and mutation workflows
- Monitor for 4 hours
- Gate: All workflows operational; error rate <2%

---

## Rollback Procedure

At any point before decommission:

1. Revert consumer endpoints to `spdtwktxdalcfigzeqrz.supabase.co`
2. Disable self-hosted n8n workflows (set all to `active: false`)
3. Disable self-hosted pg_cron jobs
4. Re-enable managed Supabase write endpoints
5. Notify all consumers of rollback

**Trigger thresholds** (any one triggers rollback evaluation):
- Any critical consumer health check fails post-cutover
- Data parity drift >1% on any monitored table
- >3 edge function failures in 1 hour
- n8n workflow error rate >10% in first 24h

---

## Reconciliation (Databricks)

Databricks serves as the reconciliation plane during the soak period:
- Daily row-count comparison: source vs target for all tables
- Drift detection alerts if any table diverges >1%
- Checksum validation on critical tables
- Databricks does NOT participate in data movement or consumer rewiring
