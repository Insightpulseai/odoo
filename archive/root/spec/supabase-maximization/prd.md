# PRD — Supabase Maximization

**Spec bundle**: `spec/supabase-maximization/`
**Status**: Active — Phase 1 in progress
**Depends on**: `spec/supabase-auth-ssot/` (Auth already complete)
**Applied by**:
- `spec/odoo-receipt-digitization/` — Lane B CDC, Iceberg landing contract, Storage (Phase 2)
- Future: all new `ops.*`/`ai.*` feature specs (via T1 gate)

> For the full feature adoption map see:
> `docs/architecture/SUPABASE_FEATURES_INTEGRATIONS_ADOPTION.md`

---

## Problem

Supabase features are adopted ad-hoc: some tables lack RLS, some secrets live outside Vault,
some async jobs use cron scripts instead of Queues, and analytics queries hit Odoo Postgres
directly. This spec encodes the desired end-state as measurable acceptance criteria so future
work defaults to Supabase primitives without requiring per-PR judgment.

---

## Success Criteria by Tier

### Tier 1 (Required — must be complete before T2 merges)

| # | Criterion | Measure |
|---|-----------|---------|
| T1-1 | 100% RLS coverage on `ops.*` and `ai.*` schema tables | `scripts/ci/check_supabase_contract.sh` exits 0 |
| T1-2 | All server-readable secrets registered in `ssot/secrets/registry.yaml` (names, not values) | `grep -c 'name:' ssot/secrets/registry.yaml` ≥ count of secrets in Vault |
| T1-3 | Edge Functions deployed for all integration bridges (OCR policy, webhooks, Odoo sync) | `supabase functions list` shows all functions in `supabase/functions/` |
| T1-4 | All async jobs use PGMQ queues (no cron-script-based polling) | `grep -r 'schedule.*cron' .github/` shows only ETL worker health ping, not job dispatch |
| T1-5 | CLAUDE.md Secrets Policy updated with Vault-first rule + approved stores table | `grep "Vault-first" CLAUDE.md` returns match |

### Tier 2 (This cycle — Phase 2)

| # | Criterion | Measure |
|---|-----------|---------|
| T2-1 | Receipt images stored in Supabase Storage `receipts` bucket | `supabase storage ls receipts/` returns objects after first upload |
| T2-2 | Every Storage bucket has an RLS policy | `check_supabase_contract.sh` includes storage RLS check |
| T2-3 | CDC pipeline active: Odoo expense tables → Iceberg; lag < 60s | Iceberg snapshot timestamp within 60s of Odoo INSERT |
| T2-4 | Realtime subscription active for run progress events | WebSocket subscription to `ops.task_queue` changes works in ops console |
| T2-5 | `ir_attachment.datas` excluded from all Iceberg schema definitions | `grep -r 'datas' infra/supabase-etl/` → zero results |
| T2-6 | Analytics bucket `odoo-expense-etl` created; publication `odoo_expense_pub` wired to ETL worker | `supabase storage ls` lists bucket; ETL config `infra/supabase-etl/odoo-expense.toml` present |
| T2-7 | ETL pipeline health surfaced in `ops.run_events` (pipeline start/stop/error events emitted) | `SELECT event_type FROM ops.run_events WHERE source='etl_worker' LIMIT 1` returns row |
| T2-8 | DuckDB Iceberg smoke query passes in CI: row count > 0, event lag < 60 s | `scripts/ci/check_iceberg_etl_smoke.sh` exits 0 (PASS line in stdout); exits non-zero + prints FAIL reason on any of: row_count = 0, lag ≥ 60 s, Iceberg read error, or missing `ICEBERG_*` env vars. Step appears in `.github/workflows/supabase-etl-expense.yml` after ETL worker deploy. |

### Tier 3 (Phase 3)

| # | Criterion | Measure |
|---|-----------|---------|
| T3-1 | pgvector index created for receipt OCR text embeddings | `\d ai.receipt_embeddings` shows `USING ivfflat` index |
| T3-2 | MCP server can query Supabase schema for agent operations | `mcp/servers/supabase/` server starts; schema queries return results |
| T3-3 | RAG pipeline for runbooks + specs wired to pgvector | `supabase/functions/embed-chunk-worker/` deploys without error |

### Tier 4 (Future capability)

| # | Criterion | Measure |
|---|-----------|---------|
| T4-1 | Supabase Branching in CI for schema experiments | PR workflow creates branch DB; migration tested on branch before main merge |
| T4-2 | Log Drains wired to observability backend | Edge Function logs appear in `infra/observability/supabase/` pipeline |

---

## Out of Scope

- Auth implementation (already in `spec/supabase-auth-ssot/`)
- New Odoo modules (feature-specific specs handle those)
- Supabase paid-tier features not already provisioned
- Migration of existing tables to RLS (separate remediation task)
