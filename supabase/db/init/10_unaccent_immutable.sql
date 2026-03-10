-- =============================================================================
-- PostgreSQL Extensions + IMMUTABLE unaccent wrapper
-- =============================================================================
-- Fixes: "functions in index expression must be marked IMMUTABLE" error
-- when Odoo or OCA modules create indexes using unaccent().
--
-- References:
-- - https://neon.com/docs/extensions/unaccent
-- - https://www.postgresql.org/docs/current/sql-createfunction.html
-- =============================================================================

-- Ensure required extensions for Odoo text search / trigram indexes
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;

-- Preferred: immutable wrapper (safe + explicit)
-- Use this in your index definitions: unaccent_immutable(column_name)
CREATE OR REPLACE FUNCTION public.unaccent_immutable(text)
RETURNS text
LANGUAGE sql
IMMUTABLE
PARALLEL SAFE
AS $$
  SELECT unaccent('unaccent', $1);
$$;

-- Compatibility: if upstream code uses public.unaccent(text) in indexes,
-- Postgres will reject it unless it's IMMUTABLE. This is a pragmatic fix.
-- WARNING: Altering volatility of an existing function can affect query plans.
DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM pg_proc p
    JOIN pg_namespace n ON n.oid = p.pronamespace
    WHERE n.nspname = 'public'
      AND p.proname = 'unaccent'
      AND pg_get_function_identity_arguments(p.oid) = 'text'
  ) THEN
    EXECUTE 'ALTER FUNCTION public.unaccent(text) IMMUTABLE';
  END IF;
END $$;
