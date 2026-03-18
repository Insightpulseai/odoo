-- Odoo Copilot: Channel identity mapping
-- Maps external platform users (Slack, Teams, web) to Odoo user IDs

CREATE TABLE IF NOT EXISTS kb.channel_identity_map (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  platform text NOT NULL CHECK (platform IN ('slack', 'teams', 'web')),
  platform_user_id text NOT NULL,
  platform_display_name text,
  odoo_user_id integer NOT NULL,
  entra_object_id text,
  created_at timestamptz DEFAULT now(),
  UNIQUE(platform, platform_user_id)
);

COMMENT ON TABLE kb.channel_identity_map IS 'Maps Slack/Teams/web users to Odoo user IDs for copilot identity resolution';

CREATE OR REPLACE FUNCTION kb.resolve_channel_user(p_platform text, p_platform_user_id text)
RETURNS integer AS $$
  SELECT odoo_user_id FROM kb.channel_identity_map
  WHERE platform = p_platform AND platform_user_id = p_platform_user_id;
$$ LANGUAGE sql STABLE;

COMMENT ON FUNCTION kb.resolve_channel_user IS 'Resolve a platform user to their Odoo user ID';
