# Odoo Shadow Schema - Deployment Guide

**Purpose**: Deploy Odoo → Supabase schema mirroring ("Innovation Sidecar")
**Status**: Ready for deployment
**Last Updated**: 2026-01-20

---

## Overview

The Odoo Shadow Schema mirrors data from Odoo CE (PostgreSQL on DigitalOcean) to Supabase for:

- **Analytics & BI**: Query Odoo data with Supabase/PostgREST without impacting production
- **RAG/AI**: Vector search and LLM context retrieval over business data
- **Reporting**: Real-time dashboards with Supabase edge caching

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     Odoo Shadow Schema Architecture                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Odoo CE (DO PostgreSQL)          Supabase (odoo_shadow schema)        │
│   ┌────────────────────┐           ┌────────────────────────────┐       │
│   │ res_partner        │──────────▶│ odoo_shadow_res_partner    │       │
│   │ account_move       │  XML-RPC  │ odoo_shadow_account_move   │       │
│   │ sale_order         │   ETL     │ odoo_shadow_sale_order     │       │
│   │ product_product    │  (incr)   │ odoo_shadow_product_product│       │
│   │ ... (357 models)   │           │ ... (288 tables)           │       │
│   └────────────────────┘           └────────────────────────────┘       │
│                                              │                          │
│                                    ┌─────────▼─────────┐                │
│                                    │  PostgREST API    │                │
│                                    │  Edge Functions   │                │
│                                    │  Analytics/RAG    │                │
│                                    └───────────────────┘                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Sync Strategy

| Aspect | Implementation |
|--------|---------------|
| Direction | One-way (Odoo → Supabase), read-only shadow |
| Method | Incremental by `write_date` watermarks |
| Conflict Resolution | UPSERT on primary key (`id`) |
| Frequency | Configurable (hourly, daily, on-demand) |
| Batch Size | 500-1000 records per batch |

---

## Components

### 1. Supabase Migrations

| File | Purpose |
|------|---------|
| `supabase/migrations/20260120100001_odoo_shadow_base.sql` | Schema infrastructure (metadata, watermarks, logging) |
| `supabase/migrations/20260120100002_odoo_shadow_tables.sql` | 288 auto-generated shadow tables |

### 2. ETL Sync Scripts

| Script | Purpose |
|--------|---------|
| `scripts/sync_odoo_shadow.py` | Main Python ETL script (CLI) |
| `supabase/functions/ops-job-worker/index.ts` | Edge Function handler for job queue |

### 3. Metadata Tables

| Table | Purpose |
|-------|---------|
| `odoo_shadow_meta` | Registry of shadow tables with sync metadata |
| `odoo_shadow_watermark` | Incremental sync watermarks per table |
| `odoo_shadow_sync_log` | Audit trail of ETL runs |

---

## Deployment Steps

### Step 1: Deploy Schema to Supabase

```bash
# Option A: Using Supabase CLI
cd /path/to/odoo-ce
supabase db push

# Option B: Using psql directly
psql "$SUPABASE_DB_URL" -f supabase/migrations/20260120100001_odoo_shadow_base.sql
psql "$SUPABASE_DB_URL" -f supabase/migrations/20260120100002_odoo_shadow_tables.sql
```

### Step 2: Configure Credentials

Store Odoo credentials in Supabase Vault:

```sql
-- In Supabase SQL Editor
SELECT vault.create_secret('ODOO_URL', 'https://erp.insightpulseai.com');
SELECT vault.create_secret('ODOO_DB', 'odoo_core');
SELECT vault.create_secret('ODOO_USER', 'api-user@example.com');
SELECT vault.create_secret('ODOO_PASSWORD', 'your-secure-password');
```

Or set environment variables for the Edge Function:

```bash
# In Vercel/Supabase dashboard
ODOO_URL=https://erp.insightpulseai.com
ODOO_DB=odoo_core
ODOO_USER=api-user@example.com
ODOO_PASSWORD=your-secure-password
```

### Step 3: Deploy Edge Function

```bash
cd supabase/functions
supabase functions deploy ops-job-worker
```

### Step 4: Run Initial Sync

```bash
# Full sync all priority models
export ODOO_URL="https://erp.insightpulseai.com"
export ODOO_DB="odoo_core"
export ODOO_USER="api-user@example.com"
export ODOO_PASSWORD="your-password"
export SUPABASE_URL="https://spdtwktxdalcfigzeqrz.supabase.co"
export SUPABASE_SERVICE_KEY="your-service-role-key"

python scripts/sync_odoo_shadow.py --full --verbose
```

### Step 5: Schedule Incremental Sync

**Option A: GitHub Actions (Recommended)**

```yaml
# .github/workflows/odoo-shadow-sync.yml
name: Odoo Shadow Sync
on:
  schedule:
    - cron: '0 */4 * * *'  # Every 4 hours
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install supabase
      - run: python scripts/sync_odoo_shadow.py
        env:
          ODOO_URL: ${{ secrets.ODOO_URL }}
          ODOO_DB: ${{ secrets.ODOO_DB }}
          ODOO_USER: ${{ secrets.ODOO_USER }}
          ODOO_PASSWORD: ${{ secrets.ODOO_PASSWORD }}
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
```

**Option B: Supabase Cron**

