-- Build a JSON schema catalog of all non-system tables and columns.
-- Optional: filter by SCHEMA_FILTER (comma-separated list of schemas).
with params as (
  select
    nullif(current_setting('SCHEMA_FILTER', true), '') as schema_filter_raw
),
schema_list as (
  select
    case
      when p.schema_filter_raw is null then null
      else regexp_split_to_array(p.schema_filter_raw, '\s*,\s*')
    end as schemas
  from params p
)
select jsonb_pretty(
  jsonb_agg(
    jsonb_build_object(
      'schema', t.table_schema,
      'table', t.table_name,
      'columns', (
        select jsonb_agg(
          jsonb_build_object(
            'name', c.column_name,
            'data_type', c.data_type,
            'is_nullable', c.is_nullable,
            'column_default', c.column_default
          ) order by c.ordinal_position
        )
        from information_schema.columns c
        where c.table_schema = t.table_schema
          and c.table_name = t.table_name
      )
    ) order by t.table_schema, t.table_name
  )
)
from information_schema.tables t
cross join schema_list s
where t.table_type = 'BASE TABLE'
  and t.table_schema not in ('pg_catalog', 'information_schema')
  and (
    s.schemas is null
    or t.table_schema = any (s.schemas)
  );
