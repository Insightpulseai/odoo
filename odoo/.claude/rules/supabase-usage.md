---
paths:
  - "supabase/**"
  - "db/**"
---

# Supabase Usage

> Supabase maximization, current usage, features to activate, and security fixes.

---

## Supabase Maximization (Pro Plan)

### Current Usage

| Feature | Status | Action |
|---------|--------|--------|
| Database | Active: 208 tables | Well utilized |
| Functions | Active: 59 functions | Well utilized |
| pgvector | Active: Installed | Use for AI search |
| Auth | Warning: 9 req/24h | Underutilized |
| Storage | Inactive: 0 usage | Activate! |
| Realtime | Inactive: 0 usage | Activate! |
| Edge Functions | Unknown | Evaluate |

### Features to Activate (FREE with Pro)

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

### Security Fixes (Run Immediately)

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

---

*Last updated: 2026-03-16*
