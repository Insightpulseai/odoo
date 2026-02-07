# Supabase Integration & Monorepo Mirroring
> Extracted from root CLAUDE.md. See [CLAUDE.md](../../CLAUDE.md) for authoritative rules.

---

## Key Principle

**Supabase is NOT a live replica of Odoo.** It is an integration layer:

| Role | What lives there |
|------|------------------|
| **Event bus** | Webhook ingestion, event outbox, sync cursors |
| **Catalog** | Unity Catalog (assets, tools, lineage) |
| **Shadow tables** | Read-only snapshots for verification (not authoritative) |
| **Edge compute** | 43 Edge Functions (sync, auth, cron, MCP gateway) |
| **Auth & storage** | External-facing auth flows, document storage |

Odoo PostgreSQL (self-hosted, PG 16) remains the authoritative ERP database.

---

## Project

| Item | Value |
|------|-------|
| **Project ID** | `spdtwktxdalcfigzeqrz` |
| **Config** | `supabase/config.toml` |
| **PG version** | 15 (Supabase) ↔ 16 (DO self-hosted): wire-compatible |
| **Migrations** | 103 files across 7 schema layers |
| **Edge Functions** | 43 deployed |
| **Deprecated projects** | `xkxyvboeubffxxbebsll`, `ublqmilcjtpnflofprkr` — never use |

---

## Monorepo Sync Architecture

```
Odoo CE 19 (PG 16)                    Supabase (PG 15)
+-----------------------+              +---------------------------+
| account.move          |  webhook     | odoo.webhook_events       |
| project.project       | ----------> | odoo.sync_cursors          |
| project.task          |  (HMAC)     | odoo.entity_mappings       |
| ir.module.module      |              | odoo.instances             |
+-----------------------+              +---------------------------+
                                                  |
                                       +----------+-----------+
                                       |                      |
                                  shadow-odoo          catalog-sync
                                  -finance              (Odoo models
                                  (snapshot)             + Scout views)
                                       |                      |
                                       v                      v
                              odoo_seed.shadow_*     catalog.assets
                              (verification only)    (FQDN indexed)
```

### Sync Patterns (Event-Driven, Not Mirroring)

| Pattern | Edge Function | Direction | Frequency |
|---------|--------------|-----------|-----------|
| **Webhook ingestion** | `odoo-webhook` | Odoo → Supabase | Real-time (on event) |
| **Module inventory** | `sync-odoo-modules` | Odoo → Supabase | Scheduled |
| **Finance shadow** | `shadow-odoo-finance` | Odoo → Supabase | Scheduled |
| **Asset catalog** | `catalog-sync` | Odoo + Scout → Supabase | Manual/scheduled |
| **Realtime broadcast** | `realtime-sync` | Supabase → clients | On change |

### Webhook Flow

```
Odoo → POST /odoo-webhook
  Headers: x-ipai-signature (HMAC-SHA256), x-ipai-timestamp
  Body: { event_type, aggregate_type, aggregate_id, payload }
  Validation: 5-minute replay window
  Destination: odoo.webhook_events (status: pending → completed/failed)
  Audit: event_log table
```

### Shadow Tables (Verification Only)

```sql
-- odoo_seed schema: read-only snapshots
shadow_projects (odoo_id, external_ref, name, synced_at, raw)
shadow_tasks    (odoo_id, external_ref, project_odoo_id, synced_at, raw)

-- Verification views (auto-detect drift)
v_missing_in_odoo   -- seed exists, shadow doesn't
v_orphan_in_odoo    -- shadow exists, seed doesn't
v_name_drift        -- names changed between sync cycles
```

### Unity Catalog

```sql
-- catalog schema: FQDN-indexed asset registry
catalog.assets (fqdn, type, metadata, registered_at)
-- FQDN format: system.db.model
-- e.g., odoo.odoo_core.account.move, scout.gold.v_revenue_summary
```

---

## Database Schema Layers

| Layer | Migration Range | Content |
|-------|----------------|---------|
| **Auth** | 5000–5003 | Identity, JWT, RLS |
| **Core** | 1000 | Tenancy, ERP base |
| **ERP** | 2000 | Finance, expense, inventory |
| **Engine** | 3000 | Processing engines |
| **Odoo Bridge** | 2025-01-25 | Integration schemas |
| **Operations** | 2026-01-24 | Ops control plane |
| **Cleanup** | 99999999 | Rollback examples |

**Key schemas**: `public`, `odoo`, `odoo_seed`, `scout_gold`, `catalog`, `integration`

---

## Seed Strategy (9-Part)

```
9000_core/       → Tenants, roles, users, auth
9001_erp/        → Odoo data + BIR templates
9002_engines/    → Processing engines (retail intel, PPM, TE, OCR)
9003_ai_rag/     → AI agent + knowledge base
9004_analytics/  → KPI registry + Superset dashboards
9005_catalog/    → Asset catalog
9006_catalog/    → Scout SUQI semantic
9007_skills/     → Certification
9008_drawio/     → DrawIO assessment
```

Master orchestrator: `supabase/seed.sql`

---

## Infrastructure as Code

```
infra/supabase/
├── main.tf              # Provider config
├── production.tf        # Project resources
├── vault_secrets.tf     # Secret management
├── envs/
│   ├── dev/             # terraform.tfvars.example
│   ├── staging/
│   └── prod/
```

Commands: `make plan ENV=prod`, `make apply`, `make db-push`

---

## Current Usage

| Feature | Status | Action |
|---------|--------|--------|
| Database | 208 tables | Well utilized |
| Functions | 43 edge functions | Well utilized |
| pgvector | Installed | Use for AI search |
| Auth | 9 req/24h | Underutilized |
| Storage | 0 usage | Activate for documents |
| Realtime | 0 usage | Activate for dashboards |

## Features to Activate (FREE with Pro)

**Realtime** - Live dashboards:
```typescript
supabase
  .channel('odoo-sync')
  .on('postgres_changes',
    { event: '*', schema: 'odoo_mirror', table: '*' },
    (payload) => console.log('Change:', payload)
  )
  .subscribe()
```

**Storage** - Replace S3/Cloudinary:
```typescript
await supabase.storage
  .from('documents')
  .upload(`bir/${year}/${form_type}/${filename}`, file)
```

**pg_cron** - Replace n8n for DB-only jobs:
```sql
SELECT cron.schedule(
  'refresh-gold-views',
  '0 2 * * *',
  $$SELECT scout.refresh_gold_materialized_views()$$
);
```

---

## Security Verification Scripts

```bash
scripts/supabase/checks.sh                     # Health checks
scripts/supabase/exposed_schemas.py             # PostgREST exposure audit
scripts/supabase/sql/assert_exposed_schemas.sql # Schema checks
scripts/supabase/sql/assert_rls_enabled.sql     # RLS verification
scripts/supabase/sql/assert_policies_exist.sql  # Policy checks
```

---

## No Dedicated Odoo Connector Module

Supabase integration is handled at the **function/API layer** — Edge Functions for webhooks + catalog sync, Python `requests` for Odoo → Supabase calls. No `ipai_supabase_connector` module needed.
