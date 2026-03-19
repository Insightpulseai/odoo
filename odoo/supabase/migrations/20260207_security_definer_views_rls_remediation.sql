-- =============================================================================
-- Migration: Security Definer Views + RLS Remediation (Batch 2)
-- Date: 2026-02-07
-- Scope: Fix remaining Supabase Database Linter findings
--   - 2 SECURITY DEFINER views (public.view_system_health_hourly, public.AssetSearchView)
--   - 42 tables missing RLS (public + ops schemas)
--   - 3 tables with sensitive columns exposed without RLS
-- =============================================================================

BEGIN;

-- =============================================================================
-- PART 1: SECURITY DEFINER Views → SECURITY INVOKER
-- =============================================================================
-- Convert SECURITY DEFINER views to default (SECURITY INVOKER) so that
-- RLS policies of the querying user are enforced, not the view creator's.
--
-- Strategy: ALTER VIEW ... SET (security_invoker = on)
-- This avoids needing to know the full view definition to DROP/CREATE.
-- Requires PostgreSQL 15+ (Supabase runs PG 15).

ALTER VIEW IF EXISTS public.view_system_health_hourly
  SET (security_invoker = on);

ALTER VIEW IF EXISTS public."AssetSearchView"
  SET (security_invoker = on);

-- =============================================================================
-- PART 2: Enable RLS on all exposed tables
-- =============================================================================
-- Tables flagged by Supabase linter as public-facing without RLS.
-- Grouped by risk level.

-- 2a. HIGH RISK - Sensitive columns (password, token)
ALTER TABLE IF EXISTS public."user" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.api_secrets ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.project_member_invite ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.workspace_member_invite ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.social_login_connection ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public."SsoDetails" ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public."UserOrganization" ENABLE ROW LEVEL SECURITY;

-- 2b. AUTH / PERMISSIONS tables
ALTER TABLE IF EXISTS public.auth_permission ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.auth_group ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.auth_group_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.user_groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.user_user_permissions ENABLE ROW LEVEL SECURITY;

-- 2c. WORKSPACE / TEAM / PROJECT hierarchy
ALTER TABLE IF EXISTS public.workspace ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.workspace_member ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.team ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.team_member ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.project ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.project_member ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.project_identifier ENABLE ROW LEVEL SECURITY;

-- 2d. ISSUE tracking tables
ALTER TABLE IF EXISTS public.issue ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.issue_timeline ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.issue_sequence ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.issue_property ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.issue_label ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.issue_blocker ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.issue_assignee ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.issue_activity ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.issue_comment ENABLE ROW LEVEL SECURITY;

-- 2e. CYCLE / MODULE / MISC
ALTER TABLE IF EXISTS public.state ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.cycle ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.cycle_issue ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.label ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.shortcut ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.file_asset ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.view ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.module ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.module_member ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.module_issues ENABLE ROW LEVEL SECURITY;

-- 2f. MIGRATION / SYSTEM tables
ALTER TABLE IF EXISTS public.django_migrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.django_content_type ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public._prisma_migrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public."_AssetToTag" ENABLE ROW LEVEL SECURITY;

-- 2g. OPS schema
ALTER TABLE IF EXISTS ops.model_repo_scans ENABLE ROW LEVEL SECURITY;

-- =============================================================================
-- PART 3: RLS Policies — Sensitive tables (HIGH priority)
-- =============================================================================
-- These tables contain passwords, tokens, or secrets and MUST have restrictive
-- policies. Default: service_role only, with authenticated read where safe.

-- 3a. public.user — contains password + token columns
CREATE POLICY "user_service_role_only"
  ON public."user" FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
    OR auth.uid()::text = id::text
  );

-- 3b. public.api_secrets — secrets table, service_role only
CREATE POLICY "api_secrets_service_role_only"
  ON public.api_secrets FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

-- 3c. Invite tables with token columns — service_role or invite owner
CREATE POLICY "project_member_invite_restricted"
  ON public.project_member_invite FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
    OR auth.uid()::text = accepted_by::text
  );

CREATE POLICY "workspace_member_invite_restricted"
  ON public.workspace_member_invite FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
    OR auth.uid()::text = accepted_by::text
  );

-- 3d. SSO / Social login — service_role only
CREATE POLICY "sso_details_service_role_only"
  ON public."SsoDetails" FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

