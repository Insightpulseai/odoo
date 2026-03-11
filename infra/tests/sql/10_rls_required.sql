-- Enforce RLS on API-exposed schemas (except allowlisted system schemas if you add them)
-- This script expects a psql variable: :exposed_schemas_csv  (e.g. public,storage)
-- It checks every table in those schemas has RLS enabled.
do $$
declare
  sch text;
  tbl record;
  exposed text[] := string_to_array(current_setting('app.exposed_schemas', true), ',');
begin
  if exposed is null or array_length(exposed,1) is null then
    raise exception 'app.exposed_schemas is not set; pass it via SET or env runner';
  end if;

  foreach sch in array exposed loop
    for tbl in
      select n.nspname as schema_name, c.relname as table_name, c.relrowsecurity as rls_enabled
      from pg_class c
      join pg_namespace n on n.oid = c.relnamespace
      where c.relkind = 'r'
        and n.nspname = sch
    loop
      if tbl.rls_enabled is distinct from true then
        raise exception 'RLS NOT enabled on %.%', tbl.schema_name, tbl.table_name;
      end if;
    end loop;
  end loop;
end $$;
