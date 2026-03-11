-- supabase_exposure_audit.sql
-- ==============================================================================
-- Goal: Deterministically list what's exposed via Supabase Data API / RPC /
--       GraphQL / Realtime authorization
-- ==============================================================================
--
-- USAGE: Run as postgres role in Supabase SQL Editor
--
-- REFERENCE:
--   - PostgREST exposed schemas: https://supabase.com/docs/guides/database/hardening-data-api
--   - GraphQL (pg_graphql): https://supabase.com/docs/guides/database/extensions/pg_graphql
--   - Realtime Authorization: https://supabase.com/docs/guides/realtime/authorization
--
-- KEY CONCEPTS:
--   - REST + RPC exposure is gated by PostgREST "exposed schemas" (pgrst.db_schemas)
--     plus privileges/RLS
--   - GraphQL exposure exists only if pg_graphql is installed; derives from SQL +
--     permissions/search_path
--   - Realtime channel access is governed by RLS policies on realtime.messages
--
-- HARDENING RULE:
--   - Put client-facing objects in schemas intentionally in "Exposed schemas" with tight RLS
--   - Put internal-only tables/functions in schemas NOT in Exposed schemas and don't grant
--     anon/authenticated any privileges
--
-- ==============================================================================

-- ===============
-- 0) Quick context
-- ===============
SELECT
    current_database() AS db,
    current_user AS role,
    now() AS ts;

-- =========================================
-- 1) PostgREST "exposed schemas" (db-schemas)
--    This is the real gate for REST/RPC.
--    Supabase manages this via Dashboard -> API Settings.
-- =========================================

-- 1a) Raw authenticator role settings
SELECT
    r.rolname,
    d.datname,
    unnest(s.setconfig) AS setting
FROM pg_db_role_setting s
JOIN pg_roles r ON r.oid = s.setrole
JOIN pg_database d ON d.oid = s.setdatabase
WHERE r.rolname = 'authenticator'
ORDER BY 1, 2, 3;

-- 1b) Extract pgrst.db_schemas / pgrst.db_extra_search_path if present
WITH cfg AS (
    SELECT unnest(s.setconfig) AS kv
    FROM pg_db_role_setting s
    JOIN pg_roles r ON r.oid = s.setrole
    JOIN pg_database d ON d.oid = s.setdatabase
    WHERE r.rolname = 'authenticator'
)
SELECT
    split_part(kv, '=', 1) AS key,
    split_part(kv, '=', 2) AS value
FROM cfg
WHERE kv LIKE 'pgrst.%'
ORDER BY key;

-- ==================================================
-- 2) REST exposure inference: objects with privileges
--    Even if schema is exposed, an object is callable only if:
--    - USAGE on schema + table/view privileges exist
--    - and RLS allows (for tables/views with RLS enabled)
-- ==================================================

-- 2a) Schemas where anon/authenticated have USAGE
SELECT
    n.nspname AS schema,
    r.rolname AS role
FROM pg_namespace n
JOIN pg_roles r ON r.rolname IN ('anon', 'authenticated')
WHERE has_schema_privilege(r.rolname, n.nspname, 'USAGE')
ORDER BY 1, 2;

-- 2b) Tables/views where anon/authenticated have SELECT privilege
SELECT
    n.nspname AS schema,
    c.relname AS relation,
    c.relkind,
    r.rolname AS role,
    has_table_privilege(r.rolname, quote_ident(n.nspname) || '.' || quote_ident(c.relname), 'SELECT') AS can_select,
    c.relrowsecurity AS rls_enabled
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
JOIN pg_roles r ON r.rolname IN ('anon', 'authenticated')
WHERE c.relkind IN ('r', 'v', 'm') -- table, view, matview
    AND n.nspname NOT IN ('pg_catalog', 'information_schema')
    AND has_table_privilege(r.rolname, quote_ident(n.nspname) || '.' || quote_ident(c.relname), 'SELECT')
ORDER BY 1, 2, 4;

