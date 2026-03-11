# Constitution — Supabase Maximization

**Spec bundle**: `spec/supabase-maximization/`
**Scope**: Encoding "Supabase as control-plane backbone" as enforceable policy across all repo surfaces.

> This spec does NOT duplicate `spec/supabase-auth-ssot/` (Auth is already fully specced).
> Cross-reference: `docs/architecture/SUPABASE_FEATURES_INTEGRATIONS_ADOPTION.md` for the
> full feature adoption map.

---

## Non-Negotiable Rules

### 1. Supabase-native primitive before any external tool
If Supabase has a native feature (Queues, Storage, Vault, Edge Functions, Realtime, Vector),
use it. Do not introduce an external tool that duplicates a Supabase primitive.
**Exception process**: Document the gap in a spec constitution before adopting an alternative.

### 2. Every new table requires RLS + policies before merge
No `supabase/migrations/*.sql` file may create a table without a corresponding
`ALTER TABLE ... ENABLE ROW LEVEL SECURITY` and at least one policy.
**Gate**: `scripts/ci/check_supabase_contract.sh` must pass in CI.

### 3. Vault for all server-readable secrets; `registry.yaml` for names
Any secret read at runtime by server code (Edge Functions, API routes, DO App Platform workers)
must be stored in Supabase Vault. The secret's **name** (not value) is registered in
`ssot/secrets/registry.yaml`. The actual value is never in git, logs, or Slack.

### 4. Queues-first for any async work
No new cron scripts, ad-hoc polling loops, or background threads for async jobs.
Use PGMQ queues (already provisioned in `supabase/migrations/*_queues*.sql`).
Jobs must be idempotent and have a `status` + `attempts` column pattern.

### 5. CDC/ETL → Iceberg for analytics; never analytics inside Odoo
Analytics queries run against the Iceberg destination, not against the Odoo Postgres directly.
No BI tool (Superset, Tableau, Metabase) gets a direct connection to the Odoo Postgres.
**Gate**: No BigQuery references anywhere in `infra/` or `spec/` (grep check).

### 6. Storage + pointer pattern for binary artifacts
Binary files (receipt images, OCR artifacts, attachments) go in Supabase Storage buckets.
Odoo `ir_attachment` stores a pointer (URL/key), not the binary `datas` column value.
Every Storage bucket must have an RLS policy.

### 7. Feature adoption follows Tiers: T1 gates T2 gates T3 gates T4
See `docs/architecture/SUPABASE_FEATURES_INTEGRATIONS_ADOPTION.md` for Tier definitions.
A Tier-2 feature may not merge until all Tier-1 gates are green in CI.

### 8. No console-only infrastructure changes
Supabase Dashboard, DigitalOcean console, Vercel dashboard — all changes that affect
production must have a corresponding repo commit (migration, config, IaC).
Dashboard-only changes are treated as drift and will be overwritten by CI.
