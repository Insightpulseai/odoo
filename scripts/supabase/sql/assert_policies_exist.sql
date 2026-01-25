-- =============================================================================
-- Assert Policies Exist on Protected Tables
-- =============================================================================
-- Fails if no RLS policies exist for required tables.
-- The shell wrapper replaces __TABLE_LIST__ with actual table names.
-- =============================================================================

DO $$
DECLARE
  t text;
  nsp text;
  relname text;
  polcount int;
  bad text[];
BEGIN
  FOREACH t IN ARRAY ARRAY __TABLE_LIST__::text[] LOOP
    nsp := split_part(t, '.', 1);
    relname := split_part(t, '.', 2);

    SELECT count(*) INTO polcount
    FROM pg_policies p
    WHERE p.schemaname = nsp
      AND p.tablename = relname;

    IF polcount = 0 THEN
      bad := array_append(bad, t || ' (no policies)');
    END IF;
  END LOOP;

  IF bad IS NOT NULL THEN
    RAISE EXCEPTION 'Policy check failed: %', bad;
  END IF;
END $$;