-- 2c) Tables/views where anon/authenticated have INSERT/UPDATE/DELETE privileges
SELECT
    n.nspname AS schema,
    c.relname AS relation,
    c.relkind,
    r.rolname AS role,
    has_table_privilege(r.rolname, quote_ident(n.nspname) || '.' || quote_ident(c.relname), 'INSERT') AS can_insert,
    has_table_privilege(r.rolname, quote_ident(n.nspname) || '.' || quote_ident(c.relname), 'UPDATE') AS can_update,
    has_table_privilege(r.rolname, quote_ident(n.nspname) || '.' || quote_ident(c.relname), 'DELETE') AS can_delete,
    c.relrowsecurity AS rls_enabled
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
JOIN pg_roles r ON r.rolname IN ('anon', 'authenticated')
WHERE c.relkind IN ('r', 'v', 'm')
    AND n.nspname NOT IN ('pg_catalog', 'information_schema')
    AND (
        has_table_privilege(r.rolname, quote_ident(n.nspname) || '.' || quote_ident(c.relname), 'INSERT')
        OR has_table_privilege(r.rolname, quote_ident(n.nspname) || '.' || quote_ident(c.relname), 'UPDATE')
        OR has_table_privilege(r.rolname, quote_ident(n.nspname) || '.' || quote_ident(c.relname), 'DELETE')
    )
ORDER BY 1, 2, 4;

-- 2d) RLS policies (these determine if SELECT/INSERT/UPDATE/DELETE actually works)
SELECT
    n.nspname AS schema,
    c.relname AS table,
    p.polname,
    p.polcmd,
    (SELECT array_agg(rolname) FROM pg_roles WHERE oid = ANY(p.polroles)) AS roles,
    pg_get_expr(p.polqual, p.polrelid) AS using_expr,
    pg_get_expr(p.polwithcheck, p.polrelid) AS withcheck_expr
FROM pg_policy p
JOIN pg_class c ON c.oid = p.polrelid
JOIN pg_namespace n ON n.oid = c.relnamespace
ORDER BY 1, 2, 3;

-- 2e) Tables with RLS enabled but NO policies (potential lockout)
SELECT
    n.nspname AS schema,
    c.relname AS table,
    c.relrowsecurity AS rls_enabled,
    'WARNING: RLS enabled but no policies found' AS warning
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'r'
    AND c.relrowsecurity = true
    AND n.nspname NOT IN ('pg_catalog', 'information_schema')
    AND NOT EXISTS (
        SELECT 1 FROM pg_policy p WHERE p.polrelid = c.oid
    )
ORDER BY 1, 2;

-- =========================================
-- 3) RPC exposure: functions callable via /rpc
--    Requirements:
--    - function is in an exposed schema (PostgREST db-schemas)
--    - EXECUTE granted to anon/authenticated
-- =========================================
SELECT
    n.nspname AS schema,
    p.proname AS function,
    pg_get_function_identity_arguments(p.oid) AS args,
    r.rolname AS role,
    has_function_privilege(r.rolname, p.oid, 'EXECUTE') AS can_execute,
    p.prosecdef AS security_definer
FROM pg_proc p
JOIN pg_namespace n ON n.oid = p.pronamespace
JOIN pg_roles r ON r.rolname IN ('anon', 'authenticated')
WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
    AND has_function_privilege(r.rolname, p.oid, 'EXECUTE')
ORDER BY 1, 2, 4;

-- 3b) SECURITY DEFINER functions (elevated privilege risk)
SELECT
    n.nspname AS schema,
    p.proname AS function,
    pg_get_function_identity_arguments(p.oid) AS args,
    p.prosecdef AS security_definer,
    'WARNING: SECURITY DEFINER runs with owner privileges' AS warning
FROM pg_proc p
JOIN pg_namespace n ON n.oid = p.pronamespace
WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
    AND p.prosecdef = true
ORDER BY 1, 2;

-- =========================================
-- 4) GraphQL exposure (pg_graphql)
--    Supabase GraphQL is powered by pg_graphql; disable extension to harden.
--    Visibility follows Postgres search_path + permissions.
-- =========================================

-- 4a) Check if pg_graphql is installed
SELECT
    extname,
    extversion,
    CASE
        WHEN extname = 'pg_graphql' THEN 'GraphQL endpoint is ENABLED'
        ELSE 'GraphQL endpoint may be disabled'
    END AS status
FROM pg_extension
WHERE extname = 'pg_graphql';

-- 4b) GraphQL entrypoints (common function names)
SELECT
    n.nspname AS schema,
    p.proname AS function,
    pg_get_function_identity_arguments(p.oid) AS args
FROM pg_proc p
JOIN pg_namespace n ON n.oid = p.pronamespace
WHERE n.nspname IN ('graphql_public', 'graphql')
ORDER BY 1, 2;

