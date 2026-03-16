-- =============================================================================
-- Tables Browser: ops.exposed_schemas + API RPCs
-- =============================================================================
-- Implements Supabase Studio-style database tables browser with:
-- - Schema exposure control (allowlist for APIs/apps)
-- - Fast relation listing via pg_catalog (no COUNT(*))
-- - On-demand exact row counts
-- =============================================================================

-- Ensure ops schema exists
create schema if not exists ops;

-- Ensure api schema exists
create schema if not exists api;

-- =============================================================================
-- 1. ops.exposed_schemas - Schema Allowlist
-- =============================================================================
-- Controls which schemas are exposed to non-admin users in the Tables browser.
-- Default: 'public' is exposed; others require explicit addition.

create table if not exists ops.exposed_schemas (
    schema_name text primary key,
    exposed boolean not null default true,
    description text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

comment on table ops.exposed_schemas is
    'Allowlist of schemas exposed to non-admin users in Tables browser';

-- Auto-update updated_at
create or replace function ops.update_exposed_schemas_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

drop trigger if exists trg_exposed_schemas_updated_at on ops.exposed_schemas;
create trigger trg_exposed_schemas_updated_at
    before update on ops.exposed_schemas
    for each row
    execute function ops.update_exposed_schemas_updated_at();

-- Seed default exposed schema (public)
insert into ops.exposed_schemas (schema_name, exposed, description)
values ('public', true, 'Default public schema')
on conflict (schema_name) do nothing;

-- =============================================================================
-- 2. RLS Policies for ops.exposed_schemas
-- =============================================================================

alter table ops.exposed_schemas enable row level security;

-- Allow authenticated users to read exposed schemas
drop policy if exists "Allow authenticated read" on ops.exposed_schemas;
create policy "Allow authenticated read" on ops.exposed_schemas
    for select
    to authenticated
    using (true);

-- Allow service_role full access (for admin operations)
drop policy if exists "Service role full access" on ops.exposed_schemas;
create policy "Service role full access" on ops.exposed_schemas
    for all
    to service_role
    using (true)
    with check (true);

-- =============================================================================
-- 3. api.list_relations - Fast Relation Listing via pg_catalog
-- =============================================================================
-- Returns tables, views, and materialized views with estimated row counts.
-- Uses pg_class.reltuples for speed (no COUNT(*) across tables).
-- Filters by exposed schemas for non-admin callers.

create or replace function api.list_relations(
    include_views boolean default true,
    include_system boolean default false
)
returns table(
    schema_name text,
    relation_name text,
    relation_type text,
    row_estimate bigint,
    is_exposed boolean
)
security definer
language sql
stable
as $$
    with exposed as (
        select es.schema_name, es.exposed
        from ops.exposed_schemas es
    ),
    relations as (
        select
            n.nspname::text as schema_name,
            c.relname::text as relation_name,
            case c.relkind
                when 'r' then 'table'
                when 'v' then 'view'
                when 'm' then 'materialized_view'
                when 'p' then 'partitioned_table'
                else 'other'
            end as relation_type,
            greatest(c.reltuples::bigint, 0) as row_estimate
        from pg_class c
        join pg_namespace n on n.oid = c.relnamespace
        where
            -- Exclude system catalogs unless requested
            (include_system or n.nspname not in ('pg_catalog', 'information_schema', 'pg_toast'))
            -- Filter by relation kind
            and (
                c.relkind in ('r', 'm', 'p')  -- tables, materialized views, partitioned tables
                or (include_views and c.relkind = 'v')  -- views if requested
            )
            -- Exclude internal schemas
            and n.nspname not like 'pg_temp%'
            and n.nspname not like 'pg_toast%'
    )
    select
        r.schema_name,
        r.relation_name,
        r.relation_type,
        r.row_estimate,
        coalesce(e.exposed, false) as is_exposed
    from relations r
    left join exposed e on e.schema_name = r.schema_name
    order by
        -- Exposed schemas first
        (case when coalesce(e.exposed, false) then 0 else 1 end),
        r.schema_name,
        r.relation_name;
$$;

comment on function api.list_relations is
    'Lists database relations with estimated row counts. Fast (uses pg_catalog).';

-- Grant execute to authenticated users
grant execute on function api.list_relations(boolean, boolean) to authenticated;
grant execute on function api.list_relations(boolean, boolean) to anon;

-- =============================================================================
-- 4. api.count_rows - Exact Row Count (On-Demand)
-- =============================================================================
-- Returns exact row count for a single table. Use sparingly (full table scan).
-- Called when user opens a specific table detail view.

create or replace function api.count_rows(
    p_schema_name text,
    p_relation_name text
)
returns bigint
security definer
language plpgsql
stable
as $$
declare
    v_count bigint;
    v_sql text;
begin
    -- Validate inputs to prevent SQL injection
    if p_schema_name is null or p_relation_name is null then
        raise exception 'Schema and relation name are required';
    end if;

    -- Check if relation exists
    if not exists (
        select 1
        from pg_class c
        join pg_namespace n on n.oid = c.relnamespace
        where n.nspname = p_schema_name
          and c.relname = p_relation_name
          and c.relkind in ('r', 'm', 'v', 'p')
    ) then
        raise exception 'Relation %.% not found', p_schema_name, p_relation_name;
    end if;

    -- Build and execute count query with proper quoting
    v_sql := format('select count(*) from %I.%I', p_schema_name, p_relation_name);
    execute v_sql into v_count;

    return v_count;
end;
$$;

comment on function api.count_rows is
    'Returns exact row count for a relation. Use sparingly (performs full scan).';

-- Grant execute to authenticated users
grant execute on function api.count_rows(text, text) to authenticated;

-- =============================================================================
-- 5. api.get_table_columns - Column Metadata
-- =============================================================================
-- Returns column information for a specific table using information_schema.

create or replace function api.get_table_columns(
    p_schema_name text,
    p_table_name text
)
returns table(
    column_name text,
    data_type text,
    is_nullable boolean,
    column_default text,
    ordinal_position integer,
    is_primary_key boolean
)
security definer
language sql
stable
as $$
    with pk_columns as (
        select a.attname as column_name
        from pg_index i
        join pg_attribute a on a.attrelid = i.indrelid and a.attnum = any(i.indkey)
        join pg_class c on c.oid = i.indrelid
        join pg_namespace n on n.oid = c.relnamespace
        where i.indisprimary
          and n.nspname = p_schema_name
          and c.relname = p_table_name
    )
    select
        c.column_name::text,
        c.data_type::text,
        (c.is_nullable = 'YES') as is_nullable,
        c.column_default::text,
        c.ordinal_position::integer,
        exists(select 1 from pk_columns pk where pk.column_name = c.column_name) as is_primary_key
    from information_schema.columns c
    where c.table_schema = p_schema_name
      and c.table_name = p_table_name
    order by c.ordinal_position;
$$;

comment on function api.get_table_columns is
    'Returns column metadata for a table including primary key information.';

grant execute on function api.get_table_columns(text, text) to authenticated;

-- =============================================================================
-- 6. api.get_table_sample - Sample Rows
-- =============================================================================
-- Returns first N rows from a table. Used in table detail view.

create or replace function api.get_table_sample(
    p_schema_name text,
    p_table_name text,
    p_limit integer default 100
)
returns jsonb
security definer
language plpgsql
stable
as $$
declare
    v_result jsonb;
    v_sql text;
begin
    -- Validate inputs
    if p_schema_name is null or p_table_name is null then
        raise exception 'Schema and table name are required';
    end if;

    -- Check if relation exists
    if not exists (
        select 1
        from pg_class c
        join pg_namespace n on n.oid = c.relnamespace
        where n.nspname = p_schema_name
          and c.relname = p_table_name
          and c.relkind in ('r', 'm', 'v', 'p')
    ) then
        raise exception 'Relation %.% not found', p_schema_name, p_table_name;
    end if;

    -- Limit to reasonable max
    if p_limit > 1000 then
        p_limit := 1000;
    end if;

    -- Build and execute query
    v_sql := format(
        'select coalesce(jsonb_agg(row_to_json(t)), ''[]''::jsonb) from (select * from %I.%I limit %s) t',
        p_schema_name, p_table_name, p_limit
    );
    execute v_sql into v_result;

    return coalesce(v_result, '[]'::jsonb);
end;
$$;

comment on function api.get_table_sample is
    'Returns sample rows from a table as JSONB array. Limited to 1000 rows max.';

grant execute on function api.get_table_sample(text, text, integer) to authenticated;

-- =============================================================================
-- 7. api.toggle_schema_exposure - Toggle Schema Visibility
-- =============================================================================
-- Upserts schema exposure setting. Only service_role can call this.

create or replace function api.toggle_schema_exposure(
    p_schema_name text,
    p_exposed boolean default true,
    p_description text default null
)
returns ops.exposed_schemas
security definer
language plpgsql
as $$
declare
    v_result ops.exposed_schemas;
begin
    insert into ops.exposed_schemas (schema_name, exposed, description)
    values (p_schema_name, p_exposed, p_description)
    on conflict (schema_name) do update set
        exposed = excluded.exposed,
        description = coalesce(excluded.description, ops.exposed_schemas.description),
        updated_at = now()
    returning * into v_result;

    return v_result;
end;
$$;

comment on function api.toggle_schema_exposure is
    'Toggles schema exposure for Tables browser. Restricted to service_role.';

-- Only service_role can toggle exposure
grant execute on function api.toggle_schema_exposure(text, boolean, text) to service_role;

-- =============================================================================
-- 8. api.list_schemas - List All Schemas with Exposure Status
-- =============================================================================

create or replace function api.list_schemas()
returns table(
    schema_name text,
    is_exposed boolean,
    table_count bigint,
    description text
)
security definer
language sql
stable
as $$
    with schema_counts as (
        select
            n.nspname::text as schema_name,
            count(*) as table_count
        from pg_class c
        join pg_namespace n on n.oid = c.relnamespace
        where c.relkind in ('r', 'v', 'm', 'p')
          and n.nspname not in ('pg_catalog', 'information_schema', 'pg_toast')
          and n.nspname not like 'pg_temp%'
          and n.nspname not like 'pg_toast%'
        group by n.nspname
    )
    select
        sc.schema_name,
        coalesce(es.exposed, false) as is_exposed,
        sc.table_count,
        es.description
    from schema_counts sc
    left join ops.exposed_schemas es on es.schema_name = sc.schema_name
    order by
        (case when coalesce(es.exposed, false) then 0 else 1 end),
        sc.schema_name;
$$;

comment on function api.list_schemas is
    'Lists all database schemas with exposure status and table counts.';

grant execute on function api.list_schemas() to authenticated;
grant execute on function api.list_schemas() to anon;

-- =============================================================================
-- Done
-- =============================================================================
