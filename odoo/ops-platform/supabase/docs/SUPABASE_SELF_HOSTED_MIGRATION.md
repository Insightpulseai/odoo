# Supabase Self-Hosted Migration

**Scope**: Migrate Supabase cloud project `spdtwktxdalcfigzeqrz` to a self-hosted instance
on Azure VM `vm-ipai-supabase-dev` (4.193.100.31), running Docker Compose under
`/opt/supabase-deploy/`. Includes 39 Edge Functions, all platform consumers, and DNS cutover.

---

## 1. Overview

InsightPulse AI runs Supabase as the task bus, AI/vector store, auth provider, and
real-time layer shared across Odoo, n8n, web apps, MCP server, GitHub Actions CI,
and Slack agents. The migration moves this from Supabase cloud to a self-hosted
instance on a dedicated Azure VM to reduce cost and eliminate cloud-tier limits on
Edge Function invocations, database connections, and storage.

The cloud project remains active during migration and is decommissioned only after
a 30-day parallel monitoring period confirms the self-hosted instance is stable.

---

## 2. System Topology

### Before Migration

```
Consumers → https://spdtwktxdalcfigzeqrz.supabase.co (Supabase Cloud)
                            |
                    Supabase Cloud (managed)
                    - Auth, REST, Storage, Realtime
                    - 39 Edge Functions (Deno Deploy)
                    - PostgreSQL (managed)
```

### After Migration

```
Consumers → https://supabase.insightpulseai.com
                            |
               Cloudflare Proxy (TLS, WAF, CDN)
                            |
              Azure VM: vm-ipai-supabase-dev (4.193.100.31)
                            |
              nginx (reverse proxy :80/:443 → :8000)
                            |
              Docker Compose: /opt/supabase-deploy/
              ├── Kong API Gateway  (:8000)
              ├── GoTrue Auth       (:9999)
              ├── PostgREST         (:3000)
              ├── Realtime          (:4000)
              ├── Storage           (:5000)
              ├── Edge Functions    (:9090) ← 39 functions rsync'd from repo
              ├── PostgreSQL 16     (:5432)
              └── n8n               (:5678) ← co-deployed
```

### Consumer Map

| Consumer | Update method | Priority |
|---|---|---|
| Edge Functions (self) | env_file on VM | 1 |
| n8n | env_file on VM | 2 |
| ipai-odoo-dev-web/worker/cron | az containerapp | 3 |
| ipai-mcp-dev | az containerapp | 4 |
| ipai-website-dev, ipai-crm-dev | az containerapp | 5 |
| ops-console | az containerapp | 6 |
| slack-agent-app | az containerapp | 7 |
| GitHub Actions | gh secret | 10 |

Full details: `ops-platform/supabase/cutover/consumers.yaml`

---

## 3. Phase Gates and Acceptance Criteria

```
Phase 1 (DONE)    Phase 2 (Schema)    Phase 3 (Data)    Phase 4 (Functions)    Phase 5 (Cutover)
Infrastructure  →  Export cloud     →  Migrate rows   →  Deploy 39 fns       →  Rewire all
provisioned        schema to VM        to self-hosted     to VM + smoke           consumers +
                   + diff report       PostgreSQL         test all tiers          verify DNS
                   │                   │                  │                       │
                   gate:               gate:              gate:                   gate:
                   0 table             row count          12/12 critical          all consumer
                   mismatches          within 1%          fns healthy             smoke tests
                   in diff report      tolerance          + 18/22 standard        pass + DNS
                                                          fns healthy             resolves
```

### Phase 1: Infrastructure (DONE)
- VM provisioned in Azure (rg-ipai-dev, southeastasia)
- Docker Compose stack deployed at /opt/supabase-deploy/
- nginx configured with reverse proxy vhosts
- PostgreSQL initialized with Supabase schema baseline
- Gate: `curl -sf http://localhost:8000/rest/v1/` returns 200 from VM

### Phase 2: Schema Export
- Export cloud project DDL using `supabase db dump`
- Apply to self-hosted PostgreSQL
- Run schema diff: 0 missing tables, 0 missing columns, 0 missing indexes
- Gate: parity report file contains `SCHEMA_PARITY: PASS`
- Evidence: `docs/evidence/<run_id>/schema/`

### Phase 3: Data Migration
- pg_dump from cloud (or Supabase backups API) + pg_restore to self-hosted
- Row count comparison per table, tolerance 1%
- pgvector embeddings included (vector columns transfer as binary)
- Gate: `DATA_PARITY: PASS` in data.log
- Evidence: `docs/evidence/<run_id>/data/`

