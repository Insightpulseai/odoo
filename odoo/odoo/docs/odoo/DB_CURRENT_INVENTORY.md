# DB Current Inventory (Summary)

Machine-readable manifest: `docs/db/DB_CURRENT_INVENTORY.json` (repo artifact — use for tooling)

This document summarizes the live introspection (schemas, representative tables, row counts, tenant/company presence, PKs/FKs). It is derived from a read-only snapshot.

---

## Schemas (High Level)

### System / Infra
- `auth`, `storage`, `realtime`, `supabase_migrations`, `supabase_functions`, `cron`, `extensions`, `pgbouncer`, `pgmq`, `vault`, `secret_vault`

### Domain / Application
- `public`, `core`, `expense`, `finance`, `projects`, `rates`, `inventory`, `maintenance`
- `ai`, `mcp`, `gold`, `platinum`, `ops`, `analytics`
- `scout_bronze`, `scout_silver`, `scout_gold`, `scout`, `notion`, `odoo`, `oca`
- `agents`, `agent`, `saricoach`, `kaggle`, `opex`

### BI / Integration
- `superset`, `net`

---

## Selected High-Value Schemas & Notes

### auth
Supabase auth users, sessions — PK: id (uuid). Several FKs reference auth.users.

### core
`core.company`, `core.app_user` — company PK uuid; app_user references company_id. Useful for company/tenant mapping.

### public
Legacy and shared tables. Many tables are multi-tenant (tenant_id) or reference tenants via `public.tenants`.

### expense
Canonical T&E domain (`expense.expense_reports`, `expense.expenses`, `expense.cash_advances`, `expense.approval_items`) present alongside legacy `public.*` equivalents.

### finance
`finance_compliance_status`, `bir_filing_audit`, `monthly_close_tracker`.

### mcp / ai / gold / platinum
RAG corpora, embeddings, agent orchestration and AI caches (`gold.docs`, `gold.doc_chunks`, `mcp.rag_embeddings`, `platinum.ai_cache`).

### scout / saricoach / kaggle
Retail & analytics stacks (Bronze/Silver/Gold medallion pattern).

### projects / rates / inventory / maintenance
Domain data used by PPM, rate governance, assets.

---

## Multi-Tenant Observations

A tenant model exists as `public.tenants` (id uuid). Many domain tables contain `tenant_id` (uuid) and/or `company_id` (integer/uuid), e.g.:
- `public.expense_reports` (tenant_id, employee_id)
- `public.projects` (tenant_id)
- `scout.transactions` (tenant_id + company_id)

Two identity patterns:
1. **JWT claim pattern** (preferred for RLS templates): `tenant_id` in JWT claim
2. **App-user mapping pattern**: `auth.uid()` -> `core.app_user` -> `company_id` / `tenant_id`

Many tables already include `tenant_id`; RLS templates will target JWT-based tenant_id retrieval.

---

## Quick Validation Notes

- **Row counts**: Most tables are small/empty in this snapshot (many have 0 rows), but `auth.users` and some BI tables contain rows. Use the JSON manifest for exact counts.
- **PKs & FKs**: Primary keys are present for most tables; foreign keys are documented in the JSON manifest.

See `docs/db/DB_CURRENT_INVENTORY.json` for the full machine-readable manifest.
