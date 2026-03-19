# Implementation Plan: Supabase Cloud-to-Self-Hosted Migration

> Execution plan for phases 2-5. Phase 1 (infrastructure) is complete.
> Governed by `constitution.md`. Requirements from `prd.md`.

---

## Architecture

```
                          CURRENT STATE
                          ============

  n8n ──┐
  Odoo ──┤                ┌──────────────────────────┐
  Web ───┼── HTTPS ──────>│  Supabase Cloud          │
  MCP ───┤                │  spdtwktxdalcfigzeqrz    │
  Slack ─┤                │  PostgreSQL (managed)    │
  GitHub─┘                │  39 Edge Functions       │
                          │  GoTrue / PostgREST      │
                          │  Storage / Realtime      │
                          └──────────────────────────┘


                          TARGET STATE
                          ============

  n8n ──┐
  Odoo ──┤     ┌────────────┐     ┌──────────────┐     ┌─────────────────────────────┐
  Web ───┼────>│ Cloudflare │────>│ Azure Front  │────>│ vm-ipai-supabase-dev        │
  MCP ───┤     │ DNS-only   │     │ Door         │     │ 4.193.100.31                │
  Slack ─┤     └────────────┘     │ ipai-fd-dev  │     │                             │
  GitHub─┘                        └──────────────┘     │ /opt/supabase-deploy/       │
                                                       │ ┌─────────────────────────┐ │
           supabase.insightpulseai.com                 │ │ Kong (8000)             │ │
                                                       │ │ ├─ PostgREST (3000)     │ │
                                                       │ │ ├─ GoTrue (9999)        │ │
                                                       │ │ ├─ Edge-Runtime (5001)  │ │
                                                       │ │ ├─ Storage (5000)       │ │
                                                       │ │ ├─ Realtime (4000)      │ │
                                                       │ │ └─ Studio (3001)        │ │
                                                       │ ├─ PostgreSQL 15.8 (5432) │ │
                                                       │ ├─ Analytics (4000)       │ │
                                                       │ ├─ imgproxy               │ │
                                                       │ ├─ meta                   │ │
                                                       │ ├─ vector                 │ │
                                                       │ ├─ pooler (6543)          │ │
                                                       │ └─ n8n                    │ │
                                                       │                           │ │
                                                       └───────────────────────────┘ │
                                                       └─────────────────────────────┘


                          MIGRATION FLOW
                          ==============

  Phase 2          Phase 3          Phase 4          Phase 5
  ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────────┐
  │ Schema   │────>│ Data     │────>│ Edge     │────>│ Cutover      │
  │ Export & │     │ Export & │     │ Functions│     │ DNS + Rewire │
  │ Apply    │     │ Import   │     │ Deploy   │     │ + Parallel   │
  │          │     │          │     │          │     │ + Decomm     │
  └──────────┘     └──────────┘     └──────────┘     └──────────────┘
       │                │                │                  │
       v                v                v                  v
  schema-parity    row-counts      function-health    consumer-smoke
  .json            .json           .json              .json
```

---

## Phase 2: Schema Migration

### 2.1 Export Cloud Schema Inventory

```bash
# Script: scripts/supabase-migrate/02-schema-export.sh
# Exports schema DDL from cloud project

supabase db dump --project-ref spdtwktxdalcfigzeqrz \
  --schema public,auth,storage,realtime,ops,extensions \
  > docs/evidence/<ts>/supabase-migrate/cloud-schema.sql
```

Output: Full DDL of all schemas, tables, indexes, constraints, functions, triggers.

### 2.2 Extension Parity Check

Query both databases for installed extensions and compare.

| Extension | Required | Purpose |
|-----------|----------|---------|
| `pgvector` | Yes | Vector embeddings for semantic search |
| `pgjwt` | Yes | JWT generation for auth |
| `pg_graphql` | Yes | GraphQL API layer |
| `pg_cron` | Yes | Scheduled jobs |
| `pg_net` | Yes | HTTP requests from SQL |
| `pgsodium` | Yes | Encryption at rest |
| `supautils` | Yes | Supabase utility functions |
| `uuid-ossp` | Yes | UUID generation |
| `postgis` | If present | Geospatial (check cloud) |

Script compares `SELECT * FROM pg_extension` on both and emits diff.

### 2.3 Apply Repo Migrations

```bash
# Script: scripts/supabase-migrate/02-apply-migrations.sh
# Applies all ~150 migration files in chronological order

for migration in supabase/migrations/*.sql; do
  psql -h 4.193.100.31 -p 5432 -U supabase_admin -d postgres \
    -f "$migration" \
    2>&1 | tee -a docs/evidence/<ts>/supabase-migrate/migration-apply.log
done
```

Idempotency: Migrations use `CREATE TABLE IF NOT EXISTS`, `DO $$ BEGIN ... EXCEPTION WHEN ... END $$` patterns.

### 2.4 Schema Parity Report

Compare cloud and self-hosted:

