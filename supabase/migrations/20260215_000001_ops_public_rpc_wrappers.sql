-- Migration: Public RPC Wrappers for OdooOps Control Plane
-- Purpose: Expose ops.* functions via PostgREST-accessible public schema wrappers
-- Pattern: Keep ops.* internal, expose curated API surface in public
-- Created: 2026-02-15

-- ============================================================================
-- public.list_projects() - List all projects
-- ============================================================================
CREATE OR REPLACE FUNCTION public.list_projects()
RETURNS SETOF ops.projects
LANGUAGE SQL
SECURITY DEFINER
SET search_path = ops, public
AS $$
  SELECT *
  FROM ops.projects
  ORDER BY created_at DESC;
$$;

COMMENT ON FUNCTION public.list_projects IS 'List all OdooOps projects (public wrapper for ops.projects)';

-- Grant execute to authenticated users and service role
-- Explicitly NOT granting to anon (control plane requires authentication)
GRANT EXECUTE ON FUNCTION public.list_projects() TO authenticated, service_role;

-- ============================================================================
-- public.list_environments() - List environments (optionally filtered by project)
-- ============================================================================
CREATE OR REPLACE FUNCTION public.list_environments(p_project_id TEXT DEFAULT NULL)
RETURNS SETOF ops.environments
LANGUAGE SQL
SECURITY DEFINER
SET search_path = ops, public
AS $$
  SELECT *
  FROM ops.environments
  WHERE (p_project_id IS NULL OR project_id = p_project_id)
  ORDER BY created_at DESC;
$$;

COMMENT ON FUNCTION public.list_environments IS 'List environments, optionally filtered by project_id';

GRANT EXECUTE ON FUNCTION public.list_environments(TEXT) TO authenticated, service_role;

-- ============================================================================
-- public.list_runs() - List recent runs (optionally filtered by project)
-- ============================================================================
CREATE OR REPLACE FUNCTION public.list_runs(
  p_project_id TEXT DEFAULT NULL,
  p_limit INT DEFAULT 50
)
RETURNS SETOF ops.runs
LANGUAGE SQL
SECURITY DEFINER
SET search_path = ops, public
AS $$
  SELECT *
  FROM ops.runs
  WHERE (p_project_id IS NULL OR project_id = p_project_id)
  ORDER BY created_at DESC
  LIMIT p_limit;
$$;

COMMENT ON FUNCTION public.list_runs IS 'List recent runs, optionally filtered by project_id';

GRANT EXECUTE ON FUNCTION public.list_runs(TEXT, INT) TO authenticated, service_role;

-- ============================================================================
-- Verification: Check that functions are in public schema
-- ============================================================================
DO $$
DECLARE
  func_count INT;
BEGIN
  SELECT COUNT(*) INTO func_count
  FROM pg_proc p
  JOIN pg_namespace n ON p.pronamespace = n.oid
  WHERE n.nspname = 'public'
    AND p.proname IN ('list_projects', 'list_environments', 'list_runs');

  IF func_count < 3 THEN
    RAISE EXCEPTION 'Public RPC wrapper functions not created successfully';
  END IF;

  RAISE NOTICE 'Successfully created % public RPC wrapper functions', func_count;
END $$;
