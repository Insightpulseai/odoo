# Azure Self-Host Migration -- PRD

---

## Goal

Complete migration of all Supabase assets from managed cloud project `spdtwktxdalcfigzeqrz` to self-hosted Supabase on Azure VM `4.193.100.31`. Assets include: tables, seeds, 39 edge functions, ~47 n8n workflows, pg_cron jobs, and consumer endpoint rewiring for 8 consumers.

---

## In Scope

| Asset Category | Count | Source |
|---------------|-------|--------|
| Database schema (tables, views, extensions, roles) | Full inventory | `supabase_cloud_inventory.py` output |
| Table data (reference, master, transactional) | All canonical tables | Cloud Supabase PostgreSQL |
| Seed data (canonicalized, deduplicated) | 6 duplicate groups to resolve | `SEED_DATA_INVENTORY.md` |
| Edge Functions | 39 in deploy manifest | `platform/supabase/edge-functions/deploy/manifest.yaml` |
| pg_cron jobs | All scheduled jobs | `cron.job` table |
| n8n workflows | ~47 workflows | n8n API + repo JSON exports |
| Consumer rewire | 8 consumers | `platform/supabase/cutover/consumers.yaml` |
| Storage buckets | Bucket metadata + objects | Supabase Storage API |

---

## Out of Scope

| Item | Reason |
|------|--------|
| VM-to-ACA/AKS replatforming | Separate program after migration proven (constitution R1) |
| Odoo database migration | Stays on local PostgreSQL; Odoo does not use Supabase for its database |
| DNS changes | Already completed; subdomains already point to Azure infrastructure |
| Business logic redesign | Migration is a lift-and-shift with canonicalization, not a rewrite |
| Workflow functional rewrites | Unless required for self-hosted compatibility (URL/credential changes only) |
| Databricks pipeline changes | Databricks is reconciliation plane only, not operational cutover plane |
| Fivetran/Airbyte/reverse ETL adoption | Not part of initial migration scope |

---

## Success Criteria

| Criterion | Validation Method | Pass Condition |
|-----------|-------------------|----------------|
| Zero data loss | Row-count comparison per table | Source and target counts within 1% tolerance |
| Critical table integrity | Keyed checksum on top-10 tables by row count | Exact MD5 match |
| Seed deduplication | Business key uniqueness check post-replay | Zero duplicate records per business key |
| All edge functions healthy | Smoke test per manifest entry (39 functions) | HTTP 200 from each endpoint |
| All n8n workflows imported | Import report via n8n API | 47 workflows present, all `active: false` initially |
| pg_cron jobs migrated | `cron.job` count comparison | Exact count match source vs target, all disabled on import |
| All consumers pointing to self-hosted URL | Health check on all 8 consumers | All consumers report healthy against self-hosted endpoints |
| n8n workflows operational | Wave-by-wave enablement with smoke tests | All 5 waves enabled and stable |
| Managed Supabase quiesced | Traffic monitoring | Zero requests to `spdtwktxdalcfigzeqrz.supabase.co` for 24h post-cutover |

---

## Dependencies

| Dependency | Status | Notes |
|-----------|--------|-------|
| Azure VM runtime-up (`4.193.100.31`) | Done | 14 Docker services running |
| Docker Compose stack healthy | Done | Supabase self-hosted stack operational |
| Azure Key Vault secrets populated | Done | `kv-ipai-dev` with 28+ secrets |
| SSH access to VM | Required | For SCP of edge functions and direct administration |
| Seed inventory evidence | Done | `docs/architecture/SEED_DATA_INVENTORY.md` |
| Seed canonical map | Required | `ssot/migration/seed_canonical_map.yaml` |
| Consumer manifest | Done | `platform/supabase/cutover/consumers.yaml` |
| Edge function deploy manifest | Done | `platform/supabase/edge-functions/deploy/manifest.yaml` |
| CI workflow skeleton | Done | `.github/workflows/supabase-self-host-migration.yml` (5 phases) |
| Phase 1 (Inventory) | Done | Completed via `supabase_cloud_inventory.py` |

---

## Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|-----------|
| Schema drift during migration window | High | Medium | Freeze cloud writes during final delta; keep migration window under 4h |
| Data loss during table migration | High | Low | pg_dump before AND after; verify row counts at every checkpoint |
| Sequence reset after data import | High | Medium | Explicit `setval()` for all sequences after data load |
| pg_cron timing conflicts | Medium | Medium | Import all jobs disabled; enable in controlled order after smoke tests |
| n8n credential mismatches | High | Medium | Export credentials backup before import; map all aliases to Key Vault refs |
| Auth token invalidation | High | Low | JWT secret must match cloud and self-hosted; verify before cutover |
| Edge function cold start failures | Low | Medium | Pre-warm critical functions after deploy; retry logic in smoke tests |
| Consumer rewire partial failure | High | Low | Rewire in priority order per consumers.yaml; rollback individual consumers if needed |
| DNS propagation delay | Medium | Low | Not applicable (DNS already points to Azure); but keep cloud running 7 days post-cutover |

---

## Consumer Rewire Order

Per `platform/supabase/cutover/consumers.yaml`, the 8 consumers are rewired in priority order. Each consumer is switched individually with a health check gate before proceeding to the next. If any consumer fails, its rewire is rolled back without affecting previously successful consumers.

---

## Timeline Constraints

- Migration (phases 2--5) and enablement (n8n waves) are separate workstreams
- Final cutover window should not exceed 4 hours of write-freeze on cloud
- 7-day soak period required before cloud project decommission
- Databricks reconciliation queries run daily during soak period
