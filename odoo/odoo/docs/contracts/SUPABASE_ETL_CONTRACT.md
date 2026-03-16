# C-14 — Supabase ETL Contract

> **Contract ID**: C-14
> **SSOT**: `docs/architecture/SSOT_BOUNDARIES.md §6` (read it before editing here)
> **Status**: ✅ Active (documentation only — ETL infra provisioned via Supabase dashboard)
> **Created**: 2026-02-21
> **Owner**: Platform / DevOps

---

## 1. What is Supabase ETL

Supabase ETL is **CDC (change data capture) off the Postgres WAL** (Write-Ahead Log) via
logical replication. It captures `INSERT`, `UPDATE`, `DELETE`, and `TRUNCATE` operations and
writes an append-only changelog to an analytics destination.

```
Supabase Postgres WAL
        │
        │  logical replication (slot)
        ▼
ETL pipeline (Supabase-managed)
  • reads row-level changes continuously
  • adds cdc_operation column (INSERT/UPDATE/DELETE/TRUNCATE)
  • writes to destination in micro-batches
        │
        ▼
Analytics Destination (non-authoritative replica)
```

---

## 2. Supported Destinations

| Destination | Status | Primary use in this stack |
|-------------|--------|--------------------------|
| **Analytics Buckets (Iceberg)** | ✅ First-class (Supabase-native) | Compliance audit history, hygiene trends, Superset data source |
| **BigQuery** | ✅ First-class | Cross-system OLAP, heavy aggregations, Tableau data source |

**Preferred destination for this stack**: Analytics Buckets (Iceberg) for Supabase-native data;
BigQuery for cross-platform queries involving non-Supabase sources.

---

## 3. Constraints

| Constraint | Detail |
|------------|--------|
| **Primary key required** | Every replicated table must have a PK; tables without PKs cannot be replicated |
| **DDL support limited** | Column additions / renames / type changes are "in development" — schema migrations must happen in Supabase first; ETL replication may pause during DDL changes |
| **No write-backs** | ETL destinations are analytics replicas; no data written to a destination should flow back into Supabase OLTP except via a formally defined pipeline with `ops.platform_events` audit trail |
| **Append-only CDC log** | The changelog is append-only; deletes are represented as `cdc_operation = DELETE` rows, not physical deletes in the destination |
| **OLTP isolation** | ETL replication uses a dedicated Postgres replication slot; it should not share resources with other replication consumers |

---

## 4. Operational Policy

### 4.1 What to replicate

| Source | Destination | Justification |
|--------|-------------|---------------|
| `ops.platform_events` | Analytics Buckets | Complete audit history for compliance, without OLTP read pressure |
| `ops.repo_hygiene_runs` | Analytics Buckets | Historical hygiene trends — queried infrequently, large over time |
| `ops.repo_hygiene_findings` | Analytics Buckets | Detail records for trend dashboards |
| Odoo projections in Supabase (`public.*`) | Analytics Buckets / BigQuery | Superset dashboards for invoices, tasks, expenses |

### 4.2 What must never be replicated

| Source | Reason |
|--------|--------|
| `vault.secrets` | Secrets never leave Vault |
| `vault.decrypted_secrets` | Never replicate decrypted secrets anywhere |
| `auth.users` (raw PII) | GDPR / privacy — only anonymized/derived projections |
| `auth.sessions`, `auth.mfa_*` | Security data — no analytics value |
| Supabase internal (`_analytics`, `_realtime`, `supabase_*`) | System tables |

### 4.3 Retention

| Destination | Retention policy |
|-------------|-----------------|
| Analytics Buckets (Iceberg) | Default Supabase retention; review at 90-day mark |
| BigQuery | Dataset-level TTL to be set when provisioned; default: 365 days |

### 4.4 Drift posture

- ETL replication lag is **not** a schema drift concern — lag is operational, not structural.
- Schema drift (ETL destination missing a column that Supabase has) is a concern. Monitor via:
  - BigQuery: schema comparison in `INFORMATION_SCHEMA`
  - Analytics Buckets: Iceberg metadata inspection
- If ETL falls behind, OLTP is the authoritative source. ETL is never the freshness reference.

### 4.5 Monitoring

- Supabase dashboard → Reports → Replication shows slot lag.
- Add a pg_cron job (separate contract) to alert if replication slot lag exceeds 5 minutes
  against `pg_stat_replication`.
- Failed replication slots must be dropped and recreated (never left in `inactive` state as
  they hold WAL indefinitely and can exhaust disk).

---

## 5. Performance Isolation

ETL is designed to isolate OLTP from OLAP:

- **Never run heavy aggregations on `odoo_prod` Postgres** — use the analytics destination.
- Superset data sources should point at BigQuery or Analytics Buckets, not directly at Supabase OLTP.
- One exception: real-time operational dashboards (sub-minute staleness) may query OLTP via
  read replicas or materialized views — document these explicitly.

---

## 6. Integration with Platform Stack

```
Odoo (SOR for ERP data)
    │ sync bridge
    ▼
Supabase Postgres (SSOT for platform events, auth, queue)
    │ CDC via ETL
    ▼
Analytics Buckets (Iceberg)  ◄── Superset connects here
BigQuery                      ◄── Tableau connects here (optional)
```

- Supabase Cron + Edge Functions orchestrate **workflows** (Zoho token prewarm, repo hygiene).
- ETL handles **data movement** for OLAP — these are complementary, not competing.

---

## 7. Provisioning (Manual)

ETL pipeline configuration is currently **UI-only** in Supabase (as of 2026-02). When a
migration-driven approach becomes available, update this section and remove the MANUAL_REQUIRED.

## [MANUAL_REQUIRED]
- What: Configure ETL pipeline in Supabase dashboard
- Why: Supabase ETL provisioning is UI-only (no SQL/migration API in 2026-02)
- Evidence: n/a (dashboard-only; document the configured pipeline in a comment in this file)
- Minimal human action:
  1. Supabase dashboard → Project → Database → Replication (or ETL tab)
  2. Add source tables (see §4.1 above)
  3. Select destination (Analytics Buckets or BigQuery)
  4. Verify replication slot is active in `pg_stat_replication`
- Then: Automation resumes — Superset can point at the analytics destination

---

## 8. No Write-Back Rule (enforcement)

**Invariant**: No pipeline may write data from an analytics destination back into
`Supabase Postgres` without:

1. A formal pipeline definition committed to `automations/etl/` or `supabase/functions/`
2. An audit trail entry in `ops.platform_events` for every write-back operation
3. A contract section added here in §8 describing the write-back schema and idempotency guarantee

This rule exists because ETL destinations may be stale (lag) — writing stale data back
would corrupt the SSOT.

---

## 9. Related Contracts

| Contract | Relationship |
|----------|-------------|
| [C-12 Supabase Cron](SUPABASE_CRON_CONTRACT.md) | Cron jobs produce events ETL replicates |
| [C-13 Nightly Repo Hygiene](SUPABASE_CRON_REPO_HYGIENE.md) | Hygiene tables are ETL replication candidates |
| [C-07 Supabase Vault Secrets](SUPABASE_VAULT_CONTRACT.md) | Vault secrets must never enter ETL pipeline |
| [C-11 Edge Functions](SUPABASE_EDGE_FUNCTIONS_CONTRACT.md) | Edge Functions write to `ops.platform_events` — replicated by ETL |
