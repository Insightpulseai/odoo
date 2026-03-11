-- ============================================
-- Organization Invites Migration
-- Description: Multi-tenant organization invite system with RLS
-- Date: 2026-02-12
-- ============================================

-- Create schema if not exists
CREATE SCHEMA IF NOT EXISTS registry;

-- ============================================
-- Table: org_invites
-- ============================================
CREATE TABLE IF NOT EXISTS registry.org_invites (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  email text NOT NULL,
  role text NOT NULL CHECK (role IN ('admin', 'member', 'viewer')),
  token_hash text NOT NULL,
  status text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'expired', 'cancelled')),
  invited_by uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  expires_at timestamptz NOT NULL DEFAULT (now() + interval '7 days'),
  accepted_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),

  -- Constraints
  CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
  CONSTRAINT token_hash_length CHECK (length(token_hash) = 64), -- SHA-256 produces 64 hex chars
  CONSTRAINT expires_after_created CHECK (expires_at > created_at)
);

-- ============================================
-- Indexes
-- ============================================
CREATE INDEX IF NOT EXISTS idx_org_invites_org_id ON registry.org_invites(org_id);
CREATE INDEX IF NOT EXISTS idx_org_invites_email ON registry.org_invites(email);
CREATE INDEX IF NOT EXISTS idx_org_invites_token_hash ON registry.org_invites(token_hash);
CREATE INDEX IF NOT EXISTS idx_org_invites_status ON registry.org_invites(status);
CREATE INDEX IF NOT EXISTS idx_org_invites_expires_at ON registry.org_invites(expires_at);
CREATE INDEX IF NOT EXISTS idx_org_invites_invited_by ON registry.org_invites(invited_by);

-- ============================================
-- Trigger: Auto-update updated_at
-- ============================================
CREATE OR REPLACE FUNCTION registry.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_org_invites_updated_at ON registry.org_invites;
CREATE TRIGGER update_org_invites_updated_at
  BEFORE UPDATE ON registry.org_invites
  FOR EACH ROW
  EXECUTE FUNCTION registry.update_updated_at_column();

-- ============================================
-- RPC Function: create_org_invite_with_token
-- Description: Create invite with SHA-256 hashed token
-- ============================================
CREATE OR REPLACE FUNCTION registry.create_org_invite_with_token(
  p_org_id uuid,
  p_email text,
  p_role text,
  p_token text
)
RETURNS registry.org_invites
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = registry, pg_temp
AS $$
DECLARE
  v_invite registry.org_invites;
  v_token_hash text;
BEGIN
  -- Validate user is org admin (user.id = org_id)
  IF auth.uid() != p_org_id THEN
    RAISE EXCEPTION 'Forbidden: You do not have permission to invite users to this organization';
  END IF;

  -- Hash token with SHA-256
  v_token_hash := encode(digest(p_token, 'sha256'), 'hex');

  -- Insert invite
  INSERT INTO registry.org_invites (org_id, email, role, token_hash, invited_by)
  VALUES (p_org_id, p_email, p_role, v_token_hash, auth.uid())
  RETURNING * INTO v_invite;

  RETURN v_invite;
END;
$$;

-- ============================================
-- RPC Function: accept_org_invite
-- Description: Accept invite and return org details
-- ============================================
CREATE OR REPLACE FUNCTION registry.accept_org_invite(
  p_token text,
  p_user_id uuid
)
RETURNS json
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = registry, pg_temp
AS $$
DECLARE
  v_invite registry.org_invites;
  v_token_hash text;
BEGIN
  -- Hash incoming token
  v_token_hash := encode(digest(p_token, 'sha256'), 'hex');

  -- Find invite by token hash
  SELECT * INTO v_invite
  FROM registry.org_invites
  WHERE token_hash = v_token_hash
  AND status = 'pending'
  FOR UPDATE;

  -- Validate invite exists
  IF NOT FOUND THEN
    RAISE EXCEPTION 'Invalid or used invite';
  END IF;

  -- Validate not expired
  IF v_invite.expires_at < now() THEN
    UPDATE registry.org_invites
    SET status = 'expired'
    WHERE id = v_invite.id;

    RAISE EXCEPTION 'Invite expired';
  END IF;

  -- Update invite status
  UPDATE registry.org_invites
  SET status = 'accepted',
      accepted_at = now()
  WHERE id = v_invite.id;

  -- Return org details
  RETURN json_build_object(
    'org_id', v_invite.org_id,
    'role', v_invite.role
  );
