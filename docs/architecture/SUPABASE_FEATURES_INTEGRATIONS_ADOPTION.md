# Supabase Features + Integrations — Adoption Map

> **Cross-references**:
> - `docs/architecture/SSOT_BOUNDARIES.md` — ownership boundaries
> - `docs/ops/SUPABASE_SSOT.md` — DB-first model
> - `spec/supabase-maximization/` — full spec bundle with phased rollout
> - `spec/supabase-auth-ssot/` — Auth SSOT (already fully specced)

This doc answers "where does X go?" for Supabase features and integrations.
It is the opinionated decision table — do not re-narrate the SSOT docs above; cross-link to them.

---

## Four-Plane Architecture

Supabase primitives map to four distinct planes in this stack:

| Plane | Purpose | Key primitives |
|-------|---------|---------------|
| **Control** | Ops/SSOT — runs, deployments, policy gates, runtime registry, audit trail | Postgres `ops.*`, Edge Functions, Vault, Auth |
| **Data** | Product DB — read models for apps, RLS-gated tables, RPCs | Postgres + RLS, RPCs, Realtime subscriptions |
| **Event** | Automation + status streaming | Queues (PGMQ), Realtime, Cron |
| **Analytics** | Warehouse-grade queries; downstream BI/AI consumers | ETL replication → Analytics Buckets (Iceberg) |

The four planes map to the receipt digitization lanes:
- **Lane A** (OCR auto-fill) → Control + Data planes
- **Lane B** (CDC → Iceberg) → Analytics plane

---

## Feature Adoption Tiers

| Tier | Feature | Concrete use in this repo | SSOT location | CI gate |
|------|---------|--------------------------|---------------|---------|
| T1 | Postgres + RLS + RBAC | Every `ops.*`/`ai.*` table; no table without RLS | `supabase/migrations/` | `scripts/ci/check_supabase_contract.sh` RLS gate |
| T1 | Auth | IdP for all non-Odoo surfaces (ops console, dashboards) | `supabase/config.toml [auth]` | `spec/supabase-auth-ssot/` |
| T1 | Vault | All server-readable secrets (OCR endpoints, S3 creds, SMTP) | `ssot/secrets/registry.yaml` (names only — never values) | No plaintext in `git diff` |
| T1 | Edge Functions | Integration bridges: receipt OCR, webhooks, policy checks, Plane sync | `supabase/functions/<name>/` | `supabase functions deploy` in CI |
| T1 | Queues (PGMQ) | Async jobs: receipt digitize, embed-chunk, Odoo sync events | `supabase/migrations/*_queues*.sql` | Idempotency + status columns required |
| T2 | Storage | Receipt images + OCR artifacts; Odoo `ir_attachment` pointer (not binary) | `supabase/storage/` policies | RLS policy on every bucket |
| T2 | Realtime | Run progress UI, task board live updates, activity feeds | Application subscriptions | — |
| T2 | ETL → Iceberg | CDC from Odoo Postgres → analytics lake | `infra/supabase-etl/` + `infra/iceberg/` | No BigQuery refs; `ICEBERG_*` vars required |
| T3 | Vector (pgvector) | Embeddings: runbooks, receipt OCR text, specs (RAG) | `supabase/migrations/*_kb_vector*` | — |
| T3 | MCP Server | Agent-controlled schema queries + controlled operations | `mcp/servers/supabase/` | — |
| T4 | Branching | Preview DBs for schema experiments before prod merge | `.github/workflows/` (supabase branch steps) | — |
| T4 | Log Drains | Edge Function + DB logs → observability backend | `infra/observability/supabase/` | — |

**Tier semantics**: T1 = required for every new feature; T2 = activated this cycle (Phase 2); T3 = wired in Phase 3; T4 = future capability.

---

## Analytics Plane: ETL → Analytics Buckets (Iceberg)

> Ref: Supabase ETL Replication docs — publication-based CDC; Analytics Buckets / Iceberg landing.

### How it works in this repo

```
Odoo Postgres (WAL, wal_level=logical)
        │
        ▼  Supabase ETL CDC worker
        │  (publication: odoo_expense_pub)
        │  at-least-once, resumable via replication slot
        ▼
Analytics Bucket  →  Iceberg table files (Parquet + metadata)
        │
        ▼
DuckDB (CI smoke query + analyst queries)
```

### Constraints (EL-only)

- **Extract + Load only** — no transforms in the ETL layer.
  Transformations happen downstream (DuckDB queries, dbt-style views, or Superset SQL).
- Iceberg schema evolution is **additive only**: new nullable columns; breaking changes require a new table version.
- Binary columns (`ir_attachment.datas`) are **excluded** from all Iceberg schemas — pointer-only pattern.
- Partition by `date` where present; else by `_sdc_received_at`.
- Namespace: `odoo_ops` (see Iceberg Landing Contract in `spec/odoo-receipt-digitization/plan.md`).

