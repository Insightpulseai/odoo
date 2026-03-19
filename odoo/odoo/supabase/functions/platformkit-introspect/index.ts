/// <reference lib="deno.ns" />
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

function requireEnv(name: string): string {
  const v = Deno.env.get(name);
  if (!v) throw new Error(`Missing env: ${name}`);
  return v;
}

Deno.serve(async (req) => {
  const SUPABASE_URL = requireEnv("SUPABASE_URL");
  const SERVICE_ROLE_KEY = requireEnv("SUPABASE_SERVICE_ROLE_KEY");
  const client = createClient(SUPABASE_URL, SERVICE_ROLE_KEY);

  // Inventory: schemas, tables, views, functions, policies
  // NOTE: relies on information_schema + pg_catalog; safe server-side
  const q = async (sql: string, args: any[] = []) => {
    const { data, error } = await client.rpc("platformkit_sql", { sql, args });
    if (error) throw new Error(error.message);
    return data as any[];
  };

  const generated_at = new Date().toISOString();

  const schemas = await q(`
    select nspname as schema
    from pg_namespace
    where nspname not like 'pg_%' and nspname <> 'information_schema'
    order by 1
  `);

  const relations = await q(`
    select
      n.nspname as schema,
      c.relname as name,
      case c.relkind
        when 'r' then 'table'
        when 'v' then 'view'
        when 'm' then 'materialized_view'
        when 'p' then 'partitioned_table'
        else c.relkind::text
      end as kind
    from pg_class c
    join pg_namespace n on n.oid = c.relnamespace
    where n.nspname not like 'pg_%' and n.nspname <> 'information_schema'
      and c.relkind in ('r','v','m','p')
    order by 1,2
  `);

  const functions = await q(`
    select
      n.nspname as schema,
      p.proname as name,
      pg_get_function_identity_arguments(p.oid) as args,
      pg_get_function_result(p.oid) as returns,
      p.prosecdef as security_definer
    from pg_proc p
    join pg_namespace n on n.oid = p.pronamespace
    where n.nspname not like 'pg_%' and n.nspname <> 'information_schema'
    order by 1,2
  `);

  const policies = await q(`
    select
      n.nspname as schema,
      c.relname as table,
      pol.polname as policy,
      pol.polcmd as cmd,
      pg_get_expr(pol.polqual, pol.polrelid) as using_expr,
      pg_get_expr(pol.polwithcheck, pol.polrelid) as check_expr,
      array_to_string(pol.polroles::regrole[], ',') as roles
    from pg_policy pol
    join pg_class c on c.oid = pol.polrelid
    join pg_namespace n on n.oid = c.relnamespace
    where n.nspname not like 'pg_%' and n.nspname <> 'information_schema'
    order by 1,2,3
  `);

  const payload = {
    ok: true,
    generated_at,
    schemas,
    relations,
    functions,
    policies
  };

  return new Response(JSON.stringify(payload, null, 2), {
    headers: { "Content-Type": "application/json" }
  });
});