CREATE POLICY "social_login_service_role_only"
  ON public.social_login_connection FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
    OR auth.uid()::text = user_id::text
  );

CREATE POLICY "user_org_service_role_only"
  ON public."UserOrganization" FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
    OR auth.uid()::text = user_id::text
  );

-- =============================================================================
-- PART 4: RLS Policies — Auth / Permissions (service_role or authenticated read)
-- =============================================================================

CREATE POLICY "auth_permission_read_authenticated"
  ON public.auth_permission FOR SELECT
  USING (auth.role() = 'authenticated');

CREATE POLICY "auth_permission_write_service_role"
  ON public.auth_permission FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

CREATE POLICY "auth_group_read_authenticated"
  ON public.auth_group FOR SELECT
  USING (auth.role() = 'authenticated');

CREATE POLICY "auth_group_write_service_role"
  ON public.auth_group FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

CREATE POLICY "auth_group_permissions_read_authenticated"
  ON public.auth_group_permissions FOR SELECT
  USING (auth.role() = 'authenticated');

CREATE POLICY "auth_group_permissions_write_service_role"
  ON public.auth_group_permissions FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

CREATE POLICY "user_groups_read_authenticated"
  ON public.user_groups FOR SELECT
  USING (auth.role() = 'authenticated');

CREATE POLICY "user_groups_write_service_role"
  ON public.user_groups FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

CREATE POLICY "user_permissions_read_authenticated"
  ON public.user_user_permissions FOR SELECT
  USING (auth.role() = 'authenticated');

CREATE POLICY "user_permissions_write_service_role"
  ON public.user_user_permissions FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

-- =============================================================================
-- PART 5: RLS Policies — Workspace / Team / Project (workspace-scoped)
-- =============================================================================
-- These tables form a hierarchy: workspace → team → project.
-- Access is scoped via membership tables.

CREATE POLICY "workspace_member_access"
  ON public.workspace FOR SELECT
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
    OR EXISTS (
      SELECT 1 FROM public.workspace_member wm
      WHERE wm.workspace_id = workspace.id
        AND wm.user_id::text = auth.uid()::text
    )
  );

CREATE POLICY "workspace_write_service_role"
  ON public.workspace FOR INSERT
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

CREATE POLICY "workspace_member_read"
  ON public.workspace_member FOR SELECT
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
    OR user_id::text = auth.uid()::text
    OR EXISTS (
      SELECT 1 FROM public.workspace_member wm2
      WHERE wm2.workspace_id = workspace_member.workspace_id
        AND wm2.user_id::text = auth.uid()::text
    )
  );

CREATE POLICY "workspace_member_write_service_role"
  ON public.workspace_member FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

CREATE POLICY "team_member_access"
  ON public.team FOR SELECT
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
    OR EXISTS (
      SELECT 1 FROM public.team_member tm
      WHERE tm.team_id = team.id
        AND tm.user_id::text = auth.uid()::text
    )
  );

CREATE POLICY "team_write_service_role"
  ON public.team FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

CREATE POLICY "team_member_read"
  ON public.team_member FOR SELECT
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
    OR user_id::text = auth.uid()::text
    OR EXISTS (
      SELECT 1 FROM public.team_member tm2
      WHERE tm2.team_id = team_member.team_id
        AND tm2.user_id::text = auth.uid()::text
    )
  );

CREATE POLICY "team_member_write_service_role"
  ON public.team_member FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

CREATE POLICY "project_workspace_member_access"
  ON public.project FOR SELECT
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
    OR EXISTS (
      SELECT 1 FROM public.project_member pm
      WHERE pm.project_id = project.id
        AND pm.member_id::text = auth.uid()::text
    )
  );

CREATE POLICY "project_write_service_role"
  ON public.project FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

CREATE POLICY "project_member_read"
  ON public.project_member FOR SELECT
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
    OR member_id::text = auth.uid()::text
    OR EXISTS (
      SELECT 1 FROM public.project_member pm2
      WHERE pm2.project_id = project_member.project_id
        AND pm2.member_id::text = auth.uid()::text
    )
  );

CREATE POLICY "project_member_write_service_role"
  ON public.project_member FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

CREATE POLICY "project_identifier_read"
  ON public.project_identifier FOR SELECT
  USING (auth.role() = 'authenticated');

