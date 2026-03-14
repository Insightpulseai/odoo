# Tasks: Supabase Cloud-to-Self-Hosted Migration

> Task list for phases 2-5. Phase 1 is complete.
> References: `constitution.md`, `prd.md`, `plan.md`

---

## Epic 1: Schema Migration (Phase 2)

### T-001: Export cloud schema inventory
- **Status**: [ ] pending
- **Script**: `scripts/supabase-migrate/02-schema-export.sh`
- **Action**: Run `supabase db dump` against cloud project `spdtwktxdalcfigzeqrz` for schemas `public`, `auth`, `storage`, `realtime`, `ops`, `extensions`
- **Output**: `docs/evidence/<ts>/supabase-migrate/cloud-schema.sql`
- **Depends on**: None
- **Gate**: File exists and contains CREATE TABLE statements

### T-002: Verify extension parity
- **Status**: [ ] pending
- **Script**: `scripts/supabase-migrate/02-verify-schema.sh` (extension check)
- **Action**: Query `pg_extension` on both cloud and self-hosted. Compare names and versions. Install any missing extensions on self-hosted.
- **Critical extensions**: `pgvector`, `pgjwt`, `pg_graphql`, `pg_cron`, `pg_net`, `pgsodium`, `supautils`, `uuid-ossp`
- **Output**: Extension diff in `schema-parity.json`
- **Depends on**: T-001
- **Gate**: All cloud extensions present on self-hosted

### T-003: Apply repo migrations to self-hosted
- **Status**: [ ] pending
- **Script**: `scripts/supabase-migrate/02-apply-migrations.sh`
- **Action**: Apply all ~150 migration files from `supabase/migrations/` in chronological order to self-hosted PostgreSQL
- **Output**: `docs/evidence/<ts>/supabase-migrate/migration-apply.log`
- **Depends on**: T-002
- **Gate**: All migrations applied without errors

### T-004: Generate schema parity report
- **Status**: [ ] pending
- **Script**: `scripts/supabase-migrate/02-verify-schema.sh`
- **Action**: Compare tables, columns, indexes, constraints, functions, and triggers between cloud and self-hosted
- **Output**: `docs/evidence/<ts>/supabase-migrate/schema-parity.json`
- **Depends on**: T-003
- **Gate**: All categories report MATCH

### T-005: Verify RLS policies
- **Status**: [ ] pending
- **Script**: `scripts/supabase-migrate/02-verify-schema.sh` (RLS section)
- **Action**: Compare `pg_policies` on both databases. Verify policy names, tables, commands, and expressions match.
- **Output**: RLS section in `schema-parity.json`
- **Depends on**: T-003
- **Gate**: All RLS policies match

### T-006: Phase 2 gate
- **Status**: [ ] pending
- **Script**: `scripts/supabase-migrate/02-gate.sh`
- **Action**: Validate `schema-parity.json` has all categories as MATCH. Emit `gate-result-phase2.json`.
- **Output**: `docs/evidence/<ts>/supabase-migrate/gate-result-phase2.json`
- **Depends on**: T-004, T-005
- **Gate**: `gate-result-phase2.json` shows PASS

---

## Epic 2: Data Migration (Phase 3)

### T-007: Export cloud data
- **Status**: [ ] pending
- **Script**: `scripts/supabase-migrate/03-data-export.sh`
- **Action**: Run `pg_dump --data-only` on cloud project. Exclude `realtime.*` and `analytics.*` schemas.
- **Output**: `docs/evidence/<ts>/supabase-migrate/cloud-data.dump`
- **Depends on**: T-006 (Phase 2 gate PASS)
- **Gate**: Dump file exists and is non-empty

### T-008: Import to self-hosted
- **Status**: [ ] pending
- **Script**: `scripts/supabase-migrate/03-data-import.sh`
- **Action**: Run `pg_restore --data-only --disable-triggers` to self-hosted PostgreSQL. Re-enable triggers after.
- **Output**: `docs/evidence/<ts>/supabase-migrate/data-import.log`
- **Depends on**: T-007
- **Gate**: pg_restore exits 0, no FATAL errors in log

