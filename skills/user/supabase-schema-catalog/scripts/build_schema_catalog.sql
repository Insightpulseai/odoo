-- Build a JSON schema catalog of all non-system tables and columns.
-- Optional: filter by SCHEMA_FILTER (comma-separated list of schemas).
WITH params AS (
  SELECT
    nullif(current_setting('SCHEMA_FILTER', true), '') AS schema_filter_raw
),
schema_list AS (
  SELECT
    CASE
      WHEN p.schema_filter_raw IS NULL THEN NULL
      ELSE regexp_split_to_array(p.schema_filter_raw, '\s*,\s*')
    END AS schemas
  FROM params p
)
SELECT jsonb_pretty(
  jsonb_agg(
    jsonb_build_object(
      'schema', t.table_schema,
      'table', t.table_name,
      'columns', (
        SELECT jsonb_agg(
          jsonb_build_object(
            'name', c.column_name,
            'data_type', c.data_type,
            'is_nullable', c.is_nullable,
            'column_default', c.column_default
          ) ORDER BY c.ordinal_position
        )
        FROM information_schema.columns c
        WHERE c.table_schema = t.table_schema
          AND c.table_name = t.table_name
      )
    ) ORDER BY t.table_schema, t.table_name
  )
)
FROM information_schema.tables t
CROSS JOIN schema_list s
WHERE t.table_type = 'BASE TABLE'
  AND t.table_schema NOT IN ('pg_catalog', 'information_schema')
  AND (
    s.schemas IS NULL
    OR t.table_schema = ANY (s.schemas)
  );
