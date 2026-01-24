-- Fails if configured "exposed schemas" are missing
-- This is executed against a live DB.
-- NOTE: keep this list in sync with supabase/config.toml extraction.
-- Placeholder list is injected by the shell wrapper.

-- shell wrapper will replace __SCHEMA_LIST__ with ('public','ops',...)
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
