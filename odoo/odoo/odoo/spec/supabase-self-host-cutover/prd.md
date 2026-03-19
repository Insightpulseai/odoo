# PRD: Supabase Cloud-to-Self-Hosted Migration

> Product requirements for migrating from managed Supabase (`spdtwktxdalcfigzeqrz`)
> to self-hosted Supabase on Azure VM `vm-ipai-supabase-dev` (4.193.100.31).

---

## 1. Objective

Migrate all data, schema, Edge Functions, and consumer bindings from Supabase managed cloud to a self-hosted Supabase instance running on Azure infrastructure. Achieve zero data loss and minimal consumer downtime during cutover.

---

## 2. Current State

| Component | Status |
|-----------|--------|
| Cloud project `spdtwktxdalcfigzeqrz` | Active, serving all consumers |
| Self-hosted VM `vm-ipai-supabase-dev` | Phase 1 complete, 14 containers running |
| Docker Compose | `/opt/supabase-deploy/` (official `supabase/docker`) |
| PostgreSQL | Cloud: managed. Self-hosted: 15.8 (container) |
| Edge Functions | 39 defined in repo (`supabase/supabase/functions/`) |
| Migrations | ~150 SQL files in `supabase/migrations/` |
| Secrets | Azure Key Vault `kv-ipai-dev` (39 secrets) |
| DNS | `supabase.insightpulseai.com` pending creation |

### Consumers

| Consumer | Integration Type | Priority |
|----------|-----------------|----------|
| n8n | REST API, webhooks | P0 |
| Odoo (`ipai_*` modules) | REST API (PostgREST) | P0 |
| Web apps (Next.js) | `@supabase/supabase-js` client | P0 |
| MCP jobs | Edge Function invocation | P1 |
| Slack integrations | Webhook-triggered Edge Functions | P1 |
| GitHub App | Edge Functions (`github-app-auth`) | P1 |

---

## 3. Phase Overview

| Phase | Name | Prerequisites | Deliverable |
|-------|------|---------------|-------------|
| 1 | Infrastructure | None | 14 containers running (COMPLETE) |
| 2 | Schema Migration | Phase 1 | Schema parity verified |
| 3 | Data Migration | Phase 2 | Data parity verified |
| 4 | Edge Functions | Phase 2 | All 39 functions deployed and responding |
| 5 | Cutover | Phases 3 + 4 | All consumers on self-hosted |

---

## 4. Phase 2: Schema Migration

### Requirements

- Export complete schema from cloud project including all custom schemas (`public`, `auth`, `storage`, `realtime`, `ops`, `extensions`)
- Verify extension parity between cloud and self-hosted (critical: `pgvector`, `pgjwt`, `pg_graphql`, `pg_cron`, `pg_net`, `pgsodium`, `supautils`)
- Apply repo migrations (`supabase/migrations/`) to self-hosted in chronological order
- Verify RLS policies are applied and match cloud

### Acceptance Criteria

- [ ] All extensions present on cloud are enabled on self-hosted
- [ ] All tables exist with matching columns, types, and constraints
- [ ] All RLS policies match (name, table, command, expression)
- [ ] All custom functions/triggers exist
- [ ] Schema parity report emitted as `schema-parity.json`

### Verification Gate

```
schema_parity.tables == MATCH
schema_parity.extensions == MATCH
schema_parity.rls_policies == MATCH
schema_parity.functions == MATCH
```

### Rollback

Drop all schemas on self-hosted and re-apply from clean state. Self-hosted is disposable at this phase.

---

## 5. Phase 3: Data Migration

### Requirements

- Export data from cloud using `pg_dump --data-only`
- Import to self-hosted using `pg_restore`
- Exclude ephemeral/session data (Realtime presence, analytics short-term)
- Verify row-count parity on all tables
- Deep verification on critical tables

### Critical Tables

| Table | Schema | Verification |
|-------|--------|-------------|
| `auth.users` | auth | Row count + email uniqueness check |
| `auth.identities` | auth | Row count + FK integrity |
| `platform_events` | public | Row count + latest timestamp check |
| `ops.task_queue` | ops | Row count + status distribution match |
| `ops.platform_events` | ops | Row count + append-only integrity (max ID match) |
| `storage.objects` | storage | Row count + bucket distribution match |
| `storage.buckets` | storage | Exact match |

### Acceptance Criteria

- [ ] Row counts match within tolerance (0 for critical tables, <0.1% for non-critical)
- [ ] Critical table checksums match
- [ ] Foreign key integrity verified post-import
- [ ] No orphaned records in junction tables
- [ ] `row-counts.json` emitted with per-table comparison

### Verification Gate

```
data_parity.critical_tables == EXACT_MATCH
data_parity.all_tables.max_drift < 0.001
data_parity.fk_integrity == PASS
```

### Rollback

Truncate all data on self-hosted and re-import. Cloud data is untouched.

---

## 6. Phase 4: Edge Functions

### Requirements