-- =========================================
-- 5) Realtime Authorization exposure
--    Realtime uses realtime.messages RLS policies to authorize channel topics.
-- =========================================

-- 5a) Check realtime.messages table and RLS status
SELECT
    n.nspname AS schema,
    c.relname AS table,
    c.relrowsecurity AS rls_enabled
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'realtime' AND c.relname = 'messages';

-- 5b) Realtime messages RLS policies
SELECT
    p.polname,
    p.polcmd,
    (SELECT array_agg(rolname) FROM pg_roles WHERE oid = ANY(p.polroles)) AS roles,
    pg_get_expr(p.polqual, p.polrelid) AS using_expr,
    pg_get_expr(p.polwithcheck, p.polrelid) AS withcheck_expr
FROM pg_policy p
WHERE p.polrelid = 'realtime.messages'::regclass
ORDER BY 1;

-- =========================================
-- 6) Storage exposure (storage.objects)
--    Supabase Storage uses RLS on storage.objects
-- =========================================

-- 6a) Storage buckets
SELECT
    id,
    name,
    public,
    CASE
        WHEN public THEN 'WARNING: Public bucket - accessible without auth'
        ELSE 'Private bucket - requires auth'
    END AS access_warning
FROM storage.buckets
ORDER BY name;

-- 6b) Storage objects RLS policies
SELECT
    p.polname,
    p.polcmd,
    (SELECT array_agg(rolname) FROM pg_roles WHERE oid = ANY(p.polroles)) AS roles,
    pg_get_expr(p.polqual, p.polrelid) AS using_expr,
    pg_get_expr(p.polwithcheck, p.polrelid) AS withcheck_expr
FROM pg_policy p
WHERE p.polrelid = 'storage.objects'::regclass
ORDER BY 1;

-- =========================================
-- 7) Summary: Exposure Risk Assessment
-- =========================================

-- 7a) High-level summary of exposed surfaces
SELECT 'SCHEMAS WITH anon USAGE' AS category, count(*) AS count
FROM pg_namespace n
WHERE has_schema_privilege('anon', n.nspname, 'USAGE')
    AND n.nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
UNION ALL
SELECT 'SCHEMAS WITH authenticated USAGE', count(*)
FROM pg_namespace n
WHERE has_schema_privilege('authenticated', n.nspname, 'USAGE')
    AND n.nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
UNION ALL
SELECT 'TABLES/VIEWS readable by anon', count(*)
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind IN ('r', 'v', 'm')
    AND n.nspname NOT IN ('pg_catalog', 'information_schema')
    AND has_table_privilege('anon', quote_ident(n.nspname) || '.' || quote_ident(c.relname), 'SELECT')
UNION ALL
SELECT 'TABLES/VIEWS readable by authenticated', count(*)
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind IN ('r', 'v', 'm')
    AND n.nspname NOT IN ('pg_catalog', 'information_schema')
    AND has_table_privilege('authenticated', quote_ident(n.nspname) || '.' || quote_ident(c.relname), 'SELECT')
UNION ALL
SELECT 'FUNCTIONS callable by anon', count(*)
FROM pg_proc p
JOIN pg_namespace n ON n.oid = p.pronamespace
WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
    AND has_function_privilege('anon', p.oid, 'EXECUTE')
UNION ALL
SELECT 'FUNCTIONS callable by authenticated', count(*)
FROM pg_proc p
JOIN pg_namespace n ON n.oid = p.pronamespace
WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
    AND has_function_privilege('authenticated', p.oid, 'EXECUTE')
UNION ALL
SELECT 'SECURITY DEFINER functions', count(*)
FROM pg_proc p
JOIN pg_namespace n ON n.oid = p.pronamespace
WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
    AND p.prosecdef = true
UNION ALL
SELECT 'TABLES with RLS enabled', count(*)
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'r'
    AND n.nspname NOT IN ('pg_catalog', 'information_schema')
    AND c.relrowsecurity = true
UNION ALL
SELECT 'TABLES with RLS enabled but NO policies', count(*)
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'r'
    AND c.relrowsecurity = true
    AND n.nspname NOT IN ('pg_catalog', 'information_schema')
    AND NOT EXISTS (SELECT 1 FROM pg_policy p WHERE p.polrelid = c.oid);

-- ==============================================================================
-- END OF AUDIT
-- ==============================================================================
