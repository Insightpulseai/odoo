-- =============================================================================
-- Migration: 20260301000030_work_membership_rpc.sql
-- Schema:    work
-- Purpose:   RPC for M365 Copilot broker membership gating
-- Branch:    feat/advisor-migrations
-- Date:      2026-03-01
-- Depends:   20260301000002_work_schema.sql (work.permissions, work.spaces, auth.users)
-- Note:      work.work_search() already exists — DO NOT recreate it.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Function: work.work_is_member(p_space_id UUID, p_subject TEXT) → BOOLEAN
-- Returns true if p_subject has any permission row on the given space.
-- p_subject may be:
--   - A Supabase user UUID expressed as text (e.g. "a1b2c3d4-...")
--   - An email / M365 UPN (e.g. "alice@insightpulseai.com")
-- Matches against auth.users.id::text or auth.users.email.
-- Any permission level (viewer, editor, admin) counts as membership.
-- SECURITY DEFINER — executes as function owner (service_role).
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION work.work_is_member(
  p_space_id  UUID,
  p_subject   TEXT   -- Supabase user UUID (as text) or email / M365 UPN
)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = work, public, auth
AS $$
DECLARE
  v_count INTEGER;
BEGIN
  -- Resolve p_subject via auth.users (by email or UUID string),
  -- then check for any permission row on the given space.
  -- work.permissions.user_id is UUID FK → auth.users(id).
  -- work.permissions.level is work.permission_level (viewer/editor/admin);
  -- any level = membership.
  SELECT COUNT(*)
  INTO v_count
  FROM work.permissions p
  JOIN auth.users u ON u.id = p.user_id
  WHERE p.space_id = p_space_id
    AND (
      u.email     = p_subject        -- M365 UPN / email match
      OR u.id::text = p_subject      -- direct UUID string match
    );

  RETURN v_count > 0;
END;
$$;

COMMENT ON FUNCTION work.work_is_member(UUID, TEXT) IS
  'Returns true if p_subject (email or UUID string) has any permission row on the given space. '
  'Resolves p_subject via auth.users; any permission level counts as membership. '
  'Used by m365-copilot-broker for query gating. Stable signature — do not drop.';

GRANT EXECUTE ON FUNCTION work.work_is_member(UUID, TEXT) TO service_role;
-- Deny to anon and authenticated: broker calls this via service_role only
REVOKE EXECUTE ON FUNCTION work.work_is_member(UUID, TEXT) FROM anon, authenticated;

-- Objects created:
--   work.work_is_member(UUID, TEXT)  (function, SECURITY DEFINER)
-- Columns used from work.permissions: space_id, user_id (UUID FK → auth.users)
-- Column NOT used: level (work.permission_level) — any level = membership
-- Note: work.work_search() already exists; not recreated here.
