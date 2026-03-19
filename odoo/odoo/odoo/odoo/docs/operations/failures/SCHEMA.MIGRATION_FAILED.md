# Runbook: SCHEMA.MIGRATION_FAILED

**Severity**: Critical
**HTTP Status**: n/a (deploy failure)
**Retryable**: After fixing the migration

## Symptoms

`supabase db push` exits non-zero.  Partial migration may have applied.

```
Error: supabase db push failed: column "fts" is of type tsvector but
expression is of type text
```

## Root Causes

1. A GENERATED ALWAYS column expression has a type mismatch.
2. A `CREATE TABLE IF NOT EXISTS` was run twice with incompatible schemas.
3. A required extension (`pg_trgm`, `unaccent`) is not enabled.
4. The migration references a table that doesn't exist yet.

## Remediation

```bash
# 1. Connect to the Supabase database
supabase db remote commit  # check current state

# 2. Inspect the partially applied migration
SELECT * FROM supabase_migrations.schema_migrations ORDER BY version DESC LIMIT 5;

# 3. If partially applied, roll back manually
# (each migration must be idempotent — all CREATE TABLE IF NOT EXISTS)

# 4. Enable missing extensions
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;

# 5. Fix the migration SQL and re-apply
supabase db push

# 6. Verify key tables exist
SELECT schemaname, tablename FROM pg_tables WHERE schemaname = 'ops' ORDER BY tablename;
```

## Prevention

- All migrations must use `CREATE TABLE IF NOT EXISTS` and `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`.
- Test migrations locally with `supabase start && supabase db push` before merging.
- Never use destructive DDL (`DROP TABLE`, `TRUNCATE`) in the `ops` schema.