### Phase 4: Edge Functions Deploy
- rsync `supabase/functions/` to `/opt/supabase-deploy/volumes/functions/`
- Restart supabase-edge container
- Smoke test all 39 functions via `https://supabase.insightpulseai.com/functions/v1/<name>`
- Gate: 12/12 critical functions return non-5xx; 18/22 standard functions return non-5xx
- Evidence: `docs/evidence/<run_id>/functions/`

### Phase 5: Cutover
- Create DNS A records: supabase.insightpulseai.com → 4.193.100.31
- Rewire all consumers in priority order (1 → 10)
- Run full consumer smoke test suite
- Gate: all consumer smoke tests pass; DNS resolves correctly via dig
- Evidence: `docs/evidence/<run_id>/cutover/`

---

## 4. Script Inventory

All scripts live under `ops-platform/supabase/scripts/`.

| Script | Phase | Description | Usage |
|---|---|---|---|
| `supabase_cloud_inventory.py` | 1 | Audit cloud project state | `python ... --project-id <id> --mode dry-run` |
| `supabase_schema_export.sh` | 2 | Export DDL, apply to VM, diff | `bash ... --mode execute --cloud-project <id>` |
| `supabase_data_migrate.sh` | 3 | pg_dump/restore + row count check | `bash ... --mode dry-run` |
| `supabase_edge_functions_sync.sh` | 4 | rsync functions, restart, smoke test | `bash ... --function auth-bootstrap` |
| `supabase_consumer_rewire.py` | 5 | Update env vars per consumer manifest | `python ... --mode dry-run --rollback` |
| `supabase_cutover_verify.sh` | 5/any | Full verification suite | `bash ... --phase dns-post` |

### Usage Examples

Dry-run full cutover phase:
```bash
python ops-platform/supabase/scripts/supabase_consumer_rewire.py \
  --mode dry-run \
  --manifest ops-platform/supabase/cutover/consumers.yaml \
  --self-hosted-url https://supabase.insightpulseai.com
```

Deploy single edge function:
```bash
bash ops-platform/supabase/scripts/supabase_edge_functions_sync.sh \
  --mode execute \
  --function ops-health \
  --vm-host 4.193.100.31 \
  --vm-user azureuser \
  --ssh-key ~/.ssh/vm_ipai_key
```

Run verification only:
```bash
bash ops-platform/supabase/scripts/supabase_cutover_verify.sh \
  --self-hosted-url https://supabase.insightpulseai.com \
  --manifest ops-platform/supabase/cutover/consumers.yaml
```

Rollback all consumers to cloud:
```bash
python ops-platform/supabase/scripts/supabase_consumer_rewire.py \
  --mode execute \
  --rollback \
  --manifest ops-platform/supabase/cutover/consumers.yaml
```

---

## 5. Evidence Output Paths

All pipeline runs write evidence to `docs/evidence/<github_run_id>/`.
Long-term evidence is committed to `docs/evidence/migrations/supabase-selfhost/`.

```
docs/evidence/<run_id>/
├── inventory/
│   ├── inventory.log
│   ├── cloud_tables.json
│   ├── cloud_functions.json
│   └── cloud_storage_buckets.json
├── schema/
│   ├── schema.log
│   ├── cloud_schema.sql
│   ├── selfhosted_schema.sql
│   └── schema_diff.txt
├── data/
│   ├── data.log
│   ├── row_counts_cloud.csv
│   ├── row_counts_selfhosted.csv
│   └── row_count_diff.csv
├── functions/
│   ├── functions.log
│   ├── smoke_test_results.json
│   └── unhealthy_functions.txt
└── cutover/
    ├── rewire.log
    ├── verify.log
    ├── consumer_smoke_tests.json
    └── dns_check.txt
```

---

## 6. Rollback Procedures

### Phase 2 Rollback (Schema)
No production impact. Schema was applied to self-hosted only.
Action: Drop and recreate self-hosted PostgreSQL if schema is corrupt.
```bash
ssh azureuser@4.193.100.31 'cd /opt/supabase-deploy && sudo docker compose down -v && sudo docker compose up -d'
```

### Phase 3 Rollback (Data)
No production impact. Data was migrated to self-hosted only; cloud is unchanged.
Action: pg_dump again from cloud after fixing any schema issues.

### Phase 4 Rollback (Edge Functions)
No production impact. Functions were deployed to self-hosted only; cloud functions unchanged.
Action: Remove/revert files in `/opt/supabase-deploy/volumes/functions/` and restart edge container.

### Phase 5 Rollback (Cutover)
This is the only phase with production impact. Rollback must be fast.