### T-009: Row-count parity verification
- **Status**: [ ] pending
- **Script**: `scripts/supabase-migrate/03-verify-counts.sh`
- **Action**: Query per-table row counts on both databases. Compare and flag any drift.
- **Output**: `docs/evidence/<ts>/supabase-migrate/row-counts.json`
- **Depends on**: T-008
- **Gate**: All tables within tolerance (0 for critical, <0.1% for others)

### T-010: Critical table checksum verification
- **Status**: [ ] pending
- **Script**: `scripts/supabase-migrate/03-verify-critical.sh`
- **Action**: Deep verification of critical tables: `auth.users` (email uniqueness), `auth.identities` (FK integrity), `ops.task_queue` (status distribution), `ops.platform_events` (max ID), `storage.buckets` (exact match), `storage.objects` (bucket distribution)
- **Output**: `docs/evidence/<ts>/supabase-migrate/critical-tables.json`
- **Depends on**: T-009
- **Gate**: All critical tables show EXACT_MATCH

### T-011: Auth.users verification
- **Status**: [ ] pending
- **Script**: `scripts/supabase-migrate/03-verify-critical.sh` (auth section)
- **Action**: Verify `auth.users` row count, email uniqueness, `auth.identities` FK integrity, and password hash presence (not values).
- **Output**: Auth section in `critical-tables.json`
- **Depends on**: T-008
- **Gate**: User count matches, no orphaned identities

### T-012: Phase 3 gate
- **Status**: [ ] pending
- **Script**: `scripts/supabase-migrate/03-gate.sh`
- **Action**: Validate `row-counts.json` and `critical-tables.json`. Emit `gate-result-phase3.json`.
- **Output**: `docs/evidence/<ts>/supabase-migrate/gate-result-phase3.json`
- **Depends on**: T-009, T-010, T-011
- **Gate**: `gate-result-phase3.json` shows PASS

---

## Epic 3: Edge Functions (Phase 4)

### T-013: Generate function deploy manifest
- **Status**: [ ] pending
- **Script**: `scripts/supabase-migrate/04-generate-manifest.sh`
- **Action**: Scan `supabase/supabase/functions/` and generate `config/edge-function-manifest.txt` listing all 39 functions.
- **Output**: `config/edge-function-manifest.txt`
- **Depends on**: T-006 (Phase 2 gate PASS)
- **Gate**: Manifest contains exactly 39 entries

### T-014: Deploy functions to self-hosted
- **Status**: [ ] pending
- **Script**: `scripts/supabase-migrate/04-deploy-functions.sh`
- **Action**: Deploy all 39 functions from repo to self-hosted edge-runtime. Configure environment variables from Key Vault.
- **Output**: Deploy log per function
- **Depends on**: T-013
- **Gate**: All 39 functions deployed without errors

### T-015: Verify function endpoints
- **Status**: [ ] pending
- **Script**: `scripts/supabase-migrate/04-verify-functions.sh`
- **Action**: HTTP probe each function endpoint via Kong. Record status code.
- **Output**: `docs/evidence/<ts>/supabase-migrate/function-health.json`
- **Depends on**: T-014
- **Gate**: All 39 endpoints return non-5xx

### T-016: Test critical function paths
- **Status**: [ ] pending
- **Script**: `scripts/supabase-migrate/04-test-critical.sh`
- **Action**: End-to-end tests for auth flow (`auth-bootstrap`, `auth-otp-request`, `auth-otp-verify`), ops pipeline (`ops-health`, `ops-ingest`), Odoo integration (`odoo-webhook`), MCP gateway (`mcp-gateway`), semantic layer (`semantic-query`).
- **Output**: Critical path results in `function-health.json`
- **Depends on**: T-015
- **Gate**: All critical paths return expected responses