- Deploy all 39 Edge Functions from `supabase/supabase/functions/` to self-hosted edge-runtime
- Configure function environment variables from Key Vault
- Verify each function endpoint returns a non-error response
- Test critical function paths end-to-end

### 39 Edge Functions

```
auth-bootstrap          auth-otp-request        auth-otp-verify
bugbot-control-plane    catalog-sync            config-publish
consumer-heartbeat      context-resolve         copilot-chat
cron-processor          docs-ai-ask             executor
expense-policy-check    github-app-auth         infra-memory-ingest
ipai-copilot            marketplace-webhook     mcp-gateway
memory-ingest           odoo-template-export    odoo-webhook
ops-health              ops-ingest              ops-job-worker
ops-summary             realtime-sync           schema-changed
seed-odoo-finance       semantic-export-osi     semantic-import-osi
semantic-query          serve-erd               shadow-odoo-finance
skill-eval              sync-kb-to-schema       sync-odoo-modules
tenant-invite           three-way-match         vendor-score
```

### Critical Function Paths

| Path | Functions Involved | Test |
|------|-------------------|------|
| Auth flow | `auth-bootstrap`, `auth-otp-request`, `auth-otp-verify` | OTP request returns 200 |
| Ops pipeline | `ops-health`, `ops-ingest`, `ops-job-worker`, `ops-summary` | Health check returns status |
| Odoo integration | `odoo-webhook`, `odoo-template-export`, `sync-odoo-modules` | Webhook accepts POST |
| MCP gateway | `mcp-gateway`, `executor`, `context-resolve` | Gateway returns capability list |
| Semantic layer | `semantic-query`, `semantic-export-osi`, `semantic-import-osi` | Query returns schema |

### Acceptance Criteria

- [ ] All 39 functions deployed without errors
- [ ] All 39 function endpoints return HTTP 200 or expected status on health probe
- [ ] Critical function paths pass end-to-end tests
- [ ] Function-to-DB connectivity verified (functions can query PostgREST)
- [ ] `function-health.json` emitted with per-function status

### Verification Gate

```
functions.deployed == 39
functions.healthy == 39
functions.critical_paths == ALL_PASS
```

### Rollback

Functions are stateless. Redeploy or remove. No data risk.

---

## 7. Phase 5: Cutover

### Requirements

- Create DNS records: `supabase.insightpulseai.com` via Cloudflare DNS-only, routed through Azure Front Door to VM origin (4.193.100.31)
- Rewire all consumers in manifest order with per-consumer smoke tests
- Run 30-day parallel period where cloud remains available as fallback
- Execute final cutover gate before cloud decommission

### Consumer Rewire Order

1. **n8n** (internal, lowest blast radius for testing)
2. **MCP jobs** (internal, batch-tolerant)
3. **Odoo modules** (internal, session-based)
4. **Slack integrations** (external-facing, webhook-based)
5. **GitHub App** (external-facing)
6. **Web apps** (external-facing, highest user visibility -- last)

### DNS Architecture

```
Client -> Cloudflare (DNS-only, no proxy) -> Azure Front Door (ipai-fd-dev)
  -> Origin: vm-ipai-supabase-dev (4.193.100.31)
    -> Kong (port 8000) -> PostgREST / GoTrue / Edge-Runtime / Storage
```

### Acceptance Criteria

- [ ] DNS resolves `supabase.insightpulseai.com` to Azure Front Door
- [ ] TLS terminates correctly at Front Door
- [ ] All consumers pass smoke tests against self-hosted
- [ ] 30-day parallel run completes with zero critical incidents
- [ ] Final cutover readiness report emitted
- [ ] Cloud project frozen (read-only)
- [ ] Cloud project decommissioned (after 30-day hold)

### Verification Gate

```
dns.resolution == CORRECT
tls.valid == true
consumers.all_smoke_tests == PASS
parallel_run.critical_incidents == 0
cutover_readiness == APPROVED
```

### Rollback

Revert DNS to cloud endpoints. Consumer configs reference cloud URLs. Instant rollback.

---

## 8. Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Data loss during migration | Low | Critical | Checksums, row counts, cloud untouched until cutover |
| Consumer downtime during rewire | Medium | High | Per-consumer smoke tests, rollback-ready DNS |
| Edge Function incompatibility | Medium | Medium | Deploy from repo (tested), not cloud export |
| DNS propagation delay | Low | Medium | Low TTL (60s) set before cutover |
| Extension version mismatch | Low | High | Extension parity check in Phase 2 gate |
| Storage bucket data loss | Low | Critical | Separate storage migration with object-level verification |
| Auth token invalidation | Medium | High | JWT secret parity, session migration plan |

---

## 9. Success Metrics

| Metric | Target |
|--------|--------|
| Data loss | Zero |
| Consumer downtime | < 5 minutes per consumer during rewire |
| Edge Function availability | 39/39 healthy post-migration |
| Schema drift | Zero tables/columns missing |
| Time to rollback | < 2 minutes (DNS revert) |
| Parallel run incidents | Zero critical |

---

*Spec bundle: supabase-self-host-cutover | Created: 2026-03-14*