Step 1: Revert all consumers to cloud URL.
```bash
python ops-platform/supabase/scripts/supabase_consumer_rewire.py \
  --mode execute \
  --rollback \
  --manifest ops-platform/supabase/cutover/consumers.yaml
```

Step 2: Delete Cloudflare DNS A records (or change target back to nothing).
```bash
cf api DELETE /zones/73f587aee652fc24fd643aec00dcca81/dns_records/<record_id>
```

Step 3: Verify cloud consumers are healthy.
```bash
curl -sf https://spdtwktxdalcfigzeqrz.supabase.co/rest/v1/ -H "apikey: $SUPABASE_ANON_KEY"
```

Low TTL (300s) means DNS rollback propagates within 5 minutes.
Consumer env var rewire via Azure Container Apps takes 2-3 minutes per app.
Total rollback time: under 15 minutes.

---

## 7. Consumer Manifest Explained

`ops-platform/supabase/cutover/consumers.yaml` is the authoritative list of all
services that hold a reference to the Supabase URL or API keys.

Each entry declares:
- `name`: Identifier matching the Azure Container App name, n8n, or github-actions
- `type`: `container_app`, `co_deployed`, `self_referencing`, or `github_secrets`
- `env_vars`: Which variables must be updated
- `update_method`: How to apply the update (`az_containerapp`, `env_file`, `gh_secret`)
- `secret_source`: Azure Key Vault for ACA consumers (secrets passed as secretRefs)
- `smoke_test`: Verification command to confirm consumer is healthy post-rewire
- `priority`: Rewire order (lower = earlier)

The `supabase_consumer_rewire.py` script reads this manifest and executes updates
in priority order, running each consumer's smoke test before advancing to the next.
If a smoke test fails, the script halts and outputs the failing consumer name.

---

## 8. Edge Function Deploy Model

### Source Location
Functions live at `supabase/functions/<name>/index.ts` in this repo.

### Deploy Method
1. `rsync -avz --delete supabase/functions/ azureuser@4.193.100.31:/opt/supabase-deploy/volumes/functions/`
2. `ssh ... 'cd /opt/supabase-deploy && sudo docker compose restart supabase-edge'`
3. Wait 10 seconds for Deno runtime to initialize.
4. Run smoke tests from `ops-platform/supabase/edge-functions/deploy/manifest.yaml`.

### Tier Model
- **critical** (12 functions): auth, ops, odoo-webhook, github-app-auth, mcp-gateway, bugbot-control-plane, realtime-sync. All 12 must be healthy to open cutover gate.
- **standard** (23 functions): copilot, semantic, sync, config, cron, executor, memory, finance, analytics. 18/23 must be healthy.
- **optional** (4 functions): serve-erd, skill-eval, marketplace-webhook, tenant-invite. No gate.

### Single Function Deploy
The GitHub Actions workflow accepts `target_function` input to deploy a single function
without touching the others. Useful for hotfixes post-cutover.

### Secret Injection
Functions read secrets via `Deno.env.get()`. Secrets are injected at container startup
from `/opt/supabase-deploy/.env`. This file is populated by `supabase_consumer_rewire.py`
during Phase 5 and is never committed to git.

---

## 9. DNS Cutover Procedure

Full DNS manifest: `ops-platform/supabase/cutover/dns.yaml`

### Pre-conditions
- VM nginx is running with vhosts for `supabase.insightpulseai.com` and `n8n-azure.insightpulseai.com`
- Kong responds on `localhost:8000` from within the VM
- Cloudflare SSL mode is set to Full or Full(strict) for `insightpulseai.com`

### Record Creation
```bash
# Create supabase A record via Cloudflare API
cf api POST /zones/73f587aee652fc24fd643aec00dcca81/dns_records \
  --field type=A \
  --field name=supabase \
  --field content=4.193.100.31 \
  --field proxied=true \
  --field ttl=300

# Create n8n-azure A record
cf api POST /zones/73f587aee652fc24fd643aec00dcca81/dns_records \
  --field type=A \
  --field name=n8n-azure \
  --field content=4.193.100.31 \
  --field proxied=true \
  --field ttl=300
```

### Post-cutover Verification
```bash
# DNS resolves
dig +short supabase.insightpulseai.com @1.1.1.1

# Supabase endpoints healthy
curl -sf https://supabase.insightpulseai.com/auth/v1/health
curl -sf https://supabase.insightpulseai.com/rest/v1/ -H "apikey: $SUPABASE_ANON_KEY"
curl -sf https://supabase.insightpulseai.com/storage/v1/health
curl -sf https://supabase.insightpulseai.com/functions/v1/ops-health

# n8n healthy
curl -sf https://n8n-azure.insightpulseai.com/healthz
```

