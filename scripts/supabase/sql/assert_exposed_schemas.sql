-- =============================================================================
-- Assert Exposed Schemas Exist
-- =============================================================================
-- Fails if configured "exposed schemas" are missing from the database.
-- The shell wrapper replaces __SCHEMA_LIST__ with actual schema names.
-- =============================================================================

DO $$
DECLARE
  missing text[];
BEGIN
  SELECT array_agg(s) INTO missing
  FROM (
    SELECT unnest(ARRAY __SCHEMA_LIST__::text[]) AS s
  ) req
  WHERE NOT EXISTS (
    SELECT 1 FROM pg_namespace n WHERE n.nspname = req.s
  );

  IF missing IS NOT NULL THEN
    RAISE EXCEPTION 'Missing schemas: %', missing;
  END IF;
END $$;