### T-017: Test function-to-DB connectivity
- **Status**: [ ] pending
- **Script**: `scripts/supabase-migrate/04-test-critical.sh` (DB connectivity section)
- **Action**: Invoke a function that queries PostgREST and returns data. Verify the function can read from and write to the database.
- **Output**: DB connectivity result in `function-health.json`
- **Depends on**: T-014
- **Gate**: Function successfully queries and returns data

### T-018: Phase 4 gate
- **Status**: [ ] pending
- **Script**: `scripts/supabase-migrate/04-gate.sh`
- **Action**: Validate `function-health.json` shows 39/39 healthy and all critical paths pass. Emit `gate-result-phase4.json`.
- **Output**: `docs/evidence/<ts>/supabase-migrate/gate-result-phase4.json`
- **Depends on**: T-015, T-016, T-017
- **Gate**: `gate-result-phase4.json` shows PASS

---

## Epic 4: Consumer Cutover (Phase 5)

### T-019: Create DNS records in Cloudflare
- **Status**: [ ] pending
- **Script**: `scripts/supabase-migrate/05-dns-setup.sh`
- **Action**: Create `supabase.insightpulseai.com` CNAME record pointing to Azure Front Door endpoint `ipai-fd-dev-ep-fnh4e8d6gtdhc8ax.z03.azurefd.net`. DNS-only mode (grey cloud). TTL 60. Configure Front Door origin group for VM `4.193.100.31:8000`.
- **Output**: DNS verification (dig + curl)
- **Depends on**: T-012 (Phase 3 gate), T-018 (Phase 4 gate)
- **Gate**: `supabase.insightpulseai.com` resolves correctly, HTTPS terminates with valid TLS

### T-020: Create consumer rewire manifest
- **Status**: [ ] pending
- **Script**: Manual creation
- **Action**: Create `config/supabase-consumers.yaml` declaring all consumers, current endpoints, target endpoints, and smoke test commands. Per constitution C-010.
- **Output**: `config/supabase-consumers.yaml`
- **Depends on**: None (can be done anytime)
- **Gate**: Manifest lists all 6 consumer categories

### T-021: Rewire n8n consumers
- **Status**: [ ] pending
- **Script**: `scripts/supabase-migrate/05-rewire-consumer.sh n8n`
- **Action**: Update `SUPABASE_URL` env var in n8n container configuration. Restart n8n. Run smoke test workflow.
- **Output**: `consumer-smoke.json` (n8n entry)
- **Depends on**: T-019, T-020
- **Gate**: n8n smoke test workflow completes successfully

### T-022: Rewire MCP jobs consumers
- **Status**: [ ] pending
- **Script**: `scripts/supabase-migrate/05-rewire-consumer.sh mcp`
- **Action**: Update Supabase URL in MCP job configurations. Run `ops-health` function invocation test.
- **Output**: `consumer-smoke.json` (MCP entry)
- **Depends on**: T-021
- **Gate**: MCP ops-health returns healthy status

### T-023: Rewire Odoo consumers
- **Status**: [ ] pending
- **Script**: `scripts/supabase-migrate/05-rewire-consumer.sh odoo`
- **Action**: Update `ir.config_parameter` `supabase_url` in Odoo. Trigger `odoo-webhook` test.
- **Output**: `consumer-smoke.json` (Odoo entry)
- **Depends on**: T-022
- **Gate**: Odoo webhook test succeeds

### T-024: Rewire Slack and GitHub consumers
- **Status**: [ ] pending
- **Script**: `scripts/supabase-migrate/05-rewire-consumer.sh slack` then `github`
- **Action**: Update webhook URLs in Slack app config and GitHub App settings. Send test events.
- **Output**: `consumer-smoke.json` (Slack + GitHub entries)
- **Depends on**: T-023
- **Gate**: Test webhook deliveries succeed