### Analytics Bucket naming convention

| Bucket name | Source publication | Tables |
|------------|-------------------|--------|
| `odoo-expense-etl` | `odoo_expense_pub` | `expense`, `expense_sheet`, `expense_attachment_meta`, `expense_ocr_run` |

Future ETL publications follow `odoo-<domain>-etl` naming.

### DuckDB Iceberg query workflow

DuckDB can query Iceberg tables directly for:

1. **CI smoke queries** — after ETL pipeline deploys, verify row counts are non-zero and lag < 60s.
2. **Analyst queries** — local DuckDB reads Iceberg files from S3/DO Spaces without a full warehouse.
3. **Schema validation** — assert `ir_attachment.datas` is absent; assert partition columns are present.

```sql
-- Example CI smoke query (run after ETL worker deploy)
INSTALL iceberg; LOAD iceberg;
SELECT count(*) AS row_count, max(_sdc_received_at) AS latest_event
FROM iceberg_scan('s3://ICEBERG_WAREHOUSE/odoo_ops/expense/');
-- Asserts: row_count > 0 AND latest_event > now() - INTERVAL '60 seconds'
```

SSOT for this query: `scripts/ci/check_iceberg_etl_smoke.sh`

---

## Integration Selection Rubric (Buy vs Build)

Use an integration **only if** it:

1. **Removes a whole subsystem** — replaces an entire category of infra, not just adds a feature
2. Has a **repo SSOT location** — no console-only integrations; all config is committed
3. Can be **drift-gated** — CI can detect if it regresses
4. Has **clean secret handling** — Vault or GitHub Secrets compatible; no plaintext in git

Avoid integrations that:
- Duplicate Supabase-native primitives (event buses, schedulers, generic workflow runners)
- Require manual dashboard ops as the "source of truth"

### Integration categories

| Category | Criterion | Examples |
|----------|-----------|---------|
| **Deploy / runtime** | Replaces deploy target or env injection | Vercel (env vars), DigitalOcean (App Platform workers) |
| **Observability** | Replaces a monitoring/alerting subsystem | Log Drains → Sentry, Datadog (T4 future) |
| **Data / BI** | Replaces a warehouse or query layer | Iceberg consumers (DuckDB, Superset); no BigQuery |
| **Comms** | Replaces a notification channel | Slack webhooks (via Edge Function); no standalone bots |

### Adopted integrations

| Integration | Category | Subsystem replaced | SSOT location |
|------------|----------|--------------------|---------------|
| **Vercel** | Deploy / runtime | Env var injection across app deploys | `supabase/config.toml` + Vercel dashboard integration |
| **Cloudflare Workers** | Deploy / runtime | Edge gateway / webhook normalization | `infra/cloudflare/` workers config |
| **n8n** | Comms / ops | Workflow automation; DB Webhooks → trigger | `docs/ops/SUPABASE_N8N.md` + `automations/n8n/` |

Any new integration must: (a) identify the subsystem it replaces, (b) add a row to this table, (c) add an entry in `ssot/secrets/registry.yaml` for any new secrets before activation.

---

## Odoo ↔ Supabase Boundary

```
Odoo CE (System of Record)          Supabase (System of Control)
──────────────────────────          ────────────────────────────
Accounting, posted docs             Ops pipelines, policies
ERP transactions, HR                Analytics, AI, embeddings
Authoritative relational data       Event stream, task queue
```

**Rules**:
- Odoo writes operational truth → Supabase brokers it to analytics/AI layers
- **No write-backs** from Supabase to Odoo ERP tables (Supabase is read-side for Odoo data)
- Cross-boundary: `webhook-ingest` Edge Function, CDC/ETL worker, auth projection

**Cross-boundary files**:
- `supabase/functions/webhook-ingest/` — Odoo → Supabase event bridge
- `infra/supabase-etl/odoo-expense.toml` — CDC config for expense tables
- `supabase/migrations/*_odoo_sync_queue*` — sync event queue

---

## Secrets Placement (Supabase context)

All Supabase-specific secret names are registered in `ssot/secrets/registry.yaml`.
Values live in Supabase Vault (runtime) or GitHub Actions Secrets (CI).

For the full secrets policy see `CLAUDE.md § Secrets Policy`.

---

## Phase Gating

Features within a Tier are gated:

- **T1 must be complete** before T2 features can merge
- **T2 must be complete** before T3 features can merge
- T4 features can start in parallel with T3 (no shared dependencies)

Phase status is tracked in `spec/supabase-maximization/plan.md`.
