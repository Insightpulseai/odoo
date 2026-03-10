do $$
declare
  sch text;
  tbl record;
  exposed text[] := string_to_array(current_setting('app.exposed_schemas', true), ',');
  pol_count int;
begin
  if exposed is null or array_length(exposed,1) is null then
    raise exception 'app.exposed_schemas is not set; pass it via SET or env runner';
  end if;

  foreach sch in array exposed loop
    for tbl in
      select n.nspname as schema_name, c.relname as table_name, c.oid as relid
      from pg_class c
      join pg_namespace n on n.oid = c.relnamespace
      where c.relkind='r'
        and n.nspname = sch
    loop
      select count(*) into pol_count from pg_policy p where p.polrelid = tbl.relid;
      if pol_count < 1 then
        raise exception 'No RLS policy found for %.% (table is in exposed schema list)', tbl.schema_name, tbl.table_name;
      end if;
    end loop;
  end loop;
end $$;