### T-025: Rewire web app consumers
- **Status**: [ ] pending
- **Script**: `scripts/supabase-migrate/05-rewire-consumer.sh webapp`
- **Action**: Update `NEXT_PUBLIC_SUPABASE_URL` env var. Redeploy. Test auth flow and data fetch.
- **Output**: `consumer-smoke.json` (webapp entry)
- **Depends on**: T-024
- **Gate**: Web app auth flow and data fetch succeed

### T-026: All-consumer smoke tests
- **Status**: [ ] pending
- **Script**: `scripts/supabase-migrate/05-smoke-all.sh`
- **Action**: Run smoke tests for all consumers in parallel. Aggregate results.
- **Output**: Complete `consumer-smoke.json`
- **Depends on**: T-025
- **Gate**: All 6 consumer categories pass

### T-027: 30-day parallel run monitoring
- **Status**: [ ] pending
- **Script**: Cron job on VM
- **Action**: Daily comparison job: verify self-hosted is accumulating new data, alert if any consumer falls back to cloud URL, emit weekly checkpoint reports.
- **Output**: Weekly reports in `docs/evidence/<ts>/supabase-migrate/parallel-run/`
- **Depends on**: T-026
- **Gate**: 30 days complete with zero critical incidents

### T-028: Final cutover readiness report
- **Status**: [ ] pending
- **Script**: `scripts/supabase-migrate/05-gate.sh`
- **Action**: Validate all conditions: 30-day parallel clean, all consumers verified, no cloud writes in 7 days, backup strategy operational, monitoring configured, DR runbook tested.
- **Output**: `docs/evidence/<ts>/supabase-migrate/gate-result-phase5.json`
- **Depends on**: T-027
- **Gate**: All conditions PASS

### T-029: Cloud project freeze
- **Status**: [ ] pending
- **Script**: `scripts/supabase-migrate/05-freeze-cloud.sh`
- **Action**: Pause cloud project compute. Set database to read-only. Export final safety backup.
- **Output**: Final backup file + freeze confirmation
- **Depends on**: T-028
- **Gate**: Cloud project is read-only, final backup exists

### T-030: Cloud project decommission
- **Status**: [ ] pending
- **Script**: `scripts/supabase-migrate/05-decomm-cloud.sh`
- **Action**: After 30-day hold period post-freeze, delete cloud project `spdtwktxdalcfigzeqrz`. Remove from Supabase org. Update all documentation references.
- **Output**: Deletion confirmation, updated docs
- **Depends on**: T-029 + 30-day hold
- **Gate**: Project deleted, no references to cloud project in active configs

---

## Task Dependency Graph

```
T-001 -> T-002 -> T-003 -> T-004 -> T-006 (Phase 2 gate)
                     |        |
                     v        v
                   T-005 -> T-006
                              |
              +---------------+---------------+
              |                               |
              v                               v
        T-007 -> T-008 -> T-009         T-013 -> T-014 -> T-015
              |        |                              |        |
              v        v                              v        v
           T-011    T-010                          T-017    T-016
              |        |                              |        |
              v        v                              v        v
           T-012 (Phase 3 gate)                    T-018 (Phase 4 gate)
              |                                       |
              +-------------------+-------------------+
                                  |
                                  v
                          T-019 -> T-020
                                  |
                                  v
                    T-021 -> T-022 -> T-023 -> T-024 -> T-025
                                                          |
                                                          v
                                                       T-026
                                                          |
                                                          v
                                                       T-027
                                                          |
                                                          v
                                                       T-028
                                                          |
                                                          v
                                                       T-029
                                                          |
                                                     (30-day hold)
                                                          |
                                                          v
                                                       T-030
```

---

## Summary

| Epic | Tasks | IDs |
|------|-------|-----|
| Schema Migration (Phase 2) | 6 | T-001 through T-006 |
| Data Migration (Phase 3) | 6 | T-007 through T-012 |
| Edge Functions (Phase 4) | 6 | T-013 through T-018 |
| Consumer Cutover (Phase 5) | 12 | T-019 through T-030 |
| **Total** | **30** | T-001 through T-030 |

---

*Spec bundle: supabase-self-host-cutover | Created: 2026-03-14*
