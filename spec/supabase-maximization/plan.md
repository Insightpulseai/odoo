# Plan — Supabase Maximization

**Spec bundle**: `spec/supabase-maximization/`
**Implements**: `prd.md`

---

## Phase Overview

| Phase | Scope | Status |
|-------|-------|--------|
| Phase 0 | Foundations (queues, ops tables, RLS baselines, Auth SSOT, receipt digitization) | ✅ Done |
| Phase 1 | SSOT docs + spec + secrets policy update (this PR) | 🔄 In progress |
| Phase 2 | Storage, Realtime, Vault refs for OCR/S3 creds, CDC pipeline | 📋 Planned |
| Phase 3 | Vector index for receipts, MCP server wiring, Iceberg analytics activation | 📋 Planned |
| Phase 4 | Branching in CI, Log Drains | 📋 Future |

---

## Phase 0 — Foundations (Done)

Already committed to `main`:

| Artifact | What was done |
|----------|---------------|
| `supabase/migrations/*_queues*.sql` | PGMQ queues provisioned |
| `supabase/migrations/*_ops_*.sql` | `ops.*` schema tables with RLS |
| `spec/supabase-auth-ssot/` | Full Auth SSOT spec (IdP for non-Odoo surfaces) |
| `addons/ipai/ipai_expense_ocr/` | Receipt digitization Lane A (OCR auto-fill) |
| `infra/supabase-etl/odoo-expense.toml` | Lane B CDC config (expense → Iceberg) |

---

## Phase 1 — SSOT Docs + Policy (This PR)

All docs/spec/policy — no new code, no new migrations.

### 1.1 CLAUDE.md Secrets Policy expansion
Replace the 5-bullet policy with:
- Approved stores table (Vault / GitHub Secrets / Keychain)
- Vault-first rule
- "Pasted once ≠ exposed" note
- Retain existing 3 "Never" bullets

### 1.2 Architecture doc: SUPABASE_FEATURES_INTEGRATIONS_ADOPTION.md
Create `docs/architecture/SUPABASE_FEATURES_INTEGRATIONS_ADOPTION.md`:
- Feature adoption Tiers table (T1–T4) with SSOT locations + CI gates
- Integration selection rubric (Buy vs Build)
- Odoo ↔ Supabase boundary diagram (text)
- Adopted integrations table (Vercel, Cloudflare, n8n)
- Secrets placement cross-reference
- Phase gating rules

### 1.3 Spec bundle: spec/supabase-maximization/
Create 4-file spec bundle:
- `constitution.md` — 8 non-negotiable rules
- `prd.md` — success criteria per Tier (T1–T4)
- `plan.md` — this file; phased rollout
- `tasks.md` — Phase 1 enforcement tasks

### 1.4 Receipt digitization spec upgrades
Add to `spec/odoo-receipt-digitization/`:
- `plan.md` — Supabase feature adoption table + Iceberg landing contract
- `prd.md` — Supabase/Infrastructure acceptance criteria block
- `tasks.md` — tasks 2.9–2.11 (env var registry, no-plaintext lint, datas exclusion check)

---

## Phase 2 — Storage + Realtime + Vault Refs

> Depends on: Phase 1 complete + T1 acceptance criteria green

### 2.1 Supabase Storage bucket for receipts
```
supabase/storage/receipts/
├── bucket.sql          — bucket creation + RLS policy
└── policies.sql        — select/insert/delete policies per role
```
Update `ipai_expense_ocr`: after OCR succeeds, upload image to `receipts/` bucket;
store returned URL in `ir_attachment.store_url` (not `datas`).

### 2.2 Vault references for OCR + S3 credentials
Register in `ssot/secrets/registry.yaml`:
- `ipai_ocr_endpoint_url` — OCR service URL (currently `ir.config_parameter`)
- `iceberg_access_key_id` — S3/DO Spaces key
- `iceberg_secret_access_key` — S3/DO Spaces secret
Edge Functions read from `Deno.env.get('ipai_ocr_endpoint_url')` via Vault injection.

### 2.3 Realtime subscription for run progress
Add `ops.task_queue` Realtime publication in `supabase/config.toml`:
```toml
[realtime]
enabled = true
[realtime.tables.ops_task_queue]
schema = "ops"
table = "task_queue"
filter = "status=neq.done"
```
Ops console subscribes to channel for live run progress UI.

### 2.4 CDC pipeline activation
Activate Supabase ETL worker on DO App Platform using `infra/supabase-etl/odoo-expense.toml`.
CI workflow: `.github/workflows/supabase-etl-expense.yml` (already in tasks.md 2.7).

### 2.5 Analytics Plane — ETL → Iceberg landing

> Ref: `docs/architecture/SUPABASE_FEATURES_INTEGRATIONS_ADOPTION.md §Analytics Plane`

**EL-only constraint**: No transforms in the ETL worker. All transformations happen downstream
(DuckDB queries, dbt-style views, or Superset SQL).

**Bucket naming**: `odoo-<domain>-etl` (e.g. `odoo-expense-etl`). Future ETL publications follow
this convention.

**Schema evolution rules** (additive only):
- New nullable columns: allowed
- Column rename / type change: requires new table version (`expense_v2`, etc.)
- Binary columns (`ir_attachment.datas`): excluded from all Iceberg schemas — pointer-only pattern

**DuckDB Iceberg query workflow**:
```sql
-- CI smoke query (run after ETL worker deploy)
INSTALL iceberg; LOAD iceberg;
SELECT count(*) AS row_count, max(_sdc_received_at) AS latest_event
FROM iceberg_scan('s3://ICEBERG_WAREHOUSE/odoo_ops/expense/');
-- Asserts: row_count > 0 AND latest_event > now() - INTERVAL '60 seconds'
```

SSOT for this script: `scripts/ci/check_iceberg_etl_smoke.sh`

**Pipeline health events**: ETL worker emits `pipeline.start`, `pipeline.stop`, `pipeline.error`
events to `ops.run_events` via Edge Function `webhook-ingest`. Enables Realtime dashboard and
alerting without polling the Iceberg warehouse.

---

## Phase 3 — Vector + MCP

> Depends on: Phase 2 complete

### 3.1 pgvector index for receipts
Migration: `supabase/migrations/*_receipt_embeddings.sql`
- Table `ai.receipt_embeddings(id, expense_id, embedding vector(1536), created_at)`
- `USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)`
Edge Function `embed-chunk-worker` (already exists) updated to process OCR text.

### 3.2 MCP server wiring
`mcp/servers/supabase/` server configuration for:
- Schema introspection queries
- Controlled `ops.*` table reads for agent workflows
- No write access to Odoo-owned tables

---

## Phase 4 — Branching + Log Drains (Future)

- Supabase Branching: add branch creation step to PR workflow
- Log Drains: wire Edge Function + DB logs to `infra/observability/supabase/` pipeline

---

## Cross-References

| Artifact | Purpose |
|----------|---------|
| `docs/architecture/SUPABASE_FEATURES_INTEGRATIONS_ADOPTION.md` | Feature adoption Tiers + integration rubric |
| `spec/supabase-auth-ssot/` | Auth SSOT (not duplicated here) |
| `docs/ops/SUPABASE_SSOT.md` | DB-first model + operational details |
| `docs/architecture/SSOT_BOUNDARIES.md` | Ownership boundaries |
| `ssot/secrets/registry.yaml` | Secret name registry (Vault-first) |
