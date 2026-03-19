-- Sync Events Schema
-- Tracks bidirectional sync operations between repo, docs, schema, and KB

-- ============================================================================
-- SYNC EVENTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS sync_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type TEXT NOT NULL,
    channel TEXT,
    action TEXT,
    source TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    -- Sync details
    details JSONB,
    broadcast_targets TEXT[],
    -- Error tracking
    error_message TEXT,
    retry_count INT DEFAULT 0,
    -- Timestamps
    timestamp TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- SYSTEM METADATA TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS system_metadata (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key TEXT UNIQUE NOT NULL,
    value TEXT,
    metadata JSONB,
    updated_at TIMESTAMPTZ DEFAULT now(),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- NOTIFICATIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    body TEXT,
    data JSONB,
    read BOOLEAN DEFAULT false,
    read_at TIMESTAMPTZ,
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================================
-- DATA ASSETS UPDATES
-- ============================================================================
-- Add columns to data_assets if they don't exist
DO $$
BEGIN
    -- Add column_count if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'data_assets' AND column_name = 'column_count') THEN
        ALTER TABLE data_assets ADD COLUMN column_count INT;
    END IF;

    -- Add row_estimate if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'data_assets' AND column_name = 'row_estimate') THEN
        ALTER TABLE data_assets ADD COLUMN row_estimate BIGINT;
    END IF;

    -- Add indexes array if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'data_assets' AND column_name = 'indexes') THEN
        ALTER TABLE data_assets ADD COLUMN indexes TEXT[];
    END IF;

    -- Add constraints array if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'data_assets' AND column_name = 'constraints') THEN
        ALTER TABLE data_assets ADD COLUMN constraints TEXT[];
    END IF;

    -- Add kb_artifact_id if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'data_assets' AND column_name = 'kb_artifact_id') THEN
        ALTER TABLE data_assets ADD COLUMN kb_artifact_id UUID REFERENCES kb_artifacts(id);
    END IF;

    -- Add kb_artifact_ids if not exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'data_assets' AND column_name = 'kb_artifact_ids') THEN
        ALTER TABLE data_assets ADD COLUMN kb_artifact_ids UUID[];
    END IF;
END $$;

-- ============================================================================
-- KB ARTIFACTS UPDATES
-- ============================================================================
-- Add content_hash column for change detection
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'kb_artifacts' AND column_name = 'content_hash') THEN
        ALTER TABLE kb_artifacts ADD COLUMN content_hash TEXT;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'kb_artifacts' AND column_name = 'source_path') THEN
        ALTER TABLE kb_artifacts ADD COLUMN source_path TEXT;
    END IF;
END $$;

-- ============================================================================
-- INDEXES
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_sync_events_type ON sync_events(event_type);
CREATE INDEX IF NOT EXISTS idx_sync_events_status ON sync_events(status);
CREATE INDEX IF NOT EXISTS idx_sync_events_timestamp ON sync_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_sync_events_channel ON sync_events(channel);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_unread ON notifications(user_id, read) WHERE read = false;
CREATE INDEX IF NOT EXISTS idx_system_metadata_key ON system_metadata(key);
CREATE INDEX IF NOT EXISTS idx_kb_artifacts_source_path ON kb_artifacts(source_path);
CREATE INDEX IF NOT EXISTS idx_kb_artifacts_content_hash ON kb_artifacts(content_hash);

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to get table metadata
CREATE OR REPLACE FUNCTION get_table_metadata(table_names TEXT[] DEFAULT NULL)
RETURNS TABLE (
    table_name TEXT,
    column_count INT,
    row_estimate BIGINT,
    indexes TEXT[],
    constraints TEXT[]
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.tablename::TEXT AS table_name,
        (SELECT COUNT(*)::INT FROM information_schema.columns c
         WHERE c.table_name = t.tablename AND c.table_schema = 'public') AS column_count,
        COALESCE(c.reltuples::BIGINT, 0) AS row_estimate,
        ARRAY(SELECT indexname FROM pg_indexes
              WHERE tablename = t.tablename AND schemaname = 'public') AS indexes,
        ARRAY(SELECT conname FROM pg_constraint con
              JOIN pg_class rel ON rel.oid = con.conrelid
              WHERE rel.relname = t.tablename) AS constraints
    FROM pg_tables t
    LEFT JOIN pg_class c ON c.relname = t.tablename
    WHERE t.schemaname = 'public'
    AND (table_names IS NULL OR t.tablename = ANY(table_names));
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to refresh metadata views (placeholder)
CREATE OR REPLACE FUNCTION refresh_metadata_views()
RETURNS VOID AS $$
BEGIN
    -- Placeholder for materialized view refresh
    -- In production, this would refresh any materialized views
    RAISE NOTICE 'Metadata views refreshed at %', now();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- ROW LEVEL SECURITY
-- ============================================================================
ALTER TABLE sync_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Sync events: admin access only
CREATE POLICY "Admin access to sync events"
    ON sync_events FOR ALL
    USING (auth.jwt()->>'role' IN ('admin', 'service'));

-- Notifications: users see their own
CREATE POLICY "Users see own notifications"
    ON notifications FOR SELECT
    USING (user_id = auth.uid() OR auth.jwt()->>'role' = 'admin');

CREATE POLICY "Users update own notifications"
    ON notifications FOR UPDATE
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- ============================================================================
-- REALTIME SUBSCRIPTIONS
-- ============================================================================
-- Enable realtime for sync events
ALTER PUBLICATION supabase_realtime ADD TABLE sync_events;
ALTER PUBLICATION supabase_realtime ADD TABLE notifications;