END;
$$;

-- ============================================
-- RPC Function: cancel_org_invite
-- Description: Cancel pending invite
-- ============================================
CREATE OR REPLACE FUNCTION registry.cancel_org_invite(
  p_invite_id uuid
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = registry, pg_temp
AS $$
DECLARE
  v_invite registry.org_invites;
BEGIN
  -- Find invite
  SELECT * INTO v_invite
  FROM registry.org_invites
  WHERE id = p_invite_id
  FOR UPDATE;

  -- Validate exists
  IF NOT FOUND THEN
    RAISE EXCEPTION 'Invite not found';
  END IF;

  -- Validate user is org admin
  IF auth.uid() != v_invite.org_id THEN
    RAISE EXCEPTION 'Forbidden: You do not have permission to cancel this invite';
  END IF;

  -- Update status
  UPDATE registry.org_invites
  SET status = 'cancelled'
  WHERE id = p_invite_id;
END;
$$;

-- ============================================
-- RPC Function: cleanup_expired_invites
-- Description: Mark expired invites (can be run via cron)
-- ============================================
CREATE OR REPLACE FUNCTION registry.cleanup_expired_invites()
RETURNS integer
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = registry, pg_temp
AS $$
DECLARE
  v_count integer;
BEGIN
  UPDATE registry.org_invites
  SET status = 'expired'
  WHERE status = 'pending'
  AND expires_at < now();

  GET DIAGNOSTICS v_count = ROW_COUNT;
  RETURN v_count;
END;
$$;

-- ============================================
-- Row Level Security (RLS)
-- ============================================
ALTER TABLE registry.org_invites ENABLE ROW LEVEL SECURITY;

-- Policy: Org admins can SELECT their org's invites
CREATE POLICY org_admins_can_select ON registry.org_invites
  FOR SELECT
  USING (auth.uid() = org_id);

-- Policy: Org admins can INSERT invites (token_hash must be provided)
CREATE POLICY org_admins_can_insert ON registry.org_invites
  FOR INSERT
  WITH CHECK (
    auth.uid() = org_id
    AND auth.uid() = invited_by
    AND token_hash IS NOT NULL
    AND length(token_hash) = 64
  );

-- Policy: Users can SELECT invites for their email
CREATE POLICY users_can_select_their_invites ON registry.org_invites
  FOR SELECT
  USING (email = auth.email());

-- ============================================
-- Grants
-- ============================================
GRANT USAGE ON SCHEMA registry TO authenticated;
GRANT SELECT, INSERT ON registry.org_invites TO authenticated;
GRANT EXECUTE ON FUNCTION registry.create_org_invite_with_token TO authenticated;
GRANT EXECUTE ON FUNCTION registry.accept_org_invite TO authenticated;
GRANT EXECUTE ON FUNCTION registry.cancel_org_invite TO authenticated;
GRANT EXECUTE ON FUNCTION registry.cleanup_expired_invites TO authenticated;

-- ============================================
-- Comments
-- ============================================
COMMENT ON TABLE registry.org_invites IS 'Organization invitations with SHA-256 token hashing and RLS';
COMMENT ON FUNCTION registry.create_org_invite_with_token IS 'Create invite with hashed token (security definer)';
COMMENT ON FUNCTION registry.accept_org_invite IS 'Accept invite and return org details (security definer)';
COMMENT ON FUNCTION registry.cancel_org_invite IS 'Cancel pending invite (security definer)';
COMMENT ON FUNCTION registry.cleanup_expired_invites IS 'Mark expired invites as expired (security definer)';