---

## 10. 30-Day Parallel Run Monitoring

After cutover, the cloud project remains active for 30 days as a fallback.
No new writes go to cloud after cutover; it is read-only backup.

### Monitoring Checklist (daily for first 7 days, weekly thereafter)

| Check | Command | Expected |
|---|---|---|
| Supabase API health | `curl -sf https://supabase.insightpulseai.com/functions/v1/ops-health` | HTTP 200 |
| Auth health | `curl -sf https://supabase.insightpulseai.com/auth/v1/health` | `{"status":"ok"}` |
| n8n health | `curl -sf https://n8n-azure.insightpulseai.com/healthz` | HTTP 200 |
| Odoo ERP health | `curl -sf https://erp.insightpulseai.com/web/health` | HTTP 200 |
| Edge Function error rate | Check Deno logs on VM | < 1% 5xx rate |
| PostgreSQL connection count | `ssh ... 'psql -c "SELECT count(*) FROM pg_stat_activity"'` | < 80% of max_connections |
| Disk usage | `ssh ... 'df -h /opt/supabase-deploy'` | < 80% full |
| VM memory | `ssh ... 'free -h'` | < 85% used |

### Alert Thresholds (configure in ops-console or Azure Monitor)
- ops-health returning non-200: page immediately
- Edge Function 5xx rate > 5% sustained 5 minutes: alert
- PostgreSQL connection count > 80 (assuming max_connections=100): alert
- VM disk > 80%: alert
- VM memory > 90%: alert

### 30-Day Sign-off Criteria
All of the following must be true before cloud decommission:
- Zero P1/P0 incidents caused by self-hosted instance
- Edge Function error rate < 0.5% over 7-day rolling window
- No consumer rollback events in final 14 days
- All 39 functions passing daily smoke tests
- Database row counts stable (no unexplained divergence)
- Monitoring alerts configured and validated (tested with synthetic failure)

---

## 11. Final Decommission Checklist

Execute only after 30-day parallel run passes sign-off.

- [ ] Export final pg_dump backup from cloud project (keep for 90 days in Azure Blob)
- [ ] Export all cloud Edge Function source (already in repo — confirm no drift)
- [ ] Export Supabase Vault secrets to Azure Key Vault (if any not already mirrored)
- [ ] Download all storage bucket objects to Azure Blob or self-hosted storage
- [ ] Rotate all cloud API keys (anon, service_role) to prevent accidental use post-decommission
- [ ] Delete cloud Edge Functions
- [ ] Delete cloud project (Supabase dashboard or CLI: `supabase projects delete spdtwktxdalcfigzeqrz`)
- [ ] Remove cloud SUPABASE_URL from GitHub Actions secrets (replaced by self-hosted URL)
- [ ] Update `CLAUDE.md` Supabase project ID reference
- [ ] Update `infra/ssot/azure/service-matrix.yaml` to remove cloud project entry
- [ ] Close migration tracking issue in GitHub

---

## 12. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| VM disk fills during data migration | Medium | High | Pre-allocate 100GB+ for data volume; monitor during Phase 3 |
| pgvector extension not installed on self-hosted PostgreSQL | Low | High | Verify `CREATE EXTENSION vector` before Phase 3; include in Phase 2 gate |
| n8n workflows fail after SUPABASE_URL change | Medium | Medium | Test 5 critical n8n workflows in dry-run mode before executing rewire |
| Cloudflare proxy caches stale auth tokens | Low | Medium | Set CF cache rules to bypass for /auth/v1/* paths |
| Azure Container App secret update causes brief restart | Low | Low | Rewire during low-traffic window (UTC+8 03:00-05:00) |
| Edge Function cold start latency increases | Low | Low | Self-hosted Deno starts are comparable; warm after first invocation |
| Cloud project billing continues if not deleted | Medium | Low | Set billing alert on cloud project; delete within 30 days of sign-off |
| SSH key rotation breaks VM access mid-migration | Low | Critical | Store VM SSH key in Key Vault; rotate only after migration completes |
| Cloudflare SSL cert not issued before consumers switch | Low | High | Create DNS record 24 hours before consumer rewire to allow cert provisioning |
| Database max_connections exceeded under full load | Medium | High | Set `max_connections=200` in PostgreSQL config; connection pooling via pgBouncer |

---

*Migration owner: InsightPulse AI Platform Engineering*
*Last updated: 2026-03-14*
*Cloud project: spdtwktxdalcfigzeqrz*
*Self-hosted VM: vm-ipai-supabase-dev (4.193.100.31)*