CREATE POLICY "project_identifier_write_service_role"
  ON public.project_identifier FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

-- =============================================================================
-- PART 6: RLS Policies — Issue tracking (project-scoped)
-- =============================================================================
-- Issue tables inherit access from the parent project via project_id.

CREATE POLICY "issue_project_member_access"
  ON public.issue FOR SELECT
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
    OR EXISTS (
      SELECT 1 FROM public.project_member pm
      WHERE pm.project_id = issue.project_id
        AND pm.member_id::text = auth.uid()::text
    )
  );

CREATE POLICY "issue_write_service_role"
  ON public.issue FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

-- Issue child tables: inherit via issue.project_id

CREATE POLICY "issue_timeline_via_project"
  ON public.issue_timeline FOR SELECT
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
    OR EXISTS (
      SELECT 1 FROM public.issue i
      JOIN public.project_member pm ON pm.project_id = i.project_id
      WHERE i.id = issue_timeline.issue_id
        AND pm.member_id::text = auth.uid()::text
    )
  );

CREATE POLICY "issue_timeline_write_service_role"
  ON public.issue_timeline FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

CREATE POLICY "issue_sequence_service_role"
  ON public.issue_sequence FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

CREATE POLICY "issue_property_via_project"
  ON public.issue_property FOR SELECT
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
    OR EXISTS (
      SELECT 1 FROM public.issue i
      JOIN public.project_member pm ON pm.project_id = i.project_id
      WHERE i.id = issue_property.issue_id
        AND pm.member_id::text = auth.uid()::text
    )
  );

CREATE POLICY "issue_property_write_service_role"
  ON public.issue_property FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

CREATE POLICY "issue_label_via_project"
  ON public.issue_label FOR SELECT
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
    OR EXISTS (
      SELECT 1 FROM public.issue i
      JOIN public.project_member pm ON pm.project_id = i.project_id
      WHERE i.id = issue_label.issue_id
        AND pm.member_id::text = auth.uid()::text
    )
  );

CREATE POLICY "issue_label_write_service_role"
  ON public.issue_label FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

CREATE POLICY "issue_blocker_via_project"
  ON public.issue_blocker FOR SELECT
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
    OR EXISTS (
      SELECT 1 FROM public.issue i
      JOIN public.project_member pm ON pm.project_id = i.project_id
      WHERE i.id = issue_blocker.issue_id
        AND pm.member_id::text = auth.uid()::text
    )
  );

CREATE POLICY "issue_blocker_write_service_role"
  ON public.issue_blocker FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

CREATE POLICY "issue_assignee_via_project"
  ON public.issue_assignee FOR SELECT
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
    OR EXISTS (
      SELECT 1 FROM public.issue i
      JOIN public.project_member pm ON pm.project_id = i.project_id
      WHERE i.id = issue_assignee.issue_id
        AND pm.member_id::text = auth.uid()::text
    )
  );

CREATE POLICY "issue_assignee_write_service_role"
  ON public.issue_assignee FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

CREATE POLICY "issue_activity_via_project"
  ON public.issue_activity FOR SELECT
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
    OR EXISTS (
      SELECT 1 FROM public.issue i
      JOIN public.project_member pm ON pm.project_id = i.project_id
      WHERE i.id = issue_activity.issue_id
        AND pm.member_id::text = auth.uid()::text
    )
  );

CREATE POLICY "issue_activity_write_service_role"
  ON public.issue_activity FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

CREATE POLICY "issue_comment_via_project"
  ON public.issue_comment FOR SELECT
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
    OR EXISTS (
      SELECT 1 FROM public.issue i
      JOIN public.project_member pm ON pm.project_id = i.project_id
      WHERE i.id = issue_comment.issue_id
        AND pm.member_id::text = auth.uid()::text
    )
  );

CREATE POLICY "issue_comment_write_service_role"
  ON public.issue_comment FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

-- =============================================================================
-- PART 7: RLS Policies — Cycles, Labels, Modules, Misc
-- =============================================================================

-- Cycles — workspace scoped
CREATE POLICY "cycle_workspace_access"
  ON public.cycle FOR SELECT
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
    OR EXISTS (
      SELECT 1 FROM public.workspace_member wm
      WHERE wm.workspace_id = cycle.workspace_id
        AND wm.user_id::text = auth.uid()::text
    )
  );