| Check | Method |
|-------|--------|
| Tables | `information_schema.tables` diff |
| Columns | `information_schema.columns` diff (name, type, nullable, default) |
| Indexes | `pg_indexes` diff |
| Constraints | `information_schema.table_constraints` diff |
| Functions | `pg_proc` + `pg_namespace` diff |
| RLS policies | `pg_policies` diff (name, table, cmd, qual, with_check) |
| Triggers | `information_schema.triggers` diff |

Output: `schema-parity.json` with per-category MATCH/DRIFT status.

### 2.5 Phase 2 Gate

All categories in schema parity report must be MATCH. Any DRIFT blocks Phase 3.

---

## Phase 3: Data Migration

### 3.1 Export Cloud Data

```bash
# Script: scripts/supabase-migrate/03-data-export.sh

pg_dump --data-only --no-owner --no-privileges \
  --schema public --schema auth --schema storage --schema ops \
  --exclude-table-data 'realtime.*' \
  --exclude-table-data 'analytics.*' \
  -h <cloud-host> -p 5432 -U postgres \
  -Fc -f docs/evidence/<ts>/supabase-migrate/cloud-data.dump
```

Exclusions: `realtime.*` (ephemeral presence), `analytics.*` (short-term, will repopulate).

### 3.2 Import to Self-Hosted

```bash
# Script: scripts/supabase-migrate/03-data-import.sh

pg_restore --data-only --no-owner --no-privileges \
  --disable-triggers \
  -h 4.193.100.31 -p 5432 -U supabase_admin -d postgres \
  docs/evidence/<ts>/supabase-migrate/cloud-data.dump \
  2>&1 | tee docs/evidence/<ts>/supabase-migrate/data-import.log
```

`--disable-triggers`: Prevents trigger side effects during bulk import. Triggers re-enabled after.

### 3.3 Row-Count Parity

```bash
# Script: scripts/supabase-migrate/03-verify-counts.sh
# Queries both databases, compares per-table row counts

SELECT schemaname, tablename, n_tup_ins - n_tup_del as row_estimate
FROM pg_stat_user_tables
ORDER BY schemaname, tablename;
```

Output: `row-counts.json` with `{table, cloud_count, self_hosted_count, drift_pct}`.

### 3.4 Critical Table Deep Verification

| Table | Verification |
|-------|-------------|
| `auth.users` | Row count exact match + `SELECT count(DISTINCT email)` match |
| `auth.identities` | Row count + FK to `auth.users` integrity |
| `ops.task_queue` | Row count + `GROUP BY status` distribution match |
| `ops.platform_events` | Row count + `MAX(id)` match (append-only) |
| `storage.buckets` | Exact row match + name list match |
| `storage.objects` | Row count + `GROUP BY bucket_id` distribution match |

### 3.5 Phase 3 Gate

- All critical tables: exact row count match
- All other tables: drift < 0.1%
- FK integrity check passes
- `row-counts.json` emitted

---

## Phase 4: Edge Functions

### 4.1 Function Deploy Manifest

Generate manifest from repo:

```bash
# Script: scripts/supabase-migrate/04-generate-manifest.sh
# Scans supabase/supabase/functions/ and generates deploy list

ls -d supabase/supabase/functions/*/index.ts | while read f; do
  dirname "$f" | xargs basename
done > config/edge-function-manifest.txt
```

Expected: 39 functions.

### 4.2 Deploy to Self-Hosted Edge-Runtime

```bash
# Script: scripts/supabase-migrate/04-deploy-functions.sh
# Deploys each function to the self-hosted edge-runtime container

for func in $(cat config/edge-function-manifest.txt); do
  # Copy function source to edge-runtime volumes
  # Configure function environment variables from Key Vault
  echo "Deploying: $func"
done
```

Environment variables for functions are sourced from Key Vault and injected into the edge-runtime container's environment.

### 4.3 Function Health Verification

```bash
# Script: scripts/supabase-migrate/04-verify-functions.sh
# Probes each function endpoint

SUPABASE_URL="http://4.193.100.31:8000"
ANON_KEY=$(az keyvault secret show --vault-name kv-ipai-dev \
  --name supabase-anon-key --query value -o tsv)

for func in $(cat config/edge-function-manifest.txt); do
  STATUS=$(curl -s -o /dev/null -w '%{http_code}' \
    -H "Authorization: Bearer $ANON_KEY" \
    "$SUPABASE_URL/functions/v1/$func")
  echo "{\"function\": \"$func\", \"status\": $STATUS}"
done > docs/evidence/<ts>/supabase-migrate/function-health.json
```

### 4.4 Critical Path Tests

| Path | Test Command | Expected |
|------|-------------|----------|
| Auth | `curl POST /functions/v1/auth-bootstrap` | 200 + JSON body |
| Ops | `curl GET /functions/v1/ops-health` | 200 + `{"status":"ok"}` |
| Odoo webhook | `curl POST /functions/v1/odoo-webhook` | 200 or 401 (auth required) |
| MCP gateway | `curl GET /functions/v1/mcp-gateway` | 200 + capabilities |
| Semantic | `curl POST /functions/v1/semantic-query` | 200 + schema response |

### 4.5 Function-to-DB Connectivity

Verify functions can reach PostgREST by invoking a function that queries a known table and returns a count.

