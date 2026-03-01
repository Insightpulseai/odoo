-- =============================================================================
-- Migration: 20260301000030_work_membership_rpc.sql
-- Schema:    work
-- Purpose:   RPC for M365 Copilot broker membership gating
-- Branch:    feat/advisor-migrations
-- Date:      2026-03-01
-- Depends:   20260301000002_work_schema.sql (work.spaces must exist)
-- Note:      work.work_search() already exists — DO NOT recreate it.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Function: work.work_is_member(p_space_id UUID, p_subject TEXT) → BOOLEAN
-- Returns true if p_subject has any read/write/admin permission on the given
-- space. Used by m365-copilot-broker for query gating.
-- SECURITY DEFINER — executes as function owner (service_role).
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION work.work_is_member(
  p_space_id  UUID,
  p_subject   TEXT   -- e.g. email, user_id, or M365 UPN
)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = work, public
AS $$
DECLARE
  v_count INTEGER;
BEGIN
  -- Check work.permissions table for a grant on this space
  SELECT COUNT(*)
  INTO v_count
  FROM work.permissions
  WHERE space_id = p_space_id
    AND (
      subject = p_subject
      OR subject = '*'   -- wildcard: all authenticated users
    )
    AND permission_type IN ('read', 'write', 'admin');

  RETURN v_count > 0;
END;
$$;

COMMENT ON FUNCTION work.work_is_member(UUID, TEXT) IS
  'Returns true if p_subject has any read/write/admin permission on the given space. '
  'Used by m365-copilot-broker for query gating. Stable signature — do not drop.';

GRANT EXECUTE ON FUNCTION work.work_is_member(UUID, TEXT) TO service_role;
-- Deny to anon and authenticated: broker calls this via service_role only
REVOKE EXECUTE ON FUNCTION work.work_is_member(UUID, TEXT) FROM anon, authenticated;

-- Objects created:
--   work.work_is_member(UUID, TEXT)  (function, SECURITY DEFINER)
-- Note: work.work_search() already exists; not recreated here.