```sql
-- Create cron job in Supabase
SELECT cron.schedule(
  'odoo-shadow-sync',
  '0 */4 * * *',
  $$
  SELECT net.http_post(
    url := 'https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/ops-job-worker',
    headers := '{"Authorization": "Bearer ' || current_setting('app.settings.service_role_key') || '"}'::jsonb,
    body := '{"job_slug": "sync_odoo_shadow"}'::jsonb
  );
  $$
);
```

**Option C: n8n Workflow**

Create a workflow that:
1. Triggers on schedule (every 4 hours)
2. HTTP POST to Edge Function endpoint
3. Logs results to Mattermost

---

## Verification

### Check Schema Deployed

```sql
-- In Supabase SQL Editor
SELECT schema_name
FROM information_schema.schemata
WHERE schema_name = 'odoo_shadow';

-- Check tables created
SELECT COUNT(*)
FROM information_schema.tables
WHERE table_schema = 'odoo_shadow';
-- Expected: 288+ tables
```

### Check Sync Status

```sql
-- Recent sync runs
SELECT table_name, status, rows_inserted, duration_ms, started_at
FROM odoo_shadow_sync_log
ORDER BY started_at DESC
LIMIT 20;

-- Watermarks (sync progress)
SELECT table_name, last_write_date, rows_synced, updated_at
FROM odoo_shadow_watermark
ORDER BY updated_at DESC;

-- Row counts per shadow table
SELECT * FROM odoo_shadow_meta ORDER BY row_count DESC;
```

### Test API Access

```bash
# Query shadow data via PostgREST
curl -X GET \
  'https://spdtwktxdalcfigzeqrz.supabase.co/rest/v1/odoo_shadow_res_partner?limit=10' \
  -H "apikey: $SUPABASE_ANON_KEY" \
  -H "Authorization: Bearer $SUPABASE_ANON_KEY"
```

---

## CLI Usage

### Full Sync

```bash
# Sync all priority models from scratch
python scripts/sync_odoo_shadow.py --full

# Sync specific models
python scripts/sync_odoo_shadow.py --full --models res.partner,account.move
```

### Incremental Sync

```bash
# Sync only changes since last watermark
python scripts/sync_odoo_shadow.py

# With larger batches
python scripts/sync_odoo_shadow.py --batch-size 2000
```

### Dry Run

```bash
# Preview what would be synced
python scripts/sync_odoo_shadow.py --dry-run --verbose
```

---

## Troubleshooting

### Sync Fails with Authentication Error

```bash
# Test Odoo connection
curl -X POST "$ODOO_URL/jsonrpc" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"call","params":{"service":"common","method":"version"},"id":1}'
```

### Shadow Tables Not Visible

```sql
-- Grant access to shadow schema
GRANT USAGE ON SCHEMA odoo_shadow TO anon, authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA odoo_shadow TO anon, authenticated;
```

### Sync Too Slow

1. Increase batch size: `--batch-size 2000`
2. Sync specific high-priority models only
3. Run during off-peak hours
4. Check Odoo server resources

### Data Mismatch

```sql
-- Compare counts between Odoo and shadow
SELECT table_name, row_count FROM odoo_shadow_meta;

-- Check for stale watermarks
SELECT * FROM odoo_shadow_watermark
WHERE last_write_date < NOW() - INTERVAL '1 day';
```

---

## Priority Models

These models are synced by default (core business data):

| Model | Shadow Table | Description |
|-------|--------------|-------------|
| `res.partner` | `odoo_shadow_res_partner` | Contacts, customers, vendors |
| `res.users` | `odoo_shadow_res_users` | User accounts |
| `res.company` | `odoo_shadow_res_company` | Companies |
| `account.move` | `odoo_shadow_account_move` | Journal entries, invoices |
| `account.move.line` | `odoo_shadow_account_move_line` | Invoice/entry lines |
| `account.account` | `odoo_shadow_account_account` | Chart of accounts |
| `sale.order` | `odoo_shadow_sale_order` | Sales orders |
| `sale.order.line` | `odoo_shadow_sale_order_line` | SO lines |
| `purchase.order` | `odoo_shadow_purchase_order` | Purchase orders |
| `product.product` | `odoo_shadow_product_product` | Products |
| `product.template` | `odoo_shadow_product_template` | Product templates |
| `project.project` | `odoo_shadow_project_project` | Projects |
| `project.task` | `odoo_shadow_project_task` | Tasks |

---

## Security Considerations

1. **Read-only shadow**: Shadow tables are for reading only; writes go to Odoo
2. **Service role only**: ETL uses service_role key, not exposed to clients
3. **RLS optional**: Enable RLS on shadow tables if needed for multi-tenant
4. **Sensitive fields**: Binary/attachment fields are excluded from sync
5. **Credentials in Vault**: Use Supabase Vault for Odoo credentials

---

## Related Documentation

- [INFRASTRUCTURE_CHECKLIST.md](../INFRASTRUCTURE_CHECKLIST.md) - Section B: Innovation Sidecar
- [SHADOW_SCHEMA_FEASIBILITY.md](../data-model/SHADOW_SCHEMA_FEASIBILITY.md) - Technical analysis
- [ODOO_MODEL_INDEX.json](../data-model/ODOO_MODEL_INDEX.json) - Source for DDL generation
- [MCP_JOBS_SYSTEM.md](./MCP_JOBS_SYSTEM.md) - Job orchestration

---

*Last verified: 2026-01-20*