### 4.6 Phase 4 Gate

- 39/39 functions deployed
- 39/39 function endpoints return non-5xx
- All critical paths pass
- Function-to-DB connectivity verified
- `function-health.json` emitted

---

## Phase 5: Cutover

### 5.1 DNS Configuration

```
Record: supabase.insightpulseai.com
Type: CNAME
Target: ipai-fd-dev-ep-fnh4e8d6gtdhc8ax.z03.azurefd.net
Proxy: DNS-only (grey cloud)
TTL: 60 (low, for fast rollback)
```

Azure Front Door origin configuration:

```
Origin group: og-supabase
Origin: vm-ipai-supabase-dev
Host: 4.193.100.31
Port: 8000 (Kong gateway)
Protocol: HTTP (TLS terminates at Front Door)
Health probe: /health (Kong)
```

### 5.2 Consumer Rewire Sequence

Executed in order, with smoke test between each:

```
1. n8n
   - Update: SUPABASE_URL env var in n8n container
   - Smoke: Trigger a test workflow that reads/writes Supabase
   - Rollback: Revert env var to cloud URL

2. MCP jobs
   - Update: SUPABASE_URL in MCP job configs
   - Smoke: Run ops-health function invocation
   - Rollback: Revert config

3. Odoo (ipai_* modules)
   - Update: ir.config_parameter supabase_url
   - Smoke: Trigger odoo-webhook test
   - Rollback: Revert config parameter

4. Slack integrations
   - Update: Webhook URLs in Slack app config
   - Smoke: Send test event to webhook endpoint
   - Rollback: Revert webhook URLs

5. GitHub App
   - Update: Webhook URL in GitHub App settings
   - Smoke: Trigger test webhook delivery
   - Rollback: Revert webhook URL

6. Web apps (Next.js)
   - Update: NEXT_PUBLIC_SUPABASE_URL env var
   - Smoke: Auth flow test, data fetch test
   - Rollback: Redeploy with cloud URL
```

### 5.3 Parallel Run (30 Days)

- Cloud project remains active but receives no new writes (consumers are rewired)
- Daily comparison job checks self-hosted is accumulating data correctly
- Alert on any consumer fallback to cloud URLs
- Weekly checkpoint reports emitted to `docs/evidence/`

### 5.4 Final Cutover Gate

All must be true:

- [ ] 30-day parallel run complete with zero critical incidents
- [ ] All consumers verified on self-hosted (smoke tests green)
- [ ] No cloud writes detected in last 7 days
- [ ] Backup strategy for self-hosted PostgreSQL is operational
- [ ] Monitoring and alerting configured for self-hosted
- [ ] Disaster recovery runbook documented and tested

### 5.5 Cloud Decommission

1. Freeze cloud project (pause compute, set read-only)
2. Export final backup from cloud (safety net)
3. Hold frozen state for 30 additional days
4. Delete cloud project after hold period

---

## Phase Dependencies

```
Phase 1 (COMPLETE)
    |
    v
Phase 2 (Schema)
    |
    v
Phase 3 (Data) ----+
    |               |
    v               v
Phase 4 (Functions) |
    |               |
    +-------+-------+
            |
            v
      Phase 5 (Cutover)
```

Phase 3 and Phase 4 can run in parallel after Phase 2 completes. Phase 5 requires both Phase 3 and Phase 4 to be complete.

---

## Scripts Directory Structure

```
scripts/supabase-migrate/
  00-common.sh              # Shared functions, vault helpers, evidence paths
  02-schema-export.sh       # Export cloud schema
  02-apply-migrations.sh    # Apply migrations to self-hosted
  02-verify-schema.sh       # Schema parity report
  02-gate.sh                # Phase 2 gate check
  03-data-export.sh         # Export cloud data
  03-data-import.sh         # Import to self-hosted
  03-verify-counts.sh       # Row count parity
  03-verify-critical.sh     # Critical table deep checks
  03-gate.sh                # Phase 3 gate check
  04-generate-manifest.sh   # Edge Function manifest
  04-deploy-functions.sh    # Deploy functions
  04-verify-functions.sh    # Function health probes
  04-test-critical.sh       # Critical path tests
  04-gate.sh                # Phase 4 gate check
  05-dns-setup.sh           # Cloudflare + Front Door DNS
  05-rewire-consumer.sh     # Per-consumer rewire (takes consumer name arg)
  05-smoke-all.sh           # All consumer smoke tests
  05-gate.sh                # Phase 5 gate check
  99-rollback-phase.sh      # Rollback a specific phase
```

---

## Evidence Directory Structure

```
docs/evidence/<YYYYMMDD-HHMM>/supabase-migrate/
  cloud-schema.sql
  migration-apply.log
  schema-parity.json
  cloud-data.dump
  data-import.log
  row-counts.json
  critical-tables.json
  edge-function-manifest.txt
  function-health.json
  consumer-smoke.json
  gate-result-phase2.json
  gate-result-phase3.json
  gate-result-phase4.json
  gate-result-phase5.json
```

---

*Spec bundle: supabase-self-host-cutover | Created: 2026-03-14*
