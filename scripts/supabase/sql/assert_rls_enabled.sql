-- =============================================================================
-- Assert RLS Enabled on Protected Tables
-- =============================================================================
-- Fails if RLS is not enabled on required tables.
-- The shell wrapper replaces __TABLE_LIST__ with actual table names.
-- =============================================================================

DO $$
DECLARE
  t text;
  rel regclass;
  relrowsecurity boolean;
  relforcerowsecurity boolean;
  bad text[];
BEGIN
  FOREACH t IN ARRAY ARRAY __TABLE_LIST__::text[] LOOP
    rel := to_regclass(t);
    IF rel IS NULL THEN
      bad := array_append(bad, t || ' (missing)');
    ELSE
      SELECT c.relrowsecurity, c.relforcerowsecurity
        INTO relrowsecurity, relforcerowsecurity
      FROM pg_class c
      JOIN pg_namespace n ON n.oid = c.relnamespace
      WHERE c.oid = rel;

      IF relrowsecurity IS DISTINCT FROM true THEN
        bad := array_append(bad, t || ' (rls=off)');
      END IF;
    END IF;
  END LOOP;

  IF bad IS NOT NULL THEN
    RAISE EXCEPTION 'RLS check failed: %', bad;
  END IF;
END $$;
