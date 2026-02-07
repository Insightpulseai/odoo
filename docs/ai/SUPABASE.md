# Supabase Maximization (Pro Plan)
> Extracted from root CLAUDE.md. See [CLAUDE.md](../../CLAUDE.md) for authoritative rules.

---

## Current Usage

| Feature | Status | Action |
|---------|--------|--------|
| Database | 208 tables | Well utilized |
| Functions | 59 functions | Well utilized |
| pgvector | Installed | Use for AI search |
| Auth | 9 req/24h | Underutilized |
| Storage | 0 usage | Activate! |
| Realtime | 0 usage | Activate! |
| Edge Functions | Check | Evaluate |

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

## Security Fixes (Run Immediately)

```sql
-- Fix function search_path (200+ functions)
DO $$
DECLARE func_record RECORD;
BEGIN
    FOR func_record IN
        SELECT n.nspname, p.proname, pg_get_function_identity_arguments(p.oid) as args
        FROM pg_proc p JOIN pg_namespace n ON p.pronamespace = n.oid
        WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
    LOOP
        EXECUTE format('ALTER FUNCTION %I.%I(%s) SET search_path = %I, pg_temp',
            func_record.nspname, func_record.proname, func_record.args, func_record.nspname);
    END LOOP;
END $$;

-- Enable RLS on unprotected tables
ALTER TABLE public."SsoDetails" ENABLE ROW LEVEL SECURITY;
ALTER TABLE public."UserOrganization" ENABLE ROW LEVEL SECURITY;
```
