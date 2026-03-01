-- GitHub App Integration Schema
-- Contract: C-19 (docs/contracts/GITHUB_APP_CONTRACT.md)

-- Events ledger (append-only per SSOT rule 5)
CREATE TABLE IF NOT EXISTS ops.github_events (
    id BIGSERIAL PRIMARY KEY,
    delivery_id TEXT UNIQUE,
    event_type TEXT NOT NULL,
    action TEXT,
    repo_full_name TEXT,
    installation_id BIGINT,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    processed BOOLEAN NOT NULL DEFAULT false,
    processed_at TIMESTAMPTZ,
    error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_github_events_event_type ON ops.github_events(event_type);
CREATE INDEX IF NOT EXISTS idx_github_events_repo ON ops.github_events(repo_full_name);
CREATE INDEX IF NOT EXISTS idx_github_events_installation ON ops.github_events(installation_id);
CREATE INDEX IF NOT EXISTS idx_github_events_created ON ops.github_events(created_at DESC);

-- Installation registry
CREATE TABLE IF NOT EXISTS ops.github_installations (
    installation_id BIGINT PRIMARY KEY,
    account_type TEXT NOT NULL, -- 'Organization' or 'User'
    account_login TEXT NOT NULL,
    repos JSONB DEFAULT '[]'::jsonb,
    permissions JSONB DEFAULT '{}'::jsonb,
    events JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- RLS: service_role only
ALTER TABLE ops.github_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE ops.github_installations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "service_role_only_github_events"
    ON ops.github_events
    FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "service_role_only_github_installations"
    ON ops.github_installations
    FOR ALL
    USING (auth.role() = 'service_role');

COMMENT ON TABLE ops.github_events IS 'GitHub App webhook events ledger (append-only). Contract C-19.';
COMMENT ON TABLE ops.github_installations IS 'GitHub App installation registry. Contract C-19.';
