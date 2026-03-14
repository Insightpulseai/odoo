# Azure Self-Host Migration — ETL Pipeline Plan

> Migrate all n8n workflows, Supabase tables/seeds, and Edge Functions
> from managed/transitional state to fully self-hosted on Azure.

---

## Current State

| Component | Where Now | Target | Gap |
|-----------|----------|--------|-----|
| **Odoo CE 19** | Azure Container Apps | ACA | **DONE** (live since 2026-03-11) |
| **n8n** | Azure VM `4.193.100.31` (Docker) | Same VM or ACA | Runtime-up, DNS pending |
| **Supabase (14 services)** | Azure VM `4.193.100.31` (Docker) | Same VM | Runtime-up, Phase 1 done |
| **Supabase Cloud** | `spdtwktxdalcfigzeqrz.supabase.co` | Decommission | Phases 2-5 pending |
| **Edge Functions (88)** | Cloud (39 deployed) + repo (88 total) | Self-hosted Deno runtime on VM | Phase 4 pending |
| **n8n Workflows (47)** | JSON in repo + n8n DB | Self-hosted n8n on VM | Import pending |
| **Seeds (120 files)** | Repo + Cloud Supabase | Self-hosted PostgreSQL on VM | Migration pending |

---

## Migration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  PHASE 2: Schema                                                 │
│  Cloud PG ──pg_dump──► schema.sql ──psql──► Self-hosted PG      │
│                                                                   │
│  PHASE 3: Data (ETL Pipeline)                                    │
│  Cloud PG ──pg_dump -a──► data.sql ──psql──► Self-hosted PG     │
│  + Repo seeds ──seed scripts──► Self-hosted PG                   │
│  + Verify: row count parity within 1%                            │
│                                                                   │
│  PHASE 4: Edge Functions                                         │
│  supabase/functions/ ──scp──► /opt/supabase-deploy/volumes/     │
│  + Restart edge-runtime container                                │
│  + Smoke test all 39 critical/standard functions                 │
│                                                                   │
│  PHASE 4b: n8n Workflow Import                                   │
│  automations/n8n/workflows/*.json ──n8n CLI──► n8n database     │
│  + Credential rewire (cloud URLs → self-hosted URLs)             │
│  + Activate workflows                                            │
│                                                                   │
│  PHASE 5: Consumer Cutover                                       │
│  Edge Functions → update .env (SUPABASE_URL)                     │
│  n8n → update .env (SUPABASE_URL)                                │
│  Odoo ACA → az containerapp env update                           │
│  DNS → Cloudflare → Front Door routes                            │
│  Verify → end-to-end smoke tests                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 2: Schema Migration

### Existing Script
`ops-platform/supabase/scripts/supabase_schema_export.sh`

### What It Does
1. `pg_dump --schema-only` from cloud Supabase
2. SSH tunnel to VM, `pg_dump --schema-only` from self-hosted
3. Diff the two schemas
4. Report missing tables/columns/indexes
5. Gate: SCHEMA_PARITY must pass

### Tables to Migrate

From the seed inventory, the cloud project contains:

| Schema | Table Category | Est. Tables | Notes |
|--------|---------------|-------------|-------|
| `public` | Core app tables | ~50 | SsoDetails, UserOrganization, etc. |
| `ops` | Operations | ~10 | platform_events, task_queue (append-only) |
| `mcp_jobs` | Job queue | ~5 | jobs, job_runs, job_events, dead_letter_queue, metrics |
| `scout` | Analytics/BI | ~15 | Materialized views, gold tables |
| `auth` | Supabase Auth | ~10 | users, sessions, identities (GoTrue-managed) |
| `storage` | Supabase Storage | ~5 | buckets, objects |
| `realtime` | Supabase Realtime | ~3 | subscription tracking |
| `_supabase` | Internal | ~5 | Do not migrate manually — GoTrue/PostgREST manage |

### Extensions Required on Self-Hosted
```sql
CREATE EXTENSION IF NOT EXISTS pgvector;
CREATE EXTENSION IF NOT EXISTS pgjwt;
CREATE EXTENSION IF NOT EXISTS pg_graphql;
CREATE EXTENSION IF NOT EXISTS pg_cron;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

### Run
```bash
gh workflow run supabase-self-host-migration.yml \
  -f phase=schema -f mode=dry-run
```

---

## Phase 3: Data Migration (ETL)

### Existing Script
`ops-platform/supabase/scripts/supabase_data_migrate.sh`

### ETL Pipeline Design

```
Source (Cloud PG)                    Target (Self-Hosted PG)
─────────────────                    ───────────────────────
                   ┌─────────────┐
  pg_dump -a ────► │  Transform  │ ────► psql (SSH tunnel)
  --data-only      │             │
  --no-owner       │ - Strip     │
                   │   cloud-    │
                   │   specific  │
                   │   roles     │
                   │ - Remap     │
                   │   auth UUIDs│
                   │ - Preserve  │
                   │   sequences │
                   └─────────────┘

  Repo Seeds                         Self-Hosted PG
  ──────────                         ──────────────
                   ┌─────────────┐
  supabase/seeds/  │  Seed       │
  *.sql        ──► │  Runner     │ ────► psql
                   │             │
  supabase/seed/   │ - Order by  │
  9000-9008/   ──► │   prefix    │
                   │ - Skip      │
                   │   deprecated│
                   │   (002)     │
                   └─────────────┘
```

### Migration Order (dependency-safe)

```
1. auth.users          (GoTrue manages; export/import via Supabase CLI)
2. public.*            (core app tables — no FK to ops/mcp_jobs)
3. ops.*               (append-only; depends on public.*)
4. mcp_jobs.*          (independent schema)
5. scout.*             (materialized views — recreate, don't migrate data)
6. storage.buckets     (metadata only; actual files in S3-compatible storage)
7. pg_cron.job         (recreate from repo definitions)
```

### Seed Execution Order (from SEED_DATA_INVENTORY.md)

```bash
# 1. Supabase core seeds (numbered prefix = order)
psql $TARGET_DB -f supabase/seeds/001_hr_seed.sql
# SKIP: supabase/seeds/002_finance_seed.sql (DEPRECATED)
psql $TARGET_DB -f supabase/seeds/003_odoo_dict_seed.sql

# 2. Consolidated seeds (9000-series)
psql $TARGET_DB -f supabase/seed/001_saas_feature_seed.sql
psql $TARGET_DB -f supabase/seed/9003_ai_rag/9003_ai_rag_agent_registry_seed.sql
psql $TARGET_DB -f supabase/seed/9004_analytics/9004_analytics_kpi_registry_seed.sql
psql $TARGET_DB -f supabase/seed/9004_analytics/9004_analytics_superset_dashboard_seed.sql
psql $TARGET_DB -f supabase/seed/9007_skills/9007_skills_certification_seed.sql
psql $TARGET_DB -f supabase/seed/9008_drawio_skills/9008_drawio_certification_seed.sql

# 3. Workstream seeds (YAML → SQL transform or direct load)
# These require a YAML-to-SQL loader or Supabase CLI import
```

### Verification Gate
```bash
# Row count parity check (within 1% tolerance)
for table in $(psql $SOURCE_DB -t -c "SELECT tablename FROM pg_tables WHERE schemaname='public'"); do
  SOURCE_COUNT=$(psql $SOURCE_DB -t -c "SELECT count(*) FROM public.$table")
  TARGET_COUNT=$(psql $TARGET_DB -t -c "SELECT count(*) FROM public.$table")
  DIFF=$(echo "scale=2; (($SOURCE_COUNT - $TARGET_COUNT) / $SOURCE_COUNT) * 100" | bc)
  echo "$table: source=$SOURCE_COUNT target=$TARGET_COUNT diff=${DIFF}%"
done
```

### Run
```bash
gh workflow run supabase-self-host-migration.yml \
  -f phase=data -f mode=dry-run
```

---

## Phase 4: Edge Functions + n8n Workflows

### 4a: Edge Functions

**Existing Script**: `ops-platform/supabase/scripts/supabase_edge_functions_sync.sh`
**Manifest**: `ops-platform/supabase/edge-functions/deploy/manifest.yaml` (39 functions)

```
Repo: supabase/functions/ (88 dirs)
  │
  ├── manifest.yaml lists 39 deployable functions
  │   ├── Tier: critical (auth, ops, webhook, gateway)
  │   ├── Tier: standard (AI, semantic, sync)
  │   └── Tier: optional (utilities)
  │
  └── SCP to VM → /opt/supabase-deploy/volumes/functions/
      └── Restart supabase-functions container
      └── Smoke test each function
```

### 4b: n8n Workflow Migration

**Not covered by existing CI workflow — needs new pipeline.**

```
Source: automations/n8n/workflows/*.json (47 files)
Target: n8n instance at https://n8n-azure.insightpulseai.com

Pipeline:
1. Export current n8n workflow list (GET /api/v1/workflows)
2. For each JSON in repo:
   a. Check if workflow exists in n8n (by name match)
   b. If exists: PUT /api/v1/workflows/:id (update)
   c. If new: POST /api/v1/workflows (create)
3. Credential rewire:
   - Replace spdtwktxdalcfigzeqrz.supabase.co → supabase.insightpulseai.com
   - Replace managed Supabase API keys → self-hosted keys
   - Preserve credential references ({{ $credentials.* }})
4. Activate workflows (PUT /api/v1/workflows/:id/activate)
5. Smoke test: trigger health-check workflow
```

### n8n Credential Migration

| Credential | Cloud Value | Self-Hosted Value |
|------------|------------|-------------------|
| Supabase URL | `https://spdtwktxdalcfigzeqrz.supabase.co` | `https://supabase.insightpulseai.com` |
| Supabase Anon Key | Cloud anon key | Self-hosted anon key (Key Vault: `supabase-anon-key`) |
| Supabase Service Role | Cloud service role | Self-hosted service role (Key Vault: `supabase-service-role-key`) |
| Odoo URL | `https://erp.insightpulseai.com` | Same (no change) |
| GitHub Token | PAT | Same (no change) |
| Slack Webhook | Slack URL | Same (no change) |

### n8n Workflow Import Script (New)

```bash
#!/bin/bash
# scripts/n8n/import_workflows.sh
#
# Import all n8n workflow JSON files from repo to self-hosted instance.
# Prerequisites: N8N_API_URL, N8N_API_KEY set in environment.

set -euo pipefail

N8N_API_URL="${N8N_API_URL:-https://n8n-azure.insightpulseai.com}"
WORKFLOW_DIR="automations/n8n/workflows"
LOG_DIR="docs/evidence/$(date +%Y%m%d-%H%M)/n8n-import"

mkdir -p "$LOG_DIR"

# Get existing workflows
existing=$(curl -sf -H "X-N8N-API-KEY: $N8N_API_KEY" \
  "$N8N_API_URL/api/v1/workflows" | jq -r '.data[].name')

imported=0
updated=0
failed=0

for json in "$WORKFLOW_DIR"/*.json; do
  name=$(jq -r '.name // .workflow.name // empty' "$json" 2>/dev/null)
  [ -z "$name" ] && name=$(basename "$json" .json)

  # URL rewire: cloud → self-hosted
  rewired=$(mktemp)
  sed 's|spdtwktxdalcfigzeqrz\.supabase\.co|supabase.insightpulseai.com|g' "$json" > "$rewired"

  if echo "$existing" | grep -qF "$name"; then
    # Update existing
    id=$(curl -sf -H "X-N8N-API-KEY: $N8N_API_KEY" \
      "$N8N_API_URL/api/v1/workflows" | jq -r ".data[] | select(.name==\"$name\") | .id")
    status=$(curl -sf -o /dev/null -w "%{http_code}" \
      -X PUT -H "X-N8N-API-KEY: $N8N_API_KEY" \
      -H "Content-Type: application/json" \
      -d @"$rewired" "$N8N_API_URL/api/v1/workflows/$id")
    if [ "$status" = "200" ]; then
      echo "UPDATED: $name" | tee -a "$LOG_DIR/import.log"
      ((updated++))
    else
      echo "FAIL: $name (HTTP $status)" | tee -a "$LOG_DIR/import.log"
      ((failed++))
    fi
  else
    # Create new
    status=$(curl -sf -o /dev/null -w "%{http_code}" \
      -X POST -H "X-N8N-API-KEY: $N8N_API_KEY" \
      -H "Content-Type: application/json" \
      -d @"$rewired" "$N8N_API_URL/api/v1/workflows")
    if [ "$status" = "200" ] || [ "$status" = "201" ]; then
      echo "IMPORTED: $name" | tee -a "$LOG_DIR/import.log"
      ((imported++))
    else
      echo "FAIL: $name (HTTP $status)" | tee -a "$LOG_DIR/import.log"
      ((failed++))
    fi
  fi

  rm -f "$rewired"
done

echo "=== Summary ===" | tee -a "$LOG_DIR/import.log"
echo "Imported: $imported" | tee -a "$LOG_DIR/import.log"
echo "Updated: $updated" | tee -a "$LOG_DIR/import.log"
echo "Failed: $failed" | tee -a "$LOG_DIR/import.log"

[ "$failed" -eq 0 ] || exit 1
```

### Run
```bash
# Edge Functions
gh workflow run supabase-self-host-migration.yml \
  -f phase=functions -f mode=dry-run

# n8n Workflows (manual — not yet in CI)
N8N_API_KEY=$(az keyvault secret show --vault-name kv-ipai-dev \
  --name n8n-api-key --query value -o tsv)
N8N_API_URL=https://n8n-azure.insightpulseai.com \
  bash scripts/n8n/import_workflows.sh
```

---

## Phase 5: Consumer Cutover

### Existing Scripts
- `ops-platform/supabase/scripts/supabase_consumer_rewire.py`
- `ops-platform/supabase/scripts/supabase_cutover_verify.sh`
- `ops-platform/supabase/cutover/consumers.yaml` (8 consumers)

### Consumer Rewire Order (from consumers.yaml)

| Priority | Consumer | Type | Update Method |
|----------|----------|------|---------------|
| 1 | Edge Functions | Self-referencing | .env file on VM |
| 2 | n8n | Co-deployed | .env file on VM |
| 3 | Odoo (ipai-odoo-dev-web) | Container App | `az containerapp env set` |
| 4 | Auth (ipai-auth-dev) | Container App | `az containerapp env set` |
| 5 | MCP (ipai-mcp-dev) | Container App | `az containerapp env set` |
| 6 | OCR (ipai-ocr-dev) | Container App | `az containerapp env set` |
| 7 | GitHub Actions | CI secrets | `gh secret set` |
| 8 | Platform tools | TypeScript | `.env` update + redeploy |

### DNS Cutover (from cutover/dns.yaml)

| Record | Current | Target |
|--------|---------|--------|
| `supabase.insightpulseai.com` | Cloudflare proxy → VM nginx | Azure Front Door → VM |
| `n8n.insightpulseai.com` | Cloudflare proxy → VM nginx | Azure Front Door → VM |
| `n8n-azure.insightpulseai.com` | Direct to VM | Retire after Front Door |

### End-to-End Verification

```bash
# 1. Supabase health
curl -sf https://supabase.insightpulseai.com/rest/v1/ \
  -H "apikey: $SUPABASE_ANON_KEY" | jq .

# 2. Edge Function health
curl -sf https://supabase.insightpulseai.com/functions/v1/health

# 3. n8n health
curl -sf https://n8n-azure.insightpulseai.com/healthz

# 4. Odoo → Supabase connectivity
curl -sf https://erp.insightpulseai.com/web/health

# 5. n8n → Odoo workflow test
# Trigger health-check workflow via n8n API
curl -X POST "https://n8n-azure.insightpulseai.com/webhook/health-check" \
  -H "Content-Type: application/json" -d '{}'
```

### Run
```bash
gh workflow run supabase-self-host-migration.yml \
  -f phase=cutover -f mode=dry-run
```

---

## Execution Sequence (Full)

```
1. Phase 2: Schema    ──dry-run──► review diff ──execute──► verify parity
2. Phase 3: Data      ──dry-run──► review counts ──execute──► verify 1% tolerance
3. Phase 4a: Functions ──dry-run──► review manifest ──execute──► smoke tests
4. Phase 4b: n8n      ──dry-run──► review rewrites ──execute──► activate + test
5. Phase 5: Cutover   ──dry-run──► review consumer list ──execute──► e2e verify
6. Decommission cloud ──only after 7-day parallel run with no incidents
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Data loss during migration | pg_dump before AND after; verify row counts |
| n8n credential corruption | Export n8n credentials backup before import |
| Edge function cold start | Pre-warm critical functions after deploy |
| DNS propagation delay | Keep cloud running in parallel for 7 days |
| Sequence reset | Ensure `setval()` for all sequences after data import |
| Auth token invalidation | JWT secret must match between cloud and self-hosted |
| n8n encryption key loss | Key is in Azure Key Vault; backup separately |

---

## Missing Scripts (To Create)

| Script | Purpose | Priority |
|--------|---------|----------|
| `scripts/n8n/import_workflows.sh` | Import n8n workflows from repo JSON | P0 |
| `scripts/n8n/export_credentials.sh` | Backup n8n credentials before migration | P0 |
| `scripts/n8n/rewire_urls.sh` | Replace cloud URLs in workflow JSON | P0 |
| `scripts/supabase/seed_runner.sh` | Execute seeds in dependency order | P1 |
| `scripts/supabase/verify_sequences.sh` | Reset sequences after data import | P1 |
