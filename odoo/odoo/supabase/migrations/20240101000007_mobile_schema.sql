-- Mobile API Schema
-- Replaces: Odoo Android & iPhone (Enterprise)

-- User devices (for push notifications)
CREATE TABLE IF NOT EXISTS mobile_devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    device_id TEXT NOT NULL,
    device_name TEXT,
    platform TEXT NOT NULL CHECK (platform IN ('ios', 'android', 'web')),
    push_token TEXT,
    app_version TEXT,
    os_version TEXT,
    is_active BOOLEAN DEFAULT true,
    last_active_at TIMESTAMPTZ DEFAULT now(),
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(user_id, device_id)
);

-- Refresh tokens
CREATE TABLE IF NOT EXISTS mobile_refresh_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    device_id TEXT NOT NULL,
    token_hash TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Push notifications
CREATE TABLE IF NOT EXISTS mobile_notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    device_id TEXT,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    data JSONB DEFAULT '{}',
    category TEXT, -- 'message', 'alert', 'reminder', 'update'
    priority TEXT DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high')),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'delivered', 'failed', 'read')),
    sent_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    read_at TIMESTAMPTZ,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Sync state (for delta sync)
CREATE TABLE IF NOT EXISTS mobile_sync_state (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    device_id TEXT NOT NULL,
    entity_type TEXT NOT NULL, -- 'kb_artifacts', 'booking_appointments', etc.
    last_sync_at TIMESTAMPTZ NOT NULL,
    sync_token TEXT, -- Opaque token for cursor-based sync
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(user_id, device_id, entity_type)
);

-- Offline changes (client-side changes to sync)
CREATE TABLE IF NOT EXISTS mobile_offline_changes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    device_id TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id UUID NOT NULL,
    operation TEXT NOT NULL CHECK (operation IN ('create', 'update', 'delete')),
    payload JSONB NOT NULL,
    client_timestamp TIMESTAMPTZ NOT NULL,
    server_timestamp TIMESTAMPTZ DEFAULT now(),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'applied', 'conflict', 'rejected')),
    conflict_resolution JSONB, -- How conflict was resolved
    created_at TIMESTAMPTZ DEFAULT now()
);

-- API rate limiting
CREATE TABLE IF NOT EXISTS mobile_rate_limits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id),
    endpoint TEXT NOT NULL,
    request_count INT DEFAULT 1,
    window_start TIMESTAMPTZ DEFAULT now(),
    window_end TIMESTAMPTZ DEFAULT now() + INTERVAL '1 minute'
);

-- Session activity log
CREATE TABLE IF NOT EXISTS mobile_activity (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id),
    device_id TEXT,
    action TEXT NOT NULL,
    endpoint TEXT,
    response_code INT,
    response_time_ms INT,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMPTZ DEFAULT now()
);

-- Indexes
CREATE INDEX idx_mobile_devices_user ON mobile_devices(user_id);
CREATE INDEX idx_mobile_devices_token ON mobile_devices(push_token) WHERE is_active = true;
CREATE INDEX idx_mobile_refresh_tokens_hash ON mobile_refresh_tokens(token_hash);
CREATE INDEX idx_mobile_refresh_tokens_user ON mobile_refresh_tokens(user_id);
CREATE INDEX idx_mobile_notifications_user ON mobile_notifications(user_id);
CREATE INDEX idx_mobile_notifications_status ON mobile_notifications(status);
CREATE INDEX idx_mobile_sync_state_user ON mobile_sync_state(user_id, device_id);
CREATE INDEX idx_mobile_offline_status ON mobile_offline_changes(status);
CREATE INDEX idx_mobile_rate_limits_user ON mobile_rate_limits(user_id, endpoint);

-- Row Level Security
ALTER TABLE mobile_devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE mobile_refresh_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE mobile_notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE mobile_sync_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE mobile_offline_changes ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Users can manage their own devices"
    ON mobile_devices FOR ALL
    USING (user_id = auth.uid());

CREATE POLICY "Users can view their own notifications"
    ON mobile_notifications FOR SELECT
    USING (user_id = auth.uid());

-- Cleanup old rate limit entries (run periodically)
CREATE OR REPLACE FUNCTION cleanup_rate_limits()
RETURNS void AS $$
BEGIN
    DELETE FROM mobile_rate_limits WHERE window_end < now() - INTERVAL '1 hour';
END;
$$ LANGUAGE plpgsql;