CREATE POLICY "cycle_write_service_role"
  ON public.cycle FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

CREATE POLICY "cycle_issue_service_role"
  ON public.cycle_issue FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

-- State — reference data, read for authenticated
CREATE POLICY "state_read_authenticated"
  ON public.state FOR SELECT
  USING (auth.role() = 'authenticated');

CREATE POLICY "state_write_service_role"
  ON public.state FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

-- Label — workspace scoped reference data
CREATE POLICY "label_read_authenticated"
  ON public.label FOR SELECT
  USING (auth.role() = 'authenticated');

CREATE POLICY "label_write_service_role"
  ON public.label FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

-- Shortcut — user-owned
CREATE POLICY "shortcut_owner_access"
  ON public.shortcut FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
    OR user_id::text = auth.uid()::text
  );

-- File asset — authenticated read, service_role write
CREATE POLICY "file_asset_read_authenticated"
  ON public.file_asset FOR SELECT
  USING (auth.role() = 'authenticated');

CREATE POLICY "file_asset_write_service_role"
  ON public.file_asset FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

-- View (table named "view") — workspace scoped
CREATE POLICY "view_read_authenticated"
  ON public.view FOR SELECT
  USING (auth.role() = 'authenticated');

CREATE POLICY "view_write_service_role"
  ON public.view FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

-- Module / Module members / Module issues — workspace scoped
CREATE POLICY "module_read_authenticated"
  ON public.module FOR SELECT
  USING (auth.role() = 'authenticated');

CREATE POLICY "module_write_service_role"
  ON public.module FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

CREATE POLICY "module_member_read_authenticated"
  ON public.module_member FOR SELECT
  USING (auth.role() = 'authenticated');

CREATE POLICY "module_member_write_service_role"
  ON public.module_member FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

CREATE POLICY "module_issues_read_authenticated"
  ON public.module_issues FOR SELECT
  USING (auth.role() = 'authenticated');

CREATE POLICY "module_issues_write_service_role"
  ON public.module_issues FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

-- =============================================================================
-- PART 8: RLS Policies — System / Migration tables (service_role only)
-- =============================================================================

CREATE POLICY "django_migrations_service_role_only"
  ON public.django_migrations FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

CREATE POLICY "django_content_type_service_role_only"
  ON public.django_content_type FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

CREATE POLICY "prisma_migrations_service_role_only"
  ON public._prisma_migrations FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

CREATE POLICY "asset_to_tag_read_authenticated"
  ON public."_AssetToTag" FOR SELECT
  USING (auth.role() = 'authenticated');

CREATE POLICY "asset_to_tag_write_service_role"
  ON public."_AssetToTag" FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

-- OPS schema — service_role only
CREATE POLICY "ops_model_repo_scans_service_role_only"
  ON ops.model_repo_scans FOR ALL
  USING (
    (current_setting('request.jwt.claims', true)::json ->> 'role') = 'service_role'
  );

-- =============================================================================
-- PART 9: Verification
-- =============================================================================

DO $$
DECLARE
  rec RECORD;
  cnt INT := 0;
BEGIN
  RAISE NOTICE '=== SECURITY DEFINER VIEW CHECK ===';

  FOR rec IN
    SELECT schemaname, viewname
    FROM pg_views
    WHERE viewname IN ('view_system_health_hourly', 'AssetSearchView')
      AND schemaname = 'public'
  LOOP
    RAISE NOTICE 'View: %.% — check security_invoker is ON', rec.schemaname, rec.viewname;
  END LOOP;

  RAISE NOTICE '=== RLS ENABLEMENT CHECK ===';

  FOR rec IN
    SELECT n.nspname AS schema_name, c.relname AS table_name
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname IN ('public', 'ops')
      AND c.relkind = 'r'
      AND c.relrowsecurity = false
    ORDER BY n.nspname, c.relname
  LOOP
    RAISE WARNING 'RLS still disabled: %.%', rec.schema_name, rec.table_name;
    cnt := cnt + 1;
  END LOOP;

  IF cnt = 0 THEN
    RAISE NOTICE 'All public/ops tables have RLS enabled';
  ELSE
    RAISE WARNING '% tables still missing RLS in public/ops', cnt;
  END IF;
END $$;

COMMIT;
