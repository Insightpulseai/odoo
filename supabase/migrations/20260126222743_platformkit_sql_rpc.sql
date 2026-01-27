create schema if not exists platformkit;

-- Minimal SQL runner for inventory queries.
-- SECURITY: keep schema locked down; Edge Function uses service role.
create or replace function platformkit.platformkit_sql(sql text, args jsonb default '[]'::jsonb)
returns jsonb
language plpgsql
security definer
set search_path = pg_catalog, public, platformkit
as $$
declare
  res jsonb;
begin
  execute format('select coalesce(jsonb_agg(t), ''[]''::jsonb) from (%s) t', sql) into res;
  return res;
end;
$$;

revoke all on function platformkit.platformkit_sql(text, jsonb) from public;
